const isAuthenticated = () => {
  return !!localStorage.getItem("access_token");
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

const clearAuth = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  dispatchAuthChange();
};

const setAuth = (accessToken, refreshToken, userInfo) => {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
  localStorage.setItem("user", JSON.stringify(userInfo));
  dispatchAuthChange();
};

const dispatchAuthChange = () => {
  window.dispatchEvent(new Event("authchange"));
};

export { isAuthenticated, getUser, clearAuth, setAuth, dispatchAuthChange };
