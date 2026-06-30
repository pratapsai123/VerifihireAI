import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = () => {
    // We check for user data instead of auth token because the access token is in-memory 
    // and might be lost on refresh, but the session is maintained via HTTP-only cookie.
    const user = localStorage.getItem('user');

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
