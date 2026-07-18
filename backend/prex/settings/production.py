"""Production settings for PREX
DO NO TOUCH IF NOT NECESSARY"""

from .base import *
from .environment import config, env_list, validate_required

DEBUG = False

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # needed for collectstatic

CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')

validate_required({
    'DJANGO_ALLOWED_HOSTS': config('DJANGO_ALLOWED_HOSTS', default=''),
    'CORS_ALLOWED_ORIGINS': config('CORS_ALLOWED_ORIGINS', default=''),
    'COINGECKO_API_KEY': COINGECKO_API_KEY,
})

# Security headers — add these for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
