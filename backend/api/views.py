import smtplib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.shortcuts import redirect
from django.core.cache import cache
from django.db.models import Q
from .models import Coin, User, Watchlist, WatchlistItem
from .serializers import (
    UserSerializer, CoinSerializer, WatchlistSerializer, WatchlistItemDetailSerializer,
    RegisterRequestSerializer, LoginRequestSerializer, ProfileUpdateRequestSerializer,
    EmailRequestSerializer, PasswordResetConfirmRequestSerializer, RefreshTokenRequestSerializer,
    WatchlistNameRequestSerializer, WatchlistCoinRequestSerializer, UserScopedRequestSerializer,
    ErrorResponseSerializer, MessageResponseSerializer, TokenResponseSerializer,
    WatchlistResponseSerializer, WatchlistListResponseSerializer, WatchlistItemsResponseSerializer,
    MembershipResponseSerializer, ChartResponseSerializer,
)
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from email.message import EmailMessage
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string
from .paginations import get_pagination_params, build_paginated_response
from .helpers import get_signed_payload, normalize_email_value, normalize_username_value

# Constants for CoinGecko API access
COINGECKO_API_URL = settings.COINGECKO_API_URL
COINGECKO_CHART_URL = settings.COINGECKO_CHART_URL
COINGECKO_SEARCH_URL = settings.COINGECKO_SEARCH_URL
HEADERS = {
    "x-cg-demo-api-key": settings.COINGECKO_API_KEY
}
COINGECKO_TIMEOUT = (3, 10)


class CoinGeckoTimeout(Exception):
    """Raised when CoinGecko does not respond within the configured timeout."""


def fetch_coingecko(url, params=None):
    retry_strategy = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.5,
        status_forcelist=(429, 502, 503, 504),
        allowed_methods=frozenset({'GET'}),
        # Keep retry delays bounded so an upstream header cannot block a worker indefinitely.
        respect_retry_after_header=False,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as session:
        session.mount('https://', adapter)
        try:
            return session.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=COINGECKO_TIMEOUT,
            )
        except requests.Timeout as error:
            raise CoinGeckoTimeout from error


def send_email_message(to_email, subject, text_body, html_content=None):
    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = settings.DEFAULT_FROM_EMAIL
    message['To'] = to_email
    message.set_content(text_body)

    if html_content:
        message.add_alternative(html_content, subtype='html')

    smtp_host = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    smtp_username = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD
    use_tls = settings.EMAIL_USE_TLS
    use_ssl = settings.EMAIL_USE_SSL

    if use_ssl:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if use_tls:
                server.starttls()
            if smtp_username and smtp_password:
                server.login(smtp_username, smtp_password)
            server.send_message(message)


# Function to send verification email using SMTP
def send_verification_email(to_email, username, verification_url):
    html_content = render_to_string('api/emails/verify_email.html', {
        'user': {'first_name': username},
        'verification_url': verification_url,
    })

    send_email_message(
        to_email,
        'Verify your PREX account',
        f'Hi {username}, verify your email: {verification_url}',
        html_content,
    )


def send_password_reset_email(to_email, username, reset_url):
    html_content = render_to_string('api/emails/reset_password.html', {
        'username': username,
        'reset_password_url': reset_url,
    })

    send_email_message(
        to_email,
        'Reset your PREX password',
        f'Hi {username}, reset your password: {reset_url}',
        html_content,
    )


# Simple view to test the API endpoint
@extend_schema(tags=['system'], responses={200: MessageResponseSerializer})
@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(tags=['system'], responses={200: MessageResponseSerializer})
def home(request):
    return Response({
        'message': 'Welcome to the PREX API!'
        })

def refresh_user_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    }


def build_error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({'error': message}, status=status_code)


def parse_request_data(request):
    if request.data is None:
        return {}

    if not isinstance(request.data, dict):
        raise ValueError('Request body must be valid JSON.')

    return request.data


