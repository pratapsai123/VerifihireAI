import React, { useEffect, useMemo, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

// ProfileDropdown Styles - All in one file
const profileStyles = {
  profileMenuContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    color: '#fff',
    fontWeight: 'bold',
  },
  profileAvatar: {
    width: '28px',
    height: '28px',
    borderRadius: '50%',
    backgroundColor: '#e0e0e0',
    color: '#1d2686',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: '12px',
    textTransform: 'uppercase',
  },
  profileDropdown: {
    position: 'absolute',
    top: '100%',
    right: 0,
    background: '#fff',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
    borderRadius: '8px',
    overflow: 'hidden',
    minWidth: '200px',
    display: 'none',
    zIndex: 1100,
    marginTop: '8px',
  },
  profileDropdownOpen: {
    position: 'absolute',
    top: '100%',
    right: 0,
    background: '#fff',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.15)',
    borderRadius: '8px',
    overflow: 'hidden',
    minWidth: '200px',
    display: 'block',
    zIndex: 1100,
    marginTop: '8px',
  },
  profileDropdownHeader: {
    padding: '8px 12px',
    background: '#f0f2f5',
    borderBottom: '1px solid #eee',
    fontWeight: 500,
    color: '#333',
    fontSize: '12px',
  },
  profileDropdownHeaderSpan: {
    fontSize: '12px',
    display: 'block',
    fontWeight: 500,
  },
  profileDropdownHeaderSmall: {
    color: '#333',
    fontWeight: 500,
    fontSize: '12px',
    display: 'block',
  },
  profileDropdownItem: {
    padding: '8px 12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    textDecoration: 'none',
    color: '#333',
    fontWeight: 500,
    fontSize: '12px',
    transition: 'background-color 0.2s',
    background: 'none',
    border: 'none',
    width: '100%',
    textAlign: 'left',
    cursor: 'pointer',
  },
  profileDropdownItemSvg: {
    flexShrink: 0,
    width: '16px',
    height: '16px',
  },
};

function ProfileDropdown() {
  const navigate = useNavigate();
  const [user, setUser] = useState({
    first_name: '',
    last_name: '',
    email: '',
    organization_name: '',
    role: '',
  });
  const [profileOpen, setProfileOpen] = useState(false);
  const profileMenuRef = useRef(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        // ignore parse errors
      }
    }
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setProfileOpen(false);
      }
    };

    if (profileOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [profileOpen]);

  const handleToggleDropdown = (e) => {
    e.stopPropagation();
    setProfileOpen(prev => !prev);
  };

  const formatRole = (value) => {
    if (!value) return '';
    const text = String(value).replace(/[_-]+/g, ' ').trim();
    if (!text) return '';
    return text.replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const initials = `${(user.first_name || '').charAt(0)}${(user.last_name || '').charAt(0)}`.toUpperCase() || 'G';

  const canSeeTeamMembers = useMemo(() => {
    const r = String(user.role || '').toLowerCase();
    return r === 'company_admin' || r === 'hr_manager' || r === 'application_admin';
  }, [user.role]);

  const handleLogout = (e) => {
    e.preventDefault();
    try {
      localStorage.removeItem('authToken');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    } catch {
      // ignore
    }
    navigate('/login');
  };

  return (
    <>
      {/* Inline styles for hover states */}
      <style>{`
        .profile-dropdown-item:hover {
          background-color: #f5f5f5;
        }
      `}</style>
      <div
        ref={profileMenuRef}
        style={profileStyles.profileMenuContainer}
        onMouseEnter={() => {
          // Open on hover for better UX
          if (!profileOpen) {
            setProfileOpen(true);
          }
        }}
        onClick={handleToggleDropdown}
      >
        <div style={profileStyles.profileAvatar}>{initials || 'G'}</div>
        <div style={profileOpen ? profileStyles.profileDropdownOpen : profileStyles.profileDropdown}>
          <div style={profileStyles.profileDropdownHeader}>
            <span style={profileStyles.profileDropdownHeaderSpan}>{user.first_name || 'Guest'}</span>
            <small style={profileStyles.profileDropdownHeaderSmall}>{user.email || 'Not Logged In'}</small>
            {user.role ? <small style={profileStyles.profileDropdownHeaderSmall}>{formatRole(user.role)}</small> : null}
            {user.organization_name ? <small style={profileStyles.profileDropdownHeaderSmall}>{user.organization_name}</small> : null}
          </div>
          <a href="/company-profile/" style={profileStyles.profileDropdownItem}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={profileStyles.profileDropdownItemSvg}>
              <path d="M8 1L2 4v3c0 4.418 3.582 8 8 8s8-3.582 8-8V4L8 1z" fill="#2563eb"/>
              <path d="M8 1v14c4.418 0 8-3.582 8-8V4L8 1z" fill="#1d4ed8"/>
            </svg>
            Company Profile
          </a>
          <button type="button" style={profileStyles.profileDropdownItem}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={profileStyles.profileDropdownItemSvg}>
              <rect x="2" y="3" width="12" height="10" rx="1" fill="#2563eb"/>
              <path d="M5 7h6M5 10h4" stroke="#fff" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Plan Usage
          </button>
          <a href="/setting/" style={profileStyles.profileDropdownItem}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={profileStyles.profileDropdownItemSvg}>
              <circle cx="8" cy="8" r="2" fill="#2563eb"/>
              <path d="M8 1v2M8 13v2M15 8h-2M3 8H1M13.364 2.636l-1.414 1.414M4.05 11.95l-1.414 1.414M13.364 13.364l-1.414-1.414M4.05 4.05L2.636 2.636" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Setting Options
          </a>
          <a href="/my-account/" style={profileStyles.profileDropdownItem}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={profileStyles.profileDropdownItemSvg}>
              <circle cx="8" cy="5" r="2.5" fill="#2563eb"/>
              <path d="M3 13.5c0-2.761 2.239-5 5-5s5 2.239 5 5" stroke="#2563eb" strokeWidth="1.5" fill="none"/>
            </svg>
            My Account
          </a>

          {canSeeTeamMembers ? (
            <a href="/team-members" style={profileStyles.profileDropdownItem}>
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={profileStyles.profileDropdownItemSvg}>
                <path d="M5.5 7a2 2 0 10-4 0 2 2 0 004 0zM14 7a2 2 0 10-4 0 2 2 0 004 0zM9.75 8.5a2.25 2.25 0 10-3.5 0" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M1.5 14c0-1.6 1.5-3 3-3s3 1.4 3 3M9.5 14c0-1.6 1.5-3 3-3s3 1.4 3 3M5.5 14c0-1.9 1.8-3.5 3.5-3.5S12.5 12.1 12.5 14" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Team Members
            </a>
          ) : null}

          <a href="/logout/" onClick={handleLogout} style={profileStyles.profileDropdownItem}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style={profileStyles.profileDropdownItemSvg}>
              <path d="M6 14H3a1 1 0 01-1-1V3a1 1 0 011-1h3M10 12l4-4-4-4M14 8H6" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
            </svg>
            Logout
          </a>
        </div>
      </div>
    </>
  );
}

export default ProfileDropdown;

