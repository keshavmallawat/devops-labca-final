FROM jenkins/jenkins:lts-jdk21

USER root

# Python for install/test stages, curl+unzip for the tool downloads below.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv python3-pip curl unzip ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Docker CLI only. The daemon is Docker Desktop's, reached through the mounted socket.
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker

USER jenkins

# Minimum plugin set: pipeline, git, SonarQube integration, test reports, stage view.
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    git \
    sonar \
    junit \
    pipeline-stage-view \
    timestamper \
    credentials-binding
