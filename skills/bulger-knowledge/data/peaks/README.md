# Per-Peak Files — Conventions & Template

One folder per Bulger peak the user has researched, attempted, or summitted. **Absence of a file is fine** — peaks get a file only when there's something worth writing down.

## Two-tier structure

```
peaks/
  {slug}.md                  # peak-wide: stable facts, durable beta, links
  {slug}/                    # trip-specific (only created when needed)
    YYYY-MM-DD-{kind}.md     # personal trips (attempt | summit | recon)
    references/              # third-party TRs worth preserving in detail
      YYYY-MM-DD-{author-or-source}.md
```

**Why split:** peak-wide files are durable curation (years), trip files are append-only history (never edited), reference files are cached third-party beta (refreshed per scrape). Mixing them stops scaling past the second attempt on any peak.

**Keep at the peak-wide level:** routes, season windows, access patterns, recurring crux, source links, open questions. Things that are true across years.

**Push to trip files:** dated conditions, "we found X loaded with Y", individual decisions, partner-specific notes.

**Push to references/:** third-party TRs detailed enough that a one-line citation in the peak-wide file would lose information.

When a trip file teaches something durable, **promote** it: add a one-line entry to the peak-wide file with `(verified YYYY-MM-DD)` and link back to the trip file.

## Filename slug

- Lowercase, hyphenated
- Drop "Mount" / "Mt" prefix: `Mount Buckner` → `buckner.md`
- Spell out abbreviated names: `7FJ` → `seven-fingered-jack.md`, `N Gardner` → `north-gardner.md`
- For peaks with disambiguators in `bulger-peaks.json` (e.g., `Mount Martin (Methow)` vs `Mount Martin (CNC)`): use parenthetical as suffix, e.g., `martin-methow.md`, `martin-cnc.md`

Trip files: `YYYY-MM-DD-{summit|attempt|recon}.md`. Reference files: `YYYY-MM-DD-{author-or-source-slug}.md`.

## Peak-wide template

Copy this structure when seeding a new peak file. Drop sections that don't apply — don't pad.

```markdown
# {Peak Name} ({elevation} ft, Bulger #{rank})

## Personal status
- **Climbed:** yes/no/attempted
- **Attempts:** {count, link to most recent trip file}
- **Style preference:** {ski mtn / scramble / alpine climb}

## Summary
{2–3 sentences: what is this peak, why is it hard, when do people climb it.}

## Best-season window
{Season + reasoning, by route. Override the JSON `best_seasons` if this conflicts.}

## Approach options
*(Include this section only when the peak has multiple non-equivalent access modes — e.g., different trailheads, ferry vs road, or fundamentally different multi-day vs day-trip framings. Skip for peaks with one obvious approach.)*

{One short paragraph or bullet list naming each approach mode and the trade-off that drives the choice — e.g., "Holden ferry+bus = standard but ferry-locked schedule; Stehekin = enables Dark traverse; Phelps Creek = no public access to Bonanza directly".}

## Standard route
{One paragraph: line, key crux, season window. Not blow-by-blow.}

## Alternate routes
{Other viable routes with trade-offs — distance, technical grade, season window.}

## Access & logistics
*(Bullets are the default. For "access-is-the-crux" peaks — ferry-dependent, multi-day required, complex shuttle — prose paragraphs are fine here. Pick whichever conveys the logistics more honestly.)*

- **Trailhead:** {name, road, current gate status if known}
- **Drive from North Bend:** {hours}
- **Permits:** {NPS zone, NF wilderness, etc.}
- **Approach distance/gain:** {numbers}

## Crux / hazards
{The thing that will turn you around — as a *seasonal pattern*, not specific conditions. Cite trip files for verification.}

## Trip history
- [YYYY-MM-DD — {one-line summary}]({slug}/YYYY-MM-DD-{kind}.md)

## Sources & reference TRs
- [Title or description](URL) — {one line: year, author, route, why useful}
- [Local cache: {author}, {date}]({slug}/references/YYYY-MM-DD-{slug}.md) — {why preserved in full}
- **Sources attempted but blocked/unavailable:** {list URLs that failed and why — 403, ad-redirect, Cloudflare JS, etc. Prevents re-trying the same dead ends. Note workaround if known, e.g., "try web.archive.org snapshot".}
- **Sources confirmed to NOT cover this peak:** {list sources you actually checked that have no entry — prevents re-checking. E.g., "Hike2Hike (no entry — too technical for that site's scope)".}

## Open questions / beta to gather
{Things you don't know yet but want to before next attempt.}
```

