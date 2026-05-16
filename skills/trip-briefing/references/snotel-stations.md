# SNOTEL stations — verified Cascade list and how to use them

The companion JSON (`scripts/data/snotel_stations.json`) holds 24 verified
Cascade SNOTEL stations plus a **blocklist of 7 hallucinated triplets** that
have shown up in prior sessions. Use the scripts — never invent a triplet.

## The blocklist

These triplets do not exist or do not serve data. **Never construct them, even
if they look plausible:**

```
540:WA:SNTL    698:WA:SNTL    680:WA:SNTL    737:WA:SNTL
717:WA:SNTL    794:WA:SNTL   1008:WA:SNTL
```

`fetch_snowpack.py` blocks them automatically and returns an error.

## How to pick stations for a peak

Use `scripts/pick_snotel_station.py`:

```powershell
# Primary station only (lowest cognitive load)
python pick_snotel_station.py --lat 48.448 --lon -121.026 --peak-elev 9080

# 2-3 station panel bracketing approach elevation
python pick_snotel_station.py --lat 48.448 --lon -121.026 --peak-elev 9080 --panel
```

The scoring function is `|station_elev_ft - approach_elev_target| + 100 * distance_mi`
where `approach_elev_target ≈ peak_elev × 0.6`. Panels add the
next-lower and next-higher candidate within 50 mi of the peak.

**A panel is better than a primary** for any peak where the climb passes
through multiple snow regimes (most Bulgers). One reading at one elevation is
not enough to call snow line, refreeze, or melt-out date.

## When to override the suggestion

The script is generic. Override for:

- **Peaks with named approach** that has its own SNOTEL (e.g. Park Creek Ridge
  for Buckner alt approach via Stehekin — already tagged in JSON).
- **Rain-shadow peaks** in the eastern Pasayten — Harts Pass or Salmon Meadows
  are usually right even when the primary picker lands on a wetter site.
- **Glacier Peak / Bonanza** — Lyman Lake (5,990 ft) is the only high-elevation
  station in the right basin and should be primary for either peak.

## Adding a new station

1. Look it up at <https://nwcc-apps.sc.egov.usda.gov/imap/>.
2. **Verify it returns current data** by hitting the CSV endpoint:
   ```
   https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/customSingleStationReport/daily/<triplet>%7Cid=%22%22%7Cname/-0,0/WTEQ::value
   ```
   If it returns "Stations do not exist" or an empty CSV, do NOT add it.
3. Add to `scripts/data/snotel_stations.json` with `{name, elev_ft, lat, lon, region}`.
4. Add a one-line entry under "Coverage" below.

## Current coverage

**I-90 corridor & Stuart Range:** Stampede Pass (3850), Rex River (3810),
Fish Lake (3440), Sasse Ridge (4340).

**US 2 corridor:** Stevens Pass (3940), Blewett Pass (4240 — Stuart south side).

**Mt Rainier:** Paradise (5150), Cayuse Pass (5260).

**South Cascades / Adams:** Surprise Lakes (4280).

**Baker / Shuksan / Pickets:** Wells Creek (4040), MF Nooksack (4940),
Beaver Pass (3630), Brown Top (5850).

**SR 20 / N Cascades:** Thunder Basin (4310), Rainy Pass (4880),
Easy Pass (5280), Swamp Creek (3930).

**Stehekin / east-of-crest big peaks:** Park Creek Ridge (4610),
Lyman Lake (5990), Trinity (2890 — Phelps Cr drainage), Pope Ridge (3590 — Entiat).

**Methow / Pasayten:** Harts Pass (6490), Salmon Meadows (4460).

**Mt Hood reference only:** Mt Hood Test Site (5380).

## Calendar-offset chip

`fetch_snowpack.py` maps `swe_pct_median` to a calendar-offset chip — the
**single line** you should surface in the briefing instead of a bare percentage.

| % of median | Chip                                              |
| ----------- | ------------------------------------------------- |
| ≥ 115%      | ~10-14 days ahead of season (more snow than normal) |
| 95-115%     | Roughly on schedule                               |
| 75-95%      | ~10-14 days behind season (less snow than normal) |
| 55-75%      | ~3-4 weeks behind season                          |
| 30-55%      | Well below normal, melting fast (~5-6 weeks ahead of calendar) |
| < 30%       | Essentially summer conditions for this elevation  |

The chip is the answer to "is this peak in or out for the date?" — the bare
percentage is not.
