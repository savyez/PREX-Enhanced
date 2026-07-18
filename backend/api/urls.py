from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),
    path('coins/', views.coin_list, name='coin_list'),
    path('coins/search/<str:coin_id>/', views.search_coins, name='search_coins'),
    path('coins/<str:coin_id>/chart/', views.get_chart_data, name='coin_chart'),

    # User authentication and management endpoints
    path('register/', views.register_user, name='register_user'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('current-user/', views.current_user, name='current_user'),
    path('users/<str:user_id>/', views.update_user, name='update_user'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-confirm/<str:token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('logout/', views.user_logout, name='logout_user'),

    # Watchlist management endpoints
    path('watchlists/create/', views.create_watchlist, name='create_watchlist'),
    path('watchlists/add-coin/', views.add_coin_to_watchlist, name='add_coin_to_watchlist'),
    path('watchlists/remove-coin/', views.remove_coin_from_watchlist, name='remove_coin_from_watchlist'),
    path('watchlists/membership/<str:ticker>/', views.coin_watchlist_membership, name='coin_watchlist_membership'),
    path('watchlists/<str:user_id>/', views.user_watchlists, name='user_watchlists'),
    path('watchlists/<str:watchlist_id>/items/', views.show_watchlist_items, name='show_watchlist_items'),
    path('watchlists/<str:watchlist_id>/delete/', views.delete_watchlist, name='delete_watchlist'),
]
