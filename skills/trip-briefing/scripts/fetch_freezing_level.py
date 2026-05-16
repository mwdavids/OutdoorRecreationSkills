#!/usr/bin/env python3
"""Fetch observed upper-air soundings (UIL + OTX) from SPC and emit JSON summary.

Twice-daily (00Z/12Z) RAOB balloon launches at UIL (Quillayute, WA coast) and
OTX (Spokane, WA) give the only direct OBSERVATION of where the air column
crosses 0 degC and how hard the wind is blowing at ridgeline elevations.
NWS/MOS snow level is a model derivative; this is ground truth.

Use as a SANITY CHECK on the forecast freezing level — if model and observation
disagree significantly, drop confidence. Comparing UIL vs OTX also reveals
the airmass boundary across the Cascade crest.

Source: https://www.spc.noaa.gov/exper/soundings/LATEST/<STID>.txt
Free, no auth.

Ported from beta-bot/app/briefing/freezing_level.py.

Usage:
  python fetch_freezing_level.py            # both stations
  python fetch_freezing_level.py UIL        # one station
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Optional

_BASE = "https://www.spc.noaa.gov/exper/soundings/LATEST"
_UA = "OutdoorRecreationSkills/1.0 (upper-air-sanity-check)"
_TIMEOUT = 15
_M_TO_FT = 3.28084
_MISSING = -9999.0
_KEY_LEVELS_MB = [850, 700, 500]

STATIONS = [
    {"id": "UIL", "name": "Quillayute, WA", "side": "west"},
    {"id": "OTX", "name": "Spokane, WA",    "side": "east"},
]


def _http_get(url: str) -> Optional[str]:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            if r.status != 200:
                return None
            return r.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def _parse_title_valid_time(text: str) -> Optional[str]:
    m = re.search(r"%TITLE%\s*\n\s*\S+\s+(\d{6})/(\d{4})", text)
    if not m:
        return None
    yymmdd, hhmm = m.group(1), m.group(2)
    yy = int(yymmdd[0:2])
    year = 2000 + yy
    return f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]} {hhmm[0:2]}Z"


def _parse_levels(text: str) -> list[tuple]:
    out = []
    m = re.search(r"%RAW%\s*\n(.*?)%END%", text, re.DOTALL)
    if not m:
        return out
    for line in m.group(1).splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 6:
            continue
        try:
            pres = float(parts[0])
            hgt = float(parts[1])
            temp = float(parts[2])
            wdir = float(parts[4])
            wspd = float(parts[5])
        except ValueError:
            continue
        if pres == _MISSING or hgt == _MISSING:
            continue
        out.append((pres, hgt, temp, wdir, wspd))
    out.sort(key=lambda r: r[1])
    return out


def _interpolate_fzl_ft(levels: list[tuple]) -> Optional[int]:
    valid = [(h, t) for (_p, h, t, _wd, _ws) in levels if t != _MISSING]
    if len(valid) < 2:
        return None
    for i in range(1, len(valid)):
        h0, t0 = valid[i - 1]
        h1, t1 = valid[i]
        if t0 >= 0 >= t1 and t0 != t1:
            frac = t0 / (t0 - t1)
            h_fzl = h0 + frac * (h1 - h0)
            return int(round(h_fzl * _M_TO_FT))
        if i == 1 and t0 < 0:
            return int(round(h0 * _M_TO_FT))
    return None


def _wind_at_pressure(levels: list[tuple], target_mb: float) -> Optional[dict]:
    candidates = [
        (p, h, wd, ws) for (p, h, _t, wd, ws) in levels
        if wd != _MISSING and ws != _MISSING
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda r: abs(r[0] - target_mb))
    p, h, wd, ws = candidates[0]
    if abs(p - target_mb) > 25:
        return None
    return {
        "height_ft": int(round(h * _M_TO_FT)),
        "dir_deg": int(round(wd)) % 360,
        "speed_kt": int(round(ws)),
    }


def _compass(deg: int) -> str:
    points = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
              "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return points[int((deg % 360) / 22.5 + 0.5) % 16]


def fetch_station(station: dict) -> Optional[dict]:
    url = f"{_BASE}/{station['id']}.txt"
    text = _http_get(url)
    if not text or "%RAW%" not in text:
        return None
    levels = _parse_levels(text)
    if not levels:
        return None
    fzl_ft = _interpolate_fzl_ft(levels)
    winds = {}
    for mb in _KEY_LEVELS_MB:
        w = _wind_at_pressure(levels, mb)
        if w:
            w["dir_compass"] = _compass(w["dir_deg"])
            winds[f"{mb}mb"] = w
    if fzl_ft is None and not winds:
        return None
    return {
        "id": station["id"],
        "name": station["name"],
        "side": station["side"],
        "valid": _parse_title_valid_time(text),
        "freezing_level_ft": fzl_ft,
        "winds": winds,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("station_ids", nargs="*", help="UIL and/or OTX (default: both)")
    args = p.parse_args()

    wanted = [s["id"].upper() for s in STATIONS]
    if args.station_ids:
        ids = [x.upper() for x in args.station_ids]
        targets = [s for s in STATIONS if s["id"].upper() in ids]
    else:
        targets = STATIONS

    results = []
    errors = []
    for s in targets:
        r = fetch_station(s)
        if r:
            results.append(r)
        else:
            errors.append({"id": s["id"], "error": "fetch or parse failed (missed launch / network)"})

    payload: dict = {"stations": results}
    if errors:
        payload["errors"] = errors
    if len(results) == 2:
        fzls = [r["freezing_level_ft"] for r in results if r.get("freezing_level_ft") is not None]
        if len(fzls) == 2:
            payload["airmass_split_ft"] = abs(fzls[0] - fzls[1])
            payload["airmass_note"] = (
                "Large UIL-OTX freezing-level gap (>2000 ft) indicates a sharp airmass "
                "boundary across the Cascade crest; west and east sides will diverge."
                if abs(fzls[0] - fzls[1]) > 2000 else
                "UIL and OTX freezing levels are similar — coherent airmass across the state."
            )

    print(json.dumps(payload, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
