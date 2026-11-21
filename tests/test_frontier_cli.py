import json
from pathlib import Path

from vigil_fuse.cli import main


def test_digital_twin_command_outputs_explicit_partial_evidence(tmp_path: Path, capsys) -> None:
    (tmp_path / "chip.svd").write_text('''<device><name>Chip</name><peripherals>
      <peripheral><name>UART</name><baseAddress>0x4000</baseAddress><registers>
      <register><name>STATUS</name><addressOffset>0</addressOffset></register>
      </registers></peripheral></peripherals></device>''', encoding="utf-8")
    result = main(["digital-twin", str(tmp_path), "--svd", "chip.svd", "--peripheral", "UART"])
    output = json.loads(capsys.readouterr().out)
    assert result == 1
    assert output["status"] == "partial"
    assert output["svd_source"] == "chip.svd"
    assert output["peripherals"][0]["name"] == "UART"


def test_digital_twin_command_rejects_external_file(tmp_path: Path, capsys) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.svd"
    outside.write_text("<device/>", encoding="utf-8")
    result = main(["digital-twin", str(root), "--svd", str(outside)])
    assert result == 2
    assert "inside" in capsys.readouterr().err


def test_flight_bus_and_seu_commands_disclose_partial_status(tmp_path: Path, capsys) -> None:
    (tmp_path / "app.c").write_text('bool armed;\nCFE_SB_Subscribe(CMD_MID, app.pipe);',
                                    encoding="utf-8")
    assert main(["flight-bus", str(tmp_path), "--source", "PAYLOAD=app.c"]) == 1
    graph = json.loads(capsys.readouterr().out)
    assert graph["status"] == "partial"
    assert any(edge["relation"] == "subscribes_to" for edge in graph["edges"])
    assert main(["seu", str(tmp_path), "--source", "app.c"]) == 1
    state = json.loads(capsys.readouterr().out)
    assert state["status"] == "partial" and state["source"] == "app.c"
    assert state["states"][0]["name"] == "armed"


def test_flight_bus_rejects_duplicate_source_assignment(tmp_path: Path, capsys) -> None:
    (tmp_path / "app.c").write_text("", encoding="utf-8")
    result = main(["flight-bus", str(tmp_path), "--source", "A=app.c", "--source", "B=app.c"])
    assert result == 2
    assert "more than once" in capsys.readouterr().err