def validate_request_data(request, serializer_class):
    try:
        data = parse_request_data(request)
    except ValueError as error:
        return None, build_error_response(str(error))

    serializer = serializer_class(data=data)
    if not serializer.is_valid():
        messages = []
        for field_errors in serializer.errors.values():
            messages.extend(str(error) for errors in field_errors for error in (errors if isinstance(errors, list) else [errors]))
        return None, build_error_response(' '.join(messages))

    return serializer.validated_data, None


def build_user_update_payload(data):
    allowed_fields = {'first_name', 'last_name', 'username'}
    invalid_fields = set(data.keys()) - allowed_fields
    if invalid_fields:
        raise ValueError(f'Invalid field(s): {", ".join(sorted(invalid_fields))}.')

    payload = {}

    first_name = str(data.get('first_name', '')).strip()
    last_name = str(data.get('last_name', '')).strip()
    username = normalize_username_value(data.get('username'))

    if 'first_name' in data and first_name:
        payload['first_name'] = first_name

    if 'last_name' in data and last_name:
        payload['last_name'] = last_name

    if 'username' in data:
        if not username:
            raise ValueError('username cannot be empty.')
        payload['username'] = username

    return payload


def validate_authenticated_user_scope(request, user_id):
    if str(request.user.id) != str(user_id):
        return build_error_response(
            'You do not have permission to update this user.',
            status.HTTP_403_FORBIDDEN
        )

    return None


def resolve_coin_gecko_id(coin_id):
    normalized_coin_id = str(coin_id).strip()
    if not normalized_coin_id:
        return None

    local_coin = Coin.objects.filter(ticker__iexact=normalized_coin_id).first()
    if local_coin:
        normalized_coin_id = local_coin.coin_name.strip()

    try:
        response = fetch_coingecko(COINGECKO_SEARCH_URL, params={'query': normalized_coin_id})
        response.raise_for_status()
        payload = response.json()
    except CoinGeckoTimeout:
        raise
    except (requests.RequestException, ValueError):
        return None

    coins = payload.get('coins', [])
    if not coins:
        return None

    search_key = normalized_coin_id.upper()
    for candidate in coins:
        if candidate.get('id', '').strip().lower() == normalized_coin_id.lower():
            return candidate.get('id')
        if candidate.get('symbol', '').upper() == search_key:
            return candidate.get('id')

    for candidate in coins:
        if candidate.get('name', '').strip().lower() == normalized_coin_id.lower():
            return candidate.get('id')

    return coins[0].get('id')


