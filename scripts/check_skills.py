#!/usr/bin/env python3
"""
check_skills.py — Layer 1 static integrity checks for OutdoorRecreationSkills.

Runs cheap deterministic checks across all skills and their shared data files.
Catches the class of bug that bit us with Martin Peak: data drift, schema
regressions, broken cross-references, duplicate entries.

Usage:
    python scripts/check_skills.py

Exit code 0 if no errors, 1 otherwise. Warnings never fail the run.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# --- helpers ---------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Tolerant single-line-per-key YAML reader. Enough for `name:` / `description:`."""
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, parts[2]


def strip_code_blocks(md: str) -> str:
    return re.sub(r"```.*?```", "", md, flags=re.DOTALL)


LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def check_links(skill_name: str, md_path: Path, body: str) -> None:
    body = strip_code_blocks(body)
    for _label, target in LINK_RE.findall(body):
        target = target.split()[0]  # drop optional title
        target_path = target.split("#", 1)[0].split("?", 1)[0]
        if not target_path:
            continue  # in-page anchor
        if target_path.startswith(("http://", "https://", "mailto:")):
            continue
        if target_path.startswith("/"):
            continue  # absolute path, out of scope
        resolved = (md_path.parent / target_path).resolve()
        if not resolved.exists():
            err(f"[{skill_name}] broken link in {md_path.name}: '{target}'")


def slugify(name: str) -> str:
    s = name.lower()
    for prefix in ("mount ", "mt. ", "mt "):
        if s.startswith(prefix):
            s = s[len(prefix):]
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# --- skill SKILL.md --------------------------------------------------------

def check_skill_md(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        err(f"[{skill_dir.name}] missing SKILL.md")
        return
    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        err(f"[{skill_dir.name}] SKILL.md has no YAML frontmatter")
    else:
        if not fm.get("name"):
            err(f"[{skill_dir.name}] frontmatter missing 'name'")
        if not fm.get("description"):
            err(f"[{skill_dir.name}] frontmatter missing 'description'")
    line_count = text.count("\n") + 1
    if line_count > 500:
        warn(f"[{skill_dir.name}] SKILL.md is {line_count} lines (skill-creator suggests <500)")
    check_links(skill_dir.name, skill_md, body)


# --- bulger-peaks.json -----------------------------------------------------

def check_bulger_peaks() -> list | None:
    p = SKILLS / "trip-briefing" / "references" / "bulger-peaks.json"
    if not p.exists():
        err(f"bulger-peaks.json missing at {p}")
        return None
    try:
        peaks = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"bulger-peaks.json invalid JSON: {e}")
        return None
    if not isinstance(peaks, list):
        err("bulger-peaks.json must be a JSON array")
        return None

    print(f"  Total entries: {len(peaks)}")

    name_counts: Counter[str] = Counter()
    for i, peak in enumerate(peaks):
        loc = f"entry {i}" + (
            f" ({peak.get('name')!r})" if isinstance(peak, dict) else ""
        )
        if not isinstance(peak, dict):
            err(f"{loc}: not an object")
            continue
        name = peak.get("name")
        if not name or not isinstance(name, str):
            err(f"{loc}: missing/invalid 'name'")
        else:
            name_counts[name] += 1
        lat, lon = peak.get("lat"), peak.get("lon")
        is_bulger = isinstance(peak.get("bulger_rank"), int)
        # Bulgers must be in WA; non-Bulger reference peaks (Shasta, Hood, etc.) just need plausible Earth coords.
        lat_lo, lat_hi = (45.0, 49.5) if is_bulger else (-90.0, 90.0)
        lon_lo, lon_hi = (-124.8, -116.5) if is_bulger else (-180.0, 180.0)
        if not isinstance(lat, (int, float)) or not (lat_lo <= lat <= lat_hi):
            err(f"{loc}: lat {lat!r} not in expected range {lat_lo}..{lat_hi}")
        if not isinstance(lon, (int, float)) or not (lon_lo <= lon <= lon_hi):
            err(f"{loc}: lon {lon!r} not in expected range {lon_lo}..{lon_hi}")
        if not isinstance(peak.get("climbed"), bool):
            err(f"{loc}: 'climbed' must be bool, got {type(peak.get('climbed')).__name__}")
        elev = peak.get("elevation_ft")
        if elev is not None and (not isinstance(elev, (int, float)) or not (0 < elev < 16000)):
            warn(f"{loc}: elevation_ft {elev!r} looks suspicious")

    for name, c in name_counts.items():
        if c > 1:
            err(f"duplicate name in bulger-peaks.json: {name!r} appears {c} times")

    # Bulger subset by `bulger_rank`
    ranked = [
        p for p in peaks
        if isinstance(p, dict) and isinstance(p.get("bulger_rank"), int)
    ]
    ranks = [p["bulger_rank"] for p in ranked]

    if len(ranked) != 100:
        err(f"expected exactly 100 entries with bulger_rank, found {len(ranked)}")

    rank_counts = Counter(ranks)
    for r, c in rank_counts.items():
        if c > 1:
            tied = [p for p in ranked if p["bulger_rank"] == r]
            elevs = [p.get("elevation_ft") for p in tied if isinstance(p.get("elevation_ft"), int)]
            names = [p["name"] for p in tied]
            # Close-elevation rank ties are expected (peakbagger groups peaks of identical
            # rounded elevation). Warn only when the elevation span is small.
            if elevs and max(elevs) - min(elevs) <= 50:
                warn(f"bulger_rank {r} shared by close-elev peaks (span {max(elevs)-min(elevs)} ft): {names}")
            else:
                err(f"bulger_rank {r} used by peaks with different elevations: {names}")

    expected = set(range(1, 101))
    actual = set(ranks)
    missing = expected - actual
    extra = actual - expected
    if missing:
        # Rank ties naturally create gaps (two peaks at rank N => no peak at rank N+1).
        # This is normal and not a data error.
        warn(f"bulger_rank values missing from 1..100 (expected when ranks tie): {sorted(missing)}")
    if extra:
        err(f"bulger_rank values outside 1..100: {sorted(extra)}")

    climbed_bulgers = sum(1 for p in ranked if p.get("climbed") is True)
    print(f"  Bulger-ranked peaks: {len(ranked)} (climbed: {climbed_bulgers}/100)")
    print("  -> cross-check against CLIMBED count in /memories/climbing.md")

    return peaks


