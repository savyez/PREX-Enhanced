import json
import smtplib
from email.message import EmailMessage

import requests
from decouple import config
from .models import Coin, User
from django.core import signing
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

COINGECKO_API_URL = config('COINGECKO_API_URL')
HEADERS = {
    "x-cg-demo-api-key": config('COINGECKO_API_KEY')
}


def get_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return None
    return request.POST


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

# Simple view to test the API endpoint
def home(request):
    return JsonResponse({
        'message': 'Welcome to the PREX API!'
        })

# View to fetch the latest coin data from the CoinGecko API and update the database accordingly.
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


def user_watchlists(request, user_id):
    # Placeholder for fetching a user's watchlists
    return JsonResponse({
        'message': f'Watchlists for user {user_id} will be returned here.'
        })
