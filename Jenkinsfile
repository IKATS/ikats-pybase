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
        /* This builds the actual image; synonymous to
         * docker build on the command line */
        ikats_pybase = docker.build("ikats-pybase")
    }

    stage('Push image') {
        branchName = "${env.BRANCH_NAME}".substring("${env.BRANCH_NAME}".lastIndexOf("/") + 1)
        docker.withRegistry("${env.REGISTRY_ADDRESS}", 'DOCKER_REGISTRY') {
          ikats_pybase.push(branchName + "_${GIT_COMMIT}")
          ikats_pybase.push(branchName + "_latest")
          if ("${env.BRANCH_NAME}" == "master") {
            ikats_pybase.push("latest")
          }
        }
    }
}
