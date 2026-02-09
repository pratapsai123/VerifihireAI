import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Swallow noisy ResizeObserver loop errors to avoid user-facing popups
const ignoreROError = (event) => {
  const msg = event?.message || '';
  if (msg.includes('ResizeObserver loop') || msg.includes('ResizeObserver loop completed')) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
};
window.addEventListener('error', ignoreROError, { capture: true });
window.onerror = (message) => {
  if (typeof message === 'string' && (message.includes('ResizeObserver loop') || message.includes('ResizeObserver loop completed'))) {
    return true; // swallow
  }
  return false;
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
