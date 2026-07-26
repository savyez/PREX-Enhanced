import '../styles/page_style/watchlist.css';
import { useEffect, useState } from 'react';
import Button from '../components/Button.jsx';
import CreateWatchlistModal from '../modals/CreateWatchlistModal.jsx';
import ConfirmationModal from '../modals/ConfirmationModal.jsx';
import { getWatchlistItems, getWatchlists, deleteWatchlist } from '../utils/api.js';
import { useAuth } from '../context/authContext.jsx';
import { useAlert } from '../context/alertContext.jsx';
import { useNavigate } from 'react-router-dom';
import { useWatchlist } from '../context/watchlistContext.jsx';

const formatPriceChange = (priceChange) => {
    const numericChange = Number(priceChange);

    if (!Number.isFinite(numericChange)) {
        return 'N/A';
    }

    return `${numericChange > 0 ? '+' : ''}${numericChange.toFixed(2)}%`;
};

const getPriceChangeClass = (priceChange) => {
    const numericChange = Number(priceChange);

    if (!Number.isFinite(numericChange)) {
        return 'price-neutral';
    }

    return numericChange >= 0 ? 'price-up' : 'price-down';
};

function Watchlist() {
    const { user } = useAuth();
    const { watchlists, refreshWatchlists, removeCoin } = useWatchlist();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
    const [items, setItems] = useState([]);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [watchlistToDelete, setWatchlistToDelete] = useState(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [coinToRemove, setCoinToRemove] = useState(null);
    const [removeLoading, setRemoveLoading] = useState(false);
    const { showAlert } = useAlert();

    const navigate = useNavigate();

    useEffect(() => {
        if (watchlists.length > 0) {
            const exists = watchlists.some((w) => String(w.id) === String(selectedWatchlistId));
            if (!exists) {
                setSelectedWatchlistId(String(watchlists[0].id));
            }
        } else {
            setSelectedWatchlistId('');
            setItems([]);
        }
    }, [watchlists, selectedWatchlistId]);

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

    const handleCreateWatchlistSuccess = async (newWatchlist) => {
        await refreshWatchlists();
        if (newWatchlist?.id) {
            setSelectedWatchlistId(String(newWatchlist.id));
        }
        showAlert(`Watchlist ${newWatchlist.name} created successfully.`, 'success');
    };

    const handleDeleteWatchlist = async () => {
        if (!watchlistToDelete || !user?.id) {
            return;
        }

        const watchlistId = watchlistToDelete.id;

        try {
            setDeleteLoading(true);
            await deleteWatchlist(user.id, watchlistId);
            await refreshWatchlists();
            setWatchlistToDelete(null);
            showAlert(`Watchlist ${watchlistToDelete.name} deleted successfully.`, 'success');
        } catch (err) {
            setError(err.message);
        } finally {
            setDeleteLoading(false);
        }
    };

    const handleRemoveCoin = async () => {
        if (!coinToRemove || !user?.id || !selectedWatchlistId) return;

        try {
            setRemoveLoading(true);
            await removeCoin(coinToRemove.ticker.ticker, selectedWatchlistId);
            setItems((prev) =>
                prev.filter(
                    (item) =>
                        item.id !== coinToRemove.id
                )
            );

            setCoinToRemove(null);
            showAlert('Coin removed from the watchlist.', 'success');

        } catch (err) {
            setError(err.message);
        } finally {
            setRemoveLoading(false);
        }
    };

    return (
        <main className="watchlist-page">
            {loading && <p className="watchlist-status">Loading watchlist...</p>}
            {error && <Alert severity="error" onClose={() => setError('')}>{error}</Alert>}

            {!loading && !error && !user?.id ? (
                <div className="empty-watchlist">
                    <h2 className="empty-watchlist-title">You need to login to see your watchlist</h2>
                    <Button className="explore-prices" name="Login" href="/login" />
                </div>
            ) : !loading && !error && watchlists.length > 0 ? (
                <div className="watchlist-container">
                    <div className="watchlist-sidebar">
                        <h3>My Watchlists <button 
                            className="add-watchlist-btn"
                            onClick={() => setShowCreateModal(true)}
                        >
                            + New
                        </button>
                        </h3>
                        <div className="watchlist-list">
                            {watchlists.map((watchlist) => (
                                <button
                                key={watchlist.id}
                                className={`watchlist-button ${
                                    String(watchlist.id) === selectedWatchlistId
                                    ? 'active'
                                    : ''
                                }`}
                                onClick={() =>
                                    setSelectedWatchlistId(String(watchlist.id))
                                }
                                >
                                <span>{watchlist.name}</span>

                                <span
                                    className="watchlist-delete"
                                    onClick={(e) => {
                                    e.stopPropagation();
                                    setWatchlistToDelete(watchlist);
                                    }}
                                >
                                    🗑
                                </span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="watchlist-content">
                        <div className="watchlist-header">
                            <h2>{selectedWatchlist?.name}</h2>
                            <p>{items.length} coins tracked</p>
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
                                    <strong className={`watchlist-price-change ${getPriceChangeClass(item.ticker.price_change_24h)}`}>
                                        Change (24h): {formatPriceChange(item.ticker.price_change_24h)}
                                    </strong>

                                    <button className='details-button' 
                                    onClick={() => navigate(`/coins/search/${item.ticker.ticker}`) }>
                                        Show Details
                                    </button>

                                    <button
                                        className="remove-item-button"
                                        onClick={() => setCoinToRemove(item)}>
                                        Remove Item
                                    </button>
                                    {}

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

            {watchlistToDelete && (
                <ConfirmationModal
                    title={`Delete ${watchlistToDelete.name}? `}
                    message="This action cannot be undone."
                    confirmLabel="Delete"
                    cancelLabel="Cancel"
                    variant="danger"
                    loading={deleteLoading}
                    onCancel={() => setWatchlistToDelete(null)}
                    onConfirm={handleDeleteWatchlist}
                />
            )}

            {coinToRemove && (
                <ConfirmationModal
                    title={`Remove ${coinToRemove.ticker.coin_name} from ${selectedWatchlist.name}?`}
                    message={`This action can not be undone.`}
                    confirmLabel="Remove"
                    cancelLabel="Cancel"
                    variant="danger"
                    loading={removeLoading}
                    onCancel={() => setCoinToRemove(null)}
                    onConfirm={handleRemoveCoin}
                />
            )}
        </main>
    );
}

export default Watchlist;
