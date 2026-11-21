"""Conservative correlation of explicitly supplied pin mappings and design evidence."""

from __future__ import annotations

from dataclasses import dataclass

from .device_tree import DeviceTreeResult
from .hardware_netlist import NetlistTopology

MAX_RESOURCE_PINS = 256
MAX_PHYSICAL_CONNECTIONS = 10_000


@dataclass(frozen=True)
class ResourceBinding:
    finding_id: str
    resource_id: str
    device_tree_node: str
    component: str
    pins: tuple[str, ...]
    mapping_evidence: str


@dataclass(frozen=True)
class PhysicalConnection:
    mcu_pin: str
    net: str
    endpoint: str
    endpoint_pin: str


@dataclass(frozen=True)
class PhysicalReachability:
    finding_id: str
    resource_id: str
    device_tree_node: str
    physical_status: str
    confidence: str
    observed_device_status: str | None
    connections: tuple[PhysicalConnection, ...]
    mapping_evidence: str
    limitations: tuple[str, ...]


def correlate_physical_evidence(
    binding: ResourceBinding, tree: DeviceTreeResult, topology: NetlistTopology
) -> PhysicalReachability:
    """Correlate an operator-supplied mapping; do not infer pins or exploitability."""
    if (
        not binding.finding_id or not binding.resource_id or not binding.device_tree_node
        or not binding.component or not binding.mapping_evidence or not binding.pins
        or len(binding.pins) > MAX_RESOURCE_PINS or any(not pin for pin in binding.pins)
    ):
        raise ValueError("A bounded, evidenced resource-to-pin mapping is required")
    nodes = [node for node in tree.nodes if node.path == binding.device_tree_node]
    limitations = [
        "The resource-to-pin mapping is supplied by the caller and has not been verified.",
        "Netlist connector candidates do not prove physical access or exploitability.",
    ]
    connections: list[PhysicalConnection] = []
    if topology.status in {"parsed", "partial"}:
        pins = set(binding.pins)
        for net in topology.nets:
            source_pins = {
                endpoint.pin for endpoint in net.endpoints
                if endpoint.reference == binding.component and endpoint.pin in pins
            }
            for source_pin in sorted(source_pins):
                for endpoint in net.endpoints:
                    if endpoint.connector_candidate and endpoint.reference != binding.component:
                        if len(connections) >= MAX_PHYSICAL_CONNECTIONS:
                            break
                        connections.append(PhysicalConnection(
                            source_pin, net.name, endpoint.reference, endpoint.pin
                        ))
                if len(connections) >= MAX_PHYSICAL_CONNECTIONS:
                    break
            if len(connections) >= MAX_PHYSICAL_CONNECTIONS:
                limitations.append("Connection output reached its limit; further paths were omitted.")
                break
    if tree.status != "parsed":
        limitations.append("Device-tree preprocessing and configuration are incomplete.")
    if topology.status != "parsed":
        limitations.append("Netlist topology is unavailable or incomplete.")
    if len(nodes) != 1:
        limitations.append("The selected device-tree node is missing or ambiguous.")
    elif nodes[0].property("status") is None:
        limitations.append("No literal device status was observed.")
    # shortcut: pin bindings and device-tree preprocessing are not verified, upgrade before verdicts.
    return PhysicalReachability(
        binding.finding_id, binding.resource_id, binding.device_tree_node,
        "PARTIAL" if len(nodes) == 1 and topology.status in {"parsed", "partial"} else "UNKNOWN",
        "low", nodes[0].property("status") if len(nodes) == 1 else None,
        tuple(sorted(connections, key=lambda c: (c.mcu_pin, c.net, c.endpoint, c.endpoint_pin))),
        binding.mapping_evidence, tuple(limitations),
    )
