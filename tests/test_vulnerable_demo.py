from pathlib import Path

from vigil_fuse.scanner import scan


def test_vulnerable_demo_native_findings_and_safe_controls() -> None:
    target = Path(__file__).resolve().parents[1] / "demo" / "vulnerable-device"
    result = scan(target, profile="esp-idf")
    findings = result.findings
    assert {f"FUSE{number:03d}" for number in range(1, 8)} <= {
        finding.rule_id for finding in findings
    }
    assert not any(finding.file.endswith("safe_controls.py") for finding in findings)
    credential = next(finding for finding in findings if finding.rule_id == "FUSE001")
    assert "[REDACTED]" in credential.evidence
    assert "fuse_demo_password_only" not in credential.evidence
