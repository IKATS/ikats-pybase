#!/bin/bash

# Deploy script called by jenkins
# Do not modify manually

for node in %%NODES%%
do
   echo "-----------------------------------------------------------------------------------------------------"
   echo "Deploying IKATS on node: [${node}]"
   echo

   # Copy on all nodes from node 1
   if test "${node}" != "1"
   then
      scp -r /home/ikats/ikats_py_deploy/ ikats@%%CLUSTER_NODE_PREFIX%%${node}:/home/ikats/ > /dev/null
   fi

   # Gunicorn has to run on this node
   run_gunicorn=""
   if test "${node}" == "%%GUNICORN_NODE%%"
   then
      echo "Starting Gunicorn for [%%CLUSTER_NODE_PREFIX%%${node}]"
      run_gunicorn="--run-gunicorn"
   fi

   ssh ikats@%%CLUSTER_NODE_PREFIX%%${node} "cd /home/ikats/ikats_py_deploy; chmod +x deploy.sh; ./deploy.sh --spark-home /usr/hdp/current/spark-client/ --target %%CLUSTER_NODE_NAME%% --no-color $run_gunicorn"%%FAST_MODE%%
   if test $? != 0
   then
     echo "ERROR during deployment"
     exit 1;
   fi
done

# Delete myself (can't use $0 because deployment_sequence.sh is launched by an upstream
# temporary shell script provided by jenkins)
rm /home/ikats/deployment_sequence.sh
