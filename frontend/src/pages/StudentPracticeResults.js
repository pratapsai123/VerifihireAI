import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Brain, Calendar, Clock, Award, FileText, CheckCircle, XCircle, AlertCircle, Loader2, Play, Sparkles } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CreateAssessment.css';

const StudentPracticeResults = () => {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const initialTab = searchParams.get('tab') === 'interviews' ? 'interviews' : 'assessments';
    const [activeTab, setActiveTab] = useState(initialTab);

    // Assessment results state
    const [results, setResults] = useState([]);
    const [resultsLoading, setResultsLoading] = useState(true);
    const [resultsError, setResultsError] = useState(null);

    // Interview sessions state
    const [interviews, setInterviews] = useState([]);
    const [interviewsLoading, setInterviewsLoading] = useState(true);
    const [interviewFilter, setInterviewFilter] = useState('all');

    useEffect(() => {
        const fetchResults = async () => {
            setResultsLoading(true);
            setResultsError(null);
            try {
                const token = localStorage.getItem('token');
                const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
                const res = await axios.get(`${API_BASE_URL}/students/assessments/results/`, config);
                setResults(res.data);
            } catch (err) {
                console.error('Error fetching practice results:', err);
                setResultsError(err.response?.data?.error || err.response?.data?.message || 'Failed to load practice results.');
            } finally {
                setResultsLoading(false);
            }
        };
        fetchResults();
    }, []);

    useEffect(() => {
        const fetchSessions = async () => {
            setInterviewsLoading(true);
            try {
                const resp = await axios.get(`${API_BASE_URL}/students/my-interviews/`);
                setInterviews(resp.data || []);
            } catch (err) {
                console.error('Failed to load sessions:', err);
            } finally {
                setInterviewsLoading(false);
            }
        };
        fetchSessions();
    }, []);

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        setSearchParams({ tab });
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        const d = new Date(dateStr);
        return d.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Interview helpers
    const activeSessions = interviews.filter(i => ['Invited', 'Interview', 'New'].includes(i.status));
    const completedSessions = interviews.filter(i => !['Invited', 'Interview', 'New'].includes(i.status));
    const filteredInterviews = interviewFilter === 'active' ? activeSessions : interviewFilter === 'completed' ? completedSessions : interviews;

    return (
        <div className="create-assessment-page" style={{ paddingTop: '2rem', paddingBottom: '4rem', minHeight: '85vh' }}>
            <div className="assessment-container" style={{ maxWidth: '900px', margin: '0 auto' }}>

                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '1.5rem' }}>
                    <button
                        onClick={() => navigate('/dashboard')}
                        style={{
                            background: 'white',
                            border: '1px solid #E2E8F0',
                            borderRadius: '12px',
                            width: '40px',
                            height: '40px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            color: '#4B5563',
                            transition: 'all 0.2s',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
                        }}
                    >
                        <ArrowLeft size={18} />
                    </button>
                    <div>
                        <h1 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#111827', margin: 0, letterSpacing: '-0.02em' }}>
                            Practice <span style={{ color: '#4F46E5' }}>Results</span>
                        </h1>
                        <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.25rem 0 0 0' }}>
                            Review your interview sessions and assessment scores.
                        </p>
                    </div>
                </div>

                {/* Toggle Tabs */}
                <div style={{
                    display: 'flex',
                    gap: '0',
                    marginBottom: '2rem',
                    background: '#F1F5F9',
                    borderRadius: '14px',
                    padding: '4px',
                    width: 'fit-content'
                }}>
                    <button
                        onClick={() => handleTabChange('interviews')}
                        style={{
                            padding: '0.65rem 1.75rem',
                            borderRadius: '10px',
                            border: 'none',
                            background: activeTab === 'interviews' ? 'white' : 'transparent',
                            color: activeTab === 'interviews' ? '#4F46E5' : '#64748b',
                            fontSize: '0.9rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            boxShadow: activeTab === 'interviews' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                        }}
                    >
                        <Sparkles size={16} />
                        Interviews
                    </button>
                    <button
                        onClick={() => handleTabChange('assessments')}
                        style={{
                            padding: '0.65rem 1.75rem',
                            borderRadius: '10px',
                            border: 'none',
                            background: activeTab === 'assessments' ? 'white' : 'transparent',
                            color: activeTab === 'assessments' ? '#4F46E5' : '#64748b',
                            fontSize: '0.9rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            boxShadow: activeTab === 'assessments' ? '0 2px 8px rgba(0,0,0,0.08)' : 'none',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                        }}
                    >
                        <Brain size={16} />
                        Assessments
                    </button>
                </div>

                {/* Interviews Tab Content */}
                {activeTab === 'interviews' && (
                    <div>
                        {/* Sub-filter tabs */}
                        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                            {[{ key: 'all', label: 'All' }, { key: 'active', label: 'Active' }, { key: 'completed', label: 'Completed' }].map(tab => (
                                <button
                                    key={tab.key}
                                    onClick={() => setInterviewFilter(tab.key)}
                                    style={{
                                        padding: '0.45rem 1.1rem', borderRadius: '20px', border: 'none',
                                        background: interviewFilter === tab.key ? '#6366f1' : '#f1f5f9',
                                        color: interviewFilter === tab.key ? 'white' : '#64748b',
                                        fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer',
                                        transition: 'all 0.2s'
                                    }}
                                >
                                    {tab.label}
                                </button>
                            ))}
                            <span style={{ marginLeft: 'auto', fontSize: '0.82rem', color: '#64748b', display: 'flex', alignItems: 'center' }}>
                                {activeSessions.length} active &bull; {completedSessions.length} completed
                            </span>
                        </div>

                        {interviewsLoading ? (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '250px', background: 'white', borderRadius: '20px', border: '1px solid #E2E8F0', padding: '3rem' }}>
                                <Loader2 size={36} style={{ color: '#4F46E5', animation: 'spin 1s linear infinite' }} />
                                <p style={{ marginTop: '1rem', color: '#6B7280', fontWeight: '500' }}>Loading sessions...</p>
                            </div>
                        ) : filteredInterviews.length === 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '250px', background: 'white', borderRadius: '20px', border: '1px solid #E2E8F0', padding: '3rem', textAlign: 'center' }}>
                                <div style={{ background: '#FEF3C7', color: '#D97706', width: '56px', height: '56px', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.25rem' }}>
                                    <Sparkles size={28} />
                                </div>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#111827', margin: 0 }}>No Interview Sessions</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                                    {interviewFilter === 'active' ? 'No active sessions.' : interviewFilter === 'completed' ? 'No completed sessions yet.' : 'Start a mock interview to see your sessions here.'}
                                </p>
                                <button
                                    onClick={() => navigate('/student/ai-interview')}
                                    className="btn-premium btn-fill"
                                    style={{ marginTop: '1.5rem', padding: '0.7rem 1.75rem' }}
                                >
                                    Start Mock Interview
                                </button>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {filteredInterviews.map((item) => {
                                    const isActive = ['Invited', 'Interview', 'New'].includes(item.status);
                                    return (
                                        <div
                                            key={item.id}
                                            style={{
                                                background: 'white',
                                                borderRadius: '16px',
                                                border: '1px solid #E2E8F0',
                                                padding: '1.25rem 1.5rem',
                                                transition: 'all 0.2s',
                                                boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
                                            }}
                                            onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#C7D2FE'; e.currentTarget.style.transform = 'translateY(-1px)'; }}
                                            onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.transform = 'translateY(0)'; }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <div>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                        {isActive ? (
                                                            <Clock size={16} style={{ color: '#22c55e' }} />
                                                        ) : item.score_percentage >= 70 ? (
                                                            <CheckCircle size={16} style={{ color: '#22c55e' }} />
                                                        ) : item.score_percentage >= 50 ? (
                                                            <AlertCircle size={16} style={{ color: '#f59e0b' }} />
                                                        ) : (
                                                            <XCircle size={16} style={{ color: '#ef4444' }} />
                                                        )}
                                                        <span style={{ fontWeight: 600, color: '#1e293b', fontSize: '1rem' }}>{item.job_title}</span>
                                                    </div>
                                                    <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '6px', marginLeft: '24px' }}>
                                                        {item.experience_level} &bull; {new Date(item.created_at).toLocaleDateString()}
                                                        {!isActive && ` \u2022 Score: ${item.score_percentage}%`}
                                                        {isActive && item.total_questions > 0 && ` \u2022 ${item.total_questions} questions answered`}
                                                    </div>
                                                </div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                    {!isActive && (
                                                        <span style={{
                                                            fontSize: '0.8rem', fontWeight: 700, padding: '4px 12px', borderRadius: '8px',
                                                            background: item.score_percentage >= 70 ? '#dcfce7' : item.score_percentage >= 50 ? '#fef3c7' : '#fee2e2',
                                                            color: item.score_percentage >= 70 ? '#166534' : item.score_percentage >= 50 ? '#92400e' : '#991b1b',
                                                        }}>
                                                            {item.score_percentage}%
                                                        </span>
                                                    )}
                                                    {isActive ? (
                                                        <button
                                                            onClick={() => navigate(`/ai-interview-session/${item.public_token}`)}
                                                            style={{
                                                                padding: '8px 20px', borderRadius: '10px', border: 'none',
                                                                background: '#22c55e', color: 'white', fontSize: '0.85rem',
                                                                fontWeight: 600, cursor: 'pointer'
                                                            }}
                                                        >
                                                            <Play size={14} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
                                                            {item.total_questions > 0 ? 'Continue' : 'Start'}
                                                        </button>
                                                    ) : (
                                                        <button
                                                            onClick={() => navigate(`/student/feedback/${item.public_token}`)}
                                                            style={{
                                                                padding: '8px 20px', borderRadius: '10px', border: '1px solid #e2e8f0',
                                                                background: 'white', color: '#6366f1', fontSize: '0.85rem',
                                                                fontWeight: 600, cursor: 'pointer'
                                                            }}
                                                        >
                                                            View Feedback
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}

                {/* Assessments Tab Content */}
                {activeTab === 'assessments' && (
                    <div>
                        {resultsLoading ? (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: 'white', borderRadius: '24px', border: '1px solid #E2E8F0', padding: '3rem' }}>
                                <Loader2 size={40} style={{ color: '#4F46E5', animation: 'spin 1s linear infinite' }} />
                                <p style={{ marginTop: '1rem', color: '#6B7280', fontWeight: '500' }}>Fetching your results...</p>
                            </div>
                        ) : resultsError ? (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: 'white', borderRadius: '24px', border: '1px solid #E2E8F0', padding: '3rem', textAlign: 'center' }}>
                                <AlertCircle size={48} style={{ color: '#EF4444', marginBottom: '1rem' }} />
                                <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#111827', margin: 0 }}>Error Loading Results</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.9rem', marginTop: '0.5rem', maxWidth: '400px' }}>{resultsError}</p>
                                <button
                                    onClick={() => window.location.reload()}
                                    className="btn-premium btn-fill"
                                    style={{ marginTop: '1.5rem', padding: '0.6rem 1.5rem' }}
                                >
                                    Retry
                                </button>
                            </div>
                        ) : results.length === 0 ? (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: 'white', borderRadius: '24px', border: '1px solid #E2E8F0', padding: '4rem', textAlign: 'center' }}>
                                <div style={{ background: '#EEF2FF', color: '#4F46E5', width: '64px', height: '64px', borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1.5rem' }}>
                                    <Award size={32} />
                                </div>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#111827', margin: 0 }}>No Practice Sessions Yet</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.95rem', marginTop: '0.5rem', maxWidth: '450px', lineHeight: '1.5' }}>
                                    You haven't completed any practice assessments yet. Start a new mock test to test your skills and get structured AI performance analysis.
                                </p>
                                <button
                                    onClick={() => navigate('/student/create-assessment')}
                                    className="btn-premium btn-fill"
                                    style={{ marginTop: '1.75rem', padding: '0.75rem 2rem' }}
                                >
                                    Generate Assessment
                                </button>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                                {results.map((item) => {
                                    const isPassed = item.percentage >= 60;
                                    return (
                                        <div
                                            key={item.id}
                                            style={{
                                                background: 'white',
                                                borderRadius: '20px',
                                                border: '1px solid #E2E8F0',
                                                padding: '1.75rem 2rem',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center',
                                                flexWrap: 'wrap',
                                                gap: '1.5rem',
                                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01)',
                                                transition: 'all 0.2s ease-in-out'
                                            }}
                                            onMouseEnter={(e) => {
                                                e.currentTarget.style.transform = 'translateY(-2px)';
                                                e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02)';
                                                e.currentTarget.style.borderColor = '#C7D2FE';
                                            }}
                                            onMouseLeave={(e) => {
                                                e.currentTarget.style.transform = 'translateY(0)';
                                                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01)';
                                                e.currentTarget.style.borderColor = '#E2E8F0';
                                            }}
                                        >
                                            {/* Left: Assessment details */}
                                            <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
                                                <div style={{
                                                    background: isPassed ? '#ECFDF5' : '#FEF2F2',
                                                    color: isPassed ? '#10B981' : '#EF4444',
                                                    width: '48px',
                                                    height: '48px',
                                                    borderRadius: '14px',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center'
                                                }}>
                                                    <Brain size={22} />
                                                </div>
                                                <div>
                                                    <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#1F2937', margin: 0, textTransform: 'capitalize' }}>
                                                        {item.assessment_title || 'Software Developer Mock'}
                                                    </h3>
                                                    <div style={{ display: 'flex', gap: '1.25rem', color: '#6B7280', fontSize: '0.8rem', marginTop: '0.4rem' }}>
                                                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                            <Calendar size={13} />
                                                            {formatDate(item.submitted_at || item.started_at)}
                                                        </span>
                                                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                            <FileText size={13} />
                                                            MCQ Score: {item.mcq_score} pts
                                                        </span>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Right: Score, status, actions */}
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '2.5rem', flexWrap: 'wrap' }}>
                                                <div style={{ textAlign: 'right' }}>
                                                    <div style={{ fontSize: '0.7rem', color: '#9CA3AF', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>SCORE</div>
                                                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '2px', justifyContent: 'flex-end', marginTop: '2px' }}>
                                                        <span style={{ fontSize: '1.4rem', fontWeight: '800', color: '#111827' }}>{item.percentage}%</span>
                                                    </div>
                                                </div>

                                                <div style={{
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    gap: '6px',
                                                    padding: '0.4rem 0.85rem',
                                                    borderRadius: '9999px',
                                                    fontSize: '0.8rem',
                                                    fontWeight: '600',
                                                    background: isPassed ? '#D1FAE5' : '#FEE2E2',
                                                    color: isPassed ? '#065F46' : '#991B1B'
                                                }}>
                                                    {isPassed ? <CheckCircle size={14} /> : <XCircle size={14} />}
                                                    {isPassed ? 'Qualified' : 'Below Threshold'}
                                                </div>

                                                <button
                                                    onClick={() => navigate(`/results/ai_${item.id}/report-view`)}
                                                    className="btn-premium btn-outline"
                                                    style={{ padding: '0.6rem 1.25rem', fontSize: '0.85rem', whiteSpace: 'nowrap' }}
                                                >
                                                    View Report
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                )}

            </div>
        </div>
    );
};

export default StudentPracticeResults;
