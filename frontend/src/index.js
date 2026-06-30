import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';

// Swallow noisy ResizeObserver loop errors to avoid user-facing popups
const isResizeObserverError = (msg) => {
  return (
    typeof msg === 'string' &&
    (msg.includes('ResizeObserver loop') ||
     msg.includes('ResizeObserver loop completed') ||
     msg.includes('ResizeObserver loop limit exceeded'))
  );
};

window.addEventListener('error', (event) => {
  if (isResizeObserverError(event.message)) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
}, { capture: true });

window.addEventListener('unhandledrejection', (event) => {
  if (isResizeObserverError(event.reason?.message)) {
    event.stopImmediatePropagation();
    event.preventDefault();
  }
}, { capture: true });

window.onerror = (message) => {
  if (isResizeObserverError(message)) {
    return true; // swallow
  }
  return false;
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
