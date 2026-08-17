import smtplib
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..helpers import get_signed_payload, normalize_email_value, normalize_username_value
from ..models import User
from .email_service import EmailService


class AuthenticationServiceError(Exception):
    """Base exception for authentication service errors with status code."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthService:
    """Service layer encapsulating registration, authentication, token management, and password recovery."""

    @staticmethod
    def set_refresh_token_cookie(response, refresh_token):
        """Sets the refresh token in an HttpOnly, SameSite cookie."""
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        cookie_secure = getattr(settings, 'AUTH_COOKIE_SECURE', not settings.DEBUG)
        cookie_samesite = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')
        cookie_path = getattr(settings, 'AUTH_COOKIE_PATH', '/api/v1/')
        max_age = int(settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=7)).total_seconds())

        response.set_cookie(
            key=cookie_name,
            value=str(refresh_token),
            max_age=max_age,
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path=cookie_path,
        )

    @staticmethod
    def clear_refresh_token_cookie(response):
        """Clears the refresh token HttpOnly cookie."""
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        cookie_samesite = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')
        cookie_path = getattr(settings, 'AUTH_COOKIE_PATH', '/api/v1/')

        response.delete_cookie(
            key=cookie_name,
            path=cookie_path,
            samesite=cookie_samesite,
        )

    @staticmethod
    def refresh_user_tokens(user):
        """Generates a fresh access and refresh token pair for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }

    @classmethod
    def register_user(cls, username, dob, email, password, request):
        """Validates, creates unverified user, and dispatches verification email."""
        norm_username = normalize_username_value(username)
        norm_email = normalize_email_value(email)

        existing_user = User.objects.filter(email=norm_email).first()

        if existing_user:
            if existing_user.email_confirmed:
                raise AuthenticationServiceError('Email already exists.', status_code=400)
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
                    EmailService.send_verification_email(existing_user.email, existing_user.username, verification_url)
                    print(f"Re-verification mail sent to {existing_user.email}")
                except smtplib.SMTPException as error:
                    raise AuthenticationServiceError(
                        f'Could not send verification email: {error}',
                        status_code=502
                    ) from error

                return existing_user, 'Verification email resent. Verify your email to complete registration.'

        if User.objects.filter(username=norm_username).exists():
            raise AuthenticationServiceError('Username already exists.', status_code=400)

        # Create inactive user (must verify email to activate)
        user = User.objects.create_user(
            username=norm_username,
            dob=dob,
            email=norm_email,
            password=password,
            email_confirmed=False,
        )

        token = signing.dumps(
            {'email': norm_email},
            salt=settings.EMAIL_VERIFICATION_SALT,
        )
        verification_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token})
        )

        try:
            print(f"Sending Verification mail to {norm_email}")
            EmailService.send_verification_email(norm_email, norm_username, verification_url)
            print(f"Verification mail sent to {norm_email}")
        except smtplib.SMTPException as error:
            user.delete()
            raise AuthenticationServiceError(
                f'Could not send verification email: {error}',
                status_code=502
            ) from error

        return user, 'Verification email sent. Verify your email to complete registration.'

    @classmethod
    def verify_email(cls, token):
        """Validates verification signature and activates the user account."""
        try:
            payload = get_signed_payload(
                token,
                settings.EMAIL_VERIFICATION_SALT,
                settings.EMAIL_VERIFICATION_MAX_AGE_SECONDS,
            )
        except ValueError as error:
            raise AuthenticationServiceError(str(error), status_code=400) from error

        email = normalize_email_value(payload.get('email'))
        if not email:
            raise AuthenticationServiceError('Invalid verification link.', status_code=400)

        user = User.objects.filter(email=email).first()
        if not user:
            raise AuthenticationServiceError('User not found. Please register again.', status_code=404)

        if user.email_confirmed:
            return user, True

        user.email_confirmed = True
        user.updated_at = timezone.now()
        user.save(update_fields=['email_confirmed', 'updated_at'])
        return user, False

    @classmethod
    def authenticate_user(cls, email, password):
        """Validates credentials and generates access/refresh tokens."""
        norm_email = normalize_email_value(email)
        user = User.objects.filter(email=norm_email).first()

        if not user or not user.check_password(password):
            raise AuthenticationServiceError('Invalid email or password.', status_code=401)

        if not user.email_confirmed:
            raise AuthenticationServiceError(
                'Email not verified. Please verify your email before logging in.',
                status_code=403
            )

        refresh = RefreshToken.for_user(user)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user, str(refresh.access_token), str(refresh)

    @classmethod
    def request_password_reset(cls, email, request):
        """Generates signed password reset token and dispatches reset instructions."""
        norm_email = normalize_email_value(email)
        user = User.objects.filter(email=norm_email).first()

        if not user:
            return 'If email exists, reset instructions sent.'

        token = signing.dumps(
            {'email': user.email},
            salt=settings.PASSWORD_RESET_SALT,
        )
        if getattr(settings, 'PASSWORD_RESET_URL', None):
            base_reset_url = settings.PASSWORD_RESET_URL.rstrip('/')
            reset_url = f"{base_reset_url}/{token}"
        else:
            reset_url = request.build_absolute_uri(
                reverse('reset_password_confirm', kwargs={'token': token})
            )

        try:
            print(f"Sending Password reset mail to {norm_email}")
            EmailService.send_password_reset_email(norm_email, user.username, reset_url)
            print(f"Password reset mail sent to {norm_email}")
        except smtplib.SMTPException as error:
            raise AuthenticationServiceError('Failed to send password reset email.', status_code=502) from error

        return f'Password reset instructions sent to {norm_email}.'

    @classmethod
    def confirm_password_reset(cls, token, new_password):
        """Validates password reset token and changes password."""
        try:
            payload = get_signed_payload(
                token,
                settings.PASSWORD_RESET_SALT,
                settings.PASSWORD_RESET_MAX_AGE_SECONDS,
            )
        except ValueError as error:
            raise AuthenticationServiceError(str(error), status_code=400) from error

        user = User.objects.filter(email=normalize_email_value(payload.get('email'))).first()
        if not user:
            raise AuthenticationServiceError('Invalid password reset link.', status_code=400)

        if user.check_password(new_password):
            raise AuthenticationServiceError('New password cannot be the same as the old password.', status_code=400)

        user.set_password(new_password)
        user.updated_at = timezone.now()
        user.save(update_fields=['password', 'updated_at'])

        return user, 'Password reset successfully.'

    @classmethod
    def update_user_profile(cls, user, data):
        """Validates payload and updates user profile."""
        allowed_fields = {'first_name', 'last_name', 'username'}
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            raise AuthenticationServiceError(f'Invalid field(s): {", ".join(sorted(invalid_fields))}.', status_code=400)

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
                raise AuthenticationServiceError('username cannot be empty.', status_code=400)
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                raise AuthenticationServiceError('username already exists, try a new one.', status_code=409)
            payload['username'] = username

        if not payload:
            raise AuthenticationServiceError('Please provide at least one field to update.', status_code=400)

        for field, value in payload.items():
            setattr(user, field, value)

        try:
            user.save(update_fields=[*payload.keys(), 'updated_at'])
        except Exception as error:
            raise AuthenticationServiceError('Unable to update your profile right now. Please try again later.', status_code=500) from error

        return user

    @classmethod
    def revoke_session(cls, user, refresh_token_string):
        """Verifies ownership and blacklists the refresh token."""
        if not refresh_token_string:
            return True

        try:
            token = RefreshToken(refresh_token_string)
            if str(token['user_id']) != str(user.id):
                raise AuthenticationServiceError('You do not have permission to revoke this session.', status_code=403)
            token.blacklist()
            return True
        except TokenError as error:
            raise AuthenticationServiceError('Invalid refresh token.', status_code=400) from error


# Helper functions
set_refresh_token_cookie = AuthService.set_refresh_token_cookie
clear_refresh_token_cookie = AuthService.clear_refresh_token_cookie
refresh_user_tokens = AuthService.refresh_user_tokens
