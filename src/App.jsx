import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SuperAdminDashboard from './pages/SuperAdminDashboard';
import AdminLogin from './pages/AdminLogin';
import './App.css';

// Minimal Axios Interceptor for Auth Token
import axios from 'axios';
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SuperAdminDashboard />} />
        <Route path="/login" element={<AdminLogin />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
