// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import HomePage from './pages/HomePage';
import RegistrationPage from './pages/RegistrationPage';
import TransferPage from './pages/TransferPage';
import VotingPage from './pages/VotingPage';
import AdminDashboard from './pages/AdminDashboard';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/register" element={<RegistrationPage />} />
          <Route path="/transfer" element={<TransferPage />} />
          <Route path="/vote" element={<VotingPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;