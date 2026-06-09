import '../styles/page_style/watchlist.css';
import { useEffect, useState } from 'react';
import Button from '../components/Button.jsx';
import CreateWatchlistModal from '../components/CreateWatchlistModal.jsx';
import { getWatchlistItems, getWatchlists } from '../utils/api.js';
import { useAuth } from '../context/AuthContext';

function Watchlist() {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [watchlists, setWatchlists] = useState([]);
    const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
    const [items, setItems] = useState([]);
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        const fetchWatchlists = async () => {
            if (!user?.id) {
                setLoading(false);
                console.log("Auth User:", user);
                return;
            }

            try {
                const data = await getWatchlists(user.id);
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
    }, [user]);

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

    const handleCreateWatchlistSuccess = (newWatchlist) => {
        // Add the new watchlist to the list
        setWatchlists([...watchlists, newWatchlist]);
        // Select the new watchlist
        setSelectedWatchlistId(String(newWatchlist.id));
    };

    return (
        <main className="watchlist-page">
            {loading && <p className="watchlist-status">Loading watchlist...</p>}
            {error && <p className="watchlist-error">{error}</p>}

            {!loading && !error && !user?.id ? (
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
                                {items.map((item) => (
                                <div key={item.id} className="watchlist-item">
                                    <h3>{item.ticker.coin_name}</h3>
                                    <span>{item.ticker.ticker}</span>
                                    <p>
                                    Price: $
                                    {Number(item.ticker.price).toLocaleString()}
                                    </p>
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
                    <h2 className="empty-watchlist-title">Have Coins to Track?</h2>
                    <p>Create a watchlist to start tracking your favorite coins. Once you create a watchlist, you can add coins from the prices page.</p>
                    <button 
                        className="empty-watchlist-create-btn"
                        onClick={() => setShowCreateModal(true)}
                    >
                        Create Watchlist
                    </button>
                    <p className="empty-watchlist-divider">
                        Or explore coins first and add them to a new watchlist
                    </p>
                    <Button className="explore-prices" name="Explore Coins" href="/prices" />
                </div>
                )
            )}

            {showCreateModal && (
                <CreateWatchlistModal
                    onClose={() => setShowCreateModal(false)}
                    onSuccess={handleCreateWatchlistSuccess}
                />
            )}
        </main>
    );
}

export default Watchlist;
