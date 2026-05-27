import Button from '../components/Button.jsx';
import '../styles/home.css';

function Home() {
    return (
        <main className="home-page">
            <section className="home-hero">
                <h2>Welcome to PREX</h2>
                <p>Track prices, follow market movement, and keep your crypto watchlist close.</p>
                <div className="home-actions">
                    <Button name="See Prices" href="/prices" />
                </div>
            </section>
        </main>
    );
}

export default Home;
