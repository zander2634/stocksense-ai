import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Forecast = () => {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [forecast, setForecast] = useState(null);
  const [reorder, setReorder] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/api/products/');
      setProducts(response.data);
      if (response.data.length > 0) {
        setSelectedProduct(response.data[0].id);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const generateForecast = async () => {
    if (!selectedProduct) return;
    setLoading(true);
    setForecast(null);
    setReorder(null);

    try {
      const [forecastRes, reorderRes] = await Promise.all([
        api.get(`/api/forecast/${selectedProduct}?days=7`),
        api.get(`/api/forecast/${selectedProduct}/reorder`),
      ]);
      setForecast(forecastRes.data);
      setReorder(reorderRes.data);
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const chartData = forecast
    ? {
        labels: forecast.predicted_demand.map((_, i) => `Day ${i + 1}`),
        datasets: [
          {
            label: 'Predicted Demand',
            data: forecast.predicted_demand,
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true,
          },
        ],
      }
    : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: '7-Day Demand Forecast' },
    },
  };

  const getProductName = (id) => {
    const p = products.find((p) => p.id === parseInt(id));
    return p ? p.name : '';
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>🤖 AI Forecasting</h1>
      </div>

      <div className="card">
        <div className="forecast-controls">
          <div className="form-group">
            <label>Select Product</label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
            >
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} (Stock: {p.stock_quantity})
                </option>
              ))}
            </select>
          </div>
          <button className="btn-primary" onClick={generateForecast} disabled={loading}>
            {loading ? 'Generating...' : '🔮 Generate Forecast'}
          </button>
        </div>
      </div>

      {loading && <div className="loading">Running AI model...</div>}

      {forecast && (
        <>
          <div className="stats-grid" style={{ marginTop: '24px' }}>
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <div className="stat-info">
                <h3>{forecast.total_predicted_demand}</h3>
                <p>Total 7-Day Demand</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-info">
                <h3>{forecast.average_daily_demand}</h3>
                <p>Avg Daily Demand</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🎯</div>
              <div className="stat-info">
                <h3 style={{ textTransform: 'uppercase' }}>{forecast.confidence}</h3>
                <p>Confidence</p>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⚙️</div>
              <div className="stat-info">
                <h3 style={{ textTransform: 'uppercase' }}>{forecast.method}</h3>
                <p>Method</p>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '24px' }}>
            <h2 style={{ marginBottom: '16px' }}>
              📊 Forecast for: {getProductName(selectedProduct)}
            </h2>
{chartData && (
  <div className="chart-container">
    <Line data={chartData} options={chartOptions} />
  </div>
)}
          </div>
        </>
      )}

      {reorder && (
        <div className="card" style={{ marginTop: '24px' }}>
          <h2 style={{ marginBottom: '16px' }}>🎯 Smart Reorder Recommendation</h2>
          <div className={`reorder-card reorder-${reorder.urgency}`}>
            <div className="reorder-header">
              <h3>Urgency: {reorder.urgency.toUpperCase()}</h3>
              {reorder.should_reorder ? (
                <span className="badge badge-critical">REORDER NOW</span>
              ) : (
                <span className="badge badge-success">STOCK OK</span>
              )}
            </div>
            <div className="reorder-grid">
              <div>
                <p className="reorder-label">Current Stock</p>
                <p className="reorder-value">{reorder.current_stock}</p>
              </div>
              <div>
                <p className="reorder-label">Reorder Point</p>
                <p className="reorder-value">{reorder.reorder_point}</p>
              </div>
              <div>
                <p className="reorder-label">Safety Stock</p>
                <p className="reorder-value">{reorder.safety_stock}</p>
              </div>
              <div>
                <p className="reorder-label">Lead Time</p>
                <p className="reorder-value">{reorder.lead_time_days} days</p>
              </div>
              <div className="reorder-highlight">
                <p className="reorder-label">Recommended Order</p>
                <p className="reorder-value-big">
                  {reorder.recommended_reorder_quantity} units
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Forecast;