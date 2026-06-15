from os import name
import smtplib
import requests
from decouple import config
from .models import Coin, User, Watchlist, WatchlistItem
from .serializers import UserSerializer, CoinSerializer, WatchlistSerializer, WatchlistItemDetailSerializer
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from email.message import EmailMessage
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.password_validation import validate_password

# Constants for CoinGecko API access
COINGECKO_API_URL = config('COINGECKO_API_URL')
HEADERS = {
    "x-cg-demo-api-key": config('COINGECKO_API_KEY')
}


def normalize_username(username):
    return username.strip().lower() if username else username


def normalize_email(email):
    return BaseUserManager.normalize_email(email.strip()) if email else email

# Function to send verification email using SMTP
def send_verification_email(to_email, username, verification_url):
    message = EmailMessage()
    message['Subject'] = 'Verify your PREX account'
    message['From'] = settings.DEFAULT_FROM_EMAIL
    message['To'] = to_email
    message.set_content(
        f'Hi {username},\n\n'
        f'Click this link to verify your email:\n{verification_url}\n\n'
        'This link will expire in 10 minutes.'
    )

    smtp_class = smtplib.SMTP_SSL if settings.EMAIL_USE_SSL else smtplib.SMTP
    with smtp_class(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
        if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
            smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        smtp.send_message(message)

def send_password_reset_email(to_email, username, reset_url):
    message = EmailMessage()
    message['Subject'] = 'Reset your PREX password'
    message['From'] = settings.DEFAULT_FROM_EMAIL
    message['To'] = to_email
    message.set_content(
        f'Hi {username},\n\n'
        f'Click this link to reset your password:\n{reset_url}\n\n'
        'This link will expire in 10 minutes.'
    )

    smtp_class = smtplib.SMTP_SSL if settings.EMAIL_USE_SSL else smtplib.SMTP
    with smtp_class(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
        if settings.EMAIL_USE_TLS and not settings.EMAIL_USE_SSL:
            smtp.starttls()
        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        smtp.send_message(message)


# Simple view to test the API endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
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


# View to fetch the latest coin data from the CoinGecko API and update the database accordingly.
@api_view(['GET'])
@permission_classes([AllowAny])
def coin_list(request):
    try:
        response = requests.get(COINGECKO_API_URL, params={
            "vs_currency": "usd",
            "order_by": "market_cap_rank_asc",
            "per_page": 250,
            "page": 1,
            "sparkline": True
        }, headers=HEADERS)
        response.raise_for_status()

    except requests.RequestException as error:
        return Response({
            "error": str(error)
            }, status=status.HTTP_502_BAD_GATEWAY)

    data = response.json()

    for coin_data in data:
        Coin.objects.update_or_create(
            ticker=coin_data['symbol'].upper(),
            defaults={
                'coin_name': coin_data['name'],
                'price': coin_data['current_price'],
                'market_volume': coin_data['total_volume'],
                'last_updated_at': coin_data['last_updated'],
                'market_cap_rank': coin_data['market_cap_rank'],
            }
        )
    coins = Coin.objects.all()
    serializer = CoinSerializer(coins, many=True)
    return Response({
        'success': True,
        'coins': serializer.data
    })


# View to handle user registration, including validation, password hashing, 
# and sending a verification email.
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data

    username = normalize_username(data.get('username'))
    dob = data.get('dob')
    email = normalize_email(data.get('email'))
    password = data.get('password')

    if not all([username, dob, email, password]):
        return Response({
            'error': 'username, dob, email, and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        if existing_user.email_confirmed:
            return Response({
                'error': 'Email already exists.'
                }, status=400)

    # existing but unverified: resend verification email

    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({
            'error': list(e.messages)
        }, status=status.HTTP_400_BAD_REQUEST)

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
        send_verification_email(email, username, verification_url)
    except smtplib.SMTPException as error:
        # Delete the user if email sending fails
        User.objects.filter(email=email).delete()
        return Response({
            'error': f'Could not send verification email: {error}'
            }, status=status.HTTP_502_BAD_GATEWAY)

    return Response({
        'message': 'Verification email sent. Verify your email to complete registration.'
        })


# View to handle email verification when the user clicks the link in the verification email, 
# activating the user account.
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request, token):
    try:
        payload = signing.loads(
            token,
            salt=settings.EMAIL_VERIFICATION_SALT,
            max_age=settings.EMAIL_VERIFICATION_MAX_AGE_SECONDS,
        )
    except signing.SignatureExpired:
        return Response({'error': 'Verification link has expired.'}, status=status.HTTP_400_BAD_REQUEST)
    except signing.BadSignature:
        return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

    email = normalize_email(payload.get('email'))
    if not email:
        return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({'error': 'User not found. Please register again.'}, status=status.HTTP_404_NOT_FOUND)

    if user.email_confirmed:
        return Response({'message': 'Email is already verified.'})

    # Activate user account
    user.email_confirmed = True
    user.updated_at = timezone.now()
    user.save(update_fields=['email_confirmed', 'updated_at'])

    return Response({'message': 'Email verified successfully. You can now login to your account.'})


# View to handle user login, including credential validation, 
# token generation, and returning user information.
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = normalize_username(request.data.get('username'))
    email = normalize_email(request.data.get('email'))
    password = request.data.get('password')

    if not all([username, email, password]):
        return Response({
            'error': 'Username, email, and password are required for login.'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username=username, email=email).first()

    if not user or not user.check_password(password):
        return Response({
            'error': 'Invalid username, email, or password.'
        }, status=status.HTTP_401_UNAUTHORIZED)

    if not user.email_confirmed:
        return Response({
            'error': 'Email not verified. Please verify your email before logging in.'
        }, status=status.HTTP_403_FORBIDDEN)

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
def current_user(request):
    user = request.user
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    })


# View to handle reset password request, including sending a password reset email with a secure token.
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = normalize_email(request.data.get('email'))

    if not email:
        return Response({
            'error': 'Email is required to reset password.'
            }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({
            "message": "If email exists, reset instructions sent."
            })

    token = signing.dumps(
        {'email': user.email},
        salt=settings.PASSWORD_RESET_SALT,
    )
    reset_url = request.build_absolute_uri(
        reverse('reset_password_confirm', kwargs={'token': token})
    )

    try:
        send_password_reset_email(email, user.username, reset_url)
    except smtplib.SMTPException:
        return Response({'error': 'Failed to send password reset email.'}, status=status.HTTP_502_BAD_GATEWAY)

    return Response({
        'success': True,
        'message': f'Password reset instructions sent to {email}.'
        })


# View to handle password reset confirmation, including validating the token, 
# checking the new password against validation rules, and updating the user's password.
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request, token):
    try:
        payload = signing.loads(
            token,
            salt=settings.PASSWORD_RESET_SALT,
            max_age=settings.PASSWORD_RESET_MAX_AGE_SECONDS,
        )
    except signing.SignatureExpired:
        return Response({'success': False, 'error': 'Password reset link has expired.'}, status=status.HTTP_400_BAD_REQUEST)
    except signing.BadSignature:
        return Response({'success': False, 'error': 'Invalid password reset link.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=normalize_email(payload.get('email'))).first()
    if not user:
        return Response({
            'success': False,
            'error': 'Invalid password reset link.'
            }, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get('new_password')
    confirm_new_password = request.data.get('confirm_new_password')

    if not new_password or not confirm_new_password:
        return Response({
            'success': False,
            'error': 'New password and confirm new password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_new_password:
        return Response({
            'success': False,
            'error': 'New password and confirm new password do not match.'
            }, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password)
    except ValidationError as e:
        return Response({
            'success': False,
            'error': list(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)

    if user.check_password(new_password):
        return Response({
            'success': False,
            'error': 'New password cannot be the same as the old password.'
        }, status=status.HTTP_400_BAD_REQUEST)

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
@permission_classes([AllowAny])
def user_logout(request):
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            'success': True,
            'message': 'Logout successful.'
        })

    except TokenError:
        return Response(
            {'error': 'Invalid refresh token.'},
            status=status.HTTP_400_BAD_REQUEST
        )


# View to retrieve all watchlists for a specific user, 
# ensuring that the requesting user has permission to view the watchlists 
# and returning the watchlist data in a structured format.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_watchlists(request, user_id):
    if str(request.user.id) != str(user_id):
        return Response({
            'error': 'You do not have permission to view this user\'s watchlists.'
            }, status=status.HTTP_403_FORBIDDEN)
    
    user = User.objects.filter(id=user_id).first()
    if not user: 
        return Response({
            'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
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
def create_watchlist(request):
    user = request.user

    watchlist_name = request.data.get('name')
    if not watchlist_name:
        return Response({
            'error': 'Watchlist name is required.'
        }, status=status.HTTP_400_BAD_REQUEST)

    watchlist_name = watchlist_name.strip()

    if user.watchlists.filter(name=watchlist_name).exists():
        return Response({
            'error': 'A watchlist with this name already exists.'
        }, status=status.HTTP_409_CONFLICT)

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
def add_coin_to_watchlist(request):
    user_id = request.data.get('user_id')
    if str(request.user.id) != str(user_id):
        return Response({
            'error': 'You do not have permission to modify this user\'s watchlists.'
            }, status=status.HTTP_403_FORBIDDEN)
    
    user = User.objects.filter(id=user_id).first()

    if not user:
        return Response({
            'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    watchlist_id = request.data.get('watchlist_id')
    if not watchlist_id:
        return Response({
            'error': 'Watchlist ID is required to add a coin to the watchlist.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    watchlist = user.watchlists.filter(id=watchlist_id).first()
    if not watchlist:
        return Response({
            'error': 'Watchlist not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    ticker = request.data.get('ticker')
    if ticker:
        ticker = ticker.upper()
    else:
        return Response({
            'error': 'Ticker is required to add a coin to the watchlist.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    coin = Coin.objects.filter(ticker=ticker).first()
    if not coin:
        return Response({
            'error': 'Coin not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    if watchlist.items.filter(ticker=coin).exists():
        return Response({
            'error': 'Coin is already in the watchlist.'
            }, status=status.HTTP_409_CONFLICT)
    
    watchlist.items.create(ticker=coin)
    serializer = WatchlistSerializer(watchlist)
    return Response({
        'success': True,
        'message': f'{coin.coin_name} ({coin.ticker}) added to watchlist {watchlist.name}.',
        'watchlist': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_coin_from_watchlist(request):
    user_id = request.data.get('user_id')
    if str(request.user.id) != str(user_id):
        return Response({
            'error': 'You do not have permission to modify this user\'s watchlists.'
            }, status=status.HTTP_403_FORBIDDEN)
    
    user = User.objects.filter(id=user_id).first()

    if not user:
        return Response({
            'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    watchlist_id = request.data.get('watchlist_id')
    if not watchlist_id:
        return Response({
            'error': 'Watchlist ID is required to remove a coin from the watchlist.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    watchlist = user.watchlists.filter(id=watchlist_id).first()
    if not watchlist:
        return Response({
            'error': 'Watchlist not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    ticker = request.data.get('ticker')
    if not ticker:
        return Response({
            'error': 'Ticker is required to remove a coin from the watchlist.'
            }, status=status.HTTP_400_BAD_REQUEST)
    ticker = ticker.upper()
    
    coin = Coin.objects.filter(ticker=ticker).first()
    if not coin:
        return Response({
            'error': 'Coin not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    item = watchlist.items.filter(ticker=coin).first()
    if not item:
        return Response({
            'error': 'Coin is not in the watchlist.'
            }, status=status.HTTP_404_NOT_FOUND)
    
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
def show_watchlist_items(request, watchlist_id):
    watchlist_id = request.query_params.get('watchlist_id') or watchlist_id
    if not watchlist_id:
        return Response({
            'error': 'Watchlist ID is required to view watchlist items.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    watchlist = Watchlist.objects.filter(id=watchlist_id).first()

    if not watchlist:
        return Response({
            'error': 'Watchlist not found.'
            }, status=status.HTTP_404_NOT_FOUND)

    if watchlist.user_id != request.user.id:
        return Response({
            'error': 'You do not have permission to view this watchlist.'
            }, status=status.HTTP_403_FORBIDDEN)
    
    items = watchlist.items.select_related('ticker').all()
    serializer = WatchlistItemDetailSerializer(items, many=True)

    return Response({
        'success': True,
        'watchlist': watchlist.name,
        'items': serializer.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_watchlist(request, watchlist_id):
    user_id = request.data.get('user_id')
    if str(request.user.id) != str(user_id):
        return Response({
            'error': 'You do not have permission to modify this user\'s watchlists.'
            }, status=status.HTTP_403_FORBIDDEN)

    user = User.objects.filter(id=user_id).first()

    if not user:
        return Response({
            'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

    watchlist = user.watchlists.filter(id=watchlist_id).first()
    if not watchlist:
        return Response({
            'error': 'Watchlist not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    watchlist.delete()
    return Response({
        'success': True,
        'message': f'Watchlist {watchlist.name} with {watchlist_id} has been deleted successfully.'
    })