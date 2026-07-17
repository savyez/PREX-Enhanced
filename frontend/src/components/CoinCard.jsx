import Card from './Card.jsx';
import CoinChart from './CoinChart.jsx';
import '../styles/component_style/coinCard.css';

function CoinCard({ coin, rank, onWatchlistClick, onCardClick, }) {
    const price = Number(coin.price).toLocaleString();
    const priceChange = Number(coin.price_change_24h);
    const hasPriceChange = Number.isFinite(priceChange);
    const priceChangeClass = !hasPriceChange ? 'price-neutral' : priceChange >= 0 ? 'price-up' : 'price-down';
    const formattedPriceChange = hasPriceChange
        ? `${priceChange > 0 ? '+' : ''}${priceChange.toFixed(2)}%`
        : 'N/A';

    return (
        <Card
            className="price-card"
            onClick={onCardClick}
        >
            <div className="coin-header">
                <div>
                    <h3>{coin.coin_name}</h3>
                    <span>{coin.ticker}</span>
                </div>

                <div className="coin-rank">
                    #{rank}
                </div>
            </div>

            <p className={`price-change ${priceChangeClass}`}>Change(24h): {formattedPriceChange}</p>

            <div className="coin-price">
                <strong>${price}</strong>
            </div>

            <CoinChart
                coin={coin}
                height={84}
            />

            <button
                className="watchlist-button"
                onClick={(e) => {
                    e.stopPropagation();
                    onWatchlistClick();
                }}
            >
                Add to Watchlist
            </button>
        </Card>
    );
}

export default CoinCard;
