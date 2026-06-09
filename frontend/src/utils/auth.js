const isAuthenticated = () => {
  return !!localStorage.getItem("access_token");
};

const clearAuth = () => {
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

  } catch (error) {
    clearAuth();
    return null;
  }
};


export { isAuthenticated, getUser, clearAuth };
