import '../styles/page_style/watchlist.css';
import { useState } from 'react';
import Navbar from '../components/Navbar.jsx';
import Button from '../components/Button.jsx';

function Watchlist() {
    const[loading, setLoading] = useState(true);
    const[user, setUser] = useState(null);
    return (
        <main className="watchlist-page">
            {user?.watchlist?.length > 0 ? (
                <>
                    <h2>Your Watchlist</h2>
                    <div className="watchlist-grid">
                        {user.watchlist.map((coin) => (
                            <div key={coin.id} className="watchlist-item">
                                <h3>{coin.name}</h3>
                                <p>Price: ${coin.price}</p>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <>
                <div className="empty-watchlist">
                    <h2 className="empty-watchlist-title">Your Watchlist is Empty</h2>
                    <p>Start adding coins to your watchlist to see them here.</p>
                    <Button className="explore-prices" name="Explore Coins" href="/prices" />
                </div>
                </>
            )}
        </main>
    );
}

export default Watchlist;
