# PREX Frontend

The PREX frontend is a modern React single-page application built with Vite. It provides cryptocurrency market browsing, instant coin search, 7-day interactive price charts, authenticated profile & watchlist management, responsive navigation, MUI alert notifications, and containerized Nginx reverse proxy deployment with full TLS/SSL termination support.

---

## Technology Stack

- **React 19**
- **Vite 8**
- **React Router**
- **Material UI (MUI)** & Emotion
- **Recharts** (interactive 7-day price charts)
- **Nginx** (Alpine-based reverse proxy, static asset server & TLS termination)

---

## Project Structure

```text
frontend/
├── public/                 # Static public assets, favicon and icons
├── src/
│   ├── assets/             # CoinGecko attribution branding and vector images
│   ├── components/         # Reusable UI components (Navbar, CoinCard, ErrorBoundary, etc.)
│   ├── context/            # AuthContext, AlertContext, and WatchlistContext providers
│   ├── hooks/              # Reusable hooks (useChartData, etc.)
│   ├── modals/             # Modal dialogs (Create Watchlist, Delete Confirmation, etc.)
│   ├── pages/              # Route-level page components
│   │   ├── Home.jsx            # Landing hero & market overview
│   │   ├── Prices.jsx          # Paginated cryptocurrency market list
│   │   ├── Search.jsx          # Search results and coin charting screen
│   │   ├── Watchlist.jsx       # Personalized watchlist management
│   │   ├── Login.jsx           # User authentication login
│   │   ├── Register.jsx        # User account registration
│   │   ├── VerifyEmail.jsx     # Email token verification
│   │   ├── PasswordReset.jsx   # Password reset request & confirmation
│   │   ├── Profile.jsx         # User profile settings
│   │   └── ...
│   ├── styles/             # Shared component and page stylesheets
│   ├── utils/
│   │   ├── api.js              # Centralized API fetch wrapper with silent token refresh
│   │   ├── auth.js             # In-memory access token storage and auth utilities
│   │   └── formatters.js       # Centralized number, currency, and date formatters
│   ├── App.jsx             # React Router layout and route definitions
│   └── main.jsx            # Application entry point wrapped in ErrorBoundary
├── Dockerfile              # Multi-stage build (Node 24 build -> Nginx Alpine)
├── nginx.conf              # HTTP reverse proxy, buffering, gzip, security headers & asset caching
├── nginx.ssl.conf          # HTTPS/TLS termination, HTTP->HTTPS redirect, HSTS & ACME challenge
├── .dockerignore           # Excludes node_modules, build artifacts, and .env.*
├── .env.example
├── eslint.config.js
├── package.json
└── vite.config.js
```

---

## Requirements

- **Node.js 24+** and **npm**
- Running **PREX Backend API**

Install dependencies from `frontend/`:

```powershell
npm install
```

---

## Environment Configuration

Create `frontend/.env` from `frontend/.env.example`.

### Local Development:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### Production / Docker:
```env
VITE_API_BASE_URL=/api/v1
```

> [!NOTE]
> Only environment variables prefixed with `VITE_` are exposed to the browser client code. Never store secrets in frontend environment files.

---

## Development

Start the local Vite development server:

