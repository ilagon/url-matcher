# URL Matcher Deployment Guide

This guide provides instructions for deploying the URL Matcher application to a Virtual Private Server (VPS) using Docker.

## Prerequisites

- A VPS with Docker and Docker Compose installed
- Domain name (optional, but recommended for production)
- Basic knowledge of Linux commands

## Deployment Steps

### 1. Prepare Your Server

Ensure Docker and Docker Compose are installed on your VPS:

```bash
# Update package lists
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker repository
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Install Docker
sudo apt update
sudo apt install -y docker-ce

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

### 2. Clone the Repository

Clone the URL Matcher repository to your server:

```bash
git clone <your-repository-url>
cd url-matcher
```

### 3. Configure Environment Variables

Create a `.env` file from the sample:

```bash
cp sample.env .env
```

Edit the `.env` file to set secure values for:
- `SECRET_KEY`: Generate a secure random string
- `DB_PASSWORD`: Set a strong password
- `ALLOWED_HOSTS`: Add your domain name
- Other settings as needed

### 4. Configure Nginx for Your Domain

Edit the Nginx configuration file at `nginx/conf.d/url_matcher.conf`:

1. Replace `your-domain.com` with your actual domain name
2. If using HTTPS, uncomment and configure the SSL sections

### 5. Build and Start the Application

```bash
# Build and start the containers in detached mode
docker-compose up -d

# Check if containers are running
docker-compose ps
```

### 6. Set Up SSL (Optional but Recommended)

For a production environment, you should set up SSL. You can use Let's Encrypt:

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Update your .env file
# Set SECURE_SSL_REDIRECT=True
# Set SESSION_COOKIE_SECURE=True
# Set CSRF_COOKIE_SECURE=True
```

### 7. Monitoring and Maintenance

```bash
# View logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Update application (after pulling new code)
docker-compose build
docker-compose up -d
```

## Troubleshooting

- **Database Connection Issues**: Check if the PostgreSQL container is running and if the credentials in `.env` match those in `docker-compose.yml`.
- **Static Files Not Loading**: Verify that the Nginx configuration correctly maps static file locations.
- **Permission Issues**: Check that the media and static volumes have correct permissions.

## Backup and Restore

### Database Backup

```bash
docker-compose exec db pg_dump -U url_matcher_user url_matcher_db > backup.sql
```

### Database Restore

```bash
cat backup.sql | docker-compose exec -T db psql -U url_matcher_user url_matcher_db
```

## Security Considerations

1. Never expose the Django development server directly to the internet
2. Keep all credentials secure and never commit them to version control
3. Regularly update dependencies to patch security vulnerabilities
4. Use strong, unique passwords for the database
5. Configure firewall rules to only allow necessary ports (80, 443)
