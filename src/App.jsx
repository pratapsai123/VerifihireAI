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
      if (window.location.pathname !== '/admin/login') {
        window.location.href = '/admin/login';
      }
    }
    return Promise.reject(error);
  }
);

import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

import CompaniesPage from './pages/CompaniesPage';
import DashboardHome from './pages/DashboardHome';

function App() {
  return (
    <BrowserRouter basename="/admin">
      <Routes>
        {/* Approvals (The original main page) - Protected */}
        <Route path="/" element={
          <ProtectedRoute>
            <Layout>
              <SuperAdminDashboard />
            </Layout>
          </ProtectedRoute>
        } />
        {/* New Overview Dashboard - Protected */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout>
              <DashboardHome />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/companies" element={
          <ProtectedRoute>
            <Layout>
              <CompaniesPage />
            </Layout>
          </ProtectedRoute>
        } />
        <Route path="/login" element={<AdminLogin />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
