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
