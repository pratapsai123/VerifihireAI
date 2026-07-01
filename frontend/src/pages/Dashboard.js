import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  Brain,
  Sparkles,
  SearchCode,
  Video,
  BarChart3,
  Clock,
  PlusCircle,
  Briefcase,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Settings as SettingsIcon
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
            <span>AI Interview:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.aiInterviews || 0}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
            <span>Live interview:</span> <span style={{ fontWeight: 600, color: '#1e293b' }}>{data.liveInterviews || 0}</span>
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
  const [userRole, setUserRole] = useState('');
  const [hoveredItem, setHoveredItem] = useState(null);
  
  // Manage Job Roles Modal state
  const [isManageModalOpen, setIsManageModalOpen] = useState(false);
  const [rolesList, setRolesList] = useState([]);
  const [editingRoleId, setEditingRoleId] = useState(null);
  const [editFormData, setEditFormData] = useState({ title: '', description: '' });
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const [isLoadingRoles, setIsLoadingRoles] = useState(false);

  const fetchRolesList = async () => {
    setIsLoadingRoles(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/job-roles/`);
      setRolesList(res.data);
    } catch (err) {
      console.error("Error fetching job roles:", err);
    } finally {
      setIsLoadingRoles(false);
    }
  };

  useEffect(() => {
    if (isManageModalOpen) {
      fetchRolesList();
    }
  }, [isManageModalOpen]);

  const handleEditRole = (role) => {
    setEditingRoleId(role.id);
    setEditFormData({ title: role.title, description: role.description });
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    setIsSavingEdit(true);
    try {
      await axios.put(`${API_BASE_URL}/job-roles/${editingRoleId}/`, editFormData);
      setEditingRoleId(null);
      fetchRolesList();
      alert('Job Role updated successfully!');
    } catch (error) {
      console.error("Error updating job role:", error);
      alert('Failed to update job role. Please try again.');
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleDeleteRole = async (roleId) => {
    const reason = window.prompt("Please enter a reason for deleting this job role:");
    if (reason === null) return;
    if (!reason.trim()) {
      alert("A reason is required to request deletion.");
      return;
    }
    try {
      const res = await axios.delete(`${API_BASE_URL}/job-roles/${roleId}/`, { data: { reason } });
      fetchRolesList();
      if (res.status === 202 || res.data?.message?.includes('requested')) {
        alert(res.data.message || 'Deletion request submitted for approval.');
      } else {
        alert('Job Role deleted successfully!');
      }
    } catch (error) {
      console.error("Error deleting job role:", error);
      alert(error.response?.data?.error || 'Failed to delete job role. Please try again.');
    }
  };

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const u = JSON.parse(storedUser);
        setUserRole(u.role || '');
      } catch (err) {
        console.error("Error parsing user data");
      }
    }
  }, []);

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
      resumesAnalyzed: 0,
      scheduledInterviews: 0
    },
    trendsAi: [],
    trendsCustom: [],
    successRate: []
  });


  const [selectedYear, setSelectedYear] = useState('');
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const fetchPendingCount = async () => {
      try {
        const [delRes, qualRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/workflow/deletion-requests/count/`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }),
          axios.get(`${API_BASE_URL}/workflow/qualification-requests/count/`, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
        ]);
        const delCount = delRes.data.count || 0;
        const qualCount = qualRes.data.count || 0;
        setPendingCount(delCount + qualCount);
      } catch (err) {
        console.error("Failed to fetch pending requests counts");
      }
    };
    fetchPendingCount();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const url = selectedYear ? `${API_BASE_URL}/dashboard/summary/?year=${selectedYear}` : `${API_BASE_URL}/dashboard/summary/`;
        const res = await axios.get(url);
        setData(res.data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedYear]);

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

  const allNavItems = [
    { icon: LayoutDashboard, label: 'Dashboard', active: true, path: '/dashboard' },
    {
      icon: FileText,
      label: 'Assessments',
      path: '#',
      role: ['company_admin', 'hr_manager', 'hr', 'application_admin'],
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
            { label: 'Send Invite', path: '/send-invite', role: ['company_admin', 'hr_manager', 'hr'] },
            { label: 'Join Room', path: '/live-interview-list' },
            { label: 'Interview List', path: '/live-interview-list' },
            { label: 'Manage Availability', path: '/manage-availability' }
          ]
        },
        {
          label: 'AI Interview',
          path: '#',
          role: ['company_admin', 'hr_manager', 'hr', 'application_admin'],
          nestedItems: [
            { label: 'Start Session', path: '/ai-interview' },
            { label: 'Result', path: '/results-ai?tab=interview' }
          ]
        }
      ]
    },
    { icon: BarChart3, label: 'Results', path: '/results', role: ['company_admin', 'hr_manager', 'hr', 'application_admin'] },
    {
      icon: SettingsIcon,
      label: 'Settings',
      path: '/setting',
      role: ['company_admin', 'hr_manager', 'hr', 'application_admin'],
      badge: pendingCount > 0 ? pendingCount : null
    },
    {
      icon: Briefcase,
      label: 'Job Roles',
      path: '#',
      role: ['company_admin', 'hr_manager', 'hr', 'application_admin'],
      subItems: [
        { label: 'Create Job Role', onClick: () => setIsRoleModalOpen(true) },
        { label: 'Manage Job Roles', onClick: () => setIsManageModalOpen(true) }
      ]
    },
  ];

  const navItems = allNavItems.filter(item => {
    if (userRole === 'student') {
      return item.label === 'Dashboard';
    }
    if (!item.role) return true;
    return item.role.includes(userRole);
  }).map(item => {
    if (item.subItems) {
      return {
        ...item,
        subItems: item.subItems.filter(sub => !sub.role || sub.role.includes(userRole)).map(sub => {
          if (sub.nestedItems) {
            return {
              ...sub,
              nestedItems: sub.nestedItems.filter(nested => !nested.role || nested.role.includes(userRole))
            };
          }
          return sub;
        })
      };
    }
    return item;
  });


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
            <div 
              key={i} 
              className="nav-group" 
              style={{ position: 'relative' }}
              onMouseEnter={() => !isSidebarCollapsed && setHoveredItem(item.label)}
              onMouseLeave={() => setHoveredItem(null)}
            >
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
                  {item.badge && (
                    <span style={{
                      marginLeft: 'auto',
                      backgroundColor: '#ef4444',
                      color: 'white',
                      fontSize: '10px',
                      padding: '2px 6px',
                      borderRadius: '10px',
                      fontWeight: 'bold'
                    }} title={`${item.badge} pending requests`}>
                      {item.badge}
                    </span>
                  )}
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
                          if (sub.onClick) {
                            sub.onClick();
                          } else {
                            navigate(sub.path);
                          }
                          setActiveFloatingMenu(null);
                        }}
                      >
                        {sub.label}
                      </div>
                    )
                  ))}
                </div>
              )}

              {item.subItems && (expandedItem === item.label || hoveredItem === item.label) && (
                <div className="sub-nav">
                  {item.subItems.map((sub, j) => (
                    <div key={j} className="sub-nav-group">
                      <div
                        className={`sub-nav-item ${expandedSubItem === sub.label ? 'expanded' : ''}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (sub.onClick) {
                            sub.onClick();
                          } else if (sub.nestedItems) {
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
              <span style={{ fontSize: '0.9rem', color: '#64748b', fontWeight: 500 }}>
                Role: <span style={{ color: '#6366f1', textTransform: 'capitalize' }}>{userRole.replace('_', ' ')}</span>
              </span>
            </div>
          </div>
        </header>

        <div className="dashboard-body">
          {userRole === 'student' ? (
            <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              {/* AI Assessments Practice Card */}
              <div className="glass-card" style={{ minHeight: '320px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '2rem' }}>
                <div>
                  <div className="card-header" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
                    <div className="card-icon" style={{ background: '#e0e7ff', color: '#4338ca', width: '50px', height: '50px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Brain size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, marginLeft: '1rem' }}>AI Practice Assessment</h3>
                  </div>
                  <p style={{ color: '#64748b', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '2rem' }}>
                    Take automated mock assessments matching your skills. Practice MCQ, MSQ, TF, and Coding questions with detailed feedback.
                  </p>
                </div>
                <div className="card-actions">
                  <button
                    className="btn-premium btn-fill"
                    style={{ width: '100%', padding: '0.85rem', fontSize: '0.95rem' }}
                    onClick={() => navigate('/ai-assessments')}
                  >
                    Start Practice Assessment
                  </button>
                </div>
              </div>

              {/* AI Interviews Practice Card */}
              <div className="glass-card" style={{ minHeight: '320px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '2rem' }}>
                <div>
                  <div className="card-header" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center' }}>
                    <div className="card-icon" style={{ background: '#fef3c7', color: '#d97706', width: '50px', height: '50px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Sparkles size={24} />
                    </div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, marginLeft: '1rem' }}>AI Mock Interview</h3>
                  </div>
                  <p style={{ color: '#64748b', fontSize: '0.95rem', lineHeight: '1.6', marginBottom: '2rem' }}>
                    Practice standard AI video/voice mock interviews. Improve your soft skills and technical articulation in real-time prep sessions.
                  </p>
                </div>
                <div className="card-actions" style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    className="btn-premium btn-fill"
                    style={{ flex: 1, padding: '0.85rem', fontSize: '0.95rem' }}
                    onClick={() => navigate('/student/ai-interview')}
                  >
                    Start Mock Interview
                  </button>
                  <button
                    className="btn-premium btn-outline"
                    style={{ flex: 1, padding: '0.85rem', fontSize: '0.95rem' }}
                    onClick={() => navigate('/student/sessions')}
                  >
                    My Sessions
                  </button>
                </div>
              </div>
            </div>
          ) : userRole === 'interviewer' ? (
            <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
              {/* Availability Management for Interviewer */}
              <div className="glass-card" style={{ minHeight: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '2rem' }}>
                <div className="card-icon" style={{ background: '#e0e7ff', color: '#4338ca', width: '60px', height: '60px', marginBottom: '1.5rem' }}>
                  <Clock size={32} />
                </div>
                <h2 style={{ marginBottom: '1rem' }}>Manage Availability</h2>
                <p style={{ color: '#64748b', marginBottom: '2rem', maxWidth: '400px' }}>
                  Set your preferred working hours and 50-minute slots. Candidates will be able to book sessions during these times.
                </p>
                <button
                  className="btn-premium btn-fill"
                  style={{ padding: '1rem 2rem', fontSize: '1rem' }}
                  onClick={() => navigate('/manage-availability')}
                >
                  Configure Slots
                </button>
              </div>

              {/* Live Interviews for Interviewer */}
              <div className="glass-card" style={{ minHeight: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '2rem' }}>
                <div className="card-icon" style={{ background: '#dcfce7', color: '#16a34a', width: '60px', height: '60px', marginBottom: '1.5rem' }}>
                  <Video size={32} />
                </div>
                <h2 style={{ marginBottom: '1rem' }}>Join Interviews</h2>
                <p style={{ color: '#64748b', marginBottom: '2rem', maxWidth: '400px' }}>
                  View your upcoming scheduled sessions and join live technical interviews with candidates.
                </p>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button
                    className="btn-premium btn-fill"
                    style={{ padding: '1rem 2rem', fontSize: '1rem' }}
                    onClick={() => navigate('/live-interview-list')}
                  >
                    View Schedule
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <>
              {/* Top Row: Core Modules */}
              <div className="dashboard-grid">
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
                      <span className="stat-label">Resumes Analyzed</span>
                      <span className="stat-value">{data.stats.resumesAnalyzed}</span>
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
                    <button className="btn-premium btn-outline" style={{ borderColor: '#6366f1', color: '#6366f1' }} onClick={() => navigate('/results-ai?tab=fully_automatic')}>Fully Automatic Results</button>
                  </div>
                </div>

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

                {/* AI Interviews */}
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
                    <button className="btn-premium btn-outline" onClick={() => navigate('/ai-interviews-overview')}>Interviews</button>
                  </div>
                </div>
              </div>

              {/* Middle Row: Interviews and Custom Assessments */}
              <div className="dashboard-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
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

                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-icon" style={{ background: '#dcfce7', color: '#16a34a' }}>
                      <Video size={20} />
                    </div>
                    <h3>Live Interviews</h3>
                  </div>
                  <div className="card-stat-row">
                    <div className="stat-item">
                      <span className="stat-label">Live Interviews</span>
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
                    <div className="stat-item" style={{ borderRight: 'none' }}>
                      <span className="stat-label">Total Candidates</span>
                      <span className="stat-value">{data.stats.totalCandidates}</span>
                    </div>
                    <div className="stat-item" style={{ borderRight: 'none' }}>
                      <span className="stat-label">In Pipeline</span>
                      <span className="stat-value">{data.stats.inPipeline}</span>
                    </div>
                    <div className="stat-item" style={{ borderRight: 'none' }}>
                      <span className="stat-label">Hired</span>
                      <span className="stat-value">{data.stats.hired}</span>
                    </div>
                  </div>

                  <div className="candidate-list">
                    <h4 style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '0.5rem' }}>Recent Candidates</h4>
                    {data.recentCandidates.length > 0 ? data.recentCandidates.map((cand, i) => (
                      <div key={i} className="candidate-row">
                        <div className="candidate-info">
                          <div className="candidate-avatar">{cand.candidate?.name ? cand.candidate.name.charAt(0) : '?'}</div>
                          <div>
                            <div className="cand-name">{cand.candidate?.name || 'Anonymous'}</div>
                            <div className="cand-email">{cand.candidate?.email}</div>
                          </div>
                        </div>
                        <span className={`status-badge ${['selected', 'Qualified', 'COMPLETED'].includes(cand.status) ? 'status-hired' : ['rejected', 'failed'].includes(cand.status?.toLowerCase()) ? 'status-rejected' : 'status-in-pipeline'}`}>
                          {['selected', 'Qualified', 'COMPLETED'].includes(cand.status) ? 'Qualified' : ['rejected', 'failed'].includes(cand.status?.toLowerCase()) ? 'Rejected' : cand.status === 'sent' ? 'Sent' : cand.status === 'ongoing' ? 'Ongoing' : 'In Pipeline'}
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
                      <select 
                        className="filter-select"
                        value={selectedYear}
                        onChange={(e) => setSelectedYear(e.target.value)}
                      >
                        <option value="">Year</option>
                        {Array.from({ length: 5 }, (_, i) => {
                          const year = new Date().getFullYear() - i;
                          return <option key={year} value={year}>{year}</option>;
                        })}
                      </select>
                    </div>
                  </div>
                  <div className="chart-container" style={{ height: '300px', minHeight: '300px' }}>
                    <ResponsiveContainer width="100%" height="100%" debounce={100}>
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

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem', marginTop: '2rem' }}>
                    <div className="glass-card" style={{ padding: '1rem', background: 'white' }}>
                      <h4 style={{ fontSize: '0.8rem', margin: '0 0 1rem' }}>Candidate Success Rate</h4>
                      <div style={{ height: '100px', width: '100%', minHeight: '100px' }}>
                        <ResponsiveContainer width="100%" height="100%" debounce={100}>
                          <BarChart data={data.successRate}>
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} />
                            <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                            <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} barSize={20} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
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

      {/* Manage Job Roles Modal */}
      {isManageModalOpen && (
        <div
          className="modal-overlay"
          onClick={() => setIsManageModalOpen(false)}
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
              maxWidth: '700px',
              width: '90%',
              maxHeight: '85vh',
              padding: '2rem',
              background: 'white',
              borderRadius: '2rem',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexShrink: 0 }}>
              <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>Manage Job Roles</h3>
              <button className="icon-btn" onClick={() => setIsManageModalOpen(false)}><ChevronDown size={20} /></button>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', paddingRight: '0.5rem', marginBottom: '1.5rem' }}>
              {isLoadingRoles ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  <div className="loader" style={{ fontSize: '1rem' }}>Loading Job Roles...</div>
                </div>
              ) : rolesList.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b', fontSize: '0.95rem' }}>
                  No job roles found. Create one to get started!
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%' }}>
                  {rolesList.map((role) => (
                    <div 
                      key={role.id} 
                      style={{ 
                        background: '#f8fafc', 
                        border: '1px solid #e2e8f0', 
                        borderRadius: '16px', 
                        padding: '1.25rem',
                        transition: 'all 0.2s',
                        width: '100%',
                        minWidth: 0
                      }}
                    >
                      {editingRoleId === role.id ? (
                        <form onSubmit={handleSaveEdit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#64748b', marginBottom: '0.25rem' }}>Role Title</label>
                            <input
                              type="text"
                              className="filter-select"
                              style={{ width: '100%', height: '38px', padding: '0 0.75rem', borderRadius: '8px' }}
                              value={editFormData.title}
                              onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })}
                              required
                            />
                          </div>
                          <div>
                            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#64748b', marginBottom: '0.25rem' }}>Description</label>
                            <textarea
                              className="filter-select"
                              style={{ width: '100%', minHeight: '80px', padding: '0.5rem 0.75rem', borderRadius: '8px', resize: 'vertical' }}
                              value={editFormData.description}
                              onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                              required
                            />
                          </div>
                          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                            <button type="button" className="btn-premium btn-outline" style={{ padding: '0.4rem 1rem', fontSize: '0.75rem' }} onClick={() => setEditingRoleId(null)}>Cancel</button>
                            <button type="submit" className="btn-premium btn-fill" style={{ padding: '0.4rem 1rem', fontSize: '0.75rem' }} disabled={isSavingEdit}>
                              {isSavingEdit ? 'Saving...' : 'Save Changes'}
                            </button>
                          </div>
                        </form>
                      ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%', minWidth: 0 }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', width: '100%', minWidth: 0 }}>
                            <h4 style={{ margin: 0, fontWeight: 700, color: '#1e293b', fontSize: '1rem', wordBreak: 'break-all', overflowWrap: 'break-word', flex: 1, minWidth: 0 }}>{role.title}</h4>
                            <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                              <button 
                                className="btn-premium btn-outline" 
                                style={{ padding: '0.35rem 0.75rem', fontSize: '0.7rem', borderColor: '#cbd5e1' }}
                                onClick={() => handleEditRole(role)}
                              >
                                Edit
                              </button>
                              <button 
                                className="btn-premium btn-outline" 
                                style={{ padding: '0.35rem 0.75rem', fontSize: '0.7rem', borderColor: '#fca5a5', color: '#ef4444' }}
                                onClick={() => handleDeleteRole(role.id)}
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                          <p style={{ margin: 0, fontSize: '0.85rem', color: '#475569', whiteSpace: 'pre-wrap', lineHeight: '1.5', wordBreak: 'break-all', overflowWrap: 'break-word', width: '100%', minWidth: 0 }}>
                            {role.description}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid #e2e8f0', paddingTop: '1rem', flexShrink: 0 }}>
              <button className="btn-premium btn-fill" style={{ padding: '0.6rem 1.5rem' }} onClick={() => setIsManageModalOpen(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
