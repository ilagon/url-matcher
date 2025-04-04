#!/bin/bash
set -e

# Set the Django settings module to production
export DJANGO_SETTINGS_MODULE=url_matcher_project.settings_production

# Wait for the database to be ready
echo "Waiting for database..."
sleep 5

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create necessary directories if they don't exist
echo "Ensuring media directories exist..."
python manage.py shell -c "
import os
from django.conf import settings
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'csv_uploads'), exist_ok=True)
os.makedirs(settings.URL_MATCHER_OUTPUT_DIR, exist_ok=True)
"

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 \
    --workers ${WORKERS:-3} \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    url_matcher_project.wsgi:application
