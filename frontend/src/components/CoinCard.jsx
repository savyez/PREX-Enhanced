import Button from './Button.jsx';
import Card from './Card.jsx';
import { useNavigate } from 'react-router-dom';
import '../styles/component_style/coinCard.css';

function CoinCard({ coin, rank, onWatchlistClick }) { 
    const navigate = useNavigate();
    const price = Number(coin.price).toLocaleString();
    const change = coin.change_24h ?? 'N/A';

    return (
        <Card className="price-card" onClick={() => navigate(`/coins/${coin.ticker}`)}>
            <div className="coin-header">
                <div>
                    <h3>{coin.coin_name}</h3>
                    <span>{coin.ticker}</span>
                </div>

                <div className="coin-rank">
                    #{rank}
                </div>
            </div>

            <p>change: {change}%</p>
            <div className="coin-price">
                <strong>${price}</strong>
            </div>
            <button
                className="watchlist-button"
                onClick={(e) => {
                    e.stopPropagation();
                    onWatchlistClick();
                }}>    
                Add to Watchlist
            </button>
        </Card>
    );
}

export default CoinCard;
