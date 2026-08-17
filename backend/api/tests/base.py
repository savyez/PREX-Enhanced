from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from ..models import User


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
)
class BaseAPITestCase(APITestCase):
    """Base test case providing user creation and authentication test utilities."""

    def create_user(self, username, email, password, dob='2000-01-01', email_confirmed=True):
        """Helper to create and persist a User instance."""
        return User.objects.create_user(
            username=username,
            dob=dob,
            email=email,
            password=password,
            email_confirmed=email_confirmed,
        )

    def authenticate_user(self, username, email, password):
        """Helper to perform API login and set Authorization header credentials on self.client."""
        response = self.client.post(
            reverse('login_user'),
            data={'username': username, 'email': email, 'password': password},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = dict(response.data)
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        if cookie_name in response.cookies:
            data['refresh_token'] = response.cookies[cookie_name].value
        return data
