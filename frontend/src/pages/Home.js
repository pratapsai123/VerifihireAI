import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';

function Home() {
  useEffect(() => {
    // Initialize AOS
    if (window.AOS) {
      window.AOS.init({
        duration: 800,
        once: true,
        offset: 50,
      });
    }

    // Initialize Particle.js only if hero container exists
    if (window.particlesJS && document.getElementById('particles-js')) {
      window.particlesJS('particles-js', {
        particles: {
          number: { value: 60, density: { enable: true, value_area: 800 } },
          color: { value: '#ffffff' },
          shape: {
            type: 'circle',
            stroke: { width: 0, color: '#000000' },
            polygon: { nb_sides: 5 },
          },
          opacity: {
            value: 0.3,
            random: false,
            anim: { enable: false, speed: 1, opacity_min: 0.1, sync: false },
          },
          size: {
            value: 3,
            random: true,
            anim: {
              enable: false,
              speed: 40,
              size_min: 0.1,
              sync: false,
            },
          },
          line_linked: {
            enable: true,
            distance: 150,
            color: '#ffffff',
            opacity: 0.2,
            width: 1,
          },
          move: {
            enable: true,
            speed: 2,
            direction: 'none',
            random: false,
            straight: false,
            out_mode: 'out',
            bounce: false,
            attract: { enable: false, rotateX: 600, rotateY: 1200 },
          },
        },
        interactivity: {
          detect_on: 'canvas',
          events: {
            onhover: { enable: true, mode: 'grab' },
            onclick: { enable: true, mode: 'push' },
            resize: true,
          },
          modes: {
            grab: { distance: 200, line_linked: { opacity: 0.4 } },
            bubble: {
              distance: 400,
              size: 40,
              duration: 2,
              opacity: 8,
              speed: 3,
            },
            repulse: { distance: 200, duration: 0.4 },
            push: { particles_nb: 4 },
            remove: { particles_nb: 2 },
          },
        },
        retina_detect: true,
      });
    }
  }, []);

  const scrollToSection = (e, sectionId) => {
    e.preventDefault();
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <MainHeader />
      <main>
        {/*
          HERO SECTION
          Focus: "Hire Real Talent" & "Stop Proxies"
        */}
        <section className="hero-section hero-gradient">
          <div id="particles-js"></div>
          <div className="container hero-container hero-content">
            <h1 className="hero-title">
              Hire <span style={{ color: '#fbbf24' }}>Real Talent</span>,<br />
              <span style={{ color: '#f87171' }}>Not Proxies.</span>
            </h1>
            <p
              className="hero-subtitle"
              style={{ maxWidth: '48rem', margin: '0 auto 2.5rem auto' }}
            >
              VerifiHireAI is the only AI-powered platform that guarantees 100% authentic assessments.
              We detect multiple faces, screen sharing, and proxy users to ensure you recruit
              genuine candidates with confidence.
            </p>
            <div
              style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}
            >
              <Link to="/signup" className="hero-cta">
                Start Hiring Now
              </Link>
              <button
                type="button"
                className="hero-cta"
                style={{
                  backgroundColor: 'transparent',
                  border: '2px solid white',
                  color: 'white',
                  padding: '0.85rem 2rem',
                }}
                onClick={(e) => scrollToSection(e, 'features')}
              >
                See How It Works
              </button>
            </div>
            <div style={{ marginTop: '3rem', color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>
              Trusted by leading tech teams to conduct secure interviews
            </div>
          </div>
        </section>

        {/*
          KEY FEATURES GRID
          Focus: High-level overview of the platform's capabilities
        */}
        <section id="features" className="section">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">The "Anti-Proxy" Hiring Platform</h2>
              <p className="section-subtitle">
                We've built a comprehensive suite of tools designed to eliminate fraud at every step of the hiring process.
              </p>
            </div>
            <div className="features-grid">
              {/* Feature 1: Anti-Proxy */}
              <div className="feature-card">
                <div className="feature-icon-wrapper" style={{ backgroundColor: '#fee2e2', color: '#ef4444' }}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <h3 className="feature-title">Fraud Detection</h3>
                <p className="feature-description">
                  Our advanced AI monitors for multiple faces, absence of face, object detection, and unauthorized screen switching.
                  We flag suspicious activity instantly.
                </p>
              </div>

              {/* Feature 2: Smart Assessments */}
              <div className="feature-card">
                <div className="feature-icon-wrapper" style={{ backgroundColor: '#e0e7ff', color: '#4f46e5' }}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="feature-title">AI Assessments</h3>
                <p className="feature-description">
                  Automatically generate technical questions based on skills (Python, React, Django) and experience level.
                  Or create your own custom challenges.
                </p>
              </div>

              {/* Feature 3: Live Interviews */}
              <div className="feature-card">
                <div className="feature-icon-wrapper" style={{ backgroundColor: '#dcfce7', color: '#16a34a' }}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="feature-title">Live Coding Studio</h3>
                <p className="feature-description">
                  Conduct real-time technical interviews with a collaborative code editor,
                  compiler support, and integrated video calling.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/*
          DEEP DIVE SECTION
          Focus: Explaining the "Why" and "How"
        */}
        <section className="section" style={{ backgroundColor: '#f9fafb' }}>
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">Why VerifiHireAI?</h2>
              <p className="section-subtitle">
                The traditional hiring process is broken. Resume fraud and proxy interviewers are on the rise.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center', marginBottom: '6rem' }}>
              <div>
                <h3 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem', color: '#1f2937' }}>
                  Stop Candidate Impersonation
                </h3>
                <p style={{ fontSize: '1.1rem', color: '#4b5563', lineHeight: '1.7', marginBottom: '2rem' }}>
                  Our system takes snapshots at random intervals during the assessment. If the face doesn't match the
                  candidate's profile, or if multiple people are detected, the session is flagged immediately.
                  You get a detailed report of every suspicious event.
                </p>
                <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {[
                    'Face Verification & Matching',
                    'Multiple Person Detection',
                    'Tab Switch Monitoring',
                    'Copy-Paste Prevention'
                  ].map((item, i) => (
                    <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#374151', fontWeight: '500' }}>
                      <span style={{ color: '#ef4444', fontWeight: 'bold' }}>✓</span> {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div
                style={{
                  backgroundColor: 'white',
                  borderRadius: '1rem',
                  padding: '2rem',
                  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                  border: '1px solid #e5e7eb'
                }}
              >
                {/* Visual Representation of Report */}
                <div style={{ paddingBottom: '1rem', borderBottom: '1px solid #f3f4f6', marginBottom: '1rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: '600', color: '#111827' }}>Candidate Report: John Doe</span>
                  <span style={{ color: '#ef4444', fontWeight: 'bold', backgroundColor: '#fee2e2', padding: '0.25rem 0.75rem', borderRadius: '999px', fontSize: '0.8rem' }}>High Risk</span>
                </div>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                  <div style={{ height: '8px', flex: 1, backgroundColor: '#e5e7eb', borderRadius: '4px' }}>
                    <div style={{ width: '85%', height: '100%', backgroundColor: '#ef4444', borderRadius: '4px' }}></div>
                  </div>
                  <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#ef4444' }}>85% Suspicion</span>
                </div>
                <p style={{ fontSize: '0.9rem', color: '#6b7280', fontStyle: 'italic' }}>
                  "Multiple faces detected at 14:02 mins..."
                </p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4rem', alignItems: 'center' }}>
              <div
                style={{
                  backgroundColor: 'white',
                  borderRadius: '1rem',
                  padding: '2rem',
                  boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                  border: '1px solid #e5e7eb'
                }}
              >
                {/* Visual Representation of Editor */}
                <div style={{ backgroundColor: '#1e293b', borderRadius: '0.5rem', padding: '1rem', color: '#60a5fa', fontFamily: 'monospace', fontSize: '0.9rem' }}>
                  <div style={{ color: '#94a3b8', marginBottom: '0.5rem' }}>// Real-time Python Assessment</div>
                  <div>def calculate_complexity(n):</div>
                  <div style={{ paddingLeft: '1.5rem', color: '#e2e8f0' }}>if n &lt;= 1: return 1</div>
                  <div style={{ paddingLeft: '1.5rem', color: '#e2e8f0' }}>return n * calculate_complexity(n-1)</div>
                  <div style={{ marginTop: '1rem', color: '#4ade80' }}>&gt; Test Cases Passed: 5/5</div>
                </div>
              </div>
              <div>
                <h3 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem', color: '#1f2937' }}>
                  Comprehensive Skill Evaluation
                </h3>
                <p style={{ fontSize: '1.1rem', color: '#4b5563', lineHeight: '1.7', marginBottom: '2rem' }}>
                  Beyond fraud detection, we provide deep insights into technical capability.
                  Our coding environment supports multiple languages and automatically grades against test cases.
                </p>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {['Python', 'JavaScript', 'Java', 'C++', 'SQL', 'React', 'Django'].map(skill => (
                    <span key={skill} style={{ backgroundColor: '#e0e7ff', color: '#4338ca', padding: '0.5rem 1rem', borderRadius: '0.5rem', fontWeight: '600', fontSize: '0.9rem' }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/*
          HOW IT WORKS (Workflow)
          Focus: Simplicity
        */}
        <section id="how-it-works" className="section" style={{ backgroundColor: 'white' }}>
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">Hiring Made Simple</h2>
              <p className="section-subtitle">
                From creating an assessment to making an offer, we streamline your entire recruitment workflow.
              </p>
            </div>
            <div className="steps-container">
              <div className="steps-grid">
                {[
                  { title: "Create Assessment", desc: "Select skills or upload your own questions.", delay: 100 },
                  { title: "Invite Candidates", desc: "Send secure, tracked invitation links.", delay: 200 },
                  { title: "Auto-Proctoring", desc: "AI monitors the session for fraud.", delay: 300 },
                  { title: "Review Reports", desc: "See scores and fraud flags instantly.", delay: 400 }
                ].map((step, idx) => (
                  <div className="step" key={idx}>
                    <div className="step-number">{idx + 1}</div>
                    <h3 className="step-title">{step.title}</h3>
                    <p className="step-description">{step.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="section" style={{ backgroundColor: '#4f46e5', color: 'white', textAlign: 'center' }}>
          <div className="container">
            <h2 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '1.5rem', color: 'white' }}>
              Ready to Hire with Confidence?
            </h2>
            <p style={{ fontSize: '1.25rem', marginBottom: '2.5rem', color: '#e0e7ff', maxWidth: '40rem', margin: '0 auto 2.5rem auto' }}>
              Join forward-thinking companies that prioritize authenticity and quality in their recruitment.
            </p>
            <Link
              to="/signup"
              style={{
                display: 'inline-block',
                backgroundColor: 'white',
                color: '#4f46e5',
                padding: '1rem 3rem',
                borderRadius: '999px',
                fontWeight: '700',
                fontSize: '1.25rem',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.2)',
                transition: 'all 0.3s ease',
                textDecoration: 'none'
              }}
            >
              Get Started for Free
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

export default Home;

