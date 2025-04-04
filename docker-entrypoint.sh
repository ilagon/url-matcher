#!/bin/bash
set -e

# Set the Django settings module to production
export DJANGO_SETTINGS_MODULE=url_matcher_project.settings_production

# Wait for the database to be ready
echo "Waiting for database..."
sleep 5

# Create necessary directories if they don't exist
echo "Ensuring media and static directories exist..."
python manage.py shell -c "
import os
from django.conf import settings

# Create media directories
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'csv_uploads'), exist_ok=True)
os.makedirs(settings.URL_MATCHER_OUTPUT_DIR, exist_ok=True)

# Create static directory
os.makedirs(settings.STATIC_ROOT, exist_ok=True)
print(f'STATIC_ROOT is set to: {settings.STATIC_ROOT}')
"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 \
    --workers ${WORKERS:-3} \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    url_matcher_project.wsgi:application
