import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ProfileDropdown from './ProfileDropdown';
import { API_BASE_URL } from '../apiConfig';
import '../styles/Header.css';

function Header() {
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState('');
  const [studentPoints, setStudentPoints] = useState(0);
  const [studentRank, setStudentRank] = useState(null);
  const [companyCredits, setCompanyCredits] = useState(0);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const u = JSON.parse(storedUser);
        setUserRole(u.role || '');
      } catch (e) {}
    }
  }, []);

  useEffect(() => {
    if (userRole === 'student') {
      const fetchPoints = async () => {
        try {
          const token = localStorage.getItem('token');
          const res = await axios.get(`${API_BASE_URL}/students/points/`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setStudentPoints(res.data.points || 0);
          setStudentRank(res.data.rank || null);
        } catch (err) {}
      };
      fetchPoints();
    }
    if (userRole && userRole !== 'student' && userRole !== 'interviewer') {
      const fetchCredits = async () => {
        try {
          const token = localStorage.getItem('token');
          const res = await axios.get(`${API_BASE_URL}/students/wallet/`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setCompanyCredits(res.data.ai_credits || 0);
        } catch (err) {}
      };
      fetchCredits();

      const handleCreditsUpdated = () => {
        fetchCredits();
      };
      window.addEventListener('vh_credits_updated', handleCreditsUpdated);
      return () => {
        window.removeEventListener('vh_credits_updated', handleCreditsUpdated);
      };
    }
  }, [userRole]);

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
          {userRole === 'student' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginRight: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: 'linear-gradient(135deg, #eef2ff, #e0e7ff)', padding: '5px 12px', borderRadius: '8px', border: '1px solid #c7d2fe' }}>
                <span style={{ fontSize: '0.85rem' }}>⚡</span>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#4338ca' }}>{studentPoints} pts</span>
              </div>
              {studentRank && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: 'linear-gradient(135deg, #fef3c7, #fde68a)', padding: '5px 12px', borderRadius: '8px', border: '1px solid #fbbf24' }}>
                  <span style={{ fontSize: '0.85rem' }}>🏆</span>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#92400e' }}>#{studentRank}</span>
                </div>
              )}
            </div>
          )}
          {userRole && userRole !== 'student' && userRole !== 'interviewer' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', background: 'linear-gradient(135deg, #eef2ff, #e0e7ff)', padding: '5px 12px', borderRadius: '8px', border: '1px solid #c7d2fe', marginRight: '1rem' }}>
              <span style={{ fontSize: '0.85rem' }}>⚡</span>
              <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#4338ca' }}>{companyCredits.toLocaleString()} credits</span>
            </div>
          )}
          <ProfileDropdown />
        </div>
      </div>
    </header>
  );
}

export default Header;
