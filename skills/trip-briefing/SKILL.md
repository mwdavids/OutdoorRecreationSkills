---
name: trip-briefing
description: Generate a peak-specific mountain trip briefing by gathering trip details from the user and fetching live weather, snowpack, avalanche, drive time, and trip report data. Use this skill whenever the user asks to plan a trip to a specific mountain, generate a trip briefing, check conditions for a peak, asks "what are conditions like on [peak]", wants a go/no-go assessment for a climb, or mentions planning a summit attempt, ski descent, or scramble on a specific objective. Also trigger when the user mentions SNOTEL, trip briefing, peak conditions, or asks about a specific Bulger peak. Do NOT use for general weekend weather overviews (that's the cascade-mountain-weather skill) — this skill is for a specific peak or objective.
---

# Trip Briefing Generator

Mountain trip briefing assistant for an experienced PNW alpinist. Gather trip details through conversation, run the deterministic fetcher to pull live conditions, then synthesize a one-page go/no-go briefing.

## Step 1 — Interview

Ask only what isn't already in the user's message. Required:

1. **Peak / objective** — look up in `scripts/data/bulger-peaks.json` (or `references/bulger-peaks.json`) first for coords, elevation, NWAC zone, nearest SNOTEL.
2. **Trip dates** — specific date, range, or "next good window."
3. **Trip style** — peak bag, ski mountaineering, BC ski, alpine climb, glacier travel, rock, raft, run/hike. Drives which data matter.
4. **Estimated total trip duration** car-to-car (hours). Drives departure timing.
5. **Special notes** — bivy plans, partner experience, route variant.

Default home: **North Bend, WA** (47.4957, -121.7886). Past trip context from the user is gold — surface relevant prior attempts inline.

If the peak isn't in `bulger-peaks.json`, ask for coordinates or use USGS GNIS: `https://geonames.usgs.gov/api/features?featureName=PEAK_NAME&featureClass=Summit&limit=10`.

## Step 2 — Fetch deterministic data

Run the orchestrator. It fans out to 10 sub-fetchers in parallel and returns one JSON bundle:

```powershell
python skills/trip-briefing/scripts/fetch_briefing_bundle.py `
    --lat <lat> --lon <lon> --peak-elev <ft> --peak-name "<Name>" `
    --zone <wsdot-zone> --nwac-zone <nwac-zone-slug> `
    --trailhead-lat <lat> --trailhead-lon <lon> `
    --date <YYYY-MM-DD> --forecast-hours 12
```

Returns 11 top-level keys: `peak`, `trip_date`, `sun_times`, `snotel_panel_triplets`, `snowpack`, `freezing_level`, `weather`, `avalanche`, `passes`, `nps_alerts`, `drive_time`. Any single-source failure surfaces as `{"error": "..."}` inside that block — keep going.

See [scripts/README.md](scripts/README.md) for individual script CLIs (useful when you only need one slice — e.g. a refreeze check via `compute_wet_bulb.py`).

### Personal Bulger knowledge layer

If the peak is on the Bulger list, also pull the `bulger-knowledge` skill context before writing the briefing:

- `skills/bulger-knowledge/data/peaks/{slug}.md` — personal route beta, vetted TR links, access overrides.
- `skills/bulger-knowledge/data/summit-log.md` — prior attempts / turnarounds.

Surface personal notes inline with attribution, e.g. `**Personal note (2026-05-04 attempt):** …`. If they flag a route or crux not in public sources, escalate to **Seasonal Crux** or **Route Notes**. Slug = lowercase, hyphenated, drop `Mount/Mt`.

### Relevance over completeness

Skip sources that don't change the briefing. A July rock climb doesn't need SNOTEL or avalanche. A November snow-free scramble on an eastside peak doesn't need NWAC. The orchestrator fetches everything; *you* decide what makes it into the output.

## Step 3 — Synthesize the briefing

Render per [references/output-template.md](references/output-template.md). That file owns the full section scaffold (Bottom line + calendar offset chip + Summary + optional Seasonal Crux + Weather Window + Snow & Avalanche + Route Notes + Logistics + Gear + Resource Links) plus the voice / grounding / local-time rules.

Pull additional references **only as needed** for the trip in front of you:

| When … | Read |
|---|---|
| Trip style shapes inclusion / interpretation, or seasonal context matters | [references/trip-style-playbook.md](references/trip-style-playbook.md) |
| Spring volcano / corn ski timing | [references/corn-cycle.md](references/corn-cycle.md) |
| Post-storm powder shelf-life call | [references/powder-shelf-life.md](references/powder-shelf-life.md) |
| Avalanche assessment (in-season OR off-season proxies) | [references/avalanche-reasoning.md](references/avalanche-reasoning.md) |
| Real make-or-break section driven by time of year | [references/seasonal-crux-guide.md](references/seasonal-crux-guide.md) |
| Refreeze physics / wet-bulb interpretation | [references/refreeze-physics.md](references/refreeze-physics.md) |
| UIL/OTX RAOB observed freezing level reading | [references/upper-air-sanity-check.md](references/upper-air-sanity-check.md) |
| Pass status looks closed (especially PARTIALLY OPEN) | [references/wsdot-closure-parsing.md](references/wsdot-closure-parsing.md) |
| Trip is >3 days out — how much to trust the forecast | [references/forecast-coverage-bands.md](references/forecast-coverage-bands.md) |
| Snowpack vocab (corn, isothermal, bridge, etc.) | [references/snow-state-vocab.md](references/snow-state-vocab.md) |
| Sanity-checking a SNOTEL station pick | [references/snotel-stations.md](references/snotel-stations.md) |

## Step 4 — Save as HTML

After delivering the markdown briefing in chat, **always also save an HTML version** to `tmp/{peak-slug}-briefing-{trip-date}.html` for email-paste. See [references/html-output.md](references/html-output.md) for the template, section mapping, and hand-off line.

## Handoff to Packing List

The trip briefing is the primary planning entry point; the `packing-list` skill is a downstream artifact. When the user asks for a list after a briefing, hand off the structured context (peak, dates, style, weather window, snow/avy summary, hazards called out, access notes, daylight margin, group size) — do **not** re-interview. The packing-list skill asks only what the briefing didn't cover.

## Tone

Direct and opinionated — "Here's what I'd do," not "Here are options." Use mountain language naturally. Show your reasoning ("ridge building as trough exits east" not "fair weather expected"). Honest about uncertainty. Enthusiastic when conditions deserve stoke. Concise — fits on one page mentally; don't pad.
