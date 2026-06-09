import { createContext, useContext, useEffect, useState } from 'react';
import { isAuthenticated, getUser } from '../utils/auth';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());
  const [user, setUser] = useState(getUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set loading to false after initial check
    setLoading(false);
  }, []);

  const updateAuth = () => {
    setAuthenticated(isAuthenticated());
    setUser(getUser());
  };

  const login = (accessToken, refreshToken, userInfo) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user', JSON.stringify(userInfo));
    updateAuth();
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    updateAuth();
  };

  useEffect(() => {
    const handleStorageChange = () => {
      updateAuth();
    };

    const handleAuthChange = () => {
      updateAuth();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('authchange', handleAuthChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authchange', handleAuthChange);
    };
  }, []);

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        user,
        loading,
        login,
        logout,
        updateAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
