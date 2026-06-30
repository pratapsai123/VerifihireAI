import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import OtpCountdown from '../components/OtpCountdown';
import { API_BASE_URL } from '../apiConfig';
import { setToken } from '../utils/authStorage';

// Personal/free email domains allowed on the student portal.
// Mirrors the backend _free_email_domains() list for instant frontend validation.
const FREE_EMAIL_DOMAINS = new Set([
  'gmail.com', 'googlemail.com',
  'yahoo.com', 'yahoo.in', 'yahoo.co.in', 'yahoo.co.uk', 'yahoo.ca', 'yahoo.com.au', 'ymail.com', 'rocketmail.com',
  'outlook.com', 'outlook.in', 'outlook.co.uk', 'hotmail.com', 'live.com',
  'icloud.com', 'me.com', 'mac.com',
  'aol.com', 'proton.me', 'protonmail.com',
  'zoho.com', 'mail.com', 'yandex.com', 'msn.com',
  'fastmail.com', 'gmx.com', 'gmx.net',
  'tutanota.com', 'tuta.com',
  'email.com', 'post.com', 'usa.com',
  'hushmail.com', 'runbox.com', 'mailfence.com', 'countermail.com', 'startmail.com',
  'web.de', 'inbox.com', 'rediffmail.com',
  'guerrillamail.com', 'mailinator.com', 'temp-mail.org', '10minutemail.com',
  'att.net', 'comcast.net', 'verizon.net',
  'laposte.net', 'orange.fr', 'free.fr',
  'seznam.cz', 'naver.com', 'daum.net',
  'student.com', 'lycos.com', 'excite.com',
]);

function isPersonalEmail(email) {
  const parts = email.trim().toLowerCase().split('@');
  if (parts.length !== 2 || !parts[1]) return false;
  return FREE_EMAIL_DOMAINS.has(parts[1]);
}

