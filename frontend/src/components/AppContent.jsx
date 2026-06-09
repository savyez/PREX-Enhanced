import { useAuth } from '../context/AuthContext';
import Navbar from './Navbar';
import Footer from './Footer';

function AppContent({ children }) {
  const { authenticated, user } = useAuth();

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
          placeholder: 'Search coins...',
          buttonLabel: 'Search',
        }}
      />

      {children}

      <Footer />
    </div>
  );
}

export default AppContent;
