from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('coins/', views.coin_list, name='coin_list'),
    path('register/', views.register_user, name='register_user'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('watchlists/<str:user_id>/', views.user_watchlists, name='user_watchlists'),
]
