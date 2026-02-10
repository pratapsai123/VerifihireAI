import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import OtpCountdown from '../components/OtpCountdown';

// Django API base URL - Update this to match your Django backend
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

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

  // OTP verification state
  const [showOtpStep, setShowOtpStep] = useState(false);
  const [otp, setOtp] = useState('');
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [otpError, setOtpError] = useState('');
  const [otpSuccess, setOtpSuccess] = useState('');
  const [otpFocused, setOtpFocused] = useState(false);
  const [otpExpiresAtMs, setOtpExpiresAtMs] = useState(null);
  const [otpExpired, setOtpExpired] = useState(false);
  const [otpRemainingSeconds, setOtpRemainingSeconds] = useState(null);

  // Handle Login - Step 1: Email and Password
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setOtpError('');
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
        setOtpRemainingSeconds(expiresIn);
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
        setLoginError(error.response.data.message || error.response.data.error || 'Login failed. Please check your credentials.');
      } else if (error.request) {
        // Request made but no response
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
      setOtpError('OTP has expired. Please resend OTP.');
      return;
    }
    if (!otp || otp.length !== 6) {
      setOtpError('Please enter a valid 6-digit OTP.');
      return;
    }

    setVerifyingOtp(true);
    setOtpError('');
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

      // Redirect to dashboard after successful login
      navigate('/dashboard');

    } catch (error) {
      if (error.response) {
        setOtpError(error.response.data.error || 'Invalid OTP. Please try again.');
      } else if (error.request) {
        setOtpError('Unable to connect to server. Please check if Django backend is running.');
      } else {
        setOtpError('An error occurred. Please try again.');
      }
      console.error('OTP verification error:', error);
    } finally {
      setVerifyingOtp(false);
    }
  };

  // Handle resend OTP
  const handleResendOtp = async () => {
    setOtp('');
    setOtpError('');
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
        setOtpRemainingSeconds(expiresIn);

        // If OTP is returned in response (for development), show it
        if (response.data.otp) {
          setOtpSuccess(`New OTP sent! Your OTP is: ${response.data.otp} (for development)`);
        }
      }
    } catch (error) {
      if (error.response) {
        setOtpError(error.response.data.error || 'Failed to resend OTP. Please try again.');
      } else {
        setOtpError('Unable to connect to server. Please try again.');
      }
    } finally {
      setLoginLoading(false);
    }
  };

  return (
    <>
      <main className="auth-page signup-page-enhanced">
        <div className="container auth-container" style={{ position: 'relative', zIndex: 1 }}>
          <div className="auth-card" data-aos="fade-up" style={{
            maxWidth: '480px',
            width: '100%',
            padding: '0.5rem 1.25rem'
          }}>
            <div className="auth-logo-wrapper">
              <div style={{
                maxWidth: '450px',
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
              }}>
                <img
                  src="/auth-logo-v7.png"
                  alt="VerifiHireAI Logo"
                  style={{
                    width: '100%',
                    height: 'auto',
                    objectFit: 'contain',
                    filter: 'brightness(0.85) contrast(1.2) sepia(0.2) saturate(1.3)'
                  }}
                />
              </div>
            </div>

            <div className="auth-content-wrapper">
              <h2 style={{ textAlign: 'center', marginBottom: '0.25rem', fontWeight: '600', color: 'var(--gray-900)' }}>Welcome Back</h2>
              <p style={{ textAlign: 'center', marginBottom: '0.5rem', color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.4' }}>
                Login to manage assessments, view reports, and monitor candidate sessions.
              </p>
              <h3 className="auth-column-title" style={{ textAlign: 'center', marginBottom: '0rem' }}>
                {showOtpStep ? 'Verify OTP' : 'Login'}
              </h3>

              {!showOtpStep ? (
                // Step 1: Email and Password
                <form className="auth-form" onSubmit={handleLogin}>
                  {loginError && (
                    <div className="auth-error-message">{loginError}</div>
                  )}

                  <div className={`auth-input-icon-wrapper ${loginEmailFocused || loginEmail ? 'focused has-value' : ''}`} style={{ marginBottom: '0.35rem' }}>
                    <i className="fas fa-envelope auth-input-icon"></i>
                    <input
                      type="email"
                      className="auth-input-with-icon"
                      placeholder=" "
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
                  <div className={`auth-input-icon-wrapper ${loginPasswordFocused || loginPassword ? 'focused has-value' : ''}`} style={{ marginBottom: '0.35rem' }}>
                    <i className="fas fa-lock auth-input-icon"></i>
                    <input
                      type="password"
                      className="auth-input-with-icon"
                      placeholder=" "
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      onFocus={() => setLoginPasswordFocused(true)}
                      onBlur={() => setLoginPasswordFocused(false)}
                      required
                      maxLength={64}
                      disabled={loginLoading}
                    />
                    <label className="auth-floating-label">Password *</label>
                  </div>
                  <div style={{ textAlign: 'right', marginBottom: '0.5rem' }}>
                    <Link
                      to="/forgot-password"
                      style={{ color: '#7c3aed', textDecoration: 'none', fontWeight: '600', fontSize: '14px' }}
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <button
                    type="submit"
                    className="auth-primary-btn"
                    disabled={loginLoading}
                  >
                    {loginLoading ? 'Verifying...' : 'Login'}
                  </button>

                  <div style={{ marginTop: '0rem', textAlign: 'center' }}>
                    <p style={{ color: '#666', fontSize: '14px' }}>
                      Don't have an account?{' '}
                      <Link
                        to="/signup"
                        style={{
                          color: '#7c3aed',
                          textDecoration: 'none',
                          fontWeight: '600',
                          cursor: 'pointer'
                        }}
                      >
                        Sign up here
                      </Link>
                    </p>
                  </div>
                </form>
              ) : (
                // Step 2: OTP Verification
                <form className="auth-form" onSubmit={handleVerifyLoginOtp}>
                  {otpError && (
                    <div className="auth-error-message">{otpError}</div>
                  )}
                  {otpSuccess && (
                    <div className="auth-success-message">{otpSuccess}</div>
                  )}

                  <div style={{ marginBottom: '1.5rem' }}>
                    <p style={{ color: '#666', fontSize: '14px', textAlign: 'center', marginBottom: '1rem' }}>
                      We've sent a verification code to <strong>{loginEmail}</strong>
                    </p>
                  </div>

                  <div className={`auth-input-icon-wrapper ${otpFocused || otp ? 'focused has-value' : ''}`}>
                    <i className="fas fa-key auth-input-icon"></i>
                    <label className="auth-floating-label">Enter OTP *</label>
                    <input
                      type="text"
                      className="auth-input-with-icon"
                      placeholder="Enter 6-digit OTP"
                      value={otp}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                        setOtp(value);
                        setOtpError('');
                      }}
                      onFocus={() => setOtpFocused(true)}
                      onBlur={() => setOtpFocused(false)}
                      maxLength={6}
                      disabled={verifyingOtp}
                      style={{ textAlign: 'center', fontSize: '20px', letterSpacing: '8px' }}
                    />
                  </div>

                  <OtpCountdown
                    expiresAtMs={otpExpiresAtMs}
                    onExpire={() => setOtpExpired(true)}
                    onRemainingSecondsChange={setOtpRemainingSeconds}
                  />

                  <button
                    type="submit"
                    className="auth-primary-btn"
                    disabled={verifyingOtp || otp.length !== 6 || otpExpired}
                    style={{
                      width: '100%',
                      marginBottom: '1rem'
                    }}
                  >
                    {verifyingOtp ? 'Verifying...' : 'Verify OTP'}
                  </button>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
                    <button
                      type="button"
                      onClick={() => {
                        setShowOtpStep(false);
                        setOtp('');
                        setOtpError('');
                        setOtpSuccess('');
                        setOtpExpiresAtMs(null);
                        setOtpExpired(false);
                      }}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#7c3aed',
                        cursor: 'pointer',
                        fontSize: '14px',
                        textDecoration: 'underline'
                      }}
                    >
                      ← Back to Login
                    </button>
                    <button
                      type="button"
                      onClick={handleResendOtp}
                      disabled={loginLoading || (otpRemainingSeconds !== null && otpRemainingSeconds > 0)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#7c3aed',
                        cursor: loginLoading || (otpRemainingSeconds !== null && otpRemainingSeconds > 0) ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        textDecoration: 'underline',
                        opacity: loginLoading || (otpRemainingSeconds !== null && otpRemainingSeconds > 0) ? 0.6 : 1
                      }}
                    >
                      Resend OTP
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default Login;
