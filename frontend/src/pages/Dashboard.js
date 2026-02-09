import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import '../styles/Dashboard.css';

// Dashboard component for VerifiHireAI
function Dashboard() {
  const navigate = useNavigate();
  const [showNewAssignment, setShowNewAssignment] = useState(false);

  return (
    <div className="dashboard-container">

      {/* Header */}
      <Header />

      {/* Main Content - Cards */}
      <div className="page-container">
        <div className="cards-grid">
          {/* Card 1 - Split into two sections */}
          <div className="card-wrapper">
            <h3 className="card-title-above">AI-Powered Assessment</h3>
            <div className="dashboard-card card-split">
              <div className="card-number-badge">01</div>
              <div className="split-container">
                <div
                  className="split-section split-left"
                  // Navigation disabled for now; functionality to be added later
                  style={{ cursor: 'default' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="split-icon">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  </svg>
                  <span className="split-text">Assessments</span>
                </div>
                <div className="split-divider"></div>
                <div
                  className="split-section split-right"
                  onClick={() => navigate('/coding')}
                  style={{ cursor: 'pointer' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="split-icon">
                    <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  </svg>
                  <span className="split-text">Coding</span>
                </div>
              </div>
            </div>
          </div>

          {/* Card 2 - Split into two sections */}
          <div className="card-wrapper">
            <h3 className="card-title-above">Custom Assessment</h3>
            <div className="dashboard-card card-split">
              <div className="card-number-badge">02</div>
              <div className="split-container">
                <div 
                  className="split-section split-left"
                  onClick={() => navigate('/custom-assessment')}
                  style={{ cursor: 'pointer' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="split-icon">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  </svg>
                  <span className="split-text">Question Cart</span>
                </div>
                <div className="split-divider"></div>
                <div
                  className="split-section split-right"
                  onClick={() => navigate('/coding')}
                  style={{ cursor: 'pointer' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="split-icon">
                    <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  </svg>
                  <span className="split-text">Coding</span>
                </div>
              </div>
            </div>
          </div>

          {/* Card 3 */}
          <div className="card-wrapper">
            <h3 className="card-title-above">AI-Interview</h3>
            <div className="dashboard-card">
              <div className="card-number-badge">03</div>
              <p className="card-description">
                Conduct intelligent interviews powered by AI that analyze responses, assess communication skills, and provide detailed insights.
              </p>
            </div>
          </div>

          {/* Card 4 */}
          <div className="card-wrapper">
            <h3 className="card-title-above">Interview</h3>
            <div className="dashboard-card">
              <div className="card-number-badge">04</div>
              <p className="card-description">
                Schedule and manage traditional interviews with candidates, track progress, and maintain comprehensive interview records.
              </p>
            </div>
          </div>

          {/* Card 5 */}
          <div className="card-wrapper">
            <h3 className="card-title-above">Results</h3>
            <div
              className="dashboard-card"
              onClick={() => navigate('/results')}
              style={{ cursor: 'pointer' }}
            >
              <div className="card-number-badge">05</div>
              <p className="card-description">
                View results overview (Selected / Rejected) for submitted assessments.
              </p>
            </div>
          </div>

          {/* Card 6 - Split into two sections (Candidates & Assessments) */}
          <div className="card-wrapper">
            <h3 className="card-title-above">Candidates</h3>
            <div className="dashboard-card card-split">
              <div className="card-number-badge">06</div>
              <div className="split-container">
                <div
                  className="split-section split-left"
                  onClick={() => navigate('/candidates')}
                  style={{ cursor: 'pointer' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="split-icon">
                    <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4zm0 2c-3.33 0-6 1.34-6 3v1h12v-1c0-1.66-2.67-3-6-3z" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  </svg>
                  <span className="split-text">Candidates</span>
                </div>
                <div className="split-divider"></div>
                <div
                  className="split-section split-right"
                  onClick={() => navigate('/assessments')}
                  style={{ cursor: 'pointer' }}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="split-icon">
                    <path d="M9 11h6M9 15h4m6 4H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h8l6 6v8a2 2 0 0 1-2 2zM13 3v6h6" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                  </svg>
                  <span className="split-text">Assessments</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* New Assignment Modal */}
      {showNewAssignment && (
        <div className="modal-container">
          <div className="modal-backdrop" onClick={() => setShowNewAssignment(false)} />
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">New Assignment</h2>
              <button
                onClick={() => setShowNewAssignment(false)}
                className="modal-close-btn"
                aria-label="Close"
                style={{ background: 'none', border: 'none', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
            <div className="modal-grid">
              <div className="modal-option option-auto" onClick={() => setShowNewAssignment(false)}>
                <img src="/logo-auto.svg" alt="Automatic" style={{ width: '80px', height: '80px' }} />
                <h3>Automatic</h3>
                <p>Automatically creates assignments based on predefined rules and data.</p>
              </div>
              <div className="modal-option option-manual" onClick={() => setShowNewAssignment(false)}>
                <img src="/logo-manual.svg" alt="Custom" style={{ width: '80px', height: '80px' }} />
                <h3>Manual</h3>
                <p>Manually create and customize your assignment details.</p>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default Dashboard;