```powershell
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Application Routes

| Route | Purpose | Access |
| :--- | :--- | :--- |
| `/` | Landing page and market overview | Public |
| `/prices` | Paginated cryptocurrency market list | Public |
| `/search` | Coin search interface | Public |
| `/coins/search/:coinId` | Coin details and 7-day interactive chart | Public |
| `/watchlist` | Personalized watchlist management | Authenticated |
| `/login` | User login screen | Public |
| `/register` | Account registration form | Public |
| `/verification-pending` | Verification guidance screen | Public |
| `/verify-email` | Email verification token handler | Public |
| `/reset-password` | Password reset request | Public |
| `/reset-password-confirm` | Password reset confirmation | Public |
| `/profile` | User profile management | Authenticated |
| `/settings` | Account settings | Authenticated |
| `/logout` | Clears user session and logs out | Authenticated |
| `/about` | About PREX | Public |
| `/contact` | Contact support | Public |
| `/privacy` | Privacy policy | Public |

All route components are lazy-loaded with `React.lazy()` and wrapped in a shared `Suspense` loading fallback.

---

## Core Architecture & Components

### 1. Error Boundary & UI Resilience
`src/components/ErrorBoundary.jsx` wraps the root React application:
- Intercepts uncaught runtime rendering errors (e.g. malformed chart data or network timeouts).
- Prevents full-screen whiteout crashes by providing a friendly fallback screen.
- Offers direct user recovery actions: **Try Again** (resets component error state), **Reload Page**, and **Go to Home**.
- Displays formatted stack traces exclusively in development mode (`import.meta.env.DEV`).

### 2. Authentication & Token Security Architecture
- **HttpOnly Refresh Cookies**: Refresh tokens are stored strictly in `HttpOnly`, `SameSite=Lax`, `Secure` browser cookies issued by Django, eliminating JavaScript token access and preventing XSS vulnerabilities.
- **In-Memory Access Tokens**: Short-lived JWT access tokens are held strictly in memory (`inMemoryAccessToken` closure) and never written to `localStorage` or `sessionStorage`.
- **Silent Refresh**: On page load, `AuthProvider` calls `POST /api/v1/auth/token/refresh/` using `credentials: 'include'` to restore the user session seamlessly.
- **Request Interception & Automatic Retry**: `api.js` catches `401 Unauthorized` responses, triggers a silent refresh, updates the in-memory access token, and transparently retries the initial request.

### 3. Watchlist State Synchronization & Access Control
- **Authentication Protected**: Unauthenticated visitors accessing `/watchlist` are presented with a clear prompt ("You need to login to see/create watchlist") and a direct **Login** button redirecting them to `/login`.
- `WatchlistProvider` manages state for watchlists with immediate, optimistic UI updates.
- Adding or removing coins uses the payload returned directly from the backend, avoiding redundant full `getWatchlists` network requests.
- A reactive `membershipMap` is derived synchronously via `useMemo`, ensuring `Add to Watchlist` / `Manage (N)` buttons update instantly across cards and search results.

### 4. Consolidated Formatting Utilities (`formatters.js`)
- `formatPrice(price)`: Localized decimal precision (2 decimal places for large prices, up to 6 for micro-cap tokens).
- `formatPriceChange(change)`: Signed 24-hour percentage strings (e.g. `+3.45%`, `-1.20%`).
- `getPriceChangeClass(change)`: Returns semantic CSS class names (`price-up`, `price-down`, `price-neutral`).
- `formatCurrency(amount)`: USD currency string formatter.
- `formatTime(date)`: 12-hour AM/PM timestamp string formatter.

---

## Nginx Reverse Proxy & Environment Configurations

The frontend container image (`frontend/Dockerfile`) utilizes a multi-stage build:
1. **Build Stage:** Installs Node 24 dependencies and compiles the Vite application into static assets (`dist/`).
2. **Runtime Stage:** Copies compiled assets into an Alpine Nginx image with reverse proxy configurations.

### 1. Development / Default HTTP Configuration (`nginx.conf`)
- **Default in Dockerfile**: Default container builds use `nginx.conf` so the app runs out-of-the-box locally on port 80 without requiring SSL certificates.
- **Slowloris Mitigation**: Configures `proxy_buffering on` with 128k/256k buffers to isolate upstream Gunicorn workers.
- **Connection Keepalive**: Upstream keepalive connection pool (`keepalive 32`) to the backend service.
- **Static Asset Caching**: 30-day client browser caching (`Cache-Control: public, no-transform`) for JavaScript bundles, CSS, images, and fonts.
- **Gzip Compression**: Compresses text, JSON, JS, CSS, and SVG payloads.
- **SPA Routing Fallback**: `try_files $uri $uri/ /index.html` ensures client-side routing works on direct page navigation and refreshes.
- **Liveness Probe**: Fast `/healthz` endpoint returning HTTP 200 for health checks.

### 2. Production HTTPS & TLS Termination (`nginx.ssl.conf`)
- **Modern Cryptography**: Enforces `TLSv1.2` and `TLSv1.3` protocols and modern forward-secret ciphers.
- **Automatic 301 Redirect**: Redirects all port 80 (HTTP) traffic to port 443 (HTTPS) while preserving query paths.
- **Let's Encrypt Support**: Passes `/.well-known/acme-challenge/` to `/var/www/certbot` for automated SSL renewals.
- **Enterprise Security Headers**: Sets `Strict-Transport-Security` (HSTS), `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`, and `Referrer-Policy`.
- **Certificate Mounting**: Mounted in `docker-compose.prod.yml` at `/etc/nginx/ssl/live/fullchain.pem` and `/etc/nginx/ssl/live/privkey.pem`.

---

## Scripts Reference

```powershell
# Start local development server
npm run dev

# Run ESLint validation
npm run lint

# Build optimized production bundle to dist/
npm run build

# Preview the production build locally
npm run preview
```
