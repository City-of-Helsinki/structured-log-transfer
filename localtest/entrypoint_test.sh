#!/bin/bash

# Does not work, curl does not like http 0.9 response
#until curl -vvv --insecure http://localhost:9300/
#do
#  echo Waiting for elastic pod to go alive...
#  curl --version
#  sleep 1
#done

# Sleeping fixed time until the loop has been fixed
sleep 60

pytest

