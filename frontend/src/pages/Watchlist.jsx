import '../styles/page_style/watchlist.css';
import { useEffect, useState } from 'react';
import Button from '../components/Button.jsx';
import { getWatchlistItems, getWatchlists } from '../utils/api.js';
import { getUser } from '../utils/auth.js';

function Watchlist() {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [watchlists, setWatchlists] = useState([]);
    const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
    const [items, setItems] = useState([]);

    useEffect(() => {
        const fetchWatchlists = async () => {
            const currentUser = getUser();

            if (!currentUser?.user_id) {
                setLoading(false);
                return;
            }

            try {
                const data = await getWatchlists(currentUser.user_id);
                const userWatchlists = data.watchlists || [];

                setWatchlists(userWatchlists);

                if (userWatchlists.length > 0) {
                    setSelectedWatchlistId(String(userWatchlists[0].id));
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchWatchlists();
    }, []);

    useEffect(() => {
        if (!selectedWatchlistId) {
            return;
        }

        const fetchItems = async () => {
            setLoading(true);
            setError('');

            try {
                const data = await getWatchlistItems(selectedWatchlistId);
                setItems(data.items || []);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchItems();
    }, [selectedWatchlistId]);

    const selectedWatchlist = watchlists.find(
        (watchlist) => String(watchlist.id) === selectedWatchlistId
    );

    return (
        <main className="watchlist-page">
            {loading && <p className="watchlist-status">Loading watchlist...</p>}
            {error && <p className="watchlist-error">{error}</p>}

            {!loading && !error && !getUser()?.user_id ? (
                <div className="empty-watchlist">
                    <h2 className="empty-watchlist-title">You need to login to see your watchlist</h2>
                    <Button className="explore-prices" name="Login" href="/login" />
                </div>
            ) : !loading && !error && watchlists.length > 0 ? (
                <div className="watchlist-container">
                    <div className="watchlist-sidebar">
                        <h3>My Watchlists</h3>
                        <div className="watchlist-list">
                            {watchlists.map((watchlist) => (
                                <button
                                    key={watchlist.id}
                                    className={`watchlist-button ${String(watchlist.id) === selectedWatchlistId ? 'active' : ''}`}
                                    onClick={() => setSelectedWatchlistId(String(watchlist.id))}
                                >
                                    {watchlist.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="watchlist-content">
                        <div className="watchlist-header">
                            <h2>{selectedWatchlist?.name || 'Your Watchlist'}</h2>
                        </div>

                        {items.length > 0 ? (
                            <div className="watchlist-grid">
                                {items.map((coin) => (
                                    <div key={coin.ticker} className="watchlist-item">
                                        <h3>{coin.coin_name}</h3>
                                        <span>{coin.ticker}</span>
                                        <p>Price: ${Number(coin.price).toLocaleString()}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="empty-watchlist">
                                <h2 className="empty-watchlist-title">This Watchlist is Empty</h2>
                                <p>Start adding coins to see them here.</p>
                                <Button className="explore-prices" name="Explore Coins" href="/prices" />
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                !loading && !error && (
                <div className="empty-watchlist">
                    <h2 className="empty-watchlist-title">Your Watchlist is Empty</h2>
                    <p>Start adding coins to your watchlist to see them here.</p>
                    <Button className="explore-prices" name="Explore Coins" href="/prices" />
                </div>
                )
            )}
        </main>
    );
}

export default Watchlist;
