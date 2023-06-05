## Platta structured log transfer utility

An application for transferring audit logs from SQL database to ElasticSearch index.

## Database model

By default, logs are fetched from a database model consisting of these three fields:

- `is_sent`: `True` if the audit log has already been sent to ElasticSearch (app should write the log with this set initially to `False`).
- `message`: JSON data to be sent to ElasticSearch.
- `created_at`: Date and time when the message was created.

An `AUDIT_TABLE_NAME` environment variable should also be set to the name of the table
where the logs are stored.

## Django Auditlog integration

Instead of the above database model, logs can be sent from LogEntries created by
[django-auditlog](https://github.com/jazzband/django-auditlog) if the
`AUDIT_LOGGER_TYPE` is set to `DJANGO_AUDITLOG` in the environment. This will create
a message in the following schema from the LogEntry:

```yaml
'@timestamp':
  type: date  # auditlog.models.LogEntry.timestamp
audit_event:
  properties:
    actor:
      type: text  # auditlog.models.LogEntry.actor.get_full_name(), or .email, or "unknown"
    date_time:
      type: date  # auditlog.models.LogEntry.timestamp
    operation:
      type: keyword  # auditlog.models.LogEntry.action (create / update / delete / access)
    origin:
      type: constant_keyword  # set by AUDIT_LOG_ORIGIN setting
    target:
      type: text  # auditlog.models.LogEntry.object_repr
    environment:
      type: constant_keyword  # set by AUDIT_LOG_ENVIRONMENT setting
    message:
      type: text  # auditlog.models.LogEntry.changes
  type: object
```

The `additional_data` field in the LogEntry should contain a `is_sent` boolean value, which
is used to keep track of whether the log has been sent to ElasticSearch or not. 
This should be set to `False` initially, but old log entries without this additional data
will be treated as not sent.

> Note: If using a custom user model, `USER_TABLE_NAME` setting should be set to the table name for the new model!

## Extending to other models

The application provides a facade that can be extended to support other database models.
The facade has the following interface:

- `log`: Database model where the logs are stored.
- `message`: A property that creates the message to be sent to ElasticSearch.
- `mark_as_sent`: A method that marks the log as sent.

An appropriate setting should be provided to `structuredlogtransfer/settings.py` which can be used
to select a new implementation of the facade in `log_transfer.services.get_unsent_entries`.

## Running tests

Tests can be run using a shell script or with docker compose

### Shell script

Prerequisites:
- podman (docker may work also, tested with podman)
- bash shell (rewrite of the .sh scripts should be relatively easy if bash shell is not available)
- network connection for downloading the pods

Running the tests:

```bash
./localtest/test.sh
```

### Docker compose

Use `docker compose --profile test-1 up --detach --build` to build and run the testing containers
(configuration 1, change `--profile test-1` to `--profile test-2` to run second configuration).
You can also use `make up` (or `make up2`) if you have make installed.

When tests have completed, run `docker compose --profile test-1 --profile test-2 down --volumes --remove-orphans`
(or `make down`) to remove the containers.

## Verifying the results

Check either the shell script output or the `structured-log-transfer-test` container logs and look for
a line containing summary like: "9 passed in 1.05s", if all passed, the tests are ok.

You can see the `elastic.log` file (or `elasticsearch-for-structured-log-transfer-test` container logs 
if using docker compose) for elastic log output if necessary.

## Configuring

| ENV variables name                | Type | Default                      | Description                                                                                                                               |
|-----------------------------------|------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| AUDIT_LOG_ENVIRONMENT             | str  | ""                           | Audit log environment for the log created from django_auditlog                                                                            |
| AUDIT_LOG_ORIGIN                  | str  | ""                           | Origin to write to elastic with the audit log entry                                                                                       |
| AUDIT_LOGGER_TYPE                 | str  | "SINGLE_COLUMN_JSON"         | Which kind of audit logger to use. Options are defined in `structuredlogtransfer.settings.AuditLoggerType`                                |
| AUDIT_TABLE_NAME                  | str  | "audit_logs"                 | Table name to read the logs from                                                                                                          |
| CLEAR_AUDIT_LOG_ENTRIES           | bool | True                         | Clear audit log entries each month when monthly job is run. Set to False to disable this functionality even when running the monthly job. |
| DATABASE_URL                      | str  | "postgres:///structuredlogs" | Set up for database connection for reading log entries from, see                                                                          |
| DATE_TIME_FIELD                   | str  | "date_time"                  | Field name for fetching the elastic timestamp from json data                                                                              |
| DATE_TIME_PARENT_FIELD            | str  | "audit_event"                | Field name for parent object for fetching the elastic timestamp from json data. If unset, will search from root                           |
| DB_USE_SSL                        | bool | False                        | Attempt to append ssl settings to the database config if set to True                                                                      |
| DEBUG                             | bool | False                        | If set to true will print more log                                                                                                        |
| ELASTICSEARCH_APP_AUDIT_LOG_INDEX | str  | "app_audit_log"              | Index to write to                                                                                                                         |
| ELASTICSEARCH_HOST                | str  | ""                           | Elastic host name to write to. You can also include port separated by colon.                                                              |
| ELASTICSEARCH_PASSWORD            | str  | ""                           | Password for auth                                                                                                                         |
| ELASTICSEARCH_PORT                | int  | 0                            | Elastic port to write to. This can be also given as part of the host.                                                                     |
| ELASTICSEARCH_SCHEME              | str  | "https"                      | Scheme for connecting to elastic                                                                                                          |
| ELASTICSEARCH_USERNAME            | str  | ""                           | User name for auth                                                                                                                        |
| ENABLE_SEND_AUDIT_LOG             | bool | True                         | Set to False to not send anything to elastic                                                                                              |
| SSL_CA                            | str  | ""                           | Database SSL-CA cert path                                                                                                                 |
| SSL_CERT                          | str  | ""                           | Database ssl-cert path                                                                                                                    |
| SSL_CIPHER                        | str  | ""                           | Database ssl-cipher                                                                                                                       |
| SSL_KEY                           | str  | ""                           | Database ssl-key client key path                                                                                                          |
| USER_TABLE_NAME                   | str  | "auth_user"                  | Table name for the user model.                                                                                                            |


See https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url for possibilities on setting the database url.

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
