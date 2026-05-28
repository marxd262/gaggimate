import json
import random
from pathlib import Path
from typing import Union

PRESSURE_TARGETS = [0.3, 1.0, 1.5, 2.0, 4.0, 6.0, 8.0, 11.0]
FLOW_CONSTANTS   = [1.5, 2.0, 2.5, 4.0, 6.0]
FLOW_DECLINING   = ("6to2", 6.0, 2.0)   # (label, start_g_s, end_g_s)
FlowVariant = Union[float, tuple[str, float, float]]
FLOW_VARIANTS: list[FlowVariant] = FLOW_CONSTANTS + [FLOW_DECLINING]
TEMPERATURE      = 93
NUM_VARIANTS     = 6
OUTPUT_DIR       = Path(__file__).parent.parent / "data" / "p"


def build_pressure_phase(pressure_target: float) -> dict:
    return {
        "name": f"Build {pressure_target:.1f} bar",
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
        "name": f"Extract {flow_rate:.1f} g/s",
        "phase": "brew",
        "valve": 1,
        "duration": 5,
        "temperature": 0,
        "pump": {"target": "flow", "pressure": 0, "flow": flow_rate},
    }


def build_anchor_phase(flow_rate: float) -> dict:
    return {
        "name": f"Anchor {flow_rate:.1f} g/s",
        "phase": "brew",
        "valve": 1,
        "duration": 0.5,
        "temperature": 0,
        "pump": {"target": "flow", "pressure": 0, "flow": flow_rate},
    }


def build_declining_flow_phase(end_flow: float) -> dict:
    return {
        "name": f"Decline to {end_flow:.1f} g/s",
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

def build_test_unit(pressure_target: float, flow_variant: FlowVariant) -> list[dict]:
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


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for seed in range(NUM_VARIANTS):
        profile = build_profile(seed)
        path = OUTPUT_DIR / f"sp-test-v{seed + 1}.json"
        path.write_text(json.dumps(profile, indent=2))
        print(f"Wrote {path} ({len(profile['phases'])} phases)")


if __name__ == "__main__":
    main()
