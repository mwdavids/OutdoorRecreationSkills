# Outdoor Recreation Skills

Custom GitHub Copilot / Claude skills for Pacific Northwest outdoor recreation planning — mountain weather analysis, trip briefings, and peak bagging tracking.

## Skills

### [cascade-mountain-weather](skills/cascade-mountain-weather/SKILL.md)
Analyzes mountain weather forecasts for the Washington Cascade Mountains and recommends outdoor activities based on conditions. Fetches live data from NWS, NWAC, WSDOT, UW WRF, and USGS to *produce opinionated weekend briefings ranked by activity* (peak bagging, ski mountaineering, backcountry skiing, trail running, rock climbing, whitewater rafting).

**Triggers:** mountain weather, weekend plans, what to do outdoors, trip planning for the Cascades, NWAC, avalanche forecast, "what should I do this weekend"

### [trip-briefing](skills/trip-briefing/SKILL.md)
Generates peak-specific mountain trip briefings by gathering trip details and fetching live weather, snowpack (SNOTEL), avalanche, drive time, and trip report data. Produces a concise, actionable one-page briefing for an experienced mountaineer.

**Triggers:** plan a trip to a specific mountain, check conditions for a peak, go/no-go assessment, summit attempt planning, SNOTEL, specific Bulger peak

### [bulger-knowledge](skills/bulger-knowledge/SKILL.md)
Personal knowledge base for the Washington Bulger list (top 100 peaks): summit/attempt log, per-peak route beta, vetted trip-report links, and access notes. Supplements `trip-briefing` with personal context — past turnarounds, alternate routes, and beta that isn't in any public trip report. Other skills stay generic; this one is the opinionated personal layer.

**Triggers:** specific Bulger peak planning, "have I climbed X?", "what's left on the Bulger list?", peak-specific beta or trip-report requests

### [packing-list](skills/packing-list/SKILL.md)
Generates tailored outdoor trip packing lists from natural language trip descriptions, informed by a personal gear library and deep knowledge of PNW outdoor activities. Covers alpine climbing, ski touring, backpacking, rafting, snow camping, day hiking, trail running, and more — with season-specific adjustments, trip-type intelligence, and export-friendly output.

**Triggers:** packing list, what should I bring, gear list, kit list, load-out, packing for an outdoor trip

## Reference Data

> **Note:** These files are personalized to the repo owner's climbing history and objectives. If you're using these skills for yourself, update them with your own peak list, completion status, and home location (North Bend, WA is the default).

- **[bulger-peaks.json](skills/trip-briefing/references/bulger-peaks.json)** — Single source of truth for all 100 Bulger peaks: coordinates, elevation, NWAC zone, nearest SNOTEL, climbed status (49/100), ski mountaineering notes, prominence, and larch scenery

## Installation

To use these skills with GitHub Copilot in VS Code, copy the skill folders into your `~/.agents/skills/` directory:

```bash
cp -r skills/cascade-mountain-weather ~/.agents/skills/
cp -r skills/trip-briefing ~/.agents/skills/
cp -r skills/bulger-knowledge ~/.agents/skills/
cp -r skills/packing-list ~/.agents/skills/
```

## Home Base

North Bend, WA — all drive times and weather defaults are calibrated from here.

## Example Prompts

### Trip Briefings
- *"Create a trip briefing for a ski tour of Mt Daniels for this upcoming Sunday. Highlight the two different routes we might take depending on the snow line elevation."*
- *"Plan a trip briefing for Bonanza Peak via Holden Village for the last weekend in July. How's the approach looking?"*
- *"Generate a go/no-go for Forbidden Peak this Saturday. We're planning the West Ridge."*
- *"I want to ski Mount Adams this weekend. Give me the full briefing — corn cycle, weather window, and departure time from North Bend."*

### Weekend Weather & Activity Planning
- *"What should I do this weekend? I'm open to anything — peak bagging, skiing, trail running."*
- *"Is there a weather window for a big Bulger peak this weekend? I'd prefer something I haven't climbed yet."*
- *"Compare conditions for Gardner vs Remmel this weekend — which is the better day trip?"*
- *"What's the avalanche forecast look like for the Stevens Pass zone? I'm thinking about backcountry skiing."*

### Peak Tracking & Data
- *"Which unclimbed Bulgers are accessible right now given current road closures?"*
- *"What are my closest unclimbed Bulgers that would make good day trips?"*
- *"Show me all the unclimbed peaks I could combine into a multi-day trip in the Entiat area."*

### Packing Lists
- *"Generate a packing list for a ski mountaineering day trip on Mount Adams this Saturday."*
- *"What should I bring for a 3-day backpacking trip in the Enchantments in August?"*
- *"Make me an ultralight packing list for a winter day hike to Snow Lake."*
- *"I'm rafting the Wenatchee this weekend with 4 people — what do we need?"*

## Development

This repo has a three-layer testing strategy. Layers 1 and 2 are fast, deterministic, and run in pre-commit. Layer 3 is LLM-in-the-loop and runs out of band.

### Layer 1 — static integrity (`scripts/check_skills.py`)

Validates `SKILL.md` frontmatter, intra-skill markdown links, `bulger-peaks.json`, and `gear-library.json`. Stdlib-only.

```bash
python scripts/check_skills.py
```

Exits non-zero on schema breakage or broken cross-references.

### Layer 2 — trigger routing lint (`scripts/check_triggers.py`)

Lints whether the four `SKILL.md` descriptions actually distinguish themselves on a fixed set of routing prompts (`tests/trigger_fixtures.json`). Uses a smoothed IDF scorer over the description vocabularies — no LLM, no network. Stdlib-only.

```bash
python scripts/check_triggers.py            # warn-only (default)
python scripts/check_triggers.py --strict   # promote mismatches to fatal (CI mode)
CHECK_TRIGGERS_STRICT=1 python scripts/check_triggers.py  # same, via env
```

In default mode, routing mismatches print as `MISMATCH` lines but the script exits 0. This is intentional: descriptions evolve, and the lint is a visibility tool, not a hard gate.

### Pre-commit wiring

Both checks run on every commit via [pre-commit](https://pre-commit.com/):

```bash
pip install pre-commit
pre-commit install
```

See [`.pre-commit-config.yaml`](.pre-commit-config.yaml). Run manually against the whole tree:

```bash
pre-commit run --all-files
```

### Layer 3 — LLM-in-the-loop evals (out of band)

Each skill has an `evals/evals.json` file conforming to the [skill-creator schema](https://github.com/anthropics/skills) (`{skill_name, evals: [{id, prompt, expected_output, expectations}]}`). These define semantic acceptance criteria that require the live model to evaluate — they are *not* run in pre-commit.

To run them, use the [skill-creator](https://github.com/anthropics/skills) executor + grader pipeline (requires the Claude Code CLI). From a workspace where skill-creator is invokable:

```text
Use the skill-creator skill to run evals against skills/<skill-name>/evals/evals.json
```

Eval files live at:

- [`skills/bulger-knowledge/evals/evals.json`](skills/bulger-knowledge/evals/evals.json)
- [`skills/trip-briefing/evals/evals.json`](skills/trip-briefing/evals/evals.json)
- [`skills/cascade-mountain-weather/evals/evals.json`](skills/cascade-mountain-weather/evals/evals.json)
- [`skills/packing-list/evals/evals.json`](skills/packing-list/evals/evals.json)

### Repo layout

```text
scripts/   # versioned executables (Python stdlib only)
tests/     # fixtures consumed by scripts/
skills/    # the skills themselves; each has SKILL.md + references/ + evals/
tmp/       # gitignored throwaway / experiment scripts
```
