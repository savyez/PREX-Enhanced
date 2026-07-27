import { useEffect, useMemo, useState } from 'react';
import { useWatchlist } from '../context/watchlistContext';
import { useAlert } from '../context/alertContext';
import '../styles/component_style/watchlist-selector.css';

function WatchlistSelector({ coin, onClose, onSuccess, existingMemberships = [], onRemove }) {
  const { watchlists, loading, error, addCoin } = useWatchlist();
  const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
  const { showAlert } = useAlert();
  const existingWatchlistIds = useMemo(
    () => new Set((existingMemberships || []).map((membership) => String(membership.watchlist_id))),
    [existingMemberships]
  );

  const activeSelectedWatchlistId = useMemo(() => {
    if (watchlists.length === 0) return '';
    if (selectedWatchlistId && watchlists.some((watchlist) => String(watchlist.id) === selectedWatchlistId)) {
      return selectedWatchlistId;
    }
    const firstExistingMembership = watchlists.find((watchlist) => existingWatchlistIds.has(String(watchlist.id)));
    return String(firstExistingMembership?.id || watchlists[0]?.id || '');
  }, [watchlists, existingWatchlistIds, selectedWatchlistId]);

  useEffect(() => {
    if (error) {
      showAlert(error, 'error');
    }
  }, [error, showAlert]);

  const handleAdd = async () => {
    if (!activeSelectedWatchlistId) {
      showAlert('Please select a watchlist.', 'warning');
      return;
    }

    const alreadyInSelectedWatchlist = existingMemberships.some(
      (membership) => String(membership.watchlist_id) === String(activeSelectedWatchlistId)
    );

    if (alreadyInSelectedWatchlist) {
      showAlert('This coin is already in the selected watchlist.', 'warning');
      return;
    }

    try {
      await addCoin(coin.ticker, activeSelectedWatchlistId);
      onSuccess?.();
      onClose();
    } catch (err) {
      showAlert(err.message || 'Failed to add coin to watchlist.', 'error');
    }
  };

  const handleRemove = async () => {
    if (!activeSelectedWatchlistId) {
      showAlert('Please select a watchlist.', 'warning');
      return;
    }

    const membership = existingMemberships.find(
      (entry) => String(entry.watchlist_id) === String(activeSelectedWatchlistId)
    );

    if (!membership) {
      showAlert('This coin is not in the selected watchlist.', 'warning');
      return;
    }

    try {
      await onRemove?.(membership);
      onClose();
    } catch (err) {
      showAlert(err.message || 'Failed to remove coin from watchlist.', 'error');
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
        {!loading && watchlists.length === 0 && (
          <p className="watchlist-selector-empty">No watchlists found. Create one first.</p>
        )}

        {!loading && watchlists.length > 0 && (
          <>
            <div className="watchlist-selector-list">
              {watchlists.map((watchlist) => {
                const isInWatchlist = existingWatchlistIds.has(String(watchlist.id));

                return (
                  <label key={watchlist.id} className="watchlist-selector-item">
                    <input
                      type="radio"
                      name="watchlist"
                      value={watchlist.id}
                      checked={String(watchlist.id) === activeSelectedWatchlistId}
                      onChange={(e) => {
                        setSelectedWatchlistId(e.target.value);
                        if (isInWatchlist) {
                          showAlert('This coin is already in the selected watchlist.', 'info');
                        }
                      }}
                    />
                    <span>{watchlist.name}</span>
                  </label>
                );
              })}
            </div>


            <div className="watchlist-selector-actions">
              <button className="watchlist-selector-cancel" onClick={onClose}>
                Cancel
              </button>
              {existingMemberships.length > 0 && (
                <button className="watchlist-selector-remove" onClick={handleRemove}>
                  Remove
                </button>
              )}
              <button className="watchlist-selector-add" onClick={handleAdd}>
                Add
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default WatchlistSelector;
