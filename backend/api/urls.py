from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('coins/', views.CoinListView.as_view(), name='coin_list'),
    path('coins/search/<str:coin_id>/', views.SearchCoinsView.as_view(), name='search_coins'),
    path('coins/<str:coin_id>/chart/', views.CoinChartView.as_view(), name='coin_chart'),

    # User authentication and management endpoints
    path('register/', views.RegisterView.as_view(), name='register_user'),
    path('verify/<str:token>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('login/', views.LoginView.as_view(), name='login_user'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('current-user/', views.CurrentUserView.as_view(), name='current_user'),
    path('users/<str:user_id>/', views.UpdateUserView.as_view(), name='update_user'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('reset-password-confirm/<str:token>/', views.ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('logout/', views.LogoutView.as_view(), name='logout_user'),

    # Watchlist management endpoints
    path('watchlists/create/', views.CreateWatchlistView.as_view(), name='create_watchlist'),
    path('watchlists/add-coin/', views.AddCoinToWatchlistView.as_view(), name='add_coin_to_watchlist'),
    path('watchlists/remove-coin/', views.RemoveCoinFromWatchlistView.as_view(), name='remove_coin_from_watchlist'),
    path('watchlists/membership/<str:ticker>/', views.CoinWatchlistMembershipView.as_view(), name='coin_watchlist_membership'),
    path('watchlists/<str:user_id>/', views.UserWatchlistsView.as_view(), name='user_watchlists'),
    path('watchlists/<str:watchlist_id>/items/', views.WatchlistItemsView.as_view(), name='show_watchlist_items'),
    path('watchlists/<str:watchlist_id>/delete/', views.DeleteWatchlistView.as_view(), name='delete_watchlist'),
]