# View to fetch the latest coin data from the CoinGecko API and update the database accordingly.
@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=25),
    ],
    responses={200: OpenApiResponse(description='Paginated coin market data.'), 502: ErrorResponseSerializer, 504: ErrorResponseSerializer},
)
def coin_list(request):
    try:
        print(f"Fetching Coin Data")
        response = fetch_coingecko(COINGECKO_API_URL, params={
            "vs_currency": "usd",
            "order_by": "market_cap_rank_asc",
            "per_page": 250,
            "page": 1,
            "sparkline": True
        })
        response.raise_for_status()
        print(f"Coin Data fetched successfully!")

    except CoinGeckoTimeout:
        return build_error_response(
            'Coin data service timed out. Please try again later.',
            status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.RequestException:
        return build_error_response(
            'Unable to fetch live coin data right now. Please try again later.',
            status.HTTP_502_BAD_GATEWAY
        ) 

    try:
        data = response.json()
    except ValueError:
        return build_error_response(
            'Coin data service returned an invalid response.',
            status.HTTP_502_BAD_GATEWAY
        )

    try:
        for coin_data in data:
            Coin.objects.update_or_create(
                ticker=coin_data['symbol'].upper(),
                defaults={
                    'coin_name': coin_data['name'],
                    'price': coin_data['current_price'],
                    'market_volume': coin_data['total_volume'],
                    'last_updated_at': coin_data['last_updated'],
                    'market_cap_rank': coin_data['market_cap_rank'],
                    'price_change_24h': coin_data.get('price_change_percentage_24h') or 0,
                }
            )
    except (KeyError, TypeError, ValueError):
        return build_error_response(
            'Coin data is missing expected fields.',
            status.HTTP_502_BAD_GATEWAY
        )
    Coin.objects.filter(market_cap_rank__isnull=True).delete()  # Remove coins without a market cap rank
    coins = Coin.objects.all().order_by('market_cap_rank', 'ticker')

    page, page_size = get_pagination_params(request)
    return build_paginated_response(CoinSerializer, coins, page, page_size)


# view to get the chart data with time from the CoinGecko API
@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('days', int, OpenApiParameter.QUERY, default=7),
    ],
    responses={200: ChartResponseSerializer, 404: ErrorResponseSerializer, 502: ErrorResponseSerializer, 504: ErrorResponseSerializer},
)
def get_chart_data(request, coin_id=None):
    try: 
        print("fetching chart data from CoinGecko API.")
        coin_id = coin_id or request.query_params.get('coin_id')
        try:
            days = int(request.query_params.get('days', 7))
        except (TypeError, ValueError):
            days = 7

        resolved_coin_id = resolve_coin_gecko_id(coin_id)
        if not resolved_coin_id:
            return build_error_response(
                'Unable to resolve the requested coin for chart data.',
                status.HTTP_404_NOT_FOUND
            )

        cache_key = f"coin_chart:{resolved_coin_id}:{days}"
        cached_chart = cache.get(cache_key)
        if cached_chart:
            return Response(cached_chart)

        response = fetch_coingecko(f"{COINGECKO_CHART_URL}{resolved_coin_id}/market_chart", params={
            "vs_currency": "usd",
            "days": days,
            "interval": "hourly",
            "precision": 4,
            "sparkline": True
        })
        response.raise_for_status()
        data = response.json()
        prices = data.get('prices', [])
        if not prices:
            return build_error_response(
                'No chart data available for the specified coin.',
                status.HTTP_404_NOT_FOUND
            )

        print(f"Chart data fetched successfully for coin_id: {resolved_coin_id}, {len(prices)} data points retrieved.")

        payload = {
            'success': True,
            'coin_id': resolved_coin_id,
            'chart_data': [{'timestamp': ts, 'price': price} for ts, price in prices]
        }
        cache.set(cache_key, payload, timeout=300)
        return Response(payload)
    except CoinGeckoTimeout:
        return build_error_response(
            'Chart data service timed out. Please try again later.',
            status.HTTP_504_GATEWAY_TIMEOUT
        )
    except requests.RequestException:
        return build_error_response(
            'Unable to fetch live chart data right now. Please try again later.',
            status.HTTP_502_BAD_GATEWAY
        )


# View to handle user registration, including validation, password hashing, 
# and sending a verification email.
@api_view(['POST'])
@permission_classes([AllowAny])
@extend_schema(tags=['auth'], request=RegisterRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 502: ErrorResponseSerializer})
def register_user(request):
    data, error_response = validate_request_data(request, RegisterRequestSerializer)
    if error_response:
        return error_response

    username = normalize_username_value(data['username'])
    dob = data['dob']
    email = normalize_email_value(data['email'])
    password = data['password']

    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        if existing_user.email_confirmed:
            return build_error_response('Email already exists.')
        else:
            token = signing.dumps(
                {'email': existing_user.email},
                salt=settings.EMAIL_VERIFICATION_SALT,
            )
            verification_url = request.build_absolute_uri(
                reverse('verify_email', kwargs={'token': token})
            )
            try:
                print(f"Sending Re-Verification mail to {existing_user.email}")
                send_verification_email(existing_user.email, existing_user.username, verification_url)
                print(f"Re-verification mail sent to {existing_user.email}")
            except smtplib.SMTPException as error:
                return build_error_response(
                    f'Could not send verification email: {error}',
                    status.HTTP_502_BAD_GATEWAY
                )

            return Response({
                'message': 'Verification email resent. Verify your email to complete registration.'
            }, status=status.HTTP_200_OK)

    if User.objects.filter(username=username).exists():
        return build_error_response('Username already exists.')

    # Create inactive user with verified password (user must verify email to activate)
    User.objects.create_user(
        username=username,
        dob=dob,
        email=email,
        password=password,
        email_confirmed=False,
    )

    # Token contains only email for verification (no password hash)
    token = signing.dumps(
        {'email': email},
        salt=settings.EMAIL_VERIFICATION_SALT,
    )
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )

    try:
        print(f"Sending Verification mail to {email}")
        send_verification_email(email, username, verification_url)
        print(f"Verification mail sent to {email}")
    except smtplib.SMTPException as error:
        # Delete the user if email sending fails
        User.objects.filter(email=email).delete()
        return build_error_response(
            f'Could not send verification email: {error}',
            status.HTTP_502_BAD_GATEWAY
        )

    return Response({
        'message': 'Verification email sent. Verify your email to complete registration.'
        })


