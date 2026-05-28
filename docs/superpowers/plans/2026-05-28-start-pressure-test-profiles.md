# Start Pressure Test Profile Generator — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a Python script that generates 6 randomized GaggiMate profile JSON files covering all 48 start-pressure × flow-rate test combinations.

**Architecture:** A single importable Python script (`scripts/generate_pressure_test_profiles.py`) exposes pure builder functions and a `main()` entry point. A pytest test file validates phase structure and profile completeness before any files are written. Generated profiles go to `data/p/sp-test-v{1..6}.json`.

**Tech Stack:** Python 3 stdlib (json, random, itertools, pathlib). pytest for tests.

---

### Task 1: Scaffold — test file + script skeleton

**Files:**
- Create: `scripts/generate_pressure_test_profiles.py`
- Create: `scripts/tests/__init__.py`
- Create: `scripts/tests/test_generate_profiles.py`

- [ ] **Step 1: Create the test directory**

```bash
mkdir -p scripts/tests && touch scripts/tests/__init__.py
```

- [ ] **Step 2: Write the failing import test**

Create `scripts/tests/test_generate_profiles.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generate_pressure_test_profiles import (
    PRESSURE_TARGETS,
    FLOW_VARIANTS,
    build_pressure_phase,
    build_stabilize_phase,
    build_flow_phase,
    build_anchor_phase,
    build_declining_flow_phase,
    build_release_phase,
    build_test_unit,
    build_profile,
)
```

- [ ] **Step 3: Run — verify it fails**

```bash
cd scripts && python -m pytest tests/test_generate_profiles.py -v
```

Expected output: `ImportError: No module named 'generate_pressure_test_profiles'`

- [ ] **Step 4: Create the script skeleton**

Create `scripts/generate_pressure_test_profiles.py`:

```python
import json
import random
from pathlib import Path

PRESSURE_TARGETS = [0.3, 1.0, 1.5, 2.0, 4.0, 6.0, 8.0, 11.0]
FLOW_CONSTANTS   = [1.5, 2.0, 2.5, 4.0, 6.0]
FLOW_DECLINING   = ("6to2", 6.0, 2.0)   # (label, start_g_s, end_g_s)
FLOW_VARIANTS    = FLOW_CONSTANTS + [FLOW_DECLINING]
TEMPERATURE      = 93
NUM_VARIANTS     = 6
OUTPUT_DIR       = Path(__file__).parent.parent / "data" / "p"


def build_pressure_phase(pressure_target: float) -> dict:
    pass

def build_stabilize_phase() -> dict:
    pass

def build_flow_phase(flow_rate: float) -> dict:
    pass

def build_anchor_phase(flow_rate: float) -> dict:
    pass

def build_declining_flow_phase(end_flow: float) -> dict:
    pass

def build_release_phase() -> dict:
    pass

def build_test_unit(pressure_target: float, flow_variant) -> list:
    pass

def build_profile(seed: int) -> dict:
    pass


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for seed in range(NUM_VARIANTS):
        profile = build_profile(seed)
        path = OUTPUT_DIR / f"sp-test-v{seed + 1}.json"
        path.write_text(json.dumps(profile, indent=2))
        print(f"Wrote {path} ({len(profile['phases'])} phases)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run — verify import test now passes**

```bash
cd scripts && python -m pytest tests/test_generate_profiles.py -v
```

Expected: PASS (import succeeds; no assertions yet)

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_pressure_test_profiles.py scripts/tests/
git commit -m "feat: scaffold pressure test profile generator and test file"
```

---

### Task 2: Phase builder functions

**Files:**
- Modify: `scripts/generate_pressure_test_profiles.py`
- Modify: `scripts/tests/test_generate_profiles.py`

Each builder produces one phase dict. Tests verify structure before implementation.

- [ ] **Step 1: Add failing tests for all six phase builders**

Append to `scripts/tests/test_generate_profiles.py`:

