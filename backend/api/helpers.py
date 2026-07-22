"""Helpers for the API app."""

from django.contrib.auth.base_user import BaseUserManager
from django.core import signing


def normalize_email_value(email):
    if not email:
        return ''

    return BaseUserManager.normalize_email(str(email).strip())


def normalize_username_value(username):
    if not username:
        return ''

    return str(username).strip().lower()


def get_signed_payload(token, salt, max_age=None):
    try:
        if max_age is None:
            return signing.loads(token, salt=salt)

        return signing.loads(token, salt=salt, max_age=max_age)
    except signing.SignatureExpired as error:
        raise ValueError('This link has expired. Please request a new one.') from error
    except signing.BadSignature as error:
        raise ValueError('Invalid or tampered link.') from error
