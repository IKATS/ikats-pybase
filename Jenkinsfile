properties([
  parameters([
    choice(name: 'CLUSTER', choices: "INT-B\nINT\nPREPROD", description: 'Target cluster'),
    string(name: 'BRANCH_TO_USE', defaultValue: 'master', description: 'Branch to use for ikats' ),
    string(name: 'DEPLOY_BRANCH_TO_USE', defaultValue: 'master', description: 'Branch to use for deploy scripts' ),
  ])
])

// Credentials identifier for Git connection
def credentialsIdHash = 'dccb5beb-b71f-4646-bf5d-837b243c0f87'

node{
  echo "\u27A1 Deploying "+params.BRANCH_TO_USE+" on "+params.CLUSTER

  currentBuild.result = "SUCCESS"

  try {

    stage('clean') {
      echo "\u27A1 Cleaning"
      sh('rm -rf SCM || true')
      sh('rm -rf contrib || true')
    }

    stage('pull ikats core') {
      echo "\u27A1 Pulling Ikats core code"

      dir('SCM/ikats_py_deploy') {
        git url: "https://thor.si.c-s.fr/git/ikats_py_deploy", branch: params.DEPLOY_BRANCH_TO_USE, credentialsId: credentialsIdHash
      }

      def repos = ['ikats_core', 'ikats_algos', 'ikats_django']
      def builders = [:]
      for (x in repos) {
          def repo = x // Need to bind the label variable before the closure - can't do 'for (repo in repos)'
          builders[repo] = {
            dir("SCM/${repo}") {
              try {
                git url: "https://thor.si.c-s.fr/git/${repo}", branch: params.BRANCH_TO_USE, credentialsId: credentialsIdHash
              }
              catch (err) {
                // Fallback to master branch if specified branch is not found
                echo "Branch ["+params.BRANCH_TO_USE+"] not found, falling back to [master]"
                git url: "https://thor.si.c-s.fr/git/${repo}", credentialsId: credentialsIdHash
              }
            }
          }
      }
      parallel builders
    }

    stage('pull contributions') {
      echo "\u27A1 Pulling contributions"
        if (fileExists("SCM/ikats_py_deploy/contrib.sources")) {
          // Cleanup file from comments to keep only useful information
          sh('sed -i "/^#/d; /^[ \t]*$/d; s/[ \t]+/ /g" SCM/ikats_py_deploy/contrib.sources')
          String[] sources = readFile("SCM/ikats_py_deploy/contrib.sources").split("\\r?\\n")
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
      sh('mkdir -p SCM/ikats_py_deploy/_sources')
      sh('cp -rf SCM/ikats_core SCM/ikats_py_deploy/_sources/ikats_core')
      sh('cp -rf SCM/ikats_algos SCM/ikats_py_deploy/_sources/ikats_algos')
      sh('cp -rf SCM/ikats_django SCM/ikats_py_deploy/_sources/ikats_django')

      // Cleaning old contributions
      sh('rm -rf SCM/ikats_py_deploy/_sources/ikats_algos/src/ikats/algo/contrib/ && mkdir SCM/ikats_py_deploy/_sources/ikats_algos/src/ikats/algo/contrib')

      // Adding new contributions
      sh('find contrib -maxdepth 3 -mindepth 3 -type d | egrep -v "tmp|.git" | grep algo | xargs -i cp -rf {} SCM/ikats_py_deploy/_sources/ikats_algos/src/ikats/algo/contrib/')
    }

    stage('catalog update') {
      echo "\u27A1 Updating Catalog"
        //TODO
    }

    stage('deploy') {
      echo "\u27A1 Deploying to " + params.CLUSTER

      if (params.CLUSTER == "PREPROD" && params.BRANCH_TO_USE != "master"){
        echo "WARNING ! Deploying non-master branch to PREPROD !!"
      }

      def cluster_node_prefix = 'ikats'+params.CLUSTER.toLowerCase()
      dir('SCM'){

        // Configuring Deployment
        sh ("sed -i 's/%%NODES%%/1 2 3 4 5/g; s/%%GUNICORN_NODE%%/3/g; s/%%CLUSTER_NODE_PREFIX%%/${cluster_node_prefix}/g; s/%%CLUSTER_NODE_NAME%%/"+params.CLUSTER.toLowerCase()+"/g' ikats_py_deploy/deployment_sequence.sh")

        // Deploying to master node
        sh("""ssh ikats@${cluster_node_prefix}1 rm -rf /home/ikats/ikats_py_deploy /home/ikats/deployment_sequence.sh &&
        scp -r ikats_py_deploy/ ikats@${cluster_node_prefix}1:/home/ikats/ &&
        ssh ikats@${cluster_node_prefix}1 mv /home/ikats/ikats_py_deploy/deployment_sequence.sh /home/ikats/deployment_sequence.sh
        ssh ikats@${cluster_node_prefix}1 bash /home/ikats/deployment_sequence.sh""")
      }
    }

    stage('tag') {
      echo "\u27A1 Tagging Deployed version"

      def repos = ['ikats_core', 'ikats_algos', 'ikats_django']
      def builders = [:]
      for (x in repos) {
        def repo = x // Need to bind the label variable before the closure - can't do 'for (repo in repos)'
        builders[repo] = {
          dir("SCM/${repo}") {
            withCredentials([usernamePassword(credentialsId: credentialsIdHash, passwordVariable: 'GIT_PASSWORD', usernameVariable: 'GIT_USERNAME')]) {
              // Delete local tag
              sh ("git tag -d DEPLOY_${CLUSTER} || true")
              // Apply new tag
              sh ("git tag DEPLOY_${CLUSTER} -m 'Deployed by jenkins build id ${BUILD_DISPLAY_NAME}'")
              // Delete remote tag
              sh ("git push https://${env.GIT_USERNAME}:${env.GIT_PASSWORD}@thor.si.c-s.fr/git/${repo} :refs/tags/DEPLOY_${CLUSTER}")
              // Push new local tag to remote
              sh ("git push https://${env.GIT_USERNAME}:${env.GIT_PASSWORD}@thor.si.c-s.fr/git/${repo} --tags")
            }
          }
        }
      }
      parallel builders
    }

  }

  catch (err) {
    echo "\u2717 Error during build"

    currentBuild.result = "FAILURE"

    emailext(
      subject: 'Ikats Python Build Failed',
      body: '''Project build error is here: ${env.BUILD_URL}''',
      recipientProviders: [[$class: 'CulpritsRecipientProvider']])

    throw err
  }
}

def pull_contribs(sources) {
  echo "\u27A1 Pulling " + sources.length + " contributions"

  def builders = [:]
  for (i = 0; i < sources.length; i++){
    String source = sources[i]
    String contrib_url = source.split(" ")[0]
    String contrib_tag = source.split(" ")[1]
    String contrib_dest_path = i.toString().padLeft(4,'0') + "__" + contrib_url.split('/').last() + "__" + contrib_tag

    builders[contrib_dest_path] = {
      echo "\u2600 Pulling [${contrib_url}] using tag [${contrib_tag}] to [${contrib_dest_path}]"

      checkout([$class: 'GitSCM',
        branches: [[name: "refs/tags/${contrib_tag}"]],
        polling: false,
        changelog: false,
        doGenerateSubmoduleConfigurations: false,
        extensions: [
          [$class: 'RelativeTargetDirectory', relativeTargetDir: contrib_dest_path],
          [$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'algo'], [path: 'viz']]],
          [$class: 'CloneOption', honorRefspec: true, depth: 1, noTags: false, reference: '', shallow: true, timeout: 10]
        ],
        submoduleCfg: [],
        userRemoteConfigs: [[credentialsId: 'dccb5beb-b71f-4646-bf5d-837b243c0f87', url: contrib_url]]])
      sh ("echo ${contrib_dest_path} > ${contrib_dest_path}/algo/VERSION")
    }
  }
  parallel builders
}
