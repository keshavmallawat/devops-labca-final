# SecurePipeline

A Jenkins-based DevSecOps pipeline that builds, tests, scans and deploys a small Flask application, and blocks the deployment when a scan finds a serious vulnerability.

Built for the DevOps Laboratory CA by a team of three.

## Overview

Security checks run inside the CI/CD pipeline instead of after deployment (shift-left security). Every push is built and tested, then checked by static analysis, a dependency scan and a container image scan. A security gate decides whether the build may be deployed.

Pipeline: Code → Build → Unit tests → SonarQube (SAST) → OWASP Dependency-Check (SCA) → Docker build → Trivy image scan → Security gate → Deploy

## Tools

- Git and GitHub: version control
- Jenkins: CI/CD orchestration
- Python, Flask and Pytest: the application and its tests
- Docker: containerisation
- SonarQube: static code analysis
- OWASP Dependency-Check: vulnerable dependency scan
- Trivy: container image scan

## Demonstration

1. Clean build: every stage passes and the application is deployed.
2. Vulnerable dependency: the scan fails and the gate blocks the deployment.
3. Remediation: the dependency is upgraded, the pipeline passes and the application is deployed.

## Team

| Member | Role | GitHub |
|---|---|---|
| Keshav Mallawat | Jenkins / CI-CD | @keshavmallawat |
| Palak Chandak | Security / DevSecOps | @palakchandak8 |
| Rudra Shetye | Application / Docker | @RudraShetye |

## Status

Under construction. This README is extended as each part of the pipeline is merged.

## Run locally

    python3 -m venv venv && . venv/bin/activate
    pip install -r requirements-dev.txt
    pytest -v
    python app.py            # http://127.0.0.1:5000

## Run in Docker

    docker build -t securepipeline-demo:local .
    docker run -d --name securepipeline-demo -p 8081:5000 securepipeline-demo:local
    curl http://localhost:8081/health
