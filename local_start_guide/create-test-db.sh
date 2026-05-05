#!/bin/sh
set -e

if [ -f ".env" ]; then
  set -a
  . ./.env
  set +a
fi

if [ -z "$DB_TEST_USER" ] || [ -z "$DB_TEST_PASS" ] || [ -z "$DB_TEST_NAME" ] || [ -z "$DB_MIGRATION_USER" ] || [ -z "$DB_NAME" ]; then
  echo "Required DB_* env variables are missing in .env"
  exit 1
fi

CONTAINER_NAME="${POSTGRES_CONTAINER_NAME:-cryptoweb-postgres}"

docker exec -i "$CONTAINER_NAME" psql -v ON_ERROR_STOP=1 -U "$DB_MIGRATION_USER" -d "$DB_NAME" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_TEST_USER}') THEN
    EXECUTE format('CREATE ROLE %I WITH LOGIN PASSWORD %L', '${DB_TEST_USER}', '${DB_TEST_PASS}');
  END IF;
END
\$\$;
SQL

DB_EXISTS=$(docker exec -i "$CONTAINER_NAME" psql -U "$DB_MIGRATION_USER" -d "$DB_NAME" -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_TEST_NAME}'")
if [ "$DB_EXISTS" != "1" ]; then
  docker exec -i "$CONTAINER_NAME" psql -v ON_ERROR_STOP=1 -U "$DB_MIGRATION_USER" -d "$DB_NAME" -c "CREATE DATABASE \"${DB_TEST_NAME}\" OWNER \"${DB_TEST_USER}\""
fi

docker exec -i "$CONTAINER_NAME" psql -v ON_ERROR_STOP=1 -U "$DB_MIGRATION_USER" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON DATABASE \"${DB_TEST_NAME}\" TO \"${DB_TEST_USER}\""

echo "Test role/database ensured: ${DB_TEST_USER} / ${DB_TEST_NAME}"
