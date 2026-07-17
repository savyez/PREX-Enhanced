from math import ceil
from rest_framework.response import Response


DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def get_pagination_params(request, default_page_size=DEFAULT_PAGE_SIZE, max_page_size=MAX_PAGE_SIZE):
    try:
        page = int(request.query_params.get('page', 1))
    except (TypeError, ValueError):
        page = 1

    try:
        page_size = int(request.query_params.get('page_size', default_page_size))
    except (TypeError, ValueError):
        page_size = default_page_size

    page = max(page, 1)
    page_size = min(max(page_size, 1), max_page_size)

    return page, page_size


def paginate_items(items, page, page_size):
    total_count = len(items)
    total_pages = ceil(total_count / page_size) if total_count else 0

    if total_pages and page > total_pages:
        page = total_pages

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    page_items = items[start_index:end_index]

    return {
        'page': page,
        'page_size': page_size,
        'total_count': total_count,
        'total_pages': total_pages,
        'results': page_items,
    }


def build_paginated_response(serializer_class, items, page, page_size, extra_data=None, status_code=200):
    pagination = paginate_items(list(items), page, page_size)
    serializer = serializer_class(pagination['results'], many=True)

    payload = {
        'success': True,
        'page': pagination['page'],
        'page_size': pagination['page_size'],
        'total_count': pagination['total_count'],
        'total_pages': pagination['total_pages'],
        'results': serializer.data,
        'coins': serializer.data,
    }

    if extra_data:
        payload.update(extra_data)

    return Response(payload, status=status_code)
