import { Link } from 'react-router-dom';
import { getUser } from '../utils/auth.js';

function Profile() {
    const user = getUser();

    return (
        <main className="watchlist-page">
            <div className="empty-watchlist">
                <h2 className="empty-watchlist-title">Profile</h2>
                {user ? (
                    <>
                        <p>{user.username}</p>
                        <p>{user.email}</p>
                    </>
                ) : (
                    <>
                        <p>You need to login to see your profile.</p>
                        <Link className="button explore-prices" to="/login">Login</Link>
                    </>
                )}
            </div>
        </main>
    );
}

export default Profile;
