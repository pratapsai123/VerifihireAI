import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import '../styles/FeatureAiAssessments.css';

/* ─── SVG ICONS (zero external deps) ─── */
const Icons = {
  FileText: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
  ),
  Upload: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
  ),
  Brain: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>
  ),
  Shield: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
  ),
  Mic: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v1a7 7 0 0 1-14 0v-1"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
  ),
  CheckCircle: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
  ),
  Calendar: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
  ),
  Code: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
  ),
  Cpu: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="15" x2="23" y2="15"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="15" x2="4" y2="15"></line></svg>
  ),
  Download: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
  ),
  Zap: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
  ),
  Settings: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
  ),
  Users: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
  ),
  Send: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
  ),
  BarChart: (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>
  )
};

/* ─── SCROLL REVEAL WRAPPER ─── */
function ScrollReveal({ children, delay = 0, lazy = false }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.05, rootMargin: '0px 0px -40px 0px' }
    );
    const currentRef = ref.current;
    if (currentRef) {
      observer.observe(currentRef);
    }
    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, []);

  return (
    <div
      ref={ref}
      className={`faa-scroll-reveal ${isVisible ? 'visible' : ''}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {lazy ? (isVisible ? children : <div style={{ minHeight: '300px' }}></div>) : children}
    </div>
  );
}

export default function FeatureAiAssessments() {
  const [activeMode, setActiveMode] = useState(0); // 0 = Manual, 1 = Automatic
  const [typewriterText, setTypewriterText] = useState('');
  const [mockupKey, setMockupKey] = useState(0);
  const [isSystemLoading, setIsSystemLoading] = useState(true);
  const [loaderText, setLoaderText] = useState('CONNECTING TO PIPELINE HOST...');
  const [loaderProgress, setLoaderProgress] = useState(0);
  const loopRef = useRef(null);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // System boot sequence loader
  useEffect(() => {
    const steps = [
      { text: 'ESTABLISHING SECURE CONNECTION...', delay: 150, progress: 20 },
      { text: 'CONNECTING TO COGNITIVE NETWORK...', delay: 350, progress: 45 },
      { text: 'PARSING RESUME NLP SCORING DICTIONARY...', delay: 550, progress: 70 },
      { text: 'INITIALIZING AI AGENT INDU VOICE MODULE...', delay: 750, progress: 90 },
      { text: 'SYSTEM SECURE. PIPELINE READY.', delay: 950, progress: 100 }
    ];

    steps.forEach((step, i) => {
      setTimeout(() => {
        setLoaderText(step.text);
        setLoaderProgress(step.progress);
        if (i === steps.length - 1) {
          setTimeout(() => {
            setIsSystemLoading(false);
          }, 250);
        }
      }, step.delay);
    });
  }, []);

  // Typewriter for JD input
  useEffect(() => {
    const fullText = activeMode === 0 ? 'Senior Frontend Developer' : 'AI Engineer (ML/NLP)';
    let idx = 0;
    setTypewriterText('');
    const timer = setInterval(() => {
      if (idx < fullText.length) {
        setTypewriterText(prev => prev + fullText.charAt(idx));
        idx++;
      } else {
        clearInterval(timer);
      }
    }, 65);
    return () => clearInterval(timer);
  }, [activeMode, mockupKey]);

  // Auto-loop mockup restart
  useEffect(() => {
    loopRef.current = setInterval(() => {
      setMockupKey(prev => prev + 1);
    }, 12000);
    return () => clearInterval(loopRef.current);
  }, [activeMode]);

  const handleModeChange = (mode) => {
    setActiveMode(mode);
    setMockupKey(prev => prev + 1);
    if (loopRef.current) clearInterval(loopRef.current);
    loopRef.current = setInterval(() => {
      setMockupKey(prev => prev + 1);
    }, 12000);
  };

  if (isSystemLoading) {
    return (
      <div className="faa-loader-screen">
        <div className="faa-loader-ambient">
          <div className="loader-glow"></div>
        </div>
        <div className="faa-loader-content">
          <div className="loader-scanner"></div>
          <div className="loader-logo">VerifiHire<span>AI</span></div>
          <div className="loader-status">
            <span className="loader-blink-tag">&gt;_ SYSTEM BOOT SEQUENCE</span>
            <div className="loader-text">{loaderText}</div>
          </div>
          <div className="loader-progress-bar">
            <div className="loader-progress-fill" style={{ width: `${loaderProgress}%` }}></div>
          </div>
          <div className="loader-percent">{loaderProgress}%</div>
        </div>
      </div>
    );
  }

  return (
    <div className="faa-container">
      <MainHeader />

      {/* Ambient Background */}
      <div className="faa-ambient-bg">
        <div className="faa-glow-1"></div>
        <div className="faa-glow-2"></div>
        <div className="faa-glow-3"></div>
        <div className="faa-grid-pattern"></div>
      </div>

      {/* ═══════ HERO SECTION ═══════ */}
      <section className="faa-hero">
        <div className="faa-hero-left">
          <div className="faa-hero-badge">
            <span className="faa-badge-dot-wrap">
              <span className="faa-badge-dot-ping"></span>
              <span className="faa-badge-dot"></span>
            </span>
            <span>AI-Powered Hiring</span>
          </div>

          <h1>
            Two modes.<br />
            <span className="faa-grad-text">One intelligent pipeline.</span>
          </h1>

          <p className="faa-hero-desc">
            Choose Manual mode for step-by-step control, or let Fully Automatic mode run the entire screening — from resume matching to AI interviews — hands-free.
          </p>

          <div className="faa-hero-cta">
            <Link to="/signup" className="faa-btn-primary">Start Free Trial</Link>
            <Link to="/contact" className="faa-btn-secondary">Book a Demo</Link>
          </div>
        </div>

        {/* Hero Right — Mode Mockup */}
        <div className="faa-hero-right">
          <div className="faa-mode-tabs">
            <button
              className={`faa-mode-tab ${activeMode === 0 ? 'active' : ''}`}
              onClick={() => handleModeChange(0)}
            >
              🔧 Manual Mode
            </button>
            <button
              className={`faa-mode-tab ${activeMode === 1 ? 'active' : ''}`}
              onClick={() => handleModeChange(1)}
            >
              ⚡ Fully Automatic
            </button>
          </div>

          <div className="faa-mockup-body">
            <div className="faa-dots-header">
              <div className="dot red"></div>
              <div className="dot yellow"></div>
              <div className="dot green"></div>
            </div>

            {/* ── MANUAL MODE MOCKUP ── */}
            {activeMode === 0 && (
              <div className="mockup-content" key={`manual-${mockupKey}`}>
                {/* Step 1: Create JD */}
                <div className="mock-step">
                  <div className="mock-label">Step 1 — Create Job Description</div>
                  <div className="mock-input">
                    <span>{typewriterText}</span>
                    <span className="mock-typing-cursor"></span>
                  </div>
                </div>

                {/* Step 2: Upload Resumes */}
                <div className="mock-step">
                  <div className="mock-label">Step 2 — Upload Resumes</div>
                  <div className="mock-success">
                    <Icons.Upload style={{ width: '14px', height: '14px' }} />
                    <span>48 resumes uploaded (PDF/CSV)</span>
                  </div>
                </div>

                {/* Step 3: AI Matching */}
                <div className="mock-step">
                  <div className="mock-label">Step 3 — AI Screens Against JD (Threshold: 70%)</div>
                  <div className="mock-loader">
                    <div className="mock-spinner"></div>
                    <span>Matching resumes to job description...</span>
                  </div>
                  <div className="mock-threshold-bar">
                    <div className="mock-threshold-fill"></div>
                  </div>
                </div>

                {/* Step 4: Download Excel */}
                <div className="mock-step">
                  <div className="mock-label">Step 4 — Qualified Candidates</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <div className="mock-success" style={{ flex: 1, minWidth: '180px' }}>
                      <Icons.CheckCircle style={{ width: '14px', height: '14px' }} />
                      <span>31 of 48 passed threshold</span>
                    </div>
                    <div className="mock-excel-btn">
                      <Icons.Download style={{ width: '13px', height: '13px' }} />
                      Download Excel
                    </div>
                  </div>
                </div>

                {/* Step 5: Send Assessment */}
                <div className="mock-step">
                  <div className="mock-label">Step 5 — Send AI Assessment</div>
                  <div className="mock-send-btn">
                    <Icons.Send style={{ width: '13px', height: '13px' }} />
                    Send Assessment to 31 Candidates
                  </div>
                </div>

                {/* Step 6: Results & Schedule */}
                <div className="mock-step">
                  <div className="mock-label">Step 6 — Review Results & Schedule AI Interview</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <div className="mock-excel-btn">
                      <Icons.BarChart style={{ width: '13px', height: '13px' }} />
                      Results Excel
                    </div>
                    <div className="mock-send-btn" style={{ background: 'linear-gradient(135deg, #059669 0%, #0891B2 100%)' }}>
                      <Icons.Mic style={{ width: '13px', height: '13px' }} />
                      Schedule AI Interview
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── FULLY AUTOMATIC MODE MOCKUP ── */}
            {activeMode === 1 && (
              <div className="mockup-content" key={`auto-${mockupKey}`}>
                {/* Step 1: Create JD */}
                <div className="mock-step">
                  <div className="mock-label">Step 1 — Create JD with Role Name</div>
                  <div className="mock-input">
                    <span>{typewriterText}</span>
                    <span className="mock-typing-cursor"></span>
                  </div>
                </div>

                {/* Step 2: Upload Resumes */}
                <div className="mock-step">
                  <div className="mock-label">Step 2 — Upload Bulk Resumes</div>
                  <div className="mock-success">
                    <Icons.Upload style={{ width: '14px', height: '14px' }} />
                    <span>120 resumes uploaded</span>
                  </div>
                </div>

                {/* Step 3: Set Date Ranges */}
                <div className="mock-step">
                  <div className="mock-label">Step 3 — Set Date Ranges</div>
                  <div className="mock-date-row">
                    <div className="mock-date-pick">
                      <span className="date-label">AI Assessment Window</span>
                      <span className="date-value">Jun 15 – Jun 20, 2026</span>
                    </div>
                    <div className="mock-date-pick">
                      <span className="date-label">AI Interview Window</span>
                      <span className="date-value">Jun 22 – Jun 28, 2026</span>
                    </div>
                  </div>
                </div>

                {/* Step 4: Generate */}
                <div className="mock-step">
                  <div className="mock-label">Step 4 — Activate Pipeline</div>
                  <div className="mock-generate-btn">
                    <Icons.Zap style={{ width: '15px', height: '15px' }} />
                    Generate — One Click to Automate
                  </div>
                </div>

                {/* Step 5: Pipeline Active */}
                <div className="mock-step">
                  <div className="mock-label">Step 5 — AI Pipeline Running</div>
                  <div className="mock-pipeline-active">
                    <div className="pipeline-title">
                      <Icons.CheckCircle style={{ width: '14px', height: '14px' }} />
                      Pipeline Active — AI is handling everything
                    </div>
                    <div className="pipeline-steps">
                      <span className="pipeline-node active-node">Resume Match</span>
                      <span className="pipeline-arrow">→</span>
                      <span className="pipeline-node active-node">AI Assessment</span>
                      <span className="pipeline-arrow">→</span>
                      <span className="pipeline-node active-node">AI Interview</span>
                    </div>
                  </div>
                </div>

                {/* Resume Matching Preview */}
                <div className="mock-step">
                  <div className="mock-label">Live Status</div>
                  <div className="mock-resume-chips">
                    <span className="resume-chip"><span className="chip-status pass"></span> Rahul_CV.pdf — 88%</span>
                    <span className="resume-chip"><span className="chip-status pass"></span> Priya_Resume.pdf — 76%</span>
                    <span className="resume-chip"><span className="chip-status fail"></span> Arjun_CV.pdf — 42%</span>
                    <span className="resume-chip"><span className="chip-status pass"></span> Neha_R.pdf — 81%</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ═══════ MODE COMPARISON SECTION ═══════ */}
      <ScrollReveal>
        <section className="faa-section">
          <div className="faa-section-header">
            <span className="faa-section-tag faa-tag-blue">Choose Your Workflow</span>
            <h2>Manual Control or Full Automation</h2>
            <p>
              Whether you prefer hands-on control at every step or want AI to run the entire pipeline autonomously — VerifiHireAI adapts to your hiring style.
            </p>
          </div>

          <div className="faa-comparison-grid">
            {/* Manual Mode Card */}
            <div className="faa-compare-card manual-card" onClick={() => handleModeChange(0)}>
              <div className="compare-card-header">
                <div className="compare-icon manual-icon">🔧</div>
                <div>
                  <h3>Manual Mode</h3>
                  <div className="compare-subtitle">Step-by-step recruiter control</div>
                </div>
              </div>
              <ul className="compare-steps-list">
                <li>
                  <span className="step-num blue">1</span>
                  <span>Create a role with detailed job description</span>
                </li>
                <li>
                  <span className="step-num blue">2</span>
                  <span>Upload candidate resumes in bulk (PDF/CSV)</span>
                </li>
                <li>
                  <span className="step-num blue">3</span>
                  <span>AI screens resumes against JD with threshold — qualified list exported as Excel</span>
                </li>
                <li>
                  <span className="step-num blue">4</span>
                  <span>Manually send AI assessments to selected candidates</span>
                </li>
                <li>
                  <span className="step-num blue">5</span>
                  <span>View assessment results in Excel — who passed, who didn't</span>
                </li>
                <li>
                  <span className="step-num blue">6</span>
                  <span>Schedule AI interviews for qualified candidates</span>
                </li>
              </ul>
            </div>

            {/* Automatic Mode Card */}
            <div className="faa-compare-card auto-card" onClick={() => handleModeChange(1)}>
              <div className="compare-card-header">
                <div className="compare-icon auto-icon">⚡</div>
                <div>
                  <h3>Fully Automatic Mode</h3>
                  <div className="compare-subtitle">One click, end-to-end AI pipeline</div>
                </div>
              </div>
              <ul className="compare-steps-list">
                <li>
                  <span className="step-num green">1</span>
                  <span>Create JD with role name and paste job description</span>
                </li>
                <li>
                  <span className="step-num green">2</span>
                  <span>Upload all candidate resumes at once</span>
                </li>
                <li>
                  <span className="step-num green">3</span>
                  <span>Set date ranges for AI Assessment and AI Interview windows</span>
                </li>
                <li>
                  <span className="step-num green">4</span>
                  <span>Click Generate — validates the link and activates the full AI pipeline</span>
                </li>
                <li>
                  <span className="step-num green">5</span>
                  <span>AI auto-matches resumes → auto-sends assessments → auto-schedules interviews</span>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ═══════ MANUAL MODE MATRIX ═══════ */}
      <ScrollReveal lazy={true}>
        <section className="faa-section faa-section-divider">
          <div className="faa-section-header">
            <span className="faa-section-tag faa-tag-purple">Manual Mode</span>
            <h2>Recruiter Command Matrix</h2>
            <p>
              Full control at every stage. Manage resume screening, assessment distribution, and interview scheduling manually.
            </p>
          </div>

          <div className="faa-matrix-grid">
            {/* Card 1: Job Description */}
            <div className="faa-matrix-card">
              <div className="matrix-card-header">
                <span className="matrix-step">Step 01</span>
                <div className="matrix-icon-wrap purple-glow">
                  <Icons.FileText style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                </div>
              </div>
              <h3>Define Role & Job Description</h3>
              <p>Define the target role with required skills, experience, and qualifications to configure the reference AI model.</p>
              <div className="matrix-widget text-widget">
                <span className="widget-label">Role Target</span>
                <span className="widget-val">Senior Frontend Developer</span>
              </div>
            </div>

            {/* Card 2: Resume Upload */}
            <div className="faa-matrix-card">
              <div className="matrix-card-header">
                <span className="matrix-step">Step 02</span>
                <div className="matrix-icon-wrap purple-glow">
                  <Icons.Upload style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                </div>
              </div>
              <h3>Upload Candidate Resumes</h3>
              <p>Upload candidate resumes in bulk. The system parses PDFs, Word documents, or spreadsheets ready for screening.</p>
              <div className="matrix-widget upload-widget">
                <div className="upload-progress-wrap">
                  <span className="upload-txt">Ingesting 48 resumes (100%)</span>
                  <div className="upload-bar"><div className="upload-fill"></div></div>
                </div>
              </div>
            </div>

            {/* Card 3: AI Screening */}
            <div className="faa-matrix-card">
              <div className="matrix-card-header">
                <span className="matrix-step">Step 03</span>
                <div className="matrix-icon-wrap purple-glow">
                  <Icons.Brain style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                </div>
              </div>
              <h3>AI Matcher & Threshold</h3>
              <p>AI compares resumes to the JD. Adjust threshold criteria to auto-qualify candidates who meet the passing score.</p>
              <div className="matrix-widget threshold-widget">
                <div className="threshold-slider-wrap">
                  <span className="threshold-label">Match Threshold</span>
                  <span className="threshold-val">70% Pass</span>
                </div>
                <div className="threshold-slider"><div className="threshold-handle"></div></div>
              </div>
            </div>

            {/* Card 4: Excel Export */}
            <div className="faa-matrix-card">
              <div className="matrix-card-header">
                <span className="matrix-step">Step 04</span>
                <div className="matrix-icon-wrap purple-glow">
                  <Icons.Download style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                </div>
              </div>
              <h3>Export Qualified List</h3>
              <p>Review the list of candidates passing the match threshold and export them as a spreadsheet file with deep score insights.</p>
              <div className="matrix-widget excel-widget">
                <div className="excel-row-preview">
                  <span className="excel-preview-name">Rahul_CV.pdf</span>
                  <span className="excel-preview-badge">88% Match</span>
                </div>
                <button className="matrix-excel-btn">
                  <Icons.Download style={{ width: '13px', height: '13px' }} />
                  <span>Download Excel List</span>
                </button>
              </div>
            </div>

            {/* Card 5: Send Assessments */}
            <div className="faa-matrix-card">
              <div className="matrix-card-header">
                <span className="matrix-step">Step 05</span>
                <div className="matrix-icon-wrap purple-glow">
                  <Icons.Send style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                </div>
              </div>
              <h3>Send AI Assessments</h3>
              <p>Manually select candidate groups and dispatch specialized MCQ/coding assessment invitation links to candidates.</p>
              <div className="matrix-widget send-widget">
                <span className="send-status">31 Candidates Qualified</span>
                <button className="matrix-send-btn">
                  <Icons.Send style={{ width: '12px', height: '12px' }} />
                  <span>Send Assessment Links</span>
                </button>
              </div>
            </div>

            {/* Card 6: AI Voice Interview */}
            <div className="faa-matrix-card">
              <div className="matrix-card-header">
                <span className="matrix-step">Step 06</span>
                <div className="matrix-icon-wrap purple-glow">
                  <Icons.Mic style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                </div>
              </div>
              <h3>Schedule AI Interview</h3>
              <p>Review assessment results in Excel. Schedule interactive, real-time voice interviews with Indu for qualifiers.</p>
              <div className="matrix-widget interview-widget">
                <span className="interview-status">12 Candidates Passed Test</span>
                <button className="matrix-interview-btn">
                  <Icons.Mic style={{ width: '12px', height: '12px' }} />
                  <span>Schedule AI Interview</span>
                </button>
              </div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ═══════ AUTOMATIC MODE FUNNEL ═══════ */}
      <ScrollReveal lazy={true}>
        <section className="faa-section faa-section-divider">
          <div className="faa-section-header">
            <span className="faa-section-tag faa-tag-emerald">Fully Automatic Mode</span>
            <h2>Autonomous AI Pipeline Funnel</h2>
            <p>
              Configure once, click generate, and let AI execute the complete hiring sequence end-to-end without manual intervention.
            </p>
          </div>

          <div className="faa-funnel-layout">
            {/* Left: Pipeline Funnel */}
            <div className="faa-funnel-pipeline">
              {/* SVG Connecting Flow Lines */}
              <div className="funnel-svg-container">
                <svg className="funnel-connector-svg" width="100%" height="100%" viewBox="0 0 100 800" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M 50 0 L 50 800" className="funnel-svg-line-bg" />
                  <path d="M 50 0 L 50 800" className="funnel-svg-line-pulse" />
                </svg>
              </div>

              {/* Funnel Step 1 */}
              <div className="funnel-stage">
                <div className="funnel-node-wrapper">
                  <div className="funnel-node-glow"></div>
                  <div className="funnel-node text-emerald">01</div>
                </div>
                <div className="funnel-stage-details">
                  <h3>Role & JD Configuration</h3>
                  <p>Recruiter defines job details and pastes the job description. The AI extracts core criteria automatically.</p>
                  <div className="funnel-tag-row">
                    <span className="f-tag f-tag-emerald">AI Configured</span>
                  </div>
                </div>
              </div>

              {/* Funnel Step 2 */}
              <div className="funnel-stage">
                <div className="funnel-node-wrapper">
                  <div className="funnel-node-glow"></div>
                  <div className="funnel-node text-emerald">02</div>
                </div>
                <div className="funnel-stage-details">
                  <h3>Bulk Resume Ingest</h3>
                  <p>Upload resumes in bulk. AI matches each CV against the JD and filters matching candidates instantly.</p>
                  <div className="funnel-tag-row">
                    <span className="f-tag f-tag-emerald">Bulk Processing</span>
                  </div>
                </div>
              </div>

              {/* Funnel Step 3 */}
              <div className="funnel-stage">
                <div className="funnel-node-wrapper">
                  <div className="funnel-node-glow"></div>
                  <div className="funnel-node text-emerald">03</div>
                </div>
                <div className="funnel-stage-details">
                  <h3>Set Link Validity & Dates</h3>
                  <p>Pick date windows for the AI Assessment and AI Interview. Date ranges serve to validate the link.</p>
                  <div className="funnel-stage-date-picker">
                    <div className="funnel-date-item">
                      <span className="date-hdr">AI Assessment Window</span>
                      <span className="date-val">Jun 15 – Jun 20</span>
                    </div>
                    <div className="funnel-date-item">
                      <span className="date-hdr">AI Interview Window</span>
                      <span className="date-val">Jun 22 – Jun 28</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Funnel Step 4 */}
              <div className="funnel-stage">
                <div className="funnel-node-wrapper">
                  <div className="funnel-node-glow"></div>
                  <div className="funnel-node text-emerald">04</div>
                </div>
                <div className="funnel-stage-details">
                  <h3>Generate AI Pipeline</h3>
                  <p>One click validates configurations and activates the end-to-end hands-free recruiter pipeline.</p>
                  <div className="funnel-tag-row">
                    <span className="f-tag f-tag-cyan">Ready to Generate</span>
                  </div>
                </div>
              </div>

              {/* Funnel Step 5 */}
              <div className="funnel-stage">
                <div className="funnel-node-wrapper">
                  <div className="funnel-node-glow"></div>
                  <div className="funnel-node text-emerald">05</div>
                </div>
                <div className="funnel-stage-details">
                  <h3>AI Runs Entire Loop</h3>
                  <p>AI automatically triggers tests for qualifiers, grades submissions, and auto-schedules voice interviews.</p>
                  <div className="funnel-tag-row">
                    <span className="f-tag f-tag-pulse">Autonomous Loop Active</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Engine Dashboard Console */}
            <div className="faa-funnel-console-wrapper">
              <div className="faa-funnel-console">
                <div className="console-bar">
                  <div className="console-status-dot-wrap">
                    <span className="console-status-dot-pulse"></span>
                    <span className="console-status-dot"></span>
                  </div>
                  <span className="console-title">PIPELINE CORE CONSOLE</span>
                  <span className="console-pill">ACTIVE</span>
                </div>
                
                <div className="console-display">
                  <div className="console-param-row">
                    <span className="param-label">Role Target:</span>
                    <span className="param-val">AI Engineer (ML/NLP)</span>
                  </div>
                  <div className="console-param-row">
                    <span className="param-label">Date Validation:</span>
                    <span className="param-val text-cyan">VALID (15 - 28 JUN)</span>
                  </div>
                  <div className="console-param-row">
                    <span className="param-label">Resume Stream:</span>
                    <span className="param-val text-emerald">CONNECTED (120 Files)</span>
                  </div>

                  <div className="console-screen-divider"></div>

                  <div className="console-logs-screen">
                    <div className="console-logs-header">// LIVE AUTONOMOUS SYSTEM STREAMS</div>
                    <div className="console-logs-list">
                      <div className="console-log green">[09:00:01] Ingested 120 resumes. Ready for evaluation.</div>
                      <div className="console-log green">[09:00:03] Matching CVs against JD...</div>
                      <div className="console-log">[09:00:08] Rahul_CV.pdf (88% Match) - QUALIFIED</div>
                      <div className="console-log">[09:00:11] Priya_Resume.pdf (76% Match) - QUALIFIED</div>
                      <div className="console-log red">[09:00:14] Arjun_CV.pdf (42% Match) - REJECTED (Under threshold)</div>
                      <div className="console-log green">[09:00:18] AI Matching complete. 84 candidates pass.</div>
                      <div className="console-log cyan">[09:00:20] AI Assessment links dispatched automatically.</div>
                      <div className="console-log">[09:00:25] Awaiting candidates test submissions...</div>
                      <div className="console-log purple">[09:00:40] Auto-scheduled voice interview for Priya_Resume (92% Score)</div>
                      <div className="console-log purple">[09:00:52] Auto-scheduled voice interview for Rahul_CV (89% Score)</div>
                    </div>
                  </div>

                  <div className="console-bottom-action">
                    <div className="console-sync-btn">
                      <Icons.Zap style={{ width: '13px', height: '13px', color: '#10B981' }} />
                      <span>Synchronized Pipeline</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ═══════ FEATURE CARDS ═══════ */}
      <ScrollReveal>
        <section className="faa-section">
          <div className="faa-section-header">
            <span className="faa-section-tag faa-tag-green">Core Capabilities</span>
            <h2>What Powers the Pipeline</h2>
            <p>
              Three AI-driven pillars that work together across both manual and automatic workflows.
            </p>
          </div>

          <div className="faa-cards-grid">
            {/* Card 1: AI Resume Screening */}
            <div className="faa-feature-card">
              <div className="faa-card-icon blue">
                <Icons.Brain style={{ width: '24px', height: '24px' }} />
              </div>
              <h3>AI Resume Screening</h3>
              <p>
                NLP-powered matching compares each resume against the job description. Configurable threshold scoring ensures only qualified candidates advance — results downloadable as Excel.
              </p>
            </div>

            {/* Card 2: AI Assessment */}
            <div className="faa-feature-card">
              <div className="faa-card-icon purple">
                <Icons.Code style={{ width: '24px', height: '24px' }} />
              </div>
              <h3>AI Assessment</h3>
              <p>
                AI-generated MCQ question pools and coding challenges tailored to the role. Proctored environment with identity verification, tab-switch detection, and automated grading.
              </p>
            </div>

            {/* Card 3: AI Interview with Indu */}
            <div className="faa-feature-card">
              <div className="faa-card-icon green">
                <Icons.Mic style={{ width: '24px', height: '24px' }} />
              </div>
              <h3>AI Interview with Indu</h3>
              <p>
                Voice-based AI interviewer conducts structured conversational interviews. Real-time speech-to-text, silence watchdog monitoring, and AI-powered evaluation of responses.
              </p>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ═══════ WHY CHOOSE US ═══════ */}
      <ScrollReveal>
        <section className="faa-section faa-section-divider">
          <div className="faa-section-header">
            <span className="faa-section-tag faa-tag-blue">Why VerifiHireAI</span>
            <h2>Built to Eliminate the Hiring Bottleneck</h2>
            <p>
              Traditional hiring drains HR teams with weeks of manual screening, scheduling, and follow-ups. We built VerifiHireAI to replace that entire burden with an AI-first pipeline.
            </p>
          </div>

          {/* Before vs After Grid */}
          <div className="faa-before-after-grid">
            {/* BEFORE Card */}
            <div className="faa-ba-card faa-ba-before">
              <div className="ba-card-header">
                <div className="ba-icon ba-icon-before">⏳</div>
                <div>
                  <h3>Before — Traditional Hiring</h3>
                  <span className="ba-subtitle">Slow, manual, error-prone</span>
                </div>
              </div>
              <ul className="ba-list">
                <li>
                  <span className="ba-x">✗</span>
                  <span>HR manually screens 100s of resumes one-by-one — takes <strong>days to weeks</strong></span>
                </li>
                <li>
                  <span className="ba-x">✗</span>
                  <span>Scheduling assessments and interviews via email chains — <strong>constant back-and-forth</strong></span>
                </li>
                <li>
                  <span className="ba-x">✗</span>
                  <span>No standardized evaluation — <strong>bias creeps in</strong>, quality varies by reviewer</span>
                </li>
                <li>
                  <span className="ba-x">✗</span>
                  <span>Qualified candidates drop off due to <strong>slow response times</strong></span>
                </li>
                <li>
                  <span className="ba-x">✗</span>
                  <span>HR spends <strong>70%+ time</strong> on repetitive screening tasks instead of strategic work</span>
                </li>
              </ul>
            </div>

            {/* AFTER Card */}
            <div className="faa-ba-card faa-ba-after">
              <div className="ba-card-header">
                <div className="ba-icon ba-icon-after">⚡</div>
                <div>
                  <h3>After — With VerifiHireAI</h3>
                  <span className="ba-subtitle">Automated, intelligent, instant</span>
                </div>
              </div>
              <ul className="ba-list">
                <li>
                  <span className="ba-check">✓</span>
                  <span>AI screens all resumes against JD in <strong>seconds</strong> — not days</span>
                </li>
                <li>
                  <span className="ba-check">✓</span>
                  <span>Assessments and interviews are <strong>auto-sent and auto-scheduled</strong> — zero email chains</span>
                </li>
                <li>
                  <span className="ba-check">✓</span>
                  <span>Standardized AI evaluation ensures <strong>fair, consistent scoring</strong> for every candidate</span>
                </li>
                <li>
                  <span className="ba-check">✓</span>
                  <span>Candidates experience <strong>instant engagement</strong> — no waiting, no ghosting</span>
                </li>
                <li>
                  <span className="ba-check">✓</span>
                  <span>HR burden reduced by <strong>90%</strong> — focus on final decisions, not logistics</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Impact Stats */}
          <div className="faa-impact-stats">
            <div className="faa-impact-item">
              <div className="impact-num"><span className="impact-accent">90</span>%</div>
              <div className="impact-label">Reduction in HR screening time</div>
            </div>
            <div className="faa-impact-item">
              <div className="impact-num"><span className="impact-accent">10</span>x</div>
              <div className="impact-label">Faster candidate processing</div>
            </div>
            <div className="faa-impact-item">
              <div className="impact-num"><span className="impact-accent">0</span></div>
              <div className="impact-label">Manual scheduling needed</div>
            </div>
            <div className="faa-impact-item">
              <div className="impact-num"><span className="impact-accent">100</span>%</div>
              <div className="impact-label">AI-powered, unbiased evaluation</div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ═══════ CTA SECTION ═══════ */}
      <ScrollReveal>
        <section className="faa-cta">
          <h2>Ready to automate your hiring pipeline?</h2>
          <p>
            Choose manual for precision control or fully automatic for zero-touch screening. Either way, AI handles the heavy lifting.
          </p>
          <div className="faa-cta-btns">
            <Link to="/signup" className="faa-btn-primary">Start Free Trial</Link>
            <Link to="/contact" className="faa-btn-secondary">Book a Demo</Link>
          </div>
          <div className="faa-cta-note">
            No credit card required &bull; Manual + Automatic modes included &bull; Unlimited AI interviews
          </div>
        </section>
      </ScrollReveal>

      <Footer />
    </div>
  );
}
