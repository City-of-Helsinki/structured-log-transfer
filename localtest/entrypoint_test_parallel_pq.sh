#!/bin/bash

if [[ "$ELASTICSEARCH_HOST" == *":"* ]]; then
    connection_string="$ELASTICSEARCH_SCHEME"://"$ELASTICSEARCH_HOST"/
else
    connection_string="$ELASTICSEARCH_SCHEME"://"$ELASTICSEARCH_HOST":"$ELASTICSEARCH_PORT"/
fi

LOG_TYPE=DJANGO_AUDITLOG # DJANGO_AUDITLOG | SINGLE_COLUMN_JSON

# Wait until the elastic no longer says connection refused
echo Waiting for the elastic to start...
curl -s --retry-all-errors --retry-delay 1 --retry 240 --insecure "$connection_string"

# Setup db
psql $DATABASE_URL -c 'CREATE DATABASE test_databasename;'

# Migrations using DJANGO_AUDITLOG so it also adds DJANGO_AUDITLOG database tables.
AUDIT_LOGGER_TYPE=DJANGO_AUDITLOG DATABASE_URL=postgres://user:password@structured-log-transfer-postgres/test_databasename python manage.py migrate

# echo Running the parallel tests..
# # --nomigrations - don't perform migrations, that's already done
# # -m "parallel" - runs tests marked with parallel marker
# # -n 2 - run 2 procceses
pytest --nomigrations --reuse-db -o "django_db_reset=false" -m "PARALLEL_$LOG_TYPE" -n 2 -vvv


echo Tests done, see the output above. See also elastic.log if you need to debug the elasticsearch logs.

# Teardown
psql $DATABASE_URL -c 'DROP DATABASE test_databasename;'