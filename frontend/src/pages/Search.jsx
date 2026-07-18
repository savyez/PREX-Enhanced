import SearchBar from '../components/SearchBar';
import Pagination from '../components/Pagination.jsx';
import WatchlistSelector from '../components/WatchlistSelector.jsx';
import ConfirmationModal from '../modals/ConfirmationModal.jsx';
import { searchCoins } from '../utils/api.js';
import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWatchlist } from '../context/watchlistContext';
import CoinChart from '../components/CoinChart.jsx';
import '../styles/page_style/search.css';

const formatPrice = (price) => {
  const numericPrice = Number(price);

  if (!Number.isFinite(numericPrice)) {
    return 'N/A';
  }

  return numericPrice.toLocaleString(undefined, {
    minimumFractionDigits: Number.isInteger(numericPrice) ? 2 : 0,
    maximumFractionDigits: Number.isInteger(numericPrice) ? 2 : 6,
  });
};

const formatTime = (last_updated_at) => {
  const dateObj = new Date(last_updated_at);

  let hours = dateObj.getHours();
  const minutes = String(dateObj.getMinutes()).padStart(2, '0');
  const seconds = String(dateObj.getSeconds()).padStart(2, '0');

  if (hours > 12) {
    hours -= 12;
    return `${String(hours).padStart(2, '0')}:${minutes}:${seconds} PM`;
  }

  if (hours === 0) {
    hours = 12;
    return `12:${minutes}:${seconds} AM`;
  }

  return `${String(hours).padStart(2, '0')}:${minutes}:${seconds} AM`;
};

const formatCur = (market_volume) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(market_volume);
};

const formatPriceChange = (price_change_24h) => {
  const numericChange = Number(price_change_24h);

  if (!Number.isFinite(numericChange)) {
    return 'N/A';
  }

  return `${numericChange > 0 ? '+' : ''}${numericChange.toFixed(2)}%`;
};

const getPriceChangeClass = (price_change_24h) => {
  const numericChange = Number(price_change_24h);

  if (!Number.isFinite(numericChange)) {
    return 'price-neutral';
  }

  return numericChange >= 0 ? 'price-up' : 'price-down';
};

