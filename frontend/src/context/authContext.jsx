import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { clearAuth, getUser } from '../utils/auth';
import { getCurrentUser, logout as revokeSession } from '../utils/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const initialized = useRef(false);

  const clearSession = useCallback(() => {
    clearAuth();
    setAuthenticated(false);
    setUser(null);
  }, []);

  const login = useCallback((accessToken, refreshToken, userInfo) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user', JSON.stringify(userInfo));
    setAuthenticated(true);
    setUser(userInfo);
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      if (refreshToken) {
        await revokeSession(refreshToken);
      }
    } catch {
      // Local logout is complete even when server-side revocation is unavailable.
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const updateUser = useCallback((updatedUser) => {
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setUser(updatedUser);
  }, []);

  useEffect(() => {
    let active = true;

    const restoreSession = async () => {
      if (!localStorage.getItem('refresh_token') && !localStorage.getItem('access_token')) {
        initialized.current = true;
        setLoading(false);
        return;
      }

      try {
        const response = await getCurrentUser();
        if (active) {
          updateUser(response.user);
          setAuthenticated(true);
        }
      } catch {
        if (active) {
          clearSession();
        }
      } finally {
        if (active) {
          initialized.current = true;
          setLoading(false);
        }
      }
    };

    restoreSession();
    return () => {
      active = false;
    };
  }, [clearSession, updateUser]);

  useEffect(() => {
    const handleAuthenticationFailure = () => {
      if (!authenticated && initialized.current) {
        return;
      }

      clearSession();
      if (initialized.current) {
        navigate('/login', { replace: true, state: { sessionExpired: true } });
      }
    };

    const handleStorageChange = (event) => {
      if (event.key === 'access_token' || event.key === 'refresh_token' || event.key === 'user') {
        if (!localStorage.getItem('access_token') || !getUser()) {
          clearSession();
        }
      }
    };

    window.addEventListener('authfailure', handleAuthenticationFailure);
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('authfailure', handleAuthenticationFailure);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [authenticated, clearSession, navigate]);

  return (
    <AuthContext.Provider
      value={{
        authenticated,
        user,
        loading,
        login,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// This hook is intentionally exported alongside the provider for the existing context API.
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
