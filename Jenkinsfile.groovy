pipeline {
    agent any 
    stages {
        stage('Stage 1') {
            steps {
                echo 'Hello world!' 
            }
        }
        stage('Codebuild') {
            awsCodeBuild credentialsId: 'codebuild', credentialsType: 'jenkins', sourceControlType: 'project'
        }

    }
}
