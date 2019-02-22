pipeline {
    options { 
        buildDiscarder(logRotator(numToKeepStr: '4', artifactNumToKeepStr: '5'))
        disableConcurrentBuilds() 
    }
    agent any
    parameters {
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run the test campaign')
    }

    stages {
        stage('Fetch SCM') {
            steps {
                checkout scm
            }
        }
        stage('Build and push image') {
            agent { node { label 'docker' } }
            steps {
                script {
                    dockerBuild 'hub.ops.ikats.org/pybase'
                }
            }
        }
        stage('Test') {
            agent { node { label 'docker' } }
            steps {
                script {
                    if (params.RUN_TESTS == true) {
                        sh 'cd tests; ./startJob.sh'
                    }
                }
            }
        }
    }
}
