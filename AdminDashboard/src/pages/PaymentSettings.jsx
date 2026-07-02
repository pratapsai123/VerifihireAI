import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import './PaymentSettings.css';

const PaymentSettings = () => {
  const [settings, setSettings] = useState({
    mode: 'test',
    test_key_id: '',
    test_key_secret: '',
    live_key_id: '',
    live_key_secret: '',
    account_holder_name: '',
    bank_name: '',
    account_number: '',
    ifsc_code: '',
    total_collected: 0
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE_URL}/admin/payment-settings/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSettings(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching payment settings:', error);
      setMessage({ text: 'Failed to load payment settings', type: 'error' });
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ text: '', type: '' });
    
    try {
      const token = localStorage.getItem('token');
      // For secrets, don't send if they haven't changed (still show '••••••••••••')
      const payload = { ...settings };
      if (payload.test_key_secret.includes('•')) delete payload.test_key_secret;
      if (payload.live_key_secret.includes('•')) delete payload.live_key_secret;

      await axios.post(`${API_BASE_URL}/admin/payment-settings/`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setMessage({ text: 'Payment settings saved successfully!', type: 'success' });
      // Reload to get masked secrets
      fetchSettings();
    } catch (error) {
      console.error('Error saving payment settings:', error);
      setMessage({ text: 'Failed to save payment settings', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="pm-loading">Loading payment settings...</div>;

  return (
    <div className="pm-container">
      <div className="pm-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 className="pm-title">Payment Gateway Settings</h1>
          <p className="pm-subtitle">Configure Razorpay keys and bank account details.</p>
        </div>
        
        {/* Total Revenue Widget */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '140px',
          height: '140px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--blue-accent) 0%, #7C3AED 100%)',
          color: 'white',
          boxShadow: '0 8px 20px rgba(79, 70, 229, 0.3)',
          border: '4px solid #f0f3f8'
        }}>
          <span style={{ fontSize: '0.8rem', fontWeight: '600', opacity: 0.9, textTransform: 'uppercase', letterSpacing: '1px' }}>Total Revenue</span>
          <span style={{ fontSize: '1.6rem', fontWeight: '800', marginTop: '4px' }}>₹{settings.total_collected?.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>

      {message.text && (
        <div className={`pm-message ${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="pm-form" style={{ maxWidth: '800px', background: '#fff', padding: '30px', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}>
        
        <div style={{ marginBottom: '30px', padding: '20px', backgroundColor: settings.mode === 'live' ? '#ecfdf5' : '#fff7ed', border: `1px solid ${settings.mode === 'live' ? '#10b981' : '#f97316'}`, borderRadius: '8px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            Operating Mode
            <span style={{ fontSize: '12px', padding: '4px 8px', borderRadius: '20px', background: settings.mode === 'live' ? '#10b981' : '#f97316', color: '#fff' }}>
              {settings.mode.toUpperCase()}
            </span>
          </h3>
          <div className="pm-form-group">
            <label>Mode</label>
            <select name="mode" value={settings.mode} onChange={handleChange} className="pm-input">
              <option value="test">Test Mode (Simulation)</option>
              <option value="live">Live Mode (Real Payments)</option>
            </select>
            <p style={{ fontSize: '12px', color: '#64748b', marginTop: '5px' }}>
              In Test mode, no real money is deducted. Switch to Live when ready for production.
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '30px' }}>
          <div>
            <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>Test Credentials</h3>
            <div className="pm-form-group" style={{ marginTop: '15px' }}>
              <label>Test Key ID</label>
              <input type="text" name="test_key_id" value={settings.test_key_id} onChange={handleChange} className="pm-input" placeholder="rzp_test_..." />
            </div>
            <div className="pm-form-group">
              <label>Test Key Secret</label>
              <input type="text" name="test_key_secret" value={settings.test_key_secret} onChange={handleChange} className="pm-input" placeholder="Enter secret to update" />
            </div>
          </div>

          <div>
            <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>Live Credentials</h3>
            <div className="pm-form-group" style={{ marginTop: '15px' }}>
              <label>Live Key ID</label>
              <input type="text" name="live_key_id" value={settings.live_key_id} onChange={handleChange} className="pm-input" placeholder="rzp_live_..." />
            </div>
            <div className="pm-form-group">
              <label>Live Key Secret</label>
              <input type="text" name="live_key_secret" value={settings.live_key_secret} onChange={handleChange} className="pm-input" placeholder="Enter secret to update" />
            </div>
          </div>
        </div>

        <h3 style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '10px', marginTop: '40px' }}>Settlement Bank Account (For Reference)</h3>
        <p style={{ fontSize: '13px', color: '#64748b', marginBottom: '20px' }}>These details must match the bank account linked in your Razorpay dashboard.</p>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div className="pm-form-group">
            <label>Account Holder Name</label>
            <input type="text" name="account_holder_name" value={settings.account_holder_name} onChange={handleChange} className="pm-input" />
          </div>
          <div className="pm-form-group">
            <label>Bank Name</label>
            <input type="text" name="bank_name" value={settings.bank_name} onChange={handleChange} className="pm-input" />
          </div>
          <div className="pm-form-group">
            <label>Account Number</label>
            <input type="text" name="account_number" value={settings.account_number} onChange={handleChange} className="pm-input" />
          </div>
          <div className="pm-form-group">
            <label>IFSC Code</label>
            <input type="text" name="ifsc_code" value={settings.ifsc_code} onChange={handleChange} className="pm-input" />
          </div>
        </div>

        <div style={{ marginTop: '30px', display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" className="pm-btn pm-btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Payment Settings'}
          </button>
        </div>

      </form>
    </div>
  );
};

export default PaymentSettings;
