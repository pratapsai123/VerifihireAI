import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import '../styles/MainHeader.css';
function MainHeader() {
  const location = useLocation();
  const navigate = useNavigate();
  const isHomePage = location.pathname === '/';

  const [isFeaturesHovered, setIsFeaturesHovered] = useState(false);
  const [isFeaturesClicked, setIsFeaturesClicked] = useState(false);

  const handleFeaturesMouseEnter = () => setIsFeaturesHovered(true);
  const handleFeaturesMouseLeave = () => setIsFeaturesHovered(false);
  const handleFeaturesClick = () => setIsFeaturesClicked(true);
  const handleFeaturesDoubleClick = () => setIsFeaturesClicked(false);

  const showFeaturesMenu = isFeaturesHovered || isFeaturesClicked;

  const scrollToSection = (e, sectionId) => {
    e.preventDefault();
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };


  const goHome = () => {
    navigate('/');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const navLinkStyle = {
    color: '#CCD6F6',
    fontWeight: 600,
    textDecoration: 'none',
    fontSize: '0.81rem',
    transition: 'all 0.3s ease',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  };

  return (
    <header style={{
      background: 'rgba(255, 255, 255, 0.85)',
      backdropFilter: 'blur(15px)',
      WebkitBackdropFilter: 'blur(15px)',
      borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      width: '100%',
    }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '4px 2%',
        width: '100%',
        margin: '0 auto',
        boxSizing: 'border-box',
      }}>
        {/* Left: Logo */}
        <button
          type="button"
          onClick={goHome}
          className="brand-logo-group"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: 'none',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            textAlign: 'left'
          }}
        >
          <img src="/auth-logo-v7.png" alt="VerifiHireAI Logo" className="brand-logo-img" style={{ height: '44px', width: 'auto', display: 'block' }} />
          <div className="brand-text-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center', lineHeight: '1.1' }}>
            <span className="brand-name-text" style={{ fontSize: '1.4rem', fontWeight: '600', color: '#c69214', fontFamily: 'Georgia, serif', letterSpacing: '0.2px', margin: 0 }}>VerifiHireAI</span>
            <p className="brand-tagline" style={{ margin: '2px 0 0 0', fontSize: '0.75rem', color: '#475569', fontWeight: '500', fontFamily: 'sans-serif' }}>Trust in Every Hire</p>
          </div>
        </button>

        {/* Center: Features Dropdown */}
        <div className="main-header-nav-center">
          <div
            className={`features-dropdown-container ${showFeaturesMenu ? 'active' : ''}`}
            onMouseEnter={handleFeaturesMouseEnter}
            onMouseLeave={handleFeaturesMouseLeave}
            onClick={handleFeaturesClick}
            onDoubleClick={handleFeaturesDoubleClick}
          >
            <span className="features-label-btn">Features</span>
            <div className={`features-menu ${showFeaturesMenu ? 'show' : ''}`}>
              <Link to="/features/ai-assessments" className="feature-menu-item feature-ai">
                AI Assessments & AI Interview
              </Link>
              <Link to="/features/live-interview" className="feature-menu-item feature-live">
                Live Interview
              </Link>
              <Link to="/features/customized-assessment" className="feature-menu-item feature-custom">
                Customized Assessment
              </Link>
              <Link to="/features/coding-assessment" className="feature-menu-item feature-coding">
                Coding Assessment
              </Link>
            </div>
          </div>

          <Link
            to="/pricing"
            className="pricing-label-btn"
          >
            Pricing
          </Link>
        </div>

        {/* Right: Login Button */}
        <Link
          to="/login"
          className="login-btn-custom"
        >
          Login
        </Link>
      </nav>
    </header>
  );
}

export default MainHeader;

