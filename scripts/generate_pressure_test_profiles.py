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
