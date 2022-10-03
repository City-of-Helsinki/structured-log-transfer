#!/bin/bash -e
docker build -t structured-log-transfer -f Dockerfile
#docker run localhost/structured-log-transfer:latest runjob quarter_hourly
docker build -t structured-log-transfer-test -f localtest/Dockerfile
docker run --env-file localtest/testenvs.txt localhost/structured-log-transfer-test
