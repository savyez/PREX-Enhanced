from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.home, name='home'),
    path('coins/', views.coin_list, name='coin_list'),

    # User authentication and management endpoints
    path('register/', views.register_user, name='register_user'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-confirm/<str:token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('logout/', views.user_logout, name='logout_user'),

    # Watchlist management endpoints
    path('watchlists/<str:user_id>/', views.user_watchlists, name='user_watchlists'),
]
