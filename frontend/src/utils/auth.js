import { getAccessToken, clearAccessToken } from './api';

const isAuthenticated = () => {
  return !!getAccessToken();
};

const clearAuth = () => {
  clearAccessToken();
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
};

const getUser = () => {
  const user = localStorage.getItem("user");

  if (!user) {
    return null;
  }

  try {
    return JSON.parse(user);
  } catch {
    clearAuth();
    return null;
  }
};


export { isAuthenticated, getUser, clearAuth };
