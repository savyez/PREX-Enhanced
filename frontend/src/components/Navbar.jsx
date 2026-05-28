import '../styles/navbar.css';
import { Link, NavLink } from 'react-router-dom';
import SearchBar from './SearchBar.jsx';
import Button from './Button.jsx';

function Navbar({ brand = 'PREX', links = [], action, search = {} }) {
    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">
                <h1 className="navbar-title">{brand}</h1>
            </Link>
            <ul className="navbar-links">
                {links.map((link) => (
                    <li key={link.href}>
                        {link.href.startsWith('/') ? (
                            <NavLink to={link.href}>{link.label}</NavLink>
                        ) : (
                            <a href={link.href}>{link.label}</a>
                        )}
                    </li>
                ))}
            </ul>

            <SearchBar {...search} />
            {action && <Button className={action.className} name={action.label} href={action.href} />}
        </nav>
    );
}

export default Navbar;
