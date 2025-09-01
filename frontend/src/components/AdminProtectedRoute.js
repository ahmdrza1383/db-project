// src/components/AdminProtectedRoute.js
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const AdminProtectedRoute = () => {
    const userInfoString = localStorage.getItem('userInfo');
    const userInfo = userInfoString ? JSON.parse(userInfoString) : null;

    const isAdmin = userInfo && userInfo.user_role === 'ADMIN';

    return isAdmin ? <Outlet /> : <Navigate to="/" />;
};

export default AdminProtectedRoute;