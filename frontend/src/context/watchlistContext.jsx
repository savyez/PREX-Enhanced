/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useAuth } from './authContext';
import { addCoinToWatchlist, getWatchlists, removeCoinFromWatchlist } from '../utils/api';

const WatchlistContext = createContext(null);

const buildMembershipMap = (watchlistArray = []) => {
  const nextMembershipMap = {};

  watchlistArray.forEach((watchlist) => {
    const items = watchlist.items || [];

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
  });

  return nextMembershipMap;
};

export function WatchlistProvider({ children }) {
  const { authenticated, user } = useAuth();
  const [watchlists, setWatchlists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const membershipMap = useMemo(() => buildMembershipMap(watchlists), [watchlists]);

  const refreshWatchlists = useCallback(async () => {
    if (!authenticated || !user?.id) {
      setWatchlists([]);
      setError('');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const { watchlists: userWatchlists = [] } = await getWatchlists(user.id);
      setWatchlists(userWatchlists);
    } catch (err) {
      setError(err.message || 'Failed to load watchlists');
      setWatchlists([]);
    } finally {
      setLoading(false);
    }
  }, [authenticated, user]);

  useEffect(() => {
    const refreshTimer = window.setTimeout(() => {
      refreshWatchlists();
    }, 0);

    return () => window.clearTimeout(refreshTimer);
  }, [refreshWatchlists]);

  const addCoin = useCallback(async (ticker, watchlistId) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    const response = await addCoinToWatchlist(user.id, watchlistId, ticker);
    const updatedWatchlist = response?.watchlist;

    if (updatedWatchlist?.id) {
      setWatchlists((prev) =>
        prev.map((w) => (w.id === updatedWatchlist.id ? updatedWatchlist : w))
      );
    }

    return response;
  }, [user]);

  const removeCoin = useCallback(async (ticker, watchlistId) => {
    if (!user?.id) {
      throw new Error('User not authenticated');
    }

    const response = await removeCoinFromWatchlist(user.id, watchlistId, ticker);
    const updatedWatchlist = response?.watchlist;

    if (updatedWatchlist?.id) {
      setWatchlists((prev) =>
        prev.map((w) => (w.id === updatedWatchlist.id ? updatedWatchlist : w))
      );
    }

    return response;
  }, [user]);

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
