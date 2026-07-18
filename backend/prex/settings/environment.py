from django.core.exceptions import ImproperlyConfigured
from decouple import config


def env_list(name, default=''):
    value = config(name, default=default)
    return [item.strip() for item in value.split(',') if item.strip()]


def validate_required(values):
    missing = sorted(name for name, value in values.items() if value in (None, ''))
    if missing:
        raise ImproperlyConfigured(
            'Missing required environment variables: ' + ', '.join(missing)
        )
