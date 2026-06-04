import { Link } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth.js';

function Settings() {
    return (
        <main className="watchlist-page">
            <div className="empty-watchlist">
                <h2 className="empty-watchlist-title">Settings</h2>
                {isAuthenticated() ? (
                    <p>Account settings will appear here.</p>
                ) : (
                    <>
                        <p>You need to login to manage your settings.</p>
                        <Link className="button explore-prices" to="/login">Login</Link>
                    </>
                )}
            </div>
        </main>
    );
}

export default Settings;
