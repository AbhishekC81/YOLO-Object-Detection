pipeline {

    agent any
	
	environment {
		AWS_REGION = 'eu-north-1'
        ECR_REGISTRY_URL = '854171615125.dkr.ecr.eu-north-1.amazonaws.com'
        DOCKER_IMAGE_TAG = '0.0.1'
    }

    stages {

        stage('Authentication') {

            steps {

                sh '''
                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URL}

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
                docker tag abhishekc-yolo5:latest ${ECR_REGISTRY_URL}/abhishekc-yolo5:${DOCKER_IMAGE_TAG}
                docker push ${ECR_REGISTRY_URL}/abhishekc-yolo5:${DOCKER_IMAGE_TAG}
                '''

            }

        }
        
        stage('Trigger Deploy') {
        	steps {
        		build job: 'Yolo5Deploy', wait: false, parameters: [
            	string(name: 'YOLO5_IMAGE_URL', value: "${ECR_REGISTRY_URL}/abhishekc-yolo5:${DOCKER_IMAGE_TAG}")
        		]
    		}
		}

    }

}
