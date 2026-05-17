import '../styles/navbar.css';
import SearchBar from './SearchBar.jsx';

function Navbar() {
    return (
        <nav className="navbar">
            <a href="#home"><h1 className="navbar-title">PREX</h1></a>
            <ul className="navbar-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>

            <SearchBar />
        </nav>
    );
}

export default Navbar;
