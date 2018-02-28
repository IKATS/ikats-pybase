#!/bin/bash

# Stop any running container if error occurs
trap "docker-compose down 2>/dev/null" INT KILL QUIT

# This script will prepare an empty environment, will start ikats and then run the test campaign
# After the campaign is completed, the script will get the result files to feed Jenkins metrics

# Prepare docker_bindings
echo "Getting fresh docker bindings"
# Get new data
export pathToDockerBindings=$(pwd)
pathToDockerBindingsRepo=/IKATSDATA/docker_bindings/
dockerBindingsName="docker_bindings_EDF_portfolio"
cp ${pathToDockerBindingsRepo}/${dockerBindingsName}.tar.gz ${pathToDockerBindings} &
# Clean previous one if exists
sudo rm -rf ${pathToDockerBindings}/docker_bindings 2 > /dev/null &
# Previous actions were performed in parallel, wait until all previous actions are completed
wait
# Unzip new one
sudo tar xzf ${dockerBindingsName}.tar.gz && rm ${dockerBindingsName}.tar.gz
sudo chown -R ${USER}:${USER} docker_bindings
# Apply patches to configure docker bindings (access allowed from any IP)
echo "listen_addresses = '*'" >> ${pathToDockerBindings}/docker_bindings/postgresql/ikats/postgresql.conf
sed -i "s@host    all             all             127.0.0.1/32           trust@host    all             all             127.0.0.1/0           trust@"  ${pathToDockerBindings}/docker_bindings/postgresql/ikats/pg_hba.conf
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
docker exec -it --user root ${containerName} bash ${IKATS_PATH}/testPrepare.sh
sleep 15
docker exec -it --user ikats ${containerName} bash ${IKATS_PATH}/testRunner.sh

# Get the results from docker container to host
docker cp ${containerName}:${IKATS_PATH}/ikats/processing/reports/junit.xml ./junit.xml

# Stop ikats
docker-compose down
