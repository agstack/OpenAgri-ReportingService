#!/bin/bash

# Exit script on error
set -e


# Check whether these values have been passed
if [ -z "${REPORTING_POSTGRES_USER}" ]; then
  echo "Postgres username is not set in env"
  exit
fi

if [ -z "${REPORTING_POSTGRES_PASSWORD}" ]; then
  echo "Postgres password is not set in env"
  exit
fi

if [ -z "${REPORTING_POSTGRES_HOST}" ]; then
  echo "Postgres hostname is not set in env"
  exit
fi

if [ -z "${REPORTING_POSTGRES_PORT}" ]; then
  echo "Postgres port is not set in env"
  exit
fi

if [ -z "${REPORTING_POSTGRES_DB}" ]; then
  echo "Postgres database name is not set in env"
  exit
fi
if [ -z "${REPORTING_GATEKEEPER_USERNAME}" ]; then
  echo "Gatekeeper username is not set in env"
  exit
fi
if [ -z "${REPORTING_GATEKEEPER_PASSWORD}" ]; then
  echo "Gatekeeper password  is not set in env"
  exit
fi
if [ -z "${REPORTING_BACKEND_CORS_ORIGINS}" ]; then
  echo "Cors is not set in env"
  exit
fi


# Before the migrations can take place, we need to build the connection string in the alembic.ini file
sed -i -e "s/PGU/${REPORTING_POSTGRES_USER}/g" -e "s/PGP/${REPORTING_POSTGRES_PASSWORD}/g" -e "s/PGH/${REPORTING_POSTGRES_HOST}/g" -e "s/PGO/${REPORTING_POSTGRES_PORT}/g" -e "s/PGD/${REPORTING_POSTGRES_DB}/g" ./alembic.ini


# Migrate sqlalchemy models to postgres via alembic
echo "Starting db migrations"

alembic upgrade head

echo "Finished db migrations"


# Start the FastAPI app with uvicorn
echo "Starting Uvicorn server"

exec uvicorn --host 0.0.0.0 --port "$1" --app-dir=app 'main:app'

echo "Started Uvicorn server"