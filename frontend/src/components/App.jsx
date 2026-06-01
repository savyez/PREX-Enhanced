import '../styles/component_style/App.css';

import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Components
import Navbar from './Navbar.jsx';
import Footer from './Footer.jsx';

// Pages
import Home from '../pages/Home.jsx';
import Prices from '../pages/Prices.jsx';
import Watchlist from '../pages/Watchlist.jsx';
import Login from '../pages/Login.jsx';
import Register from '../pages/Register.jsx';
import About from '../pages/About.jsx';
import Contact from '../pages/Contact.jsx';
import Privacy from '../pages/Privacy.jsx';

const navLinks = [
  { label: 'Home', href: '/' },
  { label: 'Prices', href: '/prices' },
  { label: 'Watchlist', href: '/watchlist' },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
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
          <Route path="/register" element={<Register />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/privacy" element={<Privacy />} />
        </Routes>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
