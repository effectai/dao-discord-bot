pipeline {
  environment {
    registry = "520776594758.dkr.ecr.eu-west-1.amazonaws.com"
    imageName = "dao-discord-bot"
    dockerImage = ""
    awsCredentials = "ecr:eu-west-1:aws-jenkins-role"
    hostname = "10.40.1.167"
  }
  agent any
  stages {
    stage ('Build 1Image') {
      steps {
        script {
          dockerImage = docker.build registry + "/$imageName:$GIT_COMMIT"
        }
      }
    }
    stage('Push Image') {
      steps{
        script {
        docker.withRegistry("https://" + registry, awsCredentials) {
            dockerImage.push()
          }
        }
      }
    }
    stage('Deploy') {
      steps {
          sshagent(credentials : ['jenkins-keypair']) {
              sh 'ssh -o StrictHostKeyChecking=no jenkins@$hostname uptime'
              sh 'ssh -v jenkins@$hostname'
              sh 'scp ./docker-compose.yml jenkins@$hostname:/home/jenkins/discord-bot.docker-compose.yml'
          }
      }
    }
  }
}