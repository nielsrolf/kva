import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import RunList from './components/RunList';
import RunDetails from './components/RunDetails';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/view/:path" element={<RunDetails />} />
        <Route path="/" element={<RunList />} />
      </Routes>
    </Router>
  );
};

export default App;
