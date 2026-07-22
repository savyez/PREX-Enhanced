import '../styles/page_style/about.css';

const About = () => {
    return (
        <div className="about-page">
            <main className="about-main">
                <section className="about-hero">
                    <div className="about-content">
                        <span className="about-eyebrow">About PREX</span>
                        <h1>Understand the market. Organize your watchlist.</h1>
                        <p>
                            PREX is a cryptocurrency tracking app that brings current market
                            data, coin search, seven-day price trends, and personal watchlists
                            into one focused workspace.
                        </p>
                    </div>

                    <aside className="about-panel">
                        <h2>What PREX helps you do</h2>
                        <ul>
                            <li>Browse paginated cryptocurrency market data</li>
                            <li>Search coins by name or ticker and view seven-day trends</li>
                            <li>Create watchlists and manage coin membership across them</li>
                            <li>Keep your account protected with email verification and session handling</li>
                        </ul>
                    </aside>
                </section>
            </main>
        </div>
    );
}

export default About;
