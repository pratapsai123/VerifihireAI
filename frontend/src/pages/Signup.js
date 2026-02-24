import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import OtpCountdown from '../components/OtpCountdown';

// Django API base URL - Update this to match your Django backend
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

function Signup() {
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

  // Signup form state
  const [fullName, setFullName] = useState('');
  const [businessEmail, setBusinessEmail] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupError, setSignupError] = useState('');
  const [signupSuccess, setSignupSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [fullNameFocused, setFullNameFocused] = useState(false);
  const [businessEmailFocused, setBusinessEmailFocused] = useState(false);
  const [organizationNameFocused, setOrganizationNameFocused] = useState(false);
  const [confirmPasswordFocused, setConfirmPasswordFocused] = useState(false);
  const [otpFocused, setOtpFocused] = useState(false);
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$/;
  const passwordRequirements = [
    { id: 'length', label: '6-12 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
    { id: 'uppercase', label: 'At least one uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
    { id: 'lowercase', label: 'At least one lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
    { id: 'number', label: 'At least one number', test: (pwd) => /\d/.test(pwd) },
    { id: 'special', label: 'At least one special character', test: (pwd) => /[^A-Za-z0-9]/.test(pwd) },
  ];

  // Email verification state
  const [emailVerified, setEmailVerified] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [otpError, setOtpError] = useState('');
  const [otpSuccess, setOtpSuccess] = useState('');
  const [otpExpiresAtMs, setOtpExpiresAtMs] = useState(null);
  const [otpExpired, setOtpExpired] = useState(false);
  const [otpRemainingSeconds, setOtpRemainingSeconds] = useState(null);

  // Handle sending OTP
  const handleSendOtp = async () => {
    if (!businessEmail) {
      setOtpError('Please enter your business email first.');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(businessEmail)) {
      setOtpError('Please enter a valid email address.');
      return;
    }

    setSendingOtp(true);
    setOtpError('');
    setOtpSuccess('');

    try {
      const response = await axios.post(`${API_BASE_URL}/send-otp/`, {
        email: businessEmail,
        context: 'register',
      });

      setOtpSent(true);
      const expiresIn = Number(response.data?.expires_in) || 120;
      setOtpExpiresAtMs(Date.now() + expiresIn * 1000);
      setOtpExpired(false);
      setOtpRemainingSeconds(expiresIn);
      setOtp('');
      setOtpSuccess(response.data.message || 'OTP sent to your email!');

      // In development, if OTP is returned, show it
      if (response.data.otp) {
        setOtpSuccess(`OTP sent! Your OTP is: ${response.data.otp} (for development)`);
      }
    } catch (error) {
      if (error.response) {
        setOtpError(error.response.data.error || 'Failed to send OTP. Please try again.');
      } else {
        setOtpError('Unable to connect to server. Please check if Django backend is running.');
      }
    } finally {
      setSendingOtp(false);
    }
  };

  // Derived flag to keep the resend button disabled while a timer is active
  const isResendLocked = verifyingOtp || sendingOtp || (otpExpiresAtMs && Date.now() < otpExpiresAtMs && !otpExpired);

  // Handle verifying OTP
  const handleVerifyOtp = async () => {
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
      await axios.post(`${API_BASE_URL}/verify-otp/`, {
        email: businessEmail,
        otp: otp,
      });

      setEmailVerified(true);
      setOtpSuccess('Email verified successfully!');
      setOtpError('');
      setOtpExpiresAtMs(null);
      setOtpExpired(false);
    } catch (error) {
      if (error.response) {
        setOtpError(error.response.data.error || 'Invalid OTP. Please try again.');
      } else {
        setOtpError('Unable to connect to server. Please check if Django backend is running.');
      }
    } finally {
      setVerifyingOtp(false);
    }
  };

  // Handle Signup
  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupError('');
    setSignupSuccess('');
    setPasswordError('');

    // Password strength validation
    if (!passwordRegex.test(password)) {
      setPasswordError('Password must be 6-12 characters and include uppercase, lowercase, number, and special character.');
      return;
    }

    // Check if email is verified
    if (!emailVerified) {
      setSignupError('Please verify your email first by entering the OTP.');
      return;
    }

    // Validate password confirmation
    if (password !== confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }

    setSignupLoading(true);

    try {
      await axios.post(`${API_BASE_URL}/register/`, {
        full_name: fullName,
        email: businessEmail,
        organization_name: organizationName,
        password: password,
      });

      // Success
      setSignupSuccess('Account created successfully! Redirecting to login...');
      // Clear form
      setFullName('');
      setBusinessEmail('');
      setOrganizationName('');
      setPassword('');
      setConfirmPassword('');
      setEmailVerified(false);
      setOtp('');
      setOtpSent(false);

      // Redirect to login page after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);

    } catch (error) {
      // Handle error
      if (error.response) {
        // Server responded with error
        const errorData = error.response.data;
        if (errorData.email) {
          setSignupError(errorData.email[0]);
        } else if (errorData.password) {
          setSignupError(errorData.password[0]);
        } else if (errorData.full_name) {
          setSignupError(errorData.full_name[0]);
        } else if (errorData.organization_name) {
          setSignupError(errorData.organization_name[0]);
        } else {
          setSignupError(errorData.message || errorData.error || 'Registration failed. Please try again.');
        }
      } else if (error.request) {
        setSignupError('Unable to connect to server. Please check if Django backend is running.');
      } else {
        setSignupError('An error occurred. Please try again.');
      }
      console.error('Signup error:', error);
    } finally {
      setSignupLoading(false);
    }
  };

  const passwordRequirementStatuses = passwordRequirements.map(req => ({
    ...req,
    met: req.test(password),
  }));
  const unmetPasswordRequirements = passwordRequirementStatuses.filter(req => !req.met);
  const showPasswordHelper = (passwordFocused || password.length > 0);

  return (
    <>
      <main className="auth-page signup-page-enhanced">
        <div className="container auth-container" style={{ position: 'relative', zIndex: 1 }}>
          <div className="auth-card" data-aos="fade-up" style={{
            maxWidth: '420px',
            width: '100%',
            padding: '0.5rem 1rem'
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
              <h2 style={{ textAlign: 'center', marginBottom: '0.25rem', fontWeight: '600', color: 'var(--gray-900)' }}>Create your account</h2>
              <p style={{ textAlign: 'center', marginBottom: '1rem', color: 'var(--gray-600)', fontSize: '0.9rem', lineHeight: '1.4' }}>
                Sign up to manage assessments, view reports, and monitor candidate sessions.
              </p>
              <h3 className="auth-column-title" style={{ textAlign: 'center', marginBottom: '1rem' }}>Sign up</h3>
              <form className="auth-form" onSubmit={handleSignup}>
                {signupError && (
                  <div className="auth-error-message">{signupError}</div>
                )}
                {passwordError && (
                  <div className="auth-error-message">{passwordError}</div>
                )}
                {signupSuccess && (
                  <div className="auth-success-message">{signupSuccess}</div>
                )}

                <div className={`auth-input-icon-wrapper ${fullNameFocused || fullName ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                  <i className="fas fa-user auth-input-icon"></i>
                  <label className="auth-floating-label">First Name *</label>
                  <input
                    type="text"
                    className="auth-input-with-icon"
                    placeholder="First Name *"
                    value={fullName}
                    onChange={(e) => {
                      const value = e.target.value.replace(/[^a-zA-Z\s]/g, '');
                      setFullName(value);
                    }}
                    onFocus={() => setFullNameFocused(true)}
                    onBlur={() => setFullNameFocused(false)}
                    required
                    maxLength={50}
                    disabled={signupLoading}
                  />
                </div>

                <div className={`auth-input-icon-wrapper ${businessEmailFocused || businessEmail ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                  <i className="fas fa-envelope auth-input-icon"></i>
                  <label className="auth-floating-label">Business Email *</label>
                  <input
                    type="email"
                    className="auth-input-with-icon"
                    placeholder="Business Email *"
                    value={businessEmail}
                    onChange={(e) => {
                      setBusinessEmail(e.target.value);
                      // Reset verification if email changes
                      if (emailVerified) {
                        setEmailVerified(false);
                        setOtpSent(false);
                        setOtp('');
                      }
                    }}
                    onFocus={() => setBusinessEmailFocused(true)}
                    onBlur={() => setBusinessEmailFocused(false)}
                    required
                    maxLength={100}
                    disabled={signupLoading || emailVerified}
                  />
                </div>

                {/* Email Verification Section */}
                {businessEmail && !emailVerified && (
                  <div style={{
                    marginBottom: '1.5rem',
                    padding: '1rem',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    backgroundColor: '#f9f9f9'
                  }}>
                    <div style={{ marginBottom: '0.5rem', fontSize: '14px', fontWeight: '500', color: '#333', textAlign: 'center' }}>
                      Verify your email
                    </div>

                    {otpError && (
                      <div className="auth-error-message" style={{ marginBottom: '0.5rem', fontSize: '12px' }}>
                        {otpError}
                      </div>
                    )}

                    {otpSuccess && (
                      <div className="auth-success-message" style={{ marginBottom: '0.5rem', fontSize: '12px' }}>
                        {otpSuccess}
                      </div>
                    )}

                    {!otpSent ? (
                      <button
                        type="button"
                        onClick={handleSendOtp}
                        disabled={sendingOtp || !businessEmail}
                        style={{
                          width: '100%',
                          padding: '10px',
                          backgroundColor: '#7c3aed',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: sendingOtp || !businessEmail ? 'not-allowed' : 'pointer',
                          fontSize: '14px',
                          fontWeight: '500',
                          opacity: sendingOtp || !businessEmail ? 0.6 : 1
                        }}
                      >
                        {sendingOtp ? 'Sending OTP...' : 'Send OTP'}
                      </button>
                    ) : (
                      <div>
                        <div className={`auth-input-icon-wrapper ${otpFocused || otp ? 'focused has-value' : ''}`} style={{ marginBottom: '0.5rem' }}>
                          <i className="fas fa-key auth-input-icon"></i>
                          <label className="auth-floating-label">Enter 6-digit OTP</label>
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
                            disabled={verifyingOtp || emailVerified}
                            style={{ textAlign: 'center', fontSize: '16px', letterSpacing: '4px' }}
                          />
                        </div>
                        <OtpCountdown
                          expiresAtMs={otpExpiresAtMs}
                          onExpire={() => setOtpExpired(true)}
                          onRemainingSecondsChange={setOtpRemainingSeconds}
                        />
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            type="button"
                            onClick={handleVerifyOtp}
                            disabled={verifyingOtp || otp.length !== 6 || emailVerified || otpExpired}
                            style={{
                              flex: 1,
                              padding: '10px',
                              backgroundColor: '#7c3aed',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              cursor: verifyingOtp || otp.length !== 6 || emailVerified ? 'not-allowed' : 'pointer',
                              fontSize: '14px',
                              fontWeight: '500',
                              opacity: verifyingOtp || otp.length !== 6 || emailVerified ? 0.6 : 1
                            }}
                          >
                            {verifyingOtp ? 'Verifying...' : 'Verify OTP'}
                          </button>
                          <button
                            type="button"
                            onClick={handleSendOtp}
                            disabled={isResendLocked}
                            style={{
                              padding: '10px 15px',
                              backgroundColor: '#f5f5f5',
                              color: '#333',
                              border: '1px solid #ddd',
                              borderRadius: '6px',
                              cursor: isResendLocked ? 'not-allowed' : 'pointer',
                              fontSize: '14px',
                              fontWeight: '500',
                              opacity: isResendLocked ? 0.6 : 1
                            }}
                          >
                            {sendingOtp ? 'Resending...' : 'Resend'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {emailVerified && (
                  <div style={{
                    marginBottom: '1.5rem',
                    padding: '0.75rem',
                    backgroundColor: '#d4edda',
                    border: '1px solid #c3e6cb',
                    borderRadius: '6px',
                    color: '#155724',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}>
                    <span>✓</span>
                    <span>Email verified successfully!</span>
                  </div>
                )}

                <div className={`auth-input-icon-wrapper ${organizationNameFocused || organizationName ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                  <i className="fas fa-building auth-input-icon"></i>
                  <label className="auth-floating-label">Organization Name *</label>
                  <input
                    type="text"
                    className="auth-input-with-icon"
                    placeholder="Organization Name *"
                    value={organizationName}
                    onChange={(e) => setOrganizationName(e.target.value)}
                    onFocus={() => setOrganizationNameFocused(true)}
                    onBlur={() => setOrganizationNameFocused(false)}
                    required
                    maxLength={100}
                    disabled={signupLoading}
                  />
                </div>

                <div className={`auth-input-icon-wrapper ${passwordFocused || password ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
                  <i className="fas fa-lock auth-input-icon"></i>
                  <label className="auth-floating-label">Password *</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showPassword ? "text" : "password"}
                      className="auth-input-with-icon"
                      placeholder="Password *"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      minLength={6}
                      maxLength={12}
                      required
                      disabled={signupLoading}
                      onFocus={() => {
                        setPasswordFocused(true);
                      }}
                      onBlur={() => setPasswordFocused(false)}
                      style={{ paddingRight: '45px' }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={signupLoading}
                      style={{
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: signupLoading ? 'not-allowed' : 'pointer',
                        color: '#666',
                        fontSize: '18px',
                        padding: '5px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: signupLoading ? 0.5 : 1
                      }}
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      <i className={showPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                    </button>
                  </div>
                </div>
                {showPasswordHelper && (
                  <div style={{
                    marginTop: '0.5rem',
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

                <div className={`auth-input-icon-wrapper ${confirmPasswordFocused || confirmPassword ? 'focused has-value' : ''}`} style={{ marginBottom: '0.75rem' }}>
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
                      required
                      disabled={signupLoading}
                      onFocus={() => setConfirmPasswordFocused(true)}
                      onBlur={() => setConfirmPasswordFocused(false)}
                      style={{ paddingRight: '45px' }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      disabled={signupLoading}
                      style={{
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: signupLoading ? 'not-allowed' : 'pointer',
                        color: '#666',
                        fontSize: '18px',
                        padding: '5px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        opacity: signupLoading ? 0.5 : 1
                      }}
                      aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                    >
                      <i className={showConfirmPassword ? "fas fa-eye-slash" : "fas fa-eye"}></i>
                    </button>
                  </div>
                </div>

                {/* Explicit Password Mismatch Error */}
                {confirmPassword && password !== confirmPassword && (
                  <div style={{ color: '#e53e3e', fontSize: '0.8rem', marginTop: '-0.5rem', marginBottom: '0.75rem' }}>
                    Passwords do not match
                  </div>
                )}

                <button
                  type="submit"
                  className="auth-primary-btn"
                  disabled={
                    signupLoading ||
                    !fullName ||
                    !businessEmail ||
                    !organizationName ||
                    !password ||
                    !confirmPassword ||
                    password !== confirmPassword ||
                    !passwordRegex.test(password) ||
                    !emailVerified
                  }
                  style={{
                    width: '100%',
                    padding: '10px',
                    fontSize: '16px',
                    fontWeight: '600',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}
                >
                  {signupLoading ? 'Creating account...' : 'REGISTER'}
                </button>

                <div style={{ marginTop: '0.25rem', textAlign: 'center' }}>
                  <p style={{ color: '#666', fontSize: '14px' }}>
                    Already have an account?{' '}
                    <Link
                      to="/login"
                      style={{
                        color: '#7c3aed',
                        textDecoration: 'none',
                        fontWeight: '600',
                        cursor: 'pointer'
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

export default Signup;