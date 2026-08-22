# PREX Backend

The PREX backend is a Django 6 and Django REST Framework API for cryptocurrency market data, authentication, email verification, password reset, and user watchlists. It uses PostgreSQL, Redis caching, Celery asynchronous processing, Gunicorn WSGI, and CoinGecko as the external market-data provider.

For the complete endpoint reference, request bodies, response examples and authentication details, [open `APIs.md`](APIs.md) or visit the interactive documentation (`/api/v1/docs/`).

---

## Backend Structure

```text
backend/
├── api/
│   ├── migrations/       # Django database migrations
│   ├── templates/        # Verification and password-reset email HTML templates
│   ├── services/         # Dedicated domain services
│   │   ├── auth_service.py     # Registration, authentication, cookies & password reset
│   │   ├── coingecko.py        # CoinGeckoClient, search, charts, caching & timeouts
│   │   └── email_service.py    # Email rendering and SMTP dispatching
│   ├── views/            # Modular class-based API views
│   │   ├── auth_views.py       # Authentication and user account views
│   │   ├── market_views.py     # Coin list, search and chart views
│   │   ├── watchlist_views.py  # Watchlist CRUD, membership and item views
│   │   └── system_views.py     # Health check and API root views
│   ├── tests/            # Modular class-based test suites (37 tests)
│   │   ├── base.py             # Base test case with auth helpers & eager settings
│   │   ├── test_auth.py        # Registration, login, cookie rotation, reset & user tests
│   │   ├── test_market.py      # Coin list, search, charts & Celery task tests
│   │   ├── test_watchlist.py   # Watchlist CRUD, items & permission tests
│   │   ├── test_services.py    # CoinGecko, Auth & Email unit tests
│   │   └── test_system.py      # System endpoint & OpenAPI schema tests
│   ├── models.py         # User, Coin, Watchlist and WatchlistItem models
│   ├── serializers.py    # API request and response serializers
│   ├── paginations.py    # Standard pagination utilities
│   ├── tasks.py          # Celery background tasks (market sync, email delivery)
│   └── urls.py           # Versioned API routes (/api/v1/)
├── prex/
│   ├── settings/         # Local, base and production settings
│   ├── celery.py         # Celery app instance and scheduled beat tasks
│   ├── urls.py           # Admin and /api/v1/ routing
│   ├── asgi.py
│   └── wsgi.py
├── Dockerfile            # Multi-worker Gunicorn container entrypoint
├── .dockerignore         # Excludes local virtual environments (.venv), cache, and secrets (.env.*)
├── manage.py
├── schema.sql            # PostgreSQL schema documentation
└── APIs.md               # Detailed API specification
```

---

## Requirements

- **Python 3.12+**
- **PostgreSQL 15+** (Postgres 17 recommended)
- **Redis 7+** (for caching & Celery broker)
- **SMTP credentials** for registration verification and password reset emails
- **CoinGecko API key**

Install dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Key dependencies:
- `Django 6.1` & `djangorestframework 3.18.0`
- `djangorestframework_simplejwt 5.5.1` & `cryptography 50.0.0`
- `gunicorn 26.0.0` (Production WSGI server)
- `celery 5.6.3` & `redis 8.1.0`
- `drf-spectacular 0.29.0` (OpenAPI 3 / Swagger generator)

---

## Configuration

Copy `backend/.env.example` to `backend/.env` and replace the placeholder values.
- Local development uses: `DJANGO_SETTINGS_MODULE=prex.settings.local`
- Production uses: `DJANGO_SETTINGS_MODULE=prex.settings.production`

### Environment Variables Reference

| Variable | Description | Example (Local) | Example (Production) |
| :--- | :--- | :--- | :--- |
| `DJANGO_SETTINGS_MODULE` | Active Django settings module | `prex.settings.local` | `prex.settings.production` |
| `DJANGO_SECRET_KEY` | Cryptographic signing key | `django-insecure-dev-key` | `<strong-production-key>` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host headers | `localhost,127.0.0.1` | `prex.duckdns.org,localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Permitted cross-origin origins | `http://localhost:5173` | `https://prex.duckdns.org` |
| `CSRF_TRUSTED_ORIGINS` | Trusted CSRF origins | `http://localhost:5173` | `https://prex.duckdns.org` |
| `DB_NAME` | PostgreSQL database name | `prex` | `prex` |
| `DB_USER` | PostgreSQL user | `postgres` | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` | `<strong-db-password>` |
| `DB_HOST` | PostgreSQL host | `127.0.0.1` | `db` (in Docker) |
| `DB_PORT` | PostgreSQL port | `5432` | `5432` |
| `REDIS_CACHE_URL` | Redis URL for caching | `redis://127.0.0.1:6379/0` | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Redis broker URL for Celery | `redis://127.0.0.1:6379/0` | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend for Celery | `redis://127.0.0.1:6379/0` | `redis://redis:6379/0` |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` | `587` |
| `EMAIL_HOST_USER` | SMTP username | `example@gmail.com` | `example@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password / app password | `<app-password>` | `<app-password>` |
| `EMAIL_USE_TLS` | Enable TLS encryption | `True` | `True` |
| `COINGECKO_API_KEY` | CoinGecko API key | `<key>` | `<key>` |
| `EMAIL_VERIFICATION_URL` | Verification redirect link | `http://localhost:5173/verify-email` | `https://prex.duckdns.org/verify-email` |
| `PASSWORD_RESET_URL` | Password reset redirect link | `http://localhost:5173/reset-password-confirm` | `https://prex.duckdns.org/reset-password-confirm` |

