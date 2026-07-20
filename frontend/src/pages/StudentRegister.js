import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

// Only personal/free-domain emails are allowed for student practice accounts.
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

function StudentRegister() {
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      navigate('/dashboard', { replace: true });
      return;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [navigate]);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupError, setSignupError] = useState('');
  const [signupSuccess, setSignupSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [fullNameFocused, setFullNameFocused] = useState(false);
  const [emailFocused, setEmailFocused] = useState(false);
  const [phoneFocused, setPhoneFocused] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [confirmPasswordFocused, setConfirmPasswordFocused] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupError('');
    setFieldErrors({});
    setSignupSuccess('');

    // 1. Validate Full Name
    if (!fullName || fullName.trim().length < 2) {
      setFieldErrors(prev => ({ ...prev, fullName: 'Name must be at least 2 characters.' }));
      return;
    }
    if (!/^[a-zA-Z\s]+$/.test(fullName.trim())) {
      setFieldErrors(prev => ({ ...prev, fullName: 'Name must contain only letters and spaces.' }));
      return;
    }

    // 2. Validate Email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setFieldErrors(prev => ({ ...prev, email: 'Please enter a valid email address.' }));
      return;
    }

    // Reject organisation/corporate email addresses
    if (!isPersonalEmail(email)) {
      setFieldErrors(prev => ({
        ...prev,
        email: 'Organisation emails are not allowed. Please use a personal email (e.g. Gmail, Yahoo, Outlook).'
      }));
      setSignupError(
        'Please use a personal email address (e.g. Gmail, Yahoo, Outlook). ' +
        'Organisation or company emails are not allowed for student practice accounts.'
      );
      return;
    }

    // 3. Validate Phone (optional, but if provided, must be valid 10 digits starting with 6-9)
    if (phone) {
      const cleanPhone = phone.replace(/[\s()-]/g, '');
      if (!/^[6-9]\d{9}$/.test(cleanPhone)) {
        setFieldErrors(prev => ({ ...prev, phone: 'Mobile number must be 10 digits and start with 6, 7, 8, or 9.' }));
        return;
      }
    }

    // 4. Validate Password Complexity
    const hasLength = password.length >= 6 && password.length <= 12;
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasNum = /[0-9]/.test(password);
    const hasSpec = /[^A-Za-z0-9]/.test(password);

    if (!hasLength || !hasUpper || !hasLower || !hasNum || !hasSpec) {
      let passwordErrors = [];
      if (!hasLength) passwordErrors.push('6-12 characters');
      if (!hasUpper) passwordErrors.push('one uppercase letter');
      if (!hasLower) passwordErrors.push('one lowercase letter');
      if (!hasNum) passwordErrors.push('one number');
      if (!hasSpec) passwordErrors.push('one special character');
      setFieldErrors(prev => ({ ...prev, password: `Password needs: ${passwordErrors.join(', ')}.` }));
      return;
    }

    // 5. Validate Password Match
    if (password !== confirmPassword) {
      setFieldErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match' }));
      return;
    }

    setSignupLoading(true);

    try {
      await axios.post(`${API_BASE_URL}/student/register/`, {
        full_name: fullName,
        email: email,
        phone: phone,
        password: password,
      });

      setSignupSuccess('Account created successfully! Redirecting to login...');
      setTimeout(() => {
        navigate('/student/login');
      }, 2000);

    } catch (error) {
      if (error.response) {
        const errorData = error.response.data;
        setSignupError(errorData.error || errorData.message || 'Registration failed.');
      } else {
        setSignupError('Unable to connect to server.');
      }
    } finally {
      setSignupLoading(false);
    }
  };

  return (
    <div className="auth-split-page">
      {/* Left Side: Branded Panel */}
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
          <h1 className="left-intro-title">Get Interview Ready</h1>
          <p className="left-intro-subtitle">
            Practice AI-Powered Mock Assessments and Mock Interviews.<br />
            Get direct public feedback and improvement tips instantly.
          </p>
          <div className="left-intro-image-wrapper">
            <img
              src="/register-illustration.png"
              alt="Prep Illustration"
              className="left-intro-image"
            />
          </div>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="auth-right-side">
        <div className="form-header-content">
          <h2 className="form-header-title">Student Signup</h2>
          <p className="form-header-subtitle" style={{ marginBottom: '2.5rem' }}>Create a practice candidate account</p>
        </div>

        <form className="auth-form" onSubmit={handleSignup}>
          {signupSuccess && (
            <div className="auth-success-message" style={{ marginBottom: '1rem' }}>{signupSuccess}</div>
          )}

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
              disabled={signupLoading}
            />
            <label className="auth-floating-label">Full Name *</label>
          </div>
          {fieldErrors.fullName && (
            <div className="field-error-text" style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.75rem', textAlign: 'left' }}>
              {fieldErrors.fullName}
            </div>
          )}

          <div className={`auth-input-icon-wrapper ${emailFocused || email ? 'focused has-value' : ''}`}>
            <i className="fas fa-envelope auth-input-icon"></i>
            <input
              type="email"
              className="auth-input-with-icon"
              placeholder="Email *"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onFocus={() => setEmailFocused(true)}
              onBlur={() => setEmailFocused(false)}
              required
              disabled={signupLoading}
            />
            <label className="auth-floating-label">Email (Gmail/Yahoo allowed) *</label>
          </div>
          {fieldErrors.email && (
            <div className="field-error-text" style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.75rem', textAlign: 'left' }}>
              {fieldErrors.email}
            </div>
          )}

          <div className={`auth-input-icon-wrapper ${phoneFocused || phone ? 'focused has-value' : ''}`}>
            <i className="fas fa-phone auth-input-icon"></i>
            <input
              type="tel"
              className="auth-input-with-icon"
              placeholder="Mobile Number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              onFocus={() => setPhoneFocused(true)}
              onBlur={() => setPhoneFocused(false)}
              disabled={signupLoading}
            />
            <label className="auth-floating-label">Mobile Number</label>
          </div>
          {fieldErrors.phone && (
            <div className="field-error-text" style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.75rem', textAlign: 'left' }}>
              {fieldErrors.phone}
            </div>
          )}

          <div className={`auth-input-icon-wrapper ${passwordFocused || password ? 'focused has-value' : ''}`}>
            <i className="fas fa-lock auth-input-icon"></i>
            <div style={{ position: 'relative' }}>
              <input
                type={showPassword ? "text" : "password"}
                className="auth-input-with-icon"
                placeholder="Password *"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => setPasswordFocused(true)}
                onBlur={() => setPasswordFocused(false)}
                required
                disabled={signupLoading}
                style={{ paddingRight: '3rem' }}
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
                  color: '#9ca3af'
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

          {/* Interactive password complexity guide */}
          {(passwordFocused || password) && (
            <div className="password-requirements-box" style={{
              backgroundColor: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              padding: '12px 16px',
              marginTop: '4px',
              marginBottom: '16px',
              fontSize: '0.875rem',
              color: '#475569',
              textAlign: 'left'
            }}>
              <p style={{ fontWeight: '600', marginBottom: '8px', color: '#334155' }}>Password must include:</p>
              <ul style={{ listStyleType: 'none', paddingLeft: 0, margin: 0 }}>
                <li style={{ display: 'flex', alignItems: 'center', marginBottom: '6px', color: (password.length >= 6 && password.length <= 12) ? '#10b981' : '#64748b', fontSize: '0.85rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: (password.length >= 6 && password.length <= 12) ? '#10b981' : '#cbd5e1',
                    marginRight: '8px'
                  }}></span>
                  6–12 characters
                </li>
                <li style={{ display: 'flex', alignItems: 'center', marginBottom: '6px', color: /[A-Z]/.test(password) ? '#10b981' : '#64748b', fontSize: '0.85rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: /[A-Z]/.test(password) ? '#10b981' : '#cbd5e1',
                    marginRight: '8px'
                  }}></span>
                  At least one uppercase letter
                </li>
                <li style={{ display: 'flex', alignItems: 'center', marginBottom: '6px', color: /[a-z]/.test(password) ? '#10b981' : '#64748b', fontSize: '0.85rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: /[a-z]/.test(password) ? '#10b981' : '#cbd5e1',
                    marginRight: '8px'
                  }}></span>
                  At least one lowercase letter
                </li>
                <li style={{ display: 'flex', alignItems: 'center', marginBottom: '6px', color: /[0-9]/.test(password) ? '#10b981' : '#64748b', fontSize: '0.85rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: /[0-9]/.test(password) ? '#10b981' : '#cbd5e1',
                    marginRight: '8px'
                  }}></span>
                  At least one number
                </li>
                <li style={{ display: 'flex', alignItems: 'center', color: /[^A-Za-z0-9]/.test(password) ? '#10b981' : '#64748b', fontSize: '0.85rem' }}>
                  <span style={{
                    display: 'inline-block',
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: /[^A-Za-z0-9]/.test(password) ? '#10b981' : '#cbd5e1',
                    marginRight: '8px'
                  }}></span>
                  At least one special character
                </li>
              </ul>
            </div>
          )}

          <div className={`auth-input-icon-wrapper ${confirmPasswordFocused || confirmPassword ? 'focused has-value' : ''}`}>
            <i className="fas fa-lock auth-input-icon"></i>
            <div style={{ position: 'relative' }}>
              <input
                type={showConfirmPassword ? "text" : "password"}
                className="auth-input-with-icon"
                placeholder="Confirm Password *"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                onFocus={() => setConfirmPasswordFocused(true)}
                onBlur={() => setConfirmPasswordFocused(false)}
                onPaste={(e) => {
                  e.preventDefault();
                  setFieldErrors(prev => ({ ...prev, confirmPassword: 'Copy-pasting is disabled for Confirm Password field.' }));
                }}
                required
                disabled={signupLoading}
                style={{ paddingRight: '3rem' }}
              />
              <label className="auth-floating-label">Confirm Password *</label>
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="password-toggle-btn"
                style={{
                  position: 'absolute',
                  right: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#9ca3af'
                }}
              >
                <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
              </button>
            </div>
          </div>
          {fieldErrors.confirmPassword && (
            <div className="field-error-text" style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.75rem', textAlign: 'left' }}>
              {fieldErrors.confirmPassword}
            </div>
          )}

          <button
            type="submit"
            className="auth-primary-btn"
            disabled={signupLoading || !fullName || !email || !password || !confirmPassword}
            style={{ width: '100%', padding: '0.875rem', fontSize: '1rem', fontWeight: '600', marginTop: '1rem' }}
          >
            {signupLoading ? 'Creating account...' : 'REGISTER'}
          </button>

          {signupError && <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center' }}>{signupError}</div>}

          <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
            <p style={{ color: '#718096', fontSize: '0.9rem' }}>
              Already registered?{' '}
              <Link to="/student/login" style={{ color: '#7c3aed', fontWeight: '700', textDecoration: 'none' }}>
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default StudentRegister;
