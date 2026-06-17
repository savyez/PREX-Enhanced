import '../styles/page_style/prices.css';
import { useEffect, useState } from 'react';
import CoinCard from '../components/CoinCard.jsx';
import WatchlistSelector from '../components/WatchlistSelector.jsx';
import { getCoins } from '../utils/api.js';
import { useAuth } from '../context/AuthContext';
import { Navigate, useNavigate } from 'react-router-dom';

function Prices() {
    const { authenticated } = useAuth();
    const [coins, setCoins] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCoin, setSelectedCoin] = useState(null);
    const [showWatchlistSelector, setShowWatchlistSelector] = useState(false);

    useEffect(() => {
        const fetchCoins = async () => {
            try {
                const data = await getCoins();
                const coinsData = data.coins || data;
                const topCoinsData = coinsData.filter(coin => coin.market_cap_rank !== null && coin.market_cap_rank <= 100);
                topCoinsData.sort((a, b) => a.market_cap_rank - b.market_cap_rank);

                setCoins(topCoinsData);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCoins();
    }, []);

    const handleWatchlistClick = (coin) => {
        if (!authenticated) {
            alert('Please log in to add coins to your watchlist');
            return;
        }
        setSelectedCoin(coin);
        setShowWatchlistSelector(true);
    };

    const handleWatchlistSelectorClose = () => {
        setShowWatchlistSelector(false);
        setSelectedCoin(null);
    };

    const handleWatchlistSelectorSuccess = () => {
        setShowWatchlistSelector(false);
        setSelectedCoin(null);
        // Optionally show a success message
        alert(`${selectedCoin.coin_name} added to watchlist!`);
    };

    const handleCardClick = (coin) => {
        // Navigate to coin details page
        navigate(`/coins/${coin.ticker}`);
    }

    return (
        <main className="prices-page">
            <section className="prices-header">
                <h1>Top Cryptocurrencies</h1>
                <p>
                    Track prices and add coins to your watchlists.
                </p>
            </section>
            {isLoading && <p>Loading prices...</p>}
            {error && <p className="price-down">{error}</p>}
            <section className="prices-grid" aria-label="Coin prices">
                {coins.slice(0, 25).map((coin) => (
                    <CoinCard
                        key={coin.ticker}
                        coin={coin}
                        rank={coin.market_cap_rank}
                        onWatchlistClick={() => handleWatchlistClick(coin)}
                        onCardClick = {() => handleCardClick(coin)}
                    />
                ))}
            </section>

            {showWatchlistSelector && selectedCoin && (
                <WatchlistSelector
                    coin={selectedCoin}
                    onClose={handleWatchlistSelectorClose}
                    onSuccess={handleWatchlistSelectorSuccess}
                />
            )}
        </main>
    );
}

export default Prices;
