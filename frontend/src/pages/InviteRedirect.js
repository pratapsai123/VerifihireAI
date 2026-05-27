import React, { useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { logCandidateActivity } from '../utils/activityLogger';
import { checkInvitationPublicAccess, isInvitationAlreadySubmitted } from '../utils/invitationAccess';

const TARGET_ROUTE_MAP = {
  assessment: (token) => `/take-assessment/${token}`,
  interview: (token) => `/interview-start/${token}`,
  ai_assessment: (token) => `/take-ai-assessment/${token}`,
  ai_interview: (token) => `/ai-interview-session/${token}`,
};

export default function InviteRedirect({ type }) {
  const { token } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!token) return;

    let cancelled = false;

    const run = async () => {
      logCandidateActivity(token, 'Opened Link', `Assessment type: ${type}`);

      const searchParams = new URLSearchParams(location.search);
      const name = searchParams.get('name');
      const email = searchParams.get('email');

      const access = await checkInvitationPublicAccess(token);
      if (cancelled) return;

      const appendParams = (baseUrl) => {
        let url = baseUrl;
        if (name) url += `${url.includes('?') ? '&' : '?'}name=${encodeURIComponent(name)}`;
        if (email) url += `${url.includes('?') ? '&' : '?'}email=${encodeURIComponent(email)}`;
        return url;
      };

      if (isInvitationAlreadySubmitted(access)) {
        const builder = TARGET_ROUTE_MAP[type] || TARGET_ROUTE_MAP.assessment;
        navigate(appendParams(builder(token)), { replace: true });
        return;
      }

      // ── DEV BYPASS ────────────────────────────────────────────────
      // When REACT_APP_SKIP_PRECHECK=true, jump straight to the target
      // route. To re-enable the precheck flow, set the env var to false
      // (or remove this block entirely).
      if (false /* TEMP BYPASS — change to false to re-enable precheck */) {
        const builder = TARGET_ROUTE_MAP[type] || TARGET_ROUTE_MAP.assessment;
        console.warn('[InviteRedirect] Skipping precheck (TEMP BYPASS)');
        navigate(appendParams(builder(token)), { replace: true });
        return;
      }

      let redirectUrl = `/precheck/${token}?type=${encodeURIComponent(type)}`;
      if (name) redirectUrl += `&name=${encodeURIComponent(name)}`;
      if (email) redirectUrl += `&email=${encodeURIComponent(email)}`;

      navigate(redirectUrl, { replace: true });
    };

    run();
    return () => {
      cancelled = true;
    };
  }, [navigate, token, type, location.search]);
  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', color: '#334155' }}>
      Redirecting to secure precheck...
    </div>
  );
}
