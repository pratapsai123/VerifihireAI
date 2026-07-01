import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Play, CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/StudentAiInterview.css';

const StudentSessions = () => {
    const navigate = useNavigate();
    const [interviews, setInterviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, active, completed

    useEffect(() => {
        const fetchSessions = async () => {
            try {
                const resp = await axios.get(`${API_BASE_URL}/students/my-interviews/`);
                setInterviews(resp.data || []);
            } catch (err) {
                console.error('Failed to load sessions:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchSessions();
    }, []);

    const activeSessions = interviews.filter(i => ['Invited', 'Interview', 'New'].includes(i.status));
    const completedSessions = interviews.filter(i => !['Invited', 'Interview', 'New'].includes(i.status));

    const filtered = filter === 'active' ? activeSessions : filter === 'completed' ? completedSessions : interviews;

    return (
        <div className="student-ai-wrapper">
            <div className="student-ai-mesh-bg"></div>
            <div className="student-ai-content" style={{ maxWidth: '800px' }}>

                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                    <button onClick={() => navigate('/dashboard')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6366f1' }}>
                        <ArrowLeft size={24} />
                    </button>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>My Interview Sessions</h2>
                        <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '0.9rem' }}>
                            {activeSessions.length} active • {completedSessions.length} completed
                        </p>
                    </div>
                </div>

                {/* Filter tabs */}
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                    {[{ key: 'all', label: 'All' }, { key: 'active', label: 'Active' }, { key: 'completed', label: 'Completed' }].map(tab => (
                        <button
                            key={tab.key}
                            onClick={() => setFilter(tab.key)}
                            style={{
                                padding: '0.5rem 1.25rem', borderRadius: '20px', border: 'none',
                                background: filter === tab.key ? '#6366f1' : '#f1f5f9',
                                color: filter === tab.key ? 'white' : '#64748b',
                                fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Sessions list */}
                {loading ? (
                    <p style={{ textAlign: 'center', color: '#64748b', padding: '3rem' }}>Loading sessions...</p>
                ) : filtered.length === 0 ? (
                    <section className="glass-panel" style={{ textAlign: 'center', padding: '3rem' }}>
                        <p style={{ color: '#64748b', fontSize: '1rem' }}>
                            {filter === 'active' ? 'No active sessions.' : filter === 'completed' ? 'No completed sessions yet.' : 'No sessions yet. Start a mock interview!'}
                        </p>
                        <button
                            onClick={() => navigate('/student/ai-interview')}
                            style={{
                                marginTop: '1rem', padding: '0.75rem 2rem', borderRadius: '12px', border: 'none',
                                background: '#6366f1', color: 'white', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer'
                            }}
                        >
                            Create New Interview
                        </button>
                    </section>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {filtered.map((item) => {
                            const isActive = ['Invited', 'Interview', 'New'].includes(item.status);
                            return (
                                <section key={item.id} className="glass-panel" style={{ padding: '1.25rem 1.5rem' }}>
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
                                                {item.experience_level} • {new Date(item.created_at).toLocaleDateString()}
                                                {!isActive && ` • Score: ${item.score_percentage}%`}
                                                {isActive && item.total_questions > 0 && ` • ${item.total_questions} questions answered`}
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
                                </section>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default StudentSessions;