function StudentLogin() {
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      navigate('/dashboard', { replace: true });
      return;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [navigate]);

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  const [showOtpStep, setShowOtpStep] = useState(false);
  const [otp, setOtp] = useState('');
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [otpSuccess, setOtpSuccess] = useState('');
  const [otpExpiresAtMs, setOtpExpiresAtMs] = useState(null);
  const [otpExpired, setOtpExpired] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setFieldErrors({});
    setOtpSuccess('');

    // 1. Validate Email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(loginEmail)) {
      setFieldErrors({ email: 'Please enter a valid email address.' });
      return;
    }

    // 2. Validate Personal/Free Domain Email
    if (!isPersonalEmail(loginEmail)) {
      setFieldErrors({ email: 'Only personal email domains (e.g. Gmail, Yahoo) are allowed here.' });
      setLoginError(
        'This portal is for student practice accounts only. Please use a personal email (e.g. Gmail, Yahoo, Outlook). ' +
        'If you are a recruiter or company user, please use the standard Login page.'
      );
      return;
    }

    // 3. Validate Password presence
    if (!loginPassword) {
      setFieldErrors({ password: 'Password is required.' });
      return;
    }

    setLoginLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/student/login/`, {
        email: loginEmail,
        password: loginPassword,
      });

      if (response.data.otp_required) {
        setShowOtpStep(true);
        setOtpSuccess(response.data.message || 'OTP sent to your email. Please check your inbox.');
        const expiresIn = Number(response.data?.expires_in) || 120;
        setOtpExpiresAtMs(Date.now() + expiresIn * 1000);
        setOtpExpired(false);
        setOtp('');
        if (response.data.otp) {
          setOtpSuccess(`OTP sent! Your OTP is: ${response.data.otp} (for development)`);
        }
      } else {
        if (response.data.token) {
          setToken(response.data.token);
        }
        navigate('/dashboard');
      }
    } catch (error) {
      if (error.response) {
        setLoginError(error.response.data.error || 'Login failed. Please check your credentials.');
      } else {
        setLoginError('Unable to connect to server.');
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    if (otpExpired) {
      setFieldErrors({ otp: 'OTP has expired. Please resend.' });
      return;
    }

    setVerifyingOtp(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/verify-login-otp/`, {
        email: loginEmail,
        otp: otp,
      });

      if (response.data.token) {
        setToken(response.data.token);
      }
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      navigate('/dashboard');
    } catch (error) {
      if (error.response) {
        setFieldErrors({ otp: error.response.data.error || 'Invalid OTP.' });
      } else {
        setLoginError('Unable to connect to server.');
      }
    } finally {
      setVerifyingOtp(false);
    }
  };

  const handleResendOtp = async () => {
    setOtp('');
    setFieldErrors({});
    setOtpSuccess('');
    setLoginLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/student/login/`, {
        email: loginEmail,
        password: loginPassword,
      });

      if (response.data.otp_required) {
        setOtpSuccess(response.data.message || 'New OTP sent to your email.');
        const expiresIn = Number(response.data?.expires_in) || 120;
        setOtpExpiresAtMs(Date.now() + expiresIn * 1000);
        setOtpExpired(false);
        if (response.data.otp) {
          setOtpSuccess(`New OTP sent! Your OTP is: ${response.data.otp} (for development)`);
        }
      }
    } catch (error) {
      setFieldErrors({ otp: 'Failed to resend OTP.' });
    } finally {
      setLoginLoading(false);
    }
  };

  return (
    <div className="auth-split-page">
      {/* Left Side */}
      <div className="auth-left-side">
        <div className="left-branded-header">
          <div className="brand-logo-group">
            <img src="/auth-logo-v7.png" alt="VerifiHireAI Logo" className="brand-logo-img" />
            <div className="brand-text-container">
              <span className="brand-name-text">VerifiHireAI</span>
              <p className="brand-tagline">Prep for Success</p>
            </div>
          </div>
        </div>

        <div className="left-intro-content" style={{ marginTop: '0.5rem' }}>
          <h1 className="left-intro-title">Welcome Back</h1>
          <p className="left-intro-subtitle">
            Log in to continue your mock practice sessions<br />
            and view your results feedback.
          </p>
          <div className="left-intro-image-wrapper">
            <img
              src="/login-illustration.png"
              alt="Login Illustration"
              className="left-intro-image"
            />
          </div>
        </div>
      </div>

      {/* Right Side */}
      <div className="auth-right-side">
        <div className="form-header-content">
          <h2 className="form-header-title">{showOtpStep ? 'Verify OTP' : 'Student Login'}</h2>
          <p className="form-header-subtitle" style={{ marginBottom: '2.5rem' }}>Enter your account details</p>
        </div>

        {!showOtpStep ? (
          <form className="auth-form" onSubmit={handleLogin}>
            <div className="auth-input-icon-wrapper focused has-value">
              <i className="fas fa-user auth-input-icon"></i>
              <input
                type="email"
                className="auth-input-with-icon"
                placeholder="Email *"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                required
                disabled={loginLoading}
              />
              <label className="auth-floating-label">Email *</label>
            </div>
            {fieldErrors.email && (
              <div className="field-error-text" style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.75rem', textAlign: 'left' }}>
                {fieldErrors.email}
              </div>
            )}

            <div className="auth-input-icon-wrapper focused has-value">
              <i className="fas fa-lock auth-input-icon"></i>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? "text" : "password"}
                  className="auth-input-with-icon"
                  placeholder="Password *"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  disabled={loginLoading}
                  style={{ paddingRight: '2.5rem' }}
                />
                <label className="auth-floating-label">Password *</label>
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="password-toggle-btn"
                  style={{
                    position: 'absolute',
                    right: '0.75rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#94a3b8'
                  }}
                >
                  <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                </button>
              </div>
            </div>
            {fieldErrors.password && (
              <div className="field-error-text" style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.75rem', textAlign: 'left' }}>
                {fieldErrors.password}
              </div>
            )}

            <button
              type="submit"
              className="auth-primary-btn"
              disabled={loginLoading || !loginEmail || !loginPassword}
              style={{ width: '100%', padding: '0.875rem', fontSize: '1rem', fontWeight: '600' }}
            >
              {loginLoading ? 'Verifying...' : 'Login'}
            </button>

            {loginError && <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center' }}>{loginError}</div>}

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
                Don't have an account?{' '}
                <Link to="/student/register" style={{ color: '#2563eb', fontWeight: '700', textDecoration: 'none' }}>
                  Sign up
                </Link>
              </p>
            </div>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleVerifyOtp}>
            {otpSuccess && <div className="auth-success-message" style={{ marginBottom: '1.5rem' }}>{otpSuccess}</div>}

            <p style={{ color: '#4a5568', fontSize: '0.9rem', textAlign: 'center', marginBottom: '1.5rem' }}>
              Code sent to <strong>{loginEmail}</strong>
            </p>

            <div className="auth-input-icon-wrapper focused has-value">
              <i className="fas fa-key auth-input-icon"></i>
              <input
                type="text"
                className="auth-input-with-icon"
                placeholder="6-digit OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength={6}
                required
                disabled={verifyingOtp}
                style={{ textAlign: 'center', fontSize: '1.25rem', letterSpacing: '4px' }}
              />
              <label className="auth-floating-label">Enter 6-digit OTP</label>
            </div>
            {fieldErrors.otp && <div className="field-error-text" style={{ textAlign: 'center' }}>{fieldErrors.otp}</div>}

            {!otpExpired && (
              <OtpCountdown
                expiresAtMs={otpExpiresAtMs}
                onExpire={() => setOtpExpired(true)}
              />
            )}

            <button
              type="submit"
              className="auth-primary-btn"
              disabled={verifyingOtp || otp.length !== 6 || otpExpired}
              style={{ width: '100%', padding: '0.875rem', marginTop: '1rem' }}
            >
              {verifyingOtp ? 'Verifying...' : 'Verify OTP'}
            </button>

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
              <button type="button" onClick={() => setShowOtpStep(false)} className="auth-secondary-btn" style={{ fontSize: '0.85rem' }}>
                Back to Login
              </button>
              <button type="button" onClick={handleResendOtp} disabled={loginLoading} className="auth-secondary-btn" style={{ fontSize: '0.85rem' }}>
                Resend OTP
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default StudentLogin;
