import '../styles/component_style/navbar.css';
import { Link, NavLink } from 'react-router-dom';
import { useMemo, useState } from 'react';
import SearchBar from './SearchBar.jsx';
import Button from './Button.jsx';

function Navbar({ brand = 'PREX', links = [], action, search = {} }) {
    const [accountMenuOpen, setAccountMenuOpen] = useState(false);
    const initials = useMemo(() => {
        const name = action?.username || action?.email || 'User';
        return name
            .split(/[.\s_-]+/)
            .filter(Boolean)
            .slice(0, 2)
            .map((part) => part[0]?.toUpperCase())
            .join('') || 'U';
    }, [action]);

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
            {action?.type === 'account' ? (
                <div className="account-menu">
                    <button
                        className="account-avatar"
                        type="button"
                        aria-label="Open account menu"
                        aria-expanded={accountMenuOpen}
                        onClick={() => setAccountMenuOpen((open) => !open)}
                    >
                        {initials}
                    </button>
                    {accountMenuOpen && (
                        <div className="account-dropdown">
                            <NavLink to="/profile" onClick={() => setAccountMenuOpen(false)}>
                                Profile
                            </NavLink>
                            <NavLink to="/settings" onClick={() => setAccountMenuOpen(false)}>
                                Settings
                            </NavLink>
                            <NavLink to="/logout" onClick={() => setAccountMenuOpen(false)}>
                                Logout
                            </NavLink>
                        </div>
                    )}
                </div>
            ) : (
                action && <Button className={action.className} name={action.label} href={action.href} />
            )}
        </nav>
    );
}

export default Navbar;
