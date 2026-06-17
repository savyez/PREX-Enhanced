import { useAuth } from '../context/AuthContext';
import Navbar from './Navbar';
import Footer from './Footer';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function AppContent({ children }) {
  const { authenticated, user } = useAuth();
  const navigate = useNavigate();
  const [navSearchTerm, setNavSearchTerm] = useState('');

  const handleNavSearch = (event) => {
    event.preventDefault();

    const query = navSearchTerm.trim();
    if (!query) {
      return;
    }

    navigate(`/coins/search/${encodeURIComponent(query)}`);
  };

  const navLinks = authenticated
    ? [
        { label: 'Home', href: '/' },
        { label: 'Prices', href: '/prices' },
        { label: 'Watchlist', href: '/watchlist' },
        { label: 'About', href: '/about' },
        { label: 'Contact', href: '/contact' },
      ]
    : [
        { label: 'Home', href: '/' },
        { label: 'Prices', href: '/prices' },
        { label: 'Watchlist', href: '/watchlist' },
        { label: 'About', href: '/about' },
        { label: 'Contact', href: '/contact' },
        { label: 'Register', href: '/register' },
      ];

  const navAction = authenticated
    ? {
        type: 'account',
        username: user?.username,
        email: user?.email,
      }
    : {
        label: 'Login',
        href: '/login',
        className: 'login-button',
      };

  return (
    <div className="app">
      <Navbar
        brand="PREX"
        links={navLinks}
        action={navAction}
        search={{
          id: 'nav-coin-search',
          name: 'navCoinSearch',
          placeholder: 'Search coins...',
          buttonLabel: 'Search',
          value: navSearchTerm,
          onChange: (event) => setNavSearchTerm(event.target.value),
          onSubmit: handleNavSearch,
        }}
      />

      {children}

      <Footer />
    </div>
  );
}

export default AppContent;
