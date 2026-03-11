import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

function AdminLogin() {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [otp, setOtp] = useState('');
    const [step, setStep] = useState('login'); // 'login' or 'otp'
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/login/`, { email, password });
            if (res.data.otp_required) {
                setStep('otp');
                setMessage(res.data.message || 'OTP sent to email. Check console for development OTP if any.');
                if (res.data.otp) {
                    setMessage(`OTP Sent! Your OTP for dev: ${res.data.otp}`);
                }
            } else {
                saveDataAndGo(res.data);
            }
        } catch (err) {
            setError(err.response?.data?.error || err.response?.data?.message || 'Login failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOtp = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/verify-login-otp/`, { email, otp });
            saveDataAndGo(res.data);
        } catch (err) {
            setError(err.response?.data?.error || 'OTP verification failed.');
        } finally {
            setLoading(false);
        }
    };

    const saveDataAndGo = (data) => {
        if (data.token) localStorage.setItem('authToken', data.token);
        if (data.access) localStorage.setItem('accessToken', data.access);
        if (data.refresh) localStorage.setItem('refreshToken', data.refresh);
        if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/');
    };

    return (
        <div style={{
            minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'linear-gradient(135deg, #f5f3ff, #ede9fe)', fontFamily: "'Inter', sans-serif"
        }}>
            <div style={{
                background: '#fff', padding: '2.5rem', borderRadius: '16px', boxShadow: '0 10px 30px rgba(124,58,237,0.1)',
                width: '100%', maxWidth: '400px'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{
                        width: '48px', height: '48px', margin: '0 auto 1rem', borderRadius: '12px',
                        background: 'linear-gradient(135deg, #7c3aed, #4f46e5)', display: 'flex',
                        alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '1.5rem', fontWeight: 800
                    }}>V</div>
                    <h2 style={{ margin: 0, color: '#1e1b4b' }}>Superadmin Login</h2>
                </div>

                {error && <div style={{ background: '#fee2e2', color: '#991b1b', padding: '10px', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>{error}</div>}
                {message && <div style={{ background: '#d1fae5', color: '#065f46', padding: '10px', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>{message}</div>}

                {step === 'login' ? (
                    <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>Email</label>
                            <input
                                type="email" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={loading}
                                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #d1d5db', boxSizing: 'border-box' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>Password</label>
                            <input
                                type="password" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={loading}
                                style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #d1d5db', boxSizing: 'border-box' }}
                            />
                        </div>
                        <button type="submit" disabled={loading} style={{
                            padding: '12px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                            color: '#fff', fontWeight: 600, cursor: loading ? 'wait' : 'pointer', marginTop: '0.5rem'
                        }}>
                            {loading ? 'Authenticating...' : 'Login'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>Enter OTP</label>
                            <input
                                type="text" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))} required disabled={loading}
                                placeholder="6-digit OTP"
                                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid #d1d5db', boxSizing: 'border-box', textAlign: 'center', fontSize: '1.25rem', letterSpacing: '4px' }}
                            />
                        </div>
                        <button type="submit" disabled={loading || otp.length !== 6} style={{
                            padding: '12px', borderRadius: '8px', border: 'none', background: 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                            color: '#fff', fontWeight: 600, cursor: loading ? 'wait' : 'pointer', marginTop: '0.5rem'
                        }}>
                            {loading ? 'Verifying...' : 'Verify OTP'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
}

export default AdminLogin;
