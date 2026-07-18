import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useAuth } from './AuthContext';
import { addCoinToWatchlist, getWatchlistItems, getWatchlists, removeCoinFromWatchlist } from '../utils/api';

const WatchlistContext = createContext(null);

export function WatchlistProvider({ children }) {
  const { authenticated, user } = useAuth();
  const [watchlists, setWatchlists] = useState([]);
  const [membershipMap, setMembershipMap] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const refreshWatchlists = useCallback(async () => {
    if (!authenticated || !user?.id) {
      setWatchlists([]);
      setMembershipMap({});
      setError('');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const { watchlists: userWatchlists = [] } = await getWatchlists(user.id);
      const nextMembershipMap = {};

      await Promise.all(
        userWatchlists.map(async (watchlist) => {
          const response = await getWatchlistItems(watchlist.id);
          const items = response.items || [];

          items.forEach((item) => {
            const ticker = item?.ticker?.ticker;
            if (!ticker) {
              return;
            }

            if (!nextMembershipMap[ticker]) {
              nextMembershipMap[ticker] = [];
            }

            nextMembershipMap[ticker].push({
              item_id: item.id,
              watchlist_id: watchlist.id,
              watchlist_name: watchlist.name,
            });
          });
        })
      );

      setWatchlists(userWatchlists);
      setMembershipMap(nextMembershipMap);
    } catch (err) {
      setError(err.message || 'Failed to load watchlists');
      setWatchlists([]);
      setMembershipMap({});
    } finally {
      setLoading(false);
    }
  }, [authenticated, user?.id]);

  useEffect(() => {
    refreshWatchlists();
  }, [refreshWatchlists]);

  const addCoin = useCallback(async (ticker, watchlistId) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    await addCoinToWatchlist(user.id, watchlistId, ticker);
    await refreshWatchlists();
  }, [refreshWatchlists, user?.id]);

  const removeCoin = useCallback(async (ticker, watchlistId) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    await removeCoinFromWatchlist(user.id, watchlistId, ticker);
    await refreshWatchlists();
  }, [refreshWatchlists, user?.id]);

  const value = useMemo(() => ({
    watchlists,
    membershipMap,
    loading,
    error,
    refreshWatchlists,
    addCoin,
    removeCoin,
  }), [watchlists, membershipMap, loading, error, refreshWatchlists, addCoin, removeCoin]);

  return (
    <WatchlistContext.Provider value={value}>
      {children}
    </WatchlistContext.Provider>
  );
}

export function useWatchlist() {
  const context = useContext(WatchlistContext);

  if (!context) {
    throw new Error('useWatchlist must be used within a WatchlistProvider');
  }

  return context;
}
