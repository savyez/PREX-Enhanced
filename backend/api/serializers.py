from rest_framework import serializers
from .models import User, Coin, Watchlist, WatchlistItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'dob', 'email', 'email_confirmed']
        read_only_fields = ['id']


class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coin
        fields = ['ticker', 'coin_name', 'price', 'market_volume', 'last_updated_at', 'market_cap_rank', 'price_change_24h']


class WatchlistItemDetailSerializer(serializers.ModelSerializer):
    ticker = CoinSerializer(read_only=True)

    class Meta:
        model = WatchlistItem
        fields = ['id', 'ticker', 'added_at']


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = ['id', 'watchlist', 'ticker', 'added_at']