```python
def test_build_pressure_phase():
    p = build_pressure_phase(4.0)
    assert p["name"] == "Build 4.0 bar"
    assert p["phase"] == "preinfusion"
    assert p["valve"] == 0
    assert p["duration"] == 30
    assert p["temperature"] == 0
    assert p["transition"] == {"type": "ease-out", "duration": 25, "adaptive": False}
    assert p["pump"] == {"target": "pressure", "pressure": 4.0, "flow": 0}
    assert p["targets"] == [{"type": "pressure", "operator": "gte", "value": 4.0}]


def test_build_stabilize_phase():
    p = build_stabilize_phase()
    assert p["name"] == "Stabilize"
    assert p["phase"] == "preinfusion"
    assert p["valve"] == 0
    assert p["duration"] == 2
    assert p["temperature"] == 0
    assert p["pump"] == 0
    assert "transition" not in p
    assert "targets" not in p


def test_build_flow_phase():
    p = build_flow_phase(2.5)
    assert p["name"] == "Extract 2.5 g/s"
    assert p["phase"] == "brew"
    assert p["valve"] == 1
    assert p["duration"] == 5
    assert p["temperature"] == 0
    assert p["pump"] == {"target": "flow", "pressure": 0, "flow": 2.5}
    assert "transition" not in p
    assert "targets" not in p


def test_build_anchor_phase():
    p = build_anchor_phase(6.0)
    assert p["name"] == "Anchor 6.0 g/s"
    assert p["phase"] == "brew"
    assert p["valve"] == 1
    assert p["duration"] == 0.5
    assert p["temperature"] == 0
    assert p["pump"] == {"target": "flow", "pressure": 0, "flow": 6.0}
    assert "transition" not in p


def test_build_declining_flow_phase():
    p = build_declining_flow_phase(2.0)
    assert p["name"] == "Decline to 2.0 g/s"
    assert p["phase"] == "brew"
    assert p["valve"] == 1
    assert p["duration"] == 5
    assert p["temperature"] == 0
    assert p["transition"] == {"type": "linear", "duration": 5, "adaptive": False}
    assert p["pump"] == {"target": "flow", "pressure": 0, "flow": 2.0}
    assert "targets" not in p


def test_build_release_phase():
    p = build_release_phase()
    assert p["name"] == "Release"
    assert p["phase"] == "brew"
    assert p["valve"] == 1
    assert p["duration"] == 2
    assert p["temperature"] == 0
    assert p["pump"] == 0
    assert "transition" not in p
    assert "targets" not in p
```

- [ ] **Step 2: Run — verify all six fail**

```bash
cd scripts && python -m pytest tests/test_generate_profiles.py -v
```

Expected: 6 failures (all builders return `None`)

- [ ] **Step 3: Implement all six builders**

Replace the stub functions in `scripts/generate_pressure_test_profiles.py`:

```python
def build_pressure_phase(pressure_target: float) -> dict:
    return {
        "name": f"Build {pressure_target} bar",
        "phase": "preinfusion",
        "valve": 0,
        "duration": 30,
        "temperature": 0,
        "transition": {"type": "ease-out", "duration": 25, "adaptive": False},
        "pump": {"target": "pressure", "pressure": pressure_target, "flow": 0},
        "targets": [{"type": "pressure", "operator": "gte", "value": pressure_target}],
    }


def build_stabilize_phase() -> dict:
    return {
        "name": "Stabilize",
        "phase": "preinfusion",
        "valve": 0,
        "duration": 2,
        "temperature": 0,
        "pump": 0,
    }


def build_flow_phase(flow_rate: float) -> dict:
    return {
        "name": f"Extract {flow_rate} g/s",
        "phase": "brew",
        "valve": 1,
        "duration": 5,
        "temperature": 0,
        "pump": {"target": "flow", "pressure": 0, "flow": flow_rate},
    }


def build_anchor_phase(flow_rate: float) -> dict:
    return {
        "name": f"Anchor {flow_rate} g/s",
        "phase": "brew",
        "valve": 1,
        "duration": 0.5,
        "temperature": 0,
        "pump": {"target": "flow", "pressure": 0, "flow": flow_rate},
    }


def build_declining_flow_phase(end_flow: float) -> dict:
    return {
        "name": f"Decline to {end_flow} g/s",
        "phase": "brew",
        "valve": 1,
        "duration": 5,
        "temperature": 0,
        "transition": {"type": "linear", "duration": 5, "adaptive": False},
        "pump": {"target": "flow", "pressure": 0, "flow": end_flow},
    }


def build_release_phase() -> dict:
    return {
        "name": "Release",
        "phase": "brew",
        "valve": 1,
        "duration": 2,
        "temperature": 0,
        "pump": 0,
    }
```

