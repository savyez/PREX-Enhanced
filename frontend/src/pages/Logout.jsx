import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const Logout = () => {
    const navigate = useNavigate();
    const { logout: authLogout } = useAuth();
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
                authLogout();
                navigate('/login');
            }
        };

        performLogout();
    }, [navigate, authLogout]);

    return (
        <div>
            <h2>Logging out...</h2>
            {error && <p>{error}</p>}
        </div>
    );
};

export default Logout;
