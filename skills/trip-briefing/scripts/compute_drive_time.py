"""Compute driving time + miles from a home location to a trailhead.

Tries Azure Maps Route Directions if AZURE_MAPS_KEY is set, otherwise falls
back to the free OSRM public demo. No haversine fallback — the Cascades crest
forces real road routes (e.g. North Bend → SR 20 east-side THs go via I-405/I-5)
that any great-circle × constant lies about. If both Azure Maps and OSRM fail,
returns ``{"error": "..."}`` rather than a fabricated estimate.

Usage:
  python compute_drive_time.py --home-lat 47.495 --home-lon -121.786 \\
      --lat 48.448 --lon -121.026

Defaults to North Bend, WA for --home-lat/--home-lon (user's home base).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

# Sensible default — North Bend, WA (user's home base).
HOME_LAT_DEFAULT = 47.495
HOME_LON_DEFAULT = -121.786

_AZURE_MAPS_URL = "https://atlas.microsoft.com/route/directions/json"
_OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
_TIMEOUT = 10
_UA = "OutdoorRecreationSkills/1.0 (drive-time)"


def _fetch_azure_maps(home_lat: float, home_lon: float,
                      lat: float, lon: float, key: str) -> Optional[tuple[float, float]]:
    """Returns (hours, miles) or None."""
    qs = urllib.parse.urlencode({
        "api-version": "1.0",
        "subscription-key": key,
        "query": f"{home_lat},{home_lon}:{lat},{lon}",
        "travelMode": "car",
        "routeType": "fastest",
        "traffic": "false",  # deterministic; no time-of-day variance
    })
    req = urllib.request.Request(f"{_AZURE_MAPS_URL}?{qs}", headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            if r.status != 200:
                return None
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        summary = data["routes"][0]["summary"]
        return (summary["travelTimeInSeconds"] / 3600.0,
                summary["lengthInMeters"] / 1609.344)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
            IndexError, json.JSONDecodeError, TimeoutError):
        return None


def _fetch_osrm(home_lat: float, home_lon: float,
                lat: float, lon: float) -> Optional[tuple[float, float]]:
    """Returns (hours, miles) or None via the free OSRM public demo."""
    url = f"{_OSRM_URL}/{home_lon},{home_lat};{lon},{lat}?overview=false"
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            if r.status != 200:
                return None
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        rt = data["routes"][0]
        return (rt["duration"] / 3600.0, rt["distance"] / 1609.344)
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError,
            IndexError, json.JSONDecodeError, TimeoutError):
        return None


def get_drive_time(home_lat: float, home_lon: float,
                   lat: float, lon: float) -> dict:
    """Try Azure Maps then OSRM. Returns {hours, miles, source} or {error}."""
    key = os.getenv("AZURE_MAPS_KEY", "").strip()
    if key:
        result = _fetch_azure_maps(home_lat, home_lon, lat, lon, key)
        if result is not None:
            hrs, mi = result
            return {"hours": round(hrs, 2), "miles": round(mi, 1),
                    "minutes": round(hrs * 60), "source": "azure_maps"}
    result = _fetch_osrm(home_lat, home_lon, lat, lon)
    if result is not None:
        hrs, mi = result
        return {"hours": round(hrs, 2), "miles": round(mi, 1),
                "minutes": round(hrs * 60), "source": "osrm"}
    return {"error": "Both Azure Maps and OSRM failed; no estimate produced.",
            "home": {"lat": home_lat, "lon": home_lon},
            "destination": {"lat": lat, "lon": lon}}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--home-lat", type=float, default=HOME_LAT_DEFAULT)
    p.add_argument("--home-lon", type=float, default=HOME_LON_DEFAULT)
    p.add_argument("--lat", type=float, required=True, help="Trailhead latitude")
    p.add_argument("--lon", type=float, required=True, help="Trailhead longitude")
    args = p.parse_args()

    print(json.dumps(get_drive_time(args.home_lat, args.home_lon, args.lat, args.lon), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
