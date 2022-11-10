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
ELASTICSEARCH_HOST        | str          | ""                           | Elastic host name to write to. You can also include port separated by colon.
ELASTICSEARCH_PORT        | int          | 0                            | Elastic port to write to. This can be also given as part of the host.
ELASTICSEARCH_USERNAME    | str          | ""                           | User name for auth
ELASTICSEARCH_PASSWORD    | str          | ""                           | Password for auth
CLEAR_AUDIT_LOG_ENTRIES   | bool         | True                         | Clear audit log entries each month when  monthly job is run. Set to False to disable this functionality even when running the monthly job.
ENABLE_SEND_AUDIT_LOG     | bool         | True                         | Set to False to not send anything to elastic
DB_PREFIX                 | str          | ""                           | 
AUDIT_LOG_ORIGIN          | str          | ""                           | Origin to write to elastic with the audit log entry
AUDIT_TABLE_NAME          | str          | "audit_logs"                 | Table name to read the logs from
ELASTICSEARCH_SCHEME      | str          | "https"                      | Scheme for connecting to elastic
DATE_TIME_PARENT_FIELD    | str          | "audit_event"                | Field name for parent object for fetching the elastic timestamp from json data. If unset, will search from root
DATE_TIME_FIELD           | str          | "date_time"                  | Field name for fetching the elastic timestamp from json data
DB_USE_SSL                | bool         | False                        | Attempt to append ssl settings to the database config if set to True
SSL_CA                    | str          | ""                           | Database SSL-CA cert path 
SSL_KEY                   | str          | ""                           | Database ssl-key client key path
SSL_CERT                  | str          | ""                           | Database ssl-cert path
SSL_CIPHER                | str          | ""                           | Database ssl-cipher

See https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url for possibilitied on setting the database url.

## Configuration examples

### Elasticsearch
To connect to `https` port `443` on host `host`

- Set ELASTICSEARCH_HOST to `host`
- Set ELASTICSEARCH_PORT to `443`
- Set ELASTICSEARCH_SCHEME to `https`

### Elasticsearch alternate way
To connect to `https` port `443` on host `host`

- Set ELASTICSEARCH_HOST to `host:443`
- Set ELASTICSEARCH_PORT to `0` or leave it unset.
- Set ELASTICSEARCH_SCHEME to `https`

### MySQL
To read from `databasename.tablename` on mysql server `host.domain.root` port `1234` using `user`:
- Set DATABASE_URL to `mysql://user@host.domain.root:1234/databasename`
- Set DATABASE_PASSWORD env variable
- Set AUDIT_TABLE_NAME to `tablename`

### MySQL SSL
Configure the MySQL example above, then to use SSL using ca cert from `https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem`
- Set DB_USE_SSL env variable to True
- Set SSL_CA to `certs/BaltimoreCyberTrustRoot.crt.pem`
- Include ` ADD --chown=appuser:appuser https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem certs/` to Dockerfile and build, alternatively map file or path when running the container

### MySQL create minimal table and insert test data into it

Connect to database
```shell
mysql -h host.domain.root -D databasename -u user
```

Create database table
```sql
CREATE TABLE audit_logs (
    id int,
    is_sent BOOLEAN,
    message JSON,
    created_at TIMESTAMP
);
```

Insert test data row into table: 
```sql
INSERT INTO audit_logs(id, is_sent, message, created_at) 
VALUES (1, 0, '{"audit_event": {"date_time": "2022-10-13T12:34:56.000Z"}}', now());
```

### PostgreSQL
To read from `databasename.tablename` on postgresql server `host.domain.root` port `1234` using `user`:
- Set DATABASE_URL to `postgres://user:password@host.domain.root:1234/databasename?sslmode=require`
- Set AUDIT_TABLE_NAME to `tablename`


### PostgreSQL create minimal table and insert test data into it

Connect to database
```shell
psql postgres://user:password@databasehost.domain.root:1234/databasename?sslmode=require
```

Create database table
```sql
CREATE TABLE audit_logs (
    id int,
    is_sent BOOLEAN,
    message JSONB,
    created_at TIMESTAMP WITH TIME ZONE
);
```

Insert test data row into table: 
```sql
INSERT INTO audit_logs(id, is_sent, message, created_at) 
VALUES (1, false, '{"audit_event": {"date_time": "2022-10-13T12:34:56.000+0300"}}', now());
```
