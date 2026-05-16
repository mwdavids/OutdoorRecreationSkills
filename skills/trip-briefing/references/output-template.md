# Output template — section scaffold

The standard one-page briefing scaffold. Use the H2 headings as shown when
you include a section. The listed order is the **suggested** flow — deviate
when the trip's primary story warrants it (e.g. lead with logistics when
access closure dominates the call).

**Use judgment about what to include.** Sections marked optional should be
omitted when they don't add signal for this trip. Prefer omission over
filler. The data layer supplies more context than every trip needs; your
job is to pick what's signal for *this* objective at *this* time of year
and ignore the rest.

---

## ## Bottom line

One line: **GO**, **CONDITIONAL**, or **NO-GO** + the headline reason.

> **GO** — The weather, road, and route conditions look favorable for the
> planned trip.

> **CONDITIONAL** — Weather looks good, but it might be the wrong time of
> year for this route.

> **NO-GO** — A major storm with heavy snow and high winds is expected on
> the trip day.

### Calendar offset chip (conditional)

When SNOTEL data is present **AND** snowpack conditions are material to
the trip's decision, emit a single structured tag on the next line in this
exact format (no surrounding prose):

```
**Calendar offset:** snowpack ~2 weeks ahead of season (less snow than normal for this date)
```

Other valid framings:

- `~1 week behind season (more snow than normal for this date)`
- `matches normal for this date`

**Framing rule:** "ahead of season = less snow than normal" (snowpack
looks like it would later in the year); "behind season = more snow than
normal" (snowpack looks like it would earlier in the year). **Always
include the parenthetical** so the reader cannot misread the direction.

The renderer extracts this line into a chip next to the verdict pill —
keep it to one line, no commentary. **Omit entirely** when SNOTEL is
unavailable, OR when the offset isn't relevant (midsummer dry-trail
scramble, fall hike on melted-out terrain).

## ## Summary

3-5 sentences. Opinionated go/no-go reasoning that synthesizes weather,
snow/avalanche, route, and seasonal hazards. Expand when there's a real
call to make; stay tight when conditions are obvious.

When the snowpack-vs-normal offset is material to this trip (and you
emitted the calendar offset chip above), use the summary to explain what
that offset *means* for this specific objective — which seasonal cruxes
are in or out of play, whether the relevant trip reports apply, what
early-/late-season hazards to expect.

For trips where snowpack isn't material, lead with whatever actually
drives the call (weather, route conditions, access).

## ## Seasonal Crux *(optional)*

Include ONLY when there is a real make-or-break section driven by time of
year. See [seasonal-crux-guide.md](seasonal-crux-guide.md).

## ## Weather Window

Interpret the structured weather table (do not restate it — it renders as
appendix below your output).

- Lead with a 1-2 sentence **pattern callout** from the NWS AFD synopsis
  (when present) — the synoptic "why" (ridge building, AR, persistent
  onshore flow) frames everything below.
- Reference summit-adjusted temperatures from the table directly (use
  `lapse_rate_f_per_1000ft` from the weather block to bridge gridpoint →
  summit elevation).
- Use NWAC mountain weather (when available) for ridgeline wind and the
  NWAC snow level for rain/snow line and corn refreeze.
- Apply [upper-air-sanity-check.md](upper-air-sanity-check.md) for the
  UIL/OTX RAOB observed FZL.
- Pick wind and temperature thresholds appropriate to the activity and
  season. A number that matters for May ski mountaineering is not the
  same as one that matters for August scrambling or whitewater.
- Flag genuine dealbreakers.

## ## Snow & Avalanche Conditions *(optional)*

Include ONLY when snow conditions affect this trip's decision.

- SNOTEL panel table renders as appendix — do NOT restate it. Interpret
  the pattern across stations (where snow starts, melt rate, refreeze
  quality).
- State the snowpack-age call from the panel's `snowpack_age_note` field
  when material. Note where the offset diverges across elevation bands.
- Tie snowpack age back to seasonal cruxes in play (bergschrund
  open/closed, cornice loading, road snow, alder vs snow on approach).
- Include NWAC avalanche danger and key problems when in avy terrain. See
  [avalanche-reasoning.md](avalanche-reasoning.md).
- For ski-mountaineering on solar-aspect spring snow, devote a paragraph
  to the corn cycle. See [corn-cycle.md](corn-cycle.md).
- For backcountry powder trips, apply [powder-shelf-life.md](powder-shelf-life.md).

## ## Route Notes & Trip Reports

Trip-style- and condition-specific considerations. Synthesize cached peak
knowledge and trip reports; cite reports with links and source (WTA, CC,
TurnsAllYear, NWHikers). **Never invent time estimates.**

Seasonal crux belongs in its own `## Seasonal Crux` section above when
present; keep this section focused on route-specific beta — line choices,
pitch-by-pitch notes from prior parties, navigation, descent options,
water, bivy locations.

## ## Logistics

Whatever logistics actually matter for *this* trip in plain language
using **local time** — not a fixed checklist. The structured data above
supplies: departure recommendation, daylight margin, drive time,
sunrise/sunset (local), pass/road status. Pick what's signal, phrase it
naturally, skip what's noise.

If daylight margin is tight or negative, that's a safety call — say so.

For pass/road interpretation see
[wsdot-closure-parsing.md](wsdot-closure-parsing.md).

## ## Gear Considerations *(optional)*

What to emphasize or add to this athlete's standard kit given the actual
conditions above. Skip the obvious; call out the non-obvious. Examples:

- Ski crampons and a second tool for steep firn.
- Pickets and a 30 m rope for a bergschrund.
- Dry bag and PFD upgrade for high-flow rafting.
- Bug head net for early-summer bushwhack approaches.

**If conditions don't justify anything special, OMIT this section** — do
not emit an H2 that just says "standard kit."

## ## Resource Links

Render resource links as a markdown bullet list with **descriptive label
text**, not raw URLs. Format: `- **Label:** [short descriptive text](url)`.

Examples:

- **Map view:** [PeakBagger](https://...peakbagger...)
- **Topo & route planning:** [CalTopo](https://...caltopo...)
- **Hi-res near-term forecast:** [HRRR via SpotWX](https://...spotwx...)
- **Extended outlook:** [ECMWF via SpotWX](https://...spotwx...)
- **Avalanche forecast:** [NWAC](https://...nwac...)
- **Recent satellite imagery:** [Copernicus](https://...copernicus...)

**Never use the URL itself as the link text.**

---

## Voice and grounding (applies to every section)

- Write for someone who wants **facts, not disclaimers**. Be opinionated,
  direct, and specific.
- **Use only the data provided** — do not invent numbers, trailheads,
  access roads, approach routes, or travel times.
- When citing times or conditions, attribute the source (trip report,
  guidebook, cached peak knowledge).
- Never expose UTC times, raw ISO timestamps, or internal field names.
  **Always use local time.**
- Don't pad sections with hedged speculation when no data supports it.
- Don't refuse to analyze a forecast that IS in the data just because the
  trip is several days out. See
  [forecast-coverage-bands.md](forecast-coverage-bands.md).
