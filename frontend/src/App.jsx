import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SearchProvider } from './context/SearchContext';
import SearchPage from './pages/SearchPage';

const App = () => (
  <Router>
    <SearchProvider>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        {/* Add more routes here as needed */}
      </Routes>
    </SearchProvider>
  </Router>
);

export default App;

// import React from 'react';
// import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
// import SearchPage from './pages/SearchPage';
// import { SearchProvider } from './context/SearchContext';

// const App = () => (
//   <SearchProvider>
//     <Router>
//       <Routes>
//         <Route path="/" element={<SearchPage />} />
//       </Routes>
//     </Router>
//   </SearchProvider>
// );

// export default App;
