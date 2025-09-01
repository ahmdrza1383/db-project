// src/components/UserProtectedRoute.js
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const UserProtectedRoute = () => {
    const userInfoString = localStorage.getItem('userInfo');
    const userInfo = userInfoString ? JSON.parse(userInfoString) : null;

    if (!userInfo) {
        return <Navigate to="/login" />;
    }

    if (userInfo.user_role === 'ADMIN') {
        return <Navigate to="/admin/dashboard" />;
    }

    return <Outlet />;
};

export default UserProtectedRoute;