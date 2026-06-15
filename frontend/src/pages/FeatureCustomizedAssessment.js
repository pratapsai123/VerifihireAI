import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import '../styles/FeatureCustomizedAssessment.css';

function FeatureCustomizedAssessment() {
  const [animationKey, setAnimationKey] = useState(0);

  useEffect(() => {
    window.scrollTo(0, 0);
    const appScrollEl = document.querySelector('.app-scroll');
    if (appScrollEl) {
      appScrollEl.scrollTop = 0;
    }
    // Loop the hero animation every 24 seconds to fit the extended phase 2 flow
    const interval = setInterval(() => {
      setAnimationKey(prev => prev + 1);
    }, 24000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <MainHeader />
      <div className="fca-container">
      
      {/* Background Gradients */}
      <div className="fca-bg-glow fca-glow-1"></div>
      <div className="fca-bg-glow fca-glow-2"></div>
      <div className="fca-bg-glow fca-glow-3"></div>

      {/* Hero Section Split Layout */}
      <section className="fca-hero-split">
        <div className="fca-hero-left">
          <div className="fca-hero-badge">CUSTOM ASSESSMENTS</div>
          <h1>
            Where Assessment Meets <br/>
            <span className="text-gradient-primary">Hiring Excellence</span>
          </h1>
          <p>
            Design role-specific tests in seconds with AI, add your own custom questions, and automatically schedule interviews for candidates who pass.
          </p>
          <div className="fca-hero-cta">
            <Link to="/contact" className="fca-btn-gradient" style={{textDecoration: 'none', display: 'inline-block'}}>
              Get Started For Free
            </Link>
          </div>
        </div>

        <div className="fca-hero-right">
          <div key={animationKey} className="fca-builder-mockup fca-glass-card">
            <div className="mockup-header-dots">
              <span className="dot red"></span>
              <span className="dot yellow"></span>
              <span className="dot green"></span>
            </div>
            
            {/* Phase 1: Building the Assessment */}
            <div className="mockup-phase phase-1">
              <div className="builder-step step-role">
                <div className="builder-label">Target Role</div>
                <div className="builder-input">
                  <span className="typing-anim">Software Engineer</span>
                </div>
              </div>

              <div className="builder-step step-ai-load">
                <div className="ai-spinner"></div>
                <span className="ai-text">AI generating skill map...</span>
              </div>

              <div className="builder-step step-skills">
                <div className="builder-label">Required Skills</div>
                <div className="skill-tags-animated">
                  <span className="tag-anim t1">React.js</span>
                  <span className="tag-anim t2">Node.js</span>
                  <span className="tag-anim t3">System Design</span>
                  <span className="tag-anim t4">Algorithms</span>
                </div>
              </div>

              <div className="builder-step step-success">
                <i className="fas fa-check-circle"></i>
                <span>Assessment Ready: 15 Questions</span>
              </div>

              <div className="builder-step step-toggle">
                <div className="toggle-label">Enable Auto-Scheduling (60% Pass)</div>
                <div className="toggle-track">
                  <div className="toggle-thumb"></div>
                </div>
              </div>

              <div className="builder-step step-send">
                <div className="send-btn">
                  <span className="send-text"><i className="fas fa-paper-plane"></i> Send to Candidates</span>
                  <span className="sent-text"><i className="fas fa-check"></i> Invitations Sent!</span>
                </div>
              </div>
            </div>

            {/* Phase 2: Candidate Taking Exam */}
            <div className="mockup-phase phase-2">
              <div className="builder-step">
                <div className="builder-label" style={{color: '#60A5FA'}}>Candidate View: John Doe</div>
                <div className="exam-taking-anim">
                  <div className="exam-question-line line-1"></div>
                  <div className="exam-question-line line-2"></div>
                  <div className="exam-question-line line-3"></div>
                </div>
                <div className="candidate-exam-progress">
                  <div style={{fontSize: '0.8rem', color: '#94A3B8', marginTop: '16px'}}>Live Score Grading...</div>
                  <div className="exam-bar-bg">
                    <div className="exam-bar-fill"></div>
                  </div>
                  <div className="exam-score">Final Score: 85%</div>
                </div>
              </div>
              
              <div className="builder-step step-pass">
                <i className="fas fa-trophy" style={{fontSize: '1.5rem', color: '#F59E0B'}}></i>
                <div>
                  <div style={{color: '#fff', fontSize: '1.1rem'}}>Passed Assessment!</div>
                  <div style={{fontSize: '0.85rem', color: '#10B981', marginTop: '4px'}}>Exceeded 60% Threshold</div>
                </div>
              </div>
              
              <div className="builder-step step-book">
                <div className="send-btn green-btn">
                  <i className="fas fa-calendar-check"></i> Automated Booking Link Sent
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="fca-process-section">
        <div className="fca-process-container">
          <div className="fca-process-header">
            <div className="fca-process-badge">&bull; PROCESS</div>
            <h2>From job post to offer in weeks, not months</h2>
            <p>A fully automated pipeline that handles assessment creation, delivery, evaluation, and scheduling.</p>
          </div>

          <div className="fca-process-grid">
            <div className="fca-process-card">
              <div className="fca-process-number">01</div>
              <h3>Configure assessment</h3>
              <p>Select role, sub-roles, skills and experience level. Questions are fetched from our curated database instantly.</p>
            </div>
            
            <div className="fca-process-card border-left">
              <div className="fca-process-number">02</div>
              <h3>Invite candidates</h3>
              <p>Add candidate emails and send branded invitations in one click. Candidates get a timed, anti-cheat assessment experience.</p>
            </div>
            
            <div className="fca-process-card border-left">
              <div className="fca-process-number">03</div>
              <h3>Auto-score & filter</h3>
              <p>Results are evaluated instantly. Candidates who meet your pass threshold receive a live interview booking link automatically.</p>
            </div>
            
            <div className="fca-process-card border-left">
              <div className="fca-process-number">04</div>
              <h3>Sync & schedule</h3>
              <p>Candidates book from your real availability. Google Calendar invites go out automatically. Zero back-and-forth emails.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Steps Container */}
      <div className="fca-steps-container">

        {/* Step 1: Role-Based Generation */}
        <div className="fca-step">
          <div className="fca-step-content">
            <div className="fca-step-label text-gradient-primary">STEP 01</div>
            <h2>Intelligent Role-Based Generation</h2>
            <p>Simply select the role and sub-role you are hiring for. Our system instantly populates relevant skills and distributes questions perfectly aligned with the experience level you need.</p>
            <ul className="fca-step-features">
              <li><i className="fas fa-check-circle"></i> AI-curated skills library</li>
              <li><i className="fas fa-check-circle"></i> Dynamic question allocation</li>
              <li><i className="fas fa-check-circle"></i> Adjustable difficulty weighting</li>
            </ul>
          </div>
          <div className="fca-step-visual">
            <div className="fca-glass-card mockup-role-card">
              <div className="mockup-header">
                <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Create Assessment</span>
              </div>
              <div className="mockup-input-group">
                <span className="mockup-label">Role</span>
                <div className="mockup-dropdown">
                  <span>Frontend Developer</span>
                  <i className="fas fa-chevron-down"></i>
                </div>
              </div>
              <div className="mockup-input-group" style={{ marginTop: '24px' }}>
                <span className="mockup-label">Suggested Skills</span>
                <div className="mockup-skills-grid">
                  <div className="mockup-skill-tag">React</div>
                  <div className="mockup-skill-tag">JavaScript</div>
                  <div className="mockup-skill-tag">TypeScript</div>
                  <div className="mockup-skill-tag">Redux</div>
                  <div className="mockup-skill-tag">HTML/CSS</div>
                </div>
              </div>
              <div className="mockup-distribution">
                <div style={{ marginBottom: '16px', fontSize: '0.8rem', color: '#94A3B8' }}>Question Distribution (10 Questions)</div>
                <div className="mockup-dist-row">
                  <span>React</span>
                  <div className="mockup-dist-controls">
                    <i className="fas fa-minus" style={{ color: '#64748B', cursor: 'pointer' }}></i>
                    <span>4</span>
                    <i className="fas fa-plus" style={{ color: '#64748B', cursor: 'pointer' }}></i>
                  </div>
                </div>
                <div className="mockup-dist-row">
                  <span>JavaScript</span>
                  <div className="mockup-dist-controls">
                    <i className="fas fa-minus" style={{ color: '#64748B', cursor: 'pointer' }}></i>
                    <span>3</span>
                    <i className="fas fa-plus" style={{ color: '#64748B', cursor: 'pointer' }}></i>
                  </div>
                </div>
                <div className="mockup-dist-row">
                  <span>TypeScript</span>
                  <div className="mockup-dist-controls">
                    <i className="fas fa-minus" style={{ color: '#64748B', cursor: 'pointer' }}></i>
                    <span>3</span>
                    <i className="fas fa-plus" style={{ color: '#64748B', cursor: 'pointer' }}></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Step 2: Custom Questions */}
        <div className="fca-step reverse">
          <div className="fca-step-content" style={{ paddingLeft: '40px' }}>
            <div className="fca-step-label text-gradient-purple">STEP 02</div>
            <h2>Add Your Own Questions</h2>
            <p>Need something specific to your company? Easily inject your own custom questions into the generated assessment to test domain-specific knowledge.</p>
            <ul className="fca-step-features">
              <li><i className="fas fa-check-circle"></i> Multiple Choice & Selection</li>
              <li><i className="fas fa-check-circle"></i> True / False scenarios</li>
              <li><i className="fas fa-check-circle"></i> Direct PDF uploads</li>
            </ul>
          </div>
          <div className="fca-step-visual">
            <div className="mockup-question-types">
              <div className="mockup-q-card">
                <i className="fas fa-dot-circle mockup-q-icon"></i>
                <div className="mockup-q-title">Multiple Choice</div>
                <div className="mockup-q-desc">Single correct answer</div>
              </div>
              <div className="mockup-q-card">
                <i className="fas fa-tasks mockup-q-icon"></i>
                <div className="mockup-q-title">Multiple Selection</div>
                <div className="mockup-q-desc">Multiple correct answers</div>
              </div>
              <div className="mockup-q-card">
                <i className="fas fa-toggle-on mockup-q-icon"></i>
                <div className="mockup-q-title">True or False</div>
                <div className="mockup-q-desc">Binary scenarios</div>
              </div>
              <div className="mockup-q-card">
                <i className="fas fa-file-pdf mockup-q-icon"></i>
                <div className="mockup-q-title">PDF Uploading</div>
                <div className="mockup-q-desc">Extract from documents</div>
              </div>
            </div>
          </div>
        </div>

        {/* Step 3: Pass Thresholds */}
        <div className="fca-step">
          <div className="fca-step-content">
            <div className="fca-step-label text-gradient-green">STEP 03</div>
            <h2>Automated Interview Scheduling</h2>
            <p>Stop manually reviewing every test. Set a passing percentage threshold. If a candidate hits your target, they instantly receive a congratulations email with a link to book an interview slot with your team.</p>
            <ul className="fca-step-features">
              <li><i className="fas fa-check-circle"></i> Zero manual intervention required</li>
              <li><i className="fas fa-check-circle"></i> Accelerates time-to-hire</li>
              <li><i className="fas fa-check-circle"></i> Candidate-friendly experience</li>
            </ul>
          </div>
          <div className="fca-step-visual">
            <div className="fca-glass-card mockup-threshold-card">
              <div style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '24px' }}>Passing Threshold</div>
              <div className="mockup-circular-progress">
                <span className="mockup-progress-val">60%</span>
              </div>
              <div style={{ color: '#94A3B8', fontSize: '0.9rem', marginBottom: '16px' }}>Minimum score to trigger auto-invite</div>
              <div className="mockup-threshold-line"></div>
              <div className="mockup-email-toast">
                <i className="fas fa-paper-plane"></i> Invitation Sent Automatically!
              </div>
            </div>
          </div>
        </div>

        {/* Step 4: Calendar Sync */}
        <div className="fca-step reverse">
          <div className="fca-step-content" style={{ paddingLeft: '40px' }}>
            <div className="fca-step-label text-gradient-primary">STEP 04</div>
            <h2>Seamless Calendar Sync</h2>
            <p>Two-way calendar synchronization ensures double-bookings never happen. Interviewers set their availability, and candidates pick a slot that works for them within the next 7 days.</p>
            <ul className="fca-step-features">
              <li><i className="fas fa-check-circle"></i> Google Calendar & Outlook integration</li>
              <li><i className="fas fa-check-circle"></i> Real-time slot availability</li>
              <li><i className="fas fa-check-circle"></i> Automated calendar invites & reminders</li>
            </ul>
          </div>
          <div className="fca-step-visual">
            <div className="fca-glass-card mockup-calendar-split">
              <div className="mockup-cal-header">
                <span style={{ fontWeight: 700 }}>Select a Time Slot</span>
                <span style={{ color: '#64748B', fontSize: '0.8rem' }}>June 2026</span>
              </div>
              <div className="mockup-cal-days">
                <div className="mockup-cal-day">Mon<span>8</span></div>
                <div className="mockup-cal-day">Tue<span>9</span></div>
                <div className="mockup-cal-day active">Wed<span>10</span></div>
                <div className="mockup-cal-day">Thu<span>11</span></div>
                <div className="mockup-cal-day">Fri<span>12</span></div>
              </div>
              <div className="mockup-slots-grid">
                <div className="mockup-slot">10:00 AM</div>
                <div className="mockup-slot selected">11:00 AM</div>
                <div className="mockup-slot booked">12:00 PM</div>
                <div className="mockup-slot booked">1:00 PM</div>
                <div className="mockup-slot">2:00 PM</div>
                <div className="mockup-slot">4:00 PM</div>
              </div>
              <div className="mockup-integrations">
                <div className="mockup-int-badge">
                  <i className="fab fa-google" style={{ color: '#EA4335' }}></i> Google Sync
                </div>
                <div className="mockup-int-badge">
                  <i className="fab fa-windows" style={{ color: '#0078D4' }}></i> Outlook Sync
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Everything You Need Section */}
      <section className="fca-features-grid-section">
        <div className="fca-fg-header">
          <h2>Everything you need to hire smarter</h2>
          <p>Built for engineering teams that value speed and signal quality in equal measure.</p>
        </div>
        
        <div className="fca-fg-grid">
          <div className="fca-fg-card">
            <div className="fca-fg-icon" style={{background: 'rgba(167, 139, 250, 0.1)', color: '#C084FC'}}>
              <i className="fas fa-layer-group"></i>
            </div>
            <h3>Role-based question engine</h3>
            <p>Questions are sourced and distributed across skills based on your exact role and sub-roles. Adjust counts per skill with precision.</p>
            <div className="fca-fg-tags">
              <span className="fg-tag green">React</span>
              <span className="fg-tag green">TypeScript</span>
              <span className="fg-tag blue">System Design</span>
              <span className="fg-tag purple">Algorithms</span>
            </div>
          </div>
          
          <div className="fca-fg-card">
            <div className="fca-fg-icon" style={{background: 'rgba(52, 211, 153, 0.1)', color: '#34D399'}}>
              <i className="fas fa-user-shield"></i>
            </div>
            <h3>Anti-cheating proctoring</h3>
            <p>AI-powered tab-switch detection, fullscreen enforcement, and randomised question ordering keep every assessment honest and meaningful.</p>
            <div className="fca-fg-tags">
              <span className="fg-tag blue">Tab monitoring</span>
              <span className="fg-tag blue">Fullscreen lock</span>
              <span className="fg-tag purple">Shuffled questions</span>
            </div>
          </div>
          
          <div className="fca-fg-card">
            <div className="fca-fg-icon" style={{background: 'rgba(59, 130, 246, 0.1)', color: '#60A5FA'}}>
              <i className="fas fa-chart-pie"></i>
            </div>
            <h3>In-depth analytics</h3>
            <p>Gain actionable insights with detailed skill-based scorecards, percentile rankings, and comparative performance metrics for every candidate.</p>
            <div className="fca-fg-tags">
              <span className="fg-tag blue">Scorecards</span>
              <span className="fg-tag purple">Percentiles</span>
              <span className="fg-tag green">Benchmarking</span>
            </div>
          </div>
          
          <div className="fca-fg-card wide-card">
            <div className="wide-card-left">
              <div className="fca-fg-icon" style={{background: 'rgba(255, 255, 255, 0.1)', color: '#fff'}}>
                <i className="fas fa-link"></i>
              </div>
              <h3>Google Calendar sync</h3>
              <p>Every confirmed interview automatically creates a Google Calendar event for both interviewer and candidate &mdash; meeting links, reminders, and all context included. Zero manual steps.</p>
              <div className="fca-fg-tags">
                <span className="fg-tag green">Auto calendar invite</span>
                <span className="fg-tag green">Email reminders</span>
                <span className="fg-tag blue">One-click reschedule</span>
              </div>
            </div>
            <div className="wide-card-right">
              <div className="cal-preview-card">
                <div className="cal-preview-title">CALENDAR EVENT PREVIEW</div>
                <div className="cal-preview-body">
                  <div className="cal-time">WED, JUNE 10 &bull; 11:00 &ndash; 11:50 AM</div>
                  <div className="cal-title">Frontend Dev Interview</div>
                  <div className="cal-subtitle">with Rohan Varma</div>
                  <div className="cal-links">
                    <span><i className="fas fa-video" style={{marginRight:'6px'}}></i> Google Meet attached</span>
                    <span><i className="fas fa-bell" style={{marginRight:'6px', marginLeft:'12px'}}></i> Reminders set</span>
                  </div>
                </div>
                <div className="fca-fg-tags" style={{marginTop:'16px'}}>
                  <span className="fg-tag green"><i className="fas fa-check"></i> Confirmed</span>
                  <span className="fg-tag green">50 min session</span>
                  <span className="fg-tag blue">10 min break included</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Auto-scheduling Workflow Section */}
      <section className="fca-workflow-section">
        <div className="fca-workflow-container">
          <div className="fca-workflow-header">
            <div className="fca-process-badge" style={{borderColor: 'rgba(59, 130, 246, 0.4)', color: '#60A5FA'}}>&bull; AUTOMATION</div>
            <h2>How auto-scheduling works</h2>
            <p>Once you publish an assessment, the entire post-assessment workflow runs on autopilot.</p>
          </div>
          
          <div className="fca-timeline">
            <div className="fca-timeline-item">
              <div className="timeline-icon" style={{background: 'rgba(15, 23, 42, 1)', border: '1px solid rgba(255,255,255,0.1)', color: '#F97316'}}>
                <i className="fas fa-file-alt"></i>
              </div>
              <div className="timeline-content">
                <h3>Candidate completes assessment</h3>
                <p>The candidate finishes the timed assessment. Results are computed instantly &mdash; no manual review needed for scoring.</p>
              </div>
            </div>
            
            <div className="fca-timeline-item">
              <div className="timeline-icon" style={{background: 'rgba(15, 23, 42, 1)', border: '1px solid rgba(255,255,255,0.1)', color: '#F97316'}}>
                <i className="fas fa-bolt"></i>
              </div>
              <div className="timeline-content">
                <h3>Score checked against pass threshold</h3>
                <p>VerifiHireAI checks the score against your configured pass percentage (e.g. 60%). The decision is instant and objective.</p>
                <div className="timeline-tag"><i className="fas fa-bolt" style={{color:'#F59E0B'}}></i> Fully automated</div>
              </div>
            </div>
            
            <div className="fca-timeline-item">
              <div className="timeline-icon" style={{background: 'rgba(15, 23, 42, 1)', border: '1px solid rgba(255,255,255,0.1)', color: '#60A5FA'}}>
                <i className="fas fa-envelope-open-text"></i>
              </div>
              <div className="timeline-content">
                <h3>Booking link sent automatically</h3>
                <p>Passing candidates receive a personalised email with a link to view the interviewer's availability and book a 50-minute live session.</p>
                <div className="timeline-tag"><i className="fas fa-bullseye" style={{color:'#EC4899'}}></i> Smart candidate filtering</div>
              </div>
            </div>
            
            <div className="fca-timeline-item">
              <div className="timeline-icon" style={{background: 'rgba(15, 23, 42, 1)', border: '1px solid rgba(255,255,255,0.1)', color: '#FBBF24'}}>
                <i className="fas fa-calendar-alt"></i>
              </div>
              <div className="timeline-content">
                <h3>Candidate picks a slot</h3>
                <p>The candidate sees available slots from the next 7 days. Once booked, the slot is immediately locked &mdash; no double-bookings, ever.</p>
              </div>
            </div>
            
            <div className="fca-timeline-item">
              <div className="timeline-icon" style={{background: 'rgba(15, 23, 42, 1)', border: '1px solid rgba(255,255,255,0.1)', color: '#10B981'}}>
                <i className="fas fa-check-square"></i>
              </div>
              <div className="timeline-content">
                <h3>Google Calendar invite dispatched</h3>
                <p>Both parties receive a Google Calendar invite with meeting details and reminders. The interviewer's dashboard shows the slot as Booked &mdash; locked and confirmed.</p>
                <div className="timeline-tag"><i className="fas fa-bolt" style={{color:'#F59E0B'}}></i> Zero manual coordination</div>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* CTA Section */}
      <section className="fca-cta">
        <div className="fca-cta-card">
          <h2>Ready to transform your technical hiring?</h2>
          <p>Create your first Custom Assessment today and let the platform handle the heavy lifting of scheduling and grading.</p>
          <Link to="/contact" className="fca-btn-gradient" style={{textDecoration: 'none', display: 'inline-block'}}>
            Get Started For Free
          </Link>
        </div>
      </section>

      </div>
      <Footer />
    </>
  );
}

export default FeatureCustomizedAssessment;

