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
          dockerImage = docker.build(registry + "/$imageName:$GIT_COMMIT")
        }
      }
    }
    stage('Push Image') {
      steps{
        script {
          docker.withRegistry("https://" + registry, awsCredentials) {
            dockerImage.push()
            dockerImage.push('latest')
          }
        }
      }
    }
    stage('Deploy') {
      steps {
        sshagent(credentials : ['jenkins-keypair']) {
          sh "ssh jenkins@$hostname 'aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin ${registry}'"
          sh "ssh jenkins@$hostname docker pull $registry/$imageName:latest"
          script {
            runningContainers = sh(
              script: 'ssh jenkins@$hostname docker ps -f "status=running" -f "label=ai.effect.project=dao-discord-bot" --format="{{.ID}}"',
              returnStdout: true
            )
          }
          echo "Stopping running containers: $runningContainers"
          sh "ssh jenkins@$hostname docker stop ${runningContainers}"
          script {
            res = sh(
              script: 'ssh jenkins@$hostname docker run --restart always -d -v "/home/jenkins/dao-discord-bot/tinydb:/var/tinydb" -l "ai.effect.project=dao-discord-bot" --env-file dao-discord-bot/SECRETS.list $registry/$imageName:latest',
              returnStdout: true
            )
          }
          echo "Done! $res"
        }
      }
    }
  }
}