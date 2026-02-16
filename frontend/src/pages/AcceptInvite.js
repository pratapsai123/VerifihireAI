import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
// import MainHeader from '../components/MainHeader';
// import Footer from '../components/Footer';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

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

  const canSubmit = useMemo(() => {
    return Boolean(token && fullName.trim() && tempPassword && newPassword && confirmPassword) && !submitting;
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
        if (!cancelled) setError(msg);
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

            {loading && <div style={{ textAlign: 'center' }}>Loading invitation...</div>}
            {error && <div className="auth-error-message">{error}</div>}
            {success && <div className="auth-success-message">{success}</div>}

            {!loading && invite && (
              <>
                <div style={{ marginBottom: '1rem', fontSize: 14, color: '#333' }}>
                  <div><strong>Company:</strong> {invite.company}</div>
                  <div><strong>Role:</strong> {invite.role}</div>
                  <div><strong>Email:</strong> {invite.email}</div>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                  <input
                    className="auth-input"
                    placeholder="Full Name"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    disabled={submitting}
                  />

                  <input
                    className="auth-input"
                    placeholder="Temporary Password"
                    type="password"
                    value={tempPassword}
                    onChange={(e) => setTempPassword(e.target.value)}
                    required
                    disabled={submitting}
                  />

                  <input
                    className="auth-input"
                    placeholder="New Password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    disabled={submitting}
                  />

                  <input
                    className="auth-input"
                    placeholder="Confirm New Password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    disabled={submitting}
                  />

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


