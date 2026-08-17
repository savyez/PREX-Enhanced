import '../styles/page_style/watchlist.css';
import { useMemo, useState } from 'react';
import Button from '../components/Button.jsx';
import CreateWatchlistModal from '../modals/CreateWatchlistModal.jsx';
import ConfirmationModal from '../modals/ConfirmationModal.jsx';
import { deleteWatchlist } from '../utils/api.js';
import { useAuth } from '../context/authContext.jsx';
import { useAlert } from '../context/alertContext.jsx';
import { useNavigate } from 'react-router-dom';
import { useWatchlist } from '../context/watchlistContext.jsx';



import {
    formatPrice,
    formatPriceChange,
    getPriceChangeClass,
} from '../utils/formatters.js';

function Watchlist() {
    const { user } = useAuth();
    const { watchlists, loading, error, refreshWatchlists, removeCoin } = useWatchlist();
    const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [watchlistToDelete, setWatchlistToDelete] = useState(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [coinToRemove, setCoinToRemove] = useState(null);
    const [removeLoading, setRemoveLoading] = useState(false);
    const { showAlert } = useAlert();

    const navigate = useNavigate();

    const activeWatchlistId = useMemo(() => {
        if (watchlists.length === 0) return '';
        const exists = watchlists.some((w) => String(w.id) === String(selectedWatchlistId));
        return exists ? String(selectedWatchlistId) : String(watchlists[0]?.id || '');
    }, [watchlists, selectedWatchlistId]);

    const selectedWatchlist = watchlists.find(
        (watchlist) => String(watchlist.id) === activeWatchlistId
    );

    const displayedItems = selectedWatchlist?.items || [];

    const handleCreateWatchlistSuccess = async (newWatchlist) => {
        await refreshWatchlists();
        if (newWatchlist?.id) {
            setSelectedWatchlistId(String(newWatchlist.id));
        }
    };

    const handleDeleteWatchlist = async () => {
        if (!watchlistToDelete?.id) return;
        setDeleteLoading(true);
        try {
            await deleteWatchlist(user.id, watchlistToDelete.id);
            await refreshWatchlists();

            showAlert('Watchlist deleted successfully.', 'success');
            setWatchlistToDelete(null);
        } catch (err) {
            showAlert(err.message || 'Failed to delete watchlist.', 'error');
        } finally {
            setDeleteLoading(false);
        }
    };

    const handleRemoveCoin = async () => {
        if (!coinToRemove || !selectedWatchlist) return;
        setRemoveLoading(true);

        try {
            await removeCoin(coinToRemove.ticker.ticker, selectedWatchlist.id);
            showAlert(`Removed ${coinToRemove.ticker.coin_name} from ${selectedWatchlist.name}`, 'success');
            setCoinToRemove(null);
        } catch (err) {
            showAlert(err.message || 'Failed to remove coin.', 'error');
        } finally {
            setRemoveLoading(false);
        }
    };

    return (
        <main className="watchlist-page">
            {loading && watchlists.length === 0 ? (
                <div className="watchlist-status">Loading watchlists...</div>
            ) : error ? (
                <div className="watchlist-error">{error}</div>
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
                                    String(watchlist.id) === activeWatchlistId
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
                            <p>{displayedItems.length} coins tracked</p>
                        </div>

                        {displayedItems.length > 0 ? (
                            <div className="watchlist-grid">
                                {displayedItems.map((item) => (
                                <div key={item.id} className="watchlist-item">
                                    <h3>{item.ticker.coin_name}</h3>
                                    <span>{item.ticker.ticker}</span>
                                    <p>
                                        Price: ${formatPrice(item.ticker.price)}
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
