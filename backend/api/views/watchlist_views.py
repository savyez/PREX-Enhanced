from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..models import Coin, Watchlist, WatchlistItem
from ..serializers import (
    WatchlistSerializer,
    WatchlistItemDetailSerializer,
    WatchlistNameRequestSerializer,
    WatchlistCoinRequestSerializer,
    UserScopedRequestSerializer,
    ErrorResponseSerializer,
    MessageResponseSerializer,
    WatchlistResponseSerializer,
    WatchlistListResponseSerializer,
    WatchlistItemsResponseSerializer,
    MembershipResponseSerializer,
)
from .common import (
    build_error_response,
    validate_authenticated_user_scope,
    validate_request_data,
)


@extend_schema(tags=['watchlists'], request=WatchlistNameRequestSerializer, responses={201: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 409: ErrorResponseSerializer})
class CreateWatchlistView(APIView):
    """View to create a new watchlist for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
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


@extend_schema(tags=['watchlists'], request=WatchlistCoinRequestSerializer, responses={200: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer, 409: ErrorResponseSerializer})
class AddCoinToWatchlistView(APIView):
    """View to add a coin to a user's watchlist."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data, error_response = validate_request_data(request, WatchlistCoinRequestSerializer)
        if error_response:
            return error_response

        permission_error = validate_authenticated_user_scope(
            request,
            data['user_id'],
            'You do not have permission to modify this user\'s watchlists.'
        )
        if permission_error:
            return permission_error

        user = request.user
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
        watchlist = user.watchlists.prefetch_related('items__ticker').get(id=watchlist_id)
        serializer = WatchlistSerializer(watchlist)
        return Response({
            'success': True,
            'message': f'{coin.coin_name} ({coin.ticker}) added to watchlist {watchlist.name}.',
            'watchlist': serializer.data
        })


@extend_schema(tags=['watchlists'], request=WatchlistCoinRequestSerializer, responses={200: WatchlistResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
class RemoveCoinFromWatchlistView(APIView):
    """View to remove a coin from a user's watchlist."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data, error_response = validate_request_data(request, WatchlistCoinRequestSerializer)
        if error_response:
            return error_response

        permission_error = validate_authenticated_user_scope(
            request,
            data['user_id'],
            'You do not have permission to modify this user\'s watchlists.'
        )
        if permission_error:
            return permission_error

        user = request.user
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
        watchlist = user.watchlists.prefetch_related('items__ticker').get(id=watchlist_id)
        serializer = WatchlistSerializer(watchlist)
        return Response({
            'success': True,
            'message': f'{coin.coin_name} ({coin.ticker}) removed from watchlist {watchlist.name}.',
            'watchlist': serializer.data
        })


@extend_schema(tags=['watchlists'], responses={200: WatchlistItemsResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
class WatchlistItemsView(APIView):
    """View to retrieve all items in a specific watchlist."""
    permission_classes = [IsAuthenticated]

    def get(self, request, watchlist_id=None):
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


@extend_schema(tags=['watchlists'], responses={200: MembershipResponseSerializer, 404: ErrorResponseSerializer})
class CoinWatchlistMembershipView(APIView):
    """Return all watchlists (and item ids) for the authenticated user that contain the given coin ticker."""
    permission_classes = [IsAuthenticated]

    def get(self, request, ticker):
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


@extend_schema(tags=['watchlists'], responses={200: WatchlistListResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
class UserWatchlistsView(APIView):
    """View to retrieve all watchlists for a specific user."""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        permission_error = validate_authenticated_user_scope(
            request,
            user_id,
            'You do not have permission to view this user\'s watchlists.'
        )
        if permission_error:
            return permission_error

        watchlists = request.user.watchlists.prefetch_related('items__ticker').all()
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


@extend_schema(tags=['watchlists'], request=UserScopedRequestSerializer, responses={200: MessageResponseSerializer, 400: ErrorResponseSerializer, 403: ErrorResponseSerializer, 404: ErrorResponseSerializer})
class DeleteWatchlistView(APIView):
    """View to delete a specific watchlist for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def post(self, request, watchlist_id):
        data, error_response = validate_request_data(request, UserScopedRequestSerializer)
        if error_response:
            return error_response

        permission_error = validate_authenticated_user_scope(
            request,
            data['user_id'],
            'You do not have permission to modify this user\'s watchlists.'
        )
        if permission_error:
            return permission_error

        user = request.user

        watchlist = user.watchlists.filter(id=watchlist_id).first()
        if not watchlist:
            return build_error_response('Watchlist not found.', status.HTTP_404_NOT_FOUND)

        watchlist.delete()
        return Response({
            'success': True,
            'message': f'Watchlist {watchlist.name} with {watchlist_id} has been deleted successfully.'
        })
