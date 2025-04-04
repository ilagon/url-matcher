"""
Production settings for url_matcher_project.
This file extends the base settings and overrides values for production.
"""

import os
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Secret key should be set from environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Allow all hosts in dokploy environment
ALLOWED_HOSTS = ['*']  # Accept requests from any host

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'url_matcher_db'),
        'USER': os.environ.get('DB_USER', 'url_matcher_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# WhiteNoise configuration for serving static files
# Use CompressedStaticFilesStorage instead of CompressedManifestStaticFilesStorage
# This avoids issues with file hashing that can cause 400 errors
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year in seconds
WHITENOISE_USE_FINDERS = True
WHITENOISE_ROOT = STATIC_ROOT
WHITENOISE_AUTOREFRESH = True  # Refresh files during development
WHITENOISE_MIMETYPES = {
    '.ico': 'image/x-icon',
    '.svg': 'image/svg+xml',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject',
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
URL_MATCHER_OUTPUT_DIR = os.path.join(MEDIA_ROOT, 'url_matcher_output')

# Security settings - relaxed for dokploy deployment
SECURE_SSL_REDIRECT = False  # Don't force SSL redirect
SESSION_COOKIE_SECURE = False  # Allow cookies over non-HTTPS
CSRF_COOKIE_SECURE = False  # Allow CSRF cookies over non-HTTPS
SECURE_HSTS_SECONDS = 0  # Disable HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# CORS settings
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = ['*']

# CSRF settings - relaxed for dokploy deployment
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')
CSRF_COOKIE_SECURE = False  # Allow CSRF cookies over non-HTTPS
CSRF_USE_SESSIONS = False  # Use cookies instead of sessions for CSRF
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to access the CSRF cookie
CSRF_COOKIE_SAMESITE = None  # Allow cross-site requests with credentials
CSRF_COOKIE_DOMAIN = None  # Allow subdomains to access the CSRF cookie

# Paths that should be exempt from CSRF verification
CSRF_EXEMPT_PATHS = [
    '/upload-csv/',  # Main upload form
    '/check-job-status/',  # AJAX endpoint for checking job status
]

# Middleware configuration - optimized for dokploy deployment
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Keep security first
    'whitenoise.middleware.WhiteNoiseMiddleware',     # WhiteNoise right after security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',         # CORS before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    # Custom CSRF middleware with more relaxed settings for dokploy
    'matcher_app.middleware.FlexibleCSRFMiddleware',  # Use our custom CSRF middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
