# HTML output — for sharing via email

After delivering the markdown briefing in chat, **always also save an
HTML version** to `tmp/` for sharing via email. The HTML retains tables,
colors, links, and callout boxes when copy-pasted into Gmail or other
email clients.

## Filename convention

```
tmp/{peak-slug}-briefing-{trip-date}.html
```

Example: `tmp/adams-briefing-2026-05-10.html`.

Use a lowercase, hyphenated slug (drop `Mount` / `Mt`): `Mount Adams` →
`adams`.

## HTML skeleton

Use this styling template. Map each markdown section to the
corresponding HTML element — tables stay as `<table>`, bullet lists as
`<ul>`, etc.

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: Arial, sans-serif; font-size: 14px; color: #222; max-width: 720px; margin: 20px auto; line-height: 1.5; }
  h2 { color: #1a5276; border-bottom: 2px solid #1a5276; padding-bottom: 4px; }
  h3 { color: #2e86c1; margin-top: 24px; }
  table { border-collapse: collapse; margin: 10px 0; width: 100%; }
  th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; font-size: 13px; }
  th { background: #eaf2f8; font-weight: bold; }
  .summary { background: #eafaf1; border-left: 4px solid #27ae60; padding: 12px 16px; margin: 12px 0; }
  .warning { background: #fef9e7; border-left: 4px solid #f39c12; padding: 10px 14px; margin: 10px 0; }
  .go { color: #27ae60; font-weight: bold; }
  .caution { color: #e67e22; font-weight: bold; }
  .nogo { color: #e74c3c; font-weight: bold; }
  a { color: #2e86c1; }
  hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
  ul, ol { margin: 6px 0; padding-left: 22px; }
  li { margin-bottom: 4px; }
  .meta { color: #666; font-size: 13px; }
</style>
</head>
<body>
<!-- Map the briefing sections here -->
</body>
</html>
```

## Section mapping

| Markdown                                | HTML                                                          |
| --------------------------------------- | ------------------------------------------------------------- |
| Bottom line GO / CONDITIONAL / NO-GO    | `<div class="summary">` with `<span class="go|caution|nogo">` |
| Calendar offset chip                    | `<p class="meta">` directly under the verdict                 |
| Summary / Weather Window prose          | `<p>`                                                         |
| Weather tables, SNOTEL panel            | `<table>` with `<th>` headers, `.meta` for footnotes          |
| Corn cycle / avalanche positive callout | `<div class="summary">`                                       |
| Hazard / cornice / crux warning         | `<div class="warning">`                                       |
| Route steps                             | `<ol>`                                                        |
| Resource links                          | `<a href="...">` in a `<p>` or `<ul>` of labelled links       |

## Hand-off line to the user

After saving, tell the user:

> Saved to `tmp/{filename}.html` — open in browser, Ctrl+A → Ctrl+C,
> paste into Gmail.