#view to update user info through profile page.
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['auth'], request=ProfileUpdateRequestSerializer, responses={200: UserSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 409: ErrorResponseSerializer})
def update_user(request, user_id):
    permission_error = validate_authenticated_user_scope(request, user_id)
    if permission_error:
        return permission_error

    data, error_response = validate_request_data(request, ProfileUpdateRequestSerializer)
    if error_response:
        return error_response

    payload = build_user_update_payload(data)

    if not payload:
        return build_error_response('Please provide at least one field to update.')

    user = request.user
    if 'username' in payload and User.objects.filter(username=payload['username']).exclude(id=user.id).exists():
        return build_error_response(
            'username already exists, try a new one.',
            status.HTTP_409_CONFLICT
        )

    for field, value in payload.items():
        setattr(user, field, value)

    try:
        user.save(update_fields=[*payload.keys(), 'updated_at'])
    except Exception:
        return build_error_response(
            'Unable to update your profile right now. Please try again later.',
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response({
        'success': True,
        'message': 'Profile updated successfully.',
        'user': UserSerializer(user).data
    })


# View to handle email verification when the user clicks the link in the verification email, 
# activating the user account.
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        print(f"Retrieving data from the payload")
        payload = get_signed_payload(
            token,
            settings.EMAIL_VERIFICATION_SALT,
            settings.EMAIL_VERIFICATION_MAX_AGE_SECONDS,
        )
        print(f"Payload retrieved successfully!")
    except ValueError as error:
        return build_error_response(str(error))

    email = normalize_email_value(payload.get('email'))
    if not email:
        return build_error_response('Invalid verification link.')

    user = User.objects.filter(email=email).first()
    if not user:
        return build_error_response('User not found. Please register again.', status.HTTP_404_NOT_FOUND)

    if user.email_confirmed:
        return redirect(settings.EMAIL_VERIFICATION_SUCCESS_URL)  # Redirect to a frontend page if already verified

    # Activate user account
    user.email_confirmed = True
    user.updated_at = timezone.now()
    user.save(update_fields=['email_confirmed', 'updated_at'])
    print(f"You have been verified successfully, Congratulations!")

    return redirect(settings.EMAIL_VERIFICATION_SUCCESS_URL)  # Redirect to a frontend page after successful verification


# View to handle user login, including credential validation, 
# token generation, and returning user information.
@api_view(['POST'])
@permission_classes([AllowAny])
@extend_schema(tags=['auth'], request=LoginRequestSerializer, responses={200: TokenResponseSerializer, 400: ErrorResponseSerializer, 401: ErrorResponseSerializer, 403: ErrorResponseSerializer})
def user_login(request):
    data, error_response = validate_request_data(request, LoginRequestSerializer)
    if error_response:
        return error_response

    email = normalize_email_value(data['email'])
    password = data['password']

    user = User.objects.filter(email=email).first()

    if not user or not user.check_password(password):
        return build_error_response('Invalid email or password.', status.HTTP_401_UNAUTHORIZED)

    if not user.email_confirmed:
        return build_error_response(
            'Email not verified. Please verify your email before logging in.',
            status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)
    refresh_token = str(refresh)
    access_token = str(refresh.access_token)

    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    user_serializer = UserSerializer(user)
    return Response({
        'status': 200,
        'success': True,
        'message': f'Login Successful, Welcome back {user.username}!',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_serializer.data
    })


# View to retrieve the current authenticated user's information, 
# ensuring that the user is authenticated and returning relevant user details.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['auth'], responses={200: UserSerializer, 401: ErrorResponseSerializer})
def current_user(request):
    user = request.user
    return Response({
        'user': UserSerializer(user).data
    })


# View to handle reset password request, including sending a password reset email with a secure token.
@api_view(['POST'])
@permission_classes([AllowAny])
@extend_schema(tags=['auth'], request=EmailRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 502: ErrorResponseSerializer})
def reset_password(request):
    data, error_response = validate_request_data(request, EmailRequestSerializer)
    if error_response:
        return error_response

    email = normalize_email_value(data['email'])

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"message": "If email exists, reset instructions sent."})

    token = signing.dumps(
        {'email': user.email},
        salt=settings.PASSWORD_RESET_SALT,
    )
    reset_url = request.build_absolute_uri(
        reverse('reset_password_confirm', kwargs={'token': token})
    )

    try:
        print(f"Sending Password reset mail to {email}")
        send_password_reset_email(email, user.username, reset_url)
        print(f"Password reset mail sent to {email}")
    except smtplib.SMTPException:
        return build_error_response('Failed to send password reset email.', status.HTTP_502_BAD_GATEWAY)

    return Response({
        'success': True,
        'message': f'Password reset instructions sent to {email}.'
        })


