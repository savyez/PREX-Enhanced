import smtplib

from django.conf import settings
from django.shortcuts import redirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from ..serializers import (
    EmailRequestSerializer,
    ErrorResponseSerializer,
    LoginRequestSerializer,
    MessageResponseSerializer,
    PasswordResetConfirmRequestSerializer,
    ProfileUpdateRequestSerializer,
    RefreshTokenRequestSerializer,
    RegisterRequestSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
    TokenResponseSerializer,
    UserSerializer,
)
from ..services.auth_service import (
    AuthService,
    AuthenticationServiceError,
    clear_refresh_token_cookie,
    refresh_user_tokens,
    set_refresh_token_cookie,
)
from ..services.email_service import (
    send_email_message,
    send_password_reset_email,
    send_verification_email,
)
from .common import (
    build_error_response,
    validate_authenticated_user_scope,
    validate_request_data,
)


@extend_schema(tags=['auth'], request=RegisterRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 502: ErrorResponseSerializer})
class RegisterView(APIView):
    """View to handle user registration, validation, and email dispatching via AuthService."""
    permission_classes = [AllowAny]

    def post(self, request):
        data, error_response = validate_request_data(request, RegisterRequestSerializer)
        if error_response:
            return error_response

        try:
            _, message = AuthService.register_user(
                username=data['username'],
                dob=data['dob'],
                email=data['email'],
                password=data['password'],
                request=request,
            )
            return Response({'message': message}, status=status.HTTP_200_OK)
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)


@extend_schema(tags=['auth'], responses={302: OpenApiResponse(description='Redirects to the configured frontend success URL.'), 400: ErrorResponseSerializer, 404: ErrorResponseSerializer})
class VerifyEmailView(APIView):
    """View to handle email verification and activate the user account via AuthService."""
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            user, already_confirmed = AuthService.verify_email(token)
            return redirect(settings.EMAIL_VERIFICATION_SUCCESS_URL)
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)


@extend_schema(tags=['auth'], request=LoginRequestSerializer, responses={200: TokenResponseSerializer, 400: ErrorResponseSerializer, 401: ErrorResponseSerializer, 403: ErrorResponseSerializer})
class LoginView(APIView):
    """View to authenticate credentials, return in-memory access token, and set HttpOnly refresh cookie."""
    permission_classes = [AllowAny]

    def post(self, request):
        data, error_response = validate_request_data(request, LoginRequestSerializer)
        if error_response:
            return error_response

        try:
            user, access_token, refresh_token = AuthService.authenticate_user(
                email=data['email'],
                password=data['password'],
            )

            user_serializer = UserSerializer(user)
            response = Response({
                'status': 200,
                'success': True,
                'message': f'Login Successful, Welcome back {user.username}!',
                'access_token': access_token,
                'user': user_serializer.data
            })
            set_refresh_token_cookie(response, refresh_token)
            return response
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)


@extend_schema(
    tags=['auth'],
    request=TokenRefreshRequestSerializer,
    responses={
        200: TokenRefreshResponseSerializer,
        401: ErrorResponseSerializer,
    }
)
class CustomTokenRefreshView(TokenRefreshView):
    """View to handle silent token refresh from HttpOnly cookie or request body."""
    def post(self, request, *args, **kwargs):
        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        raw_data = request.data if isinstance(request.data, dict) else {}
        data = raw_data.copy()

        if 'refresh' not in data and 'refresh_token' not in data:
            cookie_token = request.COOKIES.get(cookie_name)
            if cookie_token:
                data['refresh'] = cookie_token
        elif 'refresh_token' in data and 'refresh' not in data:
            data['refresh'] = data['refresh_token']

        if not data.get('refresh'):
            return build_error_response('Authentication credentials were not provided.', status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as error:
            return build_error_response(str(error), status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return build_error_response('Invalid refresh token.', status.HTTP_401_UNAUTHORIZED)

        validated_data = serializer.validated_data
        access_token = validated_data.get('access')
        response_payload = {
            'access': access_token,
            'access_token': access_token,
        }

        response = Response(response_payload, status=status.HTTP_200_OK)

        new_refresh = validated_data.get('refresh')
        if new_refresh:
            set_refresh_token_cookie(response, new_refresh)

        return response


@extend_schema(tags=['auth'], responses={200: UserSerializer, 401: ErrorResponseSerializer})
class CurrentUserView(APIView):
    """View to retrieve the current authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'user': UserSerializer(request.user).data
        })


@extend_schema(tags=['auth'], request=ProfileUpdateRequestSerializer, responses={200: UserSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 409: ErrorResponseSerializer})
class UpdateUserView(APIView):
    """View to update user profile information via AuthService."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        permission_error = validate_authenticated_user_scope(request, user_id)
        if permission_error:
            return permission_error

        data, error_response = validate_request_data(request, ProfileUpdateRequestSerializer)
        if error_response:
            return error_response

        try:
            user = AuthService.update_user_profile(request.user, data)
            return Response({
                'success': True,
                'message': 'Profile updated successfully.',
                'user': UserSerializer(user).data
            })
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)


@extend_schema(tags=['auth'], request=EmailRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 502: ErrorResponseSerializer})
class ResetPasswordView(APIView):
    """View to handle password reset requests via AuthService."""
    permission_classes = [AllowAny]

    def post(self, request):
        data, error_response = validate_request_data(request, EmailRequestSerializer)
        if error_response:
            return error_response

        try:
            message = AuthService.request_password_reset(data['email'], request)
            return Response({
                'success': True,
                'message': message
            })
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)


@extend_schema(tags=['auth'], request=PasswordResetConfirmRequestSerializer, responses={200: MessageResponseSerializer, 302: OpenApiResponse(description='Redirects to frontend reset password page on GET.'), 400: ErrorResponseSerializer})
class ResetPasswordConfirmView(APIView):
    """View to validate reset token and update user password via AuthService."""
    permission_classes = [AllowAny]

    def get(self, request, token):
        base_url = getattr(settings, 'PASSWORD_RESET_URL', None)
        target_url = f"{base_url.rstrip('/')}/{token}"
        return redirect(target_url)

    def post(self, request, token):
        data, error_response = validate_request_data(request, PasswordResetConfirmRequestSerializer)
        if error_response:
            return error_response

        try:
            _, message = AuthService.confirm_password_reset(token, data['new_password'])
            return Response({
                'success': True,
                'message': message
            })
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)


@extend_schema(tags=['auth'], request=RefreshTokenRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer})
class LogoutView(APIView):
    """View to revoke/blacklist refresh token and clear HttpOnly cookie via AuthService."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data, error_response = validate_request_data(request, RefreshTokenRequestSerializer)
        if error_response:
            return error_response

        cookie_name = getattr(settings, 'AUTH_COOKIE_REFRESH_NAME', 'refresh_token')
        refresh_token = (
            data.get('refresh_token')
            or data.get('refresh')
            or request.COOKIES.get(cookie_name)
        )

        try:
            if refresh_token:
                AuthService.revoke_session(request.user, refresh_token)
        except AuthenticationServiceError as error:
            return build_error_response(error.message, status_code=error.status_code)

        response = Response({
            'success': True,
            'message': 'Logout successful.'
        })
        clear_refresh_token_cookie(response)
        return response
