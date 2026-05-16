#!/usr/bin/env python3
"""
check_triggers.py — Layer 2 trigger-routing lint for OutdoorRecreationSkills.

Reads each skill's SKILL.md `description` field and a fixture set of
representative prompts. For each fixture, scores the prompt against each
skill description using inverse-document-frequency-weighted token overlap,
and checks the top-scoring skill matches the fixture's `expected_skill`.

This is a *static heuristic*, not an LLM-in-the-loop test. It cannot prove
Claude will route correctly. It can prove that the four skill descriptions
are distinctive enough at the keyword level — and when a prompt scores
higher for the wrong skill, it's a strong signal that the description
needs sharper trigger language.

Also runs a pairwise overlap audit between skill descriptions; high overlap
warns about descriptions that compete for the same prompts.

Default mode prints routing mismatches as WARN (still loud, never fatal),
so the script is safe to wire as a pre-commit hook even while descriptions
are still being tuned. Pass `--strict` (or set CHECK_TRIGGERS_STRICT=1)
to promote routing mismatches to fatal errors — use this in CI once the
descriptions are sharp.

Usage:
    python scripts/check_triggers.py            # lint mode (default)
    python scripts/check_triggers.py --strict   # CI / enforcement mode

Exit code 0 unless there are structural errors (missing descriptions,
malformed fixture file, unknown skill in a fixture). In --strict mode,
any fixture mismatch also exits 1.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
FIXTURES = REPO / "tests" / "trigger_fixtures.json"

# Conservative English stopword list — anything that shouldn't carry routing weight.
STOPWORDS = {
    "a", "about", "after", "all", "also", "an", "and", "any", "are", "as", "at",
    "be", "been", "before", "by", "but", "can", "could", "do", "does", "even",
    "for", "from", "give", "got", "had", "has", "have", "having", "how", "i",
    "if", "in", "into", "is", "it", "its", "just", "kind", "let", "like", "make",
    "many", "may", "me", "more", "most", "my", "no", "not", "now", "of", "on",
    "one", "only", "or", "other", "our", "out", "over", "right", "should", "so",
    "some", "such", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "those", "to", "too", "use", "user", "users",
    "using", "very", "was", "we", "well", "what", "when", "where", "whether",
    "which", "while", "who", "why", "will", "with", "would", "you", "your",
    # Glue verbs / framing words common to ALL skill descriptions, drop them
    # so they don't cancel out IDF signal.
    "skill", "use", "trigger", "ask", "asks", "mentions", "wants", "wants",
    "generates", "generate", "fetch", "fetching",
}

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# --- frontmatter (duplicated from check_skills.py to keep this script self-contained) ---

def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


# --- tokenization ----------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-/][a-z0-9]+)*")


def tokenize(text: str) -> list[str]:
    """Lowercase, alnum tokens, stopwords dropped, naive singularization."""
    text = text.lower()
    tokens: list[str] = []
    for tok in _TOKEN_RE.findall(text):
        # Tiny stem: trailing 's' on >4-char words (climb / climbs / climbed left alone).
        if len(tok) > 4 and tok.endswith("s") and not tok.endswith("ss"):
            tok = tok[:-1]
        if tok in STOPWORDS:
            continue
        if len(tok) <= 1:
            continue
        tokens.append(tok)
    return tokens


# --- scoring ---------------------------------------------------------------

def score_prompt(prompt_tokens: list[str], skill_tokens: set[str], idf: dict[str, float]) -> float:
    seen: set[str] = set()
    total = 0.0
    for tok in prompt_tokens:
        if tok in skill_tokens and tok not in seen:
            total += idf.get(tok, 0.0)
            seen.add(tok)
    return total


# --- main ------------------------------------------------------------------

def main() -> int:
    strict = "--strict" in sys.argv[1:] or os.environ.get("CHECK_TRIGGERS_STRICT") == "1"
    print("=== Outdoor Recreation Skills — trigger routing checks ===")
    print(f"    mode: {'strict (mismatches fatal)' if strict else 'lint (mismatches warn-only)'}\n")

    # Load each skill's description.
    descriptions: dict[str, str] = {}
    for sd in sorted(SKILLS.iterdir()):
        if not sd.is_dir():
            continue
        skill_md = sd / "SKILL.md"
        if not skill_md.exists():
            err(f"[{sd.name}] missing SKILL.md")
            continue
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if not fm or not fm.get("description"):
            err(f"[{sd.name}] frontmatter missing 'description'")
            continue
        descriptions[sd.name] = fm["description"]

    if not descriptions:
        err("No skill descriptions could be read; aborting.")
        return 1

    print(f"[1] Skills loaded: {sorted(descriptions)}\n")

    # Tokenize descriptions and compute IDF over the skill corpus.
    skill_tokens: dict[str, set[str]] = {
        name: set(tokenize(desc)) for name, desc in descriptions.items()
    }
    df: Counter[str] = Counter()
    for toks in skill_tokens.values():
        df.update(toks)
    n_docs = len(skill_tokens)
    idf: dict[str, float] = {
        tok: math.log((n_docs + 1) / (count + 1)) + 1.0  # smoothed
        for tok, count in df.items()
    }

    # Pairwise overlap audit on skill descriptions.
    print("[2] Pairwise description overlap (Jaccard, higher = more ambiguous)")
    names = sorted(skill_tokens)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            inter = skill_tokens[a] & skill_tokens[b]
            union = skill_tokens[a] | skill_tokens[b]
            jacc = len(inter) / len(union) if union else 0.0
            flag = "  WARN" if jacc > 0.40 else "      "
            print(f"  {flag}  {a:30s} <-> {b:30s}  J={jacc:.2f}  ({len(inter)} shared tokens)")
            if jacc > 0.40:
                warn(f"high description overlap: {a} <-> {b} (Jaccard={jacc:.2f})")
    print()

    # Load fixtures.
    if not FIXTURES.exists():
        err(f"fixtures file missing: {FIXTURES}")
        return 1
    try:
        data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"fixtures file invalid JSON: {e}")
        return 1
    fixtures = data.get("fixtures", [])

    # Score each fixture.
    print(f"[3] Fixture routing (n={len(fixtures)})")
    passes = 0
    mismatches: list[str] = []  # routing failures; warn-only unless --strict
    near_miss_margin = 0.20  # fraction of top score
    for fx in fixtures:
        fid = fx.get("id", "?")
        prompt = fx.get("prompt", "")
        expected = fx.get("expected_skill", "")
        if not prompt or not expected:
            err(f"fixture {fid}: missing prompt or expected_skill")
            continue
        if expected not in skill_tokens:
            err(f"fixture {fid}: expected_skill '{expected}' is not a known skill")
            continue

        ptoks = tokenize(prompt)
        scores = {
            name: score_prompt(ptoks, toks, idf)
            for name, toks in skill_tokens.items()
        }
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_name, top_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0
        # Resolve ties so we don't pretend to predict alphabetically.
        tied_with_top = [n for n, s in ranked if s == top_score]
        tied = len(tied_with_top) > 1
        no_signal = top_score == 0

        passed = (
            not no_signal
            and not tied
            and top_name == expected
        )
        score_summary = ", ".join(f"{n}={s:.2f}" for n, s in ranked)

        if passed:
            passes += 1
            margin = (top_score - second_score) / top_score if top_score else 0.0
            if margin < near_miss_margin:
                runner = ranked[1][0]
                warn(
                    f"fixture {fid}: routed to '{expected}' but only beat '{runner}' "
                    f"by {margin:.0%} (top={top_score:.2f}, 2nd={second_score:.2f})\n"
                    f"             prompt: {prompt!r}"
                )
        elif no_signal:
            mismatches.append(
                f"fixture {fid}: no keyword signal for any skill (all scores 0) — "
                f"description for '{expected}' shares no distinctive vocabulary with prompt\n"
                f"             prompt: {prompt!r}"
            )
        elif tied:
            mismatches.append(
                f"fixture {fid}: tied at top between {tied_with_top} (score={top_score:.2f}), "
                f"expected '{expected}' to win outright\n"
                f"             prompt: {prompt!r}\n"
                f"             scores: {score_summary}"
            )
        else:
            mismatches.append(
                f"fixture {fid}: expected '{expected}', got '{top_name}' "
                f"(top={top_score:.2f}, expected_score={scores[expected]:.2f})\n"
                f"             prompt: {prompt!r}\n"
                f"             scores: {score_summary}"
            )

    print(f"  Passed: {passes}/{len(fixtures)}\n")

    print("=== Summary ===")
    print(f"  Errors:           {len(errors)}")
    print(f"  Warnings:         {len(warnings)}")
    print(f"  Routing mismatches: {len(mismatches)} ({'fatal' if strict else 'warn-only'})")
    print()
    for e in errors:
        print(f"  ERROR     {e}")
    for w in warnings:
        print(f"  WARN      {w}")
    for m in mismatches:
        label = "ERROR    " if strict else "MISMATCH "
        print(f"  {label} {m}")
    if errors:
        return 1
    if strict and mismatches:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
