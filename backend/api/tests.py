from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.core import signing
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Coin, User, Watchlist, WatchlistItem
from . import views


class ApiIntegrationTests(APITestCase):
    def create_user(self, username, email, password, dob='2000-01-01', email_confirmed=True):
        return User.objects.create_user(
            username=username,
            dob=dob,
            email=email,
            password=password,
            email_confirmed=email_confirmed,
        )

    def authenticate_user(self, username, email, password):
        response = self.client.post(
            reverse('login_user'),
            data={'username': username, 'email': email, 'password': password},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        token = response.data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return response.data

    @patch('api.views.smtplib.SMTP')
    @patch('api.views.smtplib.SMTP_SSL')
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

    @patch('api.views.smtplib.SMTP')
    @patch('api.views.smtplib.SMTP_SSL')
    def test_register_existing_unverified_user_resends_verification_email(self, smtp_ssl_mock, smtp_mock):
        user = self.create_user('bob', 'bob@example.com', 'Password123!', email_confirmed=False)

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
        self.assertIn('refresh_token', response.data)
        self.assertEqual(response.data['user']['email'], 'fay@example.com')

    def test_expired_access_token_is_rejected(self):
        user = self.create_user('expired', 'expired@example.com', 'Password123!')
        access_token = RefreshToken.for_user(user).access_token
        access_token['exp'] = int((timezone.now() - timedelta(minutes=1)).timestamp())
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(reverse('current_user'))

        self.assertEqual(response.status_code, 401)

    def test_health_check_is_public(self):
        response = self.client.get(reverse('health_check'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_openapi_schema_is_available(self):
        response = self.client.get(reverse('api_schema'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('/api/v1/health/', response.data['paths'])
        self.assertIn('/api/v1/login/', response.data['paths'])
        self.assertIn('/api/v1/watchlists/create/', response.data['paths'])

    def test_login_rejects_missing_required_fields(self):
        response = self.client.post(reverse('login_user'), data={'email': 'bad@example.com'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'This field is required.')

    @patch('api.views.fetch_coingecko', side_effect=views.CoinGeckoTimeout)
    def test_coin_list_returns_gateway_timeout_when_provider_times_out(self, fetch_mock):
        response = self.client.get(reverse('coin_list'))

        self.assertEqual(response.status_code, 504)
        self.assertIn('timed out', response.data['error'])
        fetch_mock.assert_called_once()

    @patch('api.views.fetch_coingecko', side_effect=views.CoinGeckoTimeout)
    def test_chart_returns_gateway_timeout_when_provider_times_out(self, fetch_mock):
        response = self.client.get(
            reverse('coin_chart', kwargs={'coin_id': 'BTC'}),
            {'days': 7},
        )

        self.assertEqual(response.status_code, 504)
        self.assertIn('timed out', response.data['error'])
        fetch_mock.assert_called_once()

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
        item = WatchlistItem.objects.create(watchlist=watchlist, ticker=coin)

        user.delete()

        self.assertFalse(Watchlist.objects.filter(id=watchlist.id).exists())
        self.assertFalse(WatchlistItem.objects.filter(id=item.id).exists())
        self.assertTrue(Coin.objects.filter(ticker=coin.ticker).exists())

    @patch('api.views.smtplib.SMTP')
    @patch('api.views.smtplib.SMTP_SSL')
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

    @patch('api.views.smtplib.SMTP')
    @patch('api.views.smtplib.SMTP_SSL')
    def test_watchlist_and_coin_management(self, smtp_ssl_mock, smtp_mock):
        user = self.create_user('harry', 'harry@example.com', 'Password123!', email_confirmed=True)
        coin = Coin.objects.create(
            ticker='BTC',
            coin_name='Bitcoin',
            price='50000.00000000',
            market_volume='1000000000.00',
            last_updated_at='2026-01-01T00:00:00Z',
        )

        login_data = self.authenticate_user('harry', 'harry@example.com', 'Password123!')

        create_watchlist_response = self.client.post(
            reverse('create_watchlist'),
            data={'name': 'Favorites'},
            format='json'
        )
        self.assertEqual(create_watchlist_response.status_code, 201)
        watchlist_id = create_watchlist_response.data['watchlist']['id']

        add_coin_response = self.client.post(
            reverse('add_coin_to_watchlist'),
            data={
                'user_id': str(user.id),
                'watchlist_id': watchlist_id,
                'ticker': 'BTC',
            },
            format='json'
        )
        self.assertEqual(add_coin_response.status_code, 200)
        self.assertEqual(add_coin_response.data['watchlist']['id'], watchlist_id)

        duplicate_response = self.client.post(
            reverse('add_coin_to_watchlist'),
            data={
                'user_id': str(user.id),
                'watchlist_id': watchlist_id,
                'ticker': 'BTC',
            },
            format='json'
        )
        self.assertEqual(duplicate_response.status_code, 409)

        items_response = self.client.get(reverse('show_watchlist_items', kwargs={'watchlist_id': watchlist_id}))
        self.assertEqual(items_response.status_code, 200)
        self.assertEqual(len(items_response.data['items']), 1)
        self.assertEqual(items_response.data['items'][0]['ticker']['ticker'], 'BTC')

        remove_coin_response = self.client.post(
            reverse('remove_coin_from_watchlist'),
            data={
                'user_id': str(user.id),
                'watchlist_id': watchlist_id,
                'ticker': 'BTC',
            },
            format='json'
        )
        self.assertEqual(remove_coin_response.status_code, 200)
        self.assertEqual(remove_coin_response.data['watchlist']['id'], watchlist_id)

        self.assertFalse(WatchlistItem.objects.filter(watchlist_id=watchlist_id, ticker=coin).exists())

    def test_add_coin_to_watchlist_rejects_other_user(self):
        user1 = self.create_user('ivan', 'ivan@example.com', 'Password123!', email_confirmed=True)
        user2 = self.create_user('jill', 'jill@example.com', 'Password123!', email_confirmed=True)
        coin = Coin.objects.create(
            ticker='ETH',
            coin_name='Ethereum',
            price='3000.00000000',
            market_volume='600000000.00',
            last_updated_at='2026-01-01T00:00:00Z',
        )
        watchlist = Watchlist.objects.create(user=user2, name='Other')

        self.authenticate_user('ivan', 'ivan@example.com', 'Password123!')

        response = self.client.post(
            reverse('add_coin_to_watchlist'),
            data={
                'user_id': str(user2.id),
                'watchlist_id': watchlist.id,
                'ticker': 'ETH',
            },
            format='json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], "You do not have permission to modify this user's watchlists.")
