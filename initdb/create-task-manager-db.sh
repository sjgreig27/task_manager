#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER "task_manager" WITH PASSWORD '$POSTGRES_DB_USER_PASSWORD' SUPERUSER;
  CREATE DATABASE "task_manager";
  GRANT ALL PRIVILEGES ON DATABASE "task_manager" TO "task_manager";
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE DATABASE "task_manager_test";
  GRANT ALL PRIVILEGES ON DATABASE "task_manager_test" TO "task_manager";
EOSQL