# Powder shelf life — Cascade-specific decay

For **backcountry-powder trips** (not corn). Cascade powder is short-lived.
This is one of the most common briefing failures: the user gets stoked
about an X-inch storm total without checking what happened to the snow
between storm end and the trip day.

## The rule

If temps rose above freezing at ski elevation **at any point** between
storm end and the trip day, **the powder is gone**.

What's left depends on what happened next:

| What happened after the storm                   | What it skis as                                      |
| ------------------------------------------------ | ---------------------------------------------------- |
| Stayed cold and dry until trip day              | **Powder** (still skis well — go).                   |
| One warm-up, no refreeze yet                    | **Cascade concrete** — heavy, sticky, unedgeable.    |
| Warm-up + 2-3 freeze-thaw days before trip      | **Setting up for corn** — switch to corn-cycle reasoning. |
| Warm-up + thin overnight refreeze               | **Breakable crust** (worst case — bail or change elevation). |

## How to check

Walk through the **full daily sequence** from storm end through trip day,
not just the trip-day forecast.

Use the data already in the bundle:

- `weather.extras_by_day[].max_temp_f` and `min_temp_f` — daily max/min
  at gridpoint elevation.
- `weather.lapse_rate_f_per_1000ft` (typically 3.5 °F / 1,000 ft) — to
  bridge gridpoint elevation up to ski elevation.
- `snowpack[].swe_change_24h` and `swe_change_72h` — confirms whether
  recent loading actually accumulated at SNOTEL elevation (proxy).
- `freezing_level` — synoptic FZL on the trip day and recent days.

Compute estimated daily high at ski elevation:

```
T_ski_max ≈ T_grid_max − lapse_rate × (ski_elev − grid_elev) / 1000
```

If `T_ski_max > 32 °F` on any day between storm end and trip day → the
powder at that elevation is gone.

## The "go higher" workaround

Higher elevations that stayed below freezing the whole time preserve
powder longest. When the lower mountain is concrete:

1. Find the lowest elevation where T_max stayed ≤ 32 °F across the entire
   post-storm window.
2. If the planned objective has skiable terrain above that elevation,
   "go higher" can salvage the day.
3. If not — the powder day is over. Either skip or pivot to a corn-cycle
   objective on a different aspect.

## Example walkthrough

Storm ends Mon afternoon, trip is Sat. Ski elevation 6,500 ft. Gridpoint
elevation 3,500 ft. Lapse rate 3.5 °F / 1,000 ft → 10.5 °F adjustment.

| Day  | Grid T_max | Ski T_max (est) | Status                                |
| ---- | ---------- | --------------- | ------------------------------------- |
| Tue  | 45 °F      | 34.5 °F         | Above freezing — powder degrading.    |
| Wed  | 48 °F      | 37.5 °F         | Above freezing — powder gone.         |
| Thu  | 38 °F      | 27.5 °F         | Refreeze starting.                    |
| Fri  | 42 °F      | 31.5 °F         | Marginal refreeze; crust forming.     |
| Sat  | 44 °F      | 33.5 °F         | Trip day. Corn-cycle question now.    |

Call: **Powder day was Tue at the latest.** Sat is a corn-cycle question,
not a powder question. Switch to [corn-cycle.md](corn-cycle.md) reasoning.

## What not to do

- **Don't** report storm totals as the trip-day surface condition.
- **Don't** assume "above freezing at the trailhead = above freezing at
  the summit" — apply the lapse rate.
- **Don't** call it powder just because the trip-day forecast is cold.
  Check what happened in between.
