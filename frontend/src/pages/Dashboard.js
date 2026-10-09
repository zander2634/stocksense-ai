import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [lowStock, setLowStock] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [summaryRes, topRes, lowRes] = await Promise.all([
        api.get('/api/dashboard/summary'),
        api.get('/api/dashboard/top-products?limit=5'),
        api.get('/api/dashboard/low-stock'),
      ]);
      setSummary(summaryRes.data);
      setTopProducts(topRes.data);
      setLowStock(lowRes.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
    setLoading(false);
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (!summary) return <div className="error">Failed to load data</div>;

  return (
    <div className="dashboard">
      <h1>📊 Dashboard</h1>

      {/* Summary Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-info">
            <h3>{summary.total_products}</h3>
            <p>Total Products</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-info">
            <h3>₱{summary.total_inventory_value.toLocaleString()}</h3>
            <p>Inventory Value</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-info">
            <h3>₱{summary.sales_last_30_days.revenue.toLocaleString()}</h3>
            <p>30-Day Revenue</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <h3>{summary.low_stock_count}</h3>
            <p>Low Stock Items</p>
          </div>
        </div>
      </div>

      {/* Health Score */}
      <div className="health-score-card">
        <h2>Inventory Health Score</h2>
        <div className="health-score-bar">
          <div
            className="health-score-fill"
            style={{
              width: `${summary.inventory_health_score}%`,
              backgroundColor:
                summary.inventory_health_score >= 80
                  ? '#10b981'
                  : summary.inventory_health_score >= 60
                  ? '#f59e0b'
                  : '#ef4444',
            }}
          />
        </div>
        <p className="health-score-text">
          {summary.inventory_health_score}% Healthy
        </p>
      </div>

      {/* Top Products */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>🏆 Top Selling Products (30 days)</h2>
          {topProducts.length === 0 ? (
            <p className="empty-state">No sales data yet</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Sold</th>
                  <th>Revenue</th>
                </tr>
              </thead>
              <tbody>
                {topProducts.map((p) => (
                  <tr key={p.product_id}>
                    <td>{p.name}</td>
                    <td>{p.total_sold}</td>
                    <td>₱{p.total_revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Low Stock Alerts */}
        <div className="dashboard-card">
          <h2>⚠️ Low Stock Alerts</h2>
          {lowStock.length === 0 ? (
            <p className="empty-state">All products are well-stocked! ✅</p>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Stock</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {lowStock.map((p) => (
                  <tr key={p.product_id}>
                    <td>{p.name}</td>
                    <td>{p.stock_quantity}</td>
                    <td>
                      <span className={`badge badge-${p.status}`}>
                        {p.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;