import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../utils/api';
import { clearAuth } from '../utils/auth';

const Logout = () => {
    const navigate = useNavigate();
    const [error, setError] = useState("");

    useEffect(() => {
        const performLogout = async () => {
            setError("");
            const accessToken = localStorage.getItem('access_token');
            const refreshToken = localStorage.getItem('refresh_token');

            try {
                if (accessToken && refreshToken) {
                    await logout(refreshToken);
                }
            } catch {
                setError('Error occurred while logging out');
            } finally {
                clearAuth();
                navigate('/login');
            }
        };

        performLogout();
    }, [navigate]);

    return (
        <div>
            <h2>Logging out...</h2>
            {error && <p>{error}</p>}
        </div>
    );
};

export default Logout;
