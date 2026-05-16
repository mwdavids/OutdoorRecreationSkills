"""Fetch park-level alerts from the NPS API for North Cascades National Park.

Useful for surfacing live closures of roads/services NPS owns rather than WSDOT:
Cascade River Rd, Stehekin Valley Shuttle/Road, Thunder Creek / Colonial Creek,
Ross Dam, etc.

Maps each park alert to a known road slug (via title/description keyword match)
and classifies it CLOSED / PARTIAL / OPEN / Unknown.

Requires NPS_API_KEY (free signup at https://www.nps.gov/subjects/developer/).
If unset or the call fails, every slug returns status=Unknown — the orchestrator
treats that as "fall back to seasonal heuristics" without crashing.

Usage:
  python fetch_nps_alerts.py
  python fetch_nps_alerts.py --slug cascade-river-rd
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

_URL = "https://developer.nps.gov/api/v1/alerts"
_PARK_CODE = "noca"
_UA = "OutdoorRecreationSkills/1.0 (nps-alerts)"
_TIMEOUT = 10

# Dashboard road slug → keywords (any-of in alert title/description) + UI label.
ROAD_KEYWORDS: dict[str, dict] = {
    "cascade-river-rd": {
        "label": "Cascade River Rd (NOCA)",
        "keywords": ["cascade river road", "cascade river rd"],
    },
    "stehekin-shuttle": {
        "label": "Stehekin Valley Shuttle",
        "keywords": ["stehekin shuttle", "stehekin valley shuttle", "shuttle bus"],
    },
    "stehekin-road": {
        "label": "Stehekin Valley Rd",
        "keywords": ["stehekin valley road", "stehekin road"],
    },
    "thunder-creek": {
        "label": "Thunder Creek / Colonial Creek",
        "keywords": ["thunder creek", "colonial creek"],
    },
    "ross-dam": {
        "label": "Ross Dam / Ross Lake area",
        "keywords": ["ross dam", "ross lake"],
    },
}

CLOSED_KEYS = ("closed", "closure", "not open", "unavailable", "no access")
PARTIAL_KEYS = ("delay", "reduced", "limited", "partial", "single lane", "one lane",
                "by reservation", "advisory")
OPEN_KEYS = ("open", "reopened", "now open")


def _classify_alert_status(text: str) -> str:
    """Return 'CLOSED' | 'PARTIAL' | 'OPEN' | '' for a free-text alert blob."""
    t = (text or "").lower()
    if any(k in t for k in CLOSED_KEYS):
        return "CLOSED"
    if any(k in t for k in PARTIAL_KEYS):
        return "PARTIAL"
    if any(k in t for k in OPEN_KEYS):
        return "OPEN"
    return ""


def _match_alert(alert: dict, keywords: list[str]) -> bool:
    blob = (" ".join([
        (alert.get("title") or ""),
        (alert.get("description") or ""),
    ])).lower()
    return any(k in blob for k in keywords)


def _build_record(slug: str, info: dict, alerts: list[dict]) -> dict:
    matched = [a for a in alerts if _match_alert(a, info["keywords"])]
    if not matched:
        return {"slug": slug, "label": info["label"], "status": "Unknown",
                "note": "", "url": ""}
    chosen = matched[0]
    status = ""
    for a in matched:
        text = (a.get("title") or "") + " " + (a.get("description") or "")
        s = _classify_alert_status(text)
        if s == "CLOSED":
            chosen = a
            status = "CLOSED"
            break
        if s and not status:
            status = s
            chosen = a
    if not status:
        status = "Unknown"
    return {
        "slug": slug,
        "label": info["label"],
        "status": status,
        "note": (chosen.get("title") or "")[:200],
        "url": chosen.get("url") or "",
    }


def _fetch_alerts() -> tuple[list[dict] | None, str | None]:
    """Hit NPS Alerts API. Returns (alerts, error). alerts is None on failure."""
    key = os.getenv("NPS_API_KEY", "").strip()
    if not key:
        return None, ("NPS_API_KEY env var missing — sign up for a free key at "
                      "https://www.nps.gov/subjects/developer/get-started.htm")
    qs = urllib.parse.urlencode({"parkCode": _PARK_CODE, "api_key": key, "limit": 50})
    req = urllib.request.Request(f"{_URL}?{qs}", headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            if r.status != 200:
                return None, f"NPS API HTTP {r.status}"
            data = json.loads(r.read().decode("utf-8", errors="replace"))
        return (data.get("data") or []), None
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        return None, f"NPS API fetch failed: {type(e).__name__}: {e}"


def get_noca_road_status() -> dict:
    """Return {roads: [...], error?: str}. Slugs with no matching alert get status='Unknown'."""
    alerts, err = _fetch_alerts()
    if alerts is None:
        roads = [
            {"slug": slug, "label": info["label"], "status": "Unknown",
             "note": "", "url": ""}
            for slug, info in ROAD_KEYWORDS.items()
        ]
        return {"roads": roads, "error": err}
    roads = [_build_record(slug, info, alerts) for slug, info in ROAD_KEYWORDS.items()]
    return {"roads": roads}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--slug", type=str, default=None,
                   help="Filter output to one road slug (default: all roads)")
    p.add_argument("--list", action="store_true", help="List known road slugs")
    args = p.parse_args()

    if args.list:
        out = sorted(
            [{"slug": s, "label": info["label"], "keywords": info["keywords"]}
             for s, info in ROAD_KEYWORDS.items()],
            key=lambda r: r["slug"],
        )
        print(json.dumps({"roads": out}, indent=2))
        return 0

    result = get_noca_road_status()
    if args.slug:
        result["roads"] = [r for r in result["roads"] if r["slug"] == args.slug]
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
