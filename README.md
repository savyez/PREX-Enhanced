# PREX Crypto Tracker

PREX is a modern, high-performance full-stack cryptocurrency tracking application. It delivers live market data, instant coin search, 7-day interactive price charts, user authentication with HttpOnly cookie sessions, asynchronous email verification/password recovery flows, and personalized watchlist management.

---

## Architecture & Technology Stack

- **Backend:** Python 3.12, Django 6, Django REST Framework, Simple JWT
- **Frontend:** React 19, Vite, React Router, Material UI, Recharts
- **Database:** PostgreSQL (with B-Tree indexes on search and ranking columns)
- **Cache Layer:** Redis (`django.core.cache.backends.redis.RedisCache`) with targeted page cache invalidation
- **Background Tasks & Scheduling:** Celery & Celery Beat backed by Redis message broker
  - Asynchronous email delivery with exponential backoff (verification & password reset)
  - Periodic 5-minute CoinGecko market synchronization & caching
- **Security & Throttling:**
  - Secure HttpOnly & SameSite cookie-based refresh token rotation (zero `localStorage` storage)
  - DRF rate limiting & throttling (`AnonRateThrottle` & `UserRateThrottle`)
- **Containerization & CI/CD:** Docker Compose multi-container architecture and GitHub Actions CI workflow

---

## Repository Layout

```text
PREX/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow (Node 24, Python 3.12)
├── backend/
│   ├── api/
│   │   ├── migrations/          # Django database migrations
│   │   ├── templates/           # Verification and password-reset email templates
│   │   ├── services/            # Domain service layers
│   │   │   ├── auth_service.py      # Registration, auth, HttpOnly cookies & password recovery
│   │   │   ├── coingecko.py         # CoinGecko client, search, charts & timeout handling
│   │   │   └── email_service.py     # Email rendering and SMTP dispatching
│   │   ├── views/               # Modular class-based API views
│   │   │   ├── auth_views.py        # Authentication and user profile views
│   │   │   ├── market_views.py      # Paginated coin lists, search and charts
│   │   │   ├── watchlist_views.py   # Watchlist CRUD, membership and item operations
│   │   │   └── system_views.py      # Health check and API root views
│   │   ├── tests/               # Comprehensive class-based test suites (37 tests)
│   │   │   ├── base.py              # Base test case with auth helpers & eager settings
│   │   │   ├── test_auth.py         # Registration, login, cookie rotation, reset tests
│   │   │   ├── test_market.py       # Coin lists, search, charts & Celery task tests
│   │   │   ├── test_watchlist.py    # Watchlist CRUD, items & permission tests
│   │   │   ├── test_services.py     # CoinGecko, Auth & Celery email task tests
│   │   │   └── test_system.py       # Health check, OpenAPI schema & rate-limiting tests
│   │   ├── models.py            # User, Coin, Watchlist and WatchlistItem models
│   │   ├── serializers.py       # DRF request and response serializers
│   │   ├── paginations.py       # Standard pagination utilities
│   │   ├── tasks.py             # Celery background tasks (market sync, email delivery)
│   │   └── urls.py              # Versioned API routes (/api/v1/)
│   ├── prex/                    # Django project settings (base, local, production) & celery.py
│   ├── manage.py
│   ├── schema.sql               # PostgreSQL schema documentation
│   └── APIs.md                  # Detailed API specification
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components (Navbar, CoinCard, ErrorBoundary, etc.)
│   │   ├── context/             # AuthContext, AlertContext, WatchlistContext
│   │   ├── pages/               # Route pages (Home, Prices, Search, Watchlist, Settings, etc.)
│   │   ├── utils/               # Centralized api.js, auth.js, formatters.js
│   │   ├── styles/              # Dedicated CSS styling
│   │   ├── App.jsx              # React Router structure
│   │   └── main.jsx             # Root entrypoint wrapped in ErrorBoundary
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml           # Multi-container orchestration (DB, Redis, Backend, Celery, Frontend)
├── requirements.txt             # Python dependencies
└── README.md
```

---

## Core Features

