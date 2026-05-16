# Refreeze physics — wet-bulb, freezing degree-hours, and what kills a corn day

## The wet-bulb shortcut

**Air temperature is the wrong threshold for refreeze.** On a humid Cascade
night, T_air can read 32-34 °F while T_wet < 30 °F as evaporative cooling
drops the snow surface below the ambient reading. Wet-bulb crossing freezing
is the right threshold; air temp is a proxy that **overstates** marginal
nights.

Use `scripts/compute_wet_bulb.py --temp-f <T> --rh <RH>` to convert.
Heuristics:

- T_air = 36 °F, RH = 40% → T_wb ≈ 27 °F. **Solid refreeze.**
- T_air = 36 °F, RH = 85% → T_wb ≈ 34 °F. **Failed refreeze.** (Same air temp!)
- T_air = 32 °F, RH = 60% → T_wb ≈ 28 °F. **Solid refreeze.**

### Formula

Stull (2011) regression:

$$ T_w = T \arctan(0.151977 \sqrt{RH + 8.313659}) + \arctan(T + RH) - \arctan(RH - 1.676331) + 0.00391838 \cdot RH^{1.5} \cdot \arctan(0.023101 \cdot RH) - 4.686035 $$

Accurate to within ~0.3 °C across -20 °C to +50 °C and 5-99% RH at sea-level
pressure. Adequate for the "did it refreeze tonight?" decision.

Citation: Stull, R. (2011). *Wet-Bulb Temperature from Relative Humidity and
Air Temperature*. J. Appl. Meteorol. Climatol., 50(11), 2267-2269.

## Cloud cover is the second variable

Cloud cover gates the long-wave radiative loss that drives clear-night cooling.
A clear, dry night refreezes; an overcast humid night does not, even at the
same air temperature.

### The three-verdict classifier

| Verdict   | Conditions                                                       |
| --------- | ---------------------------------------------------------------- |
| **solid** | min T_wb ≤ 28 °F AND ≥ 4 hours below freezing AND clouds ≤ 70%   |
| **weak**  | min T_wb ≤ 32 °F AND ≥ 2 hours below freezing                    |
| **failed**| Wet-bulb never crossed freezing                                  |

When you have NWS hourly + RH + cloud cover for the overnight window, compute
all three and report the verdict. When you don't, you're guessing.

## Snow-model caveats (always include in the briefing)

> These chips are heuristics, not measurements:
>
> - SNOTEL stations are valley/pass sites, not summit ridges. Depth and timing
>   extrapolated to higher elevations get noisier the farther you go from the
>   station.
> - Refreeze quality is computed from forecast hourly data at a representative
>   elevation; complex terrain (couloirs, north faces, deep cold pools) can
>   stay much colder or much warmer than the gridded forecast suggests.
> - **Cloud cover is the dominant control on radiative refreeze and is the
>   largest source of error** — a clear forecast that turns overcast can convert
>   a "solid" call into a "weak" one without the air temperature changing at all.
> - Wind, dirty snow (albedo), and sub-surface heat flux are not modeled.
>   Strong wind builds wind crust instead of corn; dust/ash on snow accelerates
>   melt; deep isothermal snowpacks resist overnight surface refreeze even on
>   cold nights.
> - This is a desk briefing — verify with on-the-ground observations and recent
>   trip reports before committing to a steep line.

## Snowpack depth projection to summit elevation

Maritime Cascade snowpack lapse rate: roughly **+10% snow depth per 1000 ft**
of elevation gain in mid-winter, tapering to ~+5% as melt season progresses
and high-elevation snow consolidates faster than low.

Project with **±50% uncertainty on the delta**, not on the projection. So a
station at 4,000 ft reading 60 in projected to 7,000 ft (delta = +18 in)
becomes a range of 69 in (low) to 87 in (high). Always state the range — the
uncertainty is the headline.

When the station is melted out (0 inches), the projection upward is **not**
meaningful — high-elevation pockets may still hold snow. Say so.

## Freezing degree-hours (when you want to go deeper)

Hours that wet-bulb spent below 32 °F, summed across the overnight window,
predicts crust thickness. Rough mapping for Cascade maritime snow:

- 2-4 FDH → thin breakable crust by morning, blown out by 1000.
- 4-8 FDH → supportive crust, corn window 1000-1300 on south aspects.
- 8-12 FDH → deep refreeze, bulletproof ice early, corn 1100-1500 on multiple aspects.
- 12+ FDH → bulletproof all day on shaded aspects; corn confined to direct-sun aspects.

Use this when the simple verdict (solid/weak/failed) feels too coarse for the
decision.
