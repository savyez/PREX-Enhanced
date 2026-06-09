import '../styles/component_style/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';

// Components
import AppContent from './AppContent';

// Pages
import Home from '../pages/Home';
import Prices from '../pages/Prices';
import Watchlist from '../pages/Watchlist';
import Login from '../pages/Login';
import Register from '../pages/Register';
import VerificationPending from '../pages/VerificationPending';
import About from '../pages/About';
import Contact from '../pages/Contact';
import Privacy from '../pages/Privacy';
import Logout from '../pages/Logout';
import Profile from '../pages/Profile';
import Settings from '../pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/prices" element={<Prices />} />
            <Route path="/watchlist" element={<Watchlist />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verification-pending" element={<VerificationPending />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/privacy" element={<Privacy />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/logout" element={<Logout />} />
          </Routes>
        </AppContent>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
