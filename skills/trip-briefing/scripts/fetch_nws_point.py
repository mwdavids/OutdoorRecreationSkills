"""Fetch hourly weather forecast + daily extras for a lat/lon from NOAA / NWS.

Two-stage call to api.weather.gov:
  1. /points/{lat,lon}     → resolves grid (wfo, gridX, gridY) + station elevation
  2. /gridpoints/{wfo}/{x},{y}/forecast/hourly  → user-facing hourly
     /gridpoints/{wfo}/{x},{y}                  → raw gridpoint series
                                                  (wind gust, snow level,
                                                   snowfall, QPF, temp)

Emits a single JSON object with both raw hourly periods and a derived
`extras_by_day` block (one row per local Pacific date with the precip /
snow level / wind / temp extremes). The model writes the narrative on top.

No key required. NOAA api.weather.gov requires a User-Agent.

Usage:
  python fetch_nws_point.py --lat 48.448 --lon -121.026
  python fetch_nws_point.py --lat 48.448 --lon -121.026 --hours 48
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Optional
try:
    from zoneinfo import ZoneInfo
    _PT = ZoneInfo("America/Los_Angeles")
except ImportError:
    _PT = None  # type: ignore

_BASE = "https://api.weather.gov"
_UA = "OutdoorRecreationSkills/1.0 (trip-briefing)"
_TIMEOUT = 15
_RETRY_ATTEMPTS = 3
_RETRY_BACKOFF_S = (0.5, 1.5, 3.0)
_RETRY_STATUS = {500, 502, 503, 504, 522, 524}
LAPSE_RATE_F_PER_1000FT = 3.5  # PNW environmental lapse rate convention


def _http_get(url: str) -> Optional[tuple[int, str]]:
    """GET with retry on transient 5xx/network errors. Returns (status, body) or None."""
    req = urllib.request.Request(url, headers={
        "User-Agent": _UA,
        "Accept": "application/geo+json",
    })
    for attempt in range(_RETRY_ATTEMPTS):
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
                return (r.status, r.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            if e.code in _RETRY_STATUS and attempt < _RETRY_ATTEMPTS - 1:
                time.sleep(_RETRY_BACKOFF_S[attempt])
                continue
            return (e.code, "")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < _RETRY_ATTEMPTS - 1:
                time.sleep(_RETRY_BACKOFF_S[attempt])
                continue
            return None
    return None


def get_grid(lat: float, lon: float) -> Optional[dict]:
    """Resolve lat/lon → {wfo, gridX, gridY, elevation_ft, ...}."""
    res = _http_get(f"{_BASE}/points/{lat:.4f},{lon:.4f}")
    if not res or res[0] != 200:
        return None
    try:
        props = json.loads(res[1]).get("properties", {})
    except json.JSONDecodeError:
        return None
    elev = props.get("elevation", {})
    elev_m = elev.get("value") if isinstance(elev, dict) else None
    elev_ft = round(elev_m * 3.28084) if elev_m is not None else None
    return {
        "wfo": props.get("gridId"),
        "gridX": props.get("gridX"),
        "gridY": props.get("gridY"),
        "forecast_url": props.get("forecastHourly"),
        "gridpoint_url": props.get("forecastGridData"),
        "elevation_ft": elev_ft,
    }


def _expand_validtime(vt: str) -> list[datetime]:
    """NWS gridpoint validTime '2026-05-08T18:00:00+00:00/PT3H' → list of hourly UTC datetimes."""
    try:
        start_s, dur = vt.split("/")
        start = datetime.fromisoformat(start_s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return []
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?", dur)
    if not m:
        return []
    days = int(m.group(1) or 0)
    hours = int(m.group(2) or 0) + days * 24
    if hours <= 0:
        hours = 1
    base = start.replace(minute=0, second=0, microsecond=0)
    return [base + timedelta(hours=i) for i in range(hours)]


def _series_to_hourly(series: Optional[dict], conv=lambda v: v) -> dict:
    """Convert gridpoint values=[{validTime, value}] → {datetime: value}."""
    if not series:
        return {}
    out: dict = {}
    for v in series.get("values", []) or []:
        val = v.get("value")
        if val is None:
            continue
        for h in _expand_validtime(v.get("validTime", "")):
            out[h] = conv(val)
    return out


def _summarize_extras_by_day(gp: dict, tz) -> dict:
    """Bucket raw gridpoint series into per-local-date dicts with min/max/sum extremes.

    Output keys per date: wind_gust_max_mph, snow_level_ft_min/max, snowfall_in,
    qpf_in, temp_min_f, temp_max_f. Missing series simply omit their keys.
    """
    if not gp:
        return {}
    M_TO_FT = 3.28084
    KMH_TO_MPH = 0.621371
    MM_TO_IN = 0.0393701

    gust_unit = (gp.get("windGust") or {}).get("uom", "") or (gp.get("windGust") or {}).get("unitCode", "")

    def _wind_conv(v, unit):
        if unit and "m_s-1" in unit:
            return v * 2.23694
        return v * KMH_TO_MPH

    snow_level = _series_to_hourly(gp.get("snowLevel"), lambda v: v * M_TO_FT)
    snowfall = _series_to_hourly(gp.get("snowfallAmount"), lambda v: v * MM_TO_IN)
    qpf = _series_to_hourly(gp.get("quantitativePrecipitation"), lambda v: v * MM_TO_IN)
    gust = _series_to_hourly(gp.get("windGust"), lambda v: _wind_conv(v, gust_unit))
    temp = _series_to_hourly(gp.get("temperature"), lambda v: v * 9 / 5 + 32)

    by_day: dict = {}
    hrs = set(snow_level) | set(snowfall) | set(qpf) | set(gust) | set(temp)
    for h_utc in hrs:
        local = h_utc.astimezone(tz) if tz else h_utc
        bucket = by_day.setdefault(local.date(), {})
        if h_utc in gust:
            bucket.setdefault("_gusts", []).append(gust[h_utc])
        if h_utc in snow_level:
            bucket.setdefault("_snow_levels", []).append(snow_level[h_utc])
        if h_utc in snowfall:
            bucket["_snowfall"] = bucket.get("_snowfall", 0) + snowfall[h_utc]
        if h_utc in qpf:
            bucket["_qpf"] = bucket.get("_qpf", 0) + qpf[h_utc]
        if h_utc in temp:
            bucket.setdefault("_temps", []).append(temp[h_utc])

    out: dict = {}
    for d, b in by_day.items():
        row: dict = {}
        if b.get("_gusts"):
            row["wind_gust_max_mph"] = round(max(b["_gusts"]))
        if b.get("_snow_levels"):
            row["snow_level_ft_min"] = round(min(b["_snow_levels"]))
            row["snow_level_ft_max"] = round(max(b["_snow_levels"]))
        if "_snowfall" in b:
            row["snowfall_in"] = round(b["_snowfall"], 1)
        if "_qpf" in b:
            row["qpf_in"] = round(b["_qpf"], 2)
        if b.get("_temps"):
            row["temp_min_f"] = round(min(b["_temps"]))
            row["temp_max_f"] = round(max(b["_temps"]))
        if row:
            out[d.isoformat()] = row
    return out


def fetch_forecast(lat: float, lon: float, hours: int = 72) -> dict:
    """Top-level: hourly periods + per-day extras + grid metadata."""
    grid = get_grid(lat, lon)
    if not grid or not grid.get("wfo"):
        return {"error": "NWS /points lookup failed", "lat": lat, "lon": lon}

    base = f"{_BASE}/gridpoints/{grid['wfo']}/{grid['gridX']},{grid['gridY']}"
    hourly_res = _http_get(f"{base}/forecast/hourly")
    if not hourly_res or hourly_res[0] != 200:
        return {"error": "NWS hourly forecast failed", "grid": grid}

    try:
        hourly_data = json.loads(hourly_res[1])
        periods = hourly_data.get("properties", {}).get("periods", [])
    except json.JSONDecodeError:
        return {"error": "NWS hourly forecast unparseable", "grid": grid}

    extras_by_day: dict = {}
    grid_res = _http_get(base)
    if grid_res and grid_res[0] == 200:
        try:
            gp_props = json.loads(grid_res[1]).get("properties", {})
            # Elevation fallback if /points missed it
            if grid.get("elevation_ft") is None:
                gp_elev = gp_props.get("elevation", {})
                val = gp_elev.get("value") if isinstance(gp_elev, dict) else None
                unit = gp_elev.get("unitCode", "") if isinstance(gp_elev, dict) else ""
                if val is not None:
                    grid["elevation_ft"] = round(val) if "ft" in unit else round(val * 3.28084)
            extras_by_day = _summarize_extras_by_day(gp_props, _PT or timezone.utc)
        except (json.JSONDecodeError, Exception):
            extras_by_day = {}

    trimmed = []
    for p in periods[:hours]:
        trimmed.append({
            "time": p.get("startTime"),
            "temp_f": p.get("temperature"),
            "wind_speed": p.get("windSpeed"),
            "wind_dir": p.get("windDirection"),
            "precip_pct": (p.get("probabilityOfPrecipitation") or {}).get("value", 0),
            "short": p.get("shortForecast"),
            "is_day": p.get("isDaytime"),
        })

    return {
        "lat": lat,
        "lon": lon,
        "grid": grid,
        "lapse_rate_f_per_1000ft": LAPSE_RATE_F_PER_1000FT,
        "periods": trimmed,
        "extras_by_day": extras_by_day,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--hours", type=int, default=72, help="Hourly periods to keep (default 72)")
    args = p.parse_args()

    result = fetch_forecast(args.lat, args.lon, args.hours)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
