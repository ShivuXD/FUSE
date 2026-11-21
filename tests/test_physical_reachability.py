from pathlib import Path

import pytest

from vigil_fuse.device_tree import parse_device_tree
from vigil_fuse.hardware_netlist import read_netlist_topology
from vigil_fuse.physical_reachability import ResourceBinding, correlate_physical_evidence


def test_explicit_binding_records_connector_without_claiming_exploitability(tmp_path: Path) -> None:
    board = tmp_path / "board.net"
    board.write_text('''<export><components>
      <comp ref="U1"><value>MCU</value></comp><comp ref="J3"><value>Header</value></comp>
      </components><nets><net name="UART2_TX"><node ref="U1" pin="42"/>
      <node ref="J3" pin="2"/></net></nets></export>''', encoding="utf-8")
    tree = parse_device_tree(b'/ { soc { serial@40004400 { status = "okay"; }; }; };')
    binding = ResourceBinding("FUSE-1", "UART2", "/soc/serial@40004400", "U1", ("42",),
                              "Operator-supplied board pin map")
    result = correlate_physical_evidence(binding, tree, read_netlist_topology(tmp_path, board))
    assert result.physical_status == "PARTIAL"
    assert result.observed_device_status == '"okay"'
    assert [(c.mcu_pin, c.net, c.endpoint, c.endpoint_pin) for c in result.connections] == [
        ("42", "UART2_TX", "J3", "2")
    ]
    assert result.confidence == "low"


def test_missing_node_is_unknown_and_empty_mapping_is_rejected(tmp_path: Path) -> None:
    tree = parse_device_tree(b'/ { };')
    topology = read_netlist_topology(tmp_path, "missing.net")
    binding = ResourceBinding("FUSE-1", "UART2", "/missing", "U1", ("42",), "board map")
    assert correlate_physical_evidence(binding, tree, topology).physical_status == "UNKNOWN"
    with pytest.raises(ValueError):
        correlate_physical_evidence(
            ResourceBinding("FUSE-1", "UART2", "/missing", "U1", (), "board map"),
            tree, topology,
        )
