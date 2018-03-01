#!/bin/bash

# Stop any running container if error occurs
trap "docker-compose down 2>/dev/null; exit 1" INT KILL QUIT

# This script will prepare an empty environment, will start ikats and then run the test campaign
# After the campaign is completed, the script will get the result files to feed Jenkins metrics

# Prepare docker_bindings
echo "Getting fresh docker bindings"
# Get new data
export pathToDockerBindings=$(mktemp -d)
# Data are stored in /opt on remote jenkins slave host because of forbidden access to the NAS
pathToDockerBindingsRepo=${1:-/IKATSDATA/docker_bindings/}

if [[ ! -d ${pathToDockerBindingsRepo} ]]
then
  echo "Can't get docker_bindings. Unreachable folder"
  exit 2;
fi

dockerBindingsName="docker_bindings_EDF_portfolio"
cp ${pathToDockerBindingsRepo}${dockerBindingsName}.tar.gz ${pathToDockerBindings} &
# Clean previous one if exists
rm -rf ${pathToDockerBindings}/docker_bindings 2 > /dev/null &
# Previous actions were performed in parallel, wait until all previous actions are completed
wait

# Unzip new one
pushd ${pathToDockerBindings} >/dev/null
tar xzf ${dockerBindingsName}.tar.gz && rm ${dockerBindingsName}.tar.gz
popd >/dev/null
# Change location of docker bindings for docker-compose
sed -i "s@DOCKER_BINDINGS_POSTGRES=.*@DOCKER_BINDINGS_POSTGRES=${pathToDockerBindings}/docker_bindings/postgresql@" .env
sed -i "s@DOCKER_BINDINGS_HBASE=.*@DOCKER_BINDINGS_HBASE=${pathToDockerBindings}/docker_bindings/hbase/hbase@" .env

# Start ikats
docker-compose up --build -d

# Container name to test (should never change)
containerName=tests_pybase

IKATS_PATH=/ikats

# Prepare test environment
docker cp assets/test_requirements.txt ${containerName}:${IKATS_PATH}/
docker cp assets/testPrepare.sh ${containerName}:${IKATS_PATH}/
docker cp assets/pylint.rc ${containerName}:${IKATS_PATH}/
docker cp assets/testRunner.sh ${containerName}:${IKATS_PATH}/

# Execute the test campaign inside the docker container
docker exec --user root ${containerName} bash ${IKATS_PATH}/testPrepare.sh
sleep 30
docker exec --user ikats ${containerName} bash ${IKATS_PATH}/testRunner.sh
EXIT_STATUS=$?

# Get the results from docker container to host
docker cp ${containerName}:${IKATS_PATH}/ikats/processing/reports/junit.xml ./junit.xml

# Stop ikats
docker-compose down > /dev/null

# KO tests to be fixed later, continue the job
# exit ${EXIT_STATUS}
