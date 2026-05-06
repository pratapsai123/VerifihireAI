import React, { useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { logCandidateActivity } from '../utils/activityLogger';

export default function InviteRedirect({ type }) {
  const { token } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!token) return;
    logCandidateActivity(token, 'Opened Link', `Assessment type: ${type}`);
    
    // Preserve original query parameters (name, email) from the URL
    const searchParams = new URLSearchParams(location.search);
    const name = searchParams.get('name');
    const email = searchParams.get('email');
    
    console.log('InviteRedirect - Original URL:', window.location.href);
    console.log('InviteRedirect - Parsed params:', { name, email, type });
    
    // Build redirect URL with type and preserved params
    let redirectUrl = `/precheck/${token}?type=${encodeURIComponent(type)}`;
    if (name) redirectUrl += `&name=${encodeURIComponent(name)}`;
    if (email) redirectUrl += `&email=${encodeURIComponent(email)}`;
    
    console.log('InviteRedirect - Redirecting to:', redirectUrl);
    
    navigate(redirectUrl, { replace: true });
  }, [navigate, token, type, location.search]);
    // Live interviews skip precheck and go directly to the interview page
    if (type === 'interview' || type === 'live_interview') {
      navigate(`/live-interview?token=${token}`, { replace: true });
    } else {
      navigate(`/precheck/${token}?type=${encodeURIComponent(type)}`, { replace: true });
    }
  }, [navigate, token, type]);

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', color: '#334155' }}>
      Redirecting to secure precheck...
    </div>
  );
}
