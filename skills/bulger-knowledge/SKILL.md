---
name: bulger-knowledge
description: Personal knowledge base for the Washington Bulger list (top 100 peaks). Provides the user's summit/attempt log, per-peak personal route beta, curated trip-report links, and access notes that supplement the generic trip-briefing and cascade-mountain-weather skills. Use this skill whenever the user is planning, attempting, or asking about a specific Bulger peak; asks about their Bulger list progress, remaining unclimbed peaks, or peak recommendations from the list; or when generating a trip briefing for a peak that has a corresponding `data/peaks/{slug}.md` file. Do NOT use this skill for non-Bulger objectives or generic weather/conditions queries.
---

# Bulger Knowledge

Personal, opinionated knowledge layer for the Washington Bulger list (top 100 peaks by prominence/elevation, per the Bulger compilation). This skill **supplements** — it does not replace — `trip-briefing` and `cascade-mountain-weather`. Those skills handle live data fetching and synthesis; this skill provides the **personal context** they should be primed with first:

- Which peaks the user has climbed, attempted, or turned around on, and why
- Hard-won route beta from past trips that isn't in any public trip report
- Curated, vetted trip-report links per peak (so the agent doesn't have to guess at search results)
- Access / road / permit notes per peak that are stickier than seasonal data
- Best-season window overrides where the JSON data in `trip-briefing/references/bulger-peaks.json` is wrong or oversimplified

The authoritative *structured* data (coordinates, elevation, NWAC zone, nearest SNOTEL, climbed flag) still lives in `skills/trip-briefing/references/bulger-peaks.json`. This skill is for **prose, links, and personal notes** — anything that doesn't belong in a JSON record.

## When to consult this skill

Always consult this skill (read the relevant files) when:

1. The user is planning a trip to a Bulger peak. Always check whether `data/peaks/{slug}.md` exists for that peak, and read it before generating the briefing.
2. The user asks about Bulger list progress: "what's left?", "closest unclimbed?", "what should I do this weekend that's a Bulger?", "have I climbed X?".
3. The user mentions a past attempt or turnaround on a Bulger peak — check `data/summit-log.md` for prior context before responding.
4. The user is comparing Bulger candidates ("Gardner vs Remmel this weekend").

You do not need to consult this skill for non-Bulger peaks (Olympics, Hood, Shasta, random Cascadian objectives off the list) or for purely weather/snowpack questions with no peak attached.

## File layout

```
data/
  summit-log.md              # User's climb/attempt log: dates, partners, results, turnarounds
  trip-report-sources.md     # Where to look for trip reports per region/style
  peaks/
    README.md                # Conventions for per-peak files + template
    {peak-slug}.md           # One file per peak with personal beta, links, access notes
```

**Slug convention:** lowercase, hyphenated, drop "Mount/Mt": `mount-buckner` → `buckner.md`, `seven-fingered-jack` → `seven-fingered-jack.md`, `north-gardner` → `north-gardner.md`. Match the `name` field in `bulger-peaks.json`, normalized.

A peak file may not exist yet. **Absence is normal** — only peaks the user has researched or visited get a file. If the user is planning a trip to a peak with no file, generate the briefing normally and offer to seed a peak file from the trip's findings.

## How to use during a trip briefing

When the `trip-briefing` skill is generating a briefing for a Bulger peak:

1. After looking up the peak in `bulger-peaks.json`, check for `skills/bulger-knowledge/data/peaks/{slug}.md` and read it if present.
2. Check `skills/bulger-knowledge/data/summit-log.md` for any prior attempts on this peak — these often contain the most relevant beta.
3. Surface the personal beta and trip-report links **inline** in the briefing, clearly attributed (e.g., "**Personal note (2026-05-04 attempt):** Sahale-Boston Col was impassable steep snow…").
4. If the peak file recommends an alternate route or flags a crux not in public reports, escalate that to the briefing's **Hazards** or **Route notes** section.

## How to use for list-status / planning queries

For queries like "which unclimbed Bulgers are accessible right now":

1. Read `data/summit-log.md` for the climbed/unclimbed split (this is the user-curated source of truth for *status*, while `bulger-peaks.json` `climbed` field should be kept in sync).
2. Cross-reference with seasonal access (gate openings, road status from `cascade-mountain-weather` or current WSDOT/NPS alerts).
3. Prefer recommending peaks the user has *researched* (peak file exists) or that match their stated style preferences.

## Maintenance — keeping data fresh

After any Bulger trip (summit or turnaround), prompt the user to:

- Update `data/summit-log.md` with date, partners, result, and any notable beta.
- Add or update the peak's file in `data/peaks/` with what was learned.
- Update the `climbed` field in `skills/trip-briefing/references/bulger-peaks.json` if a summit was logged.

Treat the summit log as the source of truth for completion status; if it disagrees with `bulger-peaks.json`, the log wins and the JSON should be updated.
