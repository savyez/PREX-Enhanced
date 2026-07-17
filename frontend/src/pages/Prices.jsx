import '../styles/page_style/prices.css';
import { useEffect, useState } from 'react';
import CoinCard from '../components/CoinCard.jsx';
import Pagination from '../components/Pagination.jsx';
import WatchlistSelector from '../components/WatchlistSelector.jsx';
import { getCoins } from '../utils/api.js';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function Prices() {
    const { authenticated } = useAuth();
    const [coins, setCoins] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedCoin, setSelectedCoin] = useState(null);
    const [showWatchlistSelector, setShowWatchlistSelector] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const coinsPerPage = 25;

    const navigate = useNavigate();

    useEffect(() => {
        const fetchCoins = async () => {
            try {
                setIsLoading(true);
                setError(null);
                const data = await getCoins(currentPage, coinsPerPage);
                const fetchedCoins = data.results || data.coins || [];

                setCoins(fetchedCoins);
                setTotalPages(data.total_pages || 0);
                if (data.page && data.page !== currentPage) {
                    setCurrentPage(data.page);
                }
            } catch (err) {
                setError(err.message);
                setCoins([]);
                setTotalPages(0);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCoins();
    }, [currentPage]);

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
        alert(`${selectedCoin.coin_name} added to watchlist!`);
    };

    const handleCardClick = (ticker) => {
        navigate(`/coins/search/${ticker}`);
    };

    return (
        <main className="prices-page">
            <section className="prices-header">
                <h1 className="top-header">Top Cryptocurrencies</h1>
            </section>

            <section className="prices-content">
                {isLoading && <p>Loading prices...</p>}
                {error && <p className="price-down">{error}</p>}

                <section className="prices-grid" aria-label="Coin prices">
                    {coins.map((coin) => (
                        <CoinCard
                            key={coin.ticker}
                            coin={coin}
                            rank={coin.market_cap_rank}
                            onWatchlistClick={() => handleWatchlistClick(coin)}
                            onCardClick={() => handleCardClick(coin.ticker)}
                        />
                    ))}
                </section>

                {!isLoading && !error && totalPages > 1 && (
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                        ariaLabel="Prices pagination"
                    />
                )}
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
