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
function ScrollReveal({ children, delay = 0 }) {
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        } else {
          entry.target.classList.remove('visible');
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
      className="faa-scroll-reveal"
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

// Helper component for word-by-word reveal animation
const WordByWord = ({ text, boldText, startIndexRef }) => {
  const words = [];
  
  if (boldText) {
    boldText.split(/\s+/).forEach(w => {
      if (w) words.push({ word: w, isBold: true });
    });
  }
  
  if (text) {
    text.split(/\s+/).forEach(w => {
      if (w) words.push({ word: w, isBold: false });
    });
  }

  const baseIndex = startIndexRef.current;
  startIndexRef.current += words.length;

  return (
    <>
      {words.map((item, idx) => {
        const wordIndex = baseIndex + idx;
        return (
          <span
            key={idx}
            className="faa-word"
            style={{
              animationDelay: `${0.6 + wordIndex * 0.025}s`,
              fontWeight: item.isBold ? '700' : 'normal',
              color: item.isBold ? '#FFFFFF' : 'inherit',
              display: 'inline-block',
              marginRight: '4px'
            }}
          >
            {item.word}
          </span>
        );
      })}
    </>
  );
};

export default function FeatureAiAssessments() {
  const [activeMode, setActiveMode] = useState(0); // 0 = Manual, 1 = Automatic
  const [typewriterText, setTypewriterText] = useState('');
  const [mockupKey, setMockupKey] = useState(0);
  const [manualStep, setManualStep] = useState(1); // 1 = Screening, 2 = Assessment, 3 = AI Interview
  const loopRef = useRef(null);
  const manualStepRef = useRef(null);
  const manualRotationRef = useRef(0);   // counts complete 1→2→3 cycles
  const autoTimeoutRef = useRef(null);   // timeout for auto-mode single rotation
  const userClickedRef = useRef(false);  // tracks if user manually clicked a tab

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);


  // Typewriter for JD input
  useEffect(() => {
    const fullText = activeMode === 0 ? 'Senior Frontend Developer' : 'AI Engineer (ML/NLP)';
    let i = 0;
    setTypewriterText('');
    const timer = setInterval(() => {
      i++;
      if (i <= fullText.length) {
        setTypewriterText(fullText.substring(0, i));
      } else {
        clearInterval(timer);
      }
    }, 65);
    return () => clearInterval(timer);
  }, [activeMode, mockupKey]);

  // Helper: clean up all timers
  const clearAllTimers = () => {
    if (loopRef.current) { clearInterval(loopRef.current); loopRef.current = null; }
    if (manualStepRef.current) { clearInterval(manualStepRef.current); manualStepRef.current = null; }
    if (autoTimeoutRef.current) { clearTimeout(autoTimeoutRef.current); autoTimeoutRef.current = null; }
  };

  // Auto-switch: Manual → Automatic after 2 full rotations
  // Auto-switch: Automatic → Manual after 1 full animation cycle (12s)
  useEffect(() => {
    clearAllTimers();

    if (activeMode === 0) {
      // Manual mode: cycle steps 1→2→3, count rotations
      manualRotationRef.current = 0;
      manualStepRef.current = setInterval(() => {
        setManualStep(prev => {
          const next = prev >= 3 ? 1 : prev + 1;
          if (next === 1 && prev === 3) {
            // Completed one full rotation
            manualRotationRef.current += 1;
            if (manualRotationRef.current >= 2 && !userClickedRef.current) {
              // After 2 rotations, switch to Fully Automatic
              setTimeout(() => {
                userClickedRef.current = false;
                setActiveMode(1);
                setMockupKey(k => k + 1);
              }, 0);
            }
          }
          return next;
        });
      }, 6000);
    } else {
      // Automatic mode: let the animation play for one full cycle (12s), then switch back
      loopRef.current = setInterval(() => {
        setMockupKey(prev => prev + 1);
      }, 12000);

      autoTimeoutRef.current = setTimeout(() => {
        if (!userClickedRef.current) {
          userClickedRef.current = false;
          setManualStep(1);
          setActiveMode(0);
          setMockupKey(k => k + 1);
        }
      }, 12000);
    }

    return () => clearAllTimers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeMode]);

  // When user manually clicks a stepper tab inside manual mode
  const handleManualStepChange = (step) => {
    userClickedRef.current = false;
    manualRotationRef.current = 0;
    setManualStep(step);
    // Restart step cycling timer
    if (manualStepRef.current) clearInterval(manualStepRef.current);
    manualStepRef.current = setInterval(() => {
      setManualStep(prev => {
        const next = prev >= 3 ? 1 : prev + 1;
        if (next === 1 && prev === 3) {
          manualRotationRef.current += 1;
          if (manualRotationRef.current >= 2) {
            setTimeout(() => {
              setActiveMode(1);
              setMockupKey(k => k + 1);
            }, 0);
          }
        }
        return next;
      });
    }, 6000);
  };

  // When user clicks the Manual Mode / Fully Automatic top-level tabs
  const handleModeChange = (mode) => {
    userClickedRef.current = true;
    clearAllTimers();
    manualRotationRef.current = 0;
    setManualStep(1);
    setActiveMode(mode);
    setMockupKey(prev => prev + 1);

    // After user click, restart auto-rotation after a brief pause
    setTimeout(() => {
      userClickedRef.current = false;
    }, 500);
  };

  const manualIndex = { current: 0 };
  const autoIndex = { current: 0 };

  return (
    <>
      <MainHeader />
      <div className="faa-container">

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

            {/* ── MANUAL MODE MOCKUP — 3-STEP WIZARD ── */}
            {activeMode === 0 && (
              <div className="mockup-content" key={`manual-${mockupKey}`}>
                {/* Stepper Navigation */}
                <div className="mock-stepper-nav">
                  <button className={`mock-stepper-tab ${manualStep === 1 ? 'active-step' : ''}`} onClick={() => handleManualStepChange(1)}>
                    <span className="stepper-num">1</span> Screening
                  </button>
                  <button className={`mock-stepper-tab ${manualStep === 2 ? 'active-step' : ''}`} onClick={() => handleManualStepChange(2)}>
                    <span className="stepper-num">2</span> Assessment
                  </button>
                  <button className={`mock-stepper-tab ${manualStep === 3 ? 'active-step' : ''}`} onClick={() => handleManualStepChange(3)}>
                    <span className="stepper-num">3</span> AI Interview
                  </button>
                </div>

                {/* Stepper Progress Bar */}
                <div className="mock-stepper-progress">
                  <div className="mock-stepper-progress-fill" style={{ width: `${(manualStep / 3) * 100}%` }}></div>
                </div>

                {/* ── STEP 1: Resume Screening ── */}
                {manualStep === 1 && (
                  <div className="mock-step-panel" key="step1">
                    <div className="mock-step" style={{ animationDelay: '0.05s' }}>
                      <div className="mock-label">Create Role & Upload Resumes</div>
                      <div className="mock-input">
                        <span>{typewriterText}</span>
                        <span className="mock-typing-cursor"></span>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '0.4s' }}>
                      <div className="mock-success">
                        <Icons.Upload style={{ width: '14px', height: '14px' }} />
                        <span>48 resumes uploaded (PDF/CSV)</span>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '0.8s' }}>
                      <div className="mock-label">AI Screening Results</div>
                      <div className="mock-screening-results">
                        <div className="mock-screen-chip pass">
                          <span>Rahul_CV.pdf</span>
                          <span style={{ marginLeft: 'auto' }}>88%</span>
                          <span className="chip-badge pass-badge">PASS</span>
                        </div>
                        <div className="mock-screen-chip pass">
                          <span>Priya_Resume.pdf</span>
                          <span style={{ marginLeft: 'auto' }}>76%</span>
                          <span className="chip-badge pass-badge">PASS</span>
                        </div>
                        <div className="mock-screen-chip fail">
                          <span>Arjun_CV.pdf</span>
                          <span style={{ marginLeft: 'auto' }}>42%</span>
                          <span className="chip-badge fail-badge">FAIL</span>
                        </div>
                        <div className="mock-screen-chip pass">
                          <span>Neha_R.pdf</span>
                          <span style={{ marginLeft: 'auto' }}>81%</span>
                          <span className="chip-badge pass-badge">PASS</span>
                        </div>
                      </div>
                    </div>
                    <div className="mock-csv-btn">
                      <Icons.Download style={{ width: '13px', height: '13px' }} />
                      Download Qualified Candidates (CSV)
                    </div>
                  </div>
                )}

                {/* ── STEP 2: AI Assessment ── */}
                {manualStep === 2 && (
                  <div className="mock-step-panel" key="step2">
                    <div className="mock-step" style={{ animationDelay: '0.05s' }}>
                      <div className="mock-label">Select Role</div>
                      <div className="mock-role-selector">
                        <span>Senior Frontend Developer</span>
                        <span className="role-dropdown-icon">▼</span>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '0.4s' }}>
                      <div className="mock-label">Set Link Validity</div>
                      <div className="mock-validity-row">
                        <div className="mock-validity-field">
                          <span className="vf-label">Valid From</span>
                          <span className="vf-value">Jun 15, 2026 9:00 AM</span>
                        </div>
                        <div className="mock-validity-field">
                          <span className="vf-label">Expires At</span>
                          <span className="vf-value">Jun 18, 2026 11:59 PM</span>
                        </div>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '0.8s' }}>
                      <div className="mock-feature-tags">
                        <span className="mock-feature-tag tag-purple">
                          <Icons.Shield style={{ width: '10px', height: '10px' }} /> Questions Never Repeat
                        </span>
                        <span className="mock-feature-tag tag-blue">
                          <Icons.Shield style={{ width: '10px', height: '10px' }} /> Tab-Proctored
                        </span>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '1.2s' }}>
                      <div className="mock-invite-btn">
                        <Icons.Send style={{ width: '12px', height: '12px' }} />
                        Invite & Send Assessment Links
                      </div>
                    </div>
                    <div className="mock-csv-btn">
                      <Icons.Download style={{ width: '13px', height: '13px' }} />
                      Download Assessment Results (CSV)
                    </div>
                  </div>
                )}

                {/* ── STEP 3: AI Interview ── */}
                {manualStep === 3 && (
                  <div className="mock-step-panel" key="step3">
                    <div className="mock-step" style={{ animationDelay: '0.05s' }}>
                      <div className="mock-label">Select Role & Interview Schedule</div>
                      <div className="mock-role-selector">
                        <span>Senior Frontend Developer</span>
                        <span className="role-dropdown-icon">▼</span>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '0.35s' }}>
                      <div className="mock-validity-row">
                        <div className="mock-validity-field">
                          <span className="vf-label">Interview Opens</span>
                          <span className="vf-value">Jun 22, 2026 10:00 AM</span>
                        </div>
                        <div className="mock-validity-field">
                          <span className="vf-label">Closes At</span>
                          <span className="vf-value">Jun 28, 2026 6:00 PM</span>
                        </div>
                      </div>
                    </div>
                    <div className="mock-step" style={{ animationDelay: '0.7s' }}>
                      <div className="mock-interview-preview">
                        <div className="mock-candidate-action">
                          <span className="action-dot"></span>
                          Candidate opens link → Uploads Resume → Interview starts
                        </div>
                        <div className="mock-chat-bubble">
                          <div className="mock-chat-sender">
                            <span className="sender-dot"></span>
                            Indu — AI Interviewer
                          </div>
                          <div className="mock-chat-msg">
                            "I see you have experience with React on your resume. Based on current industry standards, how do you handle state optimization at scale?"
                          </div>
                          <div className="mock-question-sources">
                            <span className="mock-q-source src-resume">Resume</span>
                            <span className="mock-q-source src-jd">JD</span>
                            <span className="mock-q-source src-market">Industry</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="mock-csv-btn">
                      <Icons.Download style={{ width: '13px', height: '13px' }} />
                      Download AI Interview Results (CSV)
                    </div>
                  </div>
                )}
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
      <section className="faa-section">
          <div className="faa-section-header">
            <span className="faa-section-tag faa-tag-blue">Choose Your Workflow</span>
            <h2>Manual Control or Full Automation</h2>
            <p>
              Whether you prefer hands-on control at every step or want AI to run the entire pipeline autonomously — VerifiHireAI adapts to your hiring style.
            </p>
          </div>

          <ScrollReveal>
            <div className="faa-comparison-grid">
            {/* Manual Mode Card */}
            <div className="faa-compare-card-wrapper manual-wrapper">
              <div className="faa-compare-card manual-card" onClick={() => handleModeChange(0)}>
                <div className="compare-card-header">
                  <div className="compare-icon manual-icon">🔧</div>
                  <div>
                    <h3>
                      <WordByWord text="Manual Mode" startIndexRef={manualIndex} />
                    </h3>
                    <div className="compare-subtitle">
                      <WordByWord text="Step-by-step recruiter control" startIndexRef={manualIndex} />
                    </div>
                  </div>
                </div>
                <ul className="compare-steps-list">
                  <li>
                    <span className="step-num blue">1</span>
                    <span>
                      <WordByWord boldText="Resume Screening" text=" — Create role, upload resumes, AI matches against JD. Pass/fail results downloadable as CSV." startIndexRef={manualIndex} />
                    </span>
                  </li>
                  <li>
                    <span className="step-num blue">2</span>
                    <span>
                      <WordByWord boldText="AI Assessment" text=" — Select role, invite candidates with link validity date/time. Adaptive questions that never repeat. Results in CSV." startIndexRef={manualIndex} />
                    </span>
                  </li>
                  <li>
                    <span className="step-num blue">3</span>
                    <span>
                      <WordByWord boldText="AI Interview" text=" — Candidate uploads resume via link. Indu asks JD, resume & market-based questions. Interview results in CSV." startIndexRef={manualIndex} />
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Automatic Mode Card */}
            <div className="faa-compare-card-wrapper auto-wrapper">
              <div className="faa-compare-card auto-card" onClick={() => handleModeChange(1)}>
                <div className="compare-card-header">
                  <div className="compare-icon auto-icon">⚡</div>
                  <div>
                    <h3>
                      <WordByWord text="Fully Automatic Mode" startIndexRef={autoIndex} />
                    </h3>
                    <div className="compare-subtitle">
                      <WordByWord text="One click, end-to-end AI pipeline" startIndexRef={autoIndex} />
                    </div>
                  </div>
                </div>
                <ul className="compare-steps-list">
                  <li>
                    <span className="step-num green">1</span>
                    <span>
                      <WordByWord text="Create JD with role name and paste job description" startIndexRef={autoIndex} />
                    </span>
                  </li>
                  <li>
                    <span className="step-num green">2</span>
                    <span>
                      <WordByWord text="Upload all candidate resumes at once" startIndexRef={autoIndex} />
                    </span>
                  </li>
                  <li>
                    <span className="step-num green">3</span>
                    <span>
                      <WordByWord text="Set date ranges for AI Assessment and AI Interview windows" startIndexRef={autoIndex} />
                    </span>
                  </li>
                  <li>
                    <span className="step-num green">4</span>
                    <span>
                      <WordByWord text="Click Generate — validates the link and activates the full AI pipeline" startIndexRef={autoIndex} />
                    </span>
                  </li>
                  <li>
                    <span className="step-num green">5</span>
                    <span>
                      <WordByWord text="AI auto-matches resumes → auto-sends assessments → auto-schedules interviews" startIndexRef={autoIndex} />
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* ═══════ MANUAL MODE MATRIX ═══════ */}
      <section className="faa-section faa-section-divider">
        <div className="faa-section-header">
          <span className="faa-section-tag faa-tag-purple">Manual Mode</span>
          <h2>Recruiter Command Matrix</h2>
          <p>
            Full control at every stage. Manage resume screening, assessment distribution, and interview scheduling manually.
          </p>
        </div>

        <ScrollReveal lazy={true}>
          <div className="faa-matrix-grid">
            {/* Card 1: Resume Screening */}
            <div className="faa-matrix-card-wrapper" style={{ animationDelay: '0.1s' }}>
              <div className="faa-matrix-card">
                <div className="matrix-card-header">
                  <span className="matrix-step">Phase 01</span>
                  <div className="matrix-icon-wrap purple-glow">
                    <Icons.Brain style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                  </div>
                </div>
                <h3>Resume Screening</h3>
                <p>Create a job role, upload candidate resumes in bulk, and let AI screen them against the JD. Candidates who pass the threshold are exported as a CSV file.</p>
                <div className="matrix-widget excel-widget">
                  <div className="excel-row-preview">
                    <span className="excel-preview-name">31 of 48 Qualified</span>
                    <span className="excel-preview-badge">CSV Ready</span>
                  </div>
                  <button className="matrix-excel-btn">
                    <Icons.Download style={{ width: '13px', height: '13px' }} />
                    <span>Download CSV</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Card 2: AI Assessment */}
            <div className="faa-matrix-card-wrapper" style={{ animationDelay: '0.3s' }}>
              <div className="faa-matrix-card">
                <div className="matrix-card-header">
                  <span className="matrix-step">Phase 02</span>
                  <div className="matrix-icon-wrap purple-glow">
                    <Icons.Code style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                  </div>
                </div>
                <h3>AI Assessment</h3>
                <p>Select role, invite candidates by setting date & time for link validity. Adaptive question pool ensures questions never repeat. Results exported as CSV.</p>
                <div className="matrix-widget send-widget">
                  <span className="send-status">No-Repeat Questions</span>
                  <button className="matrix-send-btn">
                    <Icons.Send style={{ width: '12px', height: '12px' }} />
                    <span>Send Invites</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Card 3: AI Interview */}
            <div className="faa-matrix-card-wrapper" style={{ animationDelay: '0.5s' }}>
              <div className="faa-matrix-card">
                <div className="matrix-card-header">
                  <span className="matrix-step">Phase 03</span>
                  <div className="matrix-icon-wrap purple-glow">
                    <Icons.Mic style={{ width: '20px', height: '20px', color: '#A78BFA' }} />
                  </div>
                </div>
                <h3>AI Voice Interview</h3>
                <p>Select role, set interview window. Candidate opens link, uploads resume, and Indu interviews them using JD, resume, and current industry market questions.</p>
                <div className="matrix-widget interview-widget">
                  <span className="interview-status">JD + Resume + Market</span>
                  <button className="matrix-interview-btn">
                    <Icons.Mic style={{ width: '12px', height: '12px' }} />
                    <span>Schedule Interview</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </section>

      {/* ═══════ AUTOMATIC MODE FUNNEL ═══════ */}
      <section className="faa-section faa-section-divider">
        <div className="faa-section-header">
          <span className="faa-section-tag faa-tag-emerald">Fully Automatic Mode</span>
          <h2>Autonomous AI Pipeline Funnel</h2>
          <p>
            Configure once, click generate, and let AI execute the complete hiring sequence end-to-end without manual intervention.
          </p>
        </div>

        <ScrollReveal>
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
              <div className="funnel-stage" style={{ animationDelay: '0.2s' }}>
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
              <div className="funnel-stage" style={{ animationDelay: '0.5s' }}>
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
              <div className="funnel-stage" style={{ animationDelay: '0.8s' }}>
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
              <div className="funnel-stage" style={{ animationDelay: '1.1s' }}>
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
              <div className="funnel-stage" style={{ animationDelay: '1.4s' }}>
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
            <div className="faa-funnel-console-wrapper" style={{ animationDelay: '1.7s' }}>
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
        </ScrollReveal>
      </section>

      {/* ═══════ FEATURE CARDS ═══════ */}
      <section className="faa-section">
        <div className="faa-section-header">
          <span className="faa-section-tag faa-tag-green">Core Capabilities</span>
          <h2>What Powers the Pipeline</h2>
          <p>
            Three AI-driven pillars that work together across both manual and automatic workflows.
          </p>
        </div>

        <ScrollReveal>
          <div className="faa-cards-grid">
            {/* Card 1: AI Resume Screening */}
            <div className="faa-feature-card-wrapper" style={{ animationDelay: '0.1s' }}>
              <div className="faa-feature-card">
                <div className="faa-card-icon blue">
                  <Icons.Brain style={{ width: '24px', height: '24px' }} />
                </div>
                <h3>AI Resume Screening</h3>
                <p>
                  NLP-powered matching compares each resume against the job description. Configurable threshold scoring ensures only qualified candidates advance — results downloadable as Excel.
                </p>
              </div>
            </div>

            {/* Card 2: AI Assessment */}
            <div className="faa-feature-card-wrapper" style={{ animationDelay: '0.3s' }}>
              <div className="faa-feature-card">
                <div className="faa-card-icon purple">
                  <Icons.Code style={{ width: '24px', height: '24px' }} />
                </div>
                <h3>AI Assessment</h3>
                <p>
                  AI-generated MCQ question pools and coding challenges tailored to the role. Proctored environment with identity verification, tab-switch detection, and automated grading.
                </p>
              </div>
            </div>

            {/* Card 3: AI Interview with Indu */}
            <div className="faa-feature-card-wrapper" style={{ animationDelay: '0.5s' }}>
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
          </div>
        </ScrollReveal>
      </section>

      {/* ═══════ WHY CHOOSE US ═══════ */}
      <section className="faa-section faa-section-divider">
        <div className="faa-section-header">
          <span className="faa-section-tag faa-tag-blue">Why VerifiHireAI</span>
          <h2>Built to Eliminate the Hiring Bottleneck</h2>
          <p>
            Traditional hiring drains HR teams with weeks of manual screening, scheduling, and follow-ups. We built VerifiHireAI to replace that entire burden with an AI-first pipeline.
          </p>
        </div>

        <ScrollReveal>
          <div className="faa-before-after-grid">
            {/* BEFORE Card */}
            <div className="faa-ba-card-wrapper before-wrapper">
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
            </div>

            {/* AFTER Card */}
            <div className="faa-ba-card-wrapper after-wrapper">
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
          </div>
        </ScrollReveal>

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

      </div>
      <Footer />
    </>
  );
}
