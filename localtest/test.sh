#!/bin/bash -e
#Test against elastic instance

#Build pods: log transfer to be tested, test version of it and elasticsearch to test against
docker build -t structured-log-transfer -f Dockerfile
docker build -t structured-log-transfer-test -f localtest/Dockerfile
docker build -t elasticsearch-for-structured-log-transfer-test -f localtest/Dockerfile-elastic

# Create private network for the pod and a single pod to run both the containers in.
# This is to be able to run the containers also in podman non-root and still be able to communicate
docker network exists structuredlogtestnet ||  docker network create structuredlogtestnet
testpod=`docker pod create -n structuredlogtest`

# The following line may be needed to be run single time for elastic container to work
echo if getting error, this may be needed: sudo sysctl -w vm.max_map_count=262144

#Start the elastic
elasticcontainer=`docker run --pod structuredlogtest --name elasticinstance -e "discovery.type=single-node"  --detach elasticsearch-for-structured-log-transfer-test`

# Not in use, this way the password can be set even when running the container in detached mode,
# using security off for now, so no need for passwords. This requires elastic to start first,
# so if using this, set a delay or verification on elastic startup also.
#pass=
#echo resetting pass
#echo -e Y\\n$pass\\n$pass|docker exec -ti $elasticcontainer /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i

# For logging the elastic output to a file
docker attach --no-stdin $elasticcontainer > elastic.log &
echo see elastic.log for elasticsearch output

#Run the test, will wait for the elastic to be available before testing
docker run --env-file localtest/testenvs.txt --pod structuredlogtest localhost/structured-log-transfer-test || echo Test failed

#Stop and clean up
docker stop $elasticcontainer
docker container rm $elasticcontainer
docker pod rm $testpod
docker network rm -f structuredlogtestnet
