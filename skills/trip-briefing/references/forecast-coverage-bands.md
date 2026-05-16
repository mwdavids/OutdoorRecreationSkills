# Forecast coverage bands — confidence by lead time

Forecast skill degrades **smoothly** with lead time. It does not fall off a
cliff at day 3, and even day 7-10 guidance carries real (if reduced) signal.
The right move is to **discount confidence with lead time, not discard the
forecast.** Always give the trip-date forecast some weight; calibrate the
language.

## The five bands

| Lead time   | Data sources                                | Confidence       | How to write it                                                                                                                |
| ----------- | ------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Days 1-3** | NOAA hourly + daily                         | High             | Quote temps, winds, freezing levels, precip timing as point estimates. Commit to a verdict.                                    |
| **Days 4-5** | NOAA daily (edge of skill window)          | Good (synoptic)  | Quote ranges, flag timing/QPF may shift, but a clearly favorable/hostile pattern is real signal. Commit with a hedge.          |
| **Days 6-7** | NOAA daily fading + ECMWF                   | Moderate         | Lean on ECMWF for the high-level story (wet vs dry, cold vs warm, ridge vs trough). Note agreement. Soft language. Recommend regen. |
| **Days 8-10** | ECMWF only                                  | Directional only | Use to set expectations and flag obvious go/no-go signals. Do not quote specific numbers. Acknowledge low confidence explicitly. |
| **Outside window** | None                                  | None             | At most 2 sentences. State the dates fall outside the forecast window and recommend regen within 3-4 days.                     |

## NWAC avalanche caveat

NWAC is **short-validity** — typically a 1-2 day outlook from publish date.
When NWAC does not cover the trip date:

- Keep the avalanche section to **at most 2 sentences**.
- State the snowpack-age call from SNOTEL (snowpack evolves slowly, this is
  still useful).
- Note that the avalanche picture needs a fresh NWAC check 24-48 hours
  before departure.
- **Skip detailed avalanche-problem discussion** — it would be invented.

See [avalanche-reasoning.md](avalanche-reasoning.md) for the off-season
fallback (`off_season=True` or coverage gap).

## Bottom-line verdict calibration

The verdict should reflect actual, calibrated uncertainty:

| Coverage             | Verdict style                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| Solid 1-3 day        | Confident **GO** or **NO-GO**.                                                                 |
| 4-7 day              | Verdict still appropriate, just hedged ("GO if the pattern holds" / "leaning NO-GO unless the front slows"). |
| Outside window OR seasonal-crux uncertainty | **CONDITIONAL** with "too far out to call" framing.                          |

## Failure modes to avoid

- **Padding** weather/avalanche sections with hedged speculation when no
  data supports it.
- **Refusing to analyze** a forecast that IS in the data just because the
  trip is several days out.

Both are wrong. Pick the right band → commit.
