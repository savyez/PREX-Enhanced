from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('coins/', views.coin_list, name='coin_list'),

    # User authentication and management endpoints
    path('register/', views.register_user, name='register_user'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login_user'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-confirm/<str:reset_token>/', views.reset_password_confirm, name='reset_password_confirm'),

    # Watchlist management endpoints
    path('watchlists/<str:user_id>/', views.user_watchlists, name='user_watchlists'),
]
