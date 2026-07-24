from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from .models import User, Coin, Watchlist, WatchlistItem


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, trim_whitespace=True)
    dob = serializers.DateField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(' '.join(error.messages)) from error
        return value


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)


class ProfileUpdateRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=False)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=False)
    username = serializers.CharField(max_length=150, required=False, allow_blank=False)


class EmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmRequestSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_new_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError('New password and confirm new password do not match.')
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as error:
            raise serializers.ValidationError(' '.join(error.messages)) from error
        return attrs


class RefreshTokenRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(trim_whitespace=True)


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=True)


class WatchlistNameRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, trim_whitespace=True)


class WatchlistCoinRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    watchlist_id = serializers.IntegerField(min_value=1)
    ticker = serializers.CharField(max_length=16, trim_whitespace=True)


class UserScopedRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


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


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class MessageResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(required=False)
    message = serializers.CharField()


class TokenResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    success = serializers.BooleanField()
    message = serializers.CharField()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserSerializer()


class WatchlistResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    watchlist = WatchlistSerializer()


class WatchlistListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    watchlists = WatchlistSerializer(many=True)


class WatchlistItemsResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    watchlist = serializers.CharField()
    items = WatchlistItemDetailSerializer(many=True)


class MembershipSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    watchlist_id = serializers.IntegerField()
    watchlist_name = serializers.CharField()
    added_at = serializers.DateTimeField()


class MembershipResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    membership = MembershipSerializer(many=True)


class ChartPointSerializer(serializers.Serializer):
    timestamp = serializers.IntegerField()
    price = serializers.FloatField()


class ChartResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    coin_id = serializers.CharField()
    chart_data = ChartPointSerializer(many=True)
