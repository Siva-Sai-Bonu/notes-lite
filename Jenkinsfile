// One pipeline, one job: test -> build image -> push to Docker Hub -> deploy -> smoke test.
//
// Jenkins credentials required:
//   dockerhub-creds : Username/Password credential for Docker Hub
pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 20, unit: 'MINUTES')
    }

    environment {
        DOCKERHUB_USER = 'sivabonu81'                 // <-- your Docker Hub username
        IMAGE_NAME     = "${DOCKERHUB_USER}/notes-api"
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        IMAGE          = "${IMAGE_NAME}:${IMAGE_TAG}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git --no-pager log -1 --oneline'
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    docker run --rm \
                      --volumes-from $(hostname) \
                      -w "$PWD" \
                      python:3.12-slim \
                      bash -c "pip install --no-cache-dir -r app/requirements-dev.txt && pytest app/test_app.py --junitxml=test-results.xml"
                '''
            }
            post {
                always { junit 'test-results.xml' }
            }
        }

        stage('Build image') {
            steps {
                sh """
                    docker build -t ${IMAGE} -t ${IMAGE_NAME}:latest ./app
                    docker image inspect ${IMAGE} --format 'built {{.Id}} ({{.Size}} bytes)'
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                        credentialsId: 'docker-hub-repo',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push "$IMAGE"
                        docker push "$IMAGE_NAME:latest"
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh """
                    APP_VERSION=${IMAGE_TAG} DOCKERHUB_USER=${DOCKERHUB_USER} \
                      docker compose pull redis
                    APP_VERSION=${IMAGE_TAG} DOCKERHUB_USER=${DOCKERHUB_USER} \
                      docker compose up -d --build
                """
            }
        }

        stage('Smoke test') {
            steps {
                sh '''
                    docker run --rm \
                      --network container:notes-nginx \
                      -e BASE_URL=http://localhost \
                      --volumes-from $(hostname) \
                      -w "$PWD" \
                      curlimages/curl:latest \
                      sh ./smoke-test.sh
                '''
            }
        }
     }

    post {
        success { echo "Deployed ${IMAGE}" }
        failure { echo "Build ${env.BUILD_NUMBER} failed - check the stage above" }
        always  { sh 'docker image prune -f || true' }
    }
}
