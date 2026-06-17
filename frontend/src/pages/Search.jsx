import SearchBar from '../components/SearchBar';
import { searchCoins } from '../utils/api.js';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
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
    } else if (hours === 0) {
        hours = 12;
        return `12:${minutes}:${seconds} AM`;
    } else {
        return `${String(hours).padStart(2, '0')}:${minutes}:${seconds} AM`;
    }
}

const formatCur = (market_volume) => {
    const formattedCurrency = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    }).format(market_volume);

    return formattedCurrency
}

const Search = () => {
  const { coinId } = useParams();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCoinData = async (query) => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await searchCoins(query);
      setSearchResults(data.coins || []);
    } catch (err) {
      setSearchResults([]);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!coinId) {
      return;
    }

    setSearchTerm(coinId);
    fetchCoinData(coinId);
  }, [coinId]);

  const handleSearch = async (event) => {
    event.preventDefault();

    const query = searchTerm.trim();
    if (!query) {
      setSearchResults([]);
      setError('Enter a coin name or ticker to search.');
      return;
    }

    navigate(`/coins/search/${encodeURIComponent(query)}`);
    
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
          <div key={coin.ticker} className="search-result">
            <h2>Name: {coin.coin_name}</h2>
            <p>Ticker: <b>{coin.ticker}</b></p>
            <p>Price: ${formatPrice(coin.price)}</p>
            <p>Total Market Volume: {formatCur(coin.market_volume)}</p>
            <p>Market Cap Rank: {coin.market_cap_rank}</p>
            <p>Last Updated at: {formatTime(coin.last_updated_at)}</p>

          </div>
        ))}
      </div>
    </div>
  );
};

export default Search;
