import '../styles/component_style/App.css';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

import { isAuthenticated, getUser } from '../utils/auth';

// Components
import Navbar from './Navbar';
import Footer from './Footer';

// Pages
import Home from '../pages/Home';
import Prices from '../pages/Prices';
import Watchlist from '../pages/Watchlist';
import Login from '../pages/Login';
import Register from '../pages/Register';
import About from '../pages/About';
import Contact from '../pages/Contact';
import Privacy from '../pages/Privacy';
import Logout from '../pages/Logout';
import Profile from '../pages/Profile';
import Settings from '../pages/Settings';

function AppContent() {
const [authenticated, setAuthenticated] = useState(isAuthenticated());
const [user, setUser] = useState(getUser());
const location = useLocation();

// Re-check auth status on route change
useEffect(() => {
  setAuthenticated(isAuthenticated());
  setUser(getUser());
}, [location]);

// Listen for auth changes
useEffect(() => {
  const handleStorageChange = () => {
    setAuthenticated(isAuthenticated());
    setUser(getUser());
  };

  const handleAuthChange = () => {
    setAuthenticated(isAuthenticated());
    setUser(getUser());
  };

  window.addEventListener('storage', handleStorageChange);
  window.addEventListener('authchange', handleAuthChange);
  
  return () => {
    window.removeEventListener('storage', handleStorageChange);
    window.removeEventListener('authchange', handleAuthChange);
  };
}, []);

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

    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/prices" element={<Prices />} />
      <Route path="/watchlist" element={<Watchlist />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/about" element={<About />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/logout" element={<Logout />} />
    </Routes>

    <Footer />
  </div>
);
}

function App() {
return (
  <BrowserRouter>
    <AppContent />
  </BrowserRouter>
);
}

export default App;
