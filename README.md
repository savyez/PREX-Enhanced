# PREX Crypto Tracker

PREX is a full-stack cryptocurrency tracking application. It provides market data, searchable coins, seven-day price charts, user authentication, email verification and password reset flows, and user-managed watchlists.

## Stack

- **Backend:** Django 6, Django REST Framework, Simple JWT
- **Frontend:** React 19, Vite, React Router, Material UI, Recharts
- **Database:** PostgreSQL
- **Market data:** CoinGecko API
- **Email:** SMTP

## Repository Layout

```text
backend/       Django project, API, settings, migrations and tests
frontend/      React/Vite application
requirements.txt
```

## Features

- Browse paginated cryptocurrency market data
- Search coins by name or ticker
- Display seven-day price trend charts
- Register, verify email, log in, refresh sessions and log out
- Reset passwords through signed email links
- Create and delete watchlists
- Add, remove and inspect coin membership across watchlists
- Public API health endpoint at `/api/v1/health/`
- Request timeouts and error handling for CoinGecko requests

## Local Setup

### Prerequisites

- Python 3.12 or a compatible supported Python version
- Node.js and npm
- PostgreSQL
- A CoinGecko API key
- SMTP credentials for email features

### Backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example` and set the local database, email and CoinGecko values. Keep `.env` files out of Git.

Run migrations and start Django:

```powershell
cd backend
python manage.py migrate
python manage.py runserver
```

The local API is available at `http://127.0.0.1:8000/` and the versioned API at `http://127.0.0.1:8000/api/v1/`.

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
```

Create `frontend/.env` from `frontend/.env.example`. For local development, set:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Start Vite:

```powershell
npm run dev
```

The frontend normally runs at `http://localhost:5173`.

## Environment Configuration

Production should use `prex.settings.production`:

```env
DJANGO_SETTINGS_MODULE=prex.settings.production
DJANGO_SECRET_KEY=<long-random-secret-at-least-50-characters>
DJANGO_ALLOWED_HOSTS=api.example.com
CORS_ALLOWED_ORIGINS=https://app.example.com
DB_NAME=prex
DB_USER=postgres
DB_PASSWORD=<database-password>
DB_HOST=<postgres-host>
DB_PORT=5432
COINGECKO_API_KEY=<coingecko-key>
EMAIL_VERIFICATION_URL=https://app.example.com/verify-email
EMAIL_VERIFICATION_SUCCESS_URL=https://app.example.com/login
```

Set secrets through the deployment platform’s secret manager or environment settings. Do not commit real secrets to source control.

Generate a Django secret key with:

```powershell
python -c "from secrets import token_urlsafe; print(token_urlsafe(64))"
```

The frontend production build requires `VITE_API_BASE_URL`:

```powershell
$env:VITE_API_BASE_URL="https://api.example.com/api/v1"
npm run build
```

## Validation Commands

### Frontend

```powershell
cd frontend
npm run lint
npm run build
```

### Backend

```powershell
cd backend
python manage.py check
python manage.py test
```

For production settings, make sure the required environment variables are present and run:

```powershell
$env:DJANGO_SETTINGS_MODULE="prex.settings.production"
python manage.py check --deploy
```

## Production Deployment

Run these commands during the release/deploy phase, after production environment variables and PostgreSQL are available:

```powershell
cd backend
python manage.py check --deploy
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Serve the generated `backend/staticfiles/` directory at `/static/`, then start Django with a production WSGI server, for example:

```text
gunicorn prex.wsgi:application
```

Deploy the frontend build output from `frontend/dist/` through a static host or web server. Configure the web server to support client-side route fallback to `index.html` for React Router routes.

Use `/api/v1/health/` as the load balancer or platform health-check URL. The endpoint is public and does not require authentication.

## API Areas

For detailed endpoints, request bodies, response examples and error codes, [click on `backend/APIs.md` for API information](backend/APIs.md).

The versioned API is mounted at `/api/v1/` and includes:

- `/coins/`
- `/coins/search/<coin_id>/`
- `/coins/<coin_id>/chart/`
- `/register/`, `/login/`, `/token/refresh/`, `/logout/`
- `/verify/<token>/`, `/reset-password/`, `/reset-password-confirm/<token>/`
- `/current-user/` and `/users/<user_id>/`
- `/watchlists/...`
- `/health/`

Authentication-protected endpoints use the JWT access token in the `Authorization: Bearer <token>` header.

## Future Issues and Follow-up Work

These are simple next steps for improving the project:

- Add a CI/CD workflow that runs the frontend lint/build and backend tests automatically.
- Add a clear deployment setup, such as Docker or a hosting-platform configuration.
- Add more tests for login, expired tokens, watchlists and important user journeys.
- Replace browser `localStorage` tokens with a safer HttpOnly cookie session design.
- Add basic monitoring so API, email and CoinGecko failures are easier to find.
- Improve the UI with more accessibility and keyboard-navigation checks.
- Add an AI assistant that explains a coin’s recent seven-day trend in plain language and answers questions about the user’s watchlists. Any AI feature should use protected API keys, clear disclaimers and rate limits.

## Security Notes

- Never commit `.env`, database credentials, SMTP passwords, JWT secrets or API keys.
- Use HTTPS in production. Production settings enable SSL redirect, secure cookies and HSTS.
- Keep `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` narrowly scoped to real deployment domains.
- Rotate any secret that has been exposed in a terminal, screenshot, chat or repository history.
