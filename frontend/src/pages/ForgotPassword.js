import React, { useState } from 'react';
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

  const handleSendOtp = async () => {
    if (!email) {
      setError('Please enter your email.');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
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

    // Password strength validation
    if (!passwordRegex.test(newPassword)) {
      setFieldErrors(prev => ({ ...prev, newPassword: 'Password must be 6-12 characters and include uppercase, lowercase, number, and special character.' }));
      return;
    }

    if (!newPassword || !confirmPassword) {
      setError('Please fill both password fields.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setFieldErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match.' }));
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
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
        const errorData = err.response.data;
        if (errorData.new_password) {
          setFieldErrors(prev => ({ ...prev, newPassword: errorData.new_password[0] }));
        } else if (errorData.confirm_password) {
          setFieldErrors(prev => ({ ...prev, confirmPassword: errorData.confirm_password[0] }));
        } else {
          setError(errorData.error || errorData.message || 'Failed to reset password.');
        }
      } else {
        setError('Unable to connect to server. Please try again.');
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

  const passwordRequirementStatuses = passwordRequirements.map(req => ({
    ...req,
    met: req.test(newPassword),
  }));
  const unmetPasswordRequirements = passwordRequirementStatuses.filter(req => !req.met);
  const showPasswordHelper = (newPasswordFocused || newPassword.length > 0);

  const renderEmailStep = () => (
    <>
      <div className={`auth-input-icon-wrapper ${emailFocused || email ? 'focused has-value' : ''}`}>
        <i className="fas fa-envelope auth-input-icon"></i>
        <label className="auth-floating-label">Email *</label>
        <input
          type="email"
          className="auth-input-with-icon"
          placeholder="Email *"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onFocus={() => setEmailFocused(true)}
          onBlur={() => setEmailFocused(false)}
          required
          maxLength={100}
          disabled={loading}
        />
      </div>
      {fieldErrors.email && (
        <div className="field-error-text" style={{ marginTop: '-0.2rem', marginBottom: '1rem' }}>{fieldErrors.email}</div>
      )}
      <button
        type="submit"
        className="auth-primary-btn"
        disabled={loading || !email}
      >
        {loading ? 'Sending OTP...' : 'Send OTP'}
      </button>
    </>
  );

  const renderOtpStep = () => (
    <>
      <div className={`auth-input-icon-wrapper ${otpFocused || otp ? 'focused has-value' : ''}`}>
        <i className="fas fa-key auth-input-icon"></i>
        <label className="auth-floating-label">Enter OTP *</label>
        <input
          type="text"
          className="auth-input-with-icon"
          placeholder="Enter OTP *"
          value={otp}
          maxLength={6}
          onChange={(e) => {
            const val = e.target.value.replace(/\D/g, '').slice(0, 6);
            setOtp(val);
            if (val.length === 6 && !loading && !otpExpired) {
              // Auto-verify when 6 digits are reached
              setTimeout(() => handleVerifyOtp(), 100);
            }
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              if (otp.length === 6 && !loading && !otpExpired) {
                handleVerifyOtp();
              }
            }
          }}
          onFocus={() => setOtpFocused(true)}
          onBlur={() => setOtpFocused(false)}
          required
          disabled={loading}
          style={{ letterSpacing: '6px', textAlign: 'center' }}
        />
      </div>
      {fieldErrors.otp && (
        <div className="field-error-text" style={{ textAlign: 'center', marginBottom: '1rem' }}>{fieldErrors.otp}</div>
      )}
      <OtpCountdown
        expiresAtMs={otpExpiresAtMs}
        onExpire={() => setOtpExpired(true)}
      />
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button
          type="submit"
          className="auth-primary-btn"
          disabled={loading || otp.length !== 6 || otpExpired}
          style={{ flex: 1 }}
        >
          {loading ? 'Verifying...' : 'Verify OTP'}
        </button>
        <button
          type="button"
          className="auth-secondary-btn"
          onClick={handleSendOtp}
          disabled={loading || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired)}
          style={{ flex: 1 }}
        >
          Resend OTP
        </button>
      </div>
    </>
  );

  const renderResetStep = () => (
    <>
      <div className={`auth-input-icon-wrapper ${newPasswordFocused || newPassword ? 'focused has-value' : ''}`}>
        <i className="fas fa-lock auth-input-icon"></i>
        <label className="auth-floating-label">New Password *</label>
        <div style={{ position: 'relative' }}>
          <input
            type={showNewPassword ? "text" : "password"}
            className="auth-input-with-icon"
            placeholder="New Password *"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength={6}
            maxLength={12}
            onFocus={() => setNewPasswordFocused(true)}
            onBlur={() => setNewPasswordFocused(false)}
            required
            disabled={loading}
            style={{ paddingRight: '45px' }}
          />
          <button
            type="button"
            onClick={() => setShowNewPassword(!showNewPassword)}
            disabled={loading}
            style={{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              color: '#666',
              fontSize: '18px',
              padding: '5px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: loading ? 0.5 : 1
            }}
            aria-label={showNewPassword ? "Hide password" : "Show password"}
          >
            <i className={showNewPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
          </button>
        </div>
      </div>
      {fieldErrors.newPassword && (
        <div className="field-error-text" style={{ marginTop: '0.2rem', marginBottom: '0.8rem' }}>{fieldErrors.newPassword}</div>
      )}
      {showPasswordHelper && (
        <div style={{
          marginTop: '0.5rem',
          marginBottom: '1rem',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '0.75rem',
          backgroundColor: '#f8fafc'
        }}>
          {unmetPasswordRequirements.length > 0 ? (
            <>
              <div style={{ color: '#e53e3e', fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                Password must include:
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {passwordRequirementStatuses.map((req) => (
                  <div
                    key={req.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.35rem',
                      color: req.met ? '#16a34a' : '#e53e3e',
                      fontSize: '0.85rem',
                      textDecoration: req.met ? 'line-through' : 'none',
                      opacity: req.met ? 0.6 : 1,
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <span style={{ fontWeight: 700 }}>{req.met ? '✓' : '•'}</span>
                    <span>{req.label}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ color: '#16a34a', fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span>✓</span>
              <span>All password requirements met</span>
            </div>
          )}
        </div>
      )}
      <div className={`auth-input-icon-wrapper ${confirmPasswordFocused || confirmPassword ? 'focused has-value' : ''}`}>
        <i className="fas fa-lock auth-input-icon"></i>
        <label className="auth-floating-label">Confirm Password *</label>
        <div style={{ position: 'relative' }}>
          <input
            type={showConfirmPassword ? "text" : "password"}
            className="auth-input-with-icon"
            placeholder="Confirm Password *"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            minLength={6}
            maxLength={12}
            onFocus={() => setConfirmPasswordFocused(true)}
            onBlur={() => setConfirmPasswordFocused(false)}
            required
            disabled={loading}
            style={{ paddingRight: '45px' }}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            disabled={loading}
            style={{
              position: 'absolute',
              right: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              color: '#666',
              fontSize: '18px',
              padding: '5px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              opacity: loading ? 0.5 : 1
            }}
            aria-label={showConfirmPassword ? "Hide password" : "Show password"}
          >
            <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
          </button>
        </div>
      </div>
      {(fieldErrors.confirmPassword || (confirmPassword && newPassword !== confirmPassword)) && (
        <div className="field-error-text" style={{ marginTop: '0.2rem', marginBottom: '1rem' }}>
          {fieldErrors.confirmPassword || 'Passwords do not match'}
        </div>
      )}

      <button
        type="submit"
        className="auth-primary-btn"
        disabled={
          loading ||
          !newPassword ||
          !confirmPassword ||
          newPassword !== confirmPassword ||
          !passwordRegex.test(newPassword)
        }
        title={
          !newPassword || !confirmPassword ? "Please fill both password fields" :
            newPassword !== confirmPassword ? "Passwords do not match" :
              !passwordRegex.test(newPassword) ? "Password requirements not met" : ""
        }
        style={{
          opacity: (loading || !newPassword || !confirmPassword || newPassword !== confirmPassword || !passwordRegex.test(newPassword)) ? 0.6 : 1,
          cursor: (loading || !newPassword || !confirmPassword || newPassword !== confirmPassword || !passwordRegex.test(newPassword)) ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Resetting...' : 'Reset Password'}
      </button>
    </>
  );

  return (
    <>
      <main className="auth-page signup-page-enhanced">
        <div className="container auth-container" style={{ position: 'relative', zIndex: 1 }}>
          <div
            className="auth-card"
            style={{
              position: 'relative',
              padding: '0.5rem 1.25rem',
            }}
          >
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
              <h2 style={{ textAlign: 'center', marginBottom: '0.25rem', fontWeight: '600', color: 'var(--gray-900)' }}>Forgot Password</h2>
              <p style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.4' }}>
                Enter your email, verify with OTP, and set a new password.
              </p>
              <h3
                className="auth-column-title"
                style={{ textAlign: 'center', marginBottom: '0.5rem' }}
              >
                {step === 'email' ? 'Send OTP' : step === 'otp' ? 'Verify OTP' : 'Reset Password'}
              </h3>

              <form className="auth-form" onSubmit={handleSubmit}>
                {error && <div className="auth-error-message">{error}</div>}
                {success && <div className="auth-success-message">{success}</div>}

                {step === 'email' && renderEmailStep()}
                {step === 'otp' && renderOtpStep()}
                {step === 'reset' && renderResetStep()}

                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                  <p style={{ color: '#666', fontSize: '14px' }}>
                    Remembered your password?{' '}
                    <Link
                      to="/login"
                      style={{
                        color: '#7c3aed',
                        textDecoration: 'none',
                        fontWeight: '600',
                        cursor: 'pointer',
                      }}
                    >
                      Login here
                    </Link>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default ForgotPassword;


