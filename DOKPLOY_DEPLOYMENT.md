# URL Matcher Deployment Guide for Dokploy

This guide provides instructions for deploying the URL Matcher application to a VPS using Dokploy.

## Prerequisites

- A VPS with Dokploy installed
- Docker and Docker Compose installed on your VPS
- Git repository access

## Deployment Steps

### 1. Prepare Your Environment Variables

Create a `.env` file from the sample:

```bash
cp sample.env .env
```

Edit the `.env` file to set secure values for:
- `SECRET_KEY`: Generate a secure random string
- `DB_PASSWORD`: Set a strong password
- `DOKPLOY_DOMAIN`: Your domain name (will be used in ALLOWED_HOSTS)

### 2. Configure Docker Compose for Dokploy

The `docker-compose.yml` file has been configured to work with Dokploy:
- The web service exposes port 8000
- Static files are served directly by WhiteNoise
- Environment variables are properly configured

### 3. Deploy with Dokploy

Run the Dokploy deployment command:

```bash
dokploy deploy
```

Dokploy will handle:
- Building the Docker images
- Starting the containers
- Setting up networking
- Managing environment variables

### 4. Database Management

The PostgreSQL database is configured to persist data in a Docker volume. To perform database operations:

```bash
# Connect to the database
dokploy exec db psql -U url_matcher_user -d url_matcher_db

# Backup the database
dokploy exec db pg_dump -U url_matcher_user url_matcher_db > backup.sql

# Restore the database
cat backup.sql | dokploy exec -T db psql -U url_matcher_user url_matcher_db
```

### 5. Monitoring and Maintenance

```bash
# View logs
dokploy logs

# Follow logs in real-time
dokploy logs -f

# Restart services
dokploy restart

# Update application (after pulling new code)
dokploy rebuild
```

## Application Structure

The URL Matcher application has been configured with the following components:

1. **Django Web Application**:
   - Serves the URL matching interface
   - Handles file uploads and processing
   - Generates matching reports

2. **PostgreSQL Database**:
   - Stores user data and matching results
   - Persists data in a Docker volume

3. **WhiteNoise**:
   - Serves static files directly from Django
   - Optimizes static file delivery with compression and caching

## Troubleshooting

- **Database Connection Issues**: Check if the PostgreSQL container is running and if the credentials in `.env` match those in `docker-compose.yml`.
- **Static Files Not Loading**: Verify that WhiteNoise is properly configured in settings_production.py.
- **Permission Issues**: Check that the media and static volumes have correct permissions.

## Security Considerations

1. Always use HTTPS in production
2. Keep all credentials secure and never commit them to version control
3. Regularly update dependencies to patch security vulnerabilities
4. Use strong, unique passwords for the database
5. Configure firewall rules on your VPS to only allow necessary ports