- **Live Market Data & Fast Pagination:** Paginated cryptocurrency data backed by Redis cache and database ranking indexes.
- **Search & Charting:** Instant search across coin tickers/names and historical 7-day price charts via Recharts.
- **Robust Authentication & Security:**
  - Registration with signed email verification tokens.
  - HttpOnly and SameSite cookie refresh token rotation.
  - Password recovery with signed expirable reset tokens.
  - Public endpoint rate limiting against brute-force attacks.
- **Asynchronous Background Processing:** Celery worker handles email delivery with automatic retries and scheduled 5-minute CoinGecko syncs.
- **Targeted Cache Management:** Automatic initial seed on empty database and targeted page key invalidation preserving session/auth cache.
- **Personalized Watchlists:** Create multiple watchlists, add/remove coins, and track coin memberships with synchronous UI updates.
- **Global Error Boundary:** Root-level React Error Boundary for graceful UI crash recovery.
- **OpenAPI / Swagger Documentation:** Interactive API documentation available at `/api/v1/docs/`.

---

## Quick Start & Local Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 20+** and **npm**
- **PostgreSQL 15+**
- **Redis 7+**
- **CoinGecko API key**
- **SMTP credentials** (e.g. Gmail App Password)

---

### Option A: Docker Compose (Recommended)

Run the entire application stack with a single command:

```powershell
docker compose up --build -d
```

#### Access Points:
- **Frontend Application:** [http://localhost](http://localhost)
- **Backend REST API:** [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **Swagger UI Documentation:** [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)
- **Health Check:** [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/)

To view logs or stop containers:
```powershell
docker compose logs -f
docker compose down
```

---

### Option B: Manual Local Setup

#### 1. Backend Setup

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your PostgreSQL, Redis, SMTP and CoinGecko credentials

# Apply migrations
cd backend
python manage.py migrate

# Start Celery Worker (in a separate terminal)
celery -A prex worker --loglevel=info

# Start Celery Beat (in a separate terminal)
celery -A prex beat --loglevel=info

# Start Django Development Server
python manage.py runserver 127.0.0.1:8000
```

#### 2. Frontend Setup

```powershell
cd frontend
npm install

# Configure environment variables
cp .env.example .env
# Set VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1

# Start Vite dev server
npm run dev
```

The frontend will start at `http://localhost:5173`.

---

## Environment Variables

### Backend Configuration (`backend/.env` / `.env.docker`)

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `DJANGO_SETTINGS_MODULE` | Active Django settings module | `prex.settings.local` |
| `DJANGO_SECRET_KEY` | Secret key for cryptographic signing | `<strong-secret-key>` |
| `DB_NAME` | PostgreSQL database name | `prex` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `127.0.0.1` (or `db` in Docker) |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_CACHE_URL` | Redis URL for Django Cache backend | `redis://127.0.0.1:6379/0` |
| `CELERY_BROKER_URL` | Redis broker URL for Celery | `redis://127.0.0.1:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend for Celery | `redis://127.0.0.1:6379/0` |
| `THROTTLE_ANON_RATE` | Anonymous rate limit | `30/minute` |
| `THROTTLE_USER_RATE` | Authenticated rate limit | `120/minute` |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username / email address | `example@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password / app password | `<smtp-app-password>` |
| `EMAIL_USE_TLS` | Enable TLS encryption | `True` |
| `COINGECKO_API_KEY` | CoinGecko API key | `<your-coingecko-key>` |
| `EMAIL_VERIFICATION_URL` | Verification link redirect URL | `http://localhost:5173/verify-email` |
| `PASSWORD_RESET_URL` | Password reset link redirect URL | `http://localhost:5173/reset-password-confirm` |

### Frontend Configuration (`frontend/.env`)

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Base endpoint for backend API | `http://127.0.0.1:8000/api/v1` (or `/api/v1` in Docker) |

---

## Testing & Quality Checks

Run the automated test suites and linters locally before pushing changes:

### Backend Validation
```powershell
cd backend
python manage.py check
python manage.py test
```

### Frontend Validation
```powershell
cd frontend
npm run lint
npm run build
```

---

## API Documentation

For the complete endpoint specifications, request payloads, response structures, and status codes:
- **Interactive OpenAPI/Swagger:** Visit [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/) when running the backend.
- **Detailed Markdown Reference:** Read [`backend/APIs.md`](backend/APIs.md).
