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
