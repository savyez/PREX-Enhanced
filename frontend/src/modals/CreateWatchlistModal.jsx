import { useState } from 'react';
import { apiAuth } from '../utils/api';
import '../styles/modal_style/create-watchlist-modal.css';

function CreateWatchlistModal({ onClose, onSuccess }) {
  const [watchlistName, setWatchlistName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!watchlistName.trim()) {
      setError('Please enter a watchlist name');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await apiAuth('/watchlists/create/', {
        method: 'POST',
        body: JSON.stringify({ name: watchlistName.trim() }),
      });

      onSuccess?.(data.watchlist);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create watchlist');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleCreate();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div className="create-watchlist-overlay" onClick={onClose}>
      <div className="create-watchlist-modal" onClick={(e) => e.stopPropagation()}>
        <div className="create-watchlist-header">
          <h2>Create a New Watchlist</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="create-watchlist-body">
          <label htmlFor="watchlist-name">Watchlist Name</label>
          <input
            id="watchlist-name"
            type="text"
            placeholder="e.g., My Favorite Coins, Tech Coins"
            value={watchlistName}
            onChange={(e) => setWatchlistName(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            autoFocus
          />

          {error && <p className="create-watchlist-error">{error}</p>}
        </div>

        <div className="create-watchlist-actions">
          <button 
            className="cancel-button" 
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
          <button 
            className="create-button" 
            onClick={handleCreate}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default CreateWatchlistModal;
