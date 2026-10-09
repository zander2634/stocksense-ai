import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Sales = () => {
     const { user } = useAuth();
  const [sales, setSales] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    product_id: '',
    quantity: '',
    unit_price: '',
    notes: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [salesRes, productsRes] = await Promise.all([
        api.get('/api/sales/'),
        api.get('/api/products/'),
      ]);
      setSales(salesRes.data);
      setProducts(productsRes.data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        product_id: parseInt(formData.product_id),
        quantity: parseInt(formData.quantity),
        notes: formData.notes || null,
      };
      if (formData.unit_price) {
        data.unit_price = parseFloat(formData.unit_price);
      }

      await api.post('/api/sales/', data);
      setShowModal(false);
      resetForm();
      fetchData();
    } catch (error) {
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

const handleDelete = async (id) => {
  if (!window.confirm('Delete this sale? Stock will be restored.')) return;
  try {
    await api.delete(`/api/sales/${id}`);
    fetchData();
  } catch (error) {
    alert('Error: ' + (error.response?.data?.detail || error.message));
  }
};

const resetForm = () => {
  setFormData({ product_id: '', quantity: '', unit_price: '', notes: '' });
};
  const getProductName = (productId) => {
    const product = products.find((p) => p.id === productId);
    return product ? product.name : 'Unknown';
  };

  const totalRevenue = sales.reduce((sum, s) => sum + s.total_price, 0);

  if (loading) return <div className="loading">Loading sales...</div>;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>💵 Sales</h1>
        <button
          className="btn-primary"
          onClick={() => {
            resetForm();
            setShowModal(true);
          }}
        >
          + Record Sale
        </button>
      </div>

      {/* Summary Card */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-info">
            <h3>{sales.length}</h3>
            <p>Total Transactions</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-info">
            <h3>₱{totalRevenue.toLocaleString()}</h3>
            <p>Total Revenue</p>
          </div>
        </div>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Product</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Total</th>
              <th>Date</th>
              <th>Notes</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sales.length === 0 ? (
              <tr>
                <td colSpan="8" className="empty-state">
                  No sales yet. Click "Record Sale" to get started.
                </td>
              </tr>
            ) : (
              sales.map((sale) => (
                <tr key={sale.id}>
                  <td>#{sale.id}</td>
                  <td><strong>{getProductName(sale.product_id)}</strong></td>
                  <td>{sale.quantity}</td>
                  <td>₱{sale.unit_price.toLocaleString()}</td>
                  <td><strong>₱{sale.total_price.toLocaleString()}</strong></td>
                  <td>{new Date(sale.sale_date).toLocaleString()}</td>
                  <td>{sale.notes || '-'}</td>
                  <td>
                      {user?.role === 'Administrator' && (
                  <button
                      className="btn-sm btn-delete"
                      onClick={() => handleDelete(sale.id)}
                  >
                    Delete
                  </button>
                    )}
                  </td>
                  </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Record New Sale</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Product *</label>
                <select
                  name="product_id"
                  value={formData.product_id}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select product</option>
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} (Stock: {p.stock_quantity})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Quantity *</label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleChange}
                    min="1"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Unit Price (optional)</label>
                  <input
                    type="number"
                    step="0.01"
                    name="unit_price"
                    value={formData.unit_price}
                    onChange={handleChange}
                    placeholder="Default: product price"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Notes</label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows="2"
                  placeholder="Customer name, order reference, etc."
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Record Sale</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sales;