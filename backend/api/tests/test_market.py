from unittest.mock import patch
from django.urls import reverse
from django.utils import timezone
from .base import BaseAPITestCase
from ..models import Coin
from .. import views


class MarketCoinListTests(BaseAPITestCase):
    """Test suite for coin list retrieval and pagination."""

    def test_coin_list_returns_paginated_local_coins(self):
        Coin.objects.create(
            ticker='BTC',
            coin_name='Bitcoin',
            price='65000.00',
            market_volume='2000000000.00',
            market_cap_rank=1,
            last_updated_at=timezone.now(),
        )

        response1 = self.client.get(reverse('coin_list'))
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data['results']), 1)
        self.assertEqual(response1.data['results'][0]['ticker'], 'BTC')
        self.assertEqual(response1.data['results'][0]['coin_name'], 'Bitcoin')

        # Test cache hit on subsequent request
        response2 = self.client.get(reverse('coin_list'))
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data, response1.data)


class MarketSearchTests(BaseAPITestCase):
    """Test suite for coin search and CoinGecko ID resolution."""

    def test_search_coins_by_name(self):
        Coin.objects.create(
            ticker='PUDGY',
            coin_name='Pudgy Penguin',
            price='15.50',
            market_volume='500000.00',
            last_updated_at=timezone.now(),
        )

        response = self.client.get(reverse('search_coins', kwargs={'coin_id': 'Pudgy Penguin'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['ticker'], 'PUDGY')
        self.assertEqual(response.data['results'][0]['coin_name'], 'Pudgy Penguin')

    @patch('api.views.fetch_coingecko')
    def test_resolve_coin_gecko_id_multi_word_coin(self, fetch_mock):
        Coin.objects.create(
            ticker='WBTC',
            coin_name='Wrapped Bitcoin',
            price='60000.00',
            market_volume='1000000.00',
            last_updated_at=timezone.now(),
        )
        mock_response = patch('requests.Response').start()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coins': [
                {'id': 'wrapped-bitcoin', 'name': 'Wrapped Bitcoin', 'symbol': 'WBTC'},
                {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'BTC'},
            ]
        }
        fetch_mock.return_value = mock_response

        resolved = views.resolve_coin_gecko_id('WBTC')
        self.assertEqual(resolved, 'wrapped-bitcoin')

        # Test resolving by multi-word coin name
        resolved_by_name = views.resolve_coin_gecko_id('Wrapped Bitcoin')
        self.assertEqual(resolved_by_name, 'wrapped-bitcoin')


class MarketChartTests(BaseAPITestCase):
    """Test suite for historical price chart endpoints."""

    @patch('api.views.fetch_coingecko', side_effect=views.CoinGeckoTimeout)
    def test_chart_returns_gateway_timeout_when_provider_times_out(self, fetch_mock):
        response = self.client.get(
            reverse('coin_chart', kwargs={'coin_id': 'BTC'}),
            {'days': 7},
        )

        self.assertEqual(response.status_code, 504)
        self.assertIn('timed out', response.data['error'])
        fetch_mock.assert_called_once()


class MarketCeleryTaskTests(BaseAPITestCase):
    """Test suite for asynchronous Celery market synchronization tasks."""

    @patch('api.tasks.fetch_coingecko')
    def test_sync_coingecko_market_data_task(self, fetch_mock):
        from ..tasks import sync_coingecko_market_data
        mock_response = patch('requests.Response').start()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'symbol': 'btc',
                'name': 'Bitcoin',
                'current_price': 65000.0,
                'total_volume': 2000000000.0,
                'last_updated': '2026-01-01T00:00:00Z',
                'market_cap_rank': 1,
                'price_change_percentage_24h': 2.5,
                'image': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
            }
        ]
        fetch_mock.return_value = mock_response

        result = sync_coingecko_market_data()
        self.assertEqual(result['status'], 'success')
        coin = Coin.objects.get(ticker='BTC')
        self.assertEqual(coin.image, 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png')
