import "../styles/component_style/footer.css";
import { Link } from "react-router-dom";
import coingeckoLogo from "../assets/coingecko.png";

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-content">
                <div className="footer-brand">
                    <Link to="/" className="footer-logo">PREX</Link>
                </div>

                <nav className="footer-nav">
                    <Link to="/about">About</Link>
                    <Link to="/contact">Contact</Link>
                    <Link to="/privacy">Privacy</Link>
                </nav>

                <div className="footer-bottom">
                    <p className="footer-copy">&copy; {new Date().getFullYear()} PREX. All rights reserved.</p>
                    <div className="footer-powered-by">
                        <p className="footer-powered-label">Powered by</p>
                        <img
                            className="footer-powered-image"
                            src={coingeckoLogo}
                            alt="Powered by CoinGecko"
                        />
                    </div>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
