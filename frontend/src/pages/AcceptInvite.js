import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
// import MainHeader from '../components/MainHeader';
// import Footer from '../components/Footer';

import { API_BASE_URL } from '../apiConfig';

export default function AcceptInvite() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';

  const [loading, setLoading] = useState(true);
  const [invite, setInvite] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [fullName, setFullName] = useState('');
  const [tempPassword, setTempPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [showTempPassword, setShowTempPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [passwordFocused, setPasswordFocused] = useState(false);
  const [fullNameFocused, setFullNameFocused] = useState(false);
  const [tempPasswordFocused, setTempPasswordFocused] = useState(false);
  const [newPasswordFocused, setNewPasswordFocused] = useState(false);
  const [confirmPasswordFocused, setConfirmPasswordFocused] = useState(false);

  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$/;
  const passwordRequirements = [
    { id: 'length', label: '6-12 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
    { id: 'uppercase', label: 'At least one uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
    { id: 'lowercase', label: 'At least one lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
    { id: 'number', label: 'At least one number', test: (pwd) => /\d/.test(pwd) },
    { id: 'special', label: 'At least one special character', test: (pwd) => /[^A-Za-z0-9]/.test(pwd) },
  ];

  const unmetPasswordRequirements = useMemo(() => {
    return passwordRequirements.filter(req => !req.test(newPassword));
  }, [newPassword]);

  const showPasswordHelper = newPasswordFocused && newPassword.length > 0;

  const showMismatchError = confirmPassword.length > 0 && newPassword !== confirmPassword;

  const canSubmit = useMemo(() => {
    return Boolean(
      token && 
      fullName.trim() && 
      tempPassword && 
      passwordRegex.test(newPassword) && 
      newPassword === confirmPassword
    ) && !submitting;
  }, [token, fullName, tempPassword, newPassword, confirmPassword, submitting]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError('');
      setInvite(null);
      if (!token) {
        setError('Missing invitation token.');
        setLoading(false);
        return;
      }
      try {
        const res = await axios.get(`${API_BASE_URL}/users/invite/${token}/`);
        if (!cancelled) setInvite(res.data);
      } catch (e) {
        const msg = e?.response?.data?.error || 'Unable to load invitation.';
        if (!cancelled) {
          if (msg.toLowerCase().includes('is accepted')) {
            setSuccess('Invitation is accepted.');
          } else {
            setError(msg);
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!token) {
      setError('Missing invitation token.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setSubmitting(true);
    try {
      await axios.post(`${API_BASE_URL}/users/accept-invite/`, {
        token,
        full_name: fullName,
        temp_password: tempPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setSuccess('Account created successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (e2) {
      const msg = e2?.response?.data?.error || 'Failed to accept invitation.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      {/* <MainHeader /> */}
      <main className="auth-page">
        <div className="container auth-container">
          <div className="auth-card" style={{ maxWidth: 520, width: '100%' }}>
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
            <h2 className="auth-title" style={{ textAlign: 'center', marginTop: 0 }}>Accept Invitation</h2>
            <p className="auth-subtitle" style={{ textAlign: 'center' }}>
              Set your password to activate your account.
            </p>

            {loading && <div style={{ textAlign: 'center', margin: '1rem 0' }}>Loading invitation...</div>}
            {error && <div className="auth-error-message" style={{ textAlign: 'center', margin: '1rem 0' }}>{error}</div>}
            {success && <div className="auth-success-message" style={{ textAlign: 'center', margin: '1rem 0' }}>{success}</div>}

            {!loading && invite && (
              <>
                <div style={{ marginBottom: '1.5rem', fontSize: 14, color: '#333', textAlign: 'center', borderBottom: '1px solid #eee', paddingBottom: '1rem' }}>
                  <div style={{ marginBottom: '0.25rem' }}><strong>Company:</strong> {invite.company}</div>
                  <div style={{ marginBottom: '0.25rem' }}><strong>Role:</strong> {invite.role}</div>
                  <div><strong>Email:</strong> {invite.email}</div>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                  <div className={`auth-input-icon-wrapper ${fullNameFocused || fullName ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                    <i className="fas fa-user auth-input-icon"></i>
                    <label className="auth-floating-label">Full Name *</label>
                    <input
                      className="auth-input-with-icon"
                      placeholder="Full Name *"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      onFocus={() => setFullNameFocused(true)}
                      onBlur={() => setFullNameFocused(false)}
                      required
                      disabled={submitting}
                    />
                  </div>

                  <div className={`auth-input-icon-wrapper ${tempPasswordFocused || tempPassword ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                    <i className="fas fa-lock auth-input-icon"></i>
                    <label className="auth-floating-label">Temporary Password *</label>
                    <div style={{ position: 'relative' }}>
                      <input
                        className="auth-input-with-icon"
                        placeholder="Temporary Password *"
                        type={showTempPassword ? "text" : "password"}
                        value={tempPassword}
                        onChange={(e) => setTempPassword(e.target.value)}
                        onFocus={() => setTempPasswordFocused(true)}
                        onBlur={() => setTempPasswordFocused(false)}
                        required
                        disabled={submitting}
                        style={{ paddingRight: '45px' }}
                      />
                      <button
                        type="button"
                        onClick={() => setShowTempPassword(!showTempPassword)}
                        disabled={submitting}
                        style={{
                          position: 'absolute',
                          right: '12px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          cursor: submitting ? 'not-allowed' : 'pointer',
                          color: '#666',
                          fontSize: '18px',
                          padding: '5px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: submitting ? 0.5 : 1,
                          zIndex: 10
                        }}
                      >
                        <i className={showTempPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                      </button>
                    </div>
                  </div>

                  <div className={`auth-input-icon-wrapper ${newPasswordFocused || newPassword ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                    <i className="fas fa-lock auth-input-icon"></i>
                    <label className="auth-floating-label">New Password *</label>
                    <div style={{ position: 'relative' }}>
                      <input
                        className="auth-input-with-icon"
                        placeholder="New Password *"
                        type={showNewPassword ? "text" : "password"}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        onFocus={() => setNewPasswordFocused(true)}
                        onBlur={() => setNewPasswordFocused(false)}
                        required
                        disabled={submitting}
                        style={{ paddingRight: '45px' }}
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        disabled={submitting}
                        style={{
                          position: 'absolute',
                          right: '12px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          cursor: submitting ? 'not-allowed' : 'pointer',
                          color: '#666',
                          fontSize: '18px',
                          padding: '5px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: submitting ? 0.5 : 1,
                          zIndex: 10
                        }}
                      >
                        <i className={showNewPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                      </button>
                    </div>
                  </div>

                  {showPasswordHelper && unmetPasswordRequirements.length > 0 && (
                    <div style={{
                      marginTop: '0rem',
                      marginBottom: '1rem',
                      border: '1px solid #fee2e2',
                      borderRadius: '8px',
                      padding: '0.6rem 0.75rem',
                      backgroundColor: '#fffafb'
                    }}>
                      <div style={{ color: '#e53e3e', fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                        Password requirements:
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                        {unmetPasswordRequirements.map((req) => (
                          <div
                            key={req.id}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '0.35rem',
                              color: '#e53e3e',
                              fontSize: '0.8rem',
                            }}
                          >
                            <span style={{ fontWeight: 700 }}>•</span>
                            <span>{req.label}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className={`auth-input-icon-wrapper ${confirmPasswordFocused || confirmPassword ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                    <i className="fas fa-lock auth-input-icon"></i>
                    <label className="auth-floating-label">Confirm New Password *</label>
                    <div style={{ position: 'relative' }}>
                      <input
                        className="auth-input-with-icon"
                        placeholder="Confirm New Password *"
                        type={showConfirmPassword ? "text" : "password"}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        onFocus={() => setConfirmPasswordFocused(true)}
                        onBlur={() => setConfirmPasswordFocused(false)}
                        required
                        disabled={submitting}
                        style={{ paddingRight: '45px' }}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        disabled={submitting}
                        style={{
                          position: 'absolute',
                          right: '12px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          cursor: submitting ? 'not-allowed' : 'pointer',
                          color: '#666',
                          fontSize: '18px',
                          padding: '5px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: submitting ? 0.5 : 1,
                          zIndex: 10
                        }}
                      >
                        <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                      </button>
                    </div>
                  </div>

                  {confirmPassword.length > 0 && newPassword !== confirmPassword && (
                    <div style={{ color: '#e53e3e', fontSize: '0.8rem', marginTop: '-0.5rem', marginBottom: '0.75rem', fontWeight: 600 }}>
                      <i className="fas fa-exclamation-circle" style={{ marginRight: '5px' }}></i>
                      Passwords do not match
                    </div>
                  )}

                  <button type="submit" className="auth-primary-btn" disabled={!canSubmit}>
                    {submitting ? 'Activating...' : 'Activate Account'}
                  </button>

                  <div style={{ marginTop: 16, textAlign: 'center' }}>
                    <Link to="/login" style={{ color: '#7c3aed', textDecoration: 'none', fontWeight: 600 }}>
                      Back to Login
                    </Link>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      </main>
      {/* <Footer /> */}
    </>
  );
}


