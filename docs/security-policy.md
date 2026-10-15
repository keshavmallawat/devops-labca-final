# Security policy

This document explains what each security control in the pipeline checks and when a build is blocked.

## Controls

| Control | Type | What it checks | Where it runs |
|---|---|---|---|
| SonarQube | SAST | The application source code and tests for bugs, vulnerabilities and security hotspots, and applies the quality gate | `SonarQube Analysis` stage |
| OWASP Dependency-Check | SCA | The runtime Python dependencies against the National Vulnerability Database (NVD) | `Dependency-Check` stage |
| Trivy | Container scan | The packages inside the built Docker image | `Trivy Scan` stage |
| Security gate | Policy | Reads the three reports above and decides whether deployment may continue | `Security Gate` stage |

## Gate rules

`scripts/security_gate.py` blocks the build (non-zero exit, deployment skipped) if any of these is true:

1. Dependency-Check reports a vulnerability with a CVSS score of 7.0 or higher. The highest of the CVSS v4, v3 and v2 scores is used. If a finding has no score, its severity label is used instead.
2. Trivy reports a HIGH or CRITICAL vulnerability in the image. Only findings that already have a fixed version are reported (`--ignore-unfixed`), so a build is not blocked by something the team cannot patch.
3. The SonarQube quality gate status is anything other than `OK`.
4. A report is missing or cannot be read.

### Why these thresholds

- CVSS 7.0 is the start of the "High" range in the CVSS scale, so Medium and Low findings are reported but do not stop a deployment.
- Ignoring unfixed findings keeps the demo deterministic: every blocking finding has a concrete remediation (upgrade the package).
- The SonarQube quality gate is the default gate, which fails on new bugs, vulnerabilities and hotspots that are not reviewed.

### Fail closed

If a scanner does not run or its report cannot be read, the gate treats that as a failure. A missing check is never treated as a pass. This is the "fail closed" principle: when the pipeline cannot prove that a build is safe, it does not deploy it.

## Handling secrets

- The SonarQube token is stored as a Jenkins "Secret text" credential with the ID `sonar-token`. It is injected with `withCredentials`, so Jenkins masks it in the logs.
- The NVD API key is kept in `infra/.env`, which is git-ignored. Only `infra/.env.example` is committed.
- No secrets are stored in the `Jenkinsfile` or in the repository.

## Remediation workflow

1. A scan blocks a build and the report names the package and the CVE.
2. The developer upgrades the package to a fixed version in `requirements.txt` and pushes.
3. The pipeline runs again. If all checks pass, the gate passes and the new image is deployed.
