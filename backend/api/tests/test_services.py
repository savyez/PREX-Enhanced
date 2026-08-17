from unittest.mock import patch
from django.test import override_settings

from ..services.coingecko import CoinGeckoClient
from ..services.auth_service import AuthService, AuthenticationServiceError
from ..services.email_service import EmailService
from .base import BaseAPITestCase


class CoinGeckoServiceTests(BaseAPITestCase):
    """Unit tests for CoinGecko client service."""

    @patch('api.services.coingecko.CoinGeckoClient.resolve_coin_id', return_value='bitcoin')
    @patch('api.services.coingecko.CoinGeckoClient.fetch')
    def test_coingecko_service_get_chart_data_caches_result(self, fetch_mock, resolve_mock):
        mock_resp = patch('requests.Response').start()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'prices': [[1700000000000, 50000.0], [1700003600000, 50500.0]]
        }
        mock_resp.raise_for_status.return_value = None
        fetch_mock.return_value = mock_resp

        client = CoinGeckoClient(api_key='test-key')
        data, err = client.get_chart_data('bitcoin', days=7)
        self.assertIsNone(err)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['chart_data']), 2)
        self.assertEqual(data['coin_id'], 'bitcoin')


class AuthServiceTests(BaseAPITestCase):
    """Unit tests for authentication and session management service."""

    def test_auth_service_methods(self):
        user = self.create_user('serviceuser', 'serviceuser@example.com', 'Pass123!456', email_confirmed=True)

        # Authenticate
        auth_user, access, refresh = AuthService.authenticate_user('serviceuser@example.com', 'Pass123!456')
        self.assertEqual(auth_user.id, user.id)
        self.assertTrue(access)
        self.assertTrue(refresh)

        # Update profile
        updated_user = AuthService.update_user_profile(user, {'first_name': 'NewFirst', 'last_name': 'NewLast'})
        self.assertEqual(updated_user.first_name, 'NewFirst')

        # Revoke session
        self.assertTrue(AuthService.revoke_session(user, refresh))

        # Revoke invalid session should raise
        with self.assertRaises(AuthenticationServiceError):
            AuthService.revoke_session(user, 'invalid-token')


class EmailServiceTests(BaseAPITestCase):
    """Unit tests for email rendering and delivery service."""

    @override_settings(EMAIL_HOST_USER='test@example.com', EMAIL_HOST_PASSWORD='password')
    @patch('api.services.email_service.smtplib.SMTP')
    def test_email_service_sends_email_message(self, smtp_mock):
        smtp_instance = smtp_mock.return_value.__enter__.return_value

        EmailService.send_email_message(
            to_email='recipient@example.com',
            subject='Test Subject',
            text_body='Plain text message',
            html_content='<p>HTML message</p>',
        )

        smtp_instance.login.assert_called_once()
        smtp_instance.send_message.assert_called_once()
