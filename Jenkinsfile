properties([
  parameters([
    string(name: 'BRANCH_TO_USE', defaultValue: 'master', description: 'Branch to use for ikats' ),
    string(name: 'DEPLOY_BRANCH_TO_USE', defaultValue: '161229', description: 'Branch to use for deploy scripts' ),
  ])
])

node{

  currentBuild.result = "SUCCESS"

  try {
    stage('clean') {
      echo "\u27A1 Cleaning"
      sh('rm -rf SCM contrib  || true')
    }

    stage('pull ikats core') {
      echo "\u27A1 Pulling Ikats core code"


      dir('SCM/ikats_py_deploy') {
        git url: "https://thor.si.c-s.fr/git/ikats_py_deploy", branch: params.DEPLOY_BRANCH_TO_USE, credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
      }

      def repos = ['ikats_core', 'ikats_algos', 'ikats_django']
      def builders = [:]

      for (x in repos) {
          def repo = x // Need to bind the label variable before the closure - can't do 'for (repo in repos)'
          builders[repo] = {
            dir("SCM/${repo}") {
              git url: "https://thor.si.c-s.fr/git/${repo}", branch: params.BRANCH_TO_USE, credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87'
            }
          }
      }
      parallel builders
    }

    stage('pull contributions') {
      echo "\u27A1 Pulling contributions"
        if (fileExists("SCM/ikats_py_deploy/contrib.sources")) {
          sh('sed -i "/^#/d; /^[ \t]*$/d; s/[ \t]+/ /g" SCM/ikats_py_deploy/contrib.sources')
          sh('echo $(cat SCM/ikats_py_deploy/contrib.sources | wc -l)" contribution(s) to load"')
          def sources = readFile("SCM/ikats_py_deploy/contrib.sources").split("\n")
          dir('contrib'){
            pull_contribs(sources)
          }
        }
        else{
          echo "\u27A1 No contribution to load \u2713"
        }
    }

    stage('build') {
      echo "\u27A1 Building"
      // Preparing sources
      sh('mkdir -p SCM/ikats_core SCM/ikats_py_deploy/_sources')
      sh('cp -rf SCM/ikats_core SCM/ikats_py_deploy/_sources/ikats_core')
      sh('cp -rf SCM/ikats_algos SCM/ikats_py_deploy/_sources/ikats_algos')
      sh('cp -rf SCM/ikats_django SCM/ikats_py_deploy/_sources/ikats_django')

      // Cleaning old contributions
      sh('rm -rf SCM/ikats_py_deploy/_sources/ikats_algos/src/ikats/algo/contrib/*')

      // Adding new contributions
      sh('cp -rf contrib/*/algo/* SCM/ikats_py_deploy/_sources/ikats_algos/src/ikats/algo/contrib/')
    }

  }

  catch (err) {
    echo "\u2717 Error during build"

    currentBuild.result = "FAILURE"

    // mail body: "project build error is here: ${env.BUILD_URL}" ,
    // from: 'ikats_jenkins@c-s.fr',
    // to: 'fabien.tortora@c-s.fr',
    // subject: 'Ikats Deploy build failed'

    throw err
  }
}

@NonCPS
def pull_contribs(sources){
  for (source in sources){
    String contrib_url = source.split(" ")[0]
    String contrib_tag = source.split(" ")[1]
    String contrib_dest_path = contrib_url.split('/').last()
    echo "\u2600 Pulling [${contrib_url}] using tag [${contrib_tag}] to [${contrib_dest_path}]"
    checkout([$class: 'GitSCM',
      branches: [[name: "refs/tags/${contrib_tag}"]],
      doGenerateSubmoduleConfigurations: false,
      extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: contrib_dest_path]],
      submoduleCfg: [],
      userRemoteConfigs: [[credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87', url: contrib_url]]])
  }
}
