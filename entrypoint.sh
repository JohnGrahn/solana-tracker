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

# Start the application
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:${PORT:-5000} "${APP_MODULE:-run:app}"
