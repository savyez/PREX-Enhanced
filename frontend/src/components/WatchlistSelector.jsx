import { useEffect, useMemo, useState } from 'react';
import { useWatchlist } from '../context/watchlistContext';
import '../styles/component_style/watchlist-selector.css';

function WatchlistSelector({ coin, onClose, onSuccess, existingMemberships = [], onRemove }) {
  const { watchlists, loading, error, addCoin } = useWatchlist();
  const [selectedWatchlistId, setSelectedWatchlistId] = useState('');
  const [actionError, setActionError] = useState('');
  const existingWatchlistIds = useMemo(
    () => new Set((existingMemberships || []).map((membership) => String(membership.watchlist_id))),
    [existingMemberships]
  );

  useEffect(() => {
    if (watchlists.length === 0) {
      setSelectedWatchlistId('');
      return;
    }

    setSelectedWatchlistId((currentSelection) => {
      const stillExists = watchlists.some((watchlist) => String(watchlist.id) === currentSelection);
      if (stillExists) {
        return currentSelection;
      }

      const firstExistingMembership = watchlists.find((watchlist) => existingWatchlistIds.has(String(watchlist.id)));
      return String(firstExistingMembership?.id || watchlists[0].id);
    });
  }, [watchlists, existingWatchlistIds]);

  const handleAdd = async () => {
    if (!selectedWatchlistId) {
      setActionError('Please select a watchlist');
      return;
    }

    const alreadyInSelectedWatchlist = existingMemberships.some(
      (membership) => String(membership.watchlist_id) === String(selectedWatchlistId)
    );

    if (alreadyInSelectedWatchlist) {
      setActionError('This coin is already in the selected watchlist.');
      return;
    }

    try {
      setActionError('');
      await addCoin(coin.ticker, selectedWatchlistId);
      onSuccess?.();
      onClose();
    } catch (err) {
      setActionError(err.message || 'Failed to add coin to watchlist');
    }
  };

  const handleRemove = async () => {
    if (!selectedWatchlistId) {
      setActionError('Please select a watchlist');
      return;
    }

    const membership = existingMemberships.find(
      (entry) => String(entry.watchlist_id) === String(selectedWatchlistId)
    );

    if (!membership) {
      setActionError('This coin is not in the selected watchlist.');
      return;
    }

    try {
      setActionError('');
      await onRemove?.(membership);
      onClose();
    } catch (err) {
      setActionError(err.message || 'Failed to remove coin from watchlist');
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
        {(error || actionError) && <p className="watchlist-selector-error">{actionError || error}</p>}

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
                      checked={String(watchlist.id) === selectedWatchlistId}
                      onChange={(e) => {
                        setSelectedWatchlistId(e.target.value);
                        setActionError('');
                      }}
                    />
                    <span>{watchlist.name}</span>
                    {isInWatchlist && <small>Already contains this coin</small>}
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
