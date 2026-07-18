import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Card from './Card.jsx';
import CoinChart from './CoinChart.jsx';
import WatchlistSelector from './WatchlistSelector.jsx';
import {
    getWatchlists,
    getWatchlistItems,
    removeCoinFromWatchlist,
} from '../utils/api.js';
import '../styles/component_style/coinCard.css';

function CoinCard({ coin, rank, onCardClick }) {
    const { authenticated, user } = useAuth();
    const [isInWatchlist, setIsInWatchlist] = useState(false);
    const [memberWatchlist, setMemberWatchlist] = useState(null);
    const [watchlistLoading, setWatchlistLoading] = useState(false);
    const [showWatchlistSelector, setShowWatchlistSelector] = useState(false);

    const price = Number(coin.price).toLocaleString();
    const priceChange = Number(coin.price_change_24h);
    const hasPriceChange = Number.isFinite(priceChange);
    const priceChangeClass = !hasPriceChange ? 'price-neutral' : priceChange >= 0 ? 'price-up' : 'price-down';
    const formattedPriceChange = hasPriceChange
        ? `${priceChange > 0 ? '+' : ''}${priceChange.toFixed(2)}%`
        : 'N/A';

    useEffect(() => {
        let active = true;
        const loadMembership = async () => {
            if (!authenticated || !user?.id || !coin?.ticker) {
                if (active) {
                    setIsInWatchlist(false);
                    setMemberWatchlist(null);
                    setWatchlistLoading(false);
                }
                return;
            }

            setWatchlistLoading(true);

            try {
                const data = await getWatchlists(user.id);
                const watchlists = data.watchlists || [];
                let foundWatchlist = null;

                for (const watchlist of watchlists) {
                    const itemResponse = await getWatchlistItems(watchlist.id);
                    const items = itemResponse.items || [];

                    if (items.some((item) => item.ticker?.ticker === coin.ticker)) {
                        foundWatchlist = watchlist;
                        break;
                    }
                }

                if (active) {
                    setIsInWatchlist(Boolean(foundWatchlist));
                    setMemberWatchlist(foundWatchlist);
                }
            } catch (err) {
                if (active) {
                    setIsInWatchlist(false);
                    setMemberWatchlist(null);
                }
            } finally {
                if (active) {
                    setWatchlistLoading(false);
                }
            }
        };

        loadMembership();

        return () => {
            active = false;
        };
    }, [authenticated, user?.id, coin?.ticker]);

    const refreshMembership = async () => {
        if (!authenticated || !user?.id || !coin?.ticker) {
            setIsInWatchlist(false);
            setMemberWatchlist(null);
            return;
        }

        setWatchlistLoading(true);

        try {
            const data = await getWatchlists(user.id);
            const watchlists = data.watchlists || [];
            let foundWatchlist = null;

            for (const watchlist of watchlists) {
                const itemResponse = await getWatchlistItems(watchlist.id);
                const items = itemResponse.items || [];

                if (items.some((item) => item.ticker?.ticker === coin.ticker)) {
                    foundWatchlist = watchlist;
                    break;
                }
            }

            setIsInWatchlist(Boolean(foundWatchlist));
            setMemberWatchlist(foundWatchlist);
        } catch {
            setIsInWatchlist(false);
            setMemberWatchlist(null);
        } finally {
            setWatchlistLoading(false);
        }
    };

    const handleWatchlistButtonClick = async (event) => {
        event.stopPropagation();

        if (!authenticated) {
            alert('Please log in to manage your watchlist');
            return;
        }

        if (isInWatchlist && memberWatchlist) {
            try {
                setWatchlistLoading(true);
                await removeCoinFromWatchlist(user.id, memberWatchlist.id, coin.ticker);
                setIsInWatchlist(false);
                setMemberWatchlist(null);
                alert(`${coin.coin_name} removed from ${memberWatchlist.name}`);
            } catch (err) {
                alert(err.message || 'Failed to remove from watchlist');
            } finally {
                setWatchlistLoading(false);
            }
            return;
        }

        setShowWatchlistSelector(true);
    };

    const handleWatchlistSelectorClose = () => {
        setShowWatchlistSelector(false);
    };

    const handleWatchlistSelectorSuccess = async () => {
        setShowWatchlistSelector(false);
        await refreshMembership();
        alert(`${coin.coin_name} added to your watchlist`);
    };

    return (
        <>
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
                    onClick={handleWatchlistButtonClick}
                    disabled={watchlistLoading}
                >
                    {watchlistLoading
                        ? 'Checking...'
                        : isInWatchlist
                        ? 'Remove from Watchlist'
                        : 'Add to Watchlist'}
                </button>
            </Card>

            {showWatchlistSelector && (
                <WatchlistSelector
                    coin={coin}
                    onClose={handleWatchlistSelectorClose}
                    onSuccess={handleWatchlistSelectorSuccess}
                />
            )}
        </>
    );
}

export default CoinCard;
