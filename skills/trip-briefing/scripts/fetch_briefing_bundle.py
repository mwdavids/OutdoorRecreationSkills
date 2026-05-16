"""Fetch a full deterministic briefing bundle for one peak.

Runs all the fetchers in parallel and emits a single JSON object suitable for
pasting into a conversation. The model then writes the narrative on top of
this verified factual base — it never has to hallucinate a SNOTEL triplet,
guess a freezing level, or misclassify a "partial" pass closure.

Usage:
  python fetch_briefing_bundle.py \\
      --lat 48.448 --lon -121.026 --peak-elev 9080 --peak-name "Buckner" \\
      --zone cascade-east-north --nwac-zone cascade-east-north \\
      --trailhead-lat 48.477 --trailhead-lon -121.075

All fetchers fail soft: each sub-block returns an ``error`` field on failure,
the bundle as a whole still emits.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
from datetime import date, datetime
from typing import Optional
try:
    from zoneinfo import ZoneInfo
    _PT = ZoneInfo("America/Los_Angeles")
except ImportError:
    _PT = None  # type: ignore

import compute_drive_time
import compute_sun_times
import fetch_freezing_level
import fetch_nps_alerts
import fetch_nwac_zone
import fetch_nws_point
import fetch_pass_status
import fetch_snowpack
import pick_snotel_station


def _safe_call(fn, *args, **kwargs):
    """Run a fetcher and convert exceptions into an error dict."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def build_bundle(
    lat: float,
    lon: float,
    peak_elev: int,
    peak_name: Optional[str],
    zone: Optional[str] = None,
    nwac_zone: Optional[str] = None,
    trailhead_lat: Optional[float] = None,
    trailhead_lon: Optional[float] = None,
    home_lat: float = compute_drive_time.HOME_LAT_DEFAULT,
    home_lon: float = compute_drive_time.HOME_LON_DEFAULT,
    trip_date: Optional[date] = None,
    forecast_hours: int = 72,
) -> dict:
    """Run picker + fetchers in parallel; return one combined record."""
    if trip_date is None:
        trip_date = datetime.now(_PT).date() if _PT else date.today()

    # Synchronous picker (no IO, fast). _load_stations returns the full file
    # wrapper {stations, bad_triplets, ...}; pick_* expects the flat stations dict.
    db = pick_snotel_station._load_stations()["stations"]
    panel = pick_snotel_station.pick_panel(db, lat, lon, peak_elev)
    snotel_db = fetch_snowpack._load_station_db()

    # Sun times are pure CPU, run sync (avoid thread overhead).
    sun_times = _safe_call(compute_sun_times.get_sun_times, lat, lon, trip_date)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        snotel_futures = {
            t: ex.submit(_safe_call, fetch_snowpack.fetch_station, t, snotel_db, 14)
            for t in panel
        }
        fzl_futures = {
            s["id"]: ex.submit(_safe_call, fetch_freezing_level.fetch_station, s)
            for s in fetch_freezing_level.STATIONS
        }
        nws_future = ex.submit(
            _safe_call, fetch_nws_point.fetch_forecast, lat, lon, forecast_hours
        )
        nps_future = ex.submit(_safe_call, fetch_nps_alerts.get_noca_road_status)

        pass_future = None
        if zone:
            slugs = fetch_pass_status.ZONE_TO_PASSES.get(zone, [])
            if slugs:
                pass_future = ex.submit(_safe_call, fetch_pass_status.get_passes, slugs)

        nwac_future = None
        if nwac_zone:
            nwac_future = ex.submit(_safe_call, fetch_nwac_zone.fetch_zone, nwac_zone)

        drive_future = None
        if trailhead_lat is not None and trailhead_lon is not None:
            drive_future = ex.submit(
                _safe_call, compute_drive_time.get_drive_time,
                home_lat, home_lon, trailhead_lat, trailhead_lon,
            )

        snotel_results = [snotel_futures[t].result() for t in panel]
        fzl_results = [fzl_futures[s["id"]].result() for s in fetch_freezing_level.STATIONS]
        nws_result = nws_future.result()
        nps_result = nps_future.result()
        pass_results = pass_future.result() if pass_future else None
        nwac_result = nwac_future.result() if nwac_future else None
        drive_result = drive_future.result() if drive_future else None

    # Pass-status: tuple of (passes, optional error) — unwrap
    if pass_results is None:
        passes_block = {"passes": [], "note": "No --zone supplied; pass status skipped."}
    elif isinstance(pass_results, tuple):
        passes, err = pass_results
        passes_block = {"passes": passes}
        if err:
            passes_block["error"] = err
    else:
        # Came back as an exception dict from _safe_call
        passes_block = {"passes": [], **pass_results}

    # Airmass-split note from the two RAOB results
    valid_fzl = [r["freezing_level_ft"] for r in fzl_results
                 if isinstance(r, dict) and r.get("freezing_level_ft") is not None]
    if len(valid_fzl) == 2:
        split = abs(valid_fzl[0] - valid_fzl[1])
        if split >= 2000:
            airmass_note = (f"Large UIL-OTX freezing-level gap ({split:,} ft, >2000) — "
                            "sharp airmass boundary across the Cascade crest; west and "
                            "east sides will diverge.")
        else:
            airmass_note = f"UIL-OTX freezing-level gap is {split:,} ft — single coherent airmass."
    else:
        split = None
        airmass_note = "Could not compute airmass split (missing RAOB data)."

    bundle: dict = {
        "peak": {
            "name": peak_name,
            "lat": lat,
            "lon": lon,
            "elev_ft": peak_elev,
        },
        "trip_date": trip_date.isoformat(),
        "sun_times": sun_times,
        "snotel_panel_triplets": panel,
        "snowpack": snotel_results,
        "freezing_level": {
            "stations": fzl_results,
            "airmass_split_ft": split,
            "airmass_note": airmass_note,
        },
        "weather": nws_result,
        "avalanche": nwac_result if nwac_result is not None
                     else {"note": "No --nwac-zone supplied; avalanche forecast skipped."},
        "passes": passes_block,
        "nps_alerts": nps_result,
    }
    if drive_result is not None:
        bundle["drive_time"] = {
            "home": {"lat": home_lat, "lon": home_lon},
            "trailhead": {"lat": trailhead_lat, "lon": trailhead_lon},
            **drive_result,
        }
    else:
        bundle["drive_time"] = {
            "note": "No --trailhead-lat/--trailhead-lon supplied; drive-time skipped."
        }
    return bundle


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lat", type=float, required=True, help="Peak latitude")
    p.add_argument("--lon", type=float, required=True, help="Peak longitude (negative for west)")
    p.add_argument("--peak-elev", type=int, required=True, help="Peak elevation in feet")
    p.add_argument("--peak-name", type=str, default=None, help="Peak name (display only)")
    p.add_argument("--zone", type=str, default=None,
                   help="WSDOT pass zone (e.g. cascade-east-north). "
                        "Omit to skip pass status. See: python fetch_pass_status.py --list")
    p.add_argument("--nwac-zone", type=str, default=None,
                   help="NWAC avalanche zone slug (e.g. cascade-east-north). "
                        "Omit to skip avalanche forecast. See: python fetch_nwac_zone.py --list")
    p.add_argument("--trailhead-lat", type=float, default=None,
                   help="Trailhead latitude (for drive-time calc; defaults to peak coords if --trailhead-lon also omitted)")
    p.add_argument("--trailhead-lon", type=float, default=None)
    p.add_argument("--home-lat", type=float, default=compute_drive_time.HOME_LAT_DEFAULT,
                   help=f"Home origin latitude (default {compute_drive_time.HOME_LAT_DEFAULT})")
    p.add_argument("--home-lon", type=float, default=compute_drive_time.HOME_LON_DEFAULT,
                   help=f"Home origin longitude (default {compute_drive_time.HOME_LON_DEFAULT})")
    p.add_argument("--date", type=str, default=None,
                   help="Trip date YYYY-MM-DD (default today, local PT)")
    p.add_argument("--forecast-hours", type=int, default=72,
                   help="NWS hourly periods to keep (default 72)")
    args = p.parse_args()

    trip_date = None
    if args.date:
        try:
            trip_date = date.fromisoformat(args.date)
        except ValueError:
            p.error("--date must be YYYY-MM-DD")

    bundle = build_bundle(
        lat=args.lat,
        lon=args.lon,
        peak_elev=args.peak_elev,
        peak_name=args.peak_name,
        zone=args.zone,
        nwac_zone=args.nwac_zone,
        trailhead_lat=args.trailhead_lat,
        trailhead_lon=args.trailhead_lon,
        home_lat=args.home_lat,
        home_lon=args.home_lon,
        trip_date=trip_date,
        forecast_hours=args.forecast_hours,
    )
    print(json.dumps(bundle, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
