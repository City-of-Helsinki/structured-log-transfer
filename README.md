## Platta structured log transfer utility

An application for transferring logs from SQL database table to
Elasticsearch index. This application takes contents of a single table,
maps the rows to JSON and transfer this to an Elasticsearch instance.



## Database model

The database model consists of three fields:
is_sent: true if the database row has already been sent to elastic (app should write the log with ths set initially to false)
message: message in read in models.JSONField format
created_at: time when the message was created

There are two methods to override if changing the is_sent or created_at fields.
markAsSent() is used for marking the message as sent in db. If using other field name or mechanism than is_sent -field, this needs to be changed.

getUnsentEntries() is used for getting the entries that have not yet been sent to elastic (and should be sent). Returns a list of model instances.

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
