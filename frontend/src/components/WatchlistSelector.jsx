import { useEffect, useState } from 'react';
import { getWatchlists } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import '../styles/component_style/watchlist-selector.css';

function WatchlistSelector({ coin, onClose, onSuccess }) {
  const { user } = useAuth();
  const [watchlists, setWatchlists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedWatchlistId, setSelectedWatchlistId] = useState('');

  useEffect(() => {
    const fetchWatchlists = async () => {
      if (!user?.id) {
        setError('User not authenticated');
        setLoading(false);
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
        setError(err.message || 'Failed to load watchlists');
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlists();
  }, [user]);

  const handleAdd = async () => {
    if (!selectedWatchlistId) {
      setError('Please select a watchlist');
      return;
    }

    try {
      const { addCoinToWatchlist } = await import('../utils/api');
      await addCoinToWatchlist(user.id, selectedWatchlistId, coin.ticker);
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to add coin to watchlist');
    }
  };

  return (
    <div className="watchlist-selector-overlay" onClick={onClose}>
      <div className="watchlist-selector-modal" onClick={(e) => e.stopPropagation()}>
        <div className="watchlist-selector-header">
          <h2>Add {coin.coin_name} to Watchlist</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {loading && <p className="watchlist-selector-loading">Loading watchlists...</p>}
        {error && <p className="watchlist-selector-error">{error}</p>}

        {!loading && watchlists.length === 0 && (
          <p className="watchlist-selector-empty">No watchlists found. Create one first.</p>
        )}

        {!loading && watchlists.length > 0 && (
          <>
            <div className="watchlist-selector-list">
              {watchlists.map((watchlist) => (
                <label key={watchlist.id} className="watchlist-selector-item">
                  <input
                    type="radio"
                    name="watchlist"
                    value={watchlist.id}
                    checked={String(watchlist.id) === selectedWatchlistId}
                    onChange={(e) => setSelectedWatchlistId(e.target.value)}
                  />
                  <span>{watchlist.name}</span>
                </label>
              ))}
            </div>

            <div className="watchlist-selector-actions">
              <button className="watchlist-selector-cancel" onClick={onClose}>
                Cancel
              </button>
              <button className="watchlist-selector-add" onClick={handleAdd}>
                Add to Watchlist
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default WatchlistSelector;
