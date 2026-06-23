"""Production settings for PREX
DO NO TOUCH IF NOT NECESSARY"""

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # needed for collectstatic

CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Security headers — add these for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True