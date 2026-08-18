# PREX Frontend

The PREX frontend is a React single-page application built with Vite. It provides cryptocurrency browsing and search, seven-day price charts, authentication screens, profile settings, watchlist management, responsive navigation, MUI alert notifications, and containerized Nginx reverse proxy deployment with TLS/SSL termination support.

## Stack

- React 19
- Vite 8
- React Router
- Material UI and Emotion
- Recharts
- Nginx (Alpine-based reverse proxy and static asset server)

## Project Structure

```text
frontend/
├── public/                 Static files and icons
├── src/
│   ├── assets/             Images such as the CoinGecko attribution asset
│   ├── components/         App shell, ErrorBoundary, navigation, cards, charts and form controls
│   ├── context/            Authentication, watchlist and alert providers
│   ├── hooks/              Reusable chart-data hooks
│   ├── modals/             Confirmation and watchlist creation dialogs
│   ├── pages/              Route-level screens
│   ├── styles/             Shared, component and page stylesheets
│   ├── utils/api.js        Centralized API requests with silent token refresh
│   ├── utils/auth.js       In-memory authentication state helpers
│   ├── utils/formatters.js Consolidated number, currency, and time formatters
│   └── main.jsx            Application entry point wrapped in ErrorBoundary
├── Dockerfile              Multi-stage build (Node 24 build -> Nginx Alpine)
├── nginx.conf              HTTP reverse proxy, buffering, gzip, security headers & asset caching
├── nginx.ssl.conf          HTTPS/TLS termination, HTTP->HTTPS redirect, HSTS & ACME challenge
├── .dockerignore           Excludes node_modules, build artifacts, and .env.*
├── .env.example
├── eslint.config.js
├── package.json
└── vite.config.js
```

## Requirements

- Node.js 24+ and npm
- A running PREX backend API

Install dependencies from this directory:

```powershell
npm install
```

## Environment Configuration

Create `frontend/.env` from `frontend/.env.example`.

For local development:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

For production or Docker Compose:

```env
VITE_API_BASE_URL=/api/v1
```

The production Vite build fails when `VITE_API_BASE_URL` is missing. Only variables prefixed with `VITE_` are exposed to browser code, so never put private secrets in frontend environment files.

## Development

Start the development server:

```powershell
npm run dev
```

Vite normally serves the application at `http://localhost:5173`.

The backend must allow the frontend origin through `CORS_ALLOWED_ORIGINS`.

## Application Routes

| Route | Purpose |
|---|---|
| `/` | Home page |
| `/prices` | Paginated cryptocurrency market data |
| `/search` | Search screen before a query is selected |
| `/coins/search/:coinId` | Search results and seven-day chart for a query |
| `/watchlist` | Authenticated watchlist management |
| `/login` | Login form |
| `/register` | Registration form |
| `/verification-pending` | Email verification guidance |
| `/profile` | Authenticated profile update screen |
| `/settings` | Authenticated account settings |
| `/logout` | Clears the local session and attempts server logout |
| `/about` | About page |
| `/contact` | Contact page |
| `/privacy` | Privacy page |

Routes are lazy-loaded with `React.lazy` and rendered inside a shared `Suspense` loading state.

## Application Flow

### App Shell

`main.jsx` wraps the application in a global `ErrorBoundary` to gracefully catch unhandled component crashes. `App.jsx` creates the browser router and wraps the component tree with:

1. `AuthProvider` for session restoration and expiration handling
2. `AlertProvider` for temporary MUI Snackbar alerts
3. `WatchlistProvider` for watchlists and coin membership data
4. `AppContent` for the navbar, route content and footer

### Error Boundary & Recovery

`src/components/ErrorBoundary.jsx` wraps the React root:
- Intercepts uncaught runtime errors (e.g. malformed chart payloads, modal rendering exceptions) to prevent full-screen blank page crashes.
- Provides accessible recovery actions: **Try Again** (resets local error state), **Reload Page**, and **Go to Home**.
- Renders detailed stack traces exclusively in development mode (`import.meta.env.DEV`).
- Supports an optional `fallback` prop for isolated component boundaries.

### Authentication & Token Security

