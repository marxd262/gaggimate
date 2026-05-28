# Start Pressure Test Profiles — Design Spec

**Date:** 2026-05-28
**Goal:** Generate 6 randomized GaggiMate profile JSON files that enable a statistically rigorous test of how start pressure affects output weight during a fixed-duration flow-controlled extraction.

---

## Overview

A Python generator script (`scripts/generate_pressure_test_profiles.py`) produces 6 profile files in `data/p/`. Each profile contains all 48 test combinations (8 pressure levels × 6 flow variants) in a unique random order. Running one full profile takes approximately 8–12 minutes. Running all 6 profiles yields 288 total test shots with balanced coverage and randomized ordering.

---

## Parameter Matrix

### Pressure targets — Phase 1 (8 levels)

| Label | Target (bar) |
|---|---|
| `p0.3` | 0.3 |
| `p1` | 1.0 |
| `p1.5` | 1.5 |
| `p2` | 2.0 |
| `p4` | 4.0 |
| `p6` | 6.0 |
| `p8` | 8.0 |
| `p11` | 11.0 |

> `0.3 bar` represents the "< 0.5 bar" condition — adjust the value in the script if a different near-zero target is preferred.

### Flow variants — Phase 3 (6 variants)

| Label | Type | Setpoint |
|---|---|---|
| `f1.5` | constant | 1.5 g/s |
| `f2` | constant | 2.0 g/s |
| `f2.5` | constant | 2.5 g/s |
| `f4` | constant | 4.0 g/s |
| `f6` | constant | 6.0 g/s |
| `f6to2` | declining | 6.0 → 2.0 g/s linear over 5s |

**Total combinations:** 8 × 6 = **48 per profile**
**Total profiles:** **6** (seeds 0–5)

---

## Phase Structure Per Test Unit

Every test unit follows this phase sequence. A release phase separates each pair of consecutive tests.

### Standard flow tests (flow variants f1.5 – f6, 40 combinations)

```
[Phase 1: Pressure Build] → [Phase 2: Stabilize] → [Phase 3: Flow Extraction] → [Release]
```

| Phase | valve | pump | duration | stop conditions |
|---|---|---|---|---|
| **1 — Pressure Build** | 0 (closed) | `target: pressure`, value: X bar, ease-out ramp 25s, adaptive: false | max 30s | (1) `pressure ≥ X` — primary; (2) 30s duration cap — safety |
| **2 — Stabilize** | 0 (closed) | off (`pump: 0`) | 2s fixed | none |
| **3 — Flow Extraction** | 1 (open) | `target: flow`, value: Y g/s, no pressure limit | 5s fixed | none |
| **Release** | 1 (open) | off (`pump: 0`) | 2s fixed | none |

### Declining flow tests (variant f6to2, 8 combinations)

```
[Phase 1] → [Phase 2] → [Phase 3a: Anchor] → [Phase 3b: Decline] → [Release]
```

Phase 3 is split into two sub-phases so the firmware can interpolate the setpoint correctly from 6 down to 2:

| Phase | valve | pump | duration | notes |
|---|---|---|---|---|
| **1 — Pressure Build** | 0 (closed) | same as above | max 30s | same stop conditions |
| **2 — Stabilize** | 0 (closed) | off | 2s | — |
| **3a — Anchor at 6** | 1 (open) | `target: flow`, value: 6 g/s, instant | 0.5s | sets previous setpoint to 6 so the ramp starts correctly |
| **3b — 6 → 2 Decline** | 1 (open) | `target: flow`, value: 2 g/s, linear ramp 5s, adaptive: false | 5s | ramps from 6 g/s (Phase 3a setpoint) to 2 g/s |
| **Release** | 1 (open) | off | 2s | — |

---

## Phase 1 — Pressure Build Detail

**Pump config:** `target: "pressure"`, pressure: X, flow: 0 (no flow soft-limit)

**Transition:** `{ "type": "ease-out", "duration": 25, "adaptive": false }`

The ease-out easing causes the pressure setpoint to ramp quickly from 0 toward X in the first few seconds, then decelerate as it approaches X. The PID controller follows this — pump drives hard initially for fast buildup, then backs off near the target to prevent overshoot.

**Stop conditions:**
1. `{ "type": "pressure", "operator": "gte", "value": X }` — fires when the pressure sensor reads ≥ X. Normal exit path.
2. `duration: 30` — safety cap. If the target is never reached (e.g. machine under-pressure for 11 bar target), the phase times out at 30s and the test continues.

---

## Generator Script

**Location:** `scripts/generate_pressure_test_profiles.py`
**Output:** `data/p/sp-test-v1.json` … `data/p/sp-test-v6.json`

**Behavior:**
- Builds the 48 combinations by computing the cartesian product of pressure targets × flow variants
- Shuffles each variant's combination list with a fixed seed (`seed = variant_index`, 0–5) for reproducibility
- Generates phases for each test unit according to the schema above
- Writes one valid GaggiMate profile JSON per variant
- Profile metadata: `type: "pro"`, `temperature: 93`, label: `"SP Test v{n} (seed {n})"`

**No dependencies beyond Python stdlib.** Run with:
```bash
python scripts/generate_pressure_test_profiles.py
```

---

## Output File Summary

| File | Profile label | Seed |
|---|---|---|
| `data/p/sp-test-v1.json` | SP Test v1 (seed 0) | 0 |
| `data/p/sp-test-v2.json` | SP Test v2 (seed 1) | 1 |
| `data/p/sp-test-v3.json` | SP Test v3 (seed 2) | 2 |
| `data/p/sp-test-v4.json` | SP Test v4 (seed 3) | 3 |
| `data/p/sp-test-v5.json` | SP Test v5 (seed 4) | 4 |
| `data/p/sp-test-v6.json` | SP Test v6 (seed 5) | 5 |

Each file is approximately 200 phases and 80–120 KB.

---

## Statistical Notes

- Run profiles in randomized order across sessions to control for session-level drift (machine warm-up, grind consistency, barista fatigue)
- The 6 independent orderings of the same 48 combinations give 6 replicates per cell → sufficient for one-way ANOVA per flow variant (pressure as factor, output weight as response)
- Record: dose in, yield out, TDS if available, ambient temp
- The shot history (`data/w/`) logs pressure, flow, and volume at ~100ms intervals — the weight curve is available post-hoc for each test

---

## Open Questions / Assumptions

- `0.3 bar` used for the "< 0.5 bar" condition — confirm or adjust
- Temperature fixed at 93°C across all tests — adjust in script if needed
- Phase 1 flow soft-limit set to 0 (no cap) — the pump is pressure-controlled
- Phase 3 pressure soft-limit set to 0 (no cap on pressure) — the pump is flow-controlled
