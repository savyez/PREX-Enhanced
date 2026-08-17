from django.core.cache import cache
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema

from ..models import Coin
from ..serializers import CoinSerializer, ChartResponseSerializer, ErrorResponseSerializer
from ..paginations import get_pagination_params, build_paginated_response
from ..services.coingecko import (
    CoinGeckoClient,
    CoinGeckoTimeout,
    coingecko_client,
    fetch_coingecko,
    resolve_coin_gecko_id,
)
from .common import build_error_response


@extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=25),
    ],
    responses={200: OpenApiResponse(description='Paginated coin market data.')},
)
class CoinListView(APIView):
    """View to fetch local coin market data with pagination."""
    permission_classes = [AllowAny]

    def get(self, request):
        page, page_size = get_pagination_params(request)
        cache_key = f"coin_list_page_{page}_size_{page_size}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        coins = Coin.objects.all().order_by('market_cap_rank', 'ticker')
        response = build_paginated_response(CoinSerializer, coins, page, page_size)
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout=300)
        return response


@extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('page', int, OpenApiParameter.QUERY, default=1),
        OpenApiParameter('page_size', int, OpenApiParameter.QUERY, default=10),
    ],
    responses={200: OpenApiResponse(description='Paginated matching coin data.'), 400: ErrorResponseSerializer},
)
class SearchCoinsView(APIView):
    """View to search for coins by ticker or name with pagination."""
    permission_classes = [AllowAny]

    def get(self, request, coin_id):
        query = coin_id.strip()

        coins = Coin.objects.filter(
            Q(ticker__icontains=query) | Q(coin_name__icontains=query)
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


@extend_schema(
    tags=['market'],
    parameters=[
        OpenApiParameter('days', int, OpenApiParameter.QUERY, default=7),
    ],
    responses={200: ChartResponseSerializer, 404: ErrorResponseSerializer, 502: ErrorResponseSerializer, 504: ErrorResponseSerializer},
)
class CoinChartView(APIView):
    """View to retrieve historical coin price chart data via CoinGecko service."""
    permission_classes = [AllowAny]

    def get(self, request, coin_id=None):
        coin_id = coin_id or request.query_params.get('coin_id')
        try:
            days = int(request.query_params.get('days', 7))
        except (TypeError, ValueError):
            days = 7

        try:
            chart_payload, error_message = coingecko_client.get_chart_data(coin_id, days=days)
            if error_message:
                status_code = status.HTTP_404_NOT_FOUND if 'resolve' in error_message or 'available' in error_message else status.HTTP_502_BAD_GATEWAY
                return build_error_response(error_message, status_code=status_code)

            return Response(chart_payload)
        except CoinGeckoTimeout:
            return build_error_response(
                'Chart data service timed out. Please try again later.',
                status.HTTP_504_GATEWAY_TIMEOUT
            )
        except Exception:
            return build_error_response(
                'Unable to fetch live chart data right now. Please try again later.',
                status.HTTP_502_BAD_GATEWAY
            )
