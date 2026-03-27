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
          <span className="vh-header__logo" onClick={handleLogoClick}>
            VerifiHire<span className="vh-header__logo-ai">AI</span>
          </span>
        </div>
        <div className="vh-header__right">
          <ProfileDropdown />
        </div>
      </div>
    </header>
  );
}

export default Header;
