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

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .'
            }
        }

        // The security gate is placed in front of this stage by the security work package.
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
