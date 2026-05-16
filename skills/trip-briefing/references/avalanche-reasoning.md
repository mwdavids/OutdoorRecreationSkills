# Avalanche reasoning — in-season and off-season

Apply to any trip **in or under avalanche terrain**: ski mountaineering,
snow climbs, glacier travel, spring scrambles with steep snow gullies,
approaches under cornice-loaded ridges or hanging seracs. Skip for
dry-trail summer/fall trips with no overhead snow hazard.

The right reasoning forks on **whether NWAC has a current forecast** for
the trip date (`fetch_nwac_zone.py` → `off_season` flag).

---

## A. NWAC current forecast IS provided

(`day1_danger_*` populated, `off_season=False`.)

### 1. Translate the danger rating tactically

| Rating         | Tactical meaning                                                                                |
| -------------- | ----------------------------------------------------------------------------------------------- |
| **Low**        | Caution on isolated terrain features.                                                           |
| **Moderate**   | Heightened awareness on specific aspects/elevations; human triggering possible.                 |
| **Considerable** | Dangerous; conservative terrain selection mandatory; natural avalanches possible, human triggering likely. |
| **High**       | Very dangerous; avoid avy terrain.                                                              |
| **Extreme**    | Stay out.                                                                                       |

Cite the **elevation band** that matters for this objective (alpine vs
treeline vs below treeline). Don't restate the full rose.

### 2. Lead with the avalanche problem, not the rating

The 9 problem types each demand different tactics:

| Problem                         | Forecastability | Tactics                                                                                       |
| ------------------------------- | --------------- | --------------------------------------------------------------------------------------------- |
| **Storm Slab / Wind Slab**      | High            | Respect listed loading aspects/elevations. Let the slab settle 24-48 hr after wind/snow stops. |
| **Wet Loose / Wet Slab**        | Diurnal         | Tied to overnight refreeze and peak heating. Link to corn-cycle diagnosis.                    |
| **Persistent / Deep Persistent** | Low (high consequence) | Stability tests unreliable. Only safe answer is conservative terrain.                  |
| **Cornice**                     | Variable        | Give full ridge-width berth on top; never travel directly under one on warm afternoons.       |
| **Glide**                       | Unpredictable   | Don't park under glide cracks.                                                                |

State which problem(s) drive the call for this route and what the avoidance
move is.

### 3. Map the problem to the route

Name the specific route feature exposed. Examples:

- "The 35° SE-aspect couloir at 7,200 ft sits squarely in the wind-slab
  problem rose."
- "The traverse below the summit cornice is the overhead-hazard crux."

Generic "check the forecast" advice is failure.

### 4. Bottom line

Give a clear avalanche call: **green-light**, **conditional with a specific
bail trigger**, or **no-go**. Tie back to the trip verdict at top.

---

## B. NWAC OFF-SEASON or coverage gap

(`off_season=True`, or NWAC's coverage block doesn't include the trip date
— typical late-April through mid-November.)

### 1. Off-season ≠ low-risk

NWAC simply stops *monitoring*; the snowpack still avalanches. **Never
write "avalanche risk is low" without proxy evidence.** Default posture:
"unmonitored — reasoning from first principles using the proxies below."

### 2. Reason from observable proxies

- **Recent loading.** SNOTEL SWE jumps >1" in 24-48 hr, or NOAA/NWAC
  mountain weather forecasts >6-12" of new snow, mean fresh storm-slab and
  wind-slab problems are forming on lee aspects above the rain/snow line.
  Treat as **Considerable-equivalent on loaded aspects in alpine terrain**
  until ~48 hr of settlement.
- **Wind.** Sustained ridgeline winds >25 kt (NWAC mountain weather or
  700 mb obs from the upper-air block) build wind slabs on lee/cross-loaded
  aspects regardless of the date. Cornices grow on the same aspects.
- **Rapid warming or rain-on-snow.** Snow-level rise of 2,000+ ft, or rain
  onto recent snow, drives a wet-loose / wet-slab cycle within hours. **The
  first warm day after a cold storm is the highest-danger day**, not the
  storm itself.
- **Spring diurnal pattern.** Once the snowpack is isothermal, mornings are
  stable on a good refreeze and risk ramps through the afternoon. Tie
  directly to the corn-cycle diagnosis: **a broken refreeze IS the wet-avy
  problem**.
- **Cornices and seracs are year-round.** Cornice fall and serac collapse
  don't follow NWAC's calendar. For routes under hanging glaciers (N faces
  of volcanoes, icefalls below upper Boston Glacier) or summit-ridge
  cornices (Buckner, Forbidden, most Skagit/Picket peaks), keep an
  overhead-hazard call in the brief **regardless of season**.

### 3. PNW maritime baseline

By late spring the Cascade snowpack is generally well-consolidated — deep
persistent slabs largely heal out in maritime climates by April-May.
Dominant residual concerns shift to:

- Wet snow (wet-loose, wet-slab, glide).
- Fresh wind/storm slabs from any out-of-season storm.
- Cornice fall.

**Mid-winter persistent-weak-layer thinking does not apply to a May trip
on a typical PNW snowpack.**

### 4. Off-season call (2-4 sentences)

State explicitly that NWAC is in off-season / general-advisory mode,
summarize what the proxies say about the current picture for this
objective, and give a tactical call. Example:

> Unmonitored, but the 18" of new alpine snow Wednesday with 35 kt W wind
> means fresh wind slab on E-NE aspects above 7,000 ft — avoid the NE
> couloir, the SW ridge stays in play after Friday's refreeze.

Recommend the user pull a snowpack obs from a recent trip report for the
area before committing.
