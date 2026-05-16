#!/usr/bin/env python3
"""Compute wet-bulb temperature from air temp + relative humidity.

Uses Stull (2011) regression — accurate to within ~0.3 °C across the range
-20 °C to +50 °C and 5-99% RH at sea-level pressure. Adequate for the
"did it refreeze tonight?" decision.

Why wet-bulb instead of air temp:
  On a humid Cascade night, T_air can read 32-34°F while T_wet < 30°F as
  evaporative cooling drops the snow surface below the ambient reading.
  Wet-bulb crossing freezing is the right threshold for refreeze; air temp
  is a proxy that overstates marginal nights.

Reference (formula only):
  Stull, R. (2011). Wet-Bulb Temperature from Relative Humidity and Air
  Temperature. J. Appl. Meteorol. Climatol., 50(11), 2267-2269.

Usage:
  python compute_wet_bulb.py --temp-f 34 --rh 85
  python compute_wet_bulb.py --temp-c 1.1 --rh 85 --json
"""
from __future__ import annotations

import argparse
import json
import math
import sys


def wet_bulb_c(temp_c: float, rh_pct: float) -> float:
    """Wet-bulb temperature in Celsius."""
    rh = max(1.0, min(100.0, rh_pct))
    t = temp_c
    tw = (
        t * math.atan(0.151977 * math.sqrt(rh + 8.313659))
        + math.atan(t + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * (rh ** 1.5) * math.atan(0.023101 * rh)
        - 4.686035
    )
    return tw


def wet_bulb_f(temp_f: float, rh_pct: float) -> float:
    """Wet-bulb temperature in Fahrenheit."""
    t_c = (temp_f - 32.0) * 5.0 / 9.0
    tw_c = wet_bulb_c(t_c, rh_pct)
    return tw_c * 9.0 / 5.0 + 32.0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--temp-f", type=float, help="Air temperature in Fahrenheit")
    g.add_argument("--temp-c", type=float, help="Air temperature in Celsius")
    p.add_argument("--rh", type=float, required=True, help="Relative humidity, 0-100 (percent)")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of plain number")
    args = p.parse_args()

    if args.temp_f is not None:
        wb_f = wet_bulb_f(args.temp_f, args.rh)
        wb_c = (wb_f - 32.0) * 5.0 / 9.0
        t_f, t_c = args.temp_f, (args.temp_f - 32.0) * 5.0 / 9.0
    else:
        wb_c = wet_bulb_c(args.temp_c, args.rh)
        wb_f = wb_c * 9.0 / 5.0 + 32.0
        t_c, t_f = args.temp_c, args.temp_c * 9.0 / 5.0 + 32.0

    if args.json:
        out = {
            "air_temp_f": round(t_f, 1),
            "air_temp_c": round(t_c, 1),
            "rh_pct": args.rh,
            "wet_bulb_f": round(wb_f, 1),
            "wet_bulb_c": round(wb_c, 1),
            "below_freezing_air": t_f < 32.0,
            "below_freezing_wetbulb": wb_f < 32.0,
            "refreeze_basis": "wet-bulb < 32 F is the right threshold for snow surface refreeze",
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"{wb_f:.1f} F  /  {wb_c:.1f} C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
