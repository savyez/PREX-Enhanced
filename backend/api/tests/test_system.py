from django.urls import reverse
from rest_framework.test import APITestCase


class SystemEndpointTests(APITestCase):
    """Tests for system level endpoints: root welcome, health check, and OpenAPI schema."""

    def test_home_endpoint_returns_welcome_message(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Welcome to the PREX API!')

    def test_health_check_is_public(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['message'], 'PREX API is healthy and running.')

    def test_openapi_schema_is_available(self):
        response = self.client.get(reverse('api_schema'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('/api/v1/health/', response.data['paths'])
        self.assertIn('/api/v1/login/', response.data['paths'])
        self.assertIn('/api/v1/watchlists/create/', response.data['paths'])
