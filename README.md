## Platta structured log transfer utility

An application for transferring logs from SQL database table to
Elasticsearch index. This application takes contents of a single table,
maps the rows to JSON and transfer this to an Elasticsearch instance.


## Running tests

Prerequisites:
-podman (docker may work also, tested with podman)
-bash shell (rewrite of the .sh scripts should be relatively easy if bash shell is not available)
-network connection for downloading the pods

Running the tests:
localtest/test.sh

Verifying the results:
See the line containing summary like: "9 passed in 1.05s", if all passed, the tests are ok.
You can see the elastic.log for elastic log output if necessary.
