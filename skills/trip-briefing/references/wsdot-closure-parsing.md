# WSDOT closure parsing — what `PARTIALLY OPEN` actually means

`fetch_pass_status.py` returns WSDOT highway status. A naive read of a
`PARTIALLY OPEN` flag will incorrectly conclude that a trailhead is
unreachable. Read it carefully.

## What the status flags mean

| Status         | Meaning                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------- |
| **OPEN**       | Highway is fully open.                                                                    |
| **PARTIALLY OPEN** | Part of the highway is closed and part is open. The WSDOT conditions text identifies the closed segment (e.g. "closed from MP 134 to MP 178"). |
| **CLOSED**     | Highway is fully closed across the named pass/segment.                                    |

## The trailhead-access decision

A trailhead is unreachable from a given direction only if **either**:

1. The trailhead itself sits on the closed segment, **OR**
2. The access road branches off the highway **on the closed segment**.

Approach roads that branch off the highway **BEFORE** the closed segment
are unaffected, even when they share the highway number on the WSDOT
report.

### Canonical example

SR 20 winter closure runs from Ross Dam (MP 134) east to Silver Star /
Mazama (MP 178). Status: **PARTIALLY OPEN**.

- **Cascade River Rd** branches off SR 20 at Marblemount (~MP 106) — well
  **west** of the closure. Eldorado / Boston Basin / Sahale TH are
  **unaffected**, even though SR 20 reads `PARTIALLY OPEN`.
- **Canyon Creek TH** (MP 141.5) sits on the closed segment. **Unreachable
  from either end** until SR 20 opens (typically late May).
- **Ross Dam TH** (MP 134) is at the **west end of the closure**, so it's
  reachable from the west year-round (the closure starts just east).

## How to write it in the brief

- State which segment is closed (with MPs if given).
- State whether the trailhead sits on the open or closed side.
- Only flag access as a **real problem** when the trailhead truly sits on
  the closed side. Otherwise mention the closure in one sentence and move on.

### Good

> SR 20 closed MP 134 → MP 178 (Ross Dam → Silver Star). Cascade River Rd
> branches off at MP 106, west of the closure — Eldorado TH is unaffected.

### Bad

> SR 20 is closed. Approach may be blocked.

(Vague, ignores the MP segment, and creates false-positive blockers on
unaffected trailheads.)

## Other gotchas

- **WSDOT lists the highway status, not the side road.** Cascade River Rd
  has its own seasonal gate (typically at MP 20 / Eldorado TH or MP 22 /
  Boston Basin TH from late fall through late spring). That's an NPS gate,
  not a WSDOT closure. Use [fetch_nps_alerts.md](../scripts/fetch_nps_alerts.py)
  for those.
- **Conditions text changes nightly.** A snapshot from this morning may be
  stale by afternoon if a storm rolls through. For trips inside 24 hr,
  recommend the user spot-check the WSDOT travel map before launching.