### Source-confidence marking

When filling in route/beta content from general mountaineering knowledge rather than a citable first-hand source (because Tier-2 sources were blocked, or no recent TR exists), mark it inline so future updates know what to upgrade:

- *Italic with parenthetical note:* `*Standard route is the Mary Green Glacier from Holden (general knowledge — not source-verified).*`
- Or a trailing tag: `Mid-5th class on the summit pyramid `[unverified]`.

Don't mark every sentence — only the ones where a future better source would meaningfully change the content.

## Trip file template

```markdown
# {Peak} — {route or objective}, YYYY-MM-DD

← Peak file: [{slug}.md](../{slug}.md)

## Plan
- **Objective:** {summit / route / variation}
- **Style:** {c2c / overnight / etc.}
- **Approach:** {one-line route description}

## Outcome
{summit | turnaround at X | cancelled — and why in one line}

## Conditions encountered
{snow, weather, hazards, observations specific to this day}

## Decisions & reasoning
{key calls made, what drove them}

## Lessons
{what would you do differently; what should propagate to the peak file}

## Open follow-ups
{anything to verify before the next attempt}
```

## Editing rules

- **Date your observations.** Conditions notes without a date age into noise.
- **Trip files are append-only.** Don't edit history. If a later trip contradicts an earlier one, write the contradiction in the new trip file and update the peak-wide file.
- **Distinguish personal beta from public TR beta.** Personal goes in `{slug}/YYYY-MM-DD-*.md`; cached public TRs go in `{slug}/references/`.
- **Don't duplicate `bulger-peaks.json`.** Coordinates, elevation, NWAC zone, nearest SNOTEL live there. Reference them, don't restate them — except when explicitly *overriding* a field.
- **Trim ruthlessly.** A 2-page peak file is better than a 10-page one. Detail belongs in trip files and references; the peak file is the index.
- **Record source dead-ends.** When a Tier-2 source (SummitPost, Peakbagger, NWhikers, CascadeClimbers, Steph Abegg, etc.) is blocked or has no entry, write it down in the Sources sub-sections — don't leave it implicit.

## Known source accessibility (as of 2026-05)

Reference for what's likely to work when scraping a new peak. Update this table when access patterns change.

| Source | Access | Notes |
|---|---|---|
| Country Highpoints (Eric Gilbertson) | ✅ direct fetch + internal `?s=` search | Reliable; great for hard/remote peaks |
| Climber Kyle | ✅ direct fetch | Reliable when post exists; spotty Bulger coverage |
| Hike2Hike | ✅ direct fetch | Structural gap on technical peaks |
| SummitPost | ❌ ad-redirect blocks fetch | Try `web.archive.org/web/{year}/{url}` |
| Steph Abegg | ⚠ URL pattern unreliable | Find her index page first; URL guessing fails |
| Peakbagger | ❌ 403 on direct fetch | Try archive.org or accept as gap |
| CascadeClimbers forums | ❌ 403 on search | Need direct thread URLs from elsewhere |
| NWhikers.net | ❌ Cloudflare JS challenge (search + topics) | Fully blocked; archive.org may have snapshots |
| TurnsAllYear | ⚠ untested at scale | Try when scraping ski-mtn peaks |
| Google / DuckDuckGo | ❌ JS challenge | Use site-internal search instead |
| NPS NOCA climbing reports | ✅ direct fetch | Best for North Cascades NP peaks |
