import smtplib
import requests
from decouple import config
from .models import Coin, User
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from email.message import EmailMessage
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password

# Constants for CoinGecko API access
COINGECKO_API_URL = config('COINGECKO_API_URL')
HEADERS = {
    "x-cg-demo-api-key": config('COINGECKO_API_KEY')
}

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
                'last_updated_at': coin_data['last_updated']
            }
        )
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    data = request.data

    username = data.get('username')
    dob = data.get('dob')
    email = data.get('email')
    password = data.get('password')

    if not all([username, dob, email, password]):
        return Response({
            'error': 'username, dob, email, and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({
            'error': 'Email already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)

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
    
    User.objects.create(
        username=username,
        dob=dob,
        email=email,
        password_hash=make_password(password),
        email_confirmed=False,
    )

    token = signing.dumps(
        {
            'username': username,
            'dob': dob,
            'email': email,
            'password_hash': make_password(password),
        },
        salt=settings.EMAIL_VERIFICATION_SALT,
    )
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )

    try:
        send_verification_email(email, username, verification_url)
    except smtplib.SMTPException as error:
        return Response({
            'error': f'Could not send verification email: {error}'
            }, status=status.HTTP_502_BAD_GATEWAY)

    return Response({
        'message': 'Verification email sent. Verify your email to complete registration.'
        })


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

    required_fields = ['username', 'dob', 'email', 'password_hash']
    if not all(payload.get(field) for field in required_fields):
        return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=payload['email']).first()
    if user and user.email_confirmed:
        return Response({'message': 'Email is already verified.'})

    username_owner = User.objects.filter(username=payload['username']).first()
    if username_owner and username_owner.email != payload['email']:
        return Response({
            'error': 'Username is no longer available. Please register again.'
            }, status=status.HTTP_409_CONFLICT)

    if user:
        user.username = payload['username']
        user.dob = payload['dob']
        user.password_hash = payload['password_hash']
        user.email_confirmed = True
        user.updated_at = timezone.now()
        user.save(update_fields=['username', 'dob', 'password_hash', 'email_confirmed', 'updated_at'])
    else:
        User.objects.create(
            username=payload['username'],
            dob=payload['dob'],
            email=payload['email'],
            password_hash=payload['password_hash'],
            email_confirmed=True,
        )

    return Response({'message': 'Email verified successfully. Login to your account now.'})

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return Response({
            'error': 'Username, email, and password are required for login.'
            }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(username=username, email=email).first()
    if not user or not check_password(password, user.password_hash):
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

    return Response({
        'status': 200,
        'success': True,
        'message': f'Login Successful, Welcome back {username}!',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'username': username,
            'email': email
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')

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

    user = User.objects.filter(email=payload.get('email')).first()
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

    if check_password(new_password, user.password_hash):
        return Response({
            'success': False,
            'error': 'New password cannot be the same as the old password.'
            }, status=status.HTTP_400_BAD_REQUEST)

    user.password_hash = make_password(new_password)
    user.updated_at = timezone.now()
    user.save(update_fields=['password_hash', 'updated_at'])

    return Response({
        'success': True,
        'message': 'Password reset successfully.'
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({
            'error': 'Refresh token is required to logout.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response({
            'error': 'Invalid or expired refresh token.'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'message': 'Logged out successfully.'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_watchlists(request, user_id):
    # Placeholder for fetching a user's watchlists
    return Response({
        'message': f'Watchlists for user {user_id} will be returned here.'
        })
