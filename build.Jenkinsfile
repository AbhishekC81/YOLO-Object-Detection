pipeline {

    agent any


    stages {

        stage('Authentication') {

            steps {

                sh '''
                aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 854171615125.dkr.ecr.eu-north-1.amazonaws.com

                '''

            }

        }


        stage('Build') {

            steps {

                sh 'docker build -t abhishekc-yolo5 ./Yolo5'

            }

        }


        stage('Push to ECR') {

            steps {

                sh '''
                docker tag abhishekc-yolo5:latest 854171615125.dkr.ecr.eu-north-1.amazonaws.com/abhishekc-yolo5:${BUILD_NUMBER}
                docker push 854171615125.dkr.ecr.eu-north-1.amazonaws.com/abhishekc-yolo5:${BUILD_NUMBER}
                '''

            }

        }

    }

}