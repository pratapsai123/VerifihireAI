import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import '../styles/FeatureLiveInterview.css';

function FeatureLiveInterview() {
  useEffect(() => {
    window.scrollTo(0, 0);
    const appScrollEl = document.querySelector('.app-scroll');
    if (appScrollEl) {
      appScrollEl.scrollTop = 0;
    }
  }, []);

  return (
    <>
      <MainHeader />
      <div className="li-page">
        <div className="li-top-bg">
        {/* ── HERO ── */}
      <section className="li-hero">
        <div className="li-hero-inner">
          {/* Left: Text */}
          <div className="li-hero-text">
            <h1>
              Interview smarter.<br />
              <span className="li-grad">Hire with confidence.</span>
            </h1>
            <p>
              Run structured, fraud-proof technical interviews — with real-time video, screen sharing,
              and collaborative panelists — all built from scratch, no external services required.
            </p>

          </div>

          {/* Right: Mockup */}
          <div className="li-hero-mockup">
            <div className="interview-mockup">
              <div className="mockup-header">
                <div className="mockup-dots">
                  <div className="li-dot li-dot-r"></div>
                  <div className="li-dot li-dot-y"></div>
                  <div className="li-dot li-dot-g"></div>
                </div>
                <div className="mockup-title">Live Interview — Interviewer View</div>
                <div className="rec-badge">
                  <div className="rec-dot"></div>
                  REC
                </div>
              </div>

              <div className="mockup-body">
                {/* Panelist Video */}
                <div className="vid-feed vid-main">
                  <div className="vid-avatar av-blue">P1</div>
                  <div className="vid-label">Panelist 1 (You)</div>
                  <div className="vid-status vid-status-live"></div>
                </div>

                {/* Candidate Video */}
                <div className="vid-feed vid-candidate">
                  <div className="vid-avatar av-green">CA</div>
                  <div className="vid-label">Candidate</div>
                  <div className="vid-status vid-status-live"></div>
                </div>

                {/* Scoring Side Panel */}
                <div className="panel-side">
                  <div className="score-card">
                    <div className="score-title">📋 Live Scoring</div>
                    <div className="score-item">
                      <div className="score-label">Problem Solving</div>
                      <div className="score-bar-wrap">
                        <div className="score-bar" style={{ width: '75%' }}></div>
                      </div>
                      <div className="score-num">7.5</div>
                    </div>
                    <div className="score-item">
                      <div className="score-label">Data Structures</div>
                      <div className="score-bar-wrap">
                        <div className="score-bar" style={{ width: '80%' }}></div>
                      </div>
                      <div className="score-num">8.0</div>
                    </div>
                    <div className="score-item">
                      <div className="score-label">Communication</div>
                      <div className="score-bar-wrap">
                        <div className="score-bar" style={{ width: '90%', background: '#10b981' }}></div>
                      </div>
                      <div className="score-num">9.0</div>
                    </div>
                    <div className="score-item">
                      <div className="score-label">System Design</div>
                      <div className="score-bar-wrap">
                        <div className="score-bar" style={{ width: '65%', background: '#a78bfa' }}></div>
                      </div>
                      <div className="score-num">6.5</div>
                    </div>
                  </div>
                  <div className="verdict-card">
                    <div className="verdict-label">⭐ Panel Avg</div>
                    <div className="verdict-val">
                      7.8<span style={{ fontSize: '13px', color: '#94a3b8' }}>/10</span>
                    </div>
                    <div className="verdict-sub">3 of 3 panelists rated</div>
                  </div>
                </div>
              </div>

              <div className="mockup-footer">
                <div className="mockup-controls">
                  <div className="ctrl-btn" title="Mute/Unmute">🎤</div>
                  <div className="ctrl-btn" title="Camera">📷</div>
                  <div className="ctrl-btn" title="Screen Share">🖥</div>
                  <div className="ctrl-btn ctrl-btn-danger" title="End Call">📵</div>
                </div>
                <div className="timer-badge">⏱ 42:17</div>
                <div className="panelists-row">
                  <div className="p-avatar-sm pa1">P1</div>
                  <div className="p-avatar-sm pa2">P2</div>
                  <div className="p-avatar-sm pa3">P3</div>
                  <div className="p-count">+ Candidate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <div className="li-stats">
        <div className="stat-item">
          <div className="stat-num"><span className="li-accent">3</span> + 1</div>
          <div className="stat-label">Panelists + candidate per session</div>
        </div>
        <div className="stat-item">
          <div className="stat-num">100<span className="li-accent">%</span></div>
          <div className="stat-label">In-house, no third-party services</div>
        </div>
        <div className="stat-item">
          <div className="stat-num"><span className="li-accent">∞</span></div>
          <div className="stat-label">Unique interview links generated</div>
        </div>
      </div>
      </div>

      {/* ── HOW IT WORKS ── */}
      <section className="how-it-works-section">
        <div className="li-section" style={{ maxWidth: '1200px', margin: '0 auto', padding: 0 }}>
        <div className="section-tag">How it works</div>
        <h2 className="section-h2">
          From invite to decision<br />in one platform.
        </h2>
        <p className="section-sub">
          No scheduling tools, no external video apps, no spreadsheets. The entire interview
          lifecycle lives here.
        </p>
        <div className="how-timeline">
          <div className="tl-item tl-left">
            <div className="tl-dot"></div>
            <div className="tl-card-container">
              <div className="tl-card">
                <div className="tl-num-watermark">01</div>
                <div className="tl-content">
                  <h3>Generate a unique interview link</h3>
                  <p>
                    Create a session in seconds. The platform generates a one-time secure link that
                    ties the candidate and panelists to that specific interview slot — no account
                    required for candidates to join.
                  </p>
                  <div className="tl-chips">
                    <div className="chip chip-blue">One-click setup</div>
                    <div className="chip chip-blue">Unique per session</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="tl-image-container">
              <img src={require('../assets/step1.png')} alt="Generate Link" />
            </div>
          </div>

          <div className="tl-item tl-right">
            <div className="tl-dot"></div>
            <div className="tl-card-container">
              <div className="tl-card">
                <div className="tl-num-watermark">02</div>
                <div className="tl-content">
                  <h3>Panelists join — up to 3 at once</h3>
                  <p>
                    Send separate panelist links to each interviewer. All three can join simultaneously
                    alongside the candidate, see live video feeds, and collaborate without stepping on
                    each other.
                  </p>
                  <div className="tl-chips">
                    <div className="chip chip-purple">3 panelists max</div>
                    <div className="chip chip-purple">Independent sessions</div>
                    <div className="chip chip-purple">Real-time sync</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="tl-image-container">
              <img src={require('../assets/step2.png')} alt="Panelists Join" />
            </div>
          </div>

          <div className="tl-item tl-left">
            <div className="tl-dot"></div>
            <div className="tl-card-container">
              <div className="tl-card">
                <div className="tl-num-watermark">03</div>
                <div className="tl-content">
                  <h3>Conduct the interview with full tools</h3>
                  <p>
                    Run a live WebRTC session with video, audio, and screen share. Anti-fraud
                    monitoring runs passively in the background — tab switches and suspicious behaviour
                    are flagged automatically.
                  </p>
                  <div className="tl-chips">
                    <div className="chip chip-blue">WebRTC video</div>
                    <div className="chip chip-blue">Screen share</div>
                    <div className="chip chip-blue">Fraud detection active</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="tl-image-container">
              <img src={require('../assets/step3.png')} alt="Conduct Interview" />
            </div>
          </div>

          <div className="tl-item tl-right">
            <div className="tl-dot"></div>
            <div className="tl-card-container">
              <div className="tl-card">
                <div className="tl-num-watermark">04</div>
                <div className="tl-content">
                  <h3>Each panelist submits independent feedback</h3>
                  <p>
                    After the session, every panelist rates the candidate on defined rubric dimensions.
                    Scores are aggregated into a combined panel average, giving hiring managers a clear,
                    bias-reduced signal.
                  </p>
                  <div className="tl-chips">
                    <div className="chip chip-green">Per-panelist scoring</div>
                    <div className="chip chip-green">Averaged verdict</div>
                    <div className="chip chip-green">Select or reject</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="tl-image-container">
              <img src={require('../assets/step4.png')} alt="Submit Feedback" />
            </div>
          </div>
        </div>
        </div>
      </section>

      {/* ── COLLABORATIVE PANELS ── */}
      <section className="collaborative-section">
        <div className="li-section" style={{ maxWidth: '1200px', margin: '0 auto', padding: 0 }}>
        <div style={{ textAlign: 'center', maxWidth: '700px', margin: '0 auto' }}>
          <div className="section-tag" style={{ margin: '0 auto 16px' }}>Collaborative Panels</div>
          <h2 className="section-h2">
            Three voices,<br />one decision.
          </h2>
          <p className="section-sub" style={{ margin: '0 auto' }}>
            Each panelist scores independently — then the platform surfaces the aggregated verdict
            so hiring never comes down to a single opinion.
          </p>
        </div>
        <div className="cp-flowchart">
          <div className="cp-panelists">
            <div className="cp-card">
              <div className="cp-avatar" style={{ background: 'rgba(139,92,246,0.25)', color: '#c4b5fd', border: '1px solid rgba(139,92,246,0.35)' }}>RK</div>
              <div className="cp-name">Ravi Kumar</div>
              <div className="cp-role">Senior Engineer<br/>Technical Round</div>
              <div className="cp-score" style={{ color: '#c4b5fd' }}>8.2</div>
            </div>
            <div className="cp-card">
              <div className="cp-avatar" style={{ background: 'rgba(245,158,11,0.25)', color: '#fde68a', border: '1px solid rgba(245,158,11,0.35)' }}>PS</div>
              <div className="cp-name">Priya Sharma</div>
              <div className="cp-role">Engineering Manager<br/>Culture Fit</div>
              <div className="cp-score" style={{ color: '#fde68a' }}>7.5</div>
            </div>
            <div className="cp-card">
              <div className="cp-avatar" style={{ background: 'rgba(236,72,153,0.25)', color: '#f9a8d4', border: '1px solid rgba(236,72,153,0.35)' }}>AT</div>
              <div className="cp-name">Arjun Tiwari</div>
              <div className="cp-role">Tech Lead<br/>System Design</div>
              <div className="cp-score" style={{ color: '#f9a8d4' }}>8.8</div>
            </div>
          </div>

          <div className="cp-connections">
            <svg width="100%" height="100%" viewBox="0 0 800 100" preserveAspectRatio="none">
              <path d="M 140 0 C 140 60, 400 30, 400 100" stroke="rgba(16,185,129,0.3)" strokeWidth="3" fill="none" strokeDasharray="6 6" />
              <path d="M 400 0 L 400 100" stroke="rgba(16,185,129,0.3)" strokeWidth="3" fill="none" strokeDasharray="6 6" />
              <path d="M 660 0 C 660 60, 400 30, 400 100" stroke="rgba(16,185,129,0.3)" strokeWidth="3" fill="none" strokeDasharray="6 6" />
            </svg>
          </div>

          <div className="cp-verdict-container">
            <div className="cp-verdict-card">
              <div className="cp-verdict-title">Panel Verdict</div>
              <div className="cp-verdict-score">8.17 <span style={{fontSize: '24px', color: '#94a3b8', fontWeight: 600}}>/10</span></div>
              <div className="cp-verdict-tag">✓ SELECTED</div>
              <div className="cp-verdict-sub">All 3 panelists have submitted</div>
            </div>
          </div>
        </div>
        </div>
      </section>

      {/* ── SECURITY ── */}
      <section className="security-section">
        <div className="li-section" style={{ maxWidth: '1200px', margin: '0 auto', padding: 0 }}>
        <div className="section-tag">Security</div>
        <h2 className="section-h2">
          Built-in integrity,<br />zero compromises.
        </h2>
        <p className="section-sub">
          Anti-cheat runs passively throughout the session so your team can focus on evaluating
          talent, not policing behaviour.
        </p>
        <div className="security-grid">
          <div className="sec-card">
            <div className="sec-icon">👁</div>
            <div className="sec-label">Tab Switch Detection</div>
            <div className="sec-desc">
              Every time the candidate leaves the interview tab, it's logged and flagged for
              reviewers.
            </div>
          </div>
          <div className="sec-card">
            <div className="sec-icon">⌨</div>
            <div className="sec-label">Shortcut Disabled</div>
            <div className="sec-desc">
              Copy-paste and common keyboard shortcuts are blocked during active coding assessment.
            </div>
          </div>
          <div className="sec-card">
            <div className="sec-icon">🛡</div>
            <div className="sec-label">Proxy Detection</div>
            <div className="sec-desc">
              Detects VPNs, proxies, and unusual network conditions that may indicate a third-party
              proxy interview.
            </div>
          </div>
        </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="li-cta">
        <h2>
          Ready to interview<br />with confidence?
        </h2>
        <p>
          No third-party tools. No integration headaches. Just a complete, secure interview
          platform you own entirely.
        </p>
        <div className="cta-btns">
          <Link to="/signup" className="btn-cta-primary">Start Free Trial</Link>
          <Link to="/contact" className="btn-cta-outline">Book a Demo</Link>
        </div>
        <div className="cta-note">
          No credit card required · Up to 3 panelists per session · Unlimited interview links
        </div>
      </section>
      </div>
      <Footer />
    </>
  );
}

export default FeatureLiveInterview;
