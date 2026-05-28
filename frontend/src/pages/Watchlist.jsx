import '../styles/page_style/watchlist.css';

function Watchlist() {
    return (
        <main className="watchlist-page">
            {user?.watchlist?.length > 0 ? (
                <>
                    <h2>Your Watchlist</h2>
                    <div className="watchlist-grid">
                        {user.watchlist.map((coin) => (
                            <div key={coin.id} className="watchlist-item">
                                <h3>{coin.name}</h3>
                                <p>Price: ${coin.price.toFixed(2)}</p>
                            </div>
                        ))}
                    </div>
                </>
            ) : (
                <>
                    <h2>Your Watchlist is Empty</h2>
                    <p>Start adding coins to your watchlist to see them here.</p>
                    <Button className="explore-prices" name="Explore Coins" href="/prices" />
                </>
            )}
        </main>
    );
}

export default Watchlist;
