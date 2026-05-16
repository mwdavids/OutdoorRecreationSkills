#!/usr/bin/env python3
"""Pick the best SNOTEL station(s) for a given peak / coordinate.

Loads the bundled verified-station list (data/snotel_stations.json) and
returns either:
  - the single best primary station for a lat/lon (geographic + elevation match), or
  - a 2-3 station panel that brackets the approach elevation (when --panel is set).

This is deterministic and avoids the model hallucinating triplets.

Usage:
  python pick_snotel_station.py --lat 48.45 --lon -121.05 --peak-elev 6975
  python pick_snotel_station.py --lat 48.45 --lon -121.05 --peak-elev 6975 --panel
  python pick_snotel_station.py --list
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "snotel_stations.json"


def _load_stations() -> dict:
    with DATA_FILE.open() as f:
        data = json.load(f)
    return data


def _approx_dist_mi(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Equirectangular approximation, miles. Adequate for ranking nearby stations."""
    dlat = (lat1 - lat2) * 69.0
    dlon = (lon1 - lon2) * 46.5
    return (dlat * dlat + dlon * dlon) ** 0.5


def pick_primary(stations: dict, lat: float, lon: float, peak_elev_ft: int) -> str:
    """Return the single best station triplet for a peak.

    Score = elevation mismatch (ft) + 100 * geographic distance (mi).
    Approach elevation is approximated as ~60% of peak elevation.
    """
    target_elev = peak_elev_ft * 0.6
    best = min(
        stations.keys(),
        key=lambda t: abs(stations[t]["elev_ft"] - target_elev)
        + 100 * _approx_dist_mi(lat, lon, stations[t]["lat"], stations[t]["lon"]),
    )
    return best


def pick_panel(stations: dict, lat: float, lon: float, peak_elev_ft: int,
               radius_mi: float = 50.0) -> list[str]:
    """Return a 2-3 station panel bracketing approach elevation, within radius_mi."""
    primary = pick_primary(stations, lat, lon, peak_elev_ft)
    primary_elev = stations[primary]["elev_ft"]

    candidates = [
        (t, info) for t, info in stations.items()
        if t != primary
        and _approx_dist_mi(lat, lon, info["lat"], info["lon"]) <= radius_mi
    ]

    def _score(info, target):
        return abs(info["elev_ft"] - target) + 100 * _approx_dist_mi(
            lat, lon, info["lat"], info["lon"]
        )

    lower_pool = [c for c in candidates if c[1]["elev_ft"] < primary_elev - 500]
    higher_pool = [c for c in candidates if c[1]["elev_ft"] > primary_elev + 500]
    lower = min(lower_pool, key=lambda x: _score(x[1], primary_elev))[0] if lower_pool else None
    higher = min(higher_pool, key=lambda x: _score(x[1], primary_elev))[0] if higher_pool else None

    panel = []
    if lower:
        panel.append(lower)
    panel.append(primary)
    if higher:
        panel.append(higher)
    return panel


def _format_station(triplet: str, info: dict, lat: float | None = None, lon: float | None = None) -> dict:
    out = {"triplet": triplet, **info}
    if lat is not None and lon is not None:
        out["distance_mi"] = round(_approx_dist_mi(lat, lon, info["lat"], info["lon"]), 1)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lat", type=float, help="Peak latitude")
    p.add_argument("--lon", type=float, help="Peak longitude (negative for west)")
    p.add_argument("--peak-elev", type=int, help="Peak summit elevation in feet")
    p.add_argument("--panel", action="store_true",
                   help="Return a 2-3 station bracketing panel instead of just the primary")
    p.add_argument("--radius-mi", type=float, default=50.0,
                   help="Max distance for panel candidates (default 50)")
    p.add_argument("--list", action="store_true", help="List all verified stations and exit")
    args = p.parse_args()

    data = _load_stations()
    stations = data["stations"]

    if args.list:
        out = sorted(
            [{"triplet": t, **info} for t, info in stations.items()],
            key=lambda r: (r["region"], -r["elev_ft"]),
        )
        print(json.dumps({"stations": out, "bad_triplets": data["bad_triplets"]}, indent=2))
        return 0

    if args.lat is None or args.lon is None or args.peak_elev is None:
        p.error("--lat, --lon, and --peak-elev are required (or use --list)")

    if args.panel:
        panel = pick_panel(stations, args.lat, args.lon, args.peak_elev, args.radius_mi)
        result = {
            "input": {"lat": args.lat, "lon": args.lon, "peak_elev_ft": args.peak_elev,
                      "approach_elev_target_ft": int(args.peak_elev * 0.6)},
            "panel": [_format_station(t, stations[t], args.lat, args.lon) for t in panel],
        }
    else:
        primary = pick_primary(stations, args.lat, args.lon, args.peak_elev)
        result = {
            "input": {"lat": args.lat, "lon": args.lon, "peak_elev_ft": args.peak_elev,
                      "approach_elev_target_ft": int(args.peak_elev * 0.6)},
            "primary": _format_station(primary, stations[primary], args.lat, args.lon),
        }

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
