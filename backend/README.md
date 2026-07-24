# PREX Backend

The PREX backend is a Django 6 and Django REST Framework API for cryptocurrency market data, authentication, email verification, password reset, and user watchlists. It uses PostgreSQL and CoinGecko as the external market-data provider.

For the complete endpoint reference, request bodies, response examples and authentication details, [click here to open `APIs.md`](APIs.md).

## Backend Structure

```text
backend/
├── api/
│   ├── migrations/       Django database migrations
│   ├── templates/        Verification and password-reset email templates
│   ├── models.py         User, Coin, Watchlist and WatchlistItem models
│   ├── serializers.py    API response serializers
│   ├── urls.py            Versioned API routes
│   ├── views.py           API handlers and validation
│   └── tests.py           Integration tests
├── prex/
│   ├── settings/         local, shared and production settings
│   ├── urls.py            Admin and `/api/v1/` routing
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── schema.sql            Documentation schema for application tables
└── requirements.txt      Python dependencies at repository root
```

## Requirements

- Python 3.12 or a compatible supported Python version
- PostgreSQL
- SMTP credentials for registration verification and password reset emails
- CoinGecko API key

Install dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Copy `backend/.env.example` to `backend/.env` and replace the placeholder values. Local development uses `prex.settings.local`; production must use `prex.settings.production`.

Required shared settings include:

- `DJANGO_SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`
- `EMAIL_VERIFICATION_URL` and `EMAIL_VERIFICATION_SUCCESS_URL`

Production additionally requires:

- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `COINGECKO_API_KEY`

Use comma-separated values for `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` when more than one value is needed. Keep real secrets outside source control.

## Local Development

From `backend/`:

```powershell
..\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/`. The versioned API base URL is:

```text
http://127.0.0.1:8000/api/v1/
```

## Database

Django migrations are the source of truth for database changes. Apply them with:

```powershell
python manage.py makemigrations
python manage.py migrate
```

The application tables are documented in [`schema.sql`](schema.sql). Because the project uses Django authentication, sessions, permissions and Simple JWT blacklisting, a complete database must be created with `migrate`; do not use `schema.sql` as a replacement for Django migrations.

## API Summary

All routes are mounted below `/api/v1/`:

- Public system and market data: home, health, coins, search and charts
- Public account flows: registration, email verification, login, password reset and token refresh
- Authenticated account flows: current user, profile update and logout
- Authenticated watchlist flows: create, list, delete, add/remove coins, inspect items and inspect coin membership

See [`APIs.md`](APIs.md) for the full route-by-route reference.

Interactive API documentation is available while the backend is running:

- OpenAPI schema: `/api/v1/schema/`
- Swagger UI: `/api/v1/docs/`
- ReDoc: `/api/v1/redoc/`

## Authentication

Login returns a short-lived access token and a refresh token. Send the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

The logout endpoint requires authentication and only blacklists a refresh token when its `user_id` matches the authenticated user. Refresh tokens are rotated/blacklisted according to the Simple JWT settings.

## External API Behavior

CoinGecko requests use connection/read timeouts. Provider timeouts return `504`, other provider failures return `502`, and invalid or unavailable coin data returns an appropriate `4xx`/`5xx` response. Chart payloads are cached for five minutes.

## Validation

Run backend checks and tests from `backend/`:

```powershell
python manage.py check
python manage.py test
```

For a production configuration:

```powershell
$env:DJANGO_SETTINGS_MODULE="prex.settings.production"
python manage.py check --deploy
```

Before starting the production server:

```powershell
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn prex.wsgi:application
```

The public load-balancer health check should use:

```text
/api/v1/health/
```

## Current Limitations

- The API currently uses function-based views and manual request validation rather than a centralized schema/OpenAPI generator.
- JWTs are handled by the frontend through browser storage; an HttpOnly cookie-based session design would reduce token exposure to XSS.
- Rate limiting, centralized observability, background email delivery and provider-failure alerting are not yet implemented.
- PostgreSQL backup/restore procedures, deployment manifests and CI/CD configuration are maintained outside this backend directory and should be added before a larger production rollout.
