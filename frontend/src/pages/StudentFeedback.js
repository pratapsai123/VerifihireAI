import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, Minus, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/StudentAiInterview.css';

const StudentFeedback = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchFeedback = async () => {
            try {
                const resp = await axios.get(`${API_BASE_URL}/students/feedback/${token}/`);
                setData(resp.data);
            } catch (err) {
                setError(err.response?.data?.error || 'Failed to load feedback.');
            } finally {
                setLoading(false);
            }
        };
        fetchFeedback();
    }, [token]);

    if (loading) return <div className="student-ai-wrapper"><div className="student-ai-content"><p style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>Loading feedback...</p></div></div>;
    if (error) return <div className="student-ai-wrapper"><div className="student-ai-content"><p style={{ textAlign: 'center', padding: '3rem', color: '#ef4444' }}>{error}</p></div></div>;
    if (!data) return null;

    const getScoreColor = (score) => score >= 8 ? '#22c55e' : score >= 6 ? '#f59e0b' : score >= 4 ? '#f97316' : '#ef4444';
    const getPerformanceIcon = (perf) => {
        if (perf === 'excellent') return <CheckCircle size={16} style={{ color: '#22c55e' }} />;
        if (perf === 'good') return <TrendingUp size={16} style={{ color: '#f59e0b' }} />;
        if (perf === 'needs_improvement') return <AlertCircle size={16} style={{ color: '#f97316' }} />;
        return <XCircle size={16} style={{ color: '#ef4444' }} />;
    };

    return (
        <div className="student-ai-wrapper">
            <div className="student-ai-mesh-bg"></div>
            <div className="student-ai-content" style={{ maxWidth: '900px' }}>
                
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
                    <button onClick={() => navigate('/student/ai-interview')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#6366f1' }}>
                        <ArrowLeft size={24} />
                    </button>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>Interview Feedback</h2>
                        <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '0.9rem' }}>{data.job_title} • {data.experience_level}</p>
                    </div>
                </div>

                {/* Score Summary */}
                <section className="glass-panel" style={{ marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                        <div>
                            <div style={{ fontSize: '3rem', fontWeight: 800, color: data.percentage >= 70 ? '#22c55e' : data.percentage >= 50 ? '#f59e0b' : '#ef4444' }}>
                                {data.percentage}%
                            </div>
                            <div style={{ color: '#64748b', fontSize: '0.85rem' }}>
                                {data.total_score}/{data.total_possible} points • {data.total_questions_answered} questions answered
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <div style={{ textAlign: 'center', padding: '0.75rem 1.25rem', borderRadius: '12px', background: '#f0fdf4' }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#22c55e' }}>{data.summary.excellent_count}</div>
                                <div style={{ fontSize: '0.7rem', color: '#166534' }}>Excellent</div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '0.75rem 1.25rem', borderRadius: '12px', background: '#fefce8' }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f59e0b' }}>{data.summary.good_count}</div>
                                <div style={{ fontSize: '0.7rem', color: '#92400e' }}>Good</div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '0.75rem 1.25rem', borderRadius: '12px', background: '#fff7ed' }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f97316' }}>{data.summary.needs_improvement_count}</div>
                                <div style={{ fontSize: '0.7rem', color: '#9a3412' }}>Improve</div>
                            </div>
                            <div style={{ textAlign: 'center', padding: '0.75rem 1.25rem', borderRadius: '12px', background: '#fef2f2' }}>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#ef4444' }}>{data.summary.poor_count}</div>
                                <div style={{ fontSize: '0.7rem', color: '#991b1b' }}>Poor</div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Strengths & Weaknesses & Recommendations */}
                {(data.strengths.length > 0 || data.weaknesses.length > 0 || data.recommendations?.length > 0) && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
                        {data.recommendations?.length > 0 && (
                            <section className="glass-panel" style={{ borderLeft: '4px solid #6366f1' }}>
                                <h4 style={{ margin: '0 0 0.75rem', color: '#4338ca', fontSize: '0.9rem' }}>📚 Study Recommendations</h4>
                                {data.recommendations.map((r, i) => (
                                    <p key={i} style={{ margin: '0.4rem 0', fontSize: '0.85rem', color: '#374151', lineHeight: '1.5' }}>• {r}</p>
                                ))}
                            </section>
                        )}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            {data.strengths.length > 0 && (
                                <section className="glass-panel" style={{ borderLeft: '4px solid #22c55e' }}>
                                    <h4 style={{ margin: '0 0 0.75rem', color: '#166534', fontSize: '0.9rem' }}>✓ Strengths</h4>
                                    {data.strengths.map((s, i) => (
                                        <p key={i} style={{ margin: '0.25rem 0', fontSize: '0.8rem', color: '#374151' }}>• {s}</p>
                                    ))}
                                </section>
                            )}
                            {data.weaknesses.length > 0 && (
                                <section className="glass-panel" style={{ borderLeft: '4px solid #ef4444' }}>
                                    <h4 style={{ margin: '0 0 0.75rem', color: '#991b1b', fontSize: '0.9rem' }}>⚠ Areas to Improve</h4>
                                    {data.weaknesses.map((w, i) => (
                                        <p key={i} style={{ margin: '0.25rem 0', fontSize: '0.8rem', color: '#374151' }}>• {w}</p>
                                    ))}
                                </section>
                            )}
                        </div>
                    </div>
                )}

                {/* Per-Question Breakdown */}
                <section className="glass-panel">
                    <h3 style={{ margin: '0 0 1.5rem', fontSize: '1.1rem', fontWeight: 700, color: '#1e293b' }}>Question-by-Question Breakdown</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {data.questions.map((q) => (
                            <div key={q.turn} style={{
                                padding: '1.25rem', borderRadius: '12px',
                                border: `1px solid ${q.score >= 7 ? '#bbf7d0' : q.score >= 5 ? '#fde68a' : '#fecaca'}`,
                                background: q.score >= 7 ? '#fafff9' : q.score >= 5 ? '#fffbeb' : '#fff5f5',
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        {getPerformanceIcon(q.performance)}
                                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b' }}>Q{q.turn}</span>
                                    </div>
                                    <span style={{ fontSize: '1rem', fontWeight: 800, color: getScoreColor(q.score) }}>
                                        {q.score}/10
                                    </span>
                                </div>
                                <p style={{ margin: '0 0 0.5rem', fontWeight: 600, color: '#1e293b', fontSize: '0.9rem' }}>{q.question}</p>
                                <p style={{ margin: '0 0 0.5rem', color: '#475569', fontSize: '0.85rem', fontStyle: 'italic' }}>Your answer: {q.answer?.substring(0, 200)}{q.answer?.length > 200 ? '...' : ''}</p>
                                <p style={{ margin: '0', color: '#6366f1', fontSize: '0.8rem', fontWeight: 500 }}>💡 {q.feedback || q.score_reason}</p>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
};

export default StudentFeedback;
