pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    // Poll GitHub every minute so builds start without an inbound webhook.
    triggers {
        pollSCM('* * * * *')
    }

    environment {
        IMAGE_NAME     = 'securepipeline-demo'
        CONTAINER_NAME = 'securepipeline-demo'
        // Host port the deployed app is published on. Jenkins uses 8082 and SonarQube 9000.
        APP_HOST_PORT  = '8081'
        SONAR_URL      = 'http://host.docker.internal:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "Building commit: $(git rev-parse --short HEAD)"'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --quiet -r requirements-dev.txt
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    mkdir -p reports
                    . .venv/bin/activate
                    pytest -v --junitxml=reports/junit.xml --cov=app --cov-report=xml:reports/coverage.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    // The scanner runs as a sibling container that shares this container's volumes,
                    // so it sees the workspace at the same path.
                    sh '''
                        docker run --rm --volumes-from jenkins -w "$WORKSPACE" \
                            -e SONAR_HOST_URL="$SONAR_URL" -e SONAR_TOKEN="$SONAR_TOKEN" \
                            sonarsource/sonar-scanner-cli:12.2.0.4256_8.1.0
                        python3 scripts/fetch_sonar_status.py
                    '''
                }
            }
        }

        stage('Dependency-Check') {
            steps {
                // Scan only the runtime requirements, not the test tooling.
                sh '''
                    . .venv/bin/activate
                    pip install --quiet --target .deps -r requirements.txt
                    mkdir -p reports/dependency-check
                    dependency-check.sh --project securepipeline --scan .deps \
                        --format JSON --format HTML --out reports/dependency-check \
                        --data /opt/dependency-check-data \
                        ${NVD_API_KEY:+--nvdApiKey "$NVD_API_KEY"}
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Trivy Scan') {
            steps {
                // Reports fixable HIGH and CRITICAL findings; the Security Gate decides pass or fail.
                sh '''
                    mkdir -p reports
                    trivy image --format json --output reports/trivy.json \
                        --severity HIGH,CRITICAL --ignore-unfixed --exit-code 0 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Security Gate') {
            steps {
                sh '''
                    python3 scripts/security_gate.py \
                        --sonar reports/sonar-gate.json \
                        --dependency-check reports/dependency-check/dependency-check-report.json \
                        --trivy reports/trivy.json
                '''
            }
        }

        // Runs only when every stage above, including the Security Gate, passed.
        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} 2>/dev/null || true
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_HOST_PORT}:5000 ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                // Jenkins runs in a container, so the published port is reached via the Docker host.
                sh '''
                    for i in $(seq 1 15); do
                        if curl -fsS http://host.docker.internal:${APP_HOST_PORT}/health | grep -q "Application is healthy"; then
                            echo "Smoke test passed"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "Smoke test failed. Container logs:"
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
    }
}
