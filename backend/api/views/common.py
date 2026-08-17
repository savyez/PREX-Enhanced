from rest_framework import status
from rest_framework.response import Response


def build_error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """Builds a consistent JSON error response."""
    return Response({'error': message}, status=status_code)


def parse_request_data(request):
    """Safely extracts and validates that request body data is a JSON dictionary."""
    if request.data is None:
        return {}

    if not isinstance(request.data, dict):
        raise ValueError('Request body must be valid JSON.')

    return request.data


def validate_request_data(request, serializer_class):
    """Validates request data against the provided serializer class and returns (data, error_response)."""
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


def validate_authenticated_user_scope(request, user_id, message='You do not have permission to perform this action.'):
    """Validates that the authenticated user owns the resource being accessed."""
    if str(request.user.id) != str(user_id):
        return build_error_response(message, status.HTTP_403_FORBIDDEN)
    return None

