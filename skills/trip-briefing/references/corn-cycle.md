# Corn cycle — when it's the call

The corn cycle is the highest-value judgment in a spring-ski-mountaineering
brief. It is **not** relevant for: midwinter powder, dry summer firn,
descents that aren't on solar-aspect spring snow, or non-ski trips. Skip
when not applicable.

When it is in play, work the framework below using NWAC freezing level,
NOAA hourly highs/lows + cloud cover, recent-history precip and snowfall,
and the SNOTEL refreeze flag from `compute_wet_bulb.py`.

## The five-step framework

### 1. Overnight refreeze (the gate)

Did the freezing level drop below the planned ski elevation overnight, with
clear or mostly-clear skies?

- Target overnight low at ski elevation **≤ 28-30 °F wet-bulb** (use
  [refreeze-physics.md](refreeze-physics.md) — not air temp).
- **Cloud cover is the #1 refreeze predictor.** Cloudy night ruins a marginal
  refreeze even when air temps look fine. Clear night can save one that
  looks borderline on temps alone.
- Cite the overnight low and FL in the briefing.

### 2. Daytime softening by aspect

After sunrise the top 1-2 inches soften slope by slope:

| Aspect | Window           |
| ------ | ---------------- |
| **E**  | Early morning    |
| **S**  | Mid-morning      |
| **W**  | Afternoon        |
| **N**  | May never corn   |

Name the aspect of the planned descent and call when it should soften.

### 3. Window length and close

Good corn lasts **~2-4 hours per aspect** before going oversoftened, wet,
and isothermal (wet-loose / wet-slab risk). The window has closed when:

- Pinwheels start running.
- Ski-pen exceeds ~10 cm.
- NWAC flags a wet-loose problem.

Give an explicit **"be off the steep stuff by HH:MM local"** call.

### 4. Quality modifiers

- Cycle improves after several consecutive freeze-thaw days; first day after
  a storm is often chalky or crusty.
- Strong wind creates wind crust instead of corn.
- Daytime highs at ski elevation in the **35-45 °F** range are the sweet spot.

### 5. The diagnosis

Conclude with exactly one of:

| Verdict                | Meaning                                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| **corn cycle working** | Clean refreeze + timed softening + reasonable wind.                                             |
| **partial / aspect**   | Works on solar aspects, not shaded.                                                             |
| **broken**             | No refreeze → breakable crust or wet snow all day. Consider bailing.                            |
| **bulletproof**        | Refreeze too hard + solar too weak → firm/icy descent. Ski crampons mandatory.                  |

If corn matters but the data is genuinely insufficient to call it, **say so
plainly** — do not fabricate a diagnosis.

## Spring tactics (when corn drives the call)

- A forecast season-high after a cold stretch stresses the snowpack — expect
  a wet-loose / wet-slab cycle. **Start early**, limit time under avy paths
  and cornices during peak heating.
- Cascade consolidation runs **S/E first** (Stuart, eastside, Teanaway) and
  **NW / high volcanoes last**. Use this to judge whether the route is in
  season for the date.
- Plan shorter aspect-specific runs (1,500-2,500 ft) and **follow the sun**
  (E early → S mid → W late) rather than chasing a single 4,000 ft
  top-to-bottom that will be over-cooked at the bottom.
- **Creek-hole hazard**: snow-covered drainages weaken through the day.
  Collapsing into a spring creek is a real killer. Flag any ski-out that
  crosses a melting-out drainage in the afternoon.
