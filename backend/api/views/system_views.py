from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from ..serializers import MessageResponseSerializer


@extend_schema(tags=['system'], responses={200: MessageResponseSerializer})
class HomeView(APIView):
    """Simple view to test the API root endpoint."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Welcome to the PREX API!'
        })


@extend_schema(tags=['system'], responses={200: MessageResponseSerializer})
class HealthCheckView(APIView):
    """Public health check endpoint returning service status."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'PREX API is healthy and running.'
        })