# --- bulger-knowledge peak files cross-check -------------------------------

def check_peak_files(peaks: list | None) -> None:
    peaks_dir = SKILLS / "bulger-knowledge" / "data" / "peaks"
    if not peaks_dir.exists():
        warn(f"bulger-knowledge peaks dir missing: {peaks_dir}")
        return

    md_files = [
        f for f in peaks_dir.iterdir()
        if f.is_file() and f.suffix == ".md" and f.name != "README.md"
    ]
    print(f"  Peak knowledge files: {len(md_files)}")

    if not peaks:
        return

    json_slugs: dict[str, str] = {}  # slug -> name
    for p in peaks:
        if isinstance(p, dict) and isinstance(p.get("name"), str):
            json_slugs[slugify(p["name"])] = p["name"]

    for md in md_files:
        slug = md.stem
        if slug in json_slugs:
            continue
        # Lenient: any json slug that contains the file slug or vice versa
        if any(slug in js or js in slug for js in json_slugs):
            continue
        # Fall back: read H1 and try to match by name
        h1 = ""
        for line in md.read_text(encoding="utf-8").splitlines()[:30]:
            line = line.strip()
            if line.startswith("# "):
                h1 = line[2:].strip().lower()
                break
        if h1 and any(h1 in n.lower() or n.lower() in h1 for n in json_slugs.values()):
            continue
        warn(f"peak file '{md.name}' has no clear match in bulger-peaks.json (slug='{slug}', h1='{h1}')")


# --- gear-library.json -----------------------------------------------------

def check_gear_library() -> None:
    p = SKILLS / "packing-list" / "references" / "gear-library.json"
    if not p.exists():
        err(f"gear-library.json missing at {p}")
        return
    try:
        items = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"gear-library.json invalid JSON: {e}")
        return
    if not isinstance(items, list):
        err("gear-library.json must be a JSON array")
        return
    print(f"  Gear library entries: {len(items)}")
    required = ("name", "type", "date_added", "content")
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            err(f"gear-library entry {i}: not an object")
            continue
        missing = [f for f in required if f not in item]
        if missing:
            err(f"gear-library entry {i} ({item.get('name','?')!r}): missing {missing}")


# --- main ------------------------------------------------------------------

def main() -> int:
    print("=== Outdoor Recreation Skills — static checks ===\n")

    print("[1] Per-skill SKILL.md")
    for sd in sorted(SKILLS.iterdir()):
        if sd.is_dir():
            check_skill_md(sd)
    print()

    print("[2] bulger-peaks.json schema + integrity")
    peaks = check_bulger_peaks()
    print()

    print("[3] bulger-knowledge peak files vs JSON")
    check_peak_files(peaks)
    print()

    print("[4] gear-library.json")
    check_gear_library()
    print()

    print("=== Summary ===")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print()
    for e in errors:
        print(f"  ERROR   {e}")
    for w in warnings:
        print(f"  WARN    {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
