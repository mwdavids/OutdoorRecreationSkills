# Upper-air sanity check — UIL and OTX RAOBs

When `fetch_freezing_level.py` returns observations from UIL (Quillayute,
coastal west) and OTX (Spokane, east of the crest), treat them as a
**forecast-confidence check, not a peak observation.** Both stations are
100+ mi from most Cascade objectives — they describe the *airmass*, not
the peak.

## How to use them

### (a) Stations agree → high-confidence synoptic FZL

If UIL and OTX agree on freezing level (within ~500 ft), that's a
high-confidence read on the synoptic FZL.

- If the **model forecast** for that hour disagrees by **> 1000 ft**, flag
  the model as running warm/cold.
- Weight the next ~12 hr of forecast snow level accordingly.

### (b) Stations disagree → airmass boundary near the crest

When UIL and OTX disagree (often a 2,000+ ft spread in spring), there's an
airmass boundary near the crest.

- Trust the station on the **appropriate side of the divide** for that trip.
- **Say so explicitly** in the brief. E.g.:
  > UIL 4,200 ft, OTX 7,800 ft — sharp west-east split with the airmass
  > boundary near the crest. Stuart Range objectives sit in the warmer
  > eastside airmass; expect FZL closer to 7,500 ft on the east side of
  > Asgard Pass.

### (c) 700 mb and 500 mb winds → free-atmosphere flow proxy

The observed 700 mb wind (~10k ft) and 500 mb wind (~18k ft) are reliable
proxies for free-atmosphere flow over the range.

| Level   | Threshold for ridgeline scour                 |
| ------- | --------------------------------------------- |
| 700 mb  | **> 30 kt** → ridgeline scour and exposure   |
| 500 mb  | **> 50 kt** → ridgeline scour and exposure   |

Strong winds aloft mean ridgeline scour regardless of the surface forecast.

## Don't overindex

- If the RAOBs roughly match the forecast, just note **"obs agrees with
  forecast"** and move on.
- Don't pad the weather section with telemetry. Use the obs to set
  confidence, then write the brief.

## What the airmass boundary looks like in spring

Common pattern in PNW shoulder season (Apr-Jun):

- Marine push west of crest → UIL FZL low, often 3,500-5,000 ft.
- Continental dry airmass east of crest → OTX FZL high, 6,500-8,000 ft.
- Crest itself is the transition zone — surface temps can swing 15-20 °F
  east-to-west on the same day at the same elevation.

This pattern is the #1 reason a generic point forecast can be wrong by a
big margin on either side of the crest. Always check.
