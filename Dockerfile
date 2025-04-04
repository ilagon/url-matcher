FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=url_matcher_project.settings_production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install gunicorn and other production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==21.2.0 whitenoise==6.5.0

# Create a non-root user to run the application
RUN useradd -m appuser

# Copy project
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/url_matcher_web/media/csv_uploads \
    && mkdir -p /app/url_matcher_web/media/url_matcher_output \
    && mkdir -p /app/url_matcher_web/static \
    && chown -R appuser:appuser /app

# Set the working directory to the Django project
WORKDIR /app/url_matcher_web

# Create a .env file with production settings (will be overridden by environment variables)
RUN echo "DEBUG=False" > .env \
    && echo "SECRET_KEY=placeholder_replace_this_in_production" >> .env \
    && echo "ALLOWED_HOSTS=localhost,127.0.0.1" >> .env

# Switch to non-root user for better security
USER appuser

# Expose port
EXPOSE 8000

# Create entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
