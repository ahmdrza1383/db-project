import React from 'react';
import {BrowserRouter as Router, Routes, Route, Navigate} from 'react-router-dom';
import Home from './components/Home';
import Register from './components/Register';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import UserProfile from './components/UserProfile';
import ReservationHistory from './components/ReservationHistory';
import ShoppingCart from './components/ShoppingCart';

import AdminProtectedRoute from './components/AdminProtectedRoute';
import UserProtectedRoute from "./components/UserProtectedRoute";

import AdminDashboard from './components/admin/AdminDashboard';
import AdminReports from './components/admin/AdminReports';
import AdminRequests from './components/admin/AdminRequests';

function App() {
    const isAuthenticated = localStorage.getItem('accessToken');

    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/" element={<Home/>}/>
                    <Route path="/signup" element={<Register/>}/>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route element={<UserProtectedRoute/>}>
                        <Route path="/dashboard"
                               element={isAuthenticated ? <Dashboard/> : <Navigate to="/login" replace/>}/>
                        <Route path="/profile"
                               element={isAuthenticated ? <UserProfile/> : <Navigate to="/login" replace/>}/>
                        <Route path="/history"
                               element={isAuthenticated ? <ReservationHistory/> : <Navigate to="/login" replace/>}/>
                        <Route path="/cart"
                               element={isAuthenticated ? <ShoppingCart/> : <Navigate to="/login" replace/>}/>
                    </Route>

                    <Route element={<AdminProtectedRoute/>}>
                        <Route path="/admin/dashboard" element={<AdminDashboard/>}/>
                        <Route path="/admin/reports" element={<AdminReports/>}/>
                        <Route path="/admin/requests" element={<AdminRequests/>}/>
                    </Route>
                </Routes>
            </div>
        </Router>
    );
}

export default App;
