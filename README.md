# PREX Crypto Tracker

PREX is a modern, high-performance full-stack cryptocurrency tracking application. It delivers live market data, instant coin search, 7-day interactive price charts, user authentication with HttpOnly cookie sessions, asynchronous email verification/password recovery flows, and personalized watchlist management.

---

## Architecture & Technology Stack

- **Backend:** Python 3.12, Django 6, Django REST Framework, Simple JWT, Gunicorn WSGI
- **Frontend:** React 19, Vite 8, React Router, Material UI, Recharts, Nginx Reverse Proxy
- **Database:** PostgreSQL 17 (with B-Tree indexes on search and ranking columns)
- **Cache Layer:** Redis 7 (`django.core.cache.backends.redis.RedisCache`) with targeted page cache invalidation
- **Background Tasks & Scheduling:** Celery & Celery Beat backed by Redis message broker
  - Asynchronous email delivery with exponential backoff (verification & password reset)
  - Periodic 5-minute CoinGecko market synchronization & caching
- **Security & Throttling:**
  - Secure HttpOnly & SameSite cookie-based refresh token rotation (zero `localStorage` token storage)
  - DRF rate limiting & throttling (`AnonRateThrottle` & `UserRateThrottle`)
  - Nginx Slowloris mitigation, response buffering, modern TLS (TLSv1.2/1.3), HSTS, and security headers
- **Containerization & CI/CD:** Docker Compose (dev & prod configurations), GitHub Actions CI/CD workflows, automated GHCR container builds, zero-downtime SSH deployments, and automated rollback health checks

---

## Repository Layout

```text
PREX/
├── .github/
│   └── workflows/
│       ├── ci.yml               # GitHub Actions CI workflow (Node 24, Python 3.12, tests & lint)
│       └── cd.yml               # GitHub Actions CD workflow (GHCR build/push, SSH deploy, rollback)
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
│   ├── Dockerfile               # Backend Docker build with Gunicorn entrypoint
│   ├── .dockerignore            # Excludes local environments (.env.*) and cache
│   ├── manage.py
│   ├── schema.sql               # PostgreSQL schema documentation
│   ├── APIs.md                  # Detailed API specification
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components (Navbar, CoinCard, ErrorBoundary, etc.)
│   │   ├── context/             # AuthContext, AlertContext, WatchlistContext
│   │   ├── pages/               # Route pages (Home, Prices, Search, Watchlist, Settings, etc.)
│   │   ├── utils/               # Centralized api.js, auth.js, formatters.js
│   │   ├── styles/              # Dedicated CSS styling
│   │   ├── App.jsx              # React Router structure
│   │   └── main.jsx             # Root entrypoint wrapped in ErrorBoundary
│   ├── Dockerfile               # Multi-stage production build (Node 24 build -> Nginx alpine)
│   ├── nginx.conf               # Nginx HTTP reverse proxy, buffering, gzip & asset caching
│   ├── nginx.ssl.conf           # Nginx TLS/SSL termination, HSTS, ACME challenge & HTTP->HTTPS
│   ├── .dockerignore            # Excludes node_modules, build artifacts, and .env.*
│   ├── .gitignore
│   ├── package.json
│   └── README.md
├── deploy/                      # Production deployment configurations
│   ├── .env.production.example  # Production environment variable reference template
│   └── systemd/prex.service     # Systemd service unit for host autostart
├── scripts/                     # Automation & operations scripts
│   ├── deploy.sh                # Zero-downtime deployment, migration & rollback manager
│   └── server-setup.sh          # One-click Ubuntu server provisioning script
├── docker-compose.yml           # Local development orchestration (with hot reloading)
├── docker-compose.prod.yml      # Production orchestration (Gunicorn, isolated DB/Redis, immutable)
├── DEPLOYMENT.md                # Comprehensive CD, secrets & production deployment guide
├── requirements.txt             # Python dependencies (Django 6.1, DRF, Celery, Gunicorn, Cryptography)
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
- **Production-Hardened Reverse Proxy:**
  - Nginx handles TLS/SSL termination with modern ciphers (TLS 1.2/1.3) and HSTS.
  - Request/response buffering protects Gunicorn from Slowloris attacks.
  - Client-side static asset caching (30 days) and automated gzip compression.
- **Asynchronous Background Processing:** Celery worker handles email delivery with automatic retries and scheduled 5-minute CoinGecko syncs.
- **Targeted Cache Management:** Automatic initial seed on empty database and targeted page key invalidation preserving session/auth cache.
- **Personalized Watchlists:** Authenticated watchlist management allowing users to create multiple watchlists, track favorite coins, and sync memberships across views with immediate UI updates (unauthenticated visitors are prompted to log in).
- **Global Error Boundary:** Root-level React Error Boundary for graceful UI crash recovery.
- **OpenAPI / Swagger Documentation:** Interactive API documentation available at `/api/v1/docs/`.

---

## Environment & Configuration Architecture

PREX uses a unified codebase with clean separation between **Local Development** and **Production**:

| Component | Local Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Docker Compose** | [`docker-compose.yml`](docker-compose.yml) (hot-reloading, exposed DB/Redis ports, HTTP) | [`docker-compose.prod.yml`](docker-compose.prod.yml) (immutable images, isolated DB/Redis, HTTPS) |
| **Nginx Proxy** | [`frontend/nginx.conf`](frontend/nginx.conf) (HTTP port 80, no SSL required) | [`frontend/nginx.ssl.conf`](frontend/nginx.ssl.conf) (HTTPS port 443, Let's Encrypt TLS & HSTS) |
| **Django Settings** | `prex.settings.local` (`DEBUG=True`, relaxed CORS) | `prex.settings.production` (`DEBUG=False`, secure cookies & strict hosts) |
| **Frontend Base URL**| `http://127.0.0.1:8000/api/v1` (Vite dev) or `/api/v1` (Docker) | `/api/v1` (Nginx reverse proxy) |

