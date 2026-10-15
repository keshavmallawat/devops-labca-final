import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import security_gate  # noqa: E402


def write(tmp_path, name, data):
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def sonar(status):
    return {"projectStatus": {"status": status}}


def dependency_check(*vulns):
    return {"dependencies": [{"fileName": "flask", "vulnerabilities": list(vulns)}]}


def trivy(*severities):
    return {
        "Results": [
            {
                "Vulnerabilities": [
                    {"PkgName": "libx", "InstalledVersion": "1", "VulnerabilityID": f"CVE-{i}", "Severity": s}
                    for i, s in enumerate(severities)
                ]
            }
        ]
    }


def run(tmp_path, sonar_data, dc_data, trivy_data, threshold=7.0):
    return security_gate.evaluate(
        write(tmp_path, "sonar.json", sonar_data),
        write(tmp_path, "dc.json", dc_data),
        write(tmp_path, "trivy.json", trivy_data),
        threshold,
    )


def test_clean_reports_pass(tmp_path):
    assert run(tmp_path, sonar("OK"), dependency_check(), trivy("LOW", "MEDIUM")) == []


def test_high_cvss_dependency_blocks(tmp_path):
    vuln = {"name": "CVE-2023-0001", "cvssv3": {"baseScore": 8.1}}
    failures = run(tmp_path, sonar("OK"), dependency_check(vuln), trivy())
    assert len(failures) == 1 and "CVE-2023-0001" in failures[0]


def test_low_cvss_dependency_passes(tmp_path):
    vuln = {"name": "CVE-2023-0002", "cvssv3": {"baseScore": 5.3}}
    assert run(tmp_path, sonar("OK"), dependency_check(vuln), trivy()) == []


def test_threshold_is_inclusive(tmp_path):
    vuln = {"name": "CVE-2023-0003", "cvssv3": {"baseScore": 7.0}}
    assert len(run(tmp_path, sonar("OK"), dependency_check(vuln), trivy())) == 1


def test_severity_label_used_when_no_score(tmp_path):
    vuln = {"name": "CVE-2023-0004", "severity": "CRITICAL"}
    assert len(run(tmp_path, sonar("OK"), dependency_check(vuln), trivy())) == 1


def test_trivy_high_and_critical_block(tmp_path):
    failures = run(tmp_path, sonar("OK"), dependency_check(), trivy("HIGH", "CRITICAL", "LOW"))
    assert len(failures) == 2


def test_failed_quality_gate_blocks(tmp_path):
    failures = run(tmp_path, sonar("ERROR"), dependency_check(), trivy())
    assert failures == ["SonarQube: quality gate status is ERROR"]


def test_missing_report_blocks(tmp_path):
    failures = security_gate.evaluate(
        str(tmp_path / "missing.json"),
        write(tmp_path, "dc.json", dependency_check()),
        write(tmp_path, "trivy.json", trivy()),
        7.0,
    )
    assert len(failures) == 1 and "report not found" in failures[0]


def test_unreadable_report_blocks(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    failures = security_gate.evaluate(
        str(bad),
        write(tmp_path, "dc.json", dependency_check()),
        write(tmp_path, "trivy.json", trivy()),
        7.0,
    )
    assert len(failures) == 1 and "report unreadable" in failures[0]


def test_main_exit_codes(tmp_path):
    args = [
        "--sonar", write(tmp_path, "s.json", sonar("OK")),
        "--dependency-check", write(tmp_path, "d.json", dependency_check()),
        "--trivy", write(tmp_path, "t.json", trivy()),
    ]
    assert security_gate.main(args) == 0
    args[1] = write(tmp_path, "s2.json", sonar("ERROR"))
    assert security_gate.main(args) == 1
