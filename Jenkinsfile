node('docker') {

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */
        checkout scm
    }

    stage('Documentation') {
        /* This builds the actual image; synonymous to
         * docker build on the command line */
        // sh "cd doc; ./gen_doc.sh"
        // TODO Define where to store the documentation
    }

    stage('Build image') {
        /* This builds the actual image; synonymous to
         * docker build on the command line */
        ikats_pybase = docker.build("ikats-pybase")
    }

    stage('Push image') {
        docker.withRegistry("${env.REGISTRY_ADDRESS}", 'DOCKER_REGISTRY') {
          ikats_pybase.push("${env.BRANCH_NAME}_${env.BUILD_ID}")
          ikats_pybase.push("${env.BRANCH_NAME}_latest")
          if ("${env.BRANCH_NAME}" == "master") {
            ikats_pybase.push("latest")
          }
        }
    }
}
