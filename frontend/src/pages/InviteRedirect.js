import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { logCandidateActivity } from '../utils/activityLogger';

export default function InviteRedirect({ type }) {
  const { token } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) return;
    logCandidateActivity(token, 'Opened Link', `Assessment type: ${type}`);
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
