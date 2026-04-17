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
  const [fieldErrors, setFieldErrors] = useState({});
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

  const getRoleContent = () => {
    const roleVal = invite?.role?.toLowerCase() || '';
    if (roleVal.includes('interviewer')) {
      return {
        title: 'Interviewer Invitation',
        subtitle: 'You\'ve been invited to join the interview team. Set your password to start evaluating candidates.',
        image: '/interviewer_role_illustration_v2_1774866264626.png'
      };
    } else if (roleVal.includes('manager')) {
      return {
        title: 'HR Manager Invitation',
        subtitle: 'Your management account is ready. Complete your profile to manage teams and hiring strategies.',
        image: '/hr_manager_role_illustration_v2_1774866294446.png'
      };
    } else {
      return {
        title: 'HR Recruiter Invitation',
        subtitle: 'Join as a Recruiter. Set up your access to source talent and manage assessments.',
        image: '/hr_recruiter_role_illustration_v2_1774866319365.png'
      };
    }
  };

  const roleContent = getRoleContent();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f8fafc' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <i className="fas fa-circle-notch fa-spin" style={{ fontSize: '2.5rem', color: '#4f46e5' }}></i>
          <div style={{ color: '#64748b', fontSize: '1.1rem', fontWeight: 500 }}>Verifying invitation...</div>
        </div>
      </div>
    );
  }

  if (!invite && (success || error)) {
    const isSuccess = Boolean(success);
    return (
      <div className="auth-split-page" style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        background: '#f8fafc'
      }}>
        <div style={{
          background: 'white',
          padding: '3rem 2.5rem',
          borderRadius: '24px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.05)',
          textAlign: 'center',
          maxWidth: '440px',
          width: '90%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          margin: '2rem'
        }}>
          {isSuccess ? (
            <div style={{
              width: '80px',
              height: '80px',
              background: '#ecfdf5',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '2rem',
              boxShadow: '0 10px 25px rgba(16, 185, 129, 0.15)'
            }}>
              <i className="fas fa-check" style={{ fontSize: '3rem', color: '#10b981' }}></i>
            </div>
          ) : (
             <div style={{
              width: '80px',
              height: '80px',
              background: '#fef2f2',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '2rem',
              boxShadow: '0 10px 25px rgba(239, 68, 68, 0.15)'
            }}>
              <i className="fas fa-exclamation-triangle" style={{ fontSize: '2.5rem', color: '#ef4444' }}></i>
            </div>
          )}
          
          <h2 style={{ 
            fontSize: '1.75rem', 
            color: '#1e293b', 
            fontWeight: '700', 
            marginBottom: '1rem', 
            fontFamily: "'Plus Jakarta Sans', sans-serif" 
          }}>
            {isSuccess ? 'Invite Accepted' : 'Invalid Link'}
          </h2>
          <p style={{ color: '#64748b', fontSize: '1.05rem', marginBottom: '2.5rem', lineHeight: '1.6' }}>
            {isSuccess 
              ? 'You have already accepted this invitation. You can proceed to login to access your dashboard.' 
              : error}
          </p>
          <Link to="/login" className="auth-primary-btn" style={{ 
            padding: '1rem 2.5rem', 
            textDecoration: 'none', 
            borderRadius: '12px',
            fontSize: '1rem',
            fontWeight: '600',
            width: '100%',
            display: 'inline-block'
          }}>
            Back to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-split-page">
      {/* Left Side: Illustration and Intro */}
      <div className="auth-left-side">
        <div className="left-branded-header" style={{ marginBottom: '2rem' }}>
          <div className="brand-logo-group">
            <img src="/auth-logo-v7.png" alt="VerifiHireAI Logo" className="brand-logo-img" />
            <div className="brand-text-container">
              <span className="brand-name-text">VerifiHireAI</span>
              <p className="brand-tagline">Trust in Every Hire</p>
            </div>
          </div>
        </div>

        <div className="left-intro-content" style={{ marginTop: '0.5rem' }}>
          <h1 className="left-intro-title">{invite ? roleContent.title : 'Accept Invitation'}</h1>
          <p className="left-intro-subtitle">
            {invite ? roleContent.subtitle : 'Complete your registration to join your organization.'}
          </p>
          <div className="left-intro-image-wrapper">
            <img 
              src={invite ? roleContent.image : '/register-illustration.png'} 
              alt="Role Illustration" 
              className="left-intro-image"
              style={{ maxWidth: invite?.role?.toLowerCase()?.includes('interviewer') ? '420px' : '450px' }}
            />
          </div>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="auth-right-side">
        <div className="form-header-content">
          <h2 className="form-header-title">Accept Invite</h2>
          <p className="form-header-subtitle" style={{ marginBottom: '2.5rem' }}>
            {invite ? `Joining ${invite.company} as ${invite.role}` : 'Set up your account password'}
          </p>
        </div>

        {!loading && invite && (
          <form className="auth-form" onSubmit={handleSubmit}>
            {success && <div className="auth-success-message" style={{ marginBottom: '1.5rem' }}>{success}</div>}
            
            <div className={`auth-input-icon-wrapper ${fullNameFocused || fullName ? 'focused has-value' : ''}`}>
              <i className="fas fa-user auth-input-icon"></i>
              <input
                type="text"
                className="auth-input-with-icon"
                placeholder="Full Name *"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                onFocus={() => setFullNameFocused(true)}
                onBlur={() => setFullNameFocused(false)}
                required
                disabled={submitting}
              />
              <label className="auth-floating-label">Full Name *</label>
            </div>

            <div className={`auth-input-icon-wrapper ${tempPasswordFocused || tempPassword ? 'focused has-value' : ''}`}>
              <i className="fas fa-key auth-input-icon"></i>
              <input
                type={showTempPassword ? "text" : "password"}
                className="auth-input-with-icon"
                placeholder="Temporary Password *"
                value={tempPassword}
                onChange={(e) => setTempPassword(e.target.value)}
                onFocus={() => setTempPasswordFocused(true)}
                onBlur={() => setTempPasswordFocused(false)}
                required
                style={{ paddingRight: '2.5rem' }}
                disabled={submitting}
              />
              <label className="auth-floating-label">Temporary Password *</label>
              <button type="button" onClick={() => setShowTempPassword(!showTempPassword)} className="password-toggle-btn" style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'none', cursor: 'pointer', color: '#94a3b8' }}>
                <i className={showTempPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
              </button>
            </div>

            <div className={`auth-input-icon-wrapper ${newPasswordFocused || newPassword ? 'focused has-value' : ''}`}>
              <i className="fas fa-lock auth-input-icon"></i>
              <input
                type={showNewPassword ? "text" : "password"}
                className="auth-input-with-icon"
                placeholder="New Password *"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                onFocus={() => setNewPasswordFocused(true)}
                onBlur={() => setNewPasswordFocused(false)}
                required
                style={{ paddingRight: '2.5rem' }}
                disabled={submitting}
              />
              <label className="auth-floating-label">New Password *</label>
              <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="password-toggle-btn" style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'none', cursor: 'pointer', color: '#94a3b8' }}>
                <i className={showNewPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
              </button>
            </div>

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
                placeholder="Confirm New Password *"
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
              style={{ paddingRight: '2.5rem' }}
              disabled={submitting}
            />
            <label className="auth-floating-label">Confirm New Password *</label>
            <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="password-toggle-btn" style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', border: 'none', background: 'none', cursor: 'pointer', color: '#94a3b8' }}>
              <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
            </button>
          </div>

          {(fieldErrors.confirmPassword || (confirmPassword.length > 0 && newPassword !== confirmPassword)) && (
            <div className="field-error-text" style={{ color: '#e53e3e', fontSize: '0.8rem', marginTop: '-0.75rem', marginBottom: '1.25rem' }}>
              {fieldErrors.confirmPassword || 'Passwords do not match'}
            </div>
          )}

            <button type="submit" className="auth-primary-btn" disabled={!canSubmit} style={{ width: '100%', padding: '0.875rem', fontWeight: '600', fontSize: '1rem' }}>
              {submitting ? 'Activating...' : 'Activate Account'}
            </button>
            {error && (
              <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center', marginBottom: 0 }}>{error}</div>
            )}
          </form>
        )}


      </div>
    </div>
  );
}


