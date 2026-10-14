FROM jenkins/jenkins:lts-jdk21

USER root

# Python for install/test stages, curl+unzip for the tool downloads below.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv python3-pip curl unzip ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Docker CLI only. The daemon is Docker Desktop's, reached through the mounted socket.
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker

ARG TRIVY_VERSION=0.75.0

RUN curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" \
    -o /tmp/trivy.tar.gz \
 && tar -xzf /tmp/trivy.tar.gz -C /usr/local/bin trivy \
 && chmod +x /usr/local/bin/trivy \
 && rm /tmp/trivy.tar.gz

 
ARG DEPENDENCY_CHECK_VERSION=12.2.2

RUN curl -fsSL "https://github.com/dependency-check/DependencyCheck/releases/download/v${DEPENDENCY_CHECK_VERSION}/dependency-check-${DEPENDENCY_CHECK_VERSION}-release.zip" \
    -o /tmp/dependency-check.zip \
 && unzip -q /tmp/dependency-check.zip -d /opt \
 && chmod +x /opt/dependency-check/bin/dependency-check.sh \
 && ln -s /opt/dependency-check/bin/dependency-check.sh /usr/local/bin/dependency-check \
 && rm /tmp/dependency-check.zip

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
