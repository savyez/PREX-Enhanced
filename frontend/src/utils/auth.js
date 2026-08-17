import { getAccessToken, clearAccessToken } from './api';

const isAuthenticated = () => {
  return !!getAccessToken();
};

const clearAuth = () => {
  clearAccessToken();
};

export { isAuthenticated, clearAuth };
