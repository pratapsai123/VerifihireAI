import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import DetectionDemo from '../components/DetectionDemo';
import '../styles/Home.css';
import featuresBg from '../assets/features-neural-bg.png'; // kept for future use — not rendered
import {
  ShieldCheck, Activity, Users, MousePointer2,
  Zap, BarChart3, ChevronRight, CheckCircle2,
  XCircle, Clock, TrendingUp, Lock, Globe,
  Star, Award, Target, Layers, ArrowRight,
  UserCheck, FileText, AlertTriangle, RefreshCw,
  Code2, Video, ClipboardList, MessageSquare, Trophy,
  Plus, Minus, Building2, GraduationCap, Briefcase, Monitor,
  CheckSquare, Zap as ZapIcon, CreditCard, Infinity, ChevronDown
} from 'lucide-react';

/* ─────────────────────────────────────────────
   Animated Counter Hook
───────────────────────────────────────────── */
function useCountUp(target, duration = 2000, start = false) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime = null;
    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, start]);
  return count;
}


/* ─────────────────────────────────────────────
   Scroll Reveal Component
───────────────────────────────────────────── */
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
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );
    const currentRef = ref.current;
    if (currentRef) observer.observe(currentRef);
    return () => {
      if (currentRef) observer.unobserve(currentRef);
    };
  }, []);

  return (
    <div ref={ref} className="home-scroll-reveal" style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  );
}

/* ─────────────────────────────────────────────
   CANDIDATE VS RECRUITER TABS
───────────────────────────────────────────── */
const perspectiveData = {
  recruiter: {
    badge: 'For Recruiters',
    icon: <Briefcase size={20} />,
    color: '#3B82F6',
    headline: 'Hire Smarter. Eliminate Bias. Cut Costs.',
    subtext: 'Everything you need to run a world-class screening process — without the manual grind.',
    points: [
      { icon: <ZapIcon size={16} />, title: 'Post & Go', desc: 'Create a job role in 2 minutes. AI auto-generates interview questions from the JD.' },
      { icon: <Users size={16} />, title: 'Bulk Invite Candidates', desc: 'Send interview links to 1,000+ candidates at once — no scheduling headaches.' },
      { icon: <ShieldCheck size={16} />, title: 'Built-in Fraud Detection', desc: 'Real-time identity checks so you always know who you\'re actually interviewing.' },
      { icon: <BarChart3 size={16} />, title: 'Instant AI Rankings', desc: 'Ranked shortlists with scores, flags and insights — ready the moment interviews end.' },
      { icon: <FileText size={16} />, title: 'One-Click Reports', desc: 'Auto-generated PDF reports for every candidate, ready to share with stakeholders.' },
      { icon: <Globe size={16} />, title: 'ATS-Ready Exports', desc: 'Export candidate data directly to Greenhouse, Lever, Workday and more.' },
    ],
    cta: null,
    mockStats: [{ label: 'Avg. time-to-shortlist', value: '4 hrs' }, { label: 'Cost saved per hire', value: '60%' }, { label: 'Fraud attempts blocked', value: '100%' }],
  },
  candidate: {
    badge: 'For Candidates',
    icon: <GraduationCap size={20} />,
    color: '#10B981',
    headline: 'Interview on Your Terms. Anytime. Anywhere.',
    subtext: 'No scheduling stress. No bias. A fair, structured interview experience built around you.',
    points: [
      { icon: <Clock size={16} />, title: 'Interview Anytime', desc: 'Take your AI interview 24/7 from any device — no waiting for a recruiter\'s calendar.' },
      { icon: <CheckCircle2 size={16} />, title: 'Structured & Fair', desc: 'Every candidate gets the same questions in the same order. Zero human bias.' },
      { icon: <ClipboardList size={16} />, title: 'Adaptive Questions', desc: 'The AI adapts based on your answers — letting you show depth and nuance.' },
      { icon: <Monitor size={16} />, title: 'Instant Feedback', desc: 'Receive a detailed score breakdown and feedback immediately after completing.' },
      { icon: <Lock size={16} />, title: 'Privacy First', desc: 'Your session data is GDPR-compliant and never shared without your consent.' },
      { icon: <Star size={16} />, title: 'One-Round Process', desc: 'Assessment, coding, and interview — all in a single seamless session.' },
    ],
    cta: null,
    mockStats: [{ label: 'Avg. completion time', value: '28 min' }, { label: 'Candidate satisfaction', value: '97%' }, { label: 'Rounds replaced', value: '3 → 1' }],
  },
};

