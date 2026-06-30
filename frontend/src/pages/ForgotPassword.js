import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import OtpCountdown from '../components/OtpCountdown';
import { API_BASE_URL } from '../apiConfig';

function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [step, setStep] = useState('email'); // email -> otp -> reset
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [emailFocused, setEmailFocused] = useState(false);
  const [otpFocused, setOtpFocused] = useState(false);
  const [newPasswordFocused, setNewPasswordFocused] = useState(false);
  const [confirmPasswordFocused, setConfirmPasswordFocused] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [otpExpiresAtMs, setOtpExpiresAtMs] = useState(null);
  const [otpExpired, setOtpExpired] = useState(false);

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$/;
  const passwordRequirements = [
    { id: 'length', label: '6-12 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
    { id: 'uppercase', label: 'At least one uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
    { id: 'lowercase', label: 'At least one lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
    { id: 'number', label: 'At least one number', test: (pwd) => /\d/.test(pwd) },
    { id: 'special', label: 'At least one special character', test: (pwd) => /[^A-Za-z0-9]/.test(pwd) },
  ];

  const passwordRequirementStatuses = passwordRequirements.map(req => ({
    ...req,
    met: req.test(newPassword),
  }));
  const unmetPasswordRequirements = passwordRequirementStatuses.filter(req => !req.met);
  const showPasswordHelper = (newPasswordFocused || newPassword.length > 0);

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

  const handleSendOtp = async () => {
    if (!email) {
      setError('Please enter your email.');
      return;
    }
    setError('');
    setSuccess('');
    setFieldErrors({});

    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/send-otp/`, {
        email,
        context: 'forgot_password'
      });
      setSuccess(res.data.message || 'OTP sent to your email.');
      if (res.data.otp) {
        setSuccess(`OTP sent! Your OTP is: ${res.data.otp} (for development)`);
      }
      const expiresIn = Number(res.data?.expires_in) || 120;
      setOtpExpiresAtMs(Date.now() + expiresIn * 1000);
      setOtpExpired(false);
      setOtp('');
      setStep('otp');
    } catch (err) {
      if (err.response) {
        setFieldErrors(prev => ({ ...prev, email: err.response.data.error || err.response.data.email?.[0] || 'Failed to send OTP.' }));
      } else {
        setError('Unable to connect to server. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    if (otpExpired || (otpExpiresAtMs && Date.now() >= otpExpiresAtMs)) {
      setFieldErrors(prev => ({ ...prev, otp: 'OTP has expired. Please resend OTP.' }));
      return;
    }
    if (!otp || otp.length !== 6) {
      setFieldErrors(prev => ({ ...prev, otp: 'Enter a valid 6-digit OTP.' }));
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await axios.post(`${API_BASE_URL}/verify-otp/`, { email, otp });
      setSuccess(res.data.message || 'OTP verified. Set your new password.');
      setOtpExpiresAtMs(null);
      setOtpExpired(false);
      setStep('reset');
    } catch (err) {
      if (err.response) {
        setFieldErrors(prev => ({ ...prev, otp: err.response.data.error || 'Invalid OTP. Please try again.' }));
      } else {
        setError('Unable to connect to server. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async () => {
    setError('');
    setFieldErrors({});
    setSuccess('');

    if (!passwordRegex.test(newPassword)) {
      setFieldErrors(prev => ({ ...prev, newPassword: 'Password must be 6-12 characters and include uppercase, lowercase, number, and special character.' }));
      return;
    }

    if (newPassword !== confirmPassword) {
      setFieldErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match.' }));
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/reset-password/`, {
        email,
        otp,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setSuccess(res.data.message || 'Password reset successful. Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      if (err.response) {
        setError(err.response.data.error || 'Failed to reset password.');
      } else {
        setError('Unable to connect to server.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (step === 'email') {
      handleSendOtp();
    } else if (step === 'otp') {
      handleVerifyOtp();
    } else if (step === 'reset') {
      handleResetPassword();
    }
  };

  return (
    <div className="auth-split-page">
      {/* Left Side: Branding and Reset Intro */}
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
          <h1 className="left-intro-title">Reset Your Password</h1>
          <p className="left-intro-subtitle">
            Secure your account with OTP verification.<br />
            Follow the steps to regain access.
          </p>
          <div className="left-intro-image-wrapper">
            <img
              src="/reset-password-illustration.png"
              alt="Security Illustration"
              className="left-intro-image"
            //  #   style={{ maxWidth: '420px' }}
            />
          </div>
        </div>
      </div>

      {/* Right Side: Stepper and Form */}
      <div className="auth-right-side">
        <div className="forgot-password-card" data-aos="fade-up">
          <h2 style={{ textAlign: 'center', marginBottom: '1rem', fontSize: '1.5rem', fontWeight: '700', color: '#1e293b' }}>Forgot Password</h2>

          {/* Stepper */}
          <div className="auth-stepper">
            <div className={`step-item ${step === 'email' ? 'active' : ''}`}>Step 1</div>
            <div className="step-separator">→</div>
            <div className={`step-item ${step === 'otp' ? 'active' : ''}`}>Step 2</div>
            <div className="step-separator">→</div>
            <div className={`step-item ${step === 'reset' ? 'active' : ''}`}>Done</div>
          </div>

          <p style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#64748b', fontSize: '0.9rem' }}>
            {step === 'email'
              ? 'Enter your email address to receive an OTP'
              : step === 'otp'
                ? `Enter the 6-digit OTP sent to your email`
                : 'Set a strong new password for your account'}
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>

            {success && <div className="auth-success-message" style={{ marginBottom: '1.5rem' }}>{success}</div>}

            {step === 'email' && (
              <>
                <div className={`auth-input-icon-wrapper ${emailFocused || email ? 'focused has-value' : ''}`}>
                  <i className="fas fa-envelope auth-input-icon"></i>
                  <input
                    type="email"
                    className="auth-input-with-icon"
                    placeholder="Email Address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onFocus={() => setEmailFocused(true)}
                    onBlur={() => setEmailFocused(false)}
                    required
                    disabled={loading}
                  />
                  <label className="auth-floating-label">Email Address</label>
                </div>
                {fieldErrors.email && (
                  <div className="field-error-text">{fieldErrors.email}</div>
                )}
                <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1.5rem', textAlign: 'left' }}>
                  We will send a 6-digit OTP to your email
                </p>
                <button type="submit" className="auth-primary-btn" disabled={loading || !email} style={{ width: '100%', padding: '0.875rem' }}>
                  {loading ? 'Sending...' : 'Send OTP'}
                </button>
                {error && <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center', marginBottom: 0 }}>{error}</div>}
              </>
            )}

            {step === 'otp' && (
              <>
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
                    disabled={loading}
                    style={{ textAlign: 'center', fontSize: '1.25rem', letterSpacing: '4px' }}
                  />
                  <label className="auth-floating-label">Enter OTP</label>
                </div>
                {fieldErrors.otp && (
                  <div className="field-error-text" style={{ textAlign: 'center' }}>{fieldErrors.otp}</div>
                )}
                <OtpCountdown expiresAtMs={otpExpiresAtMs} onExpire={() => setOtpExpired(true)} />

                <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                  <button type="submit" className="auth-primary-btn" disabled={loading || otp.length !== 6 || otpExpired} style={{ flex: 2, padding: '0.875rem' }}>
                    {loading ? 'Verifying...' : 'Verify OTP'}
                  </button>
                  <button type="button" onClick={handleSendOtp} disabled={loading || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired)} className="auth-secondary-btn" style={{ flex: 1, fontSize: '0.8rem' }}>
                    Resend
                  </button>
                </div>
                {error && <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center', marginBottom: 0 }}>{error}</div>}
              </>
            )}

            {step === 'reset' && (
              <>
                <div className={`auth-input-icon-wrapper ${newPasswordFocused || newPassword ? 'focused has-value' : ''}`}>
                  <i className="fas fa-lock auth-input-icon"></i>
                  <input
                    type={showNewPassword ? "text" : "password"}
                    className="auth-input-with-icon"
                    placeholder="New Password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    onFocus={() => setNewPasswordFocused(true)}
                    onBlur={() => setNewPasswordFocused(false)}
                    required
                    disabled={loading}
                    style={{ paddingRight: '2.5rem' }}
                  />
                  <label className="auth-floating-label">New Password</label>
                  <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="password-toggle-btn" style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}>
                    <i className={showNewPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                  </button>
                </div>
                {fieldErrors.newPassword && <div className="field-error-text">{fieldErrors.newPassword}</div>}

                {showPasswordHelper && unmetPasswordRequirements.length > 0 && (
                  <div className="password-requirements-box" style={{
                    marginBottom: '1rem',
                    border: '1px solid #f1f5f9',
                    borderRadius: '12px',
                    padding: '0.875rem',
                    backgroundColor: '#f8fafc'
                  }}>
                    <div style={{ color: '#64748b', fontWeight: 600, fontSize: '0.8rem', marginBottom: '0.5rem' }}>
                      Password must include:
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.35rem' }}>
                      {unmetPasswordRequirements.map((req) => (
                        <div key={req.id} style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.4rem',
                          color: '#94a3b8',
                          fontSize: '0.7rem',
                        }}>
                          <i className="fas fa-circle" style={{ fontSize: '0.5rem' }}></i>
                          <span>{req.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className={`auth-input-icon-wrapper ${confirmPasswordFocused || confirmPassword ? 'focused has-value' : ''}`}>
                  <i className="fas fa-lock auth-input-icon"></i>
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    className="auth-input-with-icon"
                    placeholder="Confirm Password"
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      if (fieldErrors.confirmPassword) {
                        setFieldErrors(prev => {
                          const newState = { ...prev };
                          delete newState.confirmPassword;
                          return newState;
                        });
                      }
                    }}
                    onPaste={(e) => {
                      e.preventDefault();
                      setFieldErrors(prev => ({
                        ...prev,
                        confirmPassword: 'Copy and paste is not allowed. Please re-enter your password manually.'
                      }));
                    }}
                    onCopy={(e) => e.preventDefault()}
                    onCut={(e) => e.preventDefault()}
                    onFocus={() => setConfirmPasswordFocused(true)}
                    onBlur={() => setConfirmPasswordFocused(false)}
                    required
                    disabled={loading}
                    style={{ paddingRight: '2.5rem' }}
                  />
                  <label className="auth-floating-label">Confirm Password</label>
                  <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="password-toggle-btn" style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}>
                    <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                  </button>
                </div>
                {(fieldErrors.confirmPassword || (confirmPassword && newPassword !== confirmPassword)) && (
                  <div className="field-error-text" style={{ color: '#e53e3e', fontSize: '0.8rem', marginTop: '-0.75rem', marginBottom: '1rem' }}>
                    {fieldErrors.confirmPassword || 'Passwords do not match'}
                  </div>
                )}

                <button type="submit" className="auth-primary-btn" disabled={loading || !newPassword || newPassword !== confirmPassword} style={{ width: '100%', padding: '0.875rem', marginTop: '1rem' }}>
                  {loading ? 'Resetting...' : 'Reset Password'}
                </button>
                {error && <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center', marginBottom: 0 }}>{error}</div>}
              </>
            )}

            <div style={{ marginTop: '2.5rem', textAlign: 'center' }}>
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
                Remembered your password?{' '}
                <Link to="/login" style={{ color: '#7c3aed', fontWeight: '600' }}>
                  Login here
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
