import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Trophy, Target, BookOpen, AlertTriangle, Star, Zap, TrendingUp, MessageSquare, ChevronDown, ChevronUp, ArrowUpCircle } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const StudentFeedback = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedQ, setExpandedQ] = useState(null);
    const [allExpanded, setAllExpanded] = useState(false);
    const [showScrollTop, setShowScrollTop] = useState(false);
    const [animateScore, setAnimateScore] = useState(false);

    useEffect(() => {
        const fetchFeedback = async () => {
            try {
                const resp = await axios.get(`${API_BASE_URL}/students/feedback/${token}/`);
                setData(resp.data);
                setTimeout(() => setAnimateScore(true), 300);
            } catch (err) {
                setError(err.response?.data?.error || 'Failed to load feedback.');
            } finally {
                setLoading(false);
            }
        };
        fetchFeedback();
    }, [token]);

    useEffect(() => {
        const handleScroll = () => setShowScrollTop(window.scrollY > 400);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

    const toggleExpandAll = () => {
        setAllExpanded(!allExpanded);
        setExpandedQ(null);
    };

    if (loading) return (
        <div style={styles.wrapper}>
            <div style={styles.meshBg}></div>
            <div style={{ ...styles.content, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={styles.loadingSpinner}></div>
                    <p style={{ color: '#64748b', marginTop: '1rem', fontWeight: 500 }}>Analyzing your performance...</p>
                </div>
            </div>
        </div>
    );

    if (error) return (
        <div style={styles.wrapper}>
            <div style={styles.meshBg}></div>
            <div style={{ ...styles.content, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <AlertTriangle size={48} style={{ color: '#ef4444', marginBottom: '1rem' }} />
                    <p style={{ color: '#ef4444', fontSize: '1.1rem', fontWeight: 600 }}>{error}</p>
                    <button onClick={() => navigate(-1)} style={styles.backBtnAlt}>Go Back</button>
                </div>
            </div>
        </div>
    );

    if (!data) return null;

    const scoreColor = data.percentage >= 70 ? '#10b981' : data.percentage >= 50 ? '#f59e0b' : '#6366f1';
    const scoreGrade = data.percentage >= 80 ? 'Excellent' : data.percentage >= 70 ? 'Good' : data.percentage >= 50 ? 'Average' : 'Needs Work';

    // SVG circular progress
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = animateScore ? circumference - (data.percentage / 100) * circumference : circumference;

    return (
        <div style={styles.wrapper}>
            <div style={styles.meshBg}></div>
            <div style={styles.content}>

                {/* Header */}
                <div style={styles.header}>
                    <button onClick={() => navigate('/student/results?tab=interviews')} style={styles.backBtn}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 style={styles.title}>Interview Feedback</h1>
                        <p style={styles.subtitle}>
                            <span style={styles.badge}>{data.job_title}</span>
                            <span style={styles.badgeOutline}>{data.experience_level}</span>
                            {data.completed_at && <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}> • {new Date(data.completed_at).toLocaleDateString()}</span>}
                        </p>
                    </div>
                </div>

                {/* Score Hero Card */}
                <div style={styles.heroCard}>
                    <div style={styles.heroLeft}>
                        <div style={styles.scoreRingContainer}>
                            <svg width="130" height="130" viewBox="0 0 130 130">
                                <circle cx="65" cy="65" r={radius} fill="none" stroke="#e2e8f0" strokeWidth="10" />
                                <circle
                                    cx="65" cy="65" r={radius} fill="none"
                                    stroke={scoreColor} strokeWidth="10"
                                    strokeLinecap="round"
                                    strokeDasharray={circumference}
                                    strokeDashoffset={strokeDashoffset}
                                    transform="rotate(-90 65 65)"
                                    style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
                                />
                            </svg>
                            <div style={styles.scoreRingText}>
                                <span style={{ ...styles.scoreNumber, color: scoreColor }}>{data.percentage}%</span>
                                <span style={styles.scoreGrade}>{scoreGrade}</span>
                            </div>
                        </div>
                        <div style={styles.scoreDetails}>
                            <p style={{ margin: 0, fontSize: '0.9rem', color: '#475569', fontWeight: 500 }}>
                                {data.total_score} / {data.total_possible} points
                            </p>
                            <p style={{ margin: '4px 0 0', fontSize: '0.82rem', color: '#94a3b8' }}>
                                {data.total_questions_answered} of {data.question_count_target} questions answered
                            </p>
                        </div>
                    </div>
                    <div style={styles.heroRight}>
                        <div style={styles.statGrid}>
                            <div style={{ ...styles.statBox, borderColor: '#bbf7d0', background: '#f0fdf4' }}>
                                <Star size={16} style={{ color: '#22c55e' }} />
                                <span style={{ ...styles.statNum, color: '#22c55e' }}>{data.summary.excellent_count}</span>
                                <span style={styles.statLabel}>Excellent</span>
                            </div>
                            <div style={{ ...styles.statBox, borderColor: '#fde68a', background: '#fffbeb' }}>
                                <TrendingUp size={16} style={{ color: '#f59e0b' }} />
                                <span style={{ ...styles.statNum, color: '#f59e0b' }}>{data.summary.good_count}</span>
                                <span style={styles.statLabel}>Good</span>
                            </div>
                            <div style={{ ...styles.statBox, borderColor: '#fed7aa', background: '#fff7ed' }}>
                                <Target size={16} style={{ color: '#f97316' }} />
                                <span style={{ ...styles.statNum, color: '#f97316' }}>{data.summary.needs_improvement_count}</span>
                                <span style={styles.statLabel}>Improve</span>
                            </div>
                            <div style={{ ...styles.statBox, borderColor: '#c7d2fe', background: '#eef2ff' }}>
                                <AlertTriangle size={16} style={{ color: '#6366f1' }} />
                                <span style={{ ...styles.statNum, color: '#6366f1' }}>{data.summary.poor_count}</span>
                                <span style={styles.statLabel}>Poor</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Insights Row */}
                <div style={styles.insightsRow}>
                    {data.recommendations?.length > 0 && (
                        <div style={{ ...styles.insightCard, flex: '1.5' }}>
                            <div style={styles.insightHeader}>
                                <BookOpen size={18} style={{ color: '#6366f1' }} />
                                <h3 style={styles.insightTitle}>Study Recommendations</h3>
                            </div>
                            <div style={styles.insightBody}>
                                {data.recommendations.map((r, i) => (
                                    <div key={i} style={styles.recItem}>
                                        <Zap size={14} style={{ color: '#6366f1', flexShrink: 0, marginTop: '2px' }} />
                                        <span style={styles.recText}>{r}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flex: '1' }}>
                        {data.strengths.length > 0 && (
                            <div style={{ ...styles.insightCard, borderLeft: '4px solid #10b981' }}>
                                <h4 style={{ ...styles.insightMiniTitle, color: '#065f46' }}>
                                    <Trophy size={15} style={{ color: '#10b981' }} /> Strengths
                                </h4>
                                {data.strengths.map((s, i) => (
                                    <p key={i} style={styles.insightBullet}>✓ {s}</p>
                                ))}
                            </div>
                        )}
                        {data.weaknesses.length > 0 && (
                            <div style={{ ...styles.insightCard, borderLeft: '4px solid #f97316' }}>
                                <h4 style={{ ...styles.insightMiniTitle, color: '#9a3412' }}>
                                    <AlertTriangle size={15} style={{ color: '#f97316' }} /> Areas to Improve
                                </h4>
                                {data.weaknesses.map((w, i) => (
                                    <p key={i} style={styles.insightBullet}>→ {w}</p>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Performance Heatmap */}
                <div style={styles.heatmapCard}>
                    <h3 style={styles.heatmapTitle}>Performance Heatmap</h3>
                    <p style={styles.heatmapSubtitle}>Each tile represents a question — darker = higher score</p>
                    <div style={styles.heatmapGrid}>
                        {data.questions.map((q) => {
                            const intensity = q.score / 10;
                            const tileColor = q.score >= 8
                                ? `rgba(16, 185, 129, ${0.3 + intensity * 0.7})`
                                : q.score >= 6
                                ? `rgba(245, 158, 11, ${0.3 + intensity * 0.7})`
                                : q.score >= 4
                                ? `rgba(249, 115, 22, ${0.3 + intensity * 0.7})`
                                : `rgba(239, 68, 68, ${0.3 + intensity * 0.7})`;
                            return (
                                <div
                                    key={q.turn}
                                    style={{ ...styles.heatmapTile, background: tileColor }}
                                    title={`Q${q.turn}: ${q.score}/10`}
                                >
                                    <span style={styles.heatmapTileText}>Q{q.turn}</span>
                                    <span style={styles.heatmapTileScore}>{q.score}</span>
                                </div>
                            );
                        })}
                    </div>
                    <div style={styles.heatmapLegend}>
                        <span style={styles.heatmapLegendLabel}>Low</span>
                        <div style={styles.heatmapLegendBar}></div>
                        <span style={styles.heatmapLegendLabel}>High</span>
                    </div>
                </div>

                {/* Question-by-Question */}
                <div style={styles.qSection}>
                    <div style={styles.qSectionHeader}>
                        <h2 style={styles.qSectionTitle}>
                            <MessageSquare size={22} style={{ color: '#6366f1' }} />
                            Question-by-Question Breakdown
                        </h2>
                        <button onClick={toggleExpandAll} style={styles.expandAllBtn}>
                            {allExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                            {allExpanded ? 'Collapse All' : 'Expand All'}
                        </button>
                    </div>
                    <div style={styles.qList}>
                        {data.questions.map((q) => {
                            const isExpanded = allExpanded || expandedQ === q.turn;
                            const qColor = q.score >= 8 ? '#10b981' : q.score >= 6 ? '#f59e0b' : q.score >= 4 ? '#f97316' : '#ef4444';
                            const qBg = q.score >= 8 ? '#f0fdf4' : q.score >= 6 ? '#fffbeb' : q.score >= 4 ? '#fff7ed' : '#fef2f2';
                            const qBorder = q.score >= 8 ? '#bbf7d0' : q.score >= 6 ? '#fde68a' : q.score >= 4 ? '#fed7aa' : '#fecaca';

                            return (
                                <div
                                    key={q.turn}
                                    style={{ ...styles.qCard, background: qBg, borderColor: qBorder }}
                                    onClick={() => { if (!allExpanded) setExpandedQ(isExpanded ? null : q.turn); }}
                                >
                                    {/* Question header */}
                                    <div style={styles.qHeader}>
                                        <div style={styles.qLeft}>
                                            <div style={{ ...styles.qNumber, background: qColor }}>{q.turn}</div>
                                            <div style={{ flex: 1 }}>
                                                <p style={styles.qText}>{q.question}</p>
                                            </div>
                                        </div>
                                        <div style={{ ...styles.qScore, color: qColor }}>
                                            <span style={styles.qScoreNum}>{q.score}</span>
                                            <span style={styles.qScoreMax}>/10</span>
                                        </div>
                                    </div>

                                    {/* Expanded content */}
                                    {isExpanded && (
                                        <div style={styles.qExpanded}>
                                            <div style={styles.qAnswerBox}>
                                                <span style={styles.qAnswerLabel}>Your Answer:</span>
                                                <p style={styles.qAnswerText}>{q.answer || 'No answer provided'}</p>
                                            </div>
                                            <div style={styles.qFeedbackBox}>
                                                <span style={styles.qFeedbackLabel}>
                                                    <Zap size={13} style={{ color: '#6366f1' }} /> AI Feedback:
                                                </span>
                                                <p style={styles.qFeedbackText}>{q.feedback || q.score_reason || 'No feedback available'}</p>
                                            </div>
                                        </div>
                                    )}

                                    {/* Collapsed preview */}
                                    {!isExpanded && (
                                        <p style={styles.qPreview}>
                                            {q.answer?.substring(0, 120)}{q.answer?.length > 120 ? '...' : ''}
                                        </p>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Bottom action */}
                <div style={styles.bottomActions}>
                    <button onClick={() => navigate('/student/results?tab=interviews')} style={styles.actionBtn}>
                        ← Back to Results
                    </button>
                    <button onClick={() => navigate('/student/ai-interview')} style={styles.actionBtnPrimary}>
                        Practice Again
                    </button>
                </div>
            </div>

            {/* Scroll to top FAB */}
            {showScrollTop && (
                <button onClick={scrollToTop} style={styles.scrollTopBtn}>
                    <ArrowUpCircle size={24} />
                </button>
            )}
        </div>
    );
};

const styles = {
    wrapper: {
        minHeight: '100vh',
        background: '#f8fafc',
        position: 'relative',
        overflow: 'hidden',
    },
    meshBg: {
        position: 'fixed',
        inset: 0,
        background: 'radial-gradient(ellipse at 20% 0%, rgba(99,102,241,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 100%, rgba(168,85,247,0.06) 0%, transparent 50%), radial-gradient(ellipse at 50% 50%, rgba(236,72,153,0.04) 0%, transparent 70%)',
        pointerEvents: 'none',
        zIndex: 0,
    },
    content: {
        position: 'relative',
        zIndex: 1,
        maxWidth: '960px',
        margin: '0 auto',
        padding: '2rem 1.5rem 4rem',
    },
    header: {
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        marginBottom: '2rem',
    },
    backBtn: {
        background: 'white',
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        width: '42px',
        height: '42px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        color: '#6366f1',
        boxShadow: '0 2px 8px rgba(99,102,241,0.08)',
    },
    backBtnAlt: {
        marginTop: '1.5rem',
        padding: '0.75rem 2rem',
        background: '#6366f1',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '0.9rem',
        fontWeight: 600,
        cursor: 'pointer',
    },
    title: {
        margin: 0,
        fontSize: '1.6rem',
        fontWeight: 800,
        color: '#0f172a',
        letterSpacing: '-0.02em',
    },
    subtitle: {
        margin: '6px 0 0',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap',
    },
    badge: {
        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        color: 'white',
        padding: '3px 10px',
        borderRadius: '6px',
        fontSize: '0.75rem',
        fontWeight: 700,
    },
    badgeOutline: {
        background: 'white',
        color: '#6366f1',
        border: '1px solid #c7d2fe',
        padding: '3px 10px',
        borderRadius: '6px',
        fontSize: '0.75rem',
        fontWeight: 600,
    },
    heroCard: {
        background: 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
        borderRadius: '24px',
        padding: '2rem 2.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '2rem',
        marginBottom: '1.75rem',
        border: '1px solid rgba(99,102,241,0.1)',
        boxShadow: '0 4px 24px rgba(99,102,241,0.06)',
    },
    heroLeft: {
        display: 'flex',
        alignItems: 'center',
        gap: '1.5rem',
    },
    scoreRingContainer: {
        position: 'relative',
        width: '130px',
        height: '130px',
    },
    scoreRingText: {
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
    },
    scoreNumber: {
        fontSize: '2rem',
        fontWeight: 900,
        lineHeight: 1,
    },
    scoreGrade: {
        fontSize: '0.7rem',
        fontWeight: 700,
        color: '#64748b',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        marginTop: '4px',
    },
    scoreDetails: {
        display: 'flex',
        flexDirection: 'column',
    },
    miniChart: {
        display: 'flex',
        gap: '6px',
        marginTop: '12px',
        alignItems: 'flex-end',
        height: '40px',
    },
    miniChartCol: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '3px',
    },
    miniChartBarBg: {
        width: '16px',
        height: '32px',
        background: 'rgba(0,0,0,0.05)',
        borderRadius: '4px',
        position: 'relative',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'flex-end',
    },
    miniChartBar: {
        width: '100%',
        borderRadius: '4px',
        transition: 'height 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
        minHeight: '2px',
    },
    miniChartLabel: {
        fontSize: '0.55rem',
        color: '#94a3b8',
        fontWeight: 600,
    },
    heroRight: {},
    statGrid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '0.6rem',
    },
    statBox: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '2px',
        padding: '0.75rem 1.25rem',
        borderRadius: '14px',
        border: '1px solid',
    },
    statNum: {
        fontSize: '1.4rem',
        fontWeight: 800,
    },
    statLabel: {
        fontSize: '0.65rem',
        fontWeight: 600,
        color: '#64748b',
        textTransform: 'uppercase',
        letterSpacing: '0.03em',
    },
    insightsRow: {
        display: 'flex',
        gap: '1.25rem',
        marginBottom: '2rem',
        flexWrap: 'wrap',
    },
    insightCard: {
        background: 'white',
        borderRadius: '18px',
        padding: '1.5rem',
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 12px rgba(0,0,0,0.03)',
    },
    insightHeader: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginBottom: '1rem',
    },
    insightTitle: {
        margin: 0,
        fontSize: '1rem',
        fontWeight: 700,
        color: '#1e293b',
    },
    insightBody: {
        display: 'flex',
        flexDirection: 'column',
        gap: '0.6rem',
    },
    recItem: {
        display: 'flex',
        alignItems: 'flex-start',
        gap: '8px',
    },
    recText: {
        fontSize: '0.85rem',
        color: '#374151',
        lineHeight: '1.5',
    },
    insightMiniTitle: {
        margin: '0 0 0.5rem',
        fontSize: '0.85rem',
        fontWeight: 700,
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
    },
    insightBullet: {
        margin: '0.2rem 0',
        fontSize: '0.8rem',
        color: '#475569',
        lineHeight: '1.4',
        paddingLeft: '4px',
    },
    heatmapCard: {
        background: 'white',
        borderRadius: '20px',
        padding: '1.75rem 2rem',
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 12px rgba(0,0,0,0.03)',
        marginBottom: '2rem',
    },
    heatmapTitle: {
        margin: 0,
        fontSize: '1rem',
        fontWeight: 700,
        color: '#1e293b',
    },
    heatmapSubtitle: {
        margin: '4px 0 1.25rem',
        fontSize: '0.78rem',
        color: '#94a3b8',
    },
    heatmapGrid: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
    },
    heatmapTile: {
        width: '56px',
        height: '56px',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        transition: 'transform 0.2s, box-shadow 0.2s',
        cursor: 'default',
    },
    heatmapTileText: {
        fontSize: '0.65rem',
        fontWeight: 700,
        color: 'rgba(255,255,255,0.9)',
        textTransform: 'uppercase',
    },
    heatmapTileScore: {
        fontSize: '1.1rem',
        fontWeight: 900,
        color: 'white',
    },
    heatmapLegend: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginTop: '1rem',
        justifyContent: 'center',
    },
    heatmapLegendLabel: {
        fontSize: '0.7rem',
        color: '#94a3b8',
        fontWeight: 600,
    },
    heatmapLegendBar: {
        width: '120px',
        height: '8px',
        borderRadius: '4px',
        background: 'linear-gradient(to right, #ef4444, #f97316, #f59e0b, #22c55e, #10b981)',
    },
    qScore: {
        display: 'flex',
        alignItems: 'baseline',
        gap: '1px',
        flexShrink: 0,
    },
    qScoreNum: {
        fontSize: '1.5rem',
        fontWeight: 900,
    },
    qScoreMax: {
        fontSize: '0.8rem',
        fontWeight: 600,
        opacity: 0.7,
    },
    qSection: {
        marginBottom: '2rem',
    },
    qSectionHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.25rem',
        flexWrap: 'wrap',
        gap: '0.75rem',
    },
    qSectionTitle: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        fontSize: '1.2rem',
        fontWeight: 800,
        color: '#0f172a',
        margin: 0,
    },
    expandAllBtn: {
        display: 'flex',
        alignItems: 'center',
        gap: '5px',
        padding: '0.5rem 1rem',
        background: 'white',
        border: '1px solid #e2e8f0',
        borderRadius: '10px',
        fontSize: '0.8rem',
        fontWeight: 600,
        color: '#6366f1',
        cursor: 'pointer',
        transition: 'all 0.2s',
    },
    qList: {
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem',
    },
    qCard: {
        borderRadius: '16px',
        padding: '1.25rem 1.5rem',
        border: '1px solid',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        boxShadow: '0 2px 8px rgba(0,0,0,0.02)',
    },
    qHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        gap: '1rem',
    },
    qLeft: {
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        flex: 1,
    },
    qNumber: {
        width: '28px',
        height: '28px',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '0.75rem',
        fontWeight: 800,
        flexShrink: 0,
    },
    qText: {
        margin: 0,
        fontSize: '0.92rem',
        fontWeight: 600,
        color: '#1e293b',
        lineHeight: '1.4',
    },
    scoreBarContainer: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        marginTop: '8px',
    },
    scoreBarBg: {
        flex: 1,
        height: '6px',
        background: 'rgba(0,0,0,0.06)',
        borderRadius: '3px',
        overflow: 'hidden',
        maxWidth: '160px',
    },
    scoreBarFill: {
        height: '100%',
        borderRadius: '3px',
        transition: 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
    },
    scoreBarLabel: {
        fontSize: '0.8rem',
        fontWeight: 800,
    },
    qPreview: {
        margin: '0.6rem 0 0 40px',
        fontSize: '0.82rem',
        color: '#64748b',
        fontStyle: 'italic',
        lineHeight: '1.4',
    },
    qExpanded: {
        marginTop: '1rem',
        marginLeft: '40px',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
    },
    qAnswerBox: {
        background: 'rgba(255,255,255,0.7)',
        borderRadius: '12px',
        padding: '1rem',
        border: '1px solid rgba(0,0,0,0.05)',
    },
    qAnswerLabel: {
        fontSize: '0.7rem',
        fontWeight: 700,
        color: '#94a3b8',
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
    },
    qAnswerText: {
        margin: '0.4rem 0 0',
        fontSize: '0.85rem',
        color: '#334155',
        lineHeight: '1.6',
    },
    qFeedbackBox: {
        background: 'rgba(99,102,241,0.04)',
        borderRadius: '12px',
        padding: '1rem',
        border: '1px solid rgba(99,102,241,0.1)',
    },
    qFeedbackLabel: {
        fontSize: '0.7rem',
        fontWeight: 700,
        color: '#6366f1',
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
    },
    qFeedbackText: {
        margin: '0.4rem 0 0',
        fontSize: '0.85rem',
        color: '#4338ca',
        lineHeight: '1.6',
        fontWeight: 500,
    },
    bottomActions: {
        display: 'flex',
        justifyContent: 'center',
        gap: '1rem',
        paddingTop: '1rem',
    },
    actionBtn: {
        padding: '0.85rem 2rem',
        background: 'white',
        color: '#475569',
        border: '1px solid #e2e8f0',
        borderRadius: '12px',
        fontSize: '0.9rem',
        fontWeight: 600,
        cursor: 'pointer',
    },
    actionBtnPrimary: {
        padding: '0.85rem 2rem',
        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        fontSize: '0.9rem',
        fontWeight: 700,
        cursor: 'pointer',
        boxShadow: '0 4px 14px rgba(99,102,241,0.3)',
    },
    scrollTopBtn: {
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        width: '48px',
        height: '48px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        color: 'white',
        border: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        boxShadow: '0 4px 20px rgba(99,102,241,0.4)',
        zIndex: 100,
        transition: 'all 0.3s',
    },
    loadingSpinner: {
        width: '40px',
        height: '40px',
        border: '4px solid #e2e8f0',
        borderTopColor: '#6366f1',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        margin: '0 auto',
    },
};

export default StudentFeedback;
