pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')  // Fallback polling
        githubPush()  # Primary trigger
    }

    environment {
        DOCKER_IMAGE = "kaymima/django-devops-app"
        DROPLET_IP = "142.93.244.44"
        SSH_USER = "root"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm  # Automatically checks out triggering commit
            }
        }

        stage('Build & Test') {
            steps {
                sh 'docker-compose -f docker-compose.prod.yml build'
                sh 'python manage.py test'
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                    docker login -u $DOCKER_USER -p $DOCKER_PASS
                    docker-compose push
                    ssh ${SSH_USER}@${DROPLET_IP} "docker-compose pull && docker-compose up -d"
                    """
                }
            }
        }
    }
}