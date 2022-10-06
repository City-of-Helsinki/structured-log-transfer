#!/bin/bash -e
docker build -t structured-log-transfer -f Dockerfile
#docker run localhost/structured-log-transfer:latest runjob quarter_hourly
docker build -t structured-log-transfer-test -f localtest/Dockerfile

docker pull elasticsearch:8.4.3
#sudo sysctl -w vm.max_map_count=262144
docker network exists structuredlogtestnet
if [ "$?" -ne "0" ]
then
 docker network create structuredlogtestnet
fi
elasticcontainer=`docker run --network structuredlogtestnet --name elasticinstance --detach elasticsearch:8.4.3`

docker run --env-file localtest/testenvs.txt --network structuredlogtestnet localhost/structured-log-transfer-test

docker stop $elasticcontainer
docker container rm $elasticcontainer
#docker network rm -f structuredlogtestnet
