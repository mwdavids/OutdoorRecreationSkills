# Outdoor Recreation Skills

Custom GitHub Copilot / Claude skills for Pacific Northwest outdoor recreation planning — mountain weather analysis, trip briefings, and peak bagging tracking.

## Skills

### [cascade-mountain-weather](skills/cascade-mountain-weather/SKILL.md)
Analyzes mountain weather forecasts for the Washington Cascade Mountains and recommends outdoor activities based on conditions. Fetches live data from NWS, NWAC, WSDOT, UW WRF, and USGS to *produce opinionated weekend briefings ranked by activity* (peak bagging, ski mountaineering, backcountry skiing, trail running, rock climbing, whitewater rafting).

**Triggers:** mountain weather, weekend plans, what to do outdoors, trip planning for the Cascades, NWAC, avalanche forecast, "what should I do this weekend"

### [trip-briefing](skills/trip-briefing/SKILL.md)
Generates peak-specific mountain trip briefings by gathering trip details and fetching live weather, snowpack (SNOTEL), avalanche, drive time, and trip report data. Produces a concise, actionable one-page briefing for an experienced mountaineer.

**Triggers:** plan a trip to a specific mountain, check conditions for a peak, go/no-go assessment, summit attempt planning, SNOTEL, specific Bulger peak

## Reference Data

> **Note:** These files are personalized to the repo owner's climbing history and objectives. If you're using these skills for yourself, update them with your own peak list, completion status, and home location (North Bend, WA is the default).

- **[bulger-peaks.json](skills/trip-briefing/references/bulger-peaks.json)** — Single source of truth for all 100 Bulger peaks: coordinates, elevation, NWAC zone, nearest SNOTEL, climbed status (49/100), ski mountaineering notes, prominence, and larch scenery

## Installation

To use these skills with GitHub Copilot in VS Code, copy the skill folders into your `~/.agents/skills/` directory:

```bash
cp -r skills/cascade-mountain-weather ~/.agents/skills/
cp -r skills/trip-briefing ~/.agents/skills/
```

## Home Base

North Bend, WA — all drive times and weather defaults are calibrated from here.

## Example Prompts

### Trip Briefings
- *"Create a trip briefing for a ski tour of Mt Daniels for this upcoming Sunday. Highlight the two different routes we might take depending on the snow line elevation."*
- *"What are conditions like on Bonanza Peak right now? I'm thinking about a July attempt via Holden."*
- *"Generate a go/no-go for Forbidden Peak this Saturday. We're planning the West Ridge."*
- *"I want to ski Mount Adams this weekend. Give me the full briefing — corn cycle, weather window, and departure time from North Bend."*

### Weekend Weather & Activity Planning
- *"What should I do this weekend? I'm open to anything — peak bagging, skiing, trail running."*
- *"Is there a weather window for a big Bulger peak this weekend? I'd prefer something I haven't climbed yet."*
- *"Compare conditions for Gardner vs Remmel this weekend — which is the better day trip?"*
- *"What's the avalanche forecast look like for the Stevens Pass zone? I'm thinking about backcountry skiing."*

### Peak Tracking & Data
- *"Which unclimbed Bulgers are accessible right now given current road closures?"*
- *"What are my closest unclimbed Bulgers that would make good day trips?"*
- *"Show me all the unclimbed peaks I could combine into a multi-day trip in the Entiat area."*
