#!/usr/bin/env python3
"""Fetch WSDOT Mountain Pass conditions and classify status with segment-aware logic.

The WSDOT API returns free-text RoadCondition + two RestrictionText fields per
pass. Models routinely misread these (declaring a pass CLOSED when only one
direction or one segment is shut). This script applies the same deterministic
classification beta-bot uses so the model gets a clean OPEN / PARTIAL / CLOSED
verdict plus the underlying text.

Requires WSDOT_ACCESS_CODE env var (free at https://wsdot.wa.gov/traffic/api/).
If the key is missing, exits 0 with an `error` payload so the orchestrator can
fall back to scraping wsdot.com.

Usage:
  python fetch_pass_status.py snoqualmie stevens north-cascade-hwy
  python fetch_pass_status.py --zone cascade-west-central
  python fetch_pass_status.py --list

Ported from beta-bot/app/briefing/road_status.py.
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

_API_URL = (
    "https://wsdot.wa.gov/traffic/api/MountainPassConditions/"
    "MountainPassConditionsREST.svc/GetMountainPassConditionsAsJson"
)
_TIMEOUT = 15
_UA = "OutdoorRecreationSkills/1.0 (pass-status)"

PASSES: dict[str, dict] = {
    "north-cascade-hwy": {"name": "SR 20 North Cascades Hwy", "highway": "SR 20", "match": "north cascade"},
    "snoqualmie":        {"name": "Snoqualmie Pass",          "highway": "I-90",  "match": "snoqualmie"},
    "stevens":           {"name": "Stevens Pass",              "highway": "US 2",  "match": "stevens"},
    "white":             {"name": "White Pass",                "highway": "US 12", "match": "white pass"},
    "chinook":           {"name": "Chinook Pass",              "highway": "SR 410","match": "chinook"},
    "cayuse":            {"name": "Cayuse Pass",               "highway": "SR 410","match": "cayuse"},
    "mt-baker-hwy":      {"name": "SR 542 Mt Baker Hwy",       "highway": "SR 542","match": "mount baker"},
    "blewett":           {"name": "Blewett Pass",              "highway": "US 97", "match": "blewett"},
    "loup-loup":         {"name": "Loup Loup Pass",            "highway": "SR 20", "match": "loup loup"},
    "sherman":           {"name": "Sherman Pass",              "highway": "SR 20", "match": "sherman"},
}

ZONE_TO_PASSES: dict[str, list[str]] = {
    "cascade-west-north-baker": ["mt-baker-hwy", "north-cascade-hwy"],
    "cascade-west-north":       ["mt-baker-hwy", "north-cascade-hwy"],
    "cascade-west-central":     ["north-cascade-hwy", "stevens"],
    "cascade-west-south":       ["chinook", "cayuse", "white"],
    "stevens-pass":             ["stevens"],
    "snoqualmie-pass":          ["snoqualmie"],
    "cascade-east-north":       ["north-cascade-hwy", "loup-loup", "sherman"],
    "cascade-east-central":     ["stevens", "snoqualmie", "blewett"],
    "cascade-east-south":       ["white", "chinook", "cayuse"],
    "mt-hood":                  [],
    "olympics":                 [],
}


def _restriction_text(r: Optional[dict]) -> str:
    if not r:
        return ""
    txt = (r.get("RestrictionText") or "").strip()
    if txt.lower() in ("", "no restrictions"):
        return ""
    direction = (r.get("TravelDirection") or "").strip()
    return f"{direction}: {txt}" if direction else txt


def _classify(road_condition: str, restrictions: list[str]) -> str:
    """Return 'PARTIAL', 'CLOSED', or '' based on free-text + restrictions.

    Segment-aware: 'reopened PARTIALLY from the east side up to MP 156' is
    partial, not a full closure. A single-direction closure with the other
    direction unmentioned is also partial.
    """
    blob = " ".join([road_condition] + restrictions).lower()
    has_closed = "closed" in blob or "closure" in blob
    if not has_closed:
        return ""
    partial_markers = ("partial", "partially", "reopened from", "open from the",
                       "open to mp", "up to mp")
    if any(m in blob for m in partial_markers):
        return "PARTIAL"
    direction_closures = sum(1 for r in restrictions if "closed" in r.lower())
    if direction_closures == 1 and len(restrictions) >= 2:
        return "PARTIAL"
    return "CLOSED"


def _fetch_all() -> Optional[list[dict]]:
    code = os.environ.get("WSDOT_ACCESS_CODE", "").strip()
    if not code:
        return None
    params = urllib.parse.urlencode({"AccessCode": code})
    url = f"{_API_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return None


def _build_record(pass_slug: str, info: dict, raw: dict) -> dict:
    road_condition = (raw.get("RoadCondition") or "").strip()
    weather = (raw.get("WeatherCondition") or "").strip()
    temp_f = raw.get("TemperatureInFahrenheit")
    elev_ft = raw.get("ElevationInFeet")
    travel_advisory = bool(raw.get("TravelAdvisoryActive"))
    updated = (raw.get("DateUpdated") or "").strip()

    r1 = _restriction_text(raw.get("RestrictionOne"))
    r2 = _restriction_text(raw.get("RestrictionTwo"))
    restrictions = [r for r in (r1, r2) if r]

    closure_kind = _classify(road_condition, restrictions)
    if closure_kind:
        status = closure_kind
    elif road_condition:
        status = "OPEN"
    else:
        status = "UNKNOWN"

    parts = []
    if road_condition:
        parts.append(road_condition)
    if restrictions:
        parts.append(" / ".join(restrictions))
    if travel_advisory:
        parts.append("Travel advisory active")
    if weather and weather.lower() not in ("", "clear", "no data"):
        parts.append(f"Weather: {weather}")
    if temp_f is not None:
        parts.append(f"{temp_f}\u00b0F")
    conditions = " \u2014 ".join(parts)[:400]

    traction = ""
    for r in restrictions:
        rl = r.lower()
        if "chain" in rl or "traction" in rl:
            traction = r
            break

    return {
        "pass_slug": pass_slug,
        "pass_name": info["name"],
        "highway": info["highway"],
        "status": status,
        "traction": traction,
        "conditions": conditions,
        "elevation_ft": elev_ft,
        "updated": updated,
        "url": "https://wsdot.com/travel/real-time/mountainpasses",
    }


def get_passes(slugs: list[str]) -> tuple[list[dict], Optional[str]]:
    all_passes = _fetch_all()
    if all_passes is None:
        return [], "WSDOT_ACCESS_CODE missing or API unreachable — fall back to scraping wsdot.com pages"
    results = []
    not_found = []
    for slug in slugs:
        info = PASSES.get(slug)
        if not info:
            not_found.append(slug)
            continue
        match = info["match"]
        found = False
        for raw in all_passes:
            name = (raw.get("MountainPassName") or "").lower()
            if match in name:
                results.append(_build_record(slug, info, raw))
                found = True
                break
        if not found:
            not_found.append(slug)
    err = f"slugs not matched in API: {not_found}" if not_found else None
    return results, err


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slugs", nargs="*", help="Pass slugs (see --list)")
    p.add_argument("--zone", help="NWAC zone slug (auto-selects relevant passes)")
    p.add_argument("--list", action="store_true", help="List known pass slugs and zone mapping")
    args = p.parse_args()

    if args.list:
        print(json.dumps({
            "passes": {k: {"name": v["name"], "highway": v["highway"]} for k, v in PASSES.items()},
            "zones": ZONE_TO_PASSES,
        }, indent=2))
        return 0

    slugs = list(args.slugs)
    if args.zone:
        z = ZONE_TO_PASSES.get(args.zone, [])
        slugs.extend([s for s in z if s not in slugs])

    if not slugs:
        p.error("Provide pass slugs or --zone (or --list)")

    results, err = get_passes(slugs)
    payload: dict = {"passes": results}
    if err:
        payload["error"] = err
    print(json.dumps(payload, indent=2))
    return 0 if results or err else 1


if __name__ == "__main__":
    sys.exit(main())
