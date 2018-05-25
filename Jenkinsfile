properties([parameters([booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run the test campaign')])])

node('docker') {

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */
        scmenv = checkout scm
        GIT_COMMIT = scmenv.GIT_COMMIT.take(7)
    }

    stage('Documentation') {
        /* This builds the actual image; synonymous to
         * docker build on the command line */
        // sh "cd doc; ./gen_doc.sh"
        // TODO Define where to store the documentation
    }

    stage('Build image') {

      // Replacing docker registry to private one. See [#172302]
      sh "sed -i 's/FROM ikats/FROM hub.ops.ikats.org/' Dockerfile"

      /* This builds the actual image; synonymous to
       * docker build on the command line */
      ikats_pybase = docker.build("pybase", "--pull .")
    }

    stage('Push image') {
        branchName = "${env.BRANCH_NAME}".substring("${env.BRANCH_NAME}".lastIndexOf("/") + 1)
        docker.withRegistry("${env.REGISTRY_ADDRESS}", 'DOCKER_REGISTRY') {
          ikats_pybase.push(branchName + "_${GIT_COMMIT}")
          ikats_pybase.push(branchName + "_latest")
          if ("${env.BRANCH_NAME}" == "master") {
            ikats_pybase.push("master")
          }
        }
    }

    stage('Test') {
      if (params.RUN_TESTS == true) {
        sh 'cd tests; ./startJob.sh'
      }
    }
    //
    // stage('QA') {
    //   junit testDataPublishers: [[$class: 'AttachmentPublisher']], testResults: "tests/junit.xml"
    //   sh '''
    //     sed -i 's/filename="\\(.*\\)"/filename="code\\/procedures\\/\\1"/g' tests/junit.xml
    //     sed -i 's/filename="\\(.*\\)"/filename="code\\/procedures\\/\\1"/g' tests/junit.xml
    //   '''
    //   // requires SonarQube Scanner 2.8+
    //   def scannerHome = tool 'SonarQube Scanner 3';
    //   env.JAVA_HOME="/home/jenkins/jdk"
    //   sh 'echo j=$JAVA_HOME'
    //   withSonarQubeEnv('SonarQube@moduleci-vm15') {
    //     sh "${scannerHome}/bin/sonar-scanner -X"
    //   }
    // }

}
