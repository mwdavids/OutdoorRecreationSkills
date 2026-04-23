# Gear Library

This directory can hold personal gear library files that the packing-list skill references to personalize generated lists.

## How to Use

Create a `gear-library.json` file in this directory with your saved packing lists. The skill will reference these to:
- Reflect what you typically bring for each trip type
- Flag gaps in your usual kit for specific conditions
- Suggest upgrades when relevant

## Format

Each entry is a past packing list:

```json
[
  {
    "name": "Adams South Spur — April 2025",
    "type": "ski mountaineering",
    "content": "Skis (Voile Hyperdrifters)\nSkins (G3 Alpinist+)\nSki crampons\nBoot crampons\nAxe\n..."
  },
  {
    "name": "Enchantments Traverse — August 2024",
    "type": "backpacking",
    "content": "Pack (ULA Circuit 40L)\nTent (Big Agnes Copper Spur UL2)\n..."
  }
]
```

You can paste lists in any format — bullet lists, tab-separated, freeform text. The skill will parse whatever you give it.

## Importing from the Packing List Generator App

If you use the [packing-list-generator](https://github.com/mwdavids/packing-list-generator) web app, you can export your gear library:

1. From the app's SQLite database, export your lists table
2. Save as `gear-library.json` in this directory
3. The skill will automatically reference it when generating new lists
