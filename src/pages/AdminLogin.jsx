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
    const [timer, setTimer] = useState(120);
    const [canResend, setCanResend] = useState(false);
    const [isExpired, setIsExpired] = useState(false);
    const [resending, setResending] = useState(false);

    const handleLogin = async (e) => {
        if (e) e.preventDefault();
        setError('');
        setMessage('');
        setIsExpired(false);
        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/login/`, { email, password });
            if (res.data.otp_required) {
                setStep('otp');
                const expiry = res.data.expires_in || 120;
                setTimer(expiry);
                setCanResend(false);
                setIsExpired(false);
                setMessage(res.data.message || 'OTP sent to email.');
                if (res.data.otp) {
                    setMessage(`OTP Sent! Your OTP for dev: ${res.data.otp}`);
                }
            } else {
                saveDataAndGo(res.data);
            }
        } catch (err) {
            const backendError = err.response?.data?.error || err.response?.data?.message || err.response?.data?.email?.[0] || 'Login failed.';
            setError(backendError);
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        let interval;
        if (step === 'otp') {
            interval = setInterval(() => {
                setTimer((prev) => {
                    if (prev <= 1) {
                        setIsExpired(true);
                        setCanResend(true);
                        setMessage(''); // Clear success message when OTP expires
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [step]);

    const handleResendOtp = async () => {
        setIsExpired(false);
        setCanResend(false);
        setError('');
        setMessage('');
        setResending(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/send-otp/`, { email, context: 'login' });
            const expiry = res.data.expires_in || 120;
            setMessage(res.data.message || 'New OTP sent!');
            if (res.data.otp) {
                setMessage(`New OTP Sent! Your OTP for dev: ${res.data.otp}`);
            }
            setTimer(expiry);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to resend OTP.');
            setCanResend(true);
        } finally {
            setResending(false);
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
                {isExpired && !error && <div style={{ background: '#fee2e2', color: '#991b1b', padding: '10px', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem' }}>OTP has expired. Please resend or login again.</div>}

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
                        <button type="submit" disabled={loading || otp.length !== 6 || isExpired} style={{
                            padding: '12px', borderRadius: '8px', border: 'none',
                            background: (loading || otp.length !== 6 || isExpired) ? '#9ca3af' : 'linear-gradient(135deg, #7c3aed, #4f46e5)',
                            color: '#fff', fontWeight: 600,
                            cursor: (loading || otp.length !== 6 || isExpired) ? 'not-allowed' : 'pointer',
                            marginTop: '0.5rem',
                            transition: 'all 0.3s ease'
                        }}>
                            {loading ? 'Verifying...' : 'Verify OTP'}
                        </button>

                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginTop: '1.5rem',
                            borderTop: '1px solid #f3f4f6',
                            paddingTop: '1rem'
                        }}>
                            <button
                                type="button"
                                onClick={handleResendOtp}
                                disabled={!canResend || resending}
                                style={{
                                    background: 'none', border: 'none',
                                    color: (!canResend || resending) ? '#9ca3af' : '#7c3aed',
                                    fontWeight: 700,
                                    cursor: (!canResend || resending) ? 'not-allowed' : 'pointer',
                                    fontSize: '0.85rem',
                                    textDecoration: canResend ? 'underline' : 'none',
                                    transition: 'color 0.2s',
                                    padding: 0
                                }}
                            >
                                {resending ? 'Sending...' : 'Resend OTP'}
                            </button>

                            <div style={{
                                fontSize: '0.85rem',
                                color: isExpired ? '#ef4444' : '#6b7280',
                                fontWeight: 600,
                                background: '#f9fafb',
                                padding: '4px 10px',
                                borderRadius: '6px',
                                minWidth: '45px',
                                textAlign: 'center'
                            }}>
                                {timer}s
                            </div>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}

export default AdminLogin;
