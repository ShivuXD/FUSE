import pytest

from vigil_fuse.flight_bus import build_bus_graph, extract_bus_calls
from vigil_fuse.flight_policy import MAX_POLICY_BYTES, apply_bus_policy, parse_bus_policy


POLICY = b'''[flight_software.components.PAYLOAD]
criticality = "medium"
trust = "low"
[flight_software.components.ADCS]
criticality = "critical"
[flight_software.messages.ADCS_CMD_MID]
allowed_subscribers = ["ADCS"]
'''


def test_configured_boundary_produces_candidate_without_invented_severity() -> None:
    calls = extract_bus_calls({"payload.c": b'CFE_SB_Subscribe(ADCS_CMD_MID, pipe);',
                               "adcs.c": b'CFE_SB_Subscribe(ADCS_CMD_MID, pipe);'})
    graph = build_bus_graph(calls, {"payload.c": "PAYLOAD", "adcs.c": "ADCS"})
    result = apply_bus_policy(graph, parse_bus_policy(POLICY, "flight.toml"))
    assert result.policy_source == "flight.toml" and len(result.policy_sha256) == 64
    assert len(result.policy_observations) == 1
    observation = result.policy_observations[0]
    assert observation.application == "PAYLOAD"
    assert observation.message_expression == "ADCS_CMD_MID"
    assert observation.severity == "unknown" and observation.validation_status == "not-validated"
    assert next(item for item in result.components if item.name == "ADCS").criticality == "critical"


def test_bad_and_oversized_policy_are_rejected() -> None:
    with pytest.raises(ValueError):
        parse_bus_policy(b'x' * (MAX_POLICY_BYTES + 1), "policy.toml")
    with pytest.raises(ValueError):
        parse_bus_policy(b'[flight_software.messages.X]\nallowed_subscribers = "ADCS"', "x")
