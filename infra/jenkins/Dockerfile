FROM jenkins/jenkins:lts-jdk21

USER root

# Python for install/test stages, curl+unzip for the tool downloads below.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv python3-pip curl unzip ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Docker CLI only. The daemon is Docker Desktop's, reached through the mounted socket.
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker

ARG TRIVY_VERSION=0.74.0
RUN cd /tmp \
 && curl -fsSLO "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" \
 && curl -fsSLO "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_checksums.txt" \
 && grep " trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz\$" trivy_${TRIVY_VERSION}_checksums.txt | sha256sum -c - \
 && tar -xzf trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz -C /usr/local/bin trivy \
 && chmod +x /usr/local/bin/trivy \
 && rm -f /tmp/trivy_* \
 && trivy --version

ARG DEPENDENCY_CHECK_VERSION=13.0.0
RUN cd /tmp \
 && curl -fsSLO "https://github.com/dependency-check/DependencyCheck/releases/download/v${DEPENDENCY_CHECK_VERSION}/dependency-check-${DEPENDENCY_CHECK_VERSION}-release.zip" \
 && unzip -q dependency-check-${DEPENDENCY_CHECK_VERSION}-release.zip -d /opt \
 && chmod +x /opt/dependency-check/bin/dependency-check.sh \
 && rm -f /tmp/dependency-check-*.zip \
 && /opt/dependency-check/bin/dependency-check.sh --version

ENV PATH="/opt/dependency-check/bin:${PATH}" \
    TRIVY_CACHE_DIR=/var/cache/trivy
RUN mkdir -p /var/cache/trivy /opt/dependency-check-data \
 && chown -R jenkins:jenkins /var/cache/trivy /opt/dependency-check /opt/dependency-check-data
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
