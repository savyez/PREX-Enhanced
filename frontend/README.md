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
│   ├── components/         App shell, navigation, cards, charts and form controls
│   ├── context/            Authentication, watchlist and alert providers
│   ├── hooks/              Reusable chart-data hooks
│   ├── modals/             Confirmation and watchlist creation dialogs
│   ├── pages/              Route-level screens
│   ├── styles/             Shared, component and page stylesheets
│   ├── utils/api.js         Centralized API requests and token refresh handling
│   ├── utils/auth.js        Local session storage helpers
│   └── main.jsx             Application entry point
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

`App.jsx` creates the browser router and wraps the application with:

1. `AuthProvider` for session restoration and expiration handling
2. `AlertProvider` for temporary MUI Snackbar alerts
3. `WatchlistProvider` for watchlists and coin membership data
4. `AppContent` for the navbar, route content and footer

### Authentication

- Login stores access token, refresh token and user data in browser `localStorage`.
- The auth provider restores a saved session by calling `/current-user/`.
- `api.js` retries an authenticated request once after refreshing an expired access token.
- Failed authentication dispatches an `authfailure` event; the auth provider clears the session and redirects to `/login`.
- Logout clears local data even if server-side refresh-token revocation fails.

### Watchlists

`WatchlistProvider` loads the user’s watchlists and their items, then builds a coin membership map used by price cards, search results and the watchlist page. Add/remove/create/delete operations refresh the provider state after the API request succeeds.

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

Authenticated requests automatically use the access token from `localStorage`. The API base URL is normalized so callers can use paths with or without a leading slash.

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
- Consider a safer HttpOnly cookie session strategy instead of browser `localStorage` tokens.
- Add offline/stale-data behavior when the market-data provider is unavailable.
- Add an AI-powered, plain-language explanation of a coin’s seven-day trend, with server-side key protection, rate limiting and clear financial disclaimers.
