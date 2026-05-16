import json
import smtplib
import requests
from uuid import uuid4
from decouple import config
from .models import Coin, User
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from email.message import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.hashers import check_password, make_password

# Constants for CoinGecko API access
COINGECKO_API_URL = config('COINGECKO_API_URL')
HEADERS = {
    "x-cg-demo-api-key": config('COINGECKO_API_KEY')
}

# Utility function to parse JSON body from requests, handling both JSON and form data.
def get_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return None
    return request.POST


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
def home(request):
    return JsonResponse({
        'message': 'Welcome to the PREX API!'
        })

# View to fetch the latest coin data from the CoinGecko API and update the database accordingly.
def coin_list(request):
    if request.method == 'GET':
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
            return JsonResponse({
                "error": str(error)
                }, status=502)

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
        return JsonResponse(data, safe=False)
    
    return JsonResponse({
        'error': 'Only GET method is allowed for this endpoint.'
        }, status=405)


@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Only POST method is allowed for this endpoint.'
            }, status=405)

    data = get_request_data(request)
    if data is None:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    username = data.get('username')
    dob = data.get('dob')
    email = data.get('email')
    password = data.get('password')

    if not all([username, dob, email, password]):
        return JsonResponse({
            'error': 'username, dob, email, and password are required.'
            }, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({
            'error': 'Email already exists.'
            }, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'error': 'Username already exists.'
            }, status=400)

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
        return JsonResponse({
            'error': f'Could not send verification email: {error}'
            }, status=502)

    return JsonResponse({
        'message': 'Verification email sent. Your account will be created after email verification.'
        })


def verify_email(request, token):
    try:
        payload = signing.loads(
            token,
            salt=settings.EMAIL_VERIFICATION_SALT,
            max_age=settings.EMAIL_VERIFICATION_MAX_AGE_SECONDS,
        )
    except signing.SignatureExpired:
        return JsonResponse({'error': 'Verification link has expired.'}, status=400)
    except signing.BadSignature:
        return JsonResponse({'error': 'Invalid verification link.'}, status=400)

    required_fields = ['username', 'dob', 'email', 'password_hash']
    if not all(payload.get(field) for field in required_fields):
        return JsonResponse({'error': 'Invalid verification link.'}, status=400)

    if User.objects.filter(email=payload['email']).exists():
        return JsonResponse({'message': 'Email is already verified.'})

    if User.objects.filter(username=payload['username']).exists():
        return JsonResponse({
            'error': 'Username is no longer available. Please register again.'
            }, status=409)

    User.objects.create(
        username=payload['username'],
        dob=payload['dob'],
        email=payload['email'],
        password_hash=payload['password_hash'],
        email_confirmed=True,
    )

    return JsonResponse({'message': 'Email verified successfully. Account created.'})

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = get_request_data(request)
        if data is None:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        print(f"Login attempt: username= {username}, email= {email}")

        if username and email and password:
            valid_user = User.objects.filter(username=username, email=email).exists()
            valid_password = valid_user and check_password(password, User.objects.get(username=username).password_hash)
            if not valid_user or not valid_password:
                return JsonResponse({
                    'error': 'Invalid username, email, or password.'
                }, status=401)
            access_token = str(AccessToken.for_user(User.objects.get(username=username)))
            if valid_user:
                return JsonResponse({
                    'status': 200,
                    'success': True,
                    'message': f'Login Successful, Welcome back {username}!',
                    'access_token': access_token,
                    'user': {
                        'username': username,
                        'email': email
                    }
                })
            else:
                return JsonResponse({
                    'error': 'Invalid username or email.'
                }, status=401)
        else:
            return JsonResponse({
                'error': 'Username, email, and password are required for login.'
                }, status=400)
        
    return JsonResponse({
        'message': 'Request method not allowed. Please use POST to login.'
        })

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        data = get_request_data(request)
        if data is None:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        email = data.get('email')

        if email:
            if User.objects.filter(email=email).exists():
                reset_token = str(uuid4())
                reset_url = request.build_absolute_uri(reverse('reset_password_confirm', kwargs={'reset_token': reset_token}))
                User.objects.filter(email=email).update(reset_token=reset_token)

                try: 
                    send_password_reset_email(email, User.objects.get(email=email).username, reset_url)
                    return JsonResponse({
                        'success': True,
                        'message': f'Password reset instructions sent to {email}.'
                        })
                except Exception as e:
                    return JsonResponse({'error': 'Failed to send password reset email.'}, status=500)
                
            else:
                return JsonResponse({
                    'error': 'Email not found.'
                    }, status=404)
        else:
            return JsonResponse({
                'error': 'Email is required to reset password.'
                }, status=400)
        
    return JsonResponse({
        'message': 'Reset password functionality will be implemented here.'
        })

@csrf_exempt
def reset_password_confirm(request, reset_token):
    if request.method == 'POST':
        data = get_request_data(request)
        email = data.get('email')
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')
        if data is None:
            return JsonResponse({'success': False, 'error': 'Invalid JSON Body'}, status=400)
        
        if User.objects.filter(email=email, reset_token=reset_token).exists():
            if not new_password or not confirm_new_password:
                return JsonResponse({
                    'success': False, 
                    'error': 'New password and confirm new password are required.'
                    }, status=400)
            if new_password != confirm_new_password:
                return JsonResponse({
                    'success': False, 
                    'error': 'New password and confirm new password do not match.'
                    }, status=400)
            if len(new_password) < 8:
                return JsonResponse({
                    'success': False, 
                    'error': 'New password must be at least 8 characters long.'
                    }, status=400)
            if check_password(new_password, User.objects.get(email=email).password_hash):
                return JsonResponse({
                    'success': False, 
                    'error': 'New password cannot be the same as the old password.'
                    }, status=400)
            new_password_hash = make_password(new_password)
            User.objects.filter(email=email, reset_token=reset_token).update(password_hash=new_password_hash, reset_token=None, updated_at=timezone.now())
            return JsonResponse({
                'success': True, 
                'message': 'Password reset successfully.'
                })
        else:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid email or reset token.'
                }, status=400)
    return JsonResponse({
        'message': 'Invalid request method. Please use POST to reset password.'
        })

def user_logout(request):
    return JsonResponse({
        'message': 'User logout functionality will be implemented here.'
        })


def user_watchlists(request, user_id):
    # Placeholder for fetching a user's watchlists
    return JsonResponse({
        'message': f'Watchlists for user {user_id} will be returned here.'
        })
