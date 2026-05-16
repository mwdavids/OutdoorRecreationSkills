#!/usr/bin/env python3
"""Fetch SNOTEL snowpack data via NRCS Report Generator CSV.

Returns a compact JSON summary (current SWE, % of median, snow depth, recent
temps) plus a 14-day trend with melt-rate analysis, refreeze likelihood, and a
calendar-offset chip — so the model never has to parse raw CSV.

Ported from beta-bot/app/briefing/snowpack.py.

Usage:
  python fetch_snowpack.py 791:WA:SNTL                  # 14-day default
  python fetch_snowpack.py 791:WA:SNTL --current        # current day only
  python fetch_snowpack.py 791:WA:SNTL 515:WA:SNTL      # multi-station panel

Exits 0 on success, 1 on hard failure (network/HTTP error), 2 on argument error.
Stations that error out individually are reported in the JSON `errors` array
rather than failing the whole run.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

_BASE = "https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customSingleStationReport"
_TIMEOUT = 20
_UA = "OutdoorRecreationSkills/1.0 (trip-briefing fetcher)"
DATA_FILE = Path(__file__).parent / "data" / "snotel_stations.json"


def _load_station_db() -> dict:
    with DATA_FILE.open() as f:
        return json.load(f)


def _build_url(triplet: str, days_back: int) -> str:
    """NRCS CSV URL. days_back=0 → today only, days_back=14 → 14 days history."""
    return (
        f"{_BASE}/daily/{triplet}"
        f"%7Cid=%22%22%7Cname/-{days_back},0/"
        "WTEQ::value,WTEQ::pctOfMedian_1991,SNWD::value,TAVG::value"
        "?fitToScreen=false"
    )


def _http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "text/csv,*/*"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        return r.read().decode("utf-8", errors="replace")


def _parse_csv_rows(text: str) -> list[dict]:
    """Parse NRCS CSV into list of row dicts. Skips comment lines starting with #."""
    lines = [ln for ln in text.strip().split("\n") if ln and not ln.startswith("#")]
    if len(lines) < 2:
        return []
    header = [h.strip() for h in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        vals = line.split(",")
        row = {}
        for i, h in enumerate(header):
            row[h] = vals[i].strip() if i < len(vals) else ""
        rows.append(row)
    return rows


def _safe_float(val: str) -> Optional[float]:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _snowpack_age_note(pct: Optional[float]) -> str:
    """Map % of median to a calendar-offset chip (the renderer-extractable summary).

    This is the framing beta-bot uses: '~2 weeks behind season' is more actionable
    than a bare percentage. Negative = behind (less snow); positive = ahead (more snow).
    """
    if pct is None or pct <= 0:
        return ""
    if pct >= 115:
        return f"{pct:.0f}% of median — snowpack ~10-14 days ahead of season (more snow than normal)"
    if pct >= 95:
        return f"{pct:.0f}% of median — roughly on schedule"
    if pct >= 75:
        return f"{pct:.0f}% of median — snowpack ~10-14 days behind season (less snow than normal)"
    if pct >= 55:
        return f"{pct:.0f}% of median — snowpack ~3-4 weeks behind season"
    if pct >= 30:
        return f"{pct:.0f}% of median — well below normal, melting fast (~5-6 weeks ahead of calendar)"
    return f"{pct:.0f}% of median — essentially summer conditions for this elevation"


def fetch_station(triplet: str, db: dict, days: int = 14) -> dict:
    """Fetch one station. Returns dict with either data or an `error` field."""
    bad_set = set(db.get("bad_triplets", []))
    if triplet in bad_set:
        return {"station": triplet, "error": "known-bad triplet (hallucinated in past sessions)"}

    station_info = db["stations"].get(triplet, {})
    url = _build_url(triplet, days)

    try:
        text = _http_get(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return {"station": triplet, "error": f"http error: {e}"}

    if "Stations do not exist" in text:
        return {"station": triplet, "error": "NRCS reports station does not exist"}

    rows = _parse_csv_rows(text)
    if not rows:
        return {"station": triplet, "error": "empty CSV from NRCS"}

    # Build daily series
    daily = []
    for row in rows:
        vals = list(row.values())
        daily.append({
            "date": vals[0] if vals else "",
            "swe_in": _safe_float(vals[1]) if len(vals) > 1 else None,
            "pct_median": _safe_float(vals[2]) if len(vals) > 2 else None,
            "depth_in": _safe_float(vals[3]) if len(vals) > 3 else None,
            "avg_temp_f": _safe_float(vals[4]) if len(vals) > 4 else None,
        })

    today = daily[-1] if daily else {}
    oldest = daily[0] if daily else {}

    swe_today = today.get("swe_in")
    swe_oldest = oldest.get("swe_in")
    delta_swe = None
    melt_rate = None
    if swe_today is not None and swe_oldest is not None:
        delta_swe = round(swe_today - swe_oldest, 1)
        span_days = len(daily) - 1 if len(daily) > 1 else max(days, 1)
        melt_rate = round(delta_swe / span_days, 2) if span_days > 0 else None

    trend = "Stable"
    if delta_swe is not None:
        if delta_swe < -5:
            trend = "Rapid melt"
        elif delta_swe < -2:
            trend = "Moderate melt"
        elif delta_swe < 0:
            trend = "Slow melt"
        elif delta_swe > 2:
            trend = "Accumulating"
        elif delta_swe > 0:
            trend = "Slight gain"

    recent_temps = [d["avg_temp_f"] for d in daily[-3:] if d.get("avg_temp_f") is not None]
    min_recent_temp = min(recent_temps) if recent_temps else None
    refreeze_likely = min_recent_temp is not None and min_recent_temp < 32

    result = {
        "station": triplet,
        "station_name": station_info.get("name", ""),
        "station_elev_ft": station_info.get("elev_ft"),
        "station_lat": station_info.get("lat"),
        "station_lon": station_info.get("lon"),
        "region": station_info.get("region", ""),
        "date": today.get("date"),
        "swe_in": swe_today,
        "swe_pct_median": today.get("pct_median"),
        "depth_in": today.get("depth_in"),
        "avg_temp_f": today.get("avg_temp_f"),
        "calendar_offset_chip": _snowpack_age_note(today.get("pct_median")),
    }

    if days > 0:
        result.update({
            "trend_window_days": len(daily),
            "delta_swe_in": delta_swe,
            "melt_rate_in_per_day": melt_rate,
            "trend_label": trend,
            "min_recent_avg_temp_f": min_recent_temp,
            "recent_refreeze_likely": refreeze_likely,
        })

    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("triplets", nargs="+", help="One or more SNOTEL triplets (e.g. 791:WA:SNTL)")
    p.add_argument("--current", action="store_true", help="Current day only (days=0)")
    p.add_argument("--days", type=int, default=14, help="History window (default 14)")
    args = p.parse_args()

    db = _load_station_db()
    days = 0 if args.current else max(0, args.days)

    results = []
    errors = []
    for triplet in args.triplets:
        out = fetch_station(triplet, db, days)
        if out.get("error"):
            errors.append(out)
        else:
            results.append(out)

    payload = {"stations": results}
    if errors:
        payload["errors"] = errors
    print(json.dumps(payload, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
