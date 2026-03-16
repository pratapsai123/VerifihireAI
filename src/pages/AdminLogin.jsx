import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import './AdminLogin.css';

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
                        setMessage(''); 
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

    const [snowflakes, setSnowflakes] = useState([]);
    const [techDust, setTechDust] = useState([]);

    React.useEffect(() => {
        const snowCount = 30;
        const newSnow = [];
        for (let i = 0; i < snowCount; i++) {
            newSnow.push({
                id: `snow-${i}`,
                left: Math.random() * 100 + '%',
                size: Math.random() * 4 + 2 + 'px',
                duration: Math.random() * 5 + 5 + 's',
                delay: Math.random() * 5 + 's'
            });
        }
        setSnowflakes(newSnow);

        const dustCount = 15;
        const newDust = [];
        const hex = '0123456789ABCDEF';
        for (let i = 0; i < dustCount; i++) {
            newDust.push({
                id: `dust-${i}`,
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                text: hex[Math.floor(Math.random() * 16)] + hex[Math.floor(Math.random() * 16)],
                duration: Math.random() * 10 + 10 + 's',
                delay: Math.random() * 10 + 's'
            });
        }
        setTechDust(newDust);
    }, []);

    return (
        <div className="admin-login-wrapper">
            {/* Cyberpunk Grid */}
            <div className="grid-overlay"></div>

            {/* Background Smoke Particles */}
            <div className="smoke-container">
                <div className="smoke-particle" style={{ width: '400px', height: '400px', top: '10%', left: '5%', animationDelay: '0s' }}></div>
                <div className="smoke-particle" style={{ width: '500px', height: '500px', top: '50%', left: '60%', animationDelay: '-5s' }}></div>
                <div className="smoke-particle" style={{ width: '300px', height: '300px', top: '70%', left: '10%', animationDelay: '-10s' }}></div>
            </div>

            {/* Background Snow Particles */}
            <div className="snow-container">
                {snowflakes.map(snow => (
                    <div 
                        key={snow.id} 
                        className="snowflake" 
                        style={{ 
                            left: snow.left, 
                            width: snow.size, 
                            height: snow.size, 
                            animationDuration: snow.duration, 
                            animationDelay: snow.delay 
                        }}
                    ></div>
                ))}
            </div>

            {/* Tech Dust / Binary Drift */}
            {techDust.map(dust => (
                <div 
                    key={dust.id}
                    className="tech-dust"
                    style={{
                        left: dust.left,
                        top: dust.top,
                        animationDuration: dust.duration,
                        animationDelay: dust.delay
                    }}
                >
                    {dust.text}
                </div>
            ))}

            <div className="login-card">
                <div className="login-header">
                    <div className="logo-icon">V</div>
                    <h2>Superadmin Login</h2>
                </div>

                {error && <div className="error-msg">{error}</div>}
                {message && <div className="success-msg">{message}</div>}
                {isExpired && !error && <div className="error-msg">OTP has expired. Please resend or login again.</div>}

                {step === 'login' ? (
                    <form onSubmit={handleLogin}>
                        <div className="form-group">
                            <label>Email</label>
                            <input
                                type="email" value={email} onChange={(e) => setEmail(e.target.value)} required disabled={loading}
                                placeholder="name@company.com"
                            />
                        </div>
                        <div className="form-group">
                            <label>Password</label>
                            <input
                                type="password" value={password} onChange={(e) => setPassword(e.target.value)} required disabled={loading}
                                placeholder="••••••••"
                            />
                        </div>
                        <button type="submit" className="submit-btn" disabled={loading}>
                            {loading ? 'Authenticating...' : 'Sign In'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOtp}>
                        <div className="form-group">
                            <label>Enter Security Code</label>
                            <input
                                type="text" className="otp-input" value={otp} 
                                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))} 
                                required disabled={loading}
                                placeholder="000000"
                            />
                        </div>
                        <button type="submit" className="submit-btn" disabled={loading || otp.length !== 6 || isExpired}>
                            {loading ? 'Verifying...' : 'Complete Login'}
                        </button>

                        <div className="otp-footer">
                            <button
                                type="button"
                                className="resend-btn"
                                onClick={handleResendOtp}
                                disabled={!canResend || resending}
                                style={{
                                    color: (!canResend || resending) ? 'rgba(255,255,255,0.2)' : '#7c3aed',
                                    cursor: (!canResend || resending) ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {resending ? 'Sending...' : 'Resend Code'}
                            </button>

                            <div className="timer-pill">
                                {String(Math.floor(timer / 60)).padStart(2, '0')}:{String(timer % 60).padStart(2, '0')}
                            </div>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}

export default AdminLogin;
