pipeline {
    agent any 
    stages {
        stage('Stage 1') {
            steps {
                echo 'Hello world!';
                echo 'Now we will build';
            }
        }
        stage('Codebuild') {
            steps {
                awsCodeBuild credentialsId: 'codebuild', 
                             credentialsType: 'jenkins',
                             projectName: 'jenkins-test', 
                             sourceControlType: 'project',
                             region: 'eu-central-1';
            }
            
        }

    }
}
