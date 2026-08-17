import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { clearAuth } from '../utils/auth';
import { clearAccessToken, getCurrentUser, logout as revokeSession, refreshAccessToken, setAccessToken } from '../utils/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const initialized = useRef(false);

  const clearSession = useCallback(() => {
    clearAccessToken();
    clearAuth();
    setAuthenticated(false);
    setUser(null);
  }, []);

  const login = useCallback((accessToken, userInfo) => {
    setAccessToken(accessToken);
    setAuthenticated(true);
    setUser(userInfo);
  }, []);

  const logout = useCallback(async () => {
    try {
      await revokeSession();
    } catch {
      // Local logout is complete even when server-side revocation is unavailable.
    } finally {
      clearSession();
    }
  }, [clearSession]);

  const updateUser = useCallback((updatedUser) => {
    setUser(updatedUser);
  }, []);

  useEffect(() => {
    let active = true;

    const restoreSession = async () => {
      try {
        const accessToken = await refreshAccessToken();
        if (!active) return;
        setAccessToken(accessToken);

        const response = await getCurrentUser();
        if (active) {
          setUser(response.user);
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
  }, [clearSession]);

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

    window.addEventListener('authfailure', handleAuthenticationFailure);

    return () => {
      window.removeEventListener('authfailure', handleAuthenticationFailure);
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
