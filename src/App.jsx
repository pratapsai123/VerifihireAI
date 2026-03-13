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

import Layout from './components/Layout';

import CompaniesPage from './pages/CompaniesPage';
import DashboardHome from './pages/DashboardHome';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Approvals (The original main page) */}
        <Route path="/" element={
          <Layout>
            <SuperAdminDashboard />
          </Layout>
        } />
        {/* New Overview Dashboard */}
        <Route path="/dashboard" element={
          <Layout>
            <DashboardHome />
          </Layout>
        } />
        <Route path="/companies" element={
          <Layout>
            <CompaniesPage />
          </Layout>
        } />
        <Route path="/login" element={<AdminLogin />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
