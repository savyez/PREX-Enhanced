import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

from ..models import Coin


class CoinGeckoTimeout(Exception):
    """Raised when CoinGecko does not respond within the configured timeout."""


class CoinGeckoClient:
    """Client service for interacting with the CoinGecko API."""

    def __init__(self, api_key=None, timeout=(3, 10)):
        self.api_url = getattr(settings, 'COINGECKO_API_URL', 'https://api.coingecko.com/api/v3/coins/markets')
        self.chart_url = getattr(settings, 'COINGECKO_CHART_URL', 'https://api.coingecko.com/api/v3/coins/')
        self.search_url = getattr(settings, 'COINGECKO_SEARCH_URL', 'https://api.coingecko.com/api/v3/search')
        self.api_key = api_key or getattr(settings, 'COINGECKO_API_KEY', '')
        self.timeout = timeout

    @property
    def headers(self):
        return {
            "x-cg-demo-api-key": self.api_key
        }

    def _create_session(self):
        retry_strategy = Retry(
            total=2,
            connect=2,
            read=2,
            backoff_factor=0.5,
            status_forcelist=(429, 502, 503, 504),
            allowed_methods=frozenset({'GET'}),
            respect_retry_after_header=False,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount('https://', adapter)
        return session

    def fetch(self, url, params=None):
        """Performs a GET request against the CoinGecko API with retries and timeout bounds."""
        # Support dynamically mocked fetch_coingecko if patched in tests or top-level module
        views_mod = sys.modules.get('api.views')
        if views_mod and hasattr(views_mod, 'fetch_coingecko') and views_mod.fetch_coingecko != fetch_coingecko:
            return views_mod.fetch_coingecko(url, params=params)

        with self._create_session() as session:
            try:
                return session.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout,
                )
            except requests.Timeout as error:
                raise CoinGeckoTimeout from error

    def resolve_coin_id(self, coin_id):
        """Resolves a given ticker or coin name to its corresponding CoinGecko identifier."""
        raw_input = str(coin_id).strip()
        if not raw_input:
            return None

        search_query = raw_input
        ticker_target = raw_input.upper()
        name_target = raw_input

        local_coin = Coin.objects.filter(
            Q(ticker__iexact=raw_input) | Q(coin_name__iexact=raw_input) | Q(coin_name__icontains=raw_input)
        ).first()
        if local_coin:
            search_query = local_coin.coin_name.strip()
            name_target = local_coin.coin_name.strip()
            ticker_target = local_coin.ticker.strip().upper()

        try:
            response = self.fetch(self.search_url, params={'query': search_query})
            response.raise_for_status()
            payload = response.json()
        except CoinGeckoTimeout:
            raise
        except (requests.RequestException, ValueError):
            return None

        coins = payload.get('coins', [])
        if not coins:
            return None

        raw_lower = raw_input.lower()
        raw_slug = raw_lower.replace(' ', '-').replace('_', '-')
        name_lower = name_target.lower()
        name_slug = name_lower.replace(' ', '-').replace('_', '-')

        # 1. Match by CoinGecko ID (exact or slugified)
        for candidate in coins:
            candidate_id = str(candidate.get('id', '')).strip().lower()
            if candidate_id in (raw_lower, raw_slug, name_lower, name_slug):
                return candidate.get('id')

        # 2. Match by Symbol/Ticker
        for candidate in coins:
            candidate_symbol = str(candidate.get('symbol', '')).strip().upper()
            if candidate_symbol in (ticker_target, raw_input.upper()):
                return candidate.get('id')

        # 3. Match by Name (exact or slugified)
        for candidate in coins:
            candidate_name = str(candidate.get('name', '')).strip().lower()
            candidate_name_slug = candidate_name.replace(' ', '-').replace('_', '-')
            if candidate_name in (name_lower, raw_lower) or candidate_name_slug in (name_slug, raw_slug):
                return candidate.get('id')

        # 4. Fallback to top search result
        return coins[0].get('id')

    def get_chart_data(self, coin_id, days=7):
        """Fetches hourly historical price points for a coin and caches the formatted result."""
        resolved_coin_id = self.resolve_coin_id(coin_id)
        if not resolved_coin_id:
            return None, 'Unable to resolve the requested coin for chart data.'

        cache_key = f"coin_chart:{resolved_coin_id}:{days}"
        cached_chart = cache.get(cache_key)
        if cached_chart:
            return cached_chart, None

        try:
            response = self.fetch(f"{self.chart_url}{resolved_coin_id}/market_chart", params={
                "vs_currency": "usd",
                "days": days,
                "interval": "hourly",
                "precision": 4,
                "sparkline": True
            })
            response.raise_for_status()
            data = response.json()
        except CoinGeckoTimeout:
            raise
        except requests.RequestException:
            return None, 'Unable to fetch live chart data right now. Please try again later.'

        prices = data.get('prices', [])
        if not prices:
            return None, 'No chart data available for the specified coin.'

        payload = {
            'success': True,
            'coin_id': resolved_coin_id,
            'chart_data': [{'timestamp': ts, 'price': price} for ts, price in prices]
        }
        cache.set(cache_key, payload, timeout=300)
        return payload, None

    def get_market_coins(self, page=1, per_page=250, vs_currency='usd'):
        """Fetches paginated list of coins with current market data."""
        response = self.fetch(self.api_url, params={
            "vs_currency": vs_currency,
            "order_by": "market_cap_rank_asc",
            "per_page": per_page,
            "page": page,
            "sparkline": True,
        })
        response.raise_for_status()
        return response.json()


# Shared singleton instance
coingecko_client = CoinGeckoClient()


# Module-level convenience functions
def fetch_coingecko(url, params=None):
    return coingecko_client.fetch(url, params=params)


def resolve_coin_gecko_id(coin_id):
    return coingecko_client.resolve_coin_id(coin_id)
