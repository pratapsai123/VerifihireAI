import { useState, useEffect, Fragment } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import OtpCountdown from '../components/OtpCountdown';
import { API_BASE_URL } from '../apiConfig';

function Signup() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // If the user is already logged in, redirect them to the dashboard (Instagram style)
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      navigate('/dashboard', { replace: true });
      return;
    }

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
    
    // Fetch Plans
    const fetchPlans = async () => {
      setPlansLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/plans/?t=${new Date().getTime()}`);
        setPlans(response.data.plans || []);
        if (response.data.plans && response.data.plans.length > 0) {
          const queryParams = new URLSearchParams(location.search);
          const urlPlanId = queryParams.get('plan_id');
          const urlBillingCycle = queryParams.get('billing_cycle');
          
          if (urlBillingCycle && ['monthly', 'biannual', 'annual'].includes(urlBillingCycle)) {
            setBillingCycle(urlBillingCycle);
          }
          
          if (urlPlanId) {
            setSelectedPlanId(Number(urlPlanId));
          } else {
            const freePlan = response.data.plans.find(p => parseFloat(p.base_price_monthly) === 0);
            setSelectedPlanId(freePlan ? freePlan.id : response.data.plans[0].id);
          }
        }
      } catch (error) {
        console.error("Failed to fetch plans:", error);
      } finally {
        setPlansLoading(false);
      }
    };
    fetchPlans();

    // Load Razorpay Script
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [navigate]);

  // Signup form state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [businessEmail, setBusinessEmail] = useState('');
  const [organizationName, setOrganizationName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);
  const [signupError, setSignupError] = useState('');
  const [signupSuccess, setSignupSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [firstNameFocused, setFirstNameFocused] = useState(false);
  const [lastNameFocused, setLastNameFocused] = useState(false);
  const [businessEmailFocused, setBusinessEmailFocused] = useState(false);
  const [organizationNameFocused, setOrganizationNameFocused] = useState(false);
  const [confirmPasswordFocused, setConfirmPasswordFocused] = useState(false);
  const [otpFocused, setOtpFocused] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$/;
  const passwordRequirements = [
    { id: 'length', label: '6-12 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
    { id: 'uppercase', label: 'At least one uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
    { id: 'lowercase', label: 'At least one lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
    { id: 'number', label: 'At least one number', test: (pwd) => /\d/.test(pwd) },
    { id: 'special', label: 'At least one special character', test: (pwd) => /[^A-Za-z0-9]/.test(pwd) },
  ];

  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [plansLoading, setPlansLoading] = useState(false);

  // Email verification state
  const [emailVerified, setEmailVerified] = useState(false);
  const [otp, setOtp] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [sendingOtp, setSendingOtp] = useState(false);
  const [verifyingOtp, setVerifyingOtp] = useState(false);
  const [otpSuccess, setOtpSuccess] = useState('');
  const [otpExpiresAtMs, setOtpExpiresAtMs] = useState(null);
  const [otpExpired, setOtpExpired] = useState(false);

  // Handle sending OTP
  const handleSendOtp = async () => {
    if (!businessEmail) {
      setFieldErrors(prev => ({ ...prev, businessEmail: 'Please enter your business email first.' }));
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(businessEmail)) {
      setFieldErrors(prev => ({ ...prev, businessEmail: 'Please enter a valid email address.' }));
      return;
    }

    // Check for free email domains
    const freeDomains = [
      'gmail.com', 'googlemail.com',
      'yahoo.com', 'yahoo.in', 'ymail.com', 'rocketmail.com',
      'outlook.com', 'hotmail.com', 'live.com', 'msn.com',
      'icloud.com', 'me.com', 'mac.com',
      'aol.com', 'proton.me', 'protonmail.com', 'zoho.com',
      'mail.com', 'email.com', 'post.com', 'usa.com',
      'yandex.com', 'gmx.com', 'gmx.net', 'fastmail.com',
      'tutanota.com', 'tuta.com'
    ];
    const domain = businessEmail.split('@')[1]?.toLowerCase();
    if (freeDomains.includes(domain)) {
      setFieldErrors(prev => ({ ...prev, businessEmail: 'Please use your business email. Free email domains like Gmail/Yahoo are not allowed for organization registration.' }));
      return;
    }

    setSendingOtp(true);
    setFieldErrors({}); // Clear previous errors
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
      setOtp('');
      setOtpSuccess(response.data.message || 'OTP sent to your email!');

      // In development, if OTP is returned, show it
      if (response.data.otp) {
        setOtpSuccess(`OTP sent! Your OTP is: ${response.data.otp} (for development)`);
      }
    } catch (error) {
      if (error.response) {
        const errorData = error.response.data;
        const newFieldErrors = {};

        // Helper to map backend keys to frontend state keys
        const keyMap = {
          'email': 'businessEmail',
          'businessEmail': 'businessEmail',
          'organization_name': 'organizationName',
          'organizationName': 'organizationName'
        };

        let hasFieldErrors = false;
        Object.keys(errorData).forEach(key => {
          const frontendKey = keyMap[key] || key;
          if (Array.isArray(errorData[key])) {
            newFieldErrors[frontendKey] = errorData[key][0];
            hasFieldErrors = true;
          } else if (typeof errorData[key] === 'string' && key !== 'error' && key !== 'message') {
            newFieldErrors[frontendKey] = errorData[key];
            hasFieldErrors = true;
          }
        });

        if (hasFieldErrors) {
          setFieldErrors(prev => ({ ...prev, ...newFieldErrors }));
        } else {
          setSignupError(errorData.message || errorData.error || 'Failed to send OTP.');
        }
      } else {
        setSignupError('Unable to connect to server. Please check if Django backend is running.');
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
      await axios.post(`${API_BASE_URL}/verify-otp/`, {
        email: businessEmail,
        otp: otp,
      });

      setEmailVerified(true);
      setOtpSuccess('Email verified successfully!');
      setFieldErrors(prev => ({ ...prev, otp: '' }));
      setOtpExpiresAtMs(null);
      setOtpExpired(false);
    } catch (error) {
      if (error.response) {
        setFieldErrors(prev => ({ ...prev, otp: error.response.data.error || 'Invalid OTP. Please try again.' }));
      } else {
        setFieldErrors(prev => ({ ...prev, otp: 'Unable to connect to server.' }));
      }
    } finally {
      setVerifyingOtp(false);
    }
  };

  // Handle Signup
  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupError('');
    setFieldErrors({});
    setSignupSuccess('');

    // Password strength validation
    if (!passwordRegex.test(password)) {
      setFieldErrors(prev => ({ ...prev, password: 'Password must be 6-12 characters and include uppercase, lowercase, number, and special character.' }));
      return;
    }

    // Check if email is verified
    if (!emailVerified) {
      setSignupError('Please verify your email first by entering the OTP.');
      return;
    }

    // Validate password confirmation
    if (password !== confirmPassword) {
      setFieldErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match' }));
      return;
    }

    // Plan validation
    if (!selectedPlanId) {
      setSignupError('Please select a subscription plan to continue.');
      return;
    }

    setSignupLoading(true);

    const registrationData = {
      full_name: `${firstName} ${lastName}`.trim(),
      email: businessEmail,
      organization_name: organizationName,
      password: password,
      plan_id: selectedPlanId,
      billing_cycle: billingCycle,
    };

    const selectedPlan = plans.find(p => p.id === selectedPlanId);

    if (selectedPlan && parseFloat(selectedPlan.base_price_monthly) >= 0) {
      // Handle Razorpay Payment for All Plans (including 1 INR verification fee for free plans)
      try {
        const orderRes = await axios.post(`${API_BASE_URL}/create-razorpay-order/`, { plan_id: selectedPlanId, billing_cycle: billingCycle });
        const { order_id, amount, currency, key_id } = orderRes.data;

        const options = {
          key: key_id,
          amount: amount,
          currency: currency,
          name: "VerifiHireAI",
          description: `Subscription for ${selectedPlan.name}`,
          order_id: order_id,
          handler: async function (response) {
            // Payment successful, proceed to register
            await submitRegistration({
              ...registrationData,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_order_id: response.razorpay_order_id,
              razorpay_signature: response.razorpay_signature
            });
          },
          prefill: {
            name: `${firstName} ${lastName}`.trim(),
            email: businessEmail,
          },
          theme: {
            color: "#7c3aed"
          },
          modal: {
            ondismiss: function() {
              setSignupLoading(false);
              setSignupError("Payment cancelled.");
            }
          }
        };

        const rzp = new window.Razorpay(options);
        rzp.on('payment.failed', function (response){
          setSignupError(`Payment failed: ${response.error.description}`);
          setSignupLoading(false);
        });
        rzp.open();
      } catch (err) {
        setSignupError("Failed to initialize payment. Please try again.");
        setSignupLoading(false);
      }
    } else {
      // Free plan -> Register directly
      await submitRegistration(registrationData);
    }
  };

  const submitRegistration = async (payload) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/register/`, payload);

      // Success - check if pending approval
      const isPending = response.data.pending_approval;
      if (isPending) {
        setSignupSuccess('✅ Registration submitted! Your company account is pending review by the platform administrator. You will receive an email once your account is approved.');
      } else {
        setSignupSuccess('Account created successfully! Redirecting to login...');
      }
      // Clear form
      setFirstName('');
      setLastName('');
      setBusinessEmail('');
      setOrganizationName('');
      setPassword('');
      setConfirmPassword('');
      setEmailVerified(false);
      setOtp('');
      setOtpSent(false);

      // Only auto-redirect if not pending approval
      if (!isPending) {
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }

    } catch (error) {
      // Handle error
      if (error.response) {
        // Server responded with error
        const errorData = error.response.data;
        const newFieldErrors = {};

        // Helper to map backend keys to frontend state keys
        const keyMap = {
          'email': 'businessEmail',
          'business_email': 'businessEmail',
          'full_name': 'fullName',
          'organization_name': 'organizationName',
          'organizationName': 'organizationName',
          'password': 'password',
          'confirm_password': 'confirmPassword',
          'otp': 'otp'
        };

        let hasFieldErrors = false;
        Object.keys(errorData).forEach(key => {
          const frontendKey = keyMap[key] || key;
          if (Array.isArray(errorData[key])) {
            newFieldErrors[frontendKey] = errorData[key][0];
            hasFieldErrors = true;
          } else if (typeof errorData[key] === 'string' && key !== 'error' && key !== 'message') {
            newFieldErrors[frontendKey] = errorData[key];
            hasFieldErrors = true;
          }
        });

        if (hasFieldErrors) {
          setFieldErrors(newFieldErrors);
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
          <h1 className="left-intro-title">Create your account</h1>
          <p className="left-intro-subtitle">
            AI-Powered Hiring, Built on Trust and Precision.<br />
            Sign up to manage assessments, view reports, and monitor candidate sessions.
          </p>
          <div className="left-intro-image-wrapper">
            <img
              src="/register-illustration.png"
              alt="Hiring Illustration"
              className="left-intro-image"
            />
          </div>
        </div>
      </div>

      {/* Right Side: Form */}
      <div className="auth-right-side">
        <div className="form-header-content" data-aos="fade-up">
          <h2 className="form-header-title">Sign up</h2>
          <p className="form-header-subtitle" style={{ marginBottom: '2.5rem' }}>Enter your account details</p>
        </div>

        <form className="auth-form" onSubmit={handleSignup} data-aos="fade-up" data-aos-delay="100">

          {signupSuccess && (
            <div className="auth-success-message" style={{ marginBottom: '1rem' }}>{signupSuccess}</div>
          )}

          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className={`auth-input-icon-wrapper ${firstNameFocused || firstName ? 'focused has-value' : ''}`} style={{ flex: 1 }}>
              <i className="fas fa-user auth-input-icon"></i>
              <input
                type="text"
                className="auth-input-with-icon"
                placeholder="First Name *"
                value={firstName}
                onChange={(e) => {
                  const value = e.target.value.replace(/[^a-zA-Z\s]/g, '');
                  setFirstName(value);
                }}
                onFocus={() => setFirstNameFocused(true)}
                onBlur={() => setFirstNameFocused(false)}
                required
                maxLength={50}
                disabled={signupLoading}
              />
              <label className="auth-floating-label">First Name *</label>
            </div>

            <div className={`auth-input-icon-wrapper ${lastNameFocused || lastName ? 'focused has-value' : ''}`} style={{ flex: 1 }}>
              <i className="fas fa-user auth-input-icon"></i>
              <input
                type="text"
                className="auth-input-with-icon"
                placeholder="Last Name *"
                value={lastName}
                onChange={(e) => {
                  const value = e.target.value.replace(/[^a-zA-Z\s]/g, '');
                  setLastName(value);
                }}
                onFocus={() => setLastNameFocused(true)}
                onBlur={() => setLastNameFocused(false)}
                required
                maxLength={50}
                disabled={signupLoading}
              />
              <label className="auth-floating-label">Last Name *</label>
            </div>
          </div>
          {(fieldErrors.firstName || fieldErrors.lastName || fieldErrors.fullName) && (
            <div className="field-error-text">{fieldErrors.firstName || fieldErrors.lastName || fieldErrors.fullName}</div>
          )}

          <div className={`auth-input-icon-wrapper ${businessEmailFocused || businessEmail ? 'focused has-value' : ''}`}>
            <i className="fas fa-envelope auth-input-icon"></i>
            <input
              type="email"
              className="auth-input-with-icon"
              placeholder="Business Email *"
              value={businessEmail}
              onChange={(e) => {
                const value = e.target.value;
                setBusinessEmail(value);
                if (fieldErrors.businessEmail) {
                  setFieldErrors(prev => {
                    const newState = { ...prev };
                    delete newState.businessEmail;
                    return newState;
                  });
                }
                if (emailVerified) {
                  setEmailVerified(false);
                  setOtpSent(false);
                  setOtp('');
                }
              }}
              onFocus={() => setBusinessEmailFocused(true)}
              onBlur={() => {
                setBusinessEmailFocused(false);
                if (businessEmail) {
                  const freeDomains = [
                    'gmail.com', 'googlemail.com', 'yahoo.com', 'yahoo.in', 'ymail.com', 'rocketmail.com',
                    'outlook.com', 'hotmail.com', 'live.com', 'msn.com', 'icloud.com', 'me.com', 'mac.com',
                    'aol.com', 'proton.me', 'protonmail.com', 'zoho.com', 'mail.com', 'email.com', 'post.com', 'usa.com',
                    'yandex.com', 'gmx.com', 'gmx.net', 'fastmail.com', 'tutanota.com', 'tuta.com'
                  ];
                  const domain = businessEmail.split('@')[1]?.toLowerCase();
                  if (freeDomains.includes(domain)) {
                    setFieldErrors(prev => ({ ...prev, businessEmail: 'Please use your business email address.' }));
                  }
                }
              }}
              required
              maxLength={100}
              disabled={signupLoading}
              style={emailVerified ? { backgroundColor: '#f0fdf4', borderColor: '#16a34a' } : {}}
            />
            <label className="auth-floating-label">Business Email *</label>
          </div>
          {fieldErrors.businessEmail && (
            <div className="field-error-text">{fieldErrors.businessEmail}</div>
          )}

          {/* Email Verification Section */}
          {businessEmail && !emailVerified && (
            <div className="otp-verification-container" style={{
              marginBottom: '1.5rem',
              padding: '1.25rem',
              border: '1px solid #edf2f7',
              borderRadius: '12px',
              backgroundColor: '#f8fafc'
            }}>
              <div style={{ marginBottom: '0.75rem', fontSize: '14px', fontWeight: '600', color: '#2d3748', textAlign: 'center' }}>
                Verify your email
              </div>

              {fieldErrors.otp && (
                <div className="field-error-text" style={{ marginBottom: '0.5rem', textAlign: 'center' }}>
                  {fieldErrors.otp}
                </div>
              )}

              {!otpSent ? (
                <button
                  type="button"
                  className="auth-primary-btn"
                  onClick={handleSendOtp}
                  disabled={sendingOtp || !businessEmail}
                  style={{ width: '100%', padding: '0.75rem' }}
                >
                  {sendingOtp ? 'Sending OTP...' : 'Send OTP'}
                </button>
              ) : (
                <div>
                  <div className={`auth-input-icon-wrapper ${otpFocused || otp ? 'focused has-value' : ''}`} style={{ marginBottom: '0.5rem' }}>
                    <i className="fas fa-key auth-input-icon"></i>
                    <input
                      type="text"
                      className="auth-input-with-icon"
                      placeholder="6-digit OTP"
                      value={otp}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                        setOtp(value);
                        setFieldErrors(prev => ({ ...prev, otp: '' }));
                      }}
                      onFocus={() => setOtpFocused(true)}
                      onBlur={() => setOtpFocused(false)}
                      maxLength={6}
                      disabled={verifyingOtp || emailVerified}
                      style={{ textAlign: 'center', fontSize: '1.25rem', letterSpacing: '4px' }}
                    />
                    <label className="auth-floating-label">Enter 6-digit OTP</label>
                  </div>
                  <OtpCountdown
                    expiresAtMs={otpExpiresAtMs}
                    onExpire={() => setOtpExpired(true)}
                  />
                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem' }}>
                    <button
                      type="button"
                      className="auth-primary-btn"
                      onClick={handleVerifyOtp}
                      disabled={verifyingOtp || otp.length !== 6 || emailVerified || otpExpired}
                      style={{ flex: 1, padding: '0.75rem' }}
                    >
                      {verifyingOtp ? 'Verifying...' : 'Verify OTP'}
                    </button>
                    <button
                      type="button"
                      className="auth-secondary-btn"
                      onClick={handleSendOtp}
                      disabled={isResendLocked}
                      style={{ padding: '0.75rem 1rem' }}
                    >
                      {sendingOtp ? '...' : 'Resend'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {emailVerified && (
            <div className="registration-details-section" data-aos="fade-up">
              <div className={`auth-input-icon-wrapper ${organizationNameFocused || organizationName ? 'focused has-value' : ''}`}>
                <i className="fas fa-building auth-input-icon"></i>
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
                  disabled={signupLoading || !emailVerified}
                />
                <label className="auth-floating-label">Organization Name *</label>
              </div>
              {fieldErrors.organizationName && (
                <div className="field-error-text">{fieldErrors.organizationName}</div>
              )}

              <div className={`auth-input-icon-wrapper ${selectedPlanId ? 'focused has-value' : ''}`} style={{ marginTop: '1rem' }}>
                <i className="fas fa-layer-group auth-input-icon"></i>
                <select
                  className="auth-input-with-icon"
                  value={selectedPlanId ? `${selectedPlanId}-${billingCycle}` : ''}
                  onChange={(e) => {
                    const [pId, cycle] = e.target.value.split('-');
                    setSelectedPlanId(Number(pId));
                    setBillingCycle(cycle || 'monthly');
                  }}
                  required
                  disabled={signupLoading || plansLoading || !emailVerified}
                  style={{ appearance: 'none', cursor: 'pointer' }}
                >
                  <option value="" disabled>Select a Plan *</option>
                  {plans.filter(p => parseFloat(p.base_price_monthly) >= 0 && !['enterprise', 'custom'].includes(p.name.toLowerCase())).map(plan => {
                    const basePrice = parseFloat(plan.base_price_monthly);
                    if (basePrice === 0) {
                      return <option key={`${plan.id}-monthly`} value={`${plan.id}-monthly`}>{plan.name} - Free</option>;
                    }
                    
                    const price6Mo = basePrice * (1 - (parseFloat(plan.discount_6_months) || 0) / 100);
                    const price12Mo = basePrice * (1 - (parseFloat(plan.discount_12_months) || 0) / 100);
                    
                    return (
                      <Fragment key={plan.id}>
                        <option value={`${plan.id}-monthly`}>{plan.name} - ₹{basePrice.toFixed(2)}/mo (Monthly)</option>
                        <option value={`${plan.id}-biannual`}>{plan.name} - ₹{price6Mo.toFixed(2)}/mo (6 Months)</option>
                        <option value={`${plan.id}-annual`}>{plan.name} - ₹{price12Mo.toFixed(2)}/mo (Annually)</option>
                      </Fragment>
                    );
                  })}
                </select>
                <i className="fas fa-chevron-down" style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af', pointerEvents: 'none' }}></i>
                <label className="auth-floating-label">Subscription Plan *</label>
              </div>
              {fieldErrors.plan_id && (
                <div className="field-error-text">{fieldErrors.plan_id}</div>
              )}
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
                minLength={6}
                maxLength={12}
                required
                disabled={signupLoading || !emailVerified}
                onFocus={() => setPasswordFocused(true)}
                onBlur={() => setPasswordFocused(false)}
                style={{ paddingRight: '3rem' }}
              />
              <label className="auth-floating-label">Password *</label>
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                disabled={signupLoading || !emailVerified}
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
            <div className="field-error-text">{fieldErrors.password}</div>
          )}

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
            <div style={{ position: 'relative' }}>
              <input
                type={showConfirmPassword ? "text" : "password"}
                className="auth-input-with-icon"
                placeholder="Confirm Password *"
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
                minLength={6}
                maxLength={12}
                required
                disabled={signupLoading || !emailVerified}
                onFocus={() => setConfirmPasswordFocused(true)}
                onBlur={() => setConfirmPasswordFocused(false)}
                style={{ paddingRight: '3rem' }}
              />
              <label className="auth-floating-label">Confirm Password *</label>
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                disabled={signupLoading || !emailVerified}
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
          {(fieldErrors.confirmPassword || (confirmPassword && password !== confirmPassword)) && (
            <div className="field-error-text" style={{ color: '#e53e3e', fontSize: '0.8rem', marginTop: '-0.75rem', marginBottom: '1rem' }}>
              {fieldErrors.confirmPassword || 'Passwords do not match'}
            </div>
          )}

          <button
            type="submit"
            className="auth-primary-btn"
            disabled={
              signupLoading ||
              !firstName ||
              !lastName ||
              !businessEmail ||
              !organizationName ||
              !password ||
              !confirmPassword ||
              password !== confirmPassword ||
              !passwordRegex.test(password) ||
              !emailVerified ||
              !selectedPlanId
            }
            style={{
              width: '100%',
              padding: '0.875rem',
              fontSize: '1rem',
              fontWeight: '600',
              marginTop: '1rem'
            }}
          >
            {signupLoading ? 'Creating account...' : 'REGISTER'}
          </button>
          {signupError && (
            <div className="field-error-text" style={{ marginTop: '0.75rem', textAlign: 'center', marginBottom: 0 }}>{signupError}</div>
          )}

          <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
            <p style={{ color: '#718096', fontSize: '0.9rem' }}>
              Already have an account?{' '}
              <Link to="/login" style={{ color: '#7c3aed', fontWeight: '700', textDecoration: 'none' }}>
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Signup;