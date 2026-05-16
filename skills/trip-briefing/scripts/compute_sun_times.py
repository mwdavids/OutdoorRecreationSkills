"""Compute sunrise / sunset / civil twilight + day length for a lat/lon/date.

Uses the NOAA Solar Calculator equations (no pip deps; beta-bot used `astral`
but we want stdlib-only). Accurate to within a minute or two — plenty for
trip-planning departure math.

Reference: https://gml.noaa.gov/grad/solcalc/calcdetails.html

Usage:
  python compute_sun_times.py --lat 48.448 --lon -121.026 --date 2026-05-16
  python compute_sun_times.py --lat 48.448 --lon -121.026          # today (local PT)
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
    _PT = ZoneInfo("America/Los_Angeles")
except ImportError:
    _PT = None  # type: ignore

# Solar altitude angles (degrees below horizon).
#   sunrise/sunset = -0.833° (sun's apparent radius + atmospheric refraction)
#   civil twilight = -6° (usable hiking light begins/ends)
_ZENITH_SUNRISE = 90.833
_ZENITH_CIVIL = 96.0


def _julian_day(d: date) -> float:
    """Julian Day Number for noon UT on date d."""
    y, m, day = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day + b - 1524.5


def _solar_event_utc(d: date, lat: float, lon: float, zenith_deg: float,
                     rising: bool) -> float | None:
    """NOAA Solar Calculator: return UTC fractional hours for event, or None
    if event does not occur (e.g. polar day/night)."""
    # Day of year, longitude hour
    n = d.toordinal() - date(d.year, 1, 1).toordinal() + 1
    lng_hour = lon / 15.0

    # Approximate time
    if rising:
        t = n + ((6 - lng_hour) / 24.0)
    else:
        t = n + ((18 - lng_hour) / 24.0)

    # Sun's mean anomaly
    M = (0.9856 * t) - 3.289
    # Sun's true longitude
    L = M + (1.916 * math.sin(math.radians(M))) + (0.020 * math.sin(math.radians(2 * M))) + 282.634
    L = L % 360

    # Sun's right ascension (adjusted into same quadrant as L)
    RA = math.degrees(math.atan(0.91764 * math.tan(math.radians(L)))) % 360
    Lquadrant = (math.floor(L / 90)) * 90
    RAquadrant = (math.floor(RA / 90)) * 90
    RA = RA + (Lquadrant - RAquadrant)
    RA = RA / 15.0  # hours

    # Sun's declination
    sin_dec = 0.39782 * math.sin(math.radians(L))
    cos_dec = math.cos(math.asin(sin_dec))

    # Sun's local hour angle
    cosH = (math.cos(math.radians(zenith_deg)) - (sin_dec * math.sin(math.radians(lat)))) \
        / (cos_dec * math.cos(math.radians(lat)))
    if cosH > 1:
        return None  # sun never rises on this date at this lat
    if cosH < -1:
        return None  # sun never sets

    if rising:
        H = 360 - math.degrees(math.acos(cosH))
    else:
        H = math.degrees(math.acos(cosH))
    H = H / 15.0  # hours

    # Local mean time of event
    T = H + RA - (0.06571 * t) - 6.622
    UT = (T - lng_hour) % 24
    return UT


def _ut_hours_to_datetime(d: date, ut_hours: float) -> datetime:
    """Given a date and fractional UT hours, return a UTC datetime."""
    base = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    return base + timedelta(hours=ut_hours)


def _fmt_local(dt: datetime) -> str:
    if _PT is not None:
        dt = dt.astimezone(_PT)
    return dt.strftime("%I:%M %p").lstrip("0")


def get_sun_times(lat: float, lon: float, d: date) -> dict:
    """Return sunrise / sunset / civil dawn-dusk / day length for date d at lat/lon."""
    events = {
        "sunrise": (_ZENITH_SUNRISE, True),
        "sunset":  (_ZENITH_SUNRISE, False),
        "dawn":    (_ZENITH_CIVIL, True),
        "dusk":    (_ZENITH_CIVIL, False),
    }
    out: dict = {"date": d.isoformat(), "lat": lat, "lon": lon}
    times_utc: dict = {}
    for name, (z, rising) in events.items():
        ut = _solar_event_utc(d, lat, lon, z, rising)
        if ut is None:
            out[name] = None
            out[f"{name}_local"] = None
            continue
        dt_utc = _ut_hours_to_datetime(d, ut)
        times_utc[name] = dt_utc
        out[name] = dt_utc.isoformat()
        out[f"{name}_local"] = _fmt_local(dt_utc)

    if "sunrise" in times_utc and "sunset" in times_utc:
        delta = (times_utc["sunset"] - times_utc["sunrise"]).total_seconds() / 3600.0
        # Handle the case where sunset wrapped to next UTC day
        if delta < 0:
            delta += 24
        out["day_length_hours"] = round(delta, 1)
    else:
        out["day_length_hours"] = None
    out["tz_label"] = "PT" if _PT else "UTC"
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--date", type=str, default=None,
                   help="YYYY-MM-DD; defaults to today (local PT)")
    args = p.parse_args()

    if args.date:
        try:
            d = date.fromisoformat(args.date)
        except ValueError:
            p.error("--date must be YYYY-MM-DD")
    else:
        if _PT is not None:
            d = datetime.now(_PT).date()
        else:
            d = date.today()

    print(json.dumps(get_sun_times(args.lat, args.lon, d), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
