"""Fetch the current NWAC avalanche forecast for a Cascades zone.

Uses avalanche.org's public API — the same backend nwac.us itself consumes:
  https://api.avalanche.org/v2/public/product?center_id=NWAC&type=forecast&zone_id=...

Public, no auth, versioned. Off-season responses come back as
``product_type == "summary"`` and we surface them with ``off_season=True``
plus null danger ratings.

Output normalizes the avalanche.org response into the dashed shape callers
already expect (day1/day2 danger by elevation, bottom_line, problems).

Usage:
  python fetch_nwac_zone.py --zone cascade-east-north
  python fetch_nwac_zone.py --list
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from typing import Optional

_PRODUCT_URL = "https://api.avalanche.org/v2/public/product"
_UA = "OutdoorRecreationSkills/1.0 (avalanche-forecast)"
_TIMEOUT = 20

# avalanche.org area `id` per NWAC zone (from /v2/public/products/map-layer/NWAC).
SLUG_TO_ZONE_ID: dict[str, int] = {
    "olympics": 1645,
    "cascade-west-north": 1646,
    "cascade-west-north-baker": 1646,  # alias
    "cascade-west-central": 1647,
    "cascade-west-south": 1648,
    "stevens-pass": 1649,
    "snoqualmie-pass": 1653,
    "cascade-east-north": 1654,
    "cascade-east-central": 1655,
    "cascade-east-south": 1656,
    "mt-hood": 1657,
}

SLUG_TO_NAME: dict[str, str] = {
    "olympics": "Olympics",
    "cascade-west-north": "West Slopes North",
    "cascade-west-north-baker": "West Slopes North",
    "cascade-west-central": "West Slopes Central",
    "cascade-west-south": "West Slopes South",
    "stevens-pass": "Stevens Pass",
    "snoqualmie-pass": "Snoqualmie Pass",
    "cascade-east-north": "East Slopes North",
    "cascade-east-central": "East Slopes Central",
    "cascade-east-south": "East Slopes South",
    "mt-hood": "Mt Hood",
}

# avalanche.org danger_level int → human label.
# 0 = No Rating (None), 1=Low, 2=Moderate, 3=Considerable, 4=High, 5=Extreme.
_DANGER_BY_INT = {1: "Low", 2: "Moderate", 3: "Considerable", 4: "High", 5: "Extreme"}

_COMPASS_ASPECTS = {
    "north", "northeast", "east", "southeast",
    "south", "southwest", "west", "northwest",
}
_ELEV_TERMS = ("above treeline", "near treeline", "below treeline")


class _HTMLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _strip_html(s: Optional[str], limit: int = 1200) -> str:
    if not s:
        return ""
    p = _HTMLStripper()
    try:
        p.feed(s)
    except Exception:
        return ""
    text = re.sub(r"\s+", " ", " ".join(p.parts)).strip()
    return text[:limit]


def _danger_label(level: object) -> Optional[str]:
    try:
        i = int(level)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return _DANGER_BY_INT.get(i)


def _parse_iso_date(ts: Optional[str]) -> Optional[str]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).date().isoformat()
    except (ValueError, TypeError):
        return None


def _danger_for_day(rows: list, valid_day: str) -> dict:
    out = {"low": None, "mid": None, "high": None}
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("valid_day", "")).lower() == valid_day:
            out["low"] = _danger_label(row.get("lower"))
            out["mid"] = _danger_label(row.get("middle"))
            out["high"] = _danger_label(row.get("upper"))
            break
    return out


def _normalize_problem(p: dict) -> dict:
    if not isinstance(p, dict):
        return {}
    name = (p.get("name") or p.get("avalanche_problem_name") or "").strip()

    min_size = max_size = ""
    size = p.get("size")
    if isinstance(size, list) and size:
        min_size = str(size[0]) if size[0] is not None else ""
        max_size = str(size[-1]) if size[-1] is not None else ""
    else:
        if p.get("size_min") is not None:
            min_size = str(p["size_min"])
        if p.get("size_max") is not None:
            max_size = str(p["size_max"])

    aspects: list[str] = []
    elevations: list[str] = []
    seen_a: set = set()
    seen_e: set = set()
    locations = p.get("location") or []
    if isinstance(locations, list):
        for loc in locations:
            if not isinstance(loc, str):
                continue
            low = loc.lower()
            for et in _ELEV_TERMS:
                if et in low and et not in seen_e:
                    elevations.append(et)
                    seen_e.add(et)
            asp = low.split()[0] if low.split() else ""
            if asp in _COMPASS_ASPECTS and asp not in seen_a:
                aspects.append(asp)
                seen_a.add(asp)

    return {
        "type": name,
        "likelihood": (p.get("likelihood") or "").strip(),
        "min_size": min_size,
        "max_size": max_size,
        "description": _strip_html(p.get("discussion") or "", 600),
        "aspects": aspects,
        "elevations": elevations,
    }


def fetch_zone(zone_slug: str) -> dict:
    """Fetch the current NWAC forecast for one zone. Returns dict (with `error` on failure)."""
    zone_id = SLUG_TO_ZONE_ID.get((zone_slug or "").lower())
    if zone_id is None:
        return {"error": f"Unknown NWAC zone slug: {zone_slug}",
                "valid_slugs": sorted(SLUG_TO_ZONE_ID)}

    qs = urllib.parse.urlencode({
        "center_id": "NWAC",
        "type": "forecast",
        "zone_id": zone_id,
    })
    req = urllib.request.Request(
        f"{_PRODUCT_URL}?{qs}",
        headers={"User-Agent": _UA, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            if r.status != 200:
                return {"error": f"avalanche.org HTTP {r.status}", "zone_slug": zone_slug}
            data = json.loads(r.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        return {"error": f"avalanche.org fetch failed: {type(e).__name__}: {e}",
                "zone_slug": zone_slug}

    if not isinstance(data, dict):
        return {"error": "avalanche.org returned non-dict payload", "zone_slug": zone_slug}

    product_type = (data.get("product_type") or "").lower()
    danger_rows = data.get("danger") or []
    day1 = _danger_for_day(danger_rows, "current")
    day2 = _danger_for_day(danger_rows, "tomorrow")

    is_offseason = product_type == "summary" or not any(
        v for v in (day1["high"], day1["mid"], day1["low"])
    )

    raw_problems = data.get("forecast_avalanche_problems") or []
    problems = [np for np in (_normalize_problem(p) for p in raw_problems) if np.get("type")]

    bottom_line = _strip_html(data.get("bottom_line"), limit=900)
    hazard = _strip_html(data.get("hazard_discussion"), limit=1500)
    if not bottom_line:
        bottom_line = hazard
    if is_offseason and not bottom_line:
        bottom_line = ("NWAC off-season — general avalanche advisory in effect. "
                       "Check page directly.")

    return {
        "zone_slug": zone_slug,
        "zone_names": [SLUG_TO_NAME.get(zone_slug.lower(), zone_slug)],
        "publish_date": _parse_iso_date(data.get("published_time")),
        "expires_date": _parse_iso_date(data.get("expires_time")),
        "day1_danger_high": day1["high"],
        "day1_danger_mid": day1["mid"],
        "day1_danger_low": day1["low"],
        "day2_danger_high": day2["high"],
        "day2_danger_mid": day2["mid"],
        "day2_danger_low": day2["low"],
        "bottom_line": bottom_line,
        "problems": problems,
        "snowpack_discussion": hazard,
        "off_season": is_offseason,
        "author": (data.get("author") or "").strip(),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--zone", type=str, help="NWAC zone slug (see --list)")
    p.add_argument("--list", action="store_true", help="List valid zone slugs")
    args = p.parse_args()

    if args.list:
        out = sorted(
            [{"slug": s, "zone_name": SLUG_TO_NAME.get(s, s), "avalanche_org_id": zid}
             for s, zid in SLUG_TO_ZONE_ID.items()],
            key=lambda r: r["slug"],
        )
        print(json.dumps({"zones": out}, indent=2))
        return 0

    if not args.zone:
        p.error("--zone is required (or use --list)")

    print(json.dumps(fetch_zone(args.zone), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
