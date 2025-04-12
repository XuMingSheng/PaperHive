import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchPage from './pages/SearchPage';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<SearchPage />} />
      {/* Add more routes here as needed */}
    </Routes>
  </Router>
);

export default App;