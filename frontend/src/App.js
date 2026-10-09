import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Categories from './pages/Categories';
import Suppliers from './pages/Suppliers';
import Sales from './pages/Sales';
import Forecast from './pages/Forecast';
import Alerts from './pages/Alerts';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  
  console.log('🛡️ ProtectedRoute:', { isAuthenticated, loading, user });
  
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '18px',
        color: '#6b7280'
      }}>
        🔄 Loading...
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const Layout = ({ children }) => {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="app-content">{children}</main>
    </div>
  );
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
 <Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Layout><Dashboard /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/products"
  element={
    <ProtectedRoute>
      <Layout><Products /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/categories"
  element={
    <ProtectedRoute>
      <Layout><Categories /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/suppliers"
  element={
    <ProtectedRoute>
      <Layout><Suppliers /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/sales"
  element={
    <ProtectedRoute>
      <Layout><Sales /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/forecast"
  element={
    <ProtectedRoute>
      <Layout><Forecast /></Layout>
    </ProtectedRoute>
  }
/>
<Route
  path="/alerts"
  element={
    <ProtectedRoute>
      <Layout><Alerts /></Layout>
    </ProtectedRoute>
  }
/>
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;