---

## Quick Start & Setup

### Prerequisites

- **Python 3.12+**
- **Node.js 24+** and **npm**
- **PostgreSQL 15+** (or Docker)
- **Redis 7+** (or Docker)
- **CoinGecko API key**
- **SMTP credentials** (e.g. Gmail App Password)

---

### Option A: Docker Compose Deployment

#### 1. Local Development Mode (Hot-Reloading)
Runs the full stack locally over HTTP. The backend mounts local directories for live code reloads:

```powershell
docker compose up --build -d
```

> [!TIP]
> To rebuild only the frontend after making React changes:
> `docker compose up -d --build frontend`

#### 2. Production Deployment Mode
Runs hardened containers with Gunicorn WSGI workers, immutable build images, internal network isolation, and TLS/SSL termination:

```powershell
docker compose -f docker-compose.prod.yml up --build -d
```

#### Access Points:
- **Frontend Application:** [http://localhost](http://localhost) (or [https://prex.duckdns.org](https://prex.duckdns.org) in production)
- **Backend REST API:** [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/) (or `/api/v1/` via Nginx proxy)
- **Swagger UI Documentation:** [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/)
- **Health Checks:**
  - Backend API: [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/)
  - Nginx Gateway: [http://localhost/healthz](http://localhost/healthz)

To view logs or stop containers:
```powershell
# Development
docker compose logs -f
docker compose down

# Production
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml down
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

# Start Django Server
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
| `DJANGO_SETTINGS_MODULE` | Active Django settings module | `prex.settings.local` / `prex.settings.production` |
| `DJANGO_SECRET_KEY` | Secret key for cryptographic signing | `<strong-secret-key>` |
| `DJANGO_ALLOWED_HOSTS` | Allowed host headers (production) | `prex.duckdns.org,localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Allowed origins for CORS | `https://prex.duckdns.org,http://localhost:5173` |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF | `https://prex.duckdns.org` |
| `DB_NAME` | PostgreSQL database name | `prex` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `127.0.0.1` (or `db` in Docker) |
| `DB_PORT` | PostgreSQL port | `5432` |
| `REDIS_CACHE_URL` | Redis URL for Django Cache backend | `redis://127.0.0.1:6379/0` (or `redis://redis:6379/0`) |
| `CELERY_BROKER_URL` | Redis broker URL for Celery | `redis://127.0.0.1:6379/0` (or `redis://redis:6379/0`) |
| `CELERY_RESULT_BACKEND` | Redis result backend for Celery | `redis://127.0.0.1:6379/0` (or `redis://redis:6379/0`) |
| `THROTTLE_ANON_RATE` | Anonymous rate limit | `30/minute` |
| `THROTTLE_USER_RATE` | Authenticated rate limit | `120/minute` |
| `EMAIL_HOST` | SMTP server host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | SMTP username / email address | `example@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password / app password | `<smtp-app-password>` |
| `EMAIL_USE_TLS` | Enable TLS encryption | `True` |
| `COINGECKO_API_KEY` | CoinGecko API key | `<your-coingecko-key>` |
| `EMAIL_VERIFICATION_URL` | Verification link redirect URL | `https://prex.duckdns.org/verify-email` |
| `PASSWORD_RESET_URL` | Password reset link redirect URL | `https://prex.duckdns.org/reset-password-confirm` |

### Frontend Configuration (`frontend/.env`)

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Base endpoint for backend API | `http://127.0.0.1:8000/api/v1` (dev) or `/api/v1` (Docker/prod) |

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

## Continuous Deployment (CD) & Production

PREX features automated Continuous Deployment powered by GitHub Actions:

- **CD Pipeline ([`.github/workflows/cd.yml`](.github/workflows/cd.yml)):** Triggered on push to `main`/`master`, release tags (`v*.*.*`), or manually via `workflow_dispatch`.
  1. **Build & Push:** Builds multi-stage Docker images with layer caching and pushes to **GitHub Container Registry (GHCR)**.
  2. **SSH Deploy:** Connects securely to the target production server (`appleboy/ssh-action`), pulls immutable image tags, executes database migrations, collects static assets, and applies zero-downtime rolling updates.
  3. **Health Checks & Rollback:** Probes `/healthz` and `/api/v1/health/` with retries. Automatically rolls back to the previous stable release if health checks fail.
  4. **Summary Reporting:** Posts a deployment report to GitHub Step Summary.

For server provisioning instructions, DuckDNS + SSL setup, and GitHub Secrets configuration, see [**`DEPLOYMENT.md`**](DEPLOYMENT.md).

---

## API Documentation

For the complete endpoint specifications, request payloads, response structures, and status codes:
- **Interactive OpenAPI/Swagger:** Visit [http://localhost:8000/api/v1/docs/](http://localhost:8000/api/v1/docs/) when running the backend.
- **Detailed Markdown Reference:** Read [`backend/APIs.md`](backend/APIs.md).
