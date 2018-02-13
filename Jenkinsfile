properties([parameters(
  [
    credentials(
      name: 'REGISTRY_CREDENTIALS',
      credentialType: 'com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl',
      defaultValue: 'DOCKER_REGISTRY',
      description: '',
      required: true),
    string(
      name: 'REGISTRY_URI',
      defaultValue: 'https://hub.ops.ikats.org',
      description: 'Registry this job will push images to'
    )
  ]
)])

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
        docker.withRegistry("${env.REGISTRY_URI}", "${env.REGISTRY_CREDENTIALS}") {
          ikats_pybase.push("${env.BRANCH_NAME}_${env.CHANGE_AUTHOR}_${env.BUILD_ID}")
          ikats_pybase.push("${env.BRANCH_NAME}_latest")
          if ("${env.BRANCH_NAME}" == "master") {
            ikats_pybase.push("latest")
          }
        }
    }
}
