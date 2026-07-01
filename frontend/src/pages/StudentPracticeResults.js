import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Brain, Calendar, Clock, Award, FileText, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CreateAssessment.css'; // Reuse premium dark card styles

const StudentPracticeResults = () => {
    const navigate = useNavigate();
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchResults = async () => {
            setLoading(true);
            setError(null);
            try {
                const token = localStorage.getItem('token');
                const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
                const res = await axios.get(`${API_BASE_URL}/students/assessments/results/`, config);
                setResults(res.data);
            } catch (err) {
                console.error('Error fetching practice results:', err);
                setError(err.response?.data?.error || err.response?.data?.message || 'Failed to load practice results. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, []);

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

    return (
        <div className="create-assessment-page" style={{ paddingTop: '2rem', paddingBottom: '4rem', minHeight: '85vh' }}>
            <div className="assessment-container" style={{ maxWidth: '900px', margin: '0 auto' }}>
                
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '2.5rem' }}>
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
                        onMouseEnter={(e) => { e.currentTarget.style.background = '#F9FAFB'; e.currentTarget.style.borderColor = '#D1D5DB'; }}
                        onMouseLeave={(e) => { e.currentTarget.style.background = 'white'; e.currentTarget.style.borderColor = '#E2E8F0'; }}
                    >
                        <ArrowLeft size={18} />
                    </button>
                    <div>
                        <h1 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#111827', margin: 0, letterSpacing: '-0.02em' }}>
                            Practice <span style={{ color: '#4F46E5' }}>Results</span>
                        </h1>
                        <p style={{ color: '#6B7280', fontSize: '0.9rem', margin: '0.25rem 0 0 0' }}>
                            Review your performance and detailed scores for mock assessments.
                        </p>
                    </div>
                </div>

                {/* Main Results View */}
                {loading ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: 'white', borderRadius: '24px', border: '1px solid #E2E8F0', padding: '3rem' }}>
                        <Loader2 size={40} className="report-loading-spinner" style={{ color: '#4F46E5', animation: 'spin 1s linear infinite' }} />
                        <p style={{ marginTop: '1rem', color: '#6B7280', fontWeight: '500' }}>Fetching your results...</p>
                    </div>
                ) : error ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: 'white', borderRadius: '24px', border: '1px solid #E2E8F0', padding: '3rem', textAlign: 'center' }}>
                        <AlertCircle size={48} style={{ color: '#EF4444', marginBottom: '1rem' }} />
                        <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#111827', margin: 0 }}>Error Loading Results</h3>
                        <p style={{ color: '#6B7280', fontSize: '0.9rem', marginTop: '0.5rem', maxWidth: '400px' }}>{error}</p>
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
                            const isPassed = item.percentage >= 60; // default practice pass threshold
                            return (
                                <div 
                                    key={item.id} 
                                    className="glass-card" 
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

                                    {/* Middle/Right: Score, status, actions */}
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '2.5rem', flexWrap: 'wrap' }}>
                                        
                                        {/* Score stats */}
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: '0.7rem', color: '#9CA3AF', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>SCORE</div>
                                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '2px', justifyContent: 'flex-end', marginTop: '2px' }}>
                                                <span style={{ fontSize: '1.4rem', fontWeight: '800', color: '#111827' }}>{item.percentage}%</span>
                                            </div>
                                        </div>

                                        {/* Status Badge */}
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

                                        {/* Action Button */}
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
        </div>
    );
};

export default StudentPracticeResults;
