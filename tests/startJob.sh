#!/bin/bash

# Container name to test (should never change)
containerName=tests_pybase

# This script will prepare an empty environment, will start ikats and then run the test campaign
# After the campaign is completed, the script will get the result files to feed Jenkins metrics

# Prepare docker_bindings

# Start ikats
docker-compose up --build -d
sleep 15

# Prepare test environment
docker cp assets/test_requirements.txt ${containerName}:/ikats/
docker cp assets/testPrepare.sh ${containerName}:/ikats/
docker cp assets/testRunner.sh ${containerName}:/ikats/

# Execute the test campaign inside the docker container
docker exec -it --user root ${containerName} bash /ikats/testPrepare.sh
docker exec -it --user ikats ${containerName} bash /ikats/testRunner.sh

# Get the results from docker container to host
docker cp ${containerName}:/ikats/nosetests.xml ./nosetests.xml

# Stop ikats
docker-compose down
