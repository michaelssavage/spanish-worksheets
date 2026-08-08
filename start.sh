#!/bin/bash
set -e

echo "Waiting for postgres..."
until .venv/bin/python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL started"
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py migrate

exec .venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
