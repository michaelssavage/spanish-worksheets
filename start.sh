#!/bin/bash
set -e

echo "Waiting for postgres..."
until poetry run python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL started"
poetry run python manage.py collectstatic --noinput
poetry run python manage.py migrate
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT