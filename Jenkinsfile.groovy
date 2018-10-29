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
                script {
                  test = BRANCH_NAME.split('/')
                }
                echo "TEST: ${test}"
                /* script {
                    def scmVars = checkout(scm)
                    echo "${scmVars}"
                } */
                echo "Git Commit: ${GIT_COMMIT}"
                script {
                    if (params.GitCommit == "master") {
                        println "if statement test"
                        params.GitCommit = env.GIT_COMMIT
                    }
                }

                echo "Git Commit Params: ${params.GitCommit}"
                echo "Git Branch: ${GIT_BRANCH}"
            }
        }
        stage('Codebuild') {
            when {
                // only build master
                branch "master"
            }
            steps {
                awsCodeBuild credentialsId: 'codebuild', 
                             credentialsType: 'jenkins',
                             projectName: 'jenkins-test', 
                             sourceControlType: 'project',
                             sourceVersion: params.GitCommit,
                             region: 'eu-central-1';
            }
            
        }
        stage("Deploy feature") {
          when {
              expression { test[0].toLowerCase() == "feature" }
          }
          steps {
              script {
                  name = test[1].toLowerCase()
              }
              echo "Deploy feature branch: ${name}"
          }

        }

    }
}
