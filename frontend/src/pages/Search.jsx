import SearchBar from '../components/SearchBar';
import Pagination from '../components/Pagination.jsx';
import ConfirmationModal from '../modals/ConfirmationModal.jsx';
import { searchCoins } from '../utils/api.js';
import { lazy, Suspense, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/authContext.jsx';
import { useWatchlist } from '../context/watchlistContext.jsx';
import { useAlert } from '../context/alertContext.jsx';
import '../styles/page_style/search.css';


const CoinChart = lazy(() => import('../components/CoinChart.jsx'));
const WatchlistSelector = lazy(() => import('../components/WatchlistSelector.jsx'));

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
  const { showAlert } = useAlert();
  const resultsPerPage = 10;
  const displayedResults = coinId ? searchResults : [];
  const displayedError = coinId ? error : null;

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
      return;
    }

    const requestTimer = window.setTimeout(() => {
      fetchCoinData(coinId, currentPage);
    }, 0);

    return () => window.clearTimeout(requestTimer);
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
      showAlert('Please log in to manage your watchlist.', 'warning');
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
      showAlert(`${coinToRemove.coin_name} removed from ${removeWatchlist.name}.`, 'success');
    } catch (err) {
      showAlert(err.message || 'Failed to remove from watchlist.', 'error');
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
      showAlert(`${selectedWatchlistCoin.coin_name} added to your watchlist.`, 'success');
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
      showAlert(`${selectedWatchlistCoin.coin_name} removed from ${membership.watchlist_name}.`, 'success');
    } catch (err) {
      showAlert(err.message || 'Failed to remove from watchlist.', 'error');
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
        {displayedError && <p className="price-down">{displayedError}</p>}

        {!isLoading && !displayedError && coinId && displayedResults.length === 0 && (
          <p>No coins found.</p>
        )}

        {!isLoading && !displayedError && displayedResults.map((coin) => (
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
              <Suspense fallback={null}>
                <CoinChart
                  coin={coin}
                  height={260}
                  showAxes
                />
              </Suspense>
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

      {!isLoading && !displayedError && coinId && totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          ariaLabel="Search results pagination"
        />
      )}

      {showWatchlistSelector && selectedWatchlistCoin && (
        <Suspense fallback={null}>
          <WatchlistSelector
            coin={selectedWatchlistCoin}
            onClose={handleWatchlistSelectorClose}
            onSuccess={handleWatchlistSelectorSuccess}
            existingMemberships={membershipMap[selectedWatchlistCoin.ticker] || []}
            onRemove={handleRemoveMembershipFromSelector}
          />
        </Suspense>
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
