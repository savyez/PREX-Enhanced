import '../styles/navbar.css';
import { Link, NavLink } from 'react-router-dom';
import SearchBar from './SearchBar.jsx';
import Button from './Button.jsx';

function Navbar() {
    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">
                <h1 className="navbar-title">PREX</h1>
            </Link>
            <ul className="navbar-links">
                <li><NavLink to="/">Home</NavLink></li>
                <li><NavLink to="/prices">Prices</NavLink></li>
                <li><NavLink to="/watchlist">Watchlist</NavLink></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>

            <SearchBar />
            <Button className="login-button" name="Login" href="#login" />
        </nav>
    );
}

export default Navbar;
