import Button from './Button.jsx';
import Card from './Card.jsx';

function CoinCard({ coin, onWatchlistClick, detailsHref }) {
    const price = Number(coin.price).toLocaleString();
    const change = coin.change_24h ?? 'N/A';

    return (
        <Card className="price-card">
            <div>
                <h3>{coin.coin_name}</h3>
                <span>{coin.ticker}</span>
            </div>
            <strong>${price}</strong>
            <p>change: {change}%</p>
            <button 
                className="watchlist-button" 
                onClick={onWatchlistClick}
            >
                Add to Watchlist
            </button>
            <Button className="details-button" name="details" href={detailsHref} />
        </Card>
    );
}

export default CoinCard;
