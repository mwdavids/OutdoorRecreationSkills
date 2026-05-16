# trip-briefing — deterministic helper scripts

Stdlib-only Python scripts that fetch and structure the **non-negotiable factual
inputs** for a mountain trip briefing. Run from your terminal; pipe the JSON
into the conversation. This is the "do not let the model freelance" layer.

## Why scripts (vs. asking the model to fetch)

| Concern              | Model-driven web fetch              | These scripts                          |
| -------------------- | ----------------------------------- | -------------------------------------- |
| SNOTEL triplet IDs   | Routinely hallucinated              | Loaded from `data/snotel_stations.json` |
| WSDOT pass status    | Misreads "PARTIALLY OPEN" as CLOSED | Segment-aware classifier               |
| Wet-bulb refreeze    | Defaults to comparing air temp to 32 °F | Stull 2011 formula, correct threshold  |
| RAOB freezing level  | Pulls text, often misreads pressure-vs-height | Parses, interpolates, gives ft + winds |
| Cost per briefing    | Many tool calls, much parsing       | A handful of HTTP GETs, < 200 ms each  |

## Quick start

```powershell
# 1. Optional: set the WSDOT key (free, https://wsdot.wa.gov/traffic/api/)
$env:WSDOT_ACCESS_CODE = "your-key-here"

# 2. Pick stations for a peak (Buckner)
python pick_snotel_station.py --lat 48.448 --lon -121.026 --peak-elev 9080 --panel

# 3. Pull current snowpack for the panel
python fetch_snowpack.py 975:WA:SNTL 681:WA:SNTL 606:WA:SNTL

# 4. Pass status for the approach corridor (SR 20)
python fetch_pass_status.py --zone cascade-east-north

# 5. Upper-air sanity check (where is the actual freezing level?)
python fetch_freezing_level.py

# 6. Translate model air temp + RH into wet-bulb for refreeze call
python compute_wet_bulb.py --temp-f 34 --rh 85 --json
```

All scripts print JSON to stdout and `--help` for usage. Errors are returned
as `{"error": "..."}` payloads, never raised, so an orchestrator can keep
running when one source is down.

## Dependencies

**None.** Stdlib only (`urllib.request`, `json`, `argparse`, `math`). Works on
any Python 3.9+ — no `pip install` step.

## Environment variables

| Variable             | Required by            | How to get                                                |
| -------------------- | ---------------------- | --------------------------------------------------------- |
| `WSDOT_ACCESS_CODE`  | `fetch_pass_status.py` | Free signup at <https://wsdot.wa.gov/traffic/api/>        |
| `NPS_API_KEY`        | (future) `fetch_nps_alerts.py` | Free signup at <https://www.nps.gov/subjects/developer/> |

When a script needs a key that is missing it returns an `error` field with a
fallback instruction (typically: "scrape the public page instead").

## Data files

- `data/snotel_stations.json` — 24 verified Cascade SNOTEL stations + a
  blocklist of 7 triplets that have been hallucinated in prior sessions.
  Always verify against <https://nwcc-apps.sc.egov.usda.gov/imap/> before
  adding a new one.

## Failure philosophy

Each script exits **0** when it can return anything useful (even a partial
result with an `error` field). Exit code **1** only on hard failures with
nothing to report. The orchestrator (`fetch_briefing_bundle.py`) treats any
single source going down as recoverable, never fatal.

## Provenance

Logic ported from <https://github.com/midavids/beta-bot> (private).
Maintenance strategy: copy and accept drift — re-sync periodically rather than
share a library.
