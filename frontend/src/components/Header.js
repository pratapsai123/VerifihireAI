import React from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileDropdown from './ProfileDropdown';
import '../styles/Header.css';

function Header() {
  const navigate = useNavigate();

  const handleLogoClick = () => {
    navigate('/dashboard');
  };

  return (
    <header className="vh-header">
      <div className="vh-header__container">
        <div className="vh-header__left">
          <div className="vh-header__logo" onClick={handleLogoClick} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer' }}>
            <img src="/auth-logo-v7.png" alt="VerifiHireAI" style={{ height: '38px', width: 'auto' }} />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '1.3rem', fontWeight: 600, color: '#d19a1d', fontFamily: 'serif', lineHeight: 1.1 }}>VerifiHireAI</span>
              <span style={{ fontSize: '0.65rem', color: '#64748b', letterSpacing: '0.2px' }}>Trust in Every Hire</span>
            </div>
          </div>
        </div>
        <div className="vh-header__right">
          <ProfileDropdown />
        </div>
      </div>
    </header>
  );
}

export default Header;
