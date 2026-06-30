import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import '../styles/ThankYou.css';

const ThankYou = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const message = searchParams.get('message') || 'Your interview has been completed successfully.';

  return (
    <div className="thank-you-page">
      <div className="thank-you-card">
        <div className="success-icon">
          <i className="fas fa-check-circle"></i>
        </div>
        <h1 className="thank-you-title">Thank You!</h1>
        <p className="thank-you-message">{message}</p>
        <div className="thank-you-footer">
          <p>We have received your feedback and will be in touch soon.</p>
          <button
            className="home-button"
            onClick={() => window.close()}
          >
            Close Window
          </button>
        </div>
      </div>
      <div className="background-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
      </div>
    </div>
  );
};

export default ThankYou;
