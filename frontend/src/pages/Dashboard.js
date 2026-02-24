import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  LayoutDashboard,
  FileText,
  Users,
  MessageSquare,
  PlusCircle,
  Brain,
  Sparkles,
  SearchCode,
  Video,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  TrendingUp,
  Award,
  Clock,
  ChevronRight,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from 'recharts';
import ProfileDropdown from '../components/ProfileDropdown';
import '../styles/DashboardNew.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [expandedItem, setExpandedItem] = useState(null);
  const [expandedSubItem, setExpandedSubItem] = useState(null);

  const [data, setData] = useState({
    recentCandidates: [],
    stats: {
      totalCandidates: 0,
      inPipeline: 0,
      hired: 0,
      activeTestsAi: 0,
      activeTestsCustom: 0,
      avgScoreAi: 0,
      avgScoreCustom: 0,
      resumesToday: 0,
      scheduledInterviews: 0
    },
    trendsAi: [],
    trendsCustom: [],
    successRate: []
  });


  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resultsRes, candidatesRes, interviewsRes, aiAssessmentsRes, customAssessmentsRes] = await Promise.all([
          axios.get('http://localhost:8001/api/results/'),
          axios.get('http://localhost:8001/api/candidates/'),
          axios.get('http://localhost:8001/api/interviews/invitations/'),
          axios.get('http://localhost:8001/api/ai/'),
          axios.get('http://localhost:8001/api/assessments/')
        ]);

        const results = resultsRes.data.results || [];
        const candidates = candidatesRes.data.results || [];
        const interviews = interviewsRes.data.results || [];
        const aiAssessmentsCount = (aiAssessmentsRes.data || []).length;
        const customAssessmentsCount = (customAssessmentsRes.data?.results || []).length;

        // Calculate Stats
        const today = new Date().toISOString().split('T')[0];
        const resumesTodayCount = results.filter(r => r.submitted_at?.startsWith(today)).length;

        const totalCandidates = candidates.length + (results.length - candidates.filter(c => results.some(r => r.candidate?.email === c.email)).length);
        const hiredCount = results.filter(r => r.status === 'selected' || r.result === 'selected').length;
        const pipelineCount = candidates.filter(c => c.status !== 'Submitted' && c.status !== 'Completed').length;

        const resultsAi = results.filter(r => r.submission_id?.startsWith('ai_'));
        const resultsCustom = results.filter(r => !r.submission_id?.startsWith('ai_'));

        const scoresAi = resultsAi.map(r => r.percentage || 0).filter(s => s > 0);
        const avgScoreAi = scoresAi.length > 0 ? (scoresAi.reduce((a, b) => a + b, 0) / scoresAi.length).toFixed(1) : 0;

        const scoresCustom = resultsCustom.map(r => r.percentage || 0).filter(s => s > 0);
        const avgScoreCustom = scoresCustom.length > 0 ? (scoresCustom.reduce((a, b) => a + b, 0) / scoresCustom.length).toFixed(1) : 0;

        // Group trends by month
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const currentYear = new Date().getFullYear();

        const trendsAi = months.map((m, i) => {
          const count = resultsAi.filter(r => {
            const d = new Date(r.submitted_at);
            return d.getMonth() === i && d.getFullYear() === currentYear;
          }).length;
          return { name: m, value: count };
        });

        const trendsCustom = months.map((m, i) => {
          const count = resultsCustom.filter(r => {
            const d = new Date(r.submitted_at);
            return d.getMonth() === i && d.getFullYear() === currentYear;
          }).length;
          return { name: m, value: count };
        });

        const successData = months.map((m, i) => {
          const monthResults = results.filter(r => {
            const d = new Date(r.submitted_at);
            return d.getMonth() === i && d.getFullYear() === currentYear;
          });
          const hired = monthResults.filter(r => r.status === 'selected' || r.result === 'selected').length;
          const total = monthResults.length;
          const rate = total > 0 ? (hired / total) * 100 : 0;
          return { name: m, value: Math.round(rate) };
        });

        setData({
          recentCandidates: candidates.slice(0, 5),
          stats: {
            totalCandidates,
            inPipeline: pipelineCount,
            hired: hiredCount,
            avgScoreAi,
            avgScoreCustom,
            resumesToday: resumesTodayCount,
            activeTestsAi: aiAssessmentsCount,
            activeTestsCustom: customAssessmentsCount,
            scheduledInterviews: interviews.length
          },
          trendsAi,
          trendsCustom,
          trendsTotal: months.map((m, i) => ({
            name: m,
            value: (trendsAi[i]?.value || 0) + (trendsCustom[i]?.value || 0)
          })),
          successRate: successData
        });

        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: true, path: '/dashboard' },
    {
      icon: FileText,
      label: 'Assessments',
      path: '#',
      subItems: [
        { label: 'AI Assessments', path: '/ai-assessments' },
        { label: 'Custom Assessments', path: '/custom-assessment' }
      ]
    },
    {
      icon: MessageSquare,
      label: 'Interviews',
      path: '#',
      subItems: [
        {
          label: 'Live Interview',
          path: '#',
          nestedItems: [
            { label: 'Send Invite', path: '/send-invite' },
            { label: 'Join Room', path: '/live-interview-list' }
          ]
        },
        {
          label: 'AI Interview',
          path: '#',
          nestedItems: [
            { label: 'Start Session', path: '/ai-interview' },
            { label: 'Result', path: '/results-ai' }
          ]
        }
      ]
    },
    { icon: Users, label: 'Candidates', path: '/candidates' },
    { icon: BarChart3, label: 'Reports', path: '/results' },
  ];


  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f1f5f9' }}>
        <div className="loader">Loading VerifiHire Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="new-dashboard-container">
      {/* Sidebar */}
      <aside className="dashboard-sidebar">
        <div className="sidebar-logo">VerifiHire<span style={{ color: '#6366f1' }}>AI</span></div>
        <nav className="sidebar-nav">
          {navItems.map((item, i) => (
            <div key={i} className="nav-group">
              <div
                className={`nav-item ${item.active ? 'active' : ''} ${expandedItem === item.label ? 'expanded' : ''}`}
                onClick={() => {
                  if (item.subItems) {
                    setExpandedItem(expandedItem === item.label ? null : item.label);
                    setExpandedSubItem(null);
                  } else {
                    navigate(item.path);
                  }
                }}
              >
                <div className="nav-item-content">
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </div>
                {item.subItems && (
                  expandedItem === item.label ? <ChevronUp size={16} /> : <ChevronDown size={16} />
                )}
              </div>

              {item.subItems && expandedItem === item.label && (
                <div className="sub-nav">
                  {item.subItems.map((sub, j) => (
                    <div key={j} className="sub-nav-group">
                      <div
                        className={`sub-nav-item ${expandedSubItem === sub.label ? 'expanded' : ''}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (sub.nestedItems) {
                            setExpandedSubItem(expandedSubItem === sub.label ? null : sub.label);
                          } else {
                            navigate(sub.path);
                          }
                        }}
                      >
                        <div className="sub-nav-item-content">
                          <span>{sub.label}</span>
                        </div>
                        {sub.nestedItems && (
                          expandedSubItem === sub.label ? <ChevronUp size={14} /> : <ChevronDown size={14} />
                        )}
                      </div>

                      {sub.nestedItems && expandedSubItem === sub.label && (
                        <div className="nested-nav">
                          {sub.nestedItems.map((nested, k) => (
                            <div
                              key={k}
                              className="nested-nav-item"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(nested.path);
                              }}
                            >
                              <span>{nested.label}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="nav-item" onClick={() => navigate('/login')}>
            <Clock size={20} />
            <span>Switch Role</span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="dashboard-content">
        <header className="dashboard-topbar">
          <div className="topbar-left">
            <h2>Dashboard</h2>
          </div>
          <div className="topbar-right">
            <div className="topbar-actions">

              <div className="dashboard-profile-wrapper">
                <ProfileDropdown />
              </div>
            </div>
          </div>
        </header>

        <div className="dashboard-body">
          {/* Top Row: Core Modules */}
          <div className="dashboard-grid">
            {/* AI-Powered Assessment */}
            <div className="glass-card">
              <div className="card-header">
                <div className="card-icon" style={{ background: '#e0e7ff', color: '#4338ca' }}>
                  <Brain size={20} />
                </div>
                <h3>AI Assessments</h3>
              </div>
              <div className="card-stat-row">
                <div className="stat-item">
                  <span className="stat-label">Average Score</span>
                  <span className="stat-value">{data.stats.avgScoreAi}%</span>
                </div>
              </div>
              <div className="card-visual">
                <ResponsiveContainer width="100%" height={80}>
                  <BarChart data={data.trendsAi}>
                    <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="card-actions three-cols">
                <button className="btn-premium btn-fill" onClick={() => navigate('/ai-assessments')}>Assessments</button>
                <button className="btn-premium btn-outline" onClick={() => navigate('/create-assessment')}>Create</button>
                <button className="btn-premium btn-outline" onClick={() => navigate('/results-ai?tab=assessment')}>Results</button>
              </div>
            </div>

            {/* Custom Assessment */}
            <div className="glass-card">
              <div className="card-header">
                <div className="card-icon" style={{ background: '#f3e8ff', color: '#9333ea' }}>
                  <SearchCode size={20} />
                </div>
                <h3>Custom Assessments</h3>
              </div>
              <div className="card-stat-row">
                <div className="stat-item">
                  <span className="stat-label">Active Custom Tests</span>
                  <span className="stat-value">{data.stats.activeTestsCustom}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Average Score</span>
                  <span className="stat-value">{data.stats.avgScoreCustom}%</span>
                </div>
              </div>
              <div className="card-visual" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.5rem' }}>
                <div className="progress-item" style={{ width: '100%' }}>
                  <div className="progress-label-row"><span>Active Assessments</span><span>{data.stats.activeTestsCustom}</span></div>
                  <div className="progress-bar-bg"><div className="progress-bar-fill" style={{ width: `${Math.min(data.stats.activeTestsCustom * 10, 100)}%`, background: '#6366f1' }}></div></div>
                </div>
              </div>
              <div className="card-actions">
                <button className="btn-premium btn-fill" onClick={() => navigate('/custom-assessment')}>Question Cart</button>
                <button className="btn-premium btn-outline" onClick={() => navigate('/coding')}>Coding</button>
              </div>
            </div>

            {/* Resume Screening */}
            <div className="glass-card">
              <div className="card-header">
                <div className="card-icon" style={{ background: '#e0f2fe', color: '#0284c7' }}>
                  <FileText size={20} />
                </div>
                <h3>Resume Screening</h3>
              </div>
              <div className="card-stat-row">
                <div className="stat-item">
                  <span className="stat-label">Resumes Analyzed Today</span>
                  <span className="stat-value">{data.stats.resumesToday}</span>
                </div>
              </div>
              <div className="skills-tags" style={{ marginBottom: '1.5rem' }}>
                <span className="skill-tag">Resume Screening</span>
                <span className="skill-tag">AI Matching</span>
                <span className="skill-tag">Candidate Ranking</span>
              </div>
              <div className="card-actions">
                <button className="btn-premium btn-fill" onClick={() => navigate('/resume-matcher')}>Analyze Resumes</button>
                <button className="btn-premium btn-outline" onClick={() => navigate('/results-ai?tab=resume')}>Results</button>
              </div>
            </div>
          </div>

          {/* Middle Row: Interviews */}
          <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
            <div className="glass-card">
              <div className="card-header">
                <div className="card-icon" style={{ background: '#fef3c7', color: '#d97706' }}>
                  <Sparkles size={20} />
                </div>
                <h3>AI Interviews</h3>
              </div>
              <div className="card-stat-row">
                <div className="stat-item">
                  <span className="stat-label">Scheduled Sessions</span>
                  <span className="stat-value">{data.stats.scheduledInterviews}</span>
                </div>
              </div>
              <div className="card-actions">
                <button className="btn-premium btn-fill" onClick={() => navigate('/ai-interview')}>Start Session</button>
                <button className="btn-premium btn-outline" onClick={() => navigate('/results-ai?tab=interview')}>Results</button>
              </div>
            </div>

            <div className="glass-card">
              <div className="card-header">
                <div className="card-icon" style={{ background: '#dcfce7', color: '#16a34a' }}>
                  <Video size={20} />
                </div>
                <h3>Live Interviews</h3>
              </div>
              <div className="card-stat-row">
                <div className="stat-item">
                  <span className="stat-label">Upcoming Live Calls</span>
                  <span className="stat-value">{data.stats.scheduledInterviews}</span>
                </div>
              </div>
              <div className="card-actions">
                <button className="btn-premium btn-fill" onClick={() => navigate('/send-invite')}>Send Invite</button>
                <button className="btn-premium btn-outline" onClick={() => navigate('/live-interview-list')}>Join Room</button>
              </div>
            </div>

            <div className="glass-card" style={{ justifyContent: 'center', cursor: 'pointer' }} onClick={() => navigate('/results')}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div className="card-icon"><BarChart3 size={24} /></div>
                <div>
                  <h3 style={{ margin: 0 }}>Results</h3>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748b' }}>View selection outcomes</p>
                </div>
                <ChevronRight style={{ marginLeft: 'auto', color: '#ccd6e0' }} />
              </div>
            </div>
          </div>

          {/* Bottom Row: Detailed Insights */}
          <div className="dashboard-grid-wide">
            {/* Candidates Section */}
            <div className="glass-card">
              <div className="chart-header">
                <h3>Candidates</h3>
              </div>
              <div className="card-stat-row" style={{ marginBottom: '2rem' }}>
                <div className="stat-item">
                  <span className="stat-label">Total Candidates</span>
                  <span className="stat-value">{data.stats.totalCandidates}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">In Pipeline</span>
                  <span className="stat-value">{data.stats.inPipeline}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Hired</span>
                  <span className="stat-value">{data.stats.hired}</span>
                </div>
              </div>

              <div className="candidate-list">
                <h4 style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '0.5rem' }}>Recent Candidates</h4>
                {data.recentCandidates.length > 0 ? data.recentCandidates.map((cand, i) => (
                  <div key={i} className="candidate-row">
                    <div className="candidate-info">
                      <div className="candidate-avatar">{cand.name ? cand.name.charAt(0) : '?'}</div>
                      <div>
                        <div className="cand-name">{cand.name || 'Anonymous'}</div>
                        <div className="cand-email">{cand.email}</div>
                      </div>
                    </div>
                    <span className={`status-badge ${cand.status === 'Submitted' || cand.status === 'Completed' ? 'status-hired' : 'status-in-pipeline'}`}>
                      {cand.status === 'Submitted' || cand.status === 'Completed' ? 'Completed' : 'In Pipeline'}
                    </span>
                  </div>
                )) : (
                  <p style={{ fontSize: '0.85rem', color: '#94a3b8', textAlign: 'center', padding: '2rem' }}>No recent candidates found</p>
                )}
              </div>
            </div>

            {/* Results Chart Section */}
            <div className="glass-card">
              <div className="chart-header">
                <h3>Results</h3>
                <div className="chart-filters">
                  <select className="filter-select"><option>Month</option></select>
                  <select className="filter-select"><option>Analytics</option></select>
                </div>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.trendsTotal}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                      itemStyle={{ color: '#6366f1', fontWeight: 700 }}
                    />
                    <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '2rem' }}>
                <div className="glass-card" style={{ padding: '1rem', background: 'white' }}>
                  <h4 style={{ fontSize: '0.8rem', margin: '0 0 1rem' }}>Candidate Success Rate</h4>
                  <ResponsiveContainer width="100%" height={100}>
                    <BarChart data={data.successRate}>
                      <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Selection Today</span>
                    <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 700 }}>{data.stats.hired}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Total Interviews</span>
                    <span style={{ fontSize: '0.8rem', color: '#6366f1', fontWeight: 700 }}>{data.stats.scheduledInterviews}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
