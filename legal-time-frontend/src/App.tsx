// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Timesheets from './pages/Timesheets';
import Matters from './pages/Matters';
import PrivateRoute from './components/PrivateRoute';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        {/* Защищённые маршруты */}
        <Route element={<PrivateRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/timesheets" element={<Timesheets />} />
          <Route path="/matters" element={<Matters />} />
        </Route>

        <Route path="*" element={<div>404 — Страница не найдена</div>} />
      </Routes>
    </Router>
  );
}

export default App;