# SecurePipeline

SecurePipeline is a Jenkins-based DevSecOps pipeline for a small Flask application.
Every push is built, tested and scanned, and the application is deployed only if a
security gate passes. Security checks run inside the delivery pipeline instead of after it.

Built by a team of three for the DevOps Laboratory CA.

```text
Code -> Build -> Test -> SAST -> SCA -> Docker build -> Image scan -> Security gate -> Deploy
```

## What the pipeline does

| Stage | Tool | Purpose |
|---|---|---|
| Checkout | Git, GitHub | Fetch the commit being built |
| Install and unit tests | pytest | Run the application tests |
| Static analysis (SAST) | SonarQube | Analyse the source code and apply the quality gate |
| Dependency scan (SCA) | OWASP Dependency-Check | Look up the dependencies in the NVD |
| Docker build | Docker | Build the application image |
| Image scan | Trivy | Look for known vulnerabilities in the image packages |
| Security gate | `scripts/security_gate.py` | Block deployment on a blocking finding, fail closed |
| Deploy and smoke test | Docker, curl | Start the new container and check `/health` |

The gate blocks a build when Dependency-Check finds a vulnerability with CVSS 7.0 or higher,
Trivy finds a fixable HIGH or CRITICAL vulnerability, the SonarQube quality gate is not `OK`,
or a report is missing. Details are in [docs/security-policy.md](docs/security-policy.md).

## Documentation

- [Architecture](docs/architecture.md): components, stages, gate rules and secrets handling
- [Security policy](docs/security-policy.md): what each scan checks and why the thresholds were chosen
- [Demo runbook](docs/demo-runbook.md): checklist and steps for the clean, blocked and remediated runs
- [Infrastructure](infra/README.md): how to start Jenkins and SonarQube with Docker Compose

## Demonstration

1. **Clean build.** The clean `requirements.txt` passes every stage and the application is deployed.
2. **Vulnerable build.** A vulnerable dependency is pinned. Dependency-Check reports it, the gate
   fails and deployment is blocked.
3. **Remediation.** The dependency is upgraded, the pipeline passes and the application is deployed.

The full procedure is in the [demo runbook](docs/demo-runbook.md).

## Team

| Member | Area |
|---|---|
| Keshav Mallawat | Jenkins and CI/CD |
| Palak Chandak | Security and DevSecOps |
| Rudra Shetye | Application and Docker |

## Run the application

Locally:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
python app.py                    # http://localhost:5000
```

With Docker:

```bash
docker build -t securepipeline-demo .
docker run -d --name securepipeline-demo -p 8081:5000 securepipeline-demo
curl http://localhost:8081/health
```

The application serves `/` and `/health`.

## Run the pipeline

The Jenkins and SonarQube stack is started from `infra/` with `docker compose up -d`.
Copy `infra/.env.example` to `infra/.env` and add an NVD API key first; the file is git-ignored.
See [infra/README.md](infra/README.md) for the one-time Jenkins and SonarQube setup.