const Search = () => {
  const { coinId } = useParams();
  const navigate = useNavigate();
  const { authenticated, user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const { membershipMap, loading: watchlistLoading, removeCoin, refreshWatchlists } = useWatchlist();
  const [watchlistLoadingLocal, setWatchlistLoadingLocal] = useState(false);
  const [selectedWatchlistCoin, setSelectedWatchlistCoin] = useState(null);
  const [showWatchlistSelector, setShowWatchlistSelector] = useState(false);
  const [coinToRemove, setCoinToRemove] = useState(null);
  const [removeWatchlist, setRemoveWatchlist] = useState(null);
  const resultsPerPage = 10;

  const fetchCoinData = async (query, page = 1) => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await searchCoins(query, page, resultsPerPage);
      setSearchResults(data.results || data.coins || []);
      setTotalPages(data.total_pages || 0);
      if (data.page && data.page !== page) {
        setCurrentPage(data.page);
      }
    } catch (err) {
      setSearchResults([]);
      setTotalPages(0);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!coinId) {
      setSearchResults([]);
      setTotalPages(0);
      setCurrentPage(1);
      return;
    }

    setSearchTerm(coinId);
    fetchCoinData(coinId, currentPage);
  }, [coinId, currentPage]);


  const handleSearch = async (event) => {
    event.preventDefault();

    const query = searchTerm.trim();
    if (!query) {
      setSearchResults([]);
      setTotalPages(0);
      setError('Enter a coin name or ticker to search.');
      return;
    }

    setCurrentPage(1);
    navigate(`/coins/search/${encodeURIComponent(query)}`);
  };

  const handleWatchlistButtonClick = async (coin) => {
    if (!authenticated) {
      alert('Please log in to manage your watchlist.');
      return;
    }

    setSelectedWatchlistCoin(coin);
    setShowWatchlistSelector(true);
  };

  const handleCancelRemoval = () => {
    setCoinToRemove(null);
    setRemoveWatchlist(null);
  };

  const handleConfirmRemoval = async () => {
    if (!coinToRemove || !removeWatchlist) {
      handleCancelRemoval();
      return;
    }

    setWatchlistLoadingLocal(true);
    try {
      await removeCoin(coinToRemove.ticker, removeWatchlist.id);
      await refreshWatchlists();
      alert(`${coinToRemove.coin_name} removed from ${removeWatchlist.name}.`);
    } catch (err) {
      alert(err.message || 'Failed to remove from watchlist.');
    } finally {
      setWatchlistLoadingLocal(false);
      handleCancelRemoval();
    }
  };

  const handleWatchlistSelectorClose = () => {
    setShowWatchlistSelector(false);
    setSelectedWatchlistCoin(null);
  };

  const handleWatchlistSelectorSuccess = async () => {
    setShowWatchlistSelector(false);
    await refreshWatchlists();
    if (selectedWatchlistCoin) {
      alert(`${selectedWatchlistCoin.coin_name} added to your watchlist.`);
    }
    setSelectedWatchlistCoin(null);
  };

  const handleRemoveMembershipFromSelector = async (membership) => {
    if (!user?.id || !membership?.watchlist_id) {
      return;
    }

    setWatchlistLoadingLocal(true);
    try {
      await removeCoin(selectedWatchlistCoin.ticker, membership.watchlist_id);
      await refreshWatchlists();
      alert(`${selectedWatchlistCoin.coin_name} removed from ${membership.watchlist_name}.`);
    } catch (err) {
      alert(err.message || 'Failed to remove from watchlist.');
    } finally {
      setWatchlistLoadingLocal(false);
    }
  };

  return (
    <div className="search-page">
      <h1>Search Coins</h1>

      {!coinId && (
        <SearchBar
          id="coin-search"
          name="coinSearch"
          placeholder="Search by coin name or ticker"
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          onSubmit={handleSearch}
        />
      )}

      <div className="search-results">
        {isLoading && <p>Loading Coin Data ...</p>}
        {error && <p className="price-down">{error}</p>}

        {!isLoading && !error && coinId && searchResults.length === 0 && (
          <p>No coins found.</p>
        )}

        {!isLoading && !error && searchResults.map((coin) => (
          <div key={coin.ticker} className="search-item">
            <div className="search-result">
              <div className="search-result-layout">
                <div className="search-result-details">
                  <h2>{coin.coin_name}</h2>
                  <p>Ticker: <b>{coin.ticker}</b></p>
                  <p>Price: ${formatPrice(coin.price)}</p>
                  <p className={getPriceChangeClass(coin.price_change_24h)}>
                    Change (24h): {formatPriceChange(coin.price_change_24h)}
                  </p>
                  <p>Total Market Volume: {formatCur(coin.market_volume)}</p>
                  <p>Market Cap Rank: {coin.market_cap_rank}</p>
                  <p>Last Updated at: {formatTime(coin.last_updated_at)}</p>
                </div>
              </div>
            </div>

            <div className="search-result-chart search-result-chart--fullwidth">
              <CoinChart
                coin={coin}
                height={260}
                showAxes
              />
              <button
                type="button"
                className="watchlist-button"
                onClick={() => handleWatchlistButtonClick(coin)}
                disabled={watchlistLoading || watchlistLoadingLocal}
              >
                {watchlistLoading || watchlistLoadingLocal
                  ? 'Working...'
                  : (membershipMap[coin.ticker] || []).length > 0
                    ? `Manage (${(membershipMap[coin.ticker] || []).length})`
                    : 'Add to Watchlist'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {!isLoading && !error && totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          ariaLabel="Search results pagination"
        />
      )}

      {showWatchlistSelector && selectedWatchlistCoin && (
        <WatchlistSelector
          coin={selectedWatchlistCoin}
          onClose={handleWatchlistSelectorClose}
          onSuccess={handleWatchlistSelectorSuccess}
          existingMemberships={membershipMap[selectedWatchlistCoin.ticker] || []}
          onRemove={handleRemoveMembershipFromSelector}
        />
      )}

      {coinToRemove && removeWatchlist && (
        <ConfirmationModal
          title={`Remove ${coinToRemove.coin_name} from ${removeWatchlist.name}?`}
          message={`This action cannot be undone. ${coinToRemove.coin_name} will be removed from ${removeWatchlist.name}.`}
          confirmLabel="Remove"
          cancelLabel="Cancel"
          variant="danger"
          loading={watchlistLoading}
          onCancel={handleCancelRemoval}
          onConfirm={handleConfirmRemoval}
        />
      )}
    </div>
  );
};

export default Search;
