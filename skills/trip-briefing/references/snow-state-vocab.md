# Snow-state vocabulary

Use these six labels exactly when writing about spring / melt-freeze snow
conditions in a briefing. Consistency across briefings lets the user (and
future-you) compare conditions across trips without re-learning vocabulary.

Sourced from beta-bot/app/briefing/refreeze.py (`SNOW_STATE_VOCAB`).

| Label                 | Summary                                                                                                                              | Trigger                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **powder**            | Cold, dry, low density. Skis well; no melt-freeze cycles yet.                                                                        | Fresh storm with no above-freezing exposure since deposition.                                                                    |
| **settling**          | Storm snow consolidating; getting denser but not yet a crust.                                                                        | 1-3 days post-storm with marginal warming; minor melt-freeze.                                                                    |
| **breakable_crust**   | Thin sun/rain crust over softer snow. Worst-case skiing — hooks edges, hides instability. High ACL / knee-injury risk.              | One warm afternoon followed by a hard freeze without enough heat to consolidate underneath; or rain crust from rain-on-snow.    |
| **supportive_crust**  | Thick consolidated crust that supports a skier. Often skis as bulletproof ice in the AM; may corn up midday if heat is strong enough. | Multiple consecutive freeze-thaw days; deep refreeze; old corn base.                                                             |
| **corn**              | Top 1-2 inches of supportive crust softens into edge-able creamy snow. The spring ski-mountaineering target. ~2-4 hr window per aspect. | Solid overnight refreeze + sufficient daytime sun/heat on the aspect.                                                            |
| **slush_wet**         | Snow softens past corn — boot-pen >10 cm, pinwheels, isothermal. Wet-loose / wet-slab cycle active. Get off steep terrain.          | Failed overnight refreeze, OR corn window stayed open too long, OR rapid warming after a cold stretch.                          |

## Diagnostic rules of thumb

- Daytime high in the 30s + clear overnight + low humidity → **supportive_crust → corn** sequence (the target).
- Daytime high in the 40s + cloudy overnight or high humidity → **slush_wet** by mid-morning. Failed refreeze.
- Daytime high in the 30s + warm overnight (T > 32 °F all night) → **breakable_crust** on the second day. The worst case.
- Sustained week of nightly freezes + sunny days → **deep corn** with a wider midday window per aspect.

## What to say when

- "The route is in **corn** between 0900-1200 on east aspects, transitioning to **slush_wet** by 1300."
- "Expect **supportive_crust** on the climb, **corn** for the ski descent if you launch by sunrise."
- "Failed refreeze last night — surface will be **slush_wet** at start. No-go."
- "Recent rain event followed by a hard freeze made **breakable_crust** the dominant top layer. Defer."
