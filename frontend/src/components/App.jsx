import '../styles/component_style/App.css';
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/authContext';
import { WatchlistProvider } from '../context/watchlistContext';

// Components
import AppContent from './AppContent';

const Home = lazy(() => import('../pages/Home'));
const Prices = lazy(() => import('../pages/Prices'));
const Watchlist = lazy(() => import('../pages/Watchlist'));
const Login = lazy(() => import('../pages/Login'));
const Register = lazy(() => import('../pages/Register'));
const VerificationPending = lazy(() => import('../pages/VerificationPending'));
const About = lazy(() => import('../pages/About'));
const Contact = lazy(() => import('../pages/Contact'));
const Privacy = lazy(() => import('../pages/Privacy'));
const Logout = lazy(() => import('../pages/Logout'));
const Profile = lazy(() => import('../pages/Profile'));
const Settings = lazy(() => import('../pages/Settings'));
const Search = lazy(() => import('../pages/Search'));

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WatchlistProvider>
          <AppContent>
            <Suspense fallback={<main className="app-loading">Loading...</main>}>
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
                <Route path="/search" element={<Search />} />
                <Route path="/coins/search/:coinId" element={<Search />} />
                <Route path="/logout" element={<Logout />} />
              </Routes>
            </Suspense>
          </AppContent>
        </WatchlistProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
