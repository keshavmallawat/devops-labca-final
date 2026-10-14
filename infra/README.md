# SecurePipeline environment (Jenkins + SonarQube)

Run from this folder in PowerShell with Docker Desktop running.

    copy .env.example .env          # optionally paste your NVD API key into .env
    docker compose build
    docker compose up -d

Check the tools inside Jenkins:

    docker exec jenkins docker version
    docker exec jenkins python3 --version

Jenkins:    http://localhost:8082   (first-run password: docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword)
SonarQube:  http://localhost:9000   (first login admin / admin, you are forced to change it)

Notes
- The demo app is deployed by Jenkins as a sibling container on port 8081.
- From inside the Jenkins container, reach it at http://host.docker.internal:8081.
- Jenkins reaches SonarQube at http://sonarqube:9000 (compose network).

Stop:        docker compose down        (add -v to also wipe all data and caches)
