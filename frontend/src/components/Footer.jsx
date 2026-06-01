import "../styles/component_style/footer.css";
import { Link } from "react-router-dom";

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-content">
                <div className="footer-brand">
                    <Link to="/" className="footer-logo">PREX</Link>
                    <p>Helpful content and services, built for a smoother experience.</p>
                </div>

                <nav className="footer-nav">
                    <Link to="/about">About</Link>
                    <Link to="/contact">Contact</Link>
                    <Link to="/privacy">Privacy</Link>
                </nav>

                <p className="footer-copy">&copy; {new Date().getFullYear()} PREX. All rights reserved.</p>
            </div>
        </footer>
    );
}

export default Footer;
