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
        if (errorData.email) {
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

      // Redirect to dashboard after successful login
      navigate('/dashboard');

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
              <h3 className="auth-column-title" style={{ textAlign: 'center', marginBottom: '1rem' }}>
                {showOtpStep ? 'Verify OTP' : 'Login'}
              </h3>

              {!showOtpStep ? (
                // Step 1: Email and Password
                <form className="auth-form" onSubmit={handleLogin}>


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
                    {fieldErrors.email && (
                      <div className="field-error-text" style={{ marginTop: '-0.2rem', marginBottom: '0.5rem' }}>{fieldErrors.email}</div>
                    )}
                    <div className={`auth-input-icon-wrapper ${loginPasswordFocused || loginPassword ? 'focused has-value' : ''}`} style={{ marginBottom: '0.35rem' }}>
                      <i className="fas fa-lock auth-input-icon"></i>
                      <input
                        type={showPassword ? "text" : "password"}
                        className="auth-input-with-icon"
                        placeholder=" "
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        onFocus={() => setLoginPasswordFocused(true)}
                        onBlur={() => setLoginPasswordFocused(false)}
                        required
                        maxLength={64}
                        disabled={loginLoading}
                        style={{ paddingRight: '2.5rem' }}
                      />
                      <label className="auth-floating-label">Password *</label>
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        style={{
                          position: 'absolute',
                          right: '0.75rem',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#6b7280',
                          zIndex: 3,
                          padding: 0,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          height: '1.5rem',
                          width: '1.5rem',
                        }}
                        tabIndex="-1"
                      >
                        <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                      </button>
                    </div>
                    {fieldErrors.password && (
                      <div className="field-error-text" style={{ marginTop: '-0.2rem', marginBottom: '0.5rem' }}>{fieldErrors.password}</div>
                    )}

                  <button
                    type="submit"
                    className="auth-primary-btn"
                    disabled={loginLoading}
                  >
                    {loginLoading ? 'Verifying...' : 'Login'}
                  </button>

                  {loginError && (
                    <div className="auth-error-message" style={{ marginTop: '0.75rem', marginBottom: '0.5rem', textAlign: 'center' }}>{loginError}</div>
                  )}

                  <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      {loginError && (
                        <Link
                          to="/forgot-password"
                          style={{ color: '#7c3aed', textDecoration: 'none', fontWeight: '600', fontSize: '14px' }}
                        >
                          Forgot password?
                        </Link>
                      )}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ color: '#666', fontSize: '14px', margin: 0 }}>
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
                  </div>
                </form>
              ) : (
                // Step 2: OTP Verification
                <form className="auth-form" onSubmit={handleVerifyLoginOtp}>
                  {fieldErrors.otp && (
                    <div className="field-error-text" style={{ textAlign: 'center' }}>{fieldErrors.otp}</div>
                  )}
                  {otpSuccess && (
                    <div className="auth-success-message" style={{ marginBottom: '1rem' }}>{otpSuccess}</div>
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
                      disabled={loginLoading || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#7c3aed',
                        cursor: loginLoading || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired) ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        textDecoration: 'underline',
                        opacity: loginLoading || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired) ? 0.6 : 1
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