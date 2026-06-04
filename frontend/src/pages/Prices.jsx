import '../styles/page_style/prices.css';
import { useEffect, useState } from 'react';
import CoinCard from '../components/CoinCard.jsx';
import { getCoins } from '../utils/api.js';

function Prices() {

    const [coins, setCoins] = useState([]);
    
    const [isLoading, setIsLoading] = useState(true);

    const [error, setError] = useState(null);

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


    return (
        <main className="prices-page">
            {isLoading && <p>Loading prices...</p>}
            {error && <p className="price-down">{error}</p>}
            <section className="prices-grid" aria-label="Coin prices">
                {coins.slice(0, 12).map((coin) => (
                    <CoinCard
                        key={coin.ticker}
                        coin={coin}
                        onWatchlistHref={`/watchlist/add/${coin.ticker}`}
                        detailsHref={`/coins/${coin.ticker}`}
                    />
                ))}
            </section>
        </main>
    );
}

export default Prices;
