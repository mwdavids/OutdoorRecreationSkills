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
