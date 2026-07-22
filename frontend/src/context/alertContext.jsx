import { createContext, useCallback, useContext, useState } from 'react';
import Alert from '@mui/material/Alert';
import Fade from '@mui/material/Fade';
import Snackbar from '@mui/material/Snackbar';

const AlertContext = createContext(null);

export function AlertProvider({ children }) {
  const [notification, setNotification] = useState(null);

  const showAlert = useCallback((message, severity = 'info') => {
    setNotification({ message, severity });
  }, []);

  const closeAlert = useCallback((_, reason) => {
    if (reason !== 'clickaway') {
      setNotification(null);
    }
  }, []);

  return (
    <AlertContext.Provider value={{ showAlert }}>
      {children}
      <Snackbar
        open={Boolean(notification)}
        autoHideDuration={3000}
        onClose={closeAlert}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        TransitionComponent={Fade}
      >
        {notification ? (
          <Alert onClose={closeAlert} severity={notification.severity} variant="standard">
            {notification.message}
          </Alert>
        ) : null}
      </Snackbar>
    </AlertContext.Provider>
  );
}

// This hook is intentionally exported alongside the provider for the context API.
// eslint-disable-next-line react-refresh/only-export-components
export function useAlert() {
  const context = useContext(AlertContext);

  if (!context) {
    throw new Error('useAlert must be used within an AlertProvider');
  }

  return context;
}
