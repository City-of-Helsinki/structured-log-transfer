#!/bin/bash

# Wait until the elastic no longer says connection refused
echo Waiting for the elastic to start...
curl -s --retry-connrefused --retry-delay 1 --retry 240 --insecure http://localhost:9200/

#Do the testing
echo Running the tests..
pytest
echo Tests done, see the output above. See also elastic.log if you need to debug the elasticsearch logs.