# View to handle password reset confirmation, including validating the token, 
# checking the new password against validation rules, and updating the user's password.
@api_view(['POST'])
@permission_classes([AllowAny])
@extend_schema(tags=['auth'], request=PasswordResetConfirmRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer})
def reset_password_confirm(request, token):
    data, error_response = validate_request_data(request, PasswordResetConfirmRequestSerializer)
    if error_response:
        return error_response

    try:
        payload = get_signed_payload(
            token,
            settings.PASSWORD_RESET_SALT,
            settings.PASSWORD_RESET_MAX_AGE_SECONDS,
        )
    except ValueError as error:
        return build_error_response(str(error))

    user = User.objects.filter(email=normalize_email_value(payload.get('email'))).first()
    if not user:
        return build_error_response('Invalid password reset link.')

    new_password = data['new_password']

    if user.check_password(new_password):
        return build_error_response('New password cannot be the same as the old password.')

    user.set_password(new_password)
    user.updated_at = timezone.now()
    user.save(update_fields=['password', 'updated_at'])

    return Response({
        'success': True,
        'message': 'Password reset successfully.'
        })


# View to handle user logout by blacklisting the refresh token, 
# ensuring that it cannot be used to generate new access tokens.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['auth'], request=RefreshTokenRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer})
def user_logout(request):
    data, error_response = validate_request_data(request, RefreshTokenRequestSerializer)
    if error_response:
        return error_response

    refresh_token = data['refresh_token']

    try:
        token = RefreshToken(refresh_token)

        if str(token['user_id']) != str(request.user.id):
            return build_error_response(
                'You do not have permission to revoke this session.',
                status.HTTP_403_FORBIDDEN
            )

        token.blacklist()

        return Response({
            'success': True,
            'message': 'Logout successful.'
        })

    except TokenError:
        return build_error_response('Invalid refresh token.')


