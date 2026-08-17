# PREX Frontend

The PREX frontend is a React single-page application built with Vite. It provides cryptocurrency browsing and search, seven-day price charts, authentication screens, profile settings, watchlist management, responsive navigation, and MUI alert notifications.

## Stack

- React 19
- Vite 8
- React Router
- Material UI and Emotion
- Recharts

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
├── .env.example
├── eslint.config.js
├── package.json
└── vite.config.js
```

## Requirements

- Node.js and npm
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

For production, use the deployed API origin and versioned path:

```env
VITE_API_BASE_URL=https://api.example.com/api/v1
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

### App shell

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

## API Client

All frontend requests should go through `src/utils/api.js`. It provides helpers for:

- Authentication and token refresh
- Current-user and profile operations
- Market data and coin search
- Chart data
- Watchlist CRUD and membership
- Password-reset requests

Authenticated requests automatically use the in-memory access token. The API base URL is normalized so callers can use paths with or without a leading slash.

For endpoint details and request/response examples, see [`../backend/APIs.md`](../backend/APIs.md).

## Charts and Loading States

`CoinChart` fetches chart data through the API client and renders `SparklineChart` using Recharts. Charts support compact card views and full search-page views with axes. Trend loading, unavailable data and API errors have dedicated visual states.

The chart remark explains that the chart represents the net change over seven days.

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

The project currently has no dedicated frontend unit-test script. Backend integration tests cover API behavior; frontend testing should be added as the UI grows.

## Production Build

Set the production API URL before building:

```powershell
$env:VITE_API_BASE_URL="https://api.example.com/api/v1"
npm run lint
npm run build
```

Deploy the generated `dist/` directory to a static host or web server. Because this is a client-side routed application, configure the host to serve `index.html` for unknown frontend routes such as `/prices`, `/profile`, and `/coins/search/bitcoin`.

The Vite configuration splits large vendor groups into separate chunks for React, MUI/Emotion, Recharts and other dependencies.

## Frontend Safety Notes

- Do not place API keys, database credentials or Django secrets in `VITE_` variables.
- Use HTTPS for the deployed frontend and backend.
- Configure the backend CORS allowlist for the exact frontend origin.
- Treat browser-stored tokens as sensitive and avoid logging them.
- Replace placeholder API URLs before a production build.

## Future Frontend Work

- Add component and end-to-end tests for login, token expiry, watchlists and alerts.
- Improve keyboard focus handling and accessibility checks for modals and navigation.
- Add offline/stale-data behavior when the market-data provider is unavailable.
- Add an AI-powered, plain-language explanation of a coin’s seven-day trend, with server-side key protection, rate limiting and clear financial disclaimers.
