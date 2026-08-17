import smtplib

from .common import (
    build_error_response,
    parse_request_data,
    validate_request_data,
)
from .system_views import (
    HomeView,
    HealthCheckView,
)
from .market_views import (
    CoinListView,
    SearchCoinsView,
    CoinChartView,
    CoinGeckoTimeout,
    fetch_coingecko,
    resolve_coin_gecko_id,
)
from .auth_views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    CustomTokenRefreshView,
    CurrentUserView,
    UpdateUserView,
    ResetPasswordView,
    ResetPasswordConfirmView,
    LogoutView,
    send_email_message,
    send_verification_email,
    send_password_reset_email,
    set_refresh_token_cookie,
    clear_refresh_token_cookie,
    refresh_user_tokens,
)
from .watchlist_views import (
    CreateWatchlistView,
    AddCoinToWatchlistView,
    RemoveCoinFromWatchlistView,
    CoinWatchlistMembershipView,
    UserWatchlistsView,
    WatchlistItemsView,
    DeleteWatchlistView,
)

__all__ = [
    # System views
    'HomeView',
    'HealthCheckView',
    # Market views & helpers
    'CoinListView',
    'SearchCoinsView',
    'CoinChartView',
    'CoinGeckoTimeout',
    'fetch_coingecko',
    'resolve_coin_gecko_id',
    # Auth views & helpers
    'RegisterView',
    'VerifyEmailView',
    'LoginView',
    'CustomTokenRefreshView',
    'CurrentUserView',
    'UpdateUserView',
    'ResetPasswordView',
    'ResetPasswordConfirmView',
    'LogoutView',
    'send_email_message',
    'send_verification_email',
    'send_password_reset_email',
    'set_refresh_token_cookie',
    'clear_refresh_token_cookie',
    'refresh_user_tokens',
    # Watchlist views
    'CreateWatchlistView',
    'AddCoinToWatchlistView',
    'RemoveCoinFromWatchlistView',
    'CoinWatchlistMembershipView',
    'UserWatchlistsView',
    'WatchlistItemsView',
    'DeleteWatchlistView',
    # Common helpers
    'build_error_response',
    'parse_request_data',
    'validate_request_data',
    'smtplib',
]
