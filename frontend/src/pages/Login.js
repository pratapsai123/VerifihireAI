import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import OtpCountdown from '../components/OtpCountdown';
import { API_BASE_URL } from '../apiConfig';

function Login() {
  const navigate = useNavigate();

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Initialize AOS
    if (window.AOS) {
      window.AOS.init({
        duration: 800,
        once: true,
        offset: 50,
      });
    }
  }, []);

  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [loginEmailFocused, setLoginEmailFocused] = useState(false);
  const [loginPasswordFocused, setLoginPasswordFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  // OTP verification state
  const [showOtpStep, setShowOtpStep] = useState(false);
  const [otp, setOtp] = useState('');
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [otpSuccess, setOtpSuccess] = useState('');
  const [otpFocused, setOtpFocused] = useState(false);
  const [otpExpiresAtMs, setOtpExpiresAtMs] = useState(null);
  const [otpExpired, setOtpExpired] = useState(false);

  // Handle Login - Step 1: Email and Password
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setFieldErrors({});
    setOtpSuccess('');
    setLoginLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/login/`, {
        email: loginEmail,
        password: loginPassword,
      });

      // Check if OTP is required (2-step verification)
      if (response.data.otp_required) {
        setShowOtpStep(true);
        setOtpSuccess(response.data.message || 'OTP sent to your email. Please check your inbox.');
        const expiresIn = Number(response.data?.expires_in) || 120;
        setOtpExpiresAtMs(Date.now() + expiresIn * 1000);
        setOtpExpired(false);
        setOtp('');

        // If OTP is returned in response (for development), show it
        if (response.data.otp) {
          setOtpSuccess(`OTP sent! Your OTP is: ${response.data.otp} (for development)`);
        }
      } else {
        // Old flow - direct login (shouldn't happen with new implementation)
        // Success - save token if provided
        if (response.data.token) {
          localStorage.setItem('authToken', response.data.token);
        }
        if (response.data.access) {
          localStorage.setItem('accessToken', response.data.access);
        }
        if (response.data.refresh) {
          localStorage.setItem('refreshToken', response.data.refresh);
        }

        // Redirect to dashboard after successful login
        navigate('/dashboard');
      }

    } catch (error) {
      // Handle error
      if (error.response) {
        // Server responded with error
        const errorData = error.response.data;
        // 403 = company pending/rejected
        if (error.response.status === 403) {
          setLoginError(errorData.error || 'Your account is not authorized to log in at this time.');
        } else if (error.response.status === 404) {
          setLoginError(errorData.error || 'Your account is not registered with us.');
        } else if (error.response.status === 401) {
          setLoginError(errorData.error || (errorData.email && errorData.email[0]) || 'Invalid email or password.');
        } else if (errorData.email) {
          setFieldErrors(prev => ({ ...prev, email: errorData.email[0] }));
        } else if (errorData.password) {
          setFieldErrors(prev => ({ ...prev, password: errorData.password[0] }));
        } else {
          setLoginError(errorData.message || errorData.error || 'Login failed. Please check your credentials.');
        }
      } else if (error.request) {
        setLoginError('Unable to connect to server. Please check if Django backend is running.');
      } else {
        setLoginError('An error occurred. Please try again.');
      }
      console.error('Login error:', error);
    } finally {
      setLoginLoading(false);
    }
  };

  // Handle OTP Verification - Step 2: Verify OTP
  const handleVerifyLoginOtp = async (e) => {
    if (e) e.preventDefault();
    if (otpExpired || (otpExpiresAtMs && Date.now() >= otpExpiresAtMs)) {
      setFieldErrors(prev => ({ ...prev, otp: 'OTP has expired. Please resend OTP.' }));
      return;
    }
    if (!otp || otp.length !== 6) {
      setFieldErrors(prev => ({ ...prev, otp: 'Please enter a valid 6-digit OTP.' }));
      return;
    }

    setVerifyingOtp(true);
    setFieldErrors(prev => ({ ...prev, otp: '' }));
    setOtpSuccess('');

    try {
      const response = await axios.post(`${API_BASE_URL}/verify-login-otp/`, {
        email: loginEmail,
        otp: otp,
      });

      // Success - save token if provided
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
      }
      if (response.data.access) {
        localStorage.setItem('accessToken', response.data.access);
      }
      if (response.data.refresh) {
        localStorage.setItem('refreshToken', response.data.refresh);
      }

      // Save user data if provided
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      // Redirect based on role
      const userRole = response.data.user?.role;
      if (userRole === 'application_admin') {
        navigate('/superadmin');
      } else {
        navigate('/dashboard');
      }

    } catch (error) {
      if (error.response) {
        setFieldErrors(prev => ({ ...prev, otp: error.response.data.error || 'Invalid OTP. Please try again.' }));
      } else if (error.request) {
        setLoginError('Unable to connect to server.');
      } else {
        setLoginError('An error occurred. Please try again.');
      }
      console.error('OTP verification error:', error);
    } finally {
      setVerifyingOtp(false);
    }
  };

  // Handle resend OTP
  const handleResendOtp = async () => {
    setOtp('');
    setFieldErrors({});
    setOtpSuccess('');
    setLoginLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/login/`, {
        email: loginEmail,
        password: loginPassword,
      });

      if (response.data.otp_required) {
        setOtpSuccess(response.data.message || 'New OTP sent to your email. Please check your inbox.');
        const expiresIn = Number(response.data?.expires_in) || 120;
        setOtpExpiresAtMs(Date.now() + expiresIn * 1000);
        setOtpExpired(false);

        // If OTP is returned in response (for development), show it
        if (response.data.otp) {
          setOtpSuccess(`New OTP sent! Your OTP is: ${response.data.otp} (for development)`);
        }
      }
    } catch (error) {
      if (error.response) {
        setFieldErrors(prev => ({ ...prev, otp: error.response.data.error || 'Failed to resend OTP. Please try again.' }));
      } else {
        setFieldErrors(prev => ({ ...prev, otp: 'Unable to connect to server. Please try again.' }));
      }
    } finally {
      setLoginLoading(false);
    }
  };

  return (
    <div className="auth-split-page">
      {/* Left Side: Illustration and Intro */}
      <div className="auth-left-side">
        <div className="left-branded-header" data-aos="fade-down">
          <div className="brand-logo-group">
            <img src="/auth-logo-v7.png" alt="VerifiHireAI Logo" className="brand-logo-img" />
            <div className="brand-text-container">
              <span className="brand-name-text">VerifiHireAI</span>
              <p className="brand-tagline">Trust in Every Hire</p>
            </div>
          </div>
        </div>

        <div className="left-intro-content" data-aos="fade-right" style={{ marginTop: '0.5rem' }}>
          <h1 className="left-intro-title">Welcome Back</h1>
          <p className="left-intro-subtitle">
            Login to manage assessments, view reports,<br />
            and monitor candidate sessions.
          </p>
          <div className="left-intro-image-wrapper">
            <img
              src="/login-illustration.png"
              alt="Login Illustration"
              className="left-intro-image"
            // style={{ maxWidth: '420px' }}
            />
          </div>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="auth-right-side">
        <div className="form-header-content" data-aos="fade-up">
          <h2 className="form-header-title">{showOtpStep ? 'Verify OTP' : 'Login'}</h2>
          <p className="form-header-subtitle" style={{ marginBottom: '2.5rem' }}>Enter your account details</p>
        </div>

        {!showOtpStep ? (
          <form className="auth-form" onSubmit={handleLogin} data-aos="fade-up" data-aos-delay="100">


            <div className={`auth-input-icon-wrapper ${loginEmailFocused || loginEmail ? 'focused has-value' : ''}`}>
              <i className="fas fa-user auth-input-icon"></i>
              <input
                type="email"
                className="auth-input-with-icon"
                placeholder="Email *"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                onFocus={() => setLoginEmailFocused(true)}
                onBlur={() => setLoginEmailFocused(false)}
                required
                maxLength={100}
                disabled={loginLoading}
              />
              <label className="auth-floating-label">Email *</label>
            </div>
            {fieldErrors.email && (
              <div className="field-error-text">{fieldErrors.email}</div>
            )}

            <div className={`auth-input-icon-wrapper ${loginPasswordFocused || loginPassword ? 'focused has-value' : ''}`}>
              <i className="fas fa-lock auth-input-icon"></i>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPassword ? "text" : "password"}
                  className="auth-input-with-icon"
                  placeholder="Password *"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  maxLength={64}
                  required
                  disabled={loginLoading}
                  onFocus={() => setLoginPasswordFocused(true)}
                  onBlur={() => setLoginPasswordFocused(false)}
                  style={{ paddingRight: '2.5rem' }}
                />
                <label className="auth-floating-label">Password *</label>
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={loginLoading}
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
              <div className="field-error-text">{fieldErrors.password}</div>
            )}



            <button
              type="submit"
              className="auth-primary-btn"
              disabled={loginLoading || !loginEmail || !loginPassword}
              style={{ width: '100%', padding: '0.875rem', fontSize: '1rem', fontWeight: '600' }}
            >
              {loginLoading ? 'Verifying...' : 'Login'}
            </button>

            {loginError && (
              <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center' }}>{loginError}</div>
            )}

            <div style={{ marginTop: '2rem', textAlign: 'center', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              {loginError && (
                <>
                  <Link to="/forgot-password" style={{ color: '#2563eb', fontSize: '0.9rem', fontWeight: '600', textDecoration: 'none' }}>
                    Forgot Password?
                  </Link>
                  <span style={{ color: '#cbd5e1' }}>|</span>
                </>
              )}
              <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
                Don't have an account?{' '}
                <Link to="/signup" style={{
                  color: '#2563eb',
                  fontWeight: '700',
                  marginLeft: '4px',
                  textDecoration: 'none'
                }}>
                  Sign up
                </Link>
              </p>
            </div>
          </form>
        ) : (
          <form className="auth-form" onSubmit={handleVerifyLoginOtp} data-aos="fade-up" data-aos-delay="100">
            {otpSuccess && (
              <div className="auth-success-message" style={{ marginBottom: '1.5rem' }}>{otpSuccess}</div>
            )}

            <p style={{ color: '#4a5568', fontSize: '0.9rem', textAlign: 'center', marginBottom: '1.5rem' }}>
              We've sent a code to <strong>{loginEmail}</strong>
            </p>

            <div className={`auth-input-icon-wrapper ${otpFocused || otp ? 'focused has-value' : ''}`}>
              <i className="fas fa-key auth-input-icon"></i>
              <input
                type="text"
                className="auth-input-with-icon"
                placeholder="6-digit OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                onFocus={() => setOtpFocused(true)}
                onBlur={() => setOtpFocused(false)}
                maxLength={6}
                required
                disabled={verifyingOtp}
                style={{ textAlign: 'center', fontSize: '1.25rem', letterSpacing: '4px' }}
              />
              <label className="auth-floating-label">Enter 6-digit OTP</label>
            </div>
            {fieldErrors.otp && (
              <div className="field-error-text" style={{ textAlign: 'center' }}>{fieldErrors.otp}</div>
            )}

            <OtpCountdown
              expiresAtMs={otpExpiresAtMs}
              onExpire={() => setOtpExpired(true)}
            />

            <button
              type="submit"
              className="auth-primary-btn"
              disabled={verifyingOtp || otp.length !== 6 || otpExpired}
              style={{ width: '100%', padding: '0.875rem', marginTop: '1rem' }}
            >
              {verifyingOtp ? 'Verifying...' : 'Verify OTP'}
            </button>
            {loginError && (
              <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center', marginBottom: 0 }}>{loginError}</div>
            )}

            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
              <button type="button" onClick={() => setShowOtpStep(false)} className="auth-secondary-btn" style={{ fontSize: '0.85rem' }}>
                Back to Login
              </button>
              <button type="button" onClick={handleResendOtp} disabled={loginLoading || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired)} className="auth-secondary-btn" style={{ fontSize: '0.85rem' }}>
                Resend OTP
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default Login;