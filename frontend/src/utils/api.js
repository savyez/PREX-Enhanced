let refreshPromise = null;
let inMemoryAccessToken = null;

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = configuredApiBaseUrl || 'http://127.0.0.1:8000/api/v1';


export class AuthenticationError extends Error {
  constructor(message = 'Your session has expired. Please sign in again.') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

// In-memory access token getter / setter / clearer
const setAccessToken = (token) => {
  inMemoryAccessToken = token || null;
};

const getAccessToken = () => inMemoryAccessToken;

const clearAccessToken = () => {
  inMemoryAccessToken = null;
};

// React owns session state and navigation; the API layer only reports an expired session.
const notifyAuthenticationFailure = () => {
  window.dispatchEvent(new Event('authfailure'));
};

// Build full API URL from path
const buildUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL.replace(/\/$/, '')}${normalizedPath}`;
};


// Get authorization headers with the in-memory access token
const getAuthHeaders = () => {
  const accessToken = getAccessToken();
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
};

const apiFetch = async (path, options = {}, retry = true) => {
  const {
    auth = true,
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
    credentials: 'include',
    headers,
  });

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : null;

  if (retry && auth && response.status === 401) {
    try {
      await refreshAccessToken();
      return apiFetch(path, options, false);
    } catch (error) {
      notifyAuthenticationFailure();
      throw error;
    }
  }

  if (!response.ok) {
    if (auth && response.status === 401) {
      notifyAuthenticationFailure();
      throw new AuthenticationError();
    }

    const message = data?.error || data?.detail || data?.message || 'Request failed';
    throw new Error(Array.isArray(message) ? message.join(' ') : message);
  }

  return data;
};

const apiNoAuth = async (path, options = {}) => apiFetch(path, {
  ...options,
  auth: false,
});

const apiAuth = async (path, options = {}) => apiFetch(path, {
  ...options,
  auth: true,
});

// Refresh access token silently using the HttpOnly refresh token cookie
const refreshAccessToken = async () => {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await fetch(buildUrl('/token/refresh/'), {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        clearAccessToken();
        throw new AuthenticationError('Session expired. Please sign in again.');
      }

      const data = await response.json();
      const accessToken = data?.access_token || data?.access;

      if (!accessToken) {
        clearAccessToken();
        throw new AuthenticationError('Invalid refresh response');
      }

      setAccessToken(accessToken);
      return accessToken;
    } catch (error) {
      clearAccessToken();
      throw error;
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


const logout = async () => {
  try {
    return await apiAuth('/logout/', {
      method: 'POST',
      body: JSON.stringify({}),
    });
  } finally {
    clearAccessToken();
  }
};


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
const createWatchlist = (name) =>
  apiAuth('/watchlists/create/', {
    method: 'POST',
    body: JSON.stringify({
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

const confirmPasswordReset = (token, newPassword, confirmNewPassword) =>
  apiNoAuth(`/reset-password-confirm/${token}/`, {
    method: 'POST',
    body: JSON.stringify({
      new_password: newPassword,
      confirm_new_password: confirmNewPassword,
    }),
  });

const chart_data = (coinId, days) => apiNoAuth(`/coins/${encodeURIComponent(coinId)}/chart/?days=${days}`);


export { 
  setAccessToken,
  getAccessToken,
  clearAccessToken,
  refreshAccessToken,
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
  confirmPasswordReset,
  chart_data
};