function PerspectiveSection() {
  const [active, setActive] = useState('recruiter');
  const data = perspectiveData[active];

  return (
    <section className="persp-section">
      <div className="persp-container">
        <div className="persp-header">
          <span className="badge-dark">Built For Everyone</span>
          <h2>One Platform — Two Powerful Perspectives</h2>
          <p>Whether you\'re screening hundreds of applicants or stepping into your next opportunity, VerifiHireAI is designed for you.</p>
        </div>

        {/* Tab Toggle */}
        <div className="persp-tab-wrap">
          {['recruiter', 'candidate'].map(tab => (
            <button
              key={tab}
              className={`persp-tab ${active === tab ? 'persp-tab-active' : ''}`}
              style={active === tab ? { '--tc': perspectiveData[tab].color } : {}}
              onClick={() => setActive(tab)}
            >
              <span className="persp-tab-icon" style={{ color: active === tab ? perspectiveData[tab].color : 'rgba(255,255,255,0.4)' }}>
                {perspectiveData[tab].icon}
              </span>
              {perspectiveData[tab].badge}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="persp-content" key={active}>
          {/* Left: Points */}
          <div className="persp-left">
            <div className="persp-badge-pill" style={{ color: data.color, background: `${data.color}18`, border: `1px solid ${data.color}30` }}>
              {data.icon} {data.badge}
            </div>
            <h3 className="persp-headline">{data.headline}</h3>
            <p className="persp-subtext">{data.subtext}</p>
            <div className="persp-points">
              {data.points.map((p, i) => (
                <div className="persp-point" key={i}>
                  <div className="persp-point-icon" style={{ background: `${data.color}18`, color: data.color }}>{p.icon}</div>
                  <div>
                    <div className="persp-point-title">{p.title}</div>
                    <div className="persp-point-desc">{p.desc}</div>
                  </div>
                </div>
              ))}
            </div>
            {data.cta && (
              <Link to={data.cta.to} className="btn-primary-premium persp-cta" style={{ '--cta-color': data.color }}>
                {data.cta.label} <ArrowRight size={16} />
              </Link>
            )}
          </div>

          {/* Right: Mock Panel */}
          <div className="persp-right">
            <div className="persp-mock-card" style={{ '--mc': data.color }}>
              <div className="persp-mock-header">
                <div className="persp-mock-dots"><span /><span /><span /></div>
                <span className="persp-mock-title">VerifiHireAI — {data.badge}</span>
              </div>
              <div className="persp-mock-stats">
                {data.mockStats.map((s, i) => (
                  <div className="persp-mock-stat" key={i}>
                    <div className="persp-mock-val" style={{ color: data.color }}>{s.value}</div>
                    <div className="persp-mock-lbl">{s.label}</div>
                  </div>
                ))}
              </div>
              <div className="persp-mock-body">
                {data.points.slice(0, 4).map((p, i) => (
                  <div className="persp-mock-row" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
                    <CheckSquare size={13} color={data.color} />
                    <span>{p.title}</span>
                    <span className="persp-mock-done" style={{ background: `${data.color}20`, color: data.color }}>✓</span>
                  </div>
                ))}
              </div>
              <div className="persp-mock-glow" style={{ background: `radial-gradient(circle, ${data.color}25 0%, transparent 70%)` }} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   LIVE DEMO / DASHBOARD PREVIEW
───────────────────────────────────────────── */
const mockCandidates = [
  { name: 'Arjun Mehta', role: 'Frontend Engineer', score: 92, flag: false, status: 'Shortlisted' },
  { name: 'Priya Reddy', role: 'Data Scientist', score: 88, flag: false, status: 'Shortlisted' },
  { name: 'Rohan Singh', role: 'Frontend Engineer', score: 74, flag: true, status: 'Flagged' },
  { name: 'Anjali Nair', role: 'Backend Engineer', score: 95, flag: false, status: 'Shortlisted' },
  { name: 'Vikram Patel', role: 'DevOps', score: 61, flag: true, status: 'Review' },
];

function DemoSection() {
  const [hovered, setHovered] = useState(null);
  return (
    <section className="demo-section">
      <div className="demo-container">
        <div className="demo-header">
          <span className="badge-dark">Live Product Preview</span>
          <h2>See Exactly What You Get</h2>
          <p>A real-time look at the VerifiHireAI recruiter dashboard — rankings, fraud flags, and insights at a glance.</p>
        </div>

        {/* Browser Chrome Mock */}
        <div className="demo-browser">
          <div className="demo-browser-bar">
            <div className="demo-browser-dots"><span /><span /><span /></div>
            <div className="demo-browser-url">app.verifihire.ai / dashboard</div>
            <div className="demo-browser-actions">
              <span className="demo-live-dot" /> Live
            </div>
          </div>

          <div className="demo-browser-body">
            {/* Sidebar */}
            <div className="demo-sidebar">
              <div className="demo-sidebar-logo">✦ VH<span>AI</span></div>
              {['Dashboard', 'Candidates', 'Interviews', 'Analytics', 'Reports', 'Settings'].map((item, i) => (
                <div key={i} className={`demo-sidebar-item ${i === 1 ? 'demo-sidebar-active' : ''}`}>
                  {item}
                </div>
              ))}
            </div>

            {/* Main Panel */}
            <div className="demo-main">
              {/* Top Stats */}
              <div className="demo-top-stats">
                {[
                  { label: 'Total Applicants', val: '248', color: '#3B82F6' },
                  { label: 'Shortlisted', val: '34', color: '#10B981' },
                  { label: 'Fraud Flagged', val: '7', color: '#EF4444' },
                  { label: 'Avg. Score', val: '81%', color: '#F59E0B' },
                ].map((s, i) => (
                  <div className="demo-stat-card" key={i}>
                    <div className="demo-stat-val" style={{ color: s.color }}>{s.val}</div>
                    <div className="demo-stat-lbl">{s.label}</div>
                    <div className="demo-stat-bar" style={{ background: `${s.color}20` }}>
                      <div className="demo-stat-fill" style={{ width: `${[70, 28, 8, 81][i]}%`, background: s.color }} />
                    </div>
                  </div>
                ))}
              </div>

              {/* Candidate Table */}
              <div className="demo-table">
                <div className="demo-table-header">
                  <span>Candidate</span><span>Role</span><span>AI Score</span><span>Status</span>
                </div>
                {mockCandidates.map((c, i) => (
                  <div
                    key={i}
                    className={`demo-table-row ${hovered === i ? 'demo-row-hovered' : ''} ${c.flag ? 'demo-row-flagged' : ''}`}
                    onMouseEnter={() => setHovered(i)}
                    onMouseLeave={() => setHovered(null)}
                  >
                    <div className="demo-candidate">
                      <div className="demo-avatar" style={{ background: ['#3B82F620', '#10B98120', '#EF444420', '#8B5CF620', '#F59E0B20'][i], color: ['#3B82F6', '#10B981', '#EF4444', '#8B5CF6', '#F59E0B'][i] }}>
                        {c.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span>{c.name}</span>
                    </div>
                    <span className="demo-role">{c.role}</span>
                    <div className="demo-score-wrap">
                      <div className="demo-score-bar-bg">
                        <div className="demo-score-bar-fill" style={{ width: `${c.score}%`, background: c.score > 85 ? '#10B981' : c.score > 70 ? '#F59E0B' : '#EF4444' }} />
                      </div>
                      <span className="demo-score-num" style={{ color: c.score > 85 ? '#10B981' : c.score > 70 ? '#F59E0B' : '#EF4444' }}>{c.score}%</span>
                    </div>
                    <span className={`demo-status demo-status-${c.status.toLowerCase().replace(' ', '-')}`}>{c.flag ? '🚩 ' : ''}{c.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>


      </div>
    </section>
  );
}



/* ─────────────────────────────────────────────
   FAQ SECTION
───────────────────────────────────────────── */
const faqs = [
  { q: 'What happens after my free trial ends?', a: 'Your account moves to the Starter (free) plan automatically. No credit card is charged. You can upgrade anytime from your dashboard.' },
  { q: 'Is VerifiHireAI GDPR compliant?', a: 'Yes. All candidate data is encrypted at rest and in transit. We are fully GDPR-compliant with configurable data retention policies, right-to-erasure support, and a DPA available on request.' },
  { q: 'Can I integrate with our existing ATS?', a: 'On the Professional plan, you can export candidate data as CSV. Enterprise plans include native integrations with Greenhouse, Lever, Workday, SAP SuccessFactors, and more via our REST API.' },
  { q: 'How does the fraud detection work?', a: 'Our system performs real-time face verification, multi-person detection, browser tab-switch monitoring, audio anomaly detection, and device fingerprinting throughout the interview.' },
  { q: 'Can candidates use any device?', a: 'Yes — VerifiHireAI works on desktop, laptop, and mobile (Chrome, Firefox, Safari). A camera and microphone are required for full interview functionality.' },
  { q: 'How long does a typical AI interview take?', a: 'Most interviews are completed in 20–40 minutes depending on the role. Candidates can pause and resume if they have a stable internet connection.' },
  { q: 'Is the AI really unbiased?', a: 'Our AI scores only on predefined rubrics tied to job-relevant competencies. It has no access to candidate name, age, gender, or appearance — only responses.' },
  { q: 'Do you offer a white-label solution?', a: 'Yes, on Enterprise plans you can fully brand the interview platform with your company logo, colors, and custom domain.' },
];

function FAQSection() {
  const [open, setOpen] = useState(null);
  return (
    <section className="faq-section">
      <div className="faq-container">
        <div className="faq-header">
          <span className="badge-dark">FAQ</span>
          <h2>Frequently Asked Questions</h2>
          <p>Everything you need to know before you start. Can't find your answer? <Link to="/contact" className="faq-link">Talk to us →</Link></p>
        </div>
        <div className="faq-list">
          {faqs.map((faq, i) => (
            <div key={i} className={`faq-item ${open === i ? 'faq-open' : ''}`}>
              <button className="faq-question" onClick={() => setOpen(open === i ? null : i)}>
                <span>{faq.q}</span>
                <span className="faq-icon">{open === i ? <Minus size={18} /> : <Plus size={18} />}</span>
              </button>
              <div className="faq-answer">
                <p>{faq.a}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   All-in-One Platform Section (360° Circle)
───────────────────────────────────────────── */

// Platforms arranged in a 360° orbit around the VerifiHireAI center hub
const orbitFeatures = [
  { icon: <ClipboardList size={22} />, label: 'Assessments', sub: 'Role-based tests', color: '#3B82F6', prev: 'TestGorilla' },
  { icon: <Code2 size={22} />, label: 'Coding Rounds', sub: 'Live code execution', color: '#10B981', prev: 'HackerRank' },
  { icon: <Video size={22} />, label: 'AI Interviews', sub: 'Adaptive questioning', color: '#8B5CF6', prev: 'HireVue' },
  { icon: <ShieldCheck size={22} />, label: 'Fraud Detection', sub: 'Live identity check', color: '#F59E0B', prev: 'Manual review' },
  { icon: <MessageSquare size={22} />, label: 'Communication', sub: 'Candidate messaging', color: '#EC4899', prev: 'Email / Slack' },
  { icon: <BarChart3 size={22} />, label: 'Analytics', sub: 'Insight dashboards', color: '#06B6D4', prev: 'Excel / BI tools' },
  { icon: <Trophy size={22} />, label: 'Ranking & Reports', sub: 'Auto-generated PDFs', color: '#F97316', prev: 'Manual scoring' },
  { icon: <ShieldCheck size={22} />, label: 'Compliance', sub: 'GDPR & audit trails', color: '#6366F1', prev: 'Legal teams' },
];

function AllInOneSection() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  const [activeIdx, setActiveIdx] = useState(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVisible(true); },
      { threshold: 0.2 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  const total = orbitFeatures.length;
  const RADIUS = 230; // px from center to card center

  return (
    <section className="aio-section" ref={ref}>
      {/* ── Top Label: Previous Problem ── */}
      <div className="aio-top-badge">
        <span className="aio-before-pill">⚠ Previously — The Fragmented Hiring Problem</span>
      </div>
      <div className="aio-chaos-row">
        {['Assessments Platform', 'Coding Platform', 'Interview Platform', 'Analytics Platform', 'Compliance Tool', '+ More tools...'].map((t, i) => (
          <div key={i} className="aio-chaos-chip">
            <XCircle size={13} color="#EF4444" style={{ flexShrink: 0 }} />
            {t}
          </div>
        ))}
      </div>
      <div className="aio-chaos-caption">Organizations juggled 6+ separate platforms, logins, and data silos just to hire one candidate.</div>

      {/* ── Arrow Down ── */}
      <div className="aio-arrow-wrap">
        <div className="aio-arrow-line" />
        <div className="aio-arrow-label">VerifiHireAI Changes Everything</div>
        <div className="aio-arrow-line" />
      </div>

      {/* ── 360° Orbit Diagram ── */}
      <div className="aio-orbit-container" style={{ '--radius': `${RADIUS}px` }}>
        {/* Rotating ring (decorative) */}
        <div className={`aio-ring aio-ring-1 ${visible ? 'aio-ring-spin' : ''}`} />
        <div className={`aio-ring aio-ring-2 ${visible ? 'aio-ring-spin-rev' : ''}`} />
        <div className={`aio-ring aio-ring-3`} />

        {/* SVG connector lines from center to each node */}
        <svg className="aio-svg-lines" viewBox="0 0 600 600">
          {orbitFeatures.map((f, i) => {
            const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
            const cx = 300 + (RADIUS - 40) * Math.cos(angle);
            const cy = 300 + (RADIUS - 40) * Math.sin(angle);
            return (
              <line
                key={i}
                x1="300" y1="300"
                x2={cx} y2={cy}
                stroke={activeIdx === i ? f.color : 'rgba(255,255,255,0.12)'}
                strokeWidth={activeIdx === i ? '2' : '1'}
                strokeDasharray="5 4"
                className={visible ? 'aio-line-draw' : ''}
                style={{ '--delay': `${i * 0.12}s`, '--color': f.color }}
              />
            );
          })}
          {/* Outer orbit circle path */}
          <circle cx="300" cy="300" r={RADIUS} fill="none"
            stroke="rgba(255,255,255,0.06)" strokeWidth="1" strokeDasharray="4 6" />
        </svg>

        {/* Center Hub */}
        <div className="aio-center-hub">
          <div className="aio-hub-glow" />
          <div className="aio-hub-pulse" />
          <div className="aio-hub-inner">
            <span className="aio-hub-emoji">✦</span>
            <span className="aio-hub-name">VerifiHireAI</span>
            <span className="aio-hub-sub">All-in-One Platform</span>
            <span className="aio-hub-round">1 Round · All Features</span>
          </div>
        </div>

        {/* Orbit Nodes */}
        {orbitFeatures.map((f, i) => {
          const angle = (i / total) * 2 * Math.PI - Math.PI / 2;
          const x = 50 + (RADIUS / 300) * 50 * Math.cos(angle);
          const y = 50 + (RADIUS / 300) * 50 * Math.sin(angle);
          return (
            <div
              key={i}
              className={`aio-node ${visible ? 'aio-node-visible' : ''} ${activeIdx === i ? 'aio-node-active' : ''}`}
              style={{
                left: `calc(50% + ${RADIUS * Math.cos(angle)}px)`,
                top: `calc(50% + ${RADIUS * Math.sin(angle)}px)`,
                '--color': f.color,
                '--delay': `${0.3 + i * 0.1}s`,
              }}
              onMouseEnter={() => setActiveIdx(i)}
              onMouseLeave={() => setActiveIdx(null)}
            >
              <div className="aio-node-icon" style={{ background: `${f.color}20`, border: `1.5px solid ${f.color}50` }}>
                <span style={{ color: f.color }}>{f.icon}</span>
              </div>
              <div className="aio-node-label">{f.label}</div>
              <div className="aio-node-sub">{f.sub}</div>
              {/* Tooltip showing what it replaced */}
              <div className="aio-node-tooltip">
                <span className="aio-tooltip-before">Previously: {f.prev}</span>
                <span className="aio-tooltip-arrow">→</span>
                <span className="aio-tooltip-now" style={{ color: f.color }}>Now: VerifiHireAI</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Bottom Caption ── */}
      <div className="aio-bottom-caption">
        <CheckCircle2 size={18} color="#10B981" />
        One platform. One login. One seamless hiring experience — from assessment to offer.
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   Stats Section
───────────────────────────────────────────── */
function StatsSection() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold: 0.3 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  const s1 = useCountUp(94, 1800, visible);
  const s2 = useCountUp(3, 1500, visible);
  const s3 = useCountUp(10000, 2200, visible);
  const s4 = useCountUp(99, 1600, visible);

  return (
    <section className="stats-banner" ref={ref}>
      <div className="stats-inner">
        <div className="stat-item">
          <span className="stat-number">{s1}%</span>
          <span className="stat-label">Fraud Detection Accuracy</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{s2}x</span>
          <span className="stat-label">Faster Screening Process</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{s3.toLocaleString()}+</span>
          <span className="stat-label">Interviews Conducted</span>
        </div>
        <div className="stat-item">
          <span className="stat-number">{s4}%</span>
          <span className="stat-label">Employer Satisfaction Rate</span>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   Comparison Section  (Previous vs VerifiHireAI)
───────────────────────────────────────────── */
const traditionalProblems = [
  { icon: <AlertTriangle size={16} />, text: 'Manual resume screening – slow & error-prone' },
  { icon: <AlertTriangle size={16} />, text: 'Unconscious bias skews candidate evaluation' },
  { icon: <AlertTriangle size={16} />, text: 'No fraud detection — impersonation goes unnoticed' },
  { icon: <AlertTriangle size={16} />, text: 'Inconsistent interview questions & scoring' },
  { icon: <AlertTriangle size={16} />, text: 'Weeks of back-and-forth scheduling delays' },
  { icon: <AlertTriangle size={16} />, text: 'No behavioural or sentiment analytics' },
  { icon: <AlertTriangle size={16} />, text: 'Expensive per-hire costs with no ROI visibility' },
  { icon: <AlertTriangle size={16} />, text: 'Data scattered across emails, sheets & docs' },
];

const verifiHireBenefits = [
  { icon: <CheckCircle2 size={16} />, text: 'AI-powered screening in minutes, not weeks' },
  { icon: <CheckCircle2 size={16} />, text: 'Objective, bias-free AI scoring every time' },
  { icon: <CheckCircle2 size={16} />, text: 'Real-time identity & multi-face fraud detection' },
  { icon: <CheckCircle2 size={16} />, text: 'Standardized rubrics ensure consistent fairness' },
  { icon: <CheckCircle2 size={16} />, text: 'Instant scheduling — candidates interview 24/7' },
  { icon: <CheckCircle2 size={16} />, text: 'Behavioural sentiment & confidence analytics' },
  { icon: <CheckCircle2 size={16} />, text: 'Cut cost-per-hire by up to 60% with full ROI data' },
  { icon: <CheckCircle2 size={16} />, text: 'Unified dashboard — all data in one place' },
];

function ComparisonSection() {
  return (
    <section className="comparison-section">
      <div className="comparison-container">
        <div className="comparison-header">
          <span className="badge-premium">Side-by-Side Comparison</span>
          <h2>Why Switch to VerifiHireAI?</h2>
          <p>See exactly what you gain — and what you leave behind.</p>
        </div>
        <ScrollReveal>
          <div className="comparison-grid">
            {/* Traditional Card */}
            <div className="compare-card compare-old">
              <div className="compare-card-top old-top">
                <XCircle size={28} color="#EF4444" />
                <div>
                  <h3>Traditional Hiring</h3>
                  <span className="compare-badge old-badge">Outdated</span>
                </div>
              </div>
              <ul className="compare-list">
                {traditionalProblems.map((item, i) => (
                  <li key={i} className="compare-item old-item">
                    <span className="compare-icon old-icon">{item.icon}</span>
                    {item.text}
                  </li>
                ))}
              </ul>
            </div>

            {/* VS Divider */}
            <div className="vs-divider">
              <div className="vs-pill">VS</div>
            </div>

            {/* VerifiHireAI Card */}
            <div className="compare-card compare-new">
              <div className="compare-card-top new-top">
                <Award size={28} color="#3B82F6" />
                <div>
                  <h3>VerifiHireAI</h3>
                  <span className="compare-badge new-badge">AI-Powered</span>
                </div>
              </div>
              <ul className="compare-list">
                {verifiHireBenefits.map((item, i) => (
                  <li key={i} className="compare-item new-item">
                    <span className="compare-icon new-icon">{item.icon}</span>
                    {item.text}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   Benefits Section
───────────────────────────────────────────── */
const benefitsList = [
  {
    icon: <UserCheck size={26} />,
    color: '#3B82F6',
    bg: 'rgba(59,130,246,0.10)',
    title: 'Intelligent AI Interviewer',
    desc: 'Our NLP-driven AI conducts dynamic, role-specific interviews — asking follow-up questions in real time, adapting to each candidate\'s unique responses.',
  },
  {
    icon: <ShieldCheck size={26} />,
    color: '#10B981',
    bg: 'rgba(16,185,129,0.10)',
    title: 'Zero-Trust Fraud Prevention',
    desc: 'Multi-layer identity verification, browser lockdown, live multi-face detection, and audio anomaly alerts ensure every session is 100% authentic.',
  },
  {
    icon: <BarChart3 size={26} />,
    color: '#8B5CF6',
    bg: 'rgba(139,92,246,0.10)',
    title: 'Deep Analytics Dashboard',
    desc: 'Granular session reports, sentiment heatmaps, engagement scores, and comparative candidate rankings — all in a single, beautiful dashboard.',
  },
  {
    icon: <Clock size={26} />,
    color: '#F59E0B',
    bg: 'rgba(245,158,11,0.10)',
    title: '24/7 On-Demand Interviewing',
    desc: 'Candidates can take structured AI interviews anytime, anywhere — dramatically reducing scheduling friction and time-to-hire.',
  },
  {
    icon: <UserCheck size={26} />,
    color: '#EC4899',
    bg: 'rgba(236,72,153,0.10)',
    title: 'Bias-Free Candidate Scoring',
    desc: 'Standardized rubrics and completely objective AI evaluation eliminate human bias, delivering fair assessments at every stage.',
  },
  {
    icon: <Globe size={26} />,
    color: '#06B6D4',
    bg: 'rgba(6,182,212,0.10)',
    title: 'Enterprise-Ready Scalability',
    desc: 'From startups to Fortune 500 enterprises — VerifiHireAI scales seamlessly, handling thousands of concurrent interviews with zero degradation.',
  },
  {
    icon: <FileText size={26} />,
    color: '#F97316',
    bg: 'rgba(249,115,22,0.10)',
    title: 'Auto-Generated Reports',
    desc: 'Instant, professional PDF reports for each candidate — complete with scores, flags, behavioral insights, and a recruiter summary.',
  },
  {
    icon: <Lock size={26} />,
    color: '#6366F1',
    bg: 'rgba(99,102,241,0.10)',
    title: 'Enterprise Security & Compliance',
    desc: 'End-to-end encryption, GDPR-ready data handling, role-based access control, and full audit trails keep your hiring data safe.',
  },
];

function BenefitsSection() {
  return (
    <section className="benefits-section">
      <div className="benefits-container">
        <div className="benefits-header">
          <span className="badge-premium" style={{ background: '#EFF6FF', border: '1px solid #DBEAFE', color: '#2563EB' }}>
            Platform Benefits
          </span>
          <h2>Everything You Need to Hire Smarter</h2>
          <p>VerifiHireAI combines cutting-edge AI, behavioural science, and enterprise security into one seamless hiring platform.</p>
        </div>
        <ScrollReveal>
          <div className="benefits-grid">
            {benefitsList.map((b, i) => (
              <div className="benefit-card" key={i} style={{ "--accent": b.color }}>
                <div className="benefit-icon-wrap" style={{ background: b.bg }}>
                  <span style={{ color: b.color }}>{b.icon}</span>
                </div>
                <h3 className="benefit-title">{b.title}</h3>
                <p className="benefit-desc">{b.desc}</p>
                <div className="benefit-learn-more">
                  Learn more <ArrowRight size={14} />
                </div>
              </div>
            ))}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   How It Works Section
───────────────────────────────────────────── */
const steps = [
  { num: '01', icon: <Layers size={22} />, color: '#3B82F6', title: 'Create a Job Role', desc: 'Define the role, required skills, and evaluation criteria. VerifiHireAI auto-generates tailored interview questions.' },
  { num: '02', icon: <UserCheck size={22} />, color: '#10B981', title: 'Invite Candidates', desc: 'Send a unique, secure interview link via email. Candidates access the AI interview from any device, anytime.' },
  { num: '03', icon: <Monitor size={22} />, color: '#8B5CF6', title: 'AI Conducts the Interview', desc: 'Our AI interviewer conducts a structured session, monitoring identity, behaviour, and responses in real time.' },
  { num: '04', icon: <BarChart3 size={22} />, color: '#F59E0B', title: 'Review & Decide', desc: 'Receive instant scores, fraud flags, sentiment analysis, and ranked candidates — ready for your final decision.' },
];

function HowItWorksSection() {
  return (
    <section className="hiw-section">
      <div className="hiw-container">
        <div className="hiw-header">
          <span className="badge-dark">How It Works</span>
          <h2>From Job Post to Hired — In 4 Simple Steps</h2>
          <p>VerifiHireAI makes the entire screening process effortless, fast, and fraud-proof.</p>
        </div>
        <ScrollReveal>
          <div className="hiw-steps">
            {steps.map((s, i) => (
              <React.Fragment key={i}>
                <div className="hiw-step">
                  <div className="hiw-step-num" style={{ color: s.color, border: `2px solid ${s.color}22`, background: `${s.color}11` }}>{s.num}</div>
                  <div className="hiw-icon-wrap" style={{ background: `${s.color}15`, color: s.color }}>{s.icon}</div>
                  <h3 className="hiw-step-title">{s.title}</h3>
                  <p className="hiw-step-desc">{s.desc}</p>
                </div>
                {i < steps.length - 1 && <div className="hiw-connector"><ChevronRight size={20} color="rgba(255,255,255,0.2)" /></div>}
              </React.Fragment>
            ))}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   Testimonials Section
───────────────────────────────────────────── */
const testimonials = [
  {
    quote: "VerifiHireAI cut our time-to-hire from 3 weeks to 4 days. The fraud detection alone saved us from two impersonation attempts we'd never have caught manually.",
    name: 'Priya Sharma',
    role: 'VP of Talent, TechNova Corp',
    rating: 5,
    avatar: 'PS',
    color: '#3B82F6',
  },
  {
    quote: "The AI interviews are incredibly natural. Candidates actually prefer them — no scheduling stress. Our quality-of-hire scores have improved by 40% since onboarding.",
    name: 'James O\'Brien',
    role: 'Head of HR, ScaleUp Labs',
    rating: 5,
    avatar: 'JO',
    color: '#10B981',
  },
  {
    quote: "Finally, an unbiased hiring tool. Our diversity metrics improved significantly in just two quarters. The analytics dashboard is a game-changer for our team.",
    name: 'Amara Osei',
    role: 'Chief People Officer, Meridian AI',
    rating: 5,
    avatar: 'AO',
    color: '#8B5CF6',
  },
];

function TestimonialsSection() {
  return (
    <section className="testimonials-section">
      <div className="testimonials-container">
        <div className="testimonials-header">
          <span className="badge-premium">What Leaders Say</span>
          <h2>Trusted by Forward-Thinking Teams</h2>
        </div>
        <ScrollReveal>
          <div className="testimonials-grid">
            {testimonials.map((t, i) => (
              <div className="testimonial-card" key={i}>
                <div className="t-stars">
                  {Array(t.rating).fill(0).map((_, j) => <Star key={j} size={14} fill="#F59E0B" color="#F59E0B" />)}
                </div>
                <p className="t-quote">"{t.quote}"</p>
                <div className="t-author">
                  <div className="t-avatar" style={{ background: `${t.color}22`, color: t.color }}>{t.avatar}</div>
                  <div>
                    <div className="t-name">{t.name}</div>
                    <div className="t-role">{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   CTA Section
───────────────────────────────────────────── */
function CTASection() {
  return (
    <section className="shared-cta-section">
      <div className="shared-cta-card">
        <div className="shared-cta-badge">
          <span>AI-Powered Hiring</span>
        </div>
        <h2 className="shared-cta-title">Ready to Transform Your Hiring?</h2>
        <p className="shared-cta-text">
          Join thousands of companies already using VerifiHireAI to hire faster, fairer, and fraud-free.
        </p>
        <Link to="/signup" className="shared-cta-btn">
          Get Started For Free
        </Link>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   Main Home Component
───────────────────────────────────────────── */
function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <MainHeader />
      <main className="classic-home">

        {/* ── Hero ── */}
        <section className={`hero-classic-section ${mounted ? 'fade-in' : ''}`}>
          <div className="hero-classic-content">
            <div className="hero-classic-text">
              <span className="hero-pill">AI-Powered Hiring Platform</span>
              <h1 className="hero-classic-title">
                AI Intelligence That <br />
                <span className="accent-blue">Transforms Hiring</span>
              </h1>
              <p className="hero-classic-subtitle">
                VerifiHireAI leverages advanced artificial intelligence to conduct structured, unbiased interviews while ensuring real-time fraud detection and candidate authenticity. Make faster, data-driven hiring decisions with confidence, integrity, and precision.
              </p>
              <div className="hero-classic-buttons">
                <Link to="/signup" className="btn-primary-premium">
                  Get Started Free →
                </Link>
                <Link to="/contact" className="btn-secondary-premium">
                  Book a Demo
                </Link>
              </div>
            </div>
            <div className="hero-classic-visual">
              <DetectionDemo />
            </div>
          </div>
        </section>

        {/* ── Stats Banner ── */}
        <StatsSection />

        {/* ── All-in-One Platform (360° Circle) ── */}
        <AllInOneSection />



        {/* ── Key Features ── */}
        <section className="features-classic">
          <div className="features-header">
            <span className="features-tag">Core Capabilities</span>
            <h2>Enterprise-Grade AI Interviewing</h2>
            <p>Why VerifiHireAI — four pillars of intelligent, secure, and scalable hiring</p>
          </div>
          <ScrollReveal>
            <div className="features-grid-classic">
              <div className="feature-card-classic card-blue">
                <div className="feature-card-header">
                  <h3 className="feature-card-title">Real-Time Fraud Detection</h3>
                </div>
                <p className="feature-card-text">
                  Continuous identity verification, multi-face detection, and browser lockdown ensure complete integrity throughout the assessment.
                </p>
              </div>

              <div className="feature-card-classic card-green">
                <div className="feature-card-header">
                  <h3 className="feature-card-title">Behavioural Analysis</h3>
                </div>
                <p className="feature-card-text">
                  Advanced sentiment tracking and confidence analysis over the course of the candidate's interview responses.
                </p>
              </div>

              <div className="feature-card-classic card-purple">
                <div className="feature-card-header">
                  <h3 className="feature-card-title">Unbiased Scoring & Grading</h3>
                </div>
                <p className="feature-card-text">
                  Standardized rubrics and completely objective AI evaluation eliminates human bias from preliminary screening rounds.
                </p>
              </div>

              <div className="feature-card-classic card-orange">
                <div className="feature-card-header">
                  <h3 className="feature-card-title">Seamless Dashboard Experience</h3>
                </div>
                <p className="feature-card-text">
                  View detailed analytics, session integrity reports, and candidate progression in a premium, highly actionable unified dashboard.
                </p>
              </div>
            </div>
          </ScrollReveal>
        </section>

        {/* ── Comparison ── */}
        <ComparisonSection />

        {/* ── Candidate vs Recruiter ── */}
        <PerspectiveSection />

        {/* ── Live Demo ── */}
        <DemoSection />

        {/* ── Benefits ── */}
        <BenefitsSection />

        {/* ── How It Works ── */}
        <HowItWorksSection />



        {/* ── Testimonials ── */}
        <TestimonialsSection />

        {/* ── FAQ ── */}
        <FAQSection />

        {/* ── CTA ── */}
        <CTASection />

      </main>
      <Footer />
    </>
  );
}

export default Home;



