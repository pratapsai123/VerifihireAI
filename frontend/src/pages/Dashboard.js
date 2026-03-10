import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import {
  LayoutDashboard,
  FileText,
  Users,
  MessageSquare,
  Brain,
  Sparkles,
  SearchCode,
  Video,
  BarChart3,
  Clock,
  PlusCircle,
  ChevronRight,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts';
import '../styles/DashboardNew.css';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div style={{ background: 'white', padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}>
        <p style={{ margin: '0 0 0.5rem', fontWeight: 700, color: '#1e293b' }}>{label}</p>
        <div style={{ fontSize: '0.85rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>Total Actions:</span> <span style={{ fontWeight: 600, color: '#6366f1' }}>{data.value}</span>
          </div>
          <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '0.25rem 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>AI Assessments:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.aiAssessments || 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>Custom Assessments:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.customAssessments || 0}</span>
          </div>
          <hr style={{ border: 'none', borderTop: '1px solid #e2e8f0', margin: '0.25rem 0' }} />
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>Interviews Scheduled:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.interviewsScheduled || 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>Interviews Ongoing:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.interviewsOngoing || 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>Interviews Completed:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.interviewsCompleted || 0}</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [expandedItem, setExpandedItem] = useState(null);
  const [expandedSubItem, setExpandedSubItem] = useState(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeFloatingMenu, setActiveFloatingMenu] = useState(null);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [roleFormData, setRoleFormData] = useState({ title: '', description: '' });
  const [isSubmittingRole, setIsSubmittingRole] = useState(false);

  useEffect(() => {
    if (isSidebarCollapsed) {
      setExpandedItem(null);
      setExpandedSubItem(null);
    } else {
      setActiveFloatingMenu(null);
    }
  }, [isSidebarCollapsed]);

  // Click away for floating menu
  useEffect(() => {
    const handleClickAway = () => setActiveFloatingMenu(null);
    if (activeFloatingMenu) {
      window.addEventListener('click', handleClickAway);
    }
    return () => window.removeEventListener('click', handleClickAway);
  }, [activeFloatingMenu]);

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
        const [resultsRes, candidatesRes, interviewsRes, aiAssessmentsRes, customAssessmentsRes, aiCandidatesRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/results/`),
          axios.get(`${API_BASE_URL}/candidates/`),
          axios.get(`${API_BASE_URL}/interviews/invitations/`),
          axios.get(`${API_BASE_URL}/ai/`),
          axios.get(`${API_BASE_URL}/assessments/`),
          axios.get(`${API_BASE_URL}/ai-candidates/`)
        ]);

        const results = resultsRes.data.results || [];
        const candidates = candidatesRes.data.results || [];
        const interviews = interviewsRes.data.results || [];
        const aiAssessmentsCount = (aiAssessmentsRes.data || []).length;
        const customAssessmentsCount = (customAssessmentsRes.data?.results || []).length;
        const aiCandidates = aiCandidatesRes.data || [];

        // Calculate Stats
        const today = new Date().toISOString().split('T')[0];
        const resumesTodayCount = results.filter(r => r.submitted_at && String(r.submitted_at).startsWith(today)).length;

        const totalCandidates = candidates.length + (results.length - candidates.filter(c => results.some(r => r.candidate?.email === c.email)).length);
        const hiredCount = results.filter(r => r.status === 'selected' || r.result === 'selected').length;
        const pipelineCount = candidates.filter(c => c.status !== 'Submitted' && c.status !== 'Completed').length;

        const resultsAi = results.filter(r => String(r.submission_id || '').startsWith('ai_'));
        const resultsCustom = results.filter(r => !String(r.submission_id || '').startsWith('ai_'));

        const scoresAi = resultsAi.map(r => r.percentage || 0).filter(s => s > 0);
        const avgScoreAi = scoresAi.length > 0 ? (scoresAi.reduce((a, b) => a + b, 0) / scoresAi.length).toFixed(1) : 0;

        const scoresCustom = resultsCustom.map(r => r.percentage || 0).filter(s => s > 0);
        const avgScoreCustom = scoresCustom.length > 0 ? (scoresCustom.reduce((a, b) => a + b, 0) / scoresCustom.length).toFixed(1) : 0;

        // Calculate AI Interviews (Candidates invited to or completed an AI session)
        const aiInterviewsCount = aiCandidates.filter(c =>
          ['Invited', 'Interview', 'Completed', 'Review', 'Rejected', 'Hired'].includes(c.status)
        ).length;

        // Group trends by month
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const currentYear = new Date().getFullYear();

        const trendsTotalData = months.map((m, i) => {
          const mResults = results.filter(r => {
            const d = new Date(r.submitted_at);
            return !isNaN(d.getTime()) && d.getMonth() === i && d.getFullYear() === currentYear;
          });
          const mInterviews = interviews.filter(inv => {
            const d = new Date(inv.created_at || inv.updated_at);
            return !isNaN(d.getTime()) && d.getMonth() === i && d.getFullYear() === currentYear;
          });

          const aiAssessmentsValue = mResults.filter(r => String(r.submission_id || '').startsWith('ai_')).length;
          const customAssessmentsValue = mResults.filter(r => !String(r.submission_id || '').startsWith('ai_')).length;
          const interviewsCompleted = mInterviews.filter(inv => inv.status === 'completed').length;
          const interviewsScheduled = mInterviews.filter(inv => inv.status === 'scheduled' || inv.status === 'pending').length;
          const interviewsOngoing = mInterviews.filter(inv => inv.status === 'in_progress').length;

          return {
            name: m,
            value: aiAssessmentsValue + customAssessmentsValue + mInterviews.length,
            aiAssessments: aiAssessmentsValue,
            customAssessments: customAssessmentsValue,
            interviewsCompleted,
            interviewsScheduled,
            interviewsOngoing
          };
        });

        // Day-wise Candidate Success Rate (Mon-Sun)
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const curr = new Date();
        const first = curr.getDate() - curr.getDay() + (curr.getDay() === 0 ? -6 : 1); // Monday
        const startOfWeek = new Date(curr.setDate(first));
        startOfWeek.setHours(0, 0, 0, 0);

        const successData = days.map((dayName, index) => {
          const dayDate = new Date(startOfWeek);
          dayDate.setDate(dayDate.getDate() + index);

          const dayResults = results.filter(r => {
            const d = new Date(r.submitted_at);
            return !isNaN(d.getTime()) &&
              d.getDate() === dayDate.getDate() &&
              d.getMonth() === dayDate.getMonth() &&
              d.getFullYear() === dayDate.getFullYear();
          });
          const hired = dayResults.filter(r => r.status === 'selected' || r.result === 'selected').length;
          return { name: dayName, value: hired };
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
            scheduledInterviews: interviews.length,
            aiInterviewsCount: aiInterviewsCount
          },
          trendsTotal: trendsTotalData,
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

  const handleCreateRole = async (e) => {
    e.preventDefault();
    setIsSubmittingRole(true);
    try {
      await axios.post(`${API_BASE_URL}/job-roles/`, roleFormData);
      setIsRoleModalOpen(false);
      setRoleFormData({ title: '', description: '' });
      // Reload roles if needed elsewhere, but for now just success
      alert('Job Role created successfully!');
    } catch (error) {
      console.error("Error creating job role:", error);
      alert('Failed to create job role. Please try again.');
    } finally {
      setIsSubmittingRole(false);
    }
  };

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: true, path: '/dashboard' },
    {
      icon: FileText,
      label: 'Assessments',
      path: '#',
      subItems: [
        { label: 'Assessments List', path: '/assessments' },
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
            { label: 'Join Room', path: '/live-interview-list' },
            { label: 'Interview List', path: '/live-interview-list' }
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
    { icon: PlusCircle, label: 'Create Role', onClick: () => setIsRoleModalOpen(true), style: { color: '#6366f1', fontWeight: 700 } },
  ];


  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f1f5f9' }}>
        <div className="loader">Loading VerifiHire Dashboard...</div>
      </div>
    );
  }

  return (
    <div className={`new-dashboard-container ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Sidebar */}
      <aside className="dashboard-sidebar">
        <div className="sidebar-logo">
          {isSidebarCollapsed ? 'VH' : <>VerifiHire<span style={{ color: '#6366f1' }}>AI</span></>}
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item, i) => (
            <div key={i} className="nav-group" style={{ position: 'relative' }}>
              <div
                className={`nav-item ${item.active ? 'active' : ''} ${expandedItem === item.label ? 'expanded' : ''}`}
                onClick={(e) => {
                  if (item.onClick) {
                    item.onClick();
                    return;
                  }
                  if (item.subItems) {
                    if (isSidebarCollapsed) {
                      e.stopPropagation();
                      console.log("Toggling floating menu for:", item.label);
                      setActiveFloatingMenu(activeFloatingMenu === item.label ? null : item.label);
                    } else {
                      setExpandedItem(expandedItem === item.label ? null : item.label);
                      setExpandedSubItem(null);
                    }
                  } else {
                    navigate(item.path);
                    if (isSidebarCollapsed) setActiveFloatingMenu(null);
                  }
                }}
              >
                <div className="nav-item-content" style={item.style}>
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </div>
                {item.subItems && !isSidebarCollapsed && (
                  expandedItem === item.label ? <ChevronUp size={16} /> : <ChevronDown size={16} />
                )}
              </div>

              {/* Floating Menu for Collapsed Sidebar */}
              {isSidebarCollapsed && activeFloatingMenu === item.label && item.subItems && (
                <div
                  className="floating-sub-menu"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="floating-menu-header">{item.label}</div>
                  {item.subItems.map((sub, j) => (
                    sub.nestedItems ? (
                      // Sub-item with nested children: show group label + each child
                      <div key={j}>
                        <div className="floating-menu-group-label">{sub.label}</div>
                        {sub.nestedItems.map((nested, k) => (
                          <div
                            key={k}
                            className="floating-menu-item floating-menu-nested"
                            onClick={() => {
                              navigate(nested.path);
                              setActiveFloatingMenu(null);
                            }}
                          >
                            {nested.label}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div
                        key={j}
                        className="floating-menu-item"
                        onClick={() => {
                          navigate(sub.path);
                          setActiveFloatingMenu(null);
                        }}
                      >
                        {sub.label}
                      </div>
                    )
                  ))}
                </div>
              )}

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
            <button
              className="icon-btn sidebar-toggle"
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              style={{ marginRight: '1rem' }}
            >
              <LayoutDashboard size={20} />
            </button>
            <h2>Dashboard</h2>
          </div>
          <div className="topbar-right">
            <div className="topbar-actions">
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
                  <span className="stat-label">Active Assessments</span>
                  <span className="stat-value">{data.stats.activeTestsAi}</span>
                </div>
              </div>
              <div className="card-visual" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.5rem' }}>
                <div className="progress-item" style={{ width: '100%' }}>
                  <div className="progress-label-row"><span>Active Assessments</span><span>{data.stats.activeTestsAi}</span></div>
                  <div className="progress-bar-bg"><div className="progress-bar-fill" style={{ width: `${Math.min(data.stats.activeTestsAi * 10, 100)}%`, background: '#6366f1' }}></div></div>
                </div>
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
                  <span className="stat-value">{data.stats.aiInterviewsCount}</span>
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
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '2rem' }}>
                <div className="glass-card" style={{ padding: '1rem', background: 'white' }}>
                  <h4 style={{ fontSize: '0.8rem', margin: '0 0 1rem' }}>Candidate Success Rate</h4>
                  <ResponsiveContainer width="100%" height={100}>
                    <BarChart data={data.successRate}>
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                      <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                      <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={20} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Selection Today</span>
                    <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 700 }}>{data.stats.hired}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Live Interviews</span>
                    <span style={{ fontSize: '0.8rem', color: '#6366f1', fontWeight: 700 }}>{data.stats.scheduledInterviews}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>AI Interviews</span>
                    <span style={{ fontSize: '0.8rem', color: '#6366f1', fontWeight: 700 }}>{data.stats.aiInterviewsCount}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      {/* Job Role Modal */}
      {isRoleModalOpen && (
        <div
          className="modal-overlay"
          onClick={() => setIsRoleModalOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(15, 23, 42, 0.6)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
        >
          <div
            className="glass-card modal-content"
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: '500px',
              width: '90%',
              padding: '2rem',
              background: 'white',
              borderRadius: '2rem'
            }}
          >
            <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0 }}>Create New Job Role</h3>
              <button className="icon-btn" onClick={() => setIsRoleModalOpen(false)}><ChevronDown size={20} /></button>
            </div>
            <form onSubmit={handleCreateRole}>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#64748b', marginBottom: '0.5rem' }}>Job Title</label>
                <input
                  type="text"
                  className="filter-select"
                  style={{ width: '100%', height: '42px', padding: '0 1rem' }}
                  placeholder="e.g. Senior Frontend Engineer"
                  value={roleFormData.title}
                  onChange={(e) => setRoleFormData({ ...roleFormData, title: e.target.value })}
                  required
                />
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#64748b', marginBottom: '0.5rem' }}>Job Description</label>
                <textarea
                  className="filter-select"
                  style={{ width: '100%', minHeight: '150px', padding: '1rem', resize: 'vertical' }}
                  placeholder="Paste the job description here..."
                  value={roleFormData.description}
                  onChange={(e) => setRoleFormData({ ...roleFormData, description: e.target.value })}
                  required
                />
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="button" className="btn-premium btn-outline" style={{ flex: 1 }} onClick={() => setIsRoleModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn-premium btn-fill" style={{ flex: 1 }} disabled={isSubmittingRole}>
                  {isSubmittingRole ? 'Creating...' : 'Create Role'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
