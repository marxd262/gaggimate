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
