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

## Configuring

Env variables
name                      | type         |         default              | description
------------------------- | ------------ | -----------------            |-------------------------------------------------
DEBUG                     | bool         | False                        | If set to true will print more log
DATABASE_URL              | str          |"postgres:///structuredlogs"  | Set up for database connection for reading log entries from, see 
ELASTICSEARCH_APP_AUDIT_LOG_INDEX | str  | "app_audit_log"              | Index to write to
ELASTICSEARCH_HOST        | str          | ""                           | Elastic host name to write to
ELASTICSEARCH_PORT        | int          | 0                            | Elastic port to write to
ELASTICSEARCH_USERNAME    | str          | ""                           | User name for auth
ELASTICSEARCH_PASSWORD    | str          | ""                           | password for auth
CLEAR_AUDIT_LOG_ENTRIES   | bool         | False                        | set to True to clear audit log entries each month (Remember to also call the monthly job, monthly!)
ENABLE_SEND_AUDIT_LOG     | bool         | True                         | set to False to not send anything to elastic
DB_PREFIX                 | str          | ""                           | 
AUDIT_LOG_ORIGIN          | str          | ""                           | Origin to write to elastic with the audit log entry
AUDIT_TABLE_NAME          | str          | "audit_logs"                 | table name to read the logs from
ELASTICSEARCH_SCHEME      | str          | "https"                      | Scheme for connecting to elastic
DATE_TIME_PARENT_FIELD    | str          | "audit_event"                | Field name for parent object for fetching the elastic timestamp from json data. If unset, will search from root
DATE_TIME_FIELD           | str          | "date_time"                  | Field name for fetching the elastic timestamp from json data
DB_USE_SSL                | bool         | False                        | Attempt to append ssl settings to the database config if set to True
SSL_CA                    | str          | ""                           | Database SSL-CA cert path 
SSL_KEY                   | str          | ""                           | Database ssl-key client key path
SSL_CERT                  | str          | ""                           | Database ssl-cert path
SSL_CIPHER                | str          | ""                           | Database ssl-cipher

See https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url for possibilitied on setting the database url.