from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.core import signing
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Coin, User, Watchlist, WatchlistItem
from .base import BaseAPITestCase


class AuthRegistrationTests(BaseAPITestCase):
    """Test suite for user registration and email verification workflows."""

    @override_settings(EMAIL_HOST_USER='user@example.com', EMAIL_HOST_PASSWORD='password')
    @patch('api.services.email_service.smtplib.SMTP')
    @patch('api.services.email_service.smtplib.SMTP_SSL')
    def test_register_user_creates_unverified_user_and_sends_email(self, smtp_ssl_mock, smtp_mock):
        smtp_instance = smtp_mock.return_value.__enter__.return_value
        response = self.client.post(
            reverse('register_user'),
            data={
                'username': 'alice',
                'dob': '1995-06-10',
                'email': 'alice@example.com',
                'password': 'StrongPass!234',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Verification email sent. Verify your email to complete registration.')

        user = User.objects.get(email='alice@example.com')
        self.assertFalse(user.email_confirmed)
        smtp_instance.login.assert_called_once()
        smtp_instance.send_message.assert_called_once()

    @patch('api.services.email_service.smtplib.SMTP')
    @patch('api.services.email_service.smtplib.SMTP_SSL')
    def test_register_existing_unverified_user_resends_verification_email(self, smtp_ssl_mock, smtp_mock):
        self.create_user('bob', 'bob@example.com', 'Password123!', email_confirmed=False)

        response = self.client.post(
            reverse('register_user'),
            data={
                'username': 'bob',
                'dob': '1995-06-10',
                'email': 'bob@example.com',
                'password': 'Password123!',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Verification email resent. Verify your email to complete registration.')
        self.assertEqual(User.objects.filter(email='bob@example.com').count(), 1)

    def test_register_existing_verified_user_returns_error(self):
        self.create_user('carl', 'carl@example.com', 'Password123!', email_confirmed=True)

        response = self.client.post(
            reverse('register_user'),
            data={
                'username': 'carl',
                'dob': '1995-06-10',
                'email': 'carl@example.com',
                'password': 'Password123!',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Email already exists.')

    def test_verify_email_activates_user(self):
        user = self.create_user('dana', 'dana@example.com', 'Password123!', email_confirmed=False)
        token = signing.dumps({'email': user.email}, salt=settings.EMAIL_VERIFICATION_SALT)

        response = self.client.get(reverse('verify_email', kwargs={'token': token}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], settings.EMAIL_VERIFICATION_SUCCESS_URL)

        user.refresh_from_db()
        self.assertTrue(user.email_confirmed)


class AuthLoginLogoutTests(BaseAPITestCase):
    """Test suite for authentication, JWT session lifecycle, HttpOnly cookies, and token revocation."""

    def test_login_rejects_unverified_email(self):
        self.create_user('ed', 'ed@example.com', 'Password123!', email_confirmed=False)

        response = self.client.post(
            reverse('login_user'),
            data={
                'username': 'ed',
                'email': 'ed@example.com',
                'password': 'Password123!',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Email not verified. Please verify your email before logging in.')

    def test_login_with_verified_user_returns_tokens(self):
        self.create_user('fay', 'fay@example.com', 'Password123!', email_confirmed=True)

        response = self.client.post(
            reverse('login_user'),
            data={
                'username': 'fay',
                'email': 'fay@example.com',
                'password': 'Password123!',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.data)
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        self.assertIn(cookie_name, response.cookies)
        cookie = response.cookies[cookie_name]
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(response.data['user']['email'], 'fay@example.com')

    def test_login_rejects_missing_required_fields(self):
        response = self.client.post(reverse('login_user'), data={'email': 'bad@example.com'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'This field is required.')

    def test_expired_access_token_is_rejected(self):
        user = self.create_user('expired', 'expired@example.com', 'Password123!')
        access_token = RefreshToken.for_user(user).access_token
        access_token['exp'] = int((timezone.now() - timedelta(minutes=1)).timestamp())
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, 401)

    def test_token_refresh_via_httponly_cookie(self):
        self.create_user('refreshuser', 'refreshuser@example.com', 'Password123!', email_confirmed=True)

        login_response = self.client.post(
            reverse('login_user'),
            data={'username': 'refreshuser', 'email': 'refreshuser@example.com', 'password': 'Password123!'},
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        self.assertIn(cookie_name, self.client.cookies)

        # Clear authorization header so refresh relies exclusively on the cookie
        self.client.credentials()

        refresh_response = self.client.post(reverse('token_refresh'), data={}, format='json')
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn('access_token', refresh_response.data)
        self.assertIn('access', refresh_response.data)
        new_access_token = refresh_response.data['access_token']

        # Verify access token works on authenticated endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        user_response = self.client.get(reverse('current_user'))
        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(user_response.data['user']['email'], 'refreshuser@example.com')

    def test_token_refresh_via_request_body(self):
        self.create_user('bodyuser', 'bodyuser@example.com', 'Password123!', email_confirmed=True)

        login_response = self.client.post(
            reverse('login_user'),
            data={'username': 'bodyuser', 'email': 'bodyuser@example.com', 'password': 'Password123!'},
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        refresh_token = login_response.cookies[cookie_name].value

        # Clear cookies so refresh only comes from request body
        self.client.cookies.clear()
        self.client.credentials()

        refresh_response = self.client.post(
            reverse('token_refresh'),
            data={'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn('access_token', refresh_response.data)

    def test_token_refresh_without_token_returns_401(self):
        self.client.cookies.clear()
        self.client.credentials()

        response = self.client.post(reverse('token_refresh'), data={}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_token_refresh_with_invalid_cookie_returns_401(self):
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        self.client.cookies[cookie_name] = 'invalid-token'
        self.client.credentials()

        response = self.client.post(reverse('token_refresh'), data={}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_logout_clears_httponly_cookie_and_blacklists_token(self):
        user = self.create_user('logoutuser', 'logoutuser@example.com', 'Password123!', email_confirmed=True)
        login_response = self.client.post(
            reverse('login_user'),
            data={'username': 'logoutuser', 'email': 'logoutuser@example.com', 'password': 'Password123!'},
            format='json'
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.data['access_token']
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        raw_refresh_token = login_response.cookies[cookie_name].value

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_response = self.client.post(reverse('logout_user'), data={}, format='json')
        self.assertEqual(logout_response.status_code, 200)
        self.assertTrue(logout_response.data['success'])

        # Check cookie was cleared / deleted
        self.assertIn(cookie_name, logout_response.cookies)
        deleted_cookie = logout_response.cookies[cookie_name]
        self.assertTrue(deleted_cookie['max-age'] == 0 or deleted_cookie.value == '')

        # Check the blacklisted refresh token cannot be used again
        self.client.credentials()
        self.client.cookies.clear()
        refresh_response = self.client.post(
            reverse('token_refresh'),
            data={'refresh': raw_refresh_token},
            format='json'
        )
        self.assertEqual(refresh_response.status_code, 401)

    def test_logout_requires_ownership_of_refresh_token(self):
        user1 = self.create_user('fayone', 'fayone@example.com', 'Password123!', email_confirmed=True)
        user2 = self.create_user('faytwo', 'faytwo@example.com', 'Password123!', email_confirmed=True)

        user1_tokens = self.authenticate_user('fayone', 'fayone@example.com', 'Password123!')
        user2_tokens = self.authenticate_user('faytwo', 'faytwo@example.com', 'Password123!')

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {user1_tokens['access_token']}")
        forbidden_response = self.client.post(
            reverse('logout_user'),
            data={'refresh_token': user2_tokens['refresh_token']},
            format='json'
        )
        self.assertEqual(forbidden_response.status_code, 403)

        success_response = self.client.post(
            reverse('logout_user'),
            data={'refresh_token': user1_tokens['refresh_token']},
            format='json'
        )
        self.assertEqual(success_response.status_code, 200)

        self.client.credentials()
        anonymous_response = self.client.post(
            reverse('logout_user'),
            data={'refresh_token': user2_tokens['refresh_token']},
            format='json'
        )
        self.assertEqual(anonymous_response.status_code, 401)


class AuthPasswordResetTests(BaseAPITestCase):
    """Test suite for password reset request and confirmation workflows."""

    @patch('api.services.email_service.smtplib.SMTP')
    @patch('api.services.email_service.smtplib.SMTP_SSL')
    def test_reset_password_flow_updates_password(self, smtp_ssl_mock, smtp_mock):
        user = self.create_user('gina', 'gina@example.com', 'Password123!', email_confirmed=True)

        response = self.client.post(
            reverse('reset_password'),
            data={'email': 'gina@example.com'},
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])

        token = signing.dumps({'email': user.email}, salt=settings.PASSWORD_RESET_SALT)
        response_confirm = self.client.post(
            reverse('reset_password_confirm', kwargs={'token': token}),
            data={
                'new_password': 'NewPass!234',
                'confirm_new_password': 'NewPass!234',
            },
            format='json'
        )

        self.assertEqual(response_confirm.status_code, 200)
        self.assertTrue(response_confirm.data['success'])

        user.refresh_from_db()
        self.assertTrue(user.check_password('NewPass!234'))

    def test_reset_password_confirm_get_redirects_to_frontend(self):
        user = self.create_user('hannah', 'hannah@example.com', 'Password123!', email_confirmed=True)
        token = signing.dumps({'email': user.email}, salt=settings.PASSWORD_RESET_SALT)

        response = self.client.get(reverse('reset_password_confirm', kwargs={'token': token}))

        self.assertEqual(response.status_code, 302)
        expected_url = f"{settings.PASSWORD_RESET_URL.rstrip('/')}/{token}"
        self.assertEqual(response['Location'], expected_url)


class UserProfileTests(BaseAPITestCase):
    """Test suite for user profile management and relational cascades."""

    def test_update_user_updates_authenticated_users_profile(self):
        user = self.create_user('gail', 'gail@example.com', 'Password123!', email_confirmed=True)
        self.authenticate_user('gail', 'gail@example.com', 'Password123!')

        response = self.client.patch(
            reverse('update_user', kwargs={'user_id': str(user.id)}),
            data={
                'first_name': 'Gail',
                'last_name': 'Rivera',
                'username': 'GailR',
            },
            format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['first_name'], 'Gail')
        self.assertEqual(response.data['user']['last_name'], 'Rivera')
        self.assertEqual(response.data['user']['username'], 'gailr')

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Gail')
        self.assertEqual(user.last_name, 'Rivera')
        self.assertEqual(user.username, 'gailr')

    def test_update_user_rejects_existing_username(self):
        self.create_user('henry', 'henry@example.com', 'Password123!', email_confirmed=True)
        user = self.create_user('iris', 'iris@example.com', 'Password123!', email_confirmed=True)
        self.authenticate_user('iris', 'iris@example.com', 'Password123!')

        response = self.client.patch(
            reverse('update_user', kwargs={'user_id': str(user.id)}),
            data={'username': 'henry'},
            format='json'
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['error'], 'username already exists, try a new one.')

    def test_deleting_user_removes_related_outstanding_tokens(self):
        user = self.create_user('jules', 'jules@example.com', 'Password123!', email_confirmed=True)
        OutstandingToken.objects.create(
            user=user,
            jti='test-jti',
            token='test-token',
            created_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=1),
        )

        user.delete()
        self.assertFalse(OutstandingToken.objects.filter(user_id=user.id).exists())

    def test_deleting_user_removes_watchlists_and_items(self):
        user = self.create_user('watchlist-owner', 'watchlist-owner@example.com', 'Password123!')
        coin = Coin.objects.create(
            ticker='BTC',
            coin_name='Bitcoin',
            price='64079.00000000',
            market_volume='17988848511.00',
            last_updated_at=timezone.now(),
        )
        watchlist = Watchlist.objects.create(user=user, name='Long Term')
        WatchlistItem.objects.create(watchlist=watchlist, ticker=coin)

        user.delete()

        self.assertFalse(Watchlist.objects.filter(id=watchlist.id).exists())
        self.assertFalse(WatchlistItem.objects.filter(watchlist_id=watchlist.id).exists())
        self.assertTrue(Coin.objects.filter(ticker=coin.ticker).exists())
