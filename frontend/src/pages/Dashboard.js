import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import '../styles/Dashboard.css';

// Dashboard component for VerifiHireAI
function Dashboard() {
  const navigate = useNavigate();


  return (
    <div className="dashboard-container">
      <Header />

      <main className="dashboard-main">

        {/* Action Modules Grid */}
        <section className="modules-grid">

          {/* Module 1: AI Assessment */}
          <div className="module-card">
            <div className="module-header">
              <div className="module-icon-wrapper blue-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
              </div>
              <h3>AI-Powered Assessment</h3>
            </div>
            <div className="module-actions">
              <button className="action-btn" onClick={() => window.location.href = '/ai/assessments.html'}>
                <span>Assessments</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
              <button className="action-btn" onClick={() => window.location.href = '/ai/create_assessment.html'} style={{ marginTop: '8px' }}>
                <span>Create Assessment</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>

          {/* Module 2: Custom Assessment */}
          <div className="module-card">
            <div className="module-header">
              <div className="module-icon-wrapper purple-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
              </div>
              <h3>Custom Assessment</h3>
            </div>
            <div className="module-actions">
              <button className="action-btn" onClick={() => navigate('/custom-assessment')}>
                <span>Question Cart</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
              <button className="action-btn" onClick={() => navigate('/coding')}>
                <span>Coding</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>

          {/* Module 3a: Resume Screening */}
          <div className="module-card">
            <div className="module-header">
              <div className="module-icon-wrapper indigo-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
              </div>
              <h3>Resume Screening</h3>
            </div>
            <div className="module-actions">
              <button className="action-btn" onClick={() => window.location.href = '/ai/resume_matcher.html'}>
                <span>Analyze Resumes</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>

          {/* Module 3b: AI Interview */}
          <div className="module-card">
            <div className="module-header">
              <div className="module-icon-wrapper teal-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" /></svg>
              </div>
              <h3>AI Interview</h3>
            </div>
            <div className="module-actions">
              <button className="action-btn" onClick={() => { }}>
                <span>Start Session</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>

          {/* Module 4: Interview */}
          <div className="module-card">
            <div className="module-header">
              <div className="module-icon-wrapper orange-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
              </div>
              <h3>Live Interview</h3>
            </div>
            <div className="module-actions">
              <button className="action-btn" onClick={() => navigate('/send-invite')}>
                <span>Send Invite</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
              <button className="action-btn" onClick={() => navigate('/live-interview-list')}>
                <span>Join Room</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>

          {/* Module 5: Results */}
          <div className="module-card simple-card" onClick={() => navigate('/results')}>
            <div className="simple-card-content">
              <div className="module-icon-wrapper green-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
              </div>
              <div>
                <h3>Results</h3>
                <p>View selection outcomes</p>
              </div>
            </div>
            <div className="card-arrow-bg">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </div>
          </div>

          {/* Module 6: Candidates */}
          <div className="module-card">
            <div className="module-header">
              <div className="module-icon-wrapper pink-glow">
                <svg className="module-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              </div>
              <h3>Candidates</h3>
            </div>
            <div className="module-actions">
              <button className="action-btn" onClick={() => navigate('/candidates')}>
                <span>Manage</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
              <button className="action-btn" onClick={() => navigate('/assessments')}>
                <span>Assessments</span>
                <svg className="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
              </button>
            </div>
          </div>

        </section>
      </main>


    </div>
  );
}

export default Dashboard;
