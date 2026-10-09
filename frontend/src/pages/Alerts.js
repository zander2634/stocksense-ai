import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await api.get('/api/alerts/');
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'critical': return 'alert-critical';
      case 'high': return 'alert-high';
      case 'medium': return 'alert-medium';
      default: return 'alert-low';
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'out_of_stock': return '🚨';
      case 'low_stock': return '⚠️';
      case 'overstock': return '📦';
      case 'slow_moving': return '🐌';
      default: return 'ℹ️';
    }
  };

  if (loading) return <div className="loading">Loading alerts...</div>;

  const criticalCount = alerts.filter((a) => a.severity === 'critical').length;
  const highCount = alerts.filter((a) => a.severity === 'high').length;
  const mediumCount = alerts.filter((a) => a.severity === 'medium').length;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🔔 Alerts</h1>
        <button className="btn-primary" onClick={fetchAlerts}>
          🔄 Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🚨</div>
          <div className="stat-info">
            <h3>{criticalCount}</h3>
            <p>Critical</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <h3>{highCount}</h3>
            <p>High Priority</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-info">
            <h3>{mediumCount}</h3>
            <p>Medium</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-info">
            <h3>{alerts.length}</h3>
            <p>Total Alerts</p>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        {alerts.length === 0 ? (
          <div className="empty-state">
            🎉 No alerts! Everything is running smoothly.
          </div>
        ) : (
          <div className="alerts-list">
            {alerts.map((alert, index) => (
              <div key={index} className={`alert-item ${getSeverityClass(alert.severity)}`}>
                <div className="alert-icon">{getIcon(alert.type)}</div>
                <div className="alert-content">
                  <div className="alert-header">
                    <h4>{alert.product_name}</h4>
                    <span className={`badge badge-${alert.severity === 'critical' ? 'critical' : 'low'}`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p>{alert.message}</p>
                  <div className="alert-meta">
                    <span><strong>SKU:</strong> {alert.sku}</span>
                    <span><strong>Stock:</strong> {alert.current_stock}</span>
                    {alert.reorder_level !== undefined && (
                      <span><strong>Reorder Level:</strong> {alert.reorder_level}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