- [ ] **Step 4: Run — verify all six pass**

```bash
cd scripts && python -m pytest tests/test_generate_profiles.py -v
```

Expected: 6 PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_pressure_test_profiles.py scripts/tests/test_generate_profiles.py
git commit -m "feat: implement phase builder functions with tests"
```

---

### Task 3: Test unit and profile assembly

**Files:**
- Modify: `scripts/generate_pressure_test_profiles.py`
- Modify: `scripts/tests/test_generate_profiles.py`

- [ ] **Step 1: Add failing tests for `build_test_unit` and `build_profile`**

Append to `scripts/tests/test_generate_profiles.py`:

```python
def test_build_test_unit_standard_flow():
    unit = build_test_unit(2.0, 2.0)
    assert len(unit) == 4
    assert unit[0]["name"] == "Build 2.0 bar"
    assert unit[1]["name"] == "Stabilize"
    assert unit[2]["name"] == "Extract 2.0 g/s"
    assert unit[3]["name"] == "Release"


def test_build_test_unit_declining_flow():
    unit = build_test_unit(4.0, ("6to2", 6.0, 2.0))
    assert len(unit) == 5
    assert unit[0]["name"] == "Build 4.0 bar"
    assert unit[1]["name"] == "Stabilize"
    assert unit[2]["name"] == "Anchor 6.0 g/s"
    assert unit[3]["name"] == "Decline to 2.0 g/s"
    assert unit[4]["name"] == "Release"


def test_build_profile_phase_count():
    profile = build_profile(0)
    # 40 standard tests × 4 phases + 8 declining tests × 5 phases = 200
    assert len(profile["phases"]) == 200


def test_build_profile_metadata():
    profile = build_profile(0)
    assert profile["type"] == "pro"
    assert profile["temperature"] == 93
    assert "SP Test v1" in profile["label"]
    assert "phases" in profile
    assert "label" in profile
    assert "description" in profile


def test_build_profile_contains_all_48_combinations():
    from collections import Counter
    profile = build_profile(0)
    build_phases = [p for p in profile["phases"] if p.get("name", "").startswith("Build")]
    # 48 test units → 48 build phases
    assert len(build_phases) == 48
    # Each of the 8 pressure targets appears exactly 6 times (once per flow variant)
    pressure_counts = Counter(p["pump"]["pressure"] for p in build_phases)
    assert set(pressure_counts.values()) == {6}
    assert set(pressure_counts.keys()) == set(PRESSURE_TARGETS)


def test_six_profiles_have_different_orderings():
    profiles = [build_profile(seed) for seed in range(6)]
    # Extract the sequence of pressure targets from each profile
    def pressure_sequence(profile):
        return [
            p["pump"]["pressure"]
            for p in profile["phases"]
            if isinstance(p.get("pump"), dict) and p["pump"].get("target") == "pressure"
        ]
    sequences = [pressure_sequence(p) for p in profiles]
    # All 6 sequences must be different
    unique = {tuple(s) for s in sequences}
    assert len(unique) == 6
