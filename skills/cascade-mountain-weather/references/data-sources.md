# Cascade Weather Data Sources

URLs and selection notes for the live data behind a Cascade weekend briefing. Fetch in parallel.

## NWS Point Forecasts — fetch all 8 (zones diverge significantly)

Forecasts are tied to the grid-point elevation. Always note the elevation when interpreting summit temps; standard lapse rate ≈ **3.5 °F per 1,000 ft** of gain.

| Zone | Elev (ft) | Lat, Lon | URL |
|------|----------:|----------|-----|
| North Bend (home) | 1,000 | 47.4957, -121.7868 | `https://forecast.weather.gov/MapClick.php?lat=47.4957&lon=-121.7868` |
| Snoqualmie Pass | 3,100 | 47.4244, -121.4138 | `https://forecast.weather.gov/MapClick.php?lat=47.4244&lon=-121.4138` |
| Stevens Pass | 4,060 | 47.7465, -121.0891 | `https://forecast.weather.gov/MapClick.php?lat=47.7465&lon=-121.0891` |
| Rainier (Paradise) | 5,400 | 46.7860, -121.7353 | `https://forecast.weather.gov/MapClick.php?lat=46.786&lon=-121.7353` |
| Baker (Heather Meadows) | 4,200 | 48.8567, -121.6894 | `https://forecast.weather.gov/MapClick.php?lat=48.8567&lon=-121.6894` |
| Index (west) | 550 | 47.8207, -121.5550 | `https://forecast.weather.gov/MapClick.php?lat=47.8207&lon=-121.555` |
| Leavenworth (east) | 1,170 | 47.5962, -120.6615 | `https://forecast.weather.gov/MapClick.php?lat=47.5962&lon=-120.6615` |
| Vantage (east) | 1,500 | 46.9454, -120.4757 | `https://forecast.weather.gov/MapClick.php?lat=46.9454&lon=-120.4757` |

Pull from each: daily high/low, precip type + probability, wind, snow amounts, freezing level (when mentioned), detailed text.

## NWAC Mountain Weather Forecast

`https://nwac.us/mountain-weather-forecast/` — purpose-built for the Cascades. Gives synopsis, precip table (12 h blocks), snow level (6 h), 5,000 ft temp, **ridgeline wind (6 h, the single most actionable alpine number)**. Flag >35–40 mph ridgeline.

## NWAC Weather Stations (ground truth within 24–48 h)

