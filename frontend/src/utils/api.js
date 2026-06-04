const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

const buildUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL.replace(/\/$/, '')}${normalizedPath}`;
};

const getAuthHeaders = () => {
  const accessToken = localStorage.getItem('access_token');
  return accessToken ? { Authorization: `Bearer ${accessToken}` } : {};
};

const apiFetch = async (path, options = {}) => {
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
  const data = contentType.includes('application/json') ? await response.json() : null;

  if (!response.ok) {
    const message = data?.error || data?.detail || data?.message || 'Request failed';
    throw new Error(Array.isArray(message) ? message.join(' ') : message);
  }

  return data;
};

const login = (credentials) => (
  apiFetch('/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
);

const register = (userData) => (
  apiFetch('/register/', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
);

const logout = (refreshToken) => (
  apiFetch('/logout/', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
);

const getCoins = () => apiFetch('/coins/');

const getWatchlists = (userId) => apiFetch(`/watchlists/${userId}/`);

const getWatchlistItems = (watchlistId) => apiFetch(`/watchlists/${watchlistId}/items/`);

export { apiFetch, login, register, logout, getCoins, getWatchlists, getWatchlistItems };
