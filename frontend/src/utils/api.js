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

const apiFetch = async (path, options = {}, retry = true) => {
  const {
    auth = true,
    redirectOnAuthFailure = false,
    headers: customHeaders = {},
    ...fetchOptions
  } = options;

  const headers = {
    'Content-Type': 'application/json',
    ...customHeaders,
  };

  if (auth) {
    Object.assign(headers, getAuthHeaders());
  }

  const response = await fetch(buildUrl(path), {
    ...fetchOptions,
    headers,
  });

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : null;

  if (
    retry &&
    auth &&
    localStorage.getItem('access_token') &&
    response.status === 401 &&
    data?.code === 'token_not_valid'
  ) {
    try {
      await refreshAccessToken();
      return apiFetch(path, options, false);
    } catch (error) {
      if (redirectOnAuthFailure) {
        redirectToLogin();
      }
      throw error;
    }
  }

  if (!response.ok) {
    if (
      auth &&
      redirectOnAuthFailure &&
      response.status === 401
    ) {
      redirectToLogin();
    }

    const message = data?.error || data?.detail || data?.message || 'Request failed';
    throw new Error(Array.isArray(message) ? message.join(' ') : message);
  }

  return data;
};

const apiNoAuth = async (path, options = {}) => apiFetch(path, {
  ...options,
  auth: false,
  redirectOnAuthFailure: false,
});

const apiAuth = async (path, options = {}) => apiFetch(path, {
  ...options,
  auth: true,
  redirectOnAuthFailure: true,
});

// Refresh access token using the refresh token
const refreshAccessToken = async () => {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const refresh = localStorage.getItem('refresh_token');

      if (!refresh) {
        clearAuth();
        throw new Error('No refresh token');
      }

      const response = await fetch(buildUrl('/token/refresh/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh }),
      });

      if (!response.ok) {
        clearAuth();
        throw new Error('Session expired');
      }

      const data = await response.json();

      if (!data.access) {
        clearAuth();
        throw new Error('Invalid refresh response');
      }

      localStorage.setItem('access_token', data.access);

      if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
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
  apiNoAuth('/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
);


// Note: The register function is currently unused, but it's included here for completeness and future use.
const register = (userData) => (
  apiNoAuth('/register/', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
);


// Note: The logout function is currently unused, but it's included here for completeness and future use.
const logout = () =>
  apiNoAuth('/logout/', {
    method: 'POST',
    body: JSON.stringify({
      refresh_token: localStorage.getItem('refresh_token'),
    }),
  });


// Fetch list of coins from the API
const getCoins = (page = 1, pageSize = 25) =>
  apiNoAuth(`/coins/?page=${page}&page_size=${pageSize}`);


// Fetch watchlists for a specific user
const getWatchlists = (userId) => apiAuth(`/watchlists/${userId}/`);


// Fetch coins in a specific watchlist
const getWatchlistItems = (watchlistId) => apiAuth(`/watchlists/${watchlistId}/items/`);

// Get membership for a specific coin ticker for the current authenticated user
const getWatchlistMembershipForCoin = (ticker) => apiAuth(`/watchlists/membership/${encodeURIComponent(ticker)}/`);


// Add a coin to a specific watchlist
const addCoinToWatchlist = (userId, watchlistId, ticker) =>
  apiAuth('/watchlists/add-coin/', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      watchlist_id: watchlistId,
      ticker: ticker,
    }),
  });


// Remove a coin from a specific watchlist
const removeCoinFromWatchlist = (userId, watchlistId, ticker) =>
  apiAuth('/watchlists/remove-coin/', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      watchlist_id: watchlistId,
      ticker: ticker,
    }),
  });

// Create a new watchlist for a user
const createWatchlist = (userId, name) =>
  apiAuth('/watchlists/create/', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      name: name,
    }),
  });

// Delete a watchlist for a user
const deleteWatchlist = (userId, watchlistId) =>
  apiAuth(`/watchlists/${watchlistId}/delete/`, {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
    }),
  });


const updateUserProfile = (userId, profileData) =>
  apiAuth(`/users/${userId}/`, {
    method: 'PATCH',
    body: JSON.stringify(profileData),
  });


const getCurrentUser = () => apiAuth('/current-user/');


const searchCoins = (coinId, page = 1, pageSize = 10) =>
  apiNoAuth(`/coins/search/${encodeURIComponent(coinId)}/?page=${page}&page_size=${pageSize}`);

const requestPasswordReset = (email) =>
  apiNoAuth('/reset-password/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });

const chart_data = (coinId, days) => apiNoAuth(`/coins/${encodeURIComponent(coinId)}/chart/?days=${days}`);


export { 
  apiFetch, 
  apiNoAuth,
  apiAuth,
  login, 
  register, 
  logout, 
  getCoins, 
  getWatchlists, 
  getWatchlistItems, 
  getWatchlistMembershipForCoin,
  addCoinToWatchlist, 
  removeCoinFromWatchlist,
  createWatchlist,
  deleteWatchlist, 
  updateUserProfile,
  getCurrentUser,
  searchCoins,
  requestPasswordReset,
  chart_data
};