# View to retrieve all watchlists for a specific user, 
# ensuring that the requesting user has permission to view the watchlists 
# and returning the watchlist data in a structured format.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], responses={200: WatchlistListResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
def user_watchlists(request, user_id):
    if str(request.user.id) != str(user_id):
        return build_error_response(
            'You do not have permission to view this user\'s watchlists.',
            status.HTTP_403_FORBIDDEN
        )
    
    user = User.objects.filter(id=user_id).first()
    if not user: 
        return build_error_response('User not found.', status.HTTP_404_NOT_FOUND)
    
    watchlists = user.watchlists.all()
    if not watchlists:
        return Response({
            'success': True,
            'message': 'No watchlists found for this user. Create a watchlist to get started.',
            'watchlists': []
        })
    
    serializer = WatchlistSerializer(watchlists, many=True)
    return Response({
        'success': True,
        'watchlists': serializer.data
    })


# View to create a new watchlist for the authenticated user, 
# including validation to ensure that the watchlist name is provided and unique for the user, 
# and returning the created watchlist data upon success.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], request=WatchlistNameRequestSerializer, responses={201: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 409: ErrorResponseSerializer})
def create_watchlist(request):
    user = request.user

    data, error_response = validate_request_data(request, WatchlistNameRequestSerializer)
    if error_response:
        return error_response

    watchlist_name = data['name']

    if user.watchlists.filter(name=watchlist_name).exists():
        return build_error_response('A watchlist with this name already exists.', status.HTTP_409_CONFLICT)

    watchlist = user.watchlists.create(name=watchlist_name)
    serializer = WatchlistSerializer(watchlist)

    return Response({
        'success': True,
        'message': f'Watchlist {watchlist_name} created successfully.',
        'watchlist': serializer.data
    }, status=status.HTTP_201_CREATED)


