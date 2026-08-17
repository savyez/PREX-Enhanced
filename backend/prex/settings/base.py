"""Base Settings shared between both local.py and production.py"""


from datetime import timedelta
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from .environment import config, validate_required
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('DJANGO_SECRET_KEY', default='')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'api',
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

AUTH_USER_MODEL = 'api.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'prex.urls'
WSGI_APPLICATION = 'prex.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'PREX API',
    'DESCRIPTION': 'Cryptocurrency market data, authentication, charts and watchlist management API.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY': [{'BearerAuth': []}],
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'system', 'description': 'Health and API status.'},
        {'name': 'market', 'description': 'Coin market data, search and charts.'},
        {'name': 'auth', 'description': 'Registration, sessions and password recovery.'},
        {'name': 'watchlists', 'description': 'Authenticated watchlist operations.'},
    ],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            },
        },
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Cookie & Session Security Settings for JWT Authentication
AUTH_COOKIE_REFRESH_NAME = 'refresh_token'
AUTH_COOKIE_SECURE = config('AUTH_COOKIE_SECURE', cast=bool, default=False)
AUTH_COOKIE_SAMESITE = config('AUTH_COOKIE_SAMESITE', default='Lax')
AUTH_COOKIE_PATH = config('AUTH_COOKIE_PATH', default='/api/v1/')
CORS_ALLOW_CREDENTIALS = True

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]

# Email — config values come from .env, so safe in base
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool, default=False)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_VERIFICATION_SALT = 'api.email_verification'
EMAIL_VERIFICATION_MAX_AGE_SECONDS = config('EMAIL_VERIFICATION_MAX_AGE_SECONDS', cast=int, default=600)
EMAIL_VERIFICATION_URL = config('EMAIL_VERIFICATION_URL', default='')
EMAIL_VERIFICATION_SUCCESS_URL = config('EMAIL_VERIFICATION_SUCCESS_URL', default='')
PASSWORD_RESET_SALT = 'api.password_reset'
PASSWORD_RESET_MAX_AGE_SECONDS = config('PASSWORD_RESET_MAX_AGE_SECONDS', cast=int, default=600)
PASSWORD_RESET_URL = config('PASSWORD_RESET_URL', default='http://localhost:5173/reset-password-confirm')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default=''),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', cast=int, default=5432),
    }
}

COINGECKO_API_URL = config('COINGECKO_API_URL', default='https://api.coingecko.com/api/v3/coins/markets')
COINGECKO_CHART_URL = config('COINGECKO_CHART_URL', default='https://api.coingecko.com/api/v3/coins/')
COINGECKO_SEARCH_URL = config('COINGECKO_SEARCH_URL', default='https://api.coingecko.com/api/v3/search')
COINGECKO_API_KEY = config('COINGECKO_API_KEY', default='')

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured('EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be true.')

validate_required({
    'DJANGO_SECRET_KEY': SECRET_KEY,
    'EMAIL_VERIFICATION_URL': EMAIL_VERIFICATION_URL,
    'EMAIL_VERIFICATION_SUCCESS_URL': EMAIL_VERIFICATION_SUCCESS_URL,
    'DB_NAME': DATABASES['default']['NAME'],
    'DB_USER': DATABASES['default']['USER'],
    'DB_PASSWORD': DATABASES['default']['PASSWORD'],
    'DB_HOST': DATABASES['default']['HOST'],
})

# Cache Configuration
REDIS_CACHE_URL = config('REDIS_CACHE_URL', default=config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0'))
if REDIS_CACHE_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_CACHE_URL,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', cast=bool, default=False)

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'sync-coingecko-market-data-every-300s': {
        'task': 'api.tasks.sync_coingecko_market_data',
        'schedule': crontab(minute='*/5'),     #runs every 5 min
    },
}
