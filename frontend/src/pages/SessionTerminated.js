import React from 'react';
import { useSearchParams } from 'react-router-dom';

export default function SessionTerminated() {
  const [searchParams] = useSearchParams();
  const isTerminalViolation = searchParams.get('reason') === 'terminal';

  return (
    <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#f8fafc', padding: 24 }}>
      <div style={{ 
        maxWidth: 560, 
        textAlign: 'center', 
        background: '#fff', 
        borderRadius: 12, 
        border: '1px solid #e2e8f0', 
        padding: 28, 
        boxShadow: '0 8px 30px rgba(0,0,0,0.08)' 
      }}>
        <h2 style={{ marginTop: 0, color: '#dc2626' }}>Session Terminated</h2>
        <p style={{ color: '#475569', fontSize: '1.1rem', marginBottom: 16 }}>
          {isTerminalViolation
            ? 'Your exam has been terminated because the Secure Agent terminal was closed 3 times during the exam.'
            : 'Your exam has been terminated due to a policy violation.'}
        </p>
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '12px 16px', borderRadius: 8 }}>
          <p style={{ color: '#991b1b', margin: 0, fontWeight: 500 }}>
            Access to this assessment has been permanently revoked.
          </p>
        </div>
      </div>
    </div>
  );
}
