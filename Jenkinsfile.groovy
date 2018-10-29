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
                echo "Branhc ${BRANCH_NAME}"
                /* script {
                    def scmVars = checkout(scm)
                    echo "${scmVars}"
                } */
            }
        }
        stage('Codebuild') {
            /*when {
                // only build master
                branch "master"
            }*/
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