# View to add a coin to a user's watchlist, including permission checks,
# validating the existence of the user, watchlist, and coin, and ensuring that the coin
# is not already in the watchlist before adding it.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], request=WatchlistCoinRequestSerializer, responses={200: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer, 409: ErrorResponseSerializer})
def add_coin_to_watchlist(request):
    data, error_response = validate_request_data(request, WatchlistCoinRequestSerializer)
    if error_response:
        return error_response

    user_id = data['user_id']
    if str(request.user.id) != str(user_id):
        return build_error_response(
            'You do not have permission to modify this user\'s watchlists.',
            status.HTTP_403_FORBIDDEN
        )
    
    user = User.objects.filter(id=user_id).first()

    if not user:
        return build_error_response('User not found.', status.HTTP_404_NOT_FOUND)
    
    watchlist_id = data['watchlist_id']
    
    watchlist = user.watchlists.filter(id=watchlist_id).first()
    if not watchlist:
        return build_error_response('Watchlist not found.', status.HTTP_404_NOT_FOUND)
    
    ticker = data['ticker'].upper()
    
    coin = Coin.objects.filter(ticker=ticker).first()
    if not coin:
        return build_error_response('Coin not found.', status.HTTP_404_NOT_FOUND)
    
    if watchlist.items.filter(ticker=coin).exists():
        return build_error_response('Coin is already in the watchlist.', status.HTTP_409_CONFLICT)
    
    watchlist.items.create(ticker=coin)
    serializer = WatchlistSerializer(watchlist)
    return Response({
        'success': True,
        'message': f'{coin.coin_name} ({coin.ticker}) added to watchlist {watchlist.name}.',
        'watchlist': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], request=WatchlistCoinRequestSerializer, responses={200: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
def remove_coin_from_watchlist(request):
    data, error_response = validate_request_data(request, WatchlistCoinRequestSerializer)
    if error_response:
        return error_response

    user_id = data['user_id']
    if str(request.user.id) != str(user_id):
        return build_error_response(
            'You do not have permission to modify this user\'s watchlists.',
            status.HTTP_403_FORBIDDEN
        )
    
    user = User.objects.filter(id=user_id).first()

    if not user:
        return build_error_response('User not found.', status.HTTP_404_NOT_FOUND)
    
    watchlist_id = data['watchlist_id']
    
    watchlist = user.watchlists.filter(id=watchlist_id).first()
    if not watchlist:
        return build_error_response('Watchlist not found.', status.HTTP_404_NOT_FOUND)
    
    ticker = data['ticker'].upper()
    
    coin = Coin.objects.filter(ticker=ticker).first()
    if not coin:
        return build_error_response('Coin not found.', status.HTTP_404_NOT_FOUND)
    
    item = watchlist.items.filter(ticker=coin).first()
    if not item:
        return build_error_response('Coin is not in the watchlist.', status.HTTP_404_NOT_FOUND)
    
    item.delete()
    serializer = WatchlistSerializer(watchlist)
    return Response({
        'success': True,
        'message': f'{coin.coin_name} ({coin.ticker}) removed from watchlist {watchlist.name}.',
        'watchlist': serializer.data
    })


# View to retrieve all coins in a specific watchlist, 
# including permission checks and returning the coin data in a structured format.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], responses={200: WatchlistItemsResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
def show_watchlist_items(request, watchlist_id):
    watchlist_id = request.query_params.get('watchlist_id') or watchlist_id
    if not watchlist_id:
        return build_error_response('Watchlist ID is required to view watchlist items.')
    
    watchlist = Watchlist.objects.filter(id=watchlist_id).first()

    if not watchlist:
        return build_error_response('Watchlist not found.', status.HTTP_404_NOT_FOUND)

    if watchlist.user_id != request.user.id:
        return build_error_response('You do not have permission to view this watchlist.', status.HTTP_403_FORBIDDEN)
    
    items = watchlist.items.select_related('ticker').all()
    serializer = WatchlistItemDetailSerializer(items, many=True)

    return Response({
        'success': True,
        'watchlist': watchlist.name,
        'items': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], responses={200: MembershipResponseSerializer, 404: ErrorResponseSerializer})
def coin_watchlist_membership(request, ticker):
    """Return all watchlists (and item ids) for the authenticated user that contain the given coin ticker."""
    if not ticker:
        return build_error_response('Ticker is required.', status.HTTP_400_BAD_REQUEST)

    ticker = ticker.upper()
    coin = Coin.objects.filter(ticker=ticker).first()
    if not coin:
        return build_error_response('Coin not found.', status.HTTP_404_NOT_FOUND)

    items = WatchlistItem.objects.filter(watchlist__user=request.user, ticker=coin).select_related('watchlist')

    membership = []
    for item in items:
        membership.append({
            'item_id': item.id,
            'watchlist_id': item.watchlist.id,
            'watchlist_name': item.watchlist.name,
            'added_at': item.added_at,
        })

    return Response({
        'success': True,
        'membership': membership,
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@extend_schema(tags=['watchlists'], request=UserScopedRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
def delete_watchlist(request, watchlist_id):
    data, error_response = validate_request_data(request, UserScopedRequestSerializer)
    if error_response:
        return error_response

    user_id = data['user_id']
    if str(request.user.id) != str(user_id):
        return build_error_response(
            'You do not have permission to modify this user\'s watchlists.',
            status.HTTP_403_FORBIDDEN
        )

    user = User.objects.filter(id=user_id).first()

    if not user:
        return build_error_response('User not found.', status.HTTP_404_NOT_FOUND)

    watchlist = user.watchlists.filter(id=watchlist_id).first()
    if not watchlist:
        return build_error_response('Watchlist not found.', status.HTTP_404_NOT_FOUND)
    
    watchlist.delete()
    return Response({
        'success': True,
        'message': f'Watchlist {watchlist.name} with {watchlist_id} has been deleted successfully.'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=10),
    ],
    responses={200: OpenApiResponse(description='Paginated matching coin data.'), 400: ErrorResponseSerializer},
)
def search_coins(request, coin_id):
    query = coin_id.strip()

    coins = Coin.objects.filter(
        Q(ticker=query.upper()) | Q(coin_name__iexact=query)
    ).distinct().order_by('market_cap_rank', 'ticker')

    if not coins.exists():
        return Response({
            'success': True,
            'message': 'No coins found matching the search query.',
            'page': 1,
            'page_size': 25,
            'total_count': 0,
            'total_pages': 0,
            'results': []
        })

    page, page_size = get_pagination_params(request)
    return build_paginated_response(
        CoinSerializer,
        coins,
        page,
        page_size,
        extra_data={'message': 'Coins found matching the search query.'}
    )


@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(tags=['system'], responses={200: MessageResponseSerializer})
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'PREX API is healthy and running.'
    })


# Apply schema metadata after DRF converts function views into API views.
# This keeps the existing function-based implementation and route behavior.
home = extend_schema(tags=['system'], responses={200: MessageResponseSerializer})(home)
coin_list = extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=25),
    ],
    responses={200: OpenApiResponse(description='Paginated coin market data.'), 502: ErrorResponseSerializer, 504: ErrorResponseSerializer},
)(coin_list)
get_chart_data = extend_schema(
    tags=['market'],
    parameters=[OpenApiParameter('days', int, OpenApiParameter.QUERY, default=7)],
    responses={200: ChartResponseSerializer, 404: ErrorResponseSerializer, 502: ErrorResponseSerializer, 504: ErrorResponseSerializer},
)(get_chart_data)
search_coins = extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=10),
    ],
    responses={200: OpenApiResponse(description='Paginated matching coin data.'), 400: ErrorResponseSerializer},
)(search_coins)
register_user = extend_schema(tags=['auth'], request=RegisterRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 502: ErrorResponseSerializer})(register_user)
update_user = extend_schema(tags=['auth'], request=ProfileUpdateRequestSerializer, responses={200: UserSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 409: ErrorResponseSerializer})(update_user)
user_login = extend_schema(tags=['auth'], request=LoginRequestSerializer, responses={200: TokenResponseSerializer, 400: ErrorResponseSerializer, 401: ErrorResponseSerializer, 403: ErrorResponseSerializer})(user_login)
current_user = extend_schema(tags=['auth'], responses={200: UserSerializer, 401: ErrorResponseSerializer})(current_user)
reset_password = extend_schema(tags=['auth'], request=EmailRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 502: ErrorResponseSerializer})(reset_password)
reset_password_confirm = extend_schema(tags=['auth'], request=PasswordResetConfirmRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer})(reset_password_confirm)
user_logout = extend_schema(tags=['auth'], request=RefreshTokenRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer})(user_logout)
verify_email = extend_schema(tags=['auth'], responses={302: OpenApiResponse(description='Redirects to the configured frontend success URL.'), 400: ErrorResponseSerializer, 404: ErrorResponseSerializer})(verify_email)
user_watchlists = extend_schema(tags=['watchlists'], responses={200: WatchlistListResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})(user_watchlists)
create_watchlist = extend_schema(tags=['watchlists'], request=WatchlistNameRequestSerializer, responses={201: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 409: ErrorResponseSerializer})(create_watchlist)
add_coin_to_watchlist = extend_schema(tags=['watchlists'], request=WatchlistCoinRequestSerializer, responses={200: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer, 409: ErrorResponseSerializer})(add_coin_to_watchlist)
remove_coin_from_watchlist = extend_schema(tags=['watchlists'], request=WatchlistCoinRequestSerializer, responses={200: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})(remove_coin_from_watchlist)
show_watchlist_items = extend_schema(tags=['watchlists'], responses={200: WatchlistItemsResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})(show_watchlist_items)
coin_watchlist_membership = extend_schema(tags=['watchlists'], responses={200: MembershipResponseSerializer, 404: ErrorResponseSerializer})(coin_watchlist_membership)
delete_watchlist = extend_schema(tags=['watchlists'], request=UserScopedRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})(delete_watchlist)
health_check = extend_schema(tags=['system'], responses={200: MessageResponseSerializer})(health_check)
