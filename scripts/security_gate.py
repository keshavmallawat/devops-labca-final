#!/usr/bin/env python3
"""Security gate: decide from the scanner reports whether a build may be deployed.

Policy:
  * OWASP Dependency-Check: fail on any vulnerability with CVSS >= threshold (default 7.0).
  * Trivy: fail on any HIGH or CRITICAL finding in the image report.
  * SonarQube: fail when the quality gate status is not OK.
  * A missing or unreadable report fails the gate.

Exit code 0 means the build may be deployed, 1 means deployment is blocked.
"""
import argparse
import json
import sys

SEVERITY_FALLBACK = {"CRITICAL": 9.0, "HIGH": 7.0, "MEDIUM": 4.0, "LOW": 0.1}
TRIVY_BLOCKING = ("HIGH", "CRITICAL")


def load_report(path):
    """Return (report, error). Exactly one of the two is None."""
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle), None
    except FileNotFoundError:
        return None, f"report not found: {path}"
    except (OSError, ValueError) as exc:
        return None, f"report unreadable: {path} ({exc})"


def cvss_score(vuln):
    """Highest CVSS base score of a Dependency-Check vulnerability, falling back to its severity label."""
    scores = []
    for key, field in (("cvssv4", "baseScore"), ("cvssv3", "baseScore"), ("cvssv2", "score")):
        block = vuln.get(key)
        if isinstance(block, dict) and isinstance(block.get(field), (int, float)):
            scores.append(float(block[field]))
    if scores:
        return max(scores)
    return SEVERITY_FALLBACK.get(str(vuln.get("severity", "")).upper(), 0.0)


def check_dependency_check(report, threshold):
    findings = []
    for dep in report.get("dependencies") or []:
        for vuln in dep.get("vulnerabilities") or []:
            score = cvss_score(vuln)
            if score >= threshold:
                findings.append(
                    f"Dependency-Check: {dep.get('fileName', '?')} {vuln.get('name', '?')} CVSS {score}"
                )
    return findings


def check_trivy(report):
    findings = []
    for result in report.get("Results") or []:
        for vuln in result.get("Vulnerabilities") or []:
            severity = str(vuln.get("Severity", "")).upper()
            if severity in TRIVY_BLOCKING:
                findings.append(
                    f"Trivy: {vuln.get('PkgName', '?')} {vuln.get('InstalledVersion', '?')} "
                    f"{vuln.get('VulnerabilityID', '?')} {severity}"
                )
    return findings


def check_sonar(report):
    status = (report.get("projectStatus") or {}).get("status")
    if status == "OK":
        return []
    return [f"SonarQube: quality gate status is {status or 'unknown'}"]


def evaluate(sonar_path, dependency_check_path, trivy_path, threshold):
    """Return the list of reasons the gate fails. An empty list means the gate passes."""
    failures = []
    for path, check in (
        (sonar_path, check_sonar),
        (dependency_check_path, lambda report: check_dependency_check(report, threshold)),
        (trivy_path, check_trivy),
    ):
        report, error = load_report(path)
        if error:
            failures.append(error)
        else:
            failures.extend(check(report))
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sonar", required=True, help="SonarQube quality gate JSON")
    parser.add_argument("--dependency-check", required=True, help="Dependency-Check JSON report")
    parser.add_argument("--trivy", required=True, help="Trivy JSON report")
    parser.add_argument("--cvss-threshold", type=float, default=7.0)
    args = parser.parse_args(argv)

    failures = evaluate(args.sonar, args.dependency_check, args.trivy, args.cvss_threshold)
    if failures:
        print("SECURITY GATE: FAILED - deployment blocked")
        for line in failures:
            print(f"  - {line}")
        return 1
    print("SECURITY GATE: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
