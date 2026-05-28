import '../styles/App.css';

import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Navbar from './Navbar.jsx';
import Home from '../pages/Home.jsx';
import Prices from '../pages/Prices.jsx';
import Watchlist from '../pages/Watchlist.jsx';
import Login from '../pages/Login.jsx';

const navLinks = [
  { label: 'Home', href: '/' },
  { label: 'Prices', href: '/prices' },
  { label: 'Watchlist', href: '/watchlist' },
  { label: 'About', href: '#about' },
  { label: 'Contact', href: '#contact' },
];

const navAction = {
  label: 'Login',
  href: '/login',
  className: 'login-button',
};

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navbar
          brand="PREX"
          links={navLinks}
          action={navAction}
          search={{ placeholder: 'Search coins...', buttonLabel: 'Search' }}
        />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/prices" element={<Prices />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