- **HttpOnly Refresh Tokens**: Refresh tokens are stored strictly in `HttpOnly`, `SameSite=Lax`, `Secure` browser cookies set by Django, preventing token theft via XSS.
- **Zero LocalStorage Tokens**: No tokens or sensitive user credentials are saved in browser `localStorage`.
- **In-Memory Access Tokens**: Short-lived JWT access tokens are held strictly in memory (`inMemoryAccessToken` closure).
- **Silent Rotation**: Outgoing fetch requests use `credentials: 'include'`. The `AuthProvider` automatically restores sessions on reload via `POST /token/refresh/`.
- **Automatic Retries**: `api.js` intercepts `401 Unauthorized` responses and silently refreshes the access token once before retrying the original request.
- **Expiration Handling**: Dispatches an `authfailure` event to cleanly clear state and redirect users to `/login`.

### Watchlists & State Synchronization

- `WatchlistProvider` manages watchlists and provides immediate, optimistic-like updates:
  - Adding or removing coins consumes the updated watchlist returned directly by the backend endpoint, avoiding redundant full `getWatchlists` roundtrips.
  - A reactive `membershipMap` is derived synchronously via `useMemo`, ensuring `Add to Watchlist` / `Manage (N)` buttons update instantly across cards and search results.

### Formatting Utilities (DRY Principle)

`src/utils/formatters.js` provides centralized, reusable formatting functions:
- `formatPrice(price)`: Localized decimal precision (2 decimal places for integers, up to 6 for float prices).
- `formatPriceChange(change)`: Signed 24-hour percentage strings (e.g., `+2.50%` or `-1.20%`).
- `getPriceChangeClass(change)`: Returns semantic CSS class names (`price-up`, `price-down`, `price-neutral`).
- `formatCurrency(amount)`: USD currency string formatter.
- `formatTime(date)`: 12-hour AM/PM timestamp string formatter.

### Alerts

Use `useAlert()` for user-facing action feedback:

```jsx
const { showAlert } = useAlert();
showAlert('Coin added to your watchlist.', 'success');
```

Alerts are rendered in a top-right MUI Snackbar, automatically fade out after three seconds, and support `success`, `info`, `warning`, and `error` severities.

## Nginx Reverse Proxy & Production Server

The frontend image uses a multi-stage Docker build (`frontend/Dockerfile`) that builds the Vite SPA using Node 24 and packages the resulting static assets into an optimized `nginx:alpine` image.

### 1. Standard HTTP & Reverse Proxy Configuration (`nginx.conf`)
- **Slowloris Mitigation & Buffering**: Configures `proxy_buffering on` with 128k/256k buffers to isolate Gunicorn workers from slow client connections.
- **Connection Keepalive**: Upstream keepalive connection pool (`keepalive 32`) to the backend service.
- **Static Asset Caching**: 30-day client browser caching (`Cache-Control: public, no-transform`) for JavaScript bundles, CSS, images, and fonts.
- **Gzip Compression**: Compresses text, JSON, JS, CSS, and SVG payloads on the fly.
- **SPA Routing Fallback**: `try_files $uri $uri/ /index.html` ensures client-side routing works seamlessly on direct page visits and refreshes.
- **Health Check**: Fast, unlogged `/healthz` endpoint returning HTTP 200 for cloud load balancers.

### 2. HTTPS & TLS Termination Configuration (`nginx.ssl.conf`)
- **Modern Cryptography**: Enforces `TLSv1.2` and `TLSv1.3` protocols and modern forward-secret ciphers.
- **Automatic 301 Redirect**: Redirects all port 80 (HTTP) traffic to port 443 (HTTPS) while preserving query paths.
- **Let's Encrypt Support**: Passes `/.well-known/acme-challenge/` to `/var/www/certbot` for automated SSL renewals.
- **Enterprise Security Headers**: Sets `Strict-Transport-Security` (HSTS), `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, and `Referrer-Policy`.
- **Certificate Mounting**: Expects certificate files at:
  - `/etc/nginx/ssl/live/fullchain.pem`
  - `/etc/nginx/ssl/live/privkey.pem`

## Scripts

Run these from `frontend/`:

```powershell
# Start Vite development mode
npm run dev

# Run ESLint across the frontend
npm run lint

# Create an optimized production build in dist/
npm run build

# Preview the production build locally
npm run preview
```

## Production Build

Set the production API URL before building:

```powershell
$env:VITE_API_BASE_URL="/api/v1"
npm run lint
npm run build
```

Deploy the generated `dist/` directory or run the containerized service via `docker-compose.prod.yml`.

## Safety & Best Practices

- Do not place API keys, database credentials or Django secrets in `VITE_` variables.
- Use HTTPS for all production deployments (`nginx.ssl.conf`).
- Configure backend `CORS_ALLOWED_ORIGINS` to strictly match your production domain.
- Never store tokens in `localStorage` or `sessionStorage` (handled automatically via HttpOnly cookies and in-memory tokens).
