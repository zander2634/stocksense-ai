import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h2>📦 StockSense AI</h2>
      </div>

      <div className="navbar-links">
        <Link to="/dashboard" className={isActive('/dashboard')}>Dashboard</Link>
        <Link to="/products" className={isActive('/products')}>Products</Link>
        <Link to="/categories" className={isActive('/categories')}>Categories</Link>
        <Link to="/suppliers" className={isActive('/suppliers')}>Suppliers</Link>
        <Link to="/sales" className={isActive('/sales')}>Sales</Link>
        <Link to="/forecast" className={isActive('/forecast')}>Forecast</Link>
        <Link to="/alerts" className={isActive('/alerts')}>Alerts</Link>
      </div>

      <div className="navbar-user">
        <span>👤 {user?.username} ({user?.role})</span>
        <button onClick={handleLogout} className="btn-logout">Logout</button>
      </div>
    </nav>
  );
};

export default Navbar;