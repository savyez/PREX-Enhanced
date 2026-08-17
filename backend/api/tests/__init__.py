from .base import BaseAPITestCase
from .test_system import SystemEndpointTests
from .test_auth import (
    AuthRegistrationTests,
    AuthLoginLogoutTests,
    AuthPasswordResetTests,
    UserProfileTests,
)
from .test_market import (
    MarketCoinListTests,
    MarketSearchTests,
    MarketChartTests,
    MarketCeleryTaskTests,
)
from .test_watchlist import WatchlistManagementTests
from .test_services import (
    CoinGeckoServiceTests,
    AuthServiceTests,
    EmailServiceTests,
)

__all__ = [
    'BaseAPITestCase',
    'SystemEndpointTests',
    'AuthRegistrationTests',
    'AuthLoginLogoutTests',
    'AuthPasswordResetTests',
    'UserProfileTests',
    'MarketCoinListTests',
    'MarketSearchTests',
    'MarketChartTests',
    'MarketCeleryTaskTests',
    'WatchlistManagementTests',
    'CoinGeckoServiceTests',
    'AuthServiceTests',
    'EmailServiceTests',
]
