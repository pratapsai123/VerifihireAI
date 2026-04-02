import React from 'react';

export const ConnectionOverlay = ({ status }) => {
  if (status === 'Connected') return null;

  let displayMessage = "Connecting...";
  
  switch (status) {
    case 'Connecting':
      displayMessage = "Connecting...";
      break;
    case 'Reconnecting':
      displayMessage = "Disconnected. Reconnecting...";
      break;
    case 'Disconnected':
      displayMessage = "Disconnected";
      break;
    default:
      displayMessage = "Connecting...";
  }

  return (
    <div className="connection-overlay">
      <i className="fas fa-spinner spinner"></i>
      <h3>{displayMessage}</h3>
      <p>Waiting for connection...</p>
    </div>
  );
};

export default ConnectionOverlay;
