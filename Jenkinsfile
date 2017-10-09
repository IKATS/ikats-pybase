properties([
  parameters([
    string(name: 'BRANCH_TO_USE', defaultValue: 'master', description: 'Branch to use for ikats' )
  ])
])

node{

  currentBuild.result = "SUCCESS"

  try {
    stage('clean') {
      sh('rm -rf SCM  || true')
    }

    stage('pull ikats core') {

      dir('SCM/ikats_py_deploy') {
        git url: "https://thor.si.c-s.fr/git/ikats_py_deploy", branch: BRANCH_TO_USE,  credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      }
      // dir('SCM/ikats_hmi') {
      //   git url: "https://thor.si.c-s.fr/git/ikats_hmi", credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      // }
      // dir('SCM/ikats_core') {
      //   git url: "https://thor.si.c-s.fr/git/ikats_core", credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      // }
      // dir('SCM/ikats_algos') {
      //   git url: "https://thor.si.c-s.fr/git/ikats_algos", credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      // }
      // dir('SCM/ikats_django') {
      //   git url: "https://thor.si.c-s.fr/git/ikats_django", credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      // }
      // dir('SCM/ikats-base') {
      //   git url: "https://thor.si.c-s.fr/git/ikats-base", credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      // }
      // dir('SCM/ikats_tools') {
      //   git url: "https://thor.si.c-s.fr/git/ikats_tools", credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      // }
    }

    stage('pull contributions') {
      dir('SCM/ikats_py_deploy') {
        sh( 'echo "Parsing contrib.sources"')
        sh( 'cat contrib.sources')
      }
    }

    stage('build') {
      sh('echo "Building"')
    }

  }

  catch (err) {

    currentBuild.result = "FAILURE"

    mail body: "project build error is here: ${env.BUILD_URL}" ,
    from: 'ikats_jenkins@c-s.fr',
    to: 'fabien.tortora@c-s.fr',
    subject: 'Ikats Deploy build failed'

    throw err
  }
}
