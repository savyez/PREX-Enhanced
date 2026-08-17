from django.urls import reverse
from django.utils import timezone

from ..models import Coin, Watchlist, WatchlistItem
from .base import BaseAPITestCase


class WatchlistManagementTests(BaseAPITestCase):
    """Test suite for watchlist CRUD operations, coin membership, and access control."""

    def test_watchlist_and_coin_management(self):
        user = self.create_user('harry', 'harry@example.com', 'Password123!', email_confirmed=True)
        coin = Coin.objects.create(
            ticker='BTC',
            coin_name='Bitcoin',
            price='50000.00000000',
            market_volume='1000000000.00',
            last_updated_at='2026-01-01T00:00:00Z',
        )

        self.authenticate_user('harry', 'harry@example.com', 'Password123!')

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

        # Duplicate addition check
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

        # Retrieve items
        items_response = self.client.get(reverse('show_watchlist_items', kwargs={'watchlist_id': watchlist_id}))
        self.assertEqual(items_response.status_code, 200)
        self.assertEqual(len(items_response.data['items']), 1)
        self.assertEqual(items_response.data['items'][0]['ticker']['ticker'], 'BTC')

        # Remove coin
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
        self.create_user('ivan', 'ivan@example.com', 'Password123!', email_confirmed=True)
        user2 = self.create_user('jill', 'jill@example.com', 'Password123!', email_confirmed=True)
        Coin.objects.create(
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

    def test_user_watchlists_returns_nested_items(self):
        user = self.create_user('karen', 'karen@example.com', 'Password123!', email_confirmed=True)
        coin1 = Coin.objects.create(
            ticker='BTC',
            coin_name='Bitcoin',
            price='65000.00000000',
            market_volume='20000000000.00',
            last_updated_at=timezone.now(),
        )
        coin2 = Coin.objects.create(
            ticker='ETH',
            coin_name='Ethereum',
            price='3500.00000000',
            market_volume='10000000000.00',
            last_updated_at=timezone.now(),
        )
        watchlist1 = Watchlist.objects.create(user=user, name='Main')
        watchlist2 = Watchlist.objects.create(user=user, name='Alt')
        WatchlistItem.objects.create(watchlist=watchlist1, ticker=coin1)
        WatchlistItem.objects.create(watchlist=watchlist1, ticker=coin2)

        self.authenticate_user('karen', 'karen@example.com', 'Password123!')

        response = self.client.get(
            reverse('user_watchlists', kwargs={'user_id': str(user.id)})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['watchlists']), 2)

        main_watchlist = next(w for w in response.data['watchlists'] if w['id'] == watchlist1.id)
        self.assertIn('items', main_watchlist)
        self.assertEqual(len(main_watchlist['items']), 2)
        tickers = [item['ticker']['ticker'] for item in main_watchlist['items']]
        self.assertIn('BTC', tickers)
        self.assertIn('ETH', tickers)

        alt_watchlist = next(w for w in response.data['watchlists'] if w['id'] == watchlist2.id)
        self.assertIn('items', alt_watchlist)
        self.assertEqual(len(alt_watchlist['items']), 0)
