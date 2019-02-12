#!/bin/bash

# This script will prepare an empty environment, will start ikats and then run the test campaign
# After the campaign is completed, the script will get the result files to feed Jenkins metrics

# Stop any running container if error occurs
trap "echo 'Stopping...';docker-compose down >/dev/null 2>&1; exit 1" INT KILL QUIT PIPE

# Prepare docker_bindings
dockerBindingsName="docker_bindings_EDF_portfolio"
echo "Getting fresh docker bindings"
# Get new data
pathToDockerBindingsRepo=${1:-/mnt/IKATSNAS/docker_bindings/}

if [[ ! -d ${pathToDockerBindingsRepo} ]]
then
  echo "Can't get docker_bindings. Unreachable folder"
  exit 2;
fi
cp ${pathToDockerBindingsRepo}${dockerBindingsName}.tar.gz ./

# Preparing volumes
docker volume rm pybase_docker_bindings_postgresql pybase_docker_bindings_hbase > /dev/null 2>&1
docker volume create pybase_docker_bindings_postgresql > /dev/null 2>&1 &
docker volume create pybase_docker_bindings_hbase > /dev/null 2>&1 &
wait
tar xzf ${dockerBindingsName}.tar.gz && rm ${dockerBindingsName}.tar.gz
docker run --rm -v $(pwd)/docker_bindings/postgresql:/src -v pybase_docker_bindings_postgresql:/data busybox cp -r /src/* /data &
docker run --rm -v $(pwd)/docker_bindings/hbase:/src -v pybase_docker_bindings_hbase:/data busybox cp -r /src/* /data &
wait
rm -rf docker_bindings/

# Start ikats
docker-compose pull
docker-compose up --build -d

# Container name to test (should never change)
containerName=pybase

# Ikats path inside the container
IKATS_PATH=/ikats

# Prepare test environment
docker cp assets/test_requirements.txt ${containerName}:${IKATS_PATH}/ &
docker cp assets/testPrepare.sh ${containerName}:${IKATS_PATH}/ &
docker cp assets/pylint.rc ${containerName}:${IKATS_PATH}/ &
docker cp assets/testRunner.sh ${containerName}:${IKATS_PATH}/ &
wait
docker exec --user root ${containerName} bash ${IKATS_PATH}/testPrepare.sh

# Wait a bit to let containers to initiate communication with others
sleep 10
# Execute the test campaign inside the docker container
docker exec --user ikats ${containerName} bash ${IKATS_PATH}/testRunner.sh
EXIT_STATUS=$?

# Get the results from docker container to host
docker cp ${containerName}:${IKATS_PATH}/ikats/processing/reports/junit.xml ./junit.xml

# Stopping docker
docker-compose down > /dev/null

# Return 0 if all tests are OK, any other number indicates tests are KO
exit ${EXIT_STATUS}
