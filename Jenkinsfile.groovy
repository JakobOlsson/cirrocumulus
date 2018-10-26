pipeline {
    agent any 
    parameters {
        string(defaultValue: 'master', description: '', name: 'GitCommit')
    }

 
    stages {
        stage('Stage 1') {
            steps {
                echo 'Hello world!';
                echo 'Now we will build';
            }
        }
        stage('Git describe') {
            steps {
                sh(returnStdout: true, script: "git tag --sort version:refname | tail -1").trim()
            }
        }
        stage('Codebuild') {
            steps {
                awsCodeBuild credentialsId: 'codebuild', 
                             credentialsType: 'jenkins',
                             projectName: 'jenkins-test', 
                             sourceControlType: 'project',
                             sourceVersion: params.GitCommit,
                             region: 'eu-central-1';
            }
            
        }

    }
}