`https://nwac.us/weatherdata/` — real telemetry beats any forecast for proximate decisions. Key stations: **Camp Muir (10,188')**, **Paradise (5,400')**, **Washington Pass (5,477')**, **Snoqualmie Pass**, **Stevens Pass**, **Mt Baker Ski Area**. Check current temp, recent 24 h temp range (refreeze check), wind, and any precip vs. forecast.

## On-Trail Snow Coverage (Not Forecast Snow Level)

Use in winter/spring, whenever lingering or fresh snow could affect a run, or when asked where snow will be encountered. **Local observations improve an estimate; they are not required to produce one.** Estimate the existing snowpack first, then apply weather changes through the outing. Forecast snowfall elevation and freezing level describe atmospheric conditions, not the lower boundary of old snow on a trail.

### Inputs and availability

| Source | Availability and use | Limits |
|---|---|---|
| **WTA trip reports**: `https://www.wta.org/go-outside/trip-reports` | Preferred local observation source, especially **Mount Si, Mailbox Peak, and Snoqualmie Pass**. Search the actual route and recent outing dates; expand to comparable nearby routes if needed. | Reports are optional and irregular. Record outing date, not just posting date; distinguish route variants and how far the author traveled. No report, inaccessible reports, or no mention of snow does not mean snow-free. |
| **NRCS/SNOTEL**: `https://www.nrcs.usda.gov/resources/data-and-reports/snow-and-water-interactive-map` | Routine station observations: actual snow depth, SWE, temperature, precipitation, and recent trends where those sensors exist. Select by drainage, elevation, and setting, not distance alone. | A station measures one site, often unlike the trail. A snowy station does not establish the lower snow boundary; a bare station does not clear nearby shaded trails. Missing data is not zero; check timestamps and sensor plausibility. Percent-of-normal SWE is not a snowline. |
| **NOAA National Snow Analyses**: `https://www.nohrsc.noaa.gov/nsa/`; **SNODAS**: `https://nsidc.org/data/g02158/versions/1` | Daily regional snow-depth/SWE analyses; archived SNODAS grids are approximately 1 km. Useful baseline when route reports or representative stations are absent. | Modeled/assimilated, not trail observations. Cells mix elevations and exposures; zero modeled snow does not exclude trail ice or small snowfields. Station/model agreement may reflect assimilation, not independent confirmation. Check actual analysis time and access availability. |
| **Observed weather + NWS/NWAC forecasts** | Reconstruct accumulation, thaw, and refreeze since the snowpack anchor; use at least the recent 1-2 weeks when available, extending earlier if the last meaningful snowfall or old pack predates that. Forecast through the outing. | Today's temperature or snow level cannot reconstruct the season's remaining snowpack. Mountain precipitation and temperature inversions add uncertainty. |
| **Terrain and land cover** | Elevation, slope aspect/angle, canopy, terrain shading, wind exposure, and gullies constrain differences in retention. Use route/topographic information; disclose unknown canopy or shading. | Aspect means the slope's orientation, not travel direction. Fixed north/south elevation offsets are not defensible. Forest interception can reduce accumulation while shade prolongs remaining snow. |
| **Satellite imagery / webcams (optional)** | Sentinel-2: `https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-data/sentinel-2`; inspect acquisition date and relevant pixels. Dated webcams with known elevation/setting can corroborate. | Optical imagery cannot reliably see snow under canopy; cloud and shadow are unknown, not bare. Nominal five-day Sentinel-2 revisit does not mean a usable image every five days. Plowed/groomed surfaces are not natural-snow proxies. Do not block on these sources. |

### Estimation procedure (works without local reports)

1. **Define the area and exposure.** For a weekend overview, keep North Bend foothills separate from Snoqualmie Pass, and west-side terrain separate from east-side terrain. For named routes, identify elevation span and shaded forest versus sunny openings. Avoid one Cascade-wide elevation.
2. **Build a snowpack baseline from available evidence.** Use representative station depth/SWE and regional modeled coverage, ideally spanning elevations near the transition. If stations are absent, use the regional model with weather history; if the model is absent, use representative stations with weather history. Neither requires a WTA report. Do not extrapolate one deep, high-elevation station into an exact lower boundary. Climatology is a weak prior only, never current observation.
3. **Seek WTA observations to refine or challenge that baseline.** Prefer the same route, then comparable nearby elevation/exposure/canopy. Extract bare-to-snow transitions, landmarks, patchiness, sustained coverage, and packed snow/ice; retain the observed elevation interval rather than inventing a precise threshold. Explicitly snow-free to a turnaround only constrains that traveled section. Prefer credible route-specific evidence over coarse model output for the observed section, but explain conflicts rather than silently averaging them.
4. **Account for weather between each evidence date and the outing.** Identify new snowfall and its elevation/amount, warm spells, rain, cloud/sun, wind, and overnight refreeze. Winter accumulation and spring melt require different reasoning: old spring snow reflects weeks of accumulated snow and melt energy. Depth loss can be settlement rather than melt; SWE trends help distinguish them. High freezing levels or rain do not prove the old pack has disappeared. Do not turn degree-days, lapse rates, or a warm forecast into a universal feet-per-day snowline retreat. Account for pass cold-air pooling/inversions when relevant.
5. **Adjust qualitatively for retention, without invented precision.** Sunny open slopes often clear earlier in spring; shaded forest and north-facing hollows can retain snow lower. Wind-loaded pockets, avalanche deposits, and compacted busy trails can persist below the prevailing coverage band. A loop's shaded crossing can control runnability even when its sunny high point is bare. Give separate exposure ranges only when supported; otherwise state the expected ordering and uncertainty.
6. **Always return the best-supported assessment.** Separate **first consequential patches**, **sustained coverage**, and **surface condition** (fresh, slushy, packed, postholing, hard ice), including morning/afternoon changes. Use broad elevation intervals in feet, region/exposure, evidence dates/URLs, forecast changes, and confidence. Label estimates **report-supported** or **weather/model-inferred**. Missing WTA reports widens uncertainty, not a refusal. If current snowpack evidence is also unavailable or contradictory enough that no numerical range is defensible, say so and provide the supported qualitative assessment and conservative planning implication; never fabricate numbers to fill the template.

**Confidence:** high requires recent, representative direct coverage evidence with little intervening change; moderate can come from representative snowpack evidence and coherent weather history without a route report; low applies to coarse/distant proxies, missing history, conflicting sources, or rapid change. No report alone does not force low confidence, but weather/model inference cannot establish a precise snow-free trail ceiling. Source age is event-relative: a new storm can invalidate yesterday's report, while an older report may still constrain conditions during stable weather. Do not claim calibrated probabilities or fixed uncertainty widths without validation.

**Safety:** a coverage estimate is not a safety clearance. Flag hard ice and consequential snow crossings below sustained coverage. If a run enters avalanche terrain or runout with snow present, treat it as a snow-travel objective for the avalanche checks, regardless of its activity label.

## NWS Seattle Area Forecast Discussion (the *why*)

`https://forecast.weather.gov/product.php?site=SEW&issuedby=SEW&product=AFD&format=CI&version=1&glossary=1`

Pull pattern summary, freezing-level trend phrases, and confidence language. Surface as a 1–2 sentence "Pattern" callout — frames everything else.

## NWAC Avalanche Forecast

`https://www.nwac.us/avalanche-forecast/` — danger ratings + bottom-line per zone.

NWAC zones (cite the user's zone explicitly): West Slopes North / Central / South · Stevens Pass · Snoqualmie Pass · East Slopes North / Central / South · Olympics · Mt Hood.

**Hard safety boundary:** NWAC **High** or **Extreme** = do NOT recommend BC skiing for that zone+elevation band. Considerable = user's call, but flag prominently.

## WSDOT Mountain Pass Reports

`https://wsdot.com/travel/real-time/mountainpasses` — access gating in shoulder season.

Key direct links:
- SR 20 (N Cascades Hwy): `https://wsdot.com/travel/real-time/mountainpasses/north-cascade-hwy` — closed winter, reopens late Apr–May; gating for any N Cascades trip
- Snoqualmie I-90: `.../snoqualmie`
- Stevens US 2: `.../stevens`
- White Pass US 12: `.../white`
- Chinook SR 410: `.../chinook` — closed winter; Rainier east + Crystal access

If status is **PARTIALLY OPEN** or restricted, see [../../trip-briefing/references/wsdot-closure-parsing.md](../../trip-briefing/references/wsdot-closure-parsing.md).

## NWS Observed Freezing Levels

`https://www.weather.gov/sew/` — scroll to "Observed Freezing Levels." Ground truth vs. forecast; Cascades snowpack stability often flips around 5,000–7,000 ft FZL. For RAOB sounding interpretation see [../../trip-briefing/references/upper-air-sanity-check.md](../../trip-briefing/references/upper-air-sanity-check.md).

## UW WRF (optional — secret weapon for alpine timing)

**Time-Height Cross Sections:** `https://a.atmos.washington.edu/mm5rt/rt/timeheights_d3.cgi` — cloud, freezing level, winds by altitude over time. Use when summit-window timing is ambiguous (volcano push, narrow corn window, clear-above-700mb question).

**Precip/Cloud loops:** `https://a.atmos.washington.edu/wrfrt/data/` — system arrival timing across the range.

Skip for routine briefings where NWS + NWAC already give a clear answer.

## Too Rainy to Climb (rock crag-specific)

`https://toorainy.com/` — hourly forecasts tailored to Seattle climbing destinations with **48-hour rain accumulation** and crag-specific humidity. Coverage: Little Si / Exit 38, Index / Gold Bar, Icicle Creek, Frenchman Coulee, Squamish, Nason Ridge, Mt Erie, Mt Vernon, Newhalem, Tieton, Mazama, Smith Rock. Fetch whenever rock climbing is in play.
