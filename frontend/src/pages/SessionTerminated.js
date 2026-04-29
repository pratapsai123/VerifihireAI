import React from 'react';

export default function SessionTerminated() {
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
        <h2 style={{ marginTop: 0, color: '#0f172a' }}>Session Terminated</h2>
        <p style={{ color: '#475569', marginBottom: 0 }}>Exam terminated due to policy violation</p>
      </div>
    </div>
  );
}
