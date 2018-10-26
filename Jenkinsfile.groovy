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
                sh 'git describe --all'
                final scmVars = checkout(scm)
                print scmVars
                
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