---

## Local Development

From `backend/`:

```powershell
..\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

The API will be served at `http://127.0.0.1:8000/api/v1/`.

---

## Database Migrations

Django migrations are the single source of truth for database schema:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Database schema documentation is maintained in [`schema.sql`](schema.sql). Because the project uses Django auth, sessions, and Simple JWT token blacklisting, always create database tables with `python manage.py migrate`.

---

## API Summary & Documentation

All routes are mounted under `/api/v1/`:

- **Public System & Market Data:**
  - `GET /api/v1/` — API root
  - `GET /api/v1/health/` — Health check status (`{"status": "ok"}`)
  - `GET /api/v1/coins/` — Paginated coin list (cached in Redis, supports sorting & pagination)
  - `GET /api/v1/coins/search/?q=<query>` — Coin ticker and name search
  - `GET /api/v1/coins/<coin_id>/chart/` — 7-day price chart history
- **Authentication Flows:**
  - `POST /api/v1/auth/register/` — User registration & verification email dispatch
  - `POST /api/v1/auth/verify-email/` — Account verification token confirmation
  - `POST /api/v1/auth/login/` — Login, returns JWT access token & sets HttpOnly refresh cookie
  - `POST /api/v1/auth/token/refresh/` — Silent token refresh via HttpOnly cookie
  - `POST /api/v1/auth/password-reset/` — Initiates password reset email
  - `POST /api/v1/auth/password-reset-confirm/` — Confirms password reset with signed token
  - `POST /api/v1/auth/logout/` — Blacklists refresh token & clears cookies
  - `GET /api/v1/auth/me/` — Returns authenticated user profile
  - `PATCH /api/v1/auth/me/` — Updates user profile (name, etc.)
- **Watchlist Flows:**
  - `GET /api/v1/watchlists/` — List user watchlists
  - `POST /api/v1/watchlists/` — Create new watchlist
  - `DELETE /api/v1/watchlists/<id>/` — Delete watchlist
  - `POST /api/v1/watchlists/<id>/coins/` — Add coin to watchlist
  - `DELETE /api/v1/watchlists/<id>/coins/<coin_id>/` — Remove coin from watchlist
  - `GET /api/v1/watchlists/coins/` — Retrieve membership map across all user watchlists

### Interactive API Documentation
- **Swagger UI:** `/api/v1/docs/`
- **OpenAPI 3 Schema:** `/api/v1/schema/`
- **ReDoc UI:** `/api/v1/redoc/`

---

## Authentication & Security Architecture

- **HttpOnly Cookie Refresh Tokens**: The refresh token is strictly stored in an `HttpOnly`, `SameSite=Lax`, `Secure` browser cookie set by Django. It cannot be accessed by client-side JavaScript, eliminating XSS token theft risks.
- **Short-Lived Access Tokens**: Short-lived JWT access tokens are delivered in JSON payloads and stored only in memory on the frontend.
- **Authorization Header**: Protected endpoints require:
  ```http
  Authorization: Bearer <access-token>
  ```
- **Rate Limiting & Throttling**:
  - `AnonRateThrottle`: `30/minute` on public endpoints.
  - `UserRateThrottle`: `120/minute` on authenticated endpoints.

---

## Background Tasks & Celery Workers

Asynchronous operations are managed via Celery and Redis (`api/tasks.py`):

1. **Asynchronous Email Delivery**:
   - `send_verification_email_task`: Account verification email dispatching with exponential backoff (up to 3 retries, 30s delay).
   - `send_password_reset_email_task`: Password reset instruction email dispatching with exponential backoff.
   - Prevents SMTP network latency from slowing down registration and password reset HTTP requests.
2. **Cryptocurrency Market Synchronization**:
   - `sync_coingecko_market_data`: Periodic Celery Beat task (running every 5 minutes) batch-syncing prices, market caps, 24h volumes, and price changes from CoinGecko into the PostgreSQL database.

---

## Testing & Quality Checks

Run the automated test suite locally:

```powershell
python manage.py check
python manage.py test
```

### Production Readiness Check
```powershell
$env:DJANGO_SETTINGS_MODULE="prex.settings.production"
python manage.py check --deploy
```

---

## Production Deployment with Gunicorn

Before starting the production server:

```powershell
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn prex.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
```
