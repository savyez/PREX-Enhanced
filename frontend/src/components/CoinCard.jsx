import { lazy, Suspense, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useWatchlist } from '../context/watchlistContext';
import Card from './Card.jsx';
import '../styles/component_style/coinCard.css';

const CoinChart = lazy(() => import('./CoinChart.jsx'));
const WatchlistSelector = lazy(() => import('./WatchlistSelector.jsx'));

function CoinCard({ coin, rank, onCardClick, showChart = false }) {
    const { authenticated } = useAuth();
    const { membershipMap, loading, removeCoin } = useWatchlist();
    const [watchlistLoading, setWatchlistLoading] = useState(false);
    const [showWatchlistSelector, setShowWatchlistSelector] = useState(false);
    const memberWatchlists = membershipMap[coin?.ticker] || [];

    const price = Number(coin.price).toLocaleString();
    const priceChange = Number(coin.price_change_24h);
    const hasPriceChange = Number.isFinite(priceChange);
    const priceChangeClass = !hasPriceChange ? 'price-neutral' : priceChange >= 0 ? 'price-up' : 'price-down';
    const formattedPriceChange = hasPriceChange
        ? `${priceChange > 0 ? '+' : ''}${priceChange.toFixed(2)}%`
        : 'N/A';


    const handleWatchlistButtonClick = async (event) => {
        event.stopPropagation();

        if (!authenticated) {
            alert('Please log in to manage your watchlist');
            return;
        }

        setShowWatchlistSelector(true);
    };

    const handleRemoveMembership = async (membership) => {
        if (!membership?.watchlist_id) {
            return;
        }

        try {
            setWatchlistLoading(true);
            await removeCoin(coin.ticker, membership.watchlist_id);
            alert(`${coin.coin_name} removed from ${membership.watchlist_name}`);
        } catch (err) {
            alert(err.message || 'Failed to remove from watchlist');
        } finally {
            setWatchlistLoading(false);
        }
    };

    const handleWatchlistSelectorClose = () => {
        setShowWatchlistSelector(false);
    };

    const handleWatchlistSelectorSuccess = async () => {
        setShowWatchlistSelector(false);
        alert(`${coin.coin_name} added to your watchlist`);
    };

    return (
        <>
            <Card className="price-card" onClick={onCardClick}>
                <div className="coin-header">
                    <div>
                        <h3>{coin.coin_name}</h3>
                        <span>{coin.ticker}</span>
                    </div>

                    <div className="coin-rank">#{rank}</div>
                </div>

                <p className={`price-change ${priceChangeClass}`}>Change(24h): {formattedPriceChange}</p>

                <div className="coin-price">
                    <strong>${price}</strong>
                </div>

                {showChart && (
                    <Suspense fallback={null}>
                        <CoinChart
                            coin={coin}
                            height={84}
                        />
                    </Suspense>
                )}

                <div className="price-card-actions">
                    <button
                        className="watchlist-button"
                        onClick={handleWatchlistButtonClick}
                        disabled={watchlistLoading}
                    >
                        {watchlistLoading || loading
                            ? 'Checking...'
                            : memberWatchlists.length > 0
                            ? `Manage (${memberWatchlists.length})`
                            : 'Add to Watchlist'}
                    </button>

                    {onCardClick && (
                        <button
                            className="view-details-button"
                            onClick={(e) => {
                                e.stopPropagation();
                                onCardClick();
                            }}
                        >
                            View details
                        </button>
                    )}
                </div>
            </Card>

            {showWatchlistSelector && (
                <Suspense fallback={null}>
                    <WatchlistSelector
                        coin={coin}
                        onClose={handleWatchlistSelectorClose}
                        onSuccess={handleWatchlistSelectorSuccess}
                        existingMemberships={memberWatchlists}
                        onRemove={handleRemoveMembership}
                    />
                </Suspense>
            )}
        </>
    );
}

export default CoinCard;