```

- [ ] **Step 2: Run — verify tests fail**

```bash
cd scripts && python -m pytest tests/test_generate_profiles.py -v
```

Expected: failures on the 7 new tests (builders return `None`)

- [ ] **Step 3: Implement `build_test_unit` and `build_profile`**

Replace the stub functions in `scripts/generate_pressure_test_profiles.py`:

```python
def build_test_unit(pressure_target: float, flow_variant) -> list:
    phases = [
        build_pressure_phase(pressure_target),
        build_stabilize_phase(),
    ]
    if isinstance(flow_variant, tuple):
        _label, start_flow, end_flow = flow_variant
        phases.append(build_anchor_phase(start_flow))
        phases.append(build_declining_flow_phase(end_flow))
    else:
        phases.append(build_flow_phase(flow_variant))
    phases.append(build_release_phase())
    return phases


def build_profile(seed: int) -> dict:
    combinations = [
        (pressure, flow)
        for pressure in PRESSURE_TARGETS
        for flow in FLOW_VARIANTS
    ]
    rng = random.Random(seed)
    rng.shuffle(combinations)

    phases = []
    for pressure, flow in combinations:
        phases.extend(build_test_unit(pressure, flow))

    return {
        "label": f"SP Test v{seed + 1} (seed {seed})",
        "type": "pro",
        "description": (
            f"Start pressure test profile, variant {seed + 1}. "
            f"48 combinations (8 pressures × 6 flow variants) randomized with seed {seed}."
        ),
        "temperature": TEMPERATURE,
        "phases": phases,
    }
```

- [ ] **Step 4: Run — verify all tests pass**

```bash
cd scripts && python -m pytest tests/test_generate_profiles.py -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_pressure_test_profiles.py scripts/tests/test_generate_profiles.py
git commit -m "feat: implement test unit and profile assembly with tests"
```

---

### Task 4: Generate the 6 profile files and verify

**Files:**
- Generated: `data/p/sp-test-v1.json` … `data/p/sp-test-v6.json`

- [ ] **Step 1: Run the generator**

```bash
cd scripts && python generate_pressure_test_profiles.py
```

Expected output:
```
Wrote .../data/p/sp-test-v1.json (200 phases)
Wrote .../data/p/sp-test-v2.json (200 phases)
Wrote .../data/p/sp-test-v3.json (200 phases)
Wrote .../data/p/sp-test-v4.json (200 phases)
Wrote .../data/p/sp-test-v5.json (200 phases)
Wrote .../data/p/sp-test-v6.json (200 phases)
```

- [ ] **Step 2: Spot-check the first file**

```bash
python -c "
import json
p = json.loads(open('data/p/sp-test-v1.json').read())
print('label:', p['label'])
print('type:', p['type'])
print('temperature:', p['temperature'])
print('phase count:', len(p['phases']))
print('first phase:', json.dumps(p['phases'][0], indent=2))
print('second phase:', json.dumps(p['phases'][1], indent=2))
print('third phase:', json.dumps(p['phases'][2], indent=2))
print('fourth phase:', json.dumps(p['phases'][3], indent=2))
"
```

Expected: label contains "SP Test v1", type is "pro", temperature is 93, 200 phases. First four phases are a complete test unit (Build / Stabilize / Extract or Anchor+Decline / Release).

- [ ] **Step 3: Verify all 6 files have unique phase orderings**

```bash
python -c "
import json
from pathlib import Path
seqs = []
for i in range(1, 7):
    p = json.loads((Path('data/p') / f'sp-test-v{i}.json').read_text())
    seq = [ph['name'] for ph in p['phases'] if 'Build' in ph['name']]
    seqs.append(tuple(seq))
print('Unique orderings:', len(set(seqs)), '(expected 6)')
"
```

Expected: `Unique orderings: 6`

- [ ] **Step 4: Commit the generated files**

```bash
git add data/p/sp-test-v1.json data/p/sp-test-v2.json data/p/sp-test-v3.json \
        data/p/sp-test-v4.json data/p/sp-test-v5.json data/p/sp-test-v6.json
git commit -m "feat: generate start pressure test profiles (6 variants, 48 combos each)"
```
