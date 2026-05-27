import Card from '../components/Card.jsx';
import '../styles/prices.css';
import { useEffect, useState } from 'react';
import Button from '../components/Button.jsx';

function Prices() {

    const [coins, setCoins] = useState([]);
    
    const [isLoading, setIsLoading] = useState(true);

    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCoins = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/v1/coins/', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch coin data');
                }
                const data = await response.json();
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
                {coins.map((coin) => (
                    <Card key={coin.ticker} className="price-card">
                        <div>
                            <h3>{coin.coin_name}</h3>
                            <span>{coin.ticker}</span>
                        </div>
                        <strong>${Number(coin.price).toLocaleString()}</strong>
                        <p>change: {coin.change_24h}%</p>
                        <Button className="watchlist-button" name = "Add to Watchlist" href={`/watchlist/add/${coin.ticker}`} />
                        <Button className="details-button" name = "details" href={`/coins/${coin.ticker}`} />
                    </Card>
                )).slice(0, 12)}
            </section>
        </main>
    );
}

export default Prices;
