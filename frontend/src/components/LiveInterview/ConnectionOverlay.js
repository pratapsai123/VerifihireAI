import React from 'react';

export const ConnectionOverlay = ({ status, statusText }) => {
  if (status === 'Connected') return null;

  return (
    <div className="connection-overlay">
      <i className="fas fa-spinner spinner"></i>
      <h3>{statusText || status}</h3>
      {status !== 'Reconnecting...' && status !== 'Connecting...' && status !== 'Error' && (
        <p>Waiting for connection...</p>
      )}
    </div>
  );
};

export default ConnectionOverlay;
