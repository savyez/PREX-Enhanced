import { clearAuth } from './auth';

let refreshPromise = null;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';


// Redirect to login page and clear authentication data
const redirectToLogin = () => {
  clearAuth();
  window.location.replace('/login');
};

// Build full API URL from path
const buildUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL.replace(/\/$/, '')}${normalizedPath}`;
};


// Get authorization headers with the current access token
const getAuthHeaders = () => {
  const accessToken = localStorage.getItem('access_token');
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
};


// Centralized API request function with automatic token refresh
const apiFetch = async (path, options = {}, retry = true) => {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
    ...options.headers,
  };

  const response = await fetch(buildUrl(path), {
    ...options,
    headers,
  });

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : null;

  // Handle expired access token
  if (
    retry &&
    localStorage.getItem('access_token') &&
    response.status === 401 &&
    data?.code === 'token_not_valid'
  ) {
    await refreshAccessToken();
    return apiFetch(path, options, false);
  }

  // Handle other errors
  if (!response.ok) {
    const message = data?.error || data?.detail || data?.message || 'Request failed';

    throw new Error( Array.isArray(message) ? message.join(' ') : message );
  }

  return data;
};

// Refresh access token using the refresh token
const refreshAccessToken = async () => {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');

      if (!refresh) {
        redirectToLogin();
        throw new Error('No refresh token');
      }

      const response = await fetch (buildUrl('/token/refresh/'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            refresh,
          }),
        }
      );

      if (!response.ok) {
        redirectToLogin();
        throw new Error('Session expired');
      }

      const data = await response.json();

      if (!data.access) {
        redirectToLogin();
        throw new Error('Invalid refresh response');
      }

      localStorage.setItem( 'access_token', data.access );

      if (data.refresh) {
        localStorage.setItem( 'refresh_token', data.refresh );
      }

      return data.access;

    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
};


// API functions for authentication and watchlist management
const login = (credentials) => (
  apiFetch('/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
);


// Note: The register function is currently unused, but it's included here for completeness and future use.
const register = (userData) => (
  apiFetch('/register/', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
);


// Note: The logout function is currently unused, but it's included here for completeness and future use.
const logout = () =>
  apiFetch('/logout/', {
    method: 'POST',
    body: JSON.stringify({
      refresh_token: localStorage.getItem('refresh_token'),
    }),
  });


// Fetch list of coins from the API
const getCoins = () => apiFetch('/coins/');


// Fetch watchlists for a specific user
const getWatchlists = (userId) => apiFetch(`/watchlists/${userId}/`);


// Fetch coins in a specific watchlist
const getWatchlistItems = (watchlistId) => apiFetch(`/watchlists/${watchlistId}/items/`);


// Add a coin to a specific watchlist
const addCoinToWatchlist = (userId, watchlistId, ticker) =>
  apiFetch('/watchlists/add-coin/', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      watchlist_id: watchlistId,
      ticker: ticker,
    }),
  });


// Remove a coin from a specific watchlist
const removeCoinFromWatchlist = (userId, watchlistId, ticker) =>
  apiFetch('/watchlists/remove-coin/', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      watchlist_id: watchlistId,
      ticker: ticker,
    }),
  });


export { 
  apiFetch, 
  login, 
  register, 
  logout, 
  getCoins, 
  getWatchlists, 
  getWatchlistItems, 
  addCoinToWatchlist, 
  removeCoinFromWatchlist 
};
