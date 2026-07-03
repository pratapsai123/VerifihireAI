import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import FilterBar from '../components/FilterBar';
import Pagination from '../components/Pagination';

const STATUS_COLORS = {
  Scheduled: { bg: 'rgba(59, 130, 246, 0.1)', text: '#3B82F6', border: 'rgba(59, 130, 246, 0.2)' },
  Ongoing: { bg: 'rgba(245, 158, 11, 0.1)', text: '#F59E0B', border: 'rgba(245, 158, 11, 0.2)' },
  Completed: { bg: 'rgba(16, 185, 129, 0.1)', text: '#10B981', border: 'rgba(16, 185, 129, 0.2)' },
};

function StatusBadge({ status }) {
  const c = STATUS_COLORS[status] || { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
  return (
    <span style={{
      padding: '4px 12px', borderRadius: '999px', fontSize: '0.65rem',
      fontWeight: 800, letterSpacing: '0.05em', background: c.bg,
      color: c.text, border: `1px solid ${c.border}`, textTransform: 'uppercase',
    }}>
      {status}
    </span>
  );
}

function StudentPrepPage() {
  const [sessions, setSessions] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Selection drawer
  const [selectedSession, setSelectedSession] = useState(null);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [sessionDetail, setSessionDetail] = useState(null);

  // Filters & Pagination
  const [statusFilter, setStatusFilter] = useState('');
  const [minScore, setMinScore] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const fetchSessions = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const params = {
        page: currentPage,
        search: search,
        status: statusFilter,
        score: minScore
      };
      
      const res = await axios.get(`${API_BASE_URL}/superadmin/student-prep-sessions/`, { params });
      setSessions(res.data.sessions || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to load student prep sessions:', err);
    } finally {
      if (!silent) setLoading(false);
    }
  }, [currentPage, search, statusFilter, minScore]);

  useEffect(() => {
    fetchSessions();
    const interval = setInterval(() => fetchSessions(true), 30000);
    return () => clearInterval(interval);
  }, [fetchSessions]);

  const loadSessionDetail = async (id) => {
    setDrawerLoading(true);
    try {
      const res = await axios.get(`${API_BASE_URL}/superadmin/student-prep-sessions/${id}/`);
      setSessionDetail(res.data);
    } catch (err) {
      console.error('Failed to fetch session detail:', err);
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleRowClick = (session) => {
    setSelectedSession(session);
    setSessionDetail(null);
    loadSessionDetail(session.id);
  };

  // KPIs
  const totalSessionsCount = total;
  const activeSessionsCount = sessions.filter(s => s.status !== 'Completed').length;
  const completedSessions = sessions.filter(s => s.status === 'Completed' && s.score !== null);
  const averageScore = completedSessions.length > 0 
    ? Math.round(completedSessions.reduce((acc, curr) => acc + (curr.score || 0), 0) / completedSessions.length) 
    : 'N/A';
  const highPerformers = sessions.filter(s => s.status === 'Completed' && (s.score || 0) >= 80).length;

  return (
    <div style={{ animation: 'slideIn 0.4s ease-out' }}>
      {/* Header */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800, color: '#2B3674', letterSpacing: '-0.5px' }}>
            Student Prep Sessions
          </h1>
          <p style={{ margin: '6px 0 0', color: '#707EAE', fontSize: '0.9rem', fontWeight: 500 }}>
            Monitor B2C student mock assessments and interviews. Total Sessions: <span style={{ color: '#4318FF', fontWeight: 700 }}>{total}</span>
          </p>
        </div>

        <div style={{ position: 'relative' }}>
          <span style={{
            position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)',
            fontSize: '1rem', color: '#A3AED0',
          }}>🔍</span>
          <input
            type="text" placeholder="Search students, roles..."
            value={search} onChange={e => { setSearch(e.target.value); setCurrentPage(1); }}
            style={{
              padding: '14px 20px 14px 48px', borderRadius: '16px',
              border: '1px solid #f0f3f8', fontSize: '0.9rem', outline: 'none',
              width: 340, background: '#fff', boxShadow: '0 4px 15px rgba(0,0,0,0.03)',
              color: '#2B3674', fontWeight: 600
            }}
          />
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '24px' }}>
        {[
          { label: 'Total Sessions', value: totalSessionsCount, icon: '🎓', color: '#4318FF' },
          { label: 'Active Practice', value: activeSessionsCount, icon: '⚡', color: '#FFB547' },
          { label: 'Average Score', value: averageScore + (averageScore !== 'N/A' ? '%' : ''), icon: '📊', color: '#10B981' },
          { label: 'High Performers (>=80)', value: highPerformers, icon: '🏆', color: '#EE5D50' },
        ].map((kpi, idx) => (
          <div key={idx} style={{
            background: '#fff', borderRadius: 20, padding: '20px 24px',
            display: 'flex', alignItems: 'center', gap: 20,
            border: '1px solid #f0f3f8', boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)'
          }}>
            <div style={{
              fontSize: '1.8rem', width: 50, height: 50, borderRadius: '14px',
              background: '#F4F7FE', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>{kpi.icon}</div>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#A3AED0', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{kpi.label}</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#2B3674', marginTop: 4 }}>{kpi.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters Bar */}
      <div style={{
        background: '#fff', borderRadius: 20, padding: '16px 24px',
        display: 'flex', flexWrap: 'wrap', gap: '20px', alignItems: 'center',
        border: '1px solid #f0f3f8', boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#2B3674' }}>Status:</span>
          <select 
            value={statusFilter} 
            onChange={e => { setStatusFilter(e.target.value); setCurrentPage(1); }}
            style={{ padding: '8px 12px', borderRadius: 10, border: '1px solid #e2e8f0', outline: 'none', fontSize: '0.85rem', color: '#2B3674', fontWeight: 600 }}
          >
            <option value="">All Statuses</option>
            <option value="Scheduled">Scheduled</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Completed">Completed</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#2B3674' }}>Min Score:</span>
          <input 
            type="number" 
            placeholder="Min Score"
            value={minScore} 
            onChange={e => { setMinScore(e.target.value); setCurrentPage(1); }}
            style={{ padding: '8px 12px', width: '100px', borderRadius: 10, border: '1px solid #e2e8f0', outline: 'none', fontSize: '0.85rem', color: '#2B3674', fontWeight: 600 }}
          />
        </div>

        <button 
          onClick={() => { setStatusFilter(''); setMinScore(''); setSearch(''); setCurrentPage(1); }}
          style={{
            marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer',
            color: '#4318FF', fontWeight: 700, fontSize: '0.85rem'
          }}
        >
          Reset Filters
        </button>
      </div>

      {/* Directory Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '6rem' }}>
          <div className="spinner" style={{
            width: 48, height: 48, border: '4px solid #f3f3f3',
            borderTop: '4px solid #4318FF', borderRadius: '50%',
            margin: '0 auto 16px', animation: 'spin 1.5s linear infinite'
          }} />
          <span style={{ fontWeight: 700, fontSize: '1rem', color: '#A3AED0', letterSpacing: '1px' }}>SYNCHRONIZING DIR...</span>
        </div>
      ) : sessions.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '6rem', background: '#fff', borderRadius: 32,
          boxShadow: '0 20px 40px rgba(112, 144, 176, 0.08)', color: '#A3AED0'
        }}>
          <div style={{ fontSize: '5rem', marginBottom: 24 }}>🎓</div>
          <div style={{ fontWeight: 800, fontSize: '1.4rem', color: '#2B3674' }}>No Mock Sessions Found</div>
        </div>
      ) : (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
            {sessions.map(session => (
              <div key={session.id} style={{
                background: '#fff', borderRadius: 20, padding: '24px',
                display: 'flex', alignItems: 'center', gap: '24px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)',
                border: '1px solid #f0f3f8', cursor: 'pointer'
              }}
                onClick={() => handleRowClick(session)}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 10px 20px rgba(112, 144, 176, 0.12)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 15px rgba(112, 144, 176, 0.08)';
                }}
              >
                <div style={{
                  width: 56, height: 56, borderRadius: 16,
                  background: 'rgba(67, 24, 255, 0.1)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#4318FF',
                  fontWeight: 800, fontSize: '1.4rem', flexShrink: 0,
                  border: '1px solid rgba(0,0,0,0.03)'
                }}>
                  {session.full_name.charAt(0).toUpperCase()}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
                    <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#2B3674', letterSpacing: '-0.3px' }}>{session.full_name}</span>
                    <StatusBadge status={session.status} />
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', color: '#707EAE', fontSize: '0.8rem', fontWeight: 500 }}>
                    <span>📧 {session.email}</span>
                    <span>📞 {session.phone || 'No phone'}</span>
                    <span>🎓 Role: <strong>{session.target_role}</strong></span>
                    <span>⏳ Level: <strong>{session.experience_level}</strong></span>
                  </div>
                </div>

                <div style={{ textAlign: 'right', display: 'flex', gap: '20px', alignItems: 'center' }}>
                  <div style={{ borderLeft: '1px solid #f0f3f8', paddingLeft: 20 }}>
                    <div style={{ fontSize: '0.65rem', color: '#A3AED0', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.8px' }}>Scheduled Time</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#2B3674', marginTop: 2 }}>
                      {session.scheduled_time 
                        ? new Date(session.scheduled_time).toLocaleString('en-US', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) 
                        : 'N/A'
                      }
                    </div>
                  </div>
                  <div style={{ borderLeft: '1px solid #f0f3f8', paddingLeft: 20, width: '90px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.65rem', color: '#A3AED0', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.8px' }}>Performance</div>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: session.score >= 80 ? '#10B981' : session.score >= 50 ? '#F59E0B' : '#2B3674', marginTop: 2 }}>
                      {session.status === 'Completed' && session.score !== null ? session.score + '%' : '--'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <Pagination
            currentPage={currentPage}
            totalItems={total}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
            onPageSizeChange={setPageSize}
          />
        </>
      )}

      {/* Details Side Drawer */}
      {selectedSession && (
        <div style={{
          position: 'fixed', right: 0, top: 0, height: '100vh', width: '600px',
          background: '#fff', boxShadow: '-10px 0 40px rgba(0,0,0,0.1)',
          zIndex: 2000, display: 'flex', flexDirection: 'column',
          animation: 'slideLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        }}>
          {/* Header */}
          <div style={{ padding: '24px', borderBottom: '1px solid #f0f3f8', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: '1.3rem', fontWeight: 800, color: '#2B3674' }}>Candidate Session Detail</h2>
              <span style={{ fontSize: '0.8rem', color: '#707EAE', fontWeight: 500 }}>ID: {selectedSession.id}</span>
            </div>
            <button 
              onClick={() => setSelectedSession(null)}
              style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#A3AED0' }}
            >
              &times;
            </button>
          </div>

          {/* Drawer Body */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
            {drawerLoading ? (
              <div style={{ textAlign: 'center', padding: '4rem' }}>
                <div className="spinner" style={{
                  width: 36, height: 36, border: '3px solid #f3f3f3',
                  borderTop: '3px solid #4318FF', borderRadius: '50%',
                  margin: '0 auto 12px', animation: 'spin 1.5s linear infinite'
                }} />
                <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#A3AED0' }}>RETRIEVING PROFILE...</span>
              </div>
            ) : sessionDetail ? (
              <div>
                {/* Candidate Summary Block */}
                <div style={{ background: '#F4F7FE', borderRadius: '16px', padding: '20px', marginBottom: '24px' }}>
                  <h3 style={{ margin: '0 0 10px', fontSize: '1.05rem', fontWeight: 800, color: '#2B3674' }}>{sessionDetail.full_name}</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: '0.85rem', color: '#707EAE', fontWeight: 600 }}>
                    <span>📧 Email: <strong style={{ color: '#2B3674' }}>{sessionDetail.email}</strong></span>
                    <span>📞 Phone: <strong style={{ color: '#2B3674' }}>{sessionDetail.phone || 'N/A'}</strong></span>
                    <span>🎓 Target Role: <strong style={{ color: '#2B3674' }}>{sessionDetail.target_role}</strong></span>
                    <span>⏳ Experience Level: <strong style={{ color: '#2B3674' }}>{sessionDetail.experience_level}</strong></span>
                    <span>🕒 Status: <StatusBadge status={sessionDetail.status} /></span>
                    {sessionDetail.score !== null && (
                      <span style={{ fontSize: '1rem', color: '#4318FF', marginTop: '6px' }}>
                        Performance Score: <strong style={{ fontSize: '1.25rem' }}>{sessionDetail.score}%</strong>
                      </span>
                    )}
                  </div>
                </div>

                {/* Tab Navigation inside Drawer */}
                <DrawerTabs session={sessionDetail} />
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#EE5D50', fontWeight: 600 }}>Failed to load details.</div>
            )}
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        @keyframes slideLeft { from { transform: translateX(100%); } to { transform: translateX(0); } }
      `}</style>
    </div>
  );
}

function DrawerTabs({ session }) {
  const [activeTab, setActiveTab] = useState('transcript');

  return (
    <div>
      <div style={{ display: 'flex', borderBottom: '2px solid #f0f3f8', marginBottom: '20px', gap: '20px' }}>
        {[
          { id: 'transcript', label: 'Interview Transcript' },
          { id: 'resume', label: 'Extracted Resume' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '10px 0', border: 'none', background: 'none', cursor: 'pointer',
              fontWeight: 700, fontSize: '0.9rem',
              color: activeTab === tab.id ? '#4318FF' : '#A3AED0',
              borderBottom: activeTab === tab.id ? '3px solid #4318FF' : '3px solid transparent',
              marginBottom: '-2px', transition: 'all 0.2s ease'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'transcript' ? (
        <div>
          {session.status !== 'Completed' ? (
            <div style={{ textAlign: 'center', padding: '30px 10px', color: '#A3AED0' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>⏳</div>
              <p style={{ margin: 0, fontWeight: 600, fontSize: '0.9rem' }}>This prep session is still {session.status}.</p>
              <p style={{ margin: '4px 0 0', fontSize: '0.8rem' }}>Transcript data will generate upon completion.</p>
            </div>
          ) : session.interview_questions && session.interview_questions.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {session.interview_questions.map((q, idx) => (
                <div key={idx} style={{
                  padding: '16px', borderRadius: '14px', border: '1px solid #f0f3f8',
                  background: '#fafbfc'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                    <strong style={{ fontSize: '0.85rem', color: '#4318FF' }}>Q{idx + 1}: Question</strong>
                    {q.score !== undefined && (
                      <span style={{
                        fontSize: '0.8rem', fontWeight: 800, 
                        color: q.score >= 80 ? '#10B981' : q.score >= 50 ? '#F59E0B' : '#EE5D50'
                      }}>
                        Score: {q.score}/100
                      </span>
                    )}
                  </div>
                  <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#2B3674', fontWeight: 600 }}>{q.question}</p>
                  
                  {q.answer && (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontSize: '0.75rem', color: '#A3AED0', fontWeight: 700, marginBottom: 4 }}>CANDIDATE ANSWER</div>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: '#4a5568', fontStyle: 'italic', background: '#fff', padding: '10px 14px', borderRadius: '8px', border: '1px solid #edf2f7' }}>
                        {q.answer}
                      </p>
                    </div>
                  )}

                  {q.feedback && (
                    <div>
                      <div style={{ fontSize: '0.75rem', color: '#A3AED0', fontWeight: 700, marginBottom: 4 }}>AI FEEDBACK</div>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: '#2b6cb0', background: '#ebf8ff', padding: '10px 14px', borderRadius: '8px' }}>
                        {q.feedback}
                      </p>
                    </div>
                  )}
                </div>
              ))}
              
              {/* Summary Block */}
              {session.interview_summary && (
                <div style={{
                  padding: '20px', borderRadius: '16px', background: '#ebf8ff',
                  border: '1px solid #bee3f8', marginTop: 10
                }}>
                  <h4 style={{ margin: '0 0 10px', color: '#2b6cb0', fontWeight: 800, fontSize: '0.95rem' }}>AI Executive Summary</h4>
                  <p style={{ margin: 0, fontSize: '0.88rem', color: '#2d3748', lineHeight: '1.6' }}>
                    {session.interview_summary.summary || 'No summary text generated.'}
                  </p>
                  {session.interview_summary.strengths && (
                    <div style={{ marginTop: '12px' }}>
                      <strong style={{ fontSize: '0.8rem', color: '#2c5282' }}>Key Strengths:</strong>
                      <ul style={{ margin: '6px 0 0', paddingLeft: '20px', fontSize: '0.83rem', color: '#2d3748' }}>
                        {session.interview_summary.strengths.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: '#A3AED0', textAlign: 'center', fontSize: '0.9rem' }}>No turn-by-turn transcript recorded.</p>
          )}
        </div>
      ) : (
        <div>
          <div style={{
            background: '#fafbfc', borderRadius: '14px', padding: '16px',
            border: '1px solid #f0f3f8', maxHeight: '450px', overflowY: 'auto'
          }}>
            <h4 style={{ margin: '0 0 10px', fontSize: '0.85rem', color: '#707EAE', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Extracted Plaintext</h4>
            {session.resume_text ? (
              <pre style={{
                margin: 0, whiteSpace: 'pre-wrap', fontSize: '0.8rem',
                color: '#4a5568', lineHeight: '1.5', fontFamily: 'inherit'
              }}>{session.resume_text}</pre>
            ) : (
              <p style={{ color: '#A3AED0', margin: 0, fontSize: '0.85rem' }}>No resume text has been extracted for this session.</p>
            )}
          </div>
          {session.resume_url && (
            <div style={{ marginTop: 16, textAlign: 'right' }}>
              <a
                href={`${API_BASE_URL.replace('/api', '')}${session.resume_url}`}
                target="_blank"
                rel="noreferrer"
                style={{
                  color: '#4318FF', fontWeight: 700, fontSize: '0.85rem',
                  textDecoration: 'none'
                }}
              >
                📥 Download Original Resume File
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default StudentPrepPage;
