# Packing List Output Format

## Structure

Markdown headings + tables. Categories appropriate to the trip — not every trip needs every category.

```markdown
## [Category Name]

| Item | Priority | Notes |
|------|----------|-------|
| Item name | | Only if noteworthy |
| Another item | OPTIONAL | Brief context |
```

## Column rules

- **Item** — specific gear name. Precise: "40L pack" not "pack"; "lightweight puffy (e.g., Cerium hoody)" not "jacket."
- **Priority** — leave **blank** for essentials. Write `OPTIONAL` only for genuinely non-essential nice-to-haves. **Most items should be essential** — a list full of optionals is useless.
- **Notes** — keep very brief (a few words). Leave blank when self-explanatory. Only add a note when something is specific to this trip/season/group.

## Category system

### Universal (almost every trip)

- **Navigation & Communication** — map, compass, GPS, PLB/InReach, phone
- **Clothing Layers** — base, mid, insulation, shell, extremities
- **Food & Water** — food, hydration, purification, cooking (if applicable)
- **Safety & First Aid** — first aid kit, emergency shelter, headlamp, fire kit
- **Personal** — sunscreen, sunglasses, toiletries, misc

### Trip-type additions

| Trip type | Additional categories |
|---|---|
| Alpine climbing | Technical Climbing Gear, Glacier Travel, Helmet & Protection |
| Ski mountaineering | Ski Equipment, Avalanche Safety, Skins & Transition |
| Backcountry skiing | Ski Equipment, Avalanche Safety |
| Backpacking | Shelter & Sleep, Camp Kitchen, Pack & Organization |
| Day hiking | (usually just universals, lighter versions) |
| Snow camping | Shelter & Sleep (winter-rated), Camp Kitchen (4-season), Insulation |
| Rafting | Boat & Water Gear, Dry Storage, River Safety |
| Trail running | Run Kit, Hydration Vest, (minimal universals) |
| Car camping | Camp Kitchen, Camp Comfort, Shelter & Sleep |

## CSV export

When the user asks for a CSV / spreadsheet-friendly version:

```
Category,Item,Essential,Note
Navigation & Communication,Map (USGS topo or CalTopo print),Yes,
Navigation & Communication,Compass,Yes,
Navigation & Communication,InReach Mini,Yes,Share tracking link with emergency contact
```

`Essential` = `Yes` when Priority is blank; `No` when Priority is `OPTIONAL`.
