#!/bin/bash

if [[ "$ELASTICSEARCH_HOST" == *":"* ]]; then
    connection_string="$ELASTICSEARCH_SCHEME"://"$ELASTICSEARCH_HOST"/
else
    connection_string="$ELASTICSEARCH_SCHEME"://"$ELASTICSEARCH_HOST":"$ELASTICSEARCH_PORT"/
fi

# Wait until the elastic no longer says connection refused
echo Waiting for the elastic to start...
curl -s --retry-all-errors --retry-delay 1 --retry 240 --insecure "$connection_string"

#Do the testing
echo Running the tests..
pytest
echo Tests done, see the output above. See also elastic.log if you need to debug the elasticsearch logs.
