import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/authContext';

const Logout = () => {
    const navigate = useNavigate();
    const { logout: authLogout } = useAuth();

    useEffect(() => {
        const performLogout = async () => {
            await authLogout();
            navigate('/login', { replace: true });
        };

        performLogout();
    }, [navigate, authLogout]);

    return (
        <div>
            <h2>Logging out...</h2>
        </div>
    );
};

export default Logout;
