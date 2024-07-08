#!/bin/sh

set -e

# Wait for the database to be ready
echo "Waiting for database..."
while ! pg_isready -h db -p 5432 > /dev/null 2>&1; do
  sleep 1
done
echo "Database is ready!"

# Initialize migrations if they don't exist
if [ ! -f "migrations/alembic.ini" ]; then
  echo "Initializing migrations..."
  flask db init
  flask db migrate -m "Initial migration"
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Check if we should start the Celery worker
if [ "${START_CELERY_WORKER}" = "true" ]; then
  echo "Starting Celery worker..."
  celery -A celery_worker.celery worker --loglevel=info &
fi

# Start the Flask application
echo "Starting the Flask application..."
exec gunicorn --bind 0.0.0.0:${PORT:-5000} "${APP_MODULE:-run:app}"
