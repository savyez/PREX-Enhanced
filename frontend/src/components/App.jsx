import '../styles/App.css';

import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Navbar from './Navbar.jsx';
import Home from '../pages/Home.jsx';
import Prices from '../pages/Prices.jsx';
import Watchlist from '../pages/Watchlist.jsx';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/prices" element={<Prices />} />
          <Route path="/watchlist" element={<Watchlist />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
