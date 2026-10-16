# Cascade Weekend Activity Playbook

Activity priority + interpretation lens for the cascade-mountain-weather skill. The user's actual desire order — not frequency.

For trip-specific gear thinking, see the trip-briefing skill's [trip-style-playbook](../../trip-briefing/references/trip-style-playbook.md). This file is the **weekend planner** variant: ranking activities against a forecast and recommending what to do.

## Priority order

1. **Peak bagging** (Bulger list)
2. **Ski mountaineering** (volcanoes)
3. **Backcountry skiing** (powder or corn)
4. **Trail running** — happens regardless; not a recommendation
5. **Rock climbing**
6. **Whitewater rafting** — least frequent

## 1. Peak bagging — highest priority

- **Want it most** — if a high-pressure window opens with light wind and good vis, recommend a Bulger over everything else. Multi-day windows = high value for remote peaks with long approaches.
- Key factors: freezing level, ridgeline wind, vis, precip prob, lightning.
- Seasons: summer (Jul–Sep) for non-glaciated; spring/early summer for glaciated when bridges are solid; fall for larch tours.

## 2. Ski mountaineering

- **Current dream objective: Fuhrer Finger on Rainier.** When conditions align (stable, low avy in Fuhrer Thumb couloir, weather window for the summit push, good corn) — call it out by name.
- Season: Apr–Jun (corn), into Jul on volcanoes.
- Corn cycle is the centerpiece — read [../../trip-briefing/references/corn-cycle.md](../../trip-briefing/references/corn-cycle.md).
- Departure timing driven by corn timing, not sunrise.

## 3. Backcountry skiing

- **Hard rule: NWAC High or Extreme = no.** Considerable = flag prominently, user's call.
- Powder shelf-life check before recommending "powder" days — see [../../trip-briefing/references/powder-shelf-life.md](../../trip-briefing/references/powder-shelf-life.md). If any above-freezing temps intervened at ski elevation between storm and trip date, it's no longer powder.
- Core zones (winter): Snoqualmie (Alpental sidecountry, Chair Peak, Snow Lake), Stevens (Cowboy Mtn, Big Chief), Crystal sidecountry, Baker (Heather Meadows, Table Mtn, Herman Saddle, Artist Point).

## 4. Trail running — the baseline

- Done **4–6 days/week regardless of weather**. Do NOT phrase as a recommendation.
- Home base North Bend → Middle Fork Snoqualmie trail system, Mailbox, Si, Teneriffe.
- Note relevant conditions instead: "Expect steady rain and 38 °F in North Bend — dress for wet/cool on Middle Fork."
- When snow may affect running, follow [data-sources.md](data-sources.md#on-trail-snow-coverage-not-forecast-snow-level): estimate on-trail coverage from available snowpack evidence, weather history/forecast, and terrain **even without local reports**. Prefer **WTA.org** for optional route observations, especially Mount Si, Mailbox, and Snoqualmie Pass. Distinguish first consequential patches, sustained coverage, and packed snow/ice; provide supported exposure-specific elevation ranges, evidence dates, and confidence. Do not substitute forecast snow level for existing coverage or treat missing reports as snow-free.
- Genuinely hazardous: flag ice storms, extreme heat, AQI >150.

## 5. Rock climbing

Microclimates matter — west/east diverge sharply.

| Area | Side | Rock | Best | Notes |
|---|---|---|---|---|
| Exit 38 (Mt Washington) | West | Various | Summer heat waves | Shady, north-facing. Wet in shoulder seasons. Close to North Bend. |
| Exit 32 (Little Si) | West | Various | Summer | Slightly more exposed than 38. Close. |
| Leavenworth (Icicle, Castle Rock) | East | Granite | Spring–fall | Drier, sunnier than west side. |
| Peshastin Pinnacles | East | Sandstone | Spring/fall | Too hot midsummer. |
| Vantage (Frenchman Coulee) | East | Basalt | Spring/fall, 45–65 °F | Too hot summer. Wind common. |
| Index (Town Wall, Lower Town Wall) | West | Granite | Summer dry spells | Steep, seeps; needs **3+ dry days**. |
| Squamish (BC) | BC | Granite | Jul–Sep | Best within weekend range. Needs sustained dry window. |

**Decision rule:** West socked in, east sunny + 50–60 °F = Vantage / Leavenworth day. Hot dry west = Exit 38/32. Index needs 3+ dry days (check recent precip, not just forecast). Squamish = sustained summer high pressure.

Always sanity-check with toorainy.com for rock dryness — see [data-sources.md](data-sources.md).

## 6. Whitewater rafting

- **Middle Fork Snoqualmie** — at home in North Bend. Always glance at it. USGS gauge `12141300`.
- **Wenatchee** — favorite spring run, flow-dependent. Sweet spot driven by snowmelt. USGS `12462500` (Peshastin) or `12459000` (Plain). Best when warm spell drives rapid melt (Apr–Jun).
- **Skykomish** — user has interest but less experience. USGS `12134500` (Gold Bar). Rain-fed and snowmelt.

When a warm spell is driving rapid melt in spring → call out the Wenatchee.

Real-time flow: `https://waterdata.usgs.gov/nwis/uv?site_no={GAUGE}`.

Don't recommend rafting as a fallback for bad weather.

## The baseline fallback

When weather shuts everything down: trail running from North Bend (happening anyway) + kilterboard at home. Acknowledge this honestly instead of forcing a marginal outdoor pick.
