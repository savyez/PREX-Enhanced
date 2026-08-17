import logging
import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import Coin
from .services.coingecko import fetch_coingecko, CoinGeckoTimeout
from .services.email_service import EmailService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_verification_email_task(self, email, username, verification_url):
    """
    Background task to render and send account verification emails.
    Retries up to 3 times with exponential backoff on SMTP/network failures.
    """
    try:
        EmailService.send_verification_email(email, username, verification_url)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_password_reset_email_task(self, email, username, reset_url):
    """
    Background task to render and send password reset emails.
    Retries up to 3 times with exponential backoff on SMTP/network failures.
    """
    try:
        EmailService.send_password_reset_email(email, username, reset_url)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    autoretry_for=(CoinGeckoTimeout, requests.RequestException),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
)
def sync_coingecko_market_data(self):
    """
    Background task to fetch live cryptocurrency market data from CoinGecko API
    and perform batch database updates using a single atomic transaction.
    Catches network timeouts/errors and handles task retries with exponential backoff.
    """
    response = fetch_coingecko(settings.COINGECKO_API_URL, params={
        "vs_currency": "usd",
        "order_by": "market_cap_rank_asc",
        "per_page": 250,
        "page": 1,
        "sparkline": True,
    })
    response.raise_for_status()
    coins_list = response.json()

    if not isinstance(coins_list, list):
        return {"status": "error", "message": "Invalid response format from CoinGecko"}

    # Prepare data for batch database operations
    existing_coins = {coin.ticker: coin for coin in Coin.objects.all()}
    coins_to_create = []
    coins_to_update = []

    for coin_data in coins_list:
        if not isinstance(coin_data, dict):
            continue

        symbol = coin_data.get('symbol')
        name = coin_data.get('name')
        if not symbol or not name:
            continue

        ticker = symbol.upper()
        price = coin_data.get('current_price') if coin_data.get('current_price') is not None else 0
        volume = coin_data.get('total_volume') if coin_data.get('total_volume') is not None else 0
        last_updated = coin_data.get('last_updated') or timezone.now()
        price_change = coin_data.get('price_change_percentage_24h') if coin_data.get('price_change_percentage_24h') is not None else 0
        market_cap_rank = coin_data.get('market_cap_rank')
        image = coin_data.get('image') or ''

        if ticker in existing_coins:
            coin = existing_coins[ticker]
            coin.coin_name = name
            coin.price = price
            coin.market_volume = volume
            coin.last_updated_at = last_updated
            coin.market_cap_rank = market_cap_rank
            coin.price_change_24h = price_change
            coin.image = image
            coins_to_update.append(coin)
        else:
            coins_to_create.append(
                Coin(
                    ticker=ticker,
                    coin_name=name,
                    price=price,
                    market_volume=volume,
                    last_updated_at=last_updated,
                    market_cap_rank=market_cap_rank,
                    price_change_24h=price_change,
                    image=image,
                )
            )

    # Perform batch database updates using a single atomic transaction
    with transaction.atomic():
        if coins_to_create:
            Coin.objects.bulk_create(coins_to_create, ignore_conflicts=True)
        if coins_to_update:
            Coin.objects.bulk_update(
                coins_to_update,
                fields=['coin_name', 'price', 'market_volume', 'last_updated_at', 'market_cap_rank', 'price_change_24h', 'image']
            )

    # Invalidate cached coin list pages instead of flushing the entire Redis instance
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern("coin_list_*")
        else:
            # Fallback for default cache backend: clear known page ranges and sizes
            keys_to_delete = [
                f"coin_list_page_{page}_size_{size}"
                for page in range(1, 20)
                for size in (10, 25, 50, 100)
            ]
            if hasattr(cache, 'delete_many'):
                cache.delete_many(keys_to_delete)
            else:
                for key in keys_to_delete:
                    cache.delete(key)
    except Exception as cache_err:
        logger.warning("Failed to clear coin list cache after market sync: %s", cache_err)

    return {
        "status": "success",
        "created": len(coins_to_create),
        "updated": len(coins_to_update),
    }