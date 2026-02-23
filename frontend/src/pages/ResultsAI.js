import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

const ResultsAI = () => {
    const navigate = useNavigate();
    const [searchParams, setSearchParams] = useSearchParams();
    const initialTab = searchParams.get('tab') || 'resume';
    const [activeTab, setActiveTab] = useState(initialTab);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [resumeResults, setResumeResults] = useState([]);
    const [aiAssessments, setAiAssessments] = useState([]);
    const [aiInterviews, setAiInterviews] = useState([]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            // In a real scenario, these would be separate API calls. 
            // For now, we'll fetch what's available and adapt.

            // 1. Fetch AI Candidates (Interviews & Resume Matches)
            const candidatesResp = await axios.get(`${API_BASE_URL}/ai-candidates/`);
            const allCandidates = candidatesResp.data || [];

            // Filter candidates by status or other markers to separate "Resume Screening" from "AI Interview"
            // Assuming candidates with score > 0 or status 'Completed' have done interviews.
            setAiInterviews(allCandidates.filter(c => c.total_questions > 0));

            // Resume results are those that might have been matched but not necessarily interviewed yet
            // Or we might need a dedicated endpoint for resume matches if they are stored differently.
            setResumeResults(allCandidates);

            // 2. Fetch AI Assessments Submissions
            // This usually requires fetching all assessments then their submissions, 
            // but for a unified view we might need a global results endpoint.
            // Using the existing results endpoint which seems to aggregate some data.
            const resultsResp = await axios.get(`${API_BASE_URL}/results/`);
            setAiAssessments(resultsResp.data?.results || []);

        } catch (err) {
            console.error('Error fetching AI results:', err);
            setError('Failed to load results. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    useEffect(() => {
        const tab = searchParams.get('tab');
        if (tab && tab !== activeTab) {
            setActiveTab(tab);
        }
    }, [searchParams, activeTab]);

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        setSearchParams({ tab });
    };

    const getStatusStyle = (status) => {
        const s = status?.toLowerCase();
        if (s === 'selected' || s === 'completed' || s === 'resume passed')
            return { background: '#E6FBF5', color: '#05CD99' };
        if (s === 'rejected' || s === 'resume failed')
            return { background: '#FFF5F5', color: '#EE5D50' };
        return { background: '#F4F7FE', color: '#A3AED0' };
    };

    return (
        <div className="dashboard-container">
            <div className="dashboard-main" style={{ maxWidth: '1200px' }}>
                <header style={{ marginBottom: '2.5rem' }}>
                    <h1 style={{ fontSize: '2.4rem', fontWeight: '900', color: '#111827', margin: 0, letterSpacing: '-0.03em' }}>
                        AI <span style={{ color: '#4F46E5' }}>Results</span>
                    </h1>
                    <p style={{ color: '#6B7280', fontSize: '1rem', marginTop: '0.5rem' }}>
                        Centralized analytics for all AI-powered selection processes.
                    </p>
                </header>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', background: '#F4F7FE', padding: '0.4rem', borderRadius: '12px', width: 'fit-content' }}>
                    {[
                        { id: 'resume', label: 'Resume Screening', icon: 'fa-file-magnifying-glass' },
                        { id: 'assessment', label: 'AI Assessments', icon: 'fa-brain' },
                        { id: 'interview', label: 'AI Interviews', icon: 'fa-microphone-lines' }
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => handleTabChange(tab.id)}
                            style={{
                                background: activeTab === tab.id ? 'white' : 'transparent',
                                border: 'none', padding: '0.75rem 1.5rem', borderRadius: '10px',
                                fontWeight: '700', color: activeTab === tab.id ? '#4F46E5' : '#718096',
                                cursor: 'pointer', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '0.6rem',
                                boxShadow: activeTab === tab.id ? '0 4px 10px rgba(0, 0, 0, 0.05)' : 'none'
                            }}
                        >
                            <i className={`fa-solid ${tab.icon}`}></i>
                            {tab.label}
                        </button>
                    ))}
                </div>

                <div className="module-card" style={{ padding: '0', overflow: 'hidden', border: '1px solid #E5E7EB' }}>
                    {loading ? (
                        <div style={{ padding: '4rem', textAlign: 'center', color: '#6B7280' }}>
                            <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '2rem', marginBottom: '1rem' }}></i>
                            <p>Analyzing data...</p>
                        </div>
                    ) : error ? (
                        <div style={{ padding: '4rem', textAlign: 'center', color: '#EF4444' }}>
                            <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '2.5rem', marginBottom: '1rem' }}></i>
                            <p>{error}</p>
                            <button onClick={fetchData} style={{ marginTop: '1rem', padding: '0.5rem 1.5rem', background: '#4F46E5', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer' }}>Retry</button>
                        </div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ background: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>
                                    <th style={{ padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>Candidate</th>
                                    {activeTab === 'resume' && <th style={{ padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>Match %</th>}
                                    {activeTab === 'assessment' && <th style={{ padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>Assessment</th>}
                                    {activeTab === 'interview' && <th style={{ padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>AI Score</th>}
                                    <th style={{ padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>Date</th>
                                    <th style={{ padding: '1rem 1.5rem', textAlign: 'left', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>Status</th>
                                    <th style={{ padding: '1rem 1.5rem', textAlign: 'center', color: '#6B7280', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {activeTab === 'resume' && resumeResults.length > 0 ? resumeResults.map((r, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <div style={{ fontWeight: '700', color: '#111827' }}>{r.full_name}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.email}</div>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#EEF2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4F46E5', fontWeight: '800', fontSize: '0.8rem' }}>
                                                    {r.score || 0}%
                                                </div>
                                            </div>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem', color: '#6B7280', fontSize: '0.85rem' }}>
                                            {new Date(r.created_at).toLocaleDateString()}
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                {r.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem', textAlign: 'center' }}>
                                            <button className="action-btn" style={{ width: 'fit-content', margin: '0 auto' }}>View Detail</button>
                                        </td>
                                    </tr>
                                )) : activeTab === 'resume' && <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>No resume screening results found.</td></tr>}

                                {activeTab === 'assessment' && aiAssessments.length > 0 ? aiAssessments.map((r, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <div style={{ fontWeight: '700', color: '#111827' }}>{r.candidate?.name || 'Candidate'}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.candidate?.email}</div>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <div style={{ fontWeight: '600', color: '#374151', fontSize: '0.9rem' }}>{r.assessment?.display_name || r.assessment?.name}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>Score: {r.score}/{r.total}</div>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem', color: '#6B7280', fontSize: '0.85rem' }}>
                                            {new Date(r.submitted_at).toLocaleDateString()}
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                {r.status === 'selected' ? 'QUALIFIED' : 'NOT QUALIFIED'}
                                            </span>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem', textAlign: 'center' }}>
                                            <button
                                                className="action-btn"
                                                style={{ width: 'fit-content', margin: '0 auto' }}
                                                onClick={() => navigate(`/ai-assessments/${r.assessment?.id}?tab=submissions`)}
                                            >
                                                Details
                                            </button>
                                        </td>
                                    </tr>
                                )) : activeTab === 'assessment' && <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>No AI assessment attempts found.</td></tr>}

                                {activeTab === 'interview' && aiInterviews.length > 0 ? aiInterviews.map((r, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #F3F4F6' }}>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <div style={{ fontWeight: '700', color: '#111827' }}>{r.full_name}</div>
                                            <div style={{ fontSize: '0.8rem', color: '#6B7280' }}>{r.email}</div>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <div style={{ fontSize: '1.2rem', fontWeight: '900', color: '#4F46E5' }}>{r.score}</div>
                                            <div style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: '700' }}>{r.total_questions} Questions</div>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem', color: '#6B7280', fontSize: '0.85rem' }}>
                                            {r.completed_at ? new Date(r.completed_at).toLocaleDateString() : 'In Progress'}
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem' }}>
                                            <span style={{ padding: '0.3rem 0.75rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '800', ...getStatusStyle(r.status) }}>
                                                {r.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: '1rem 1.5rem', textAlign: 'center' }}>
                                            <button className="action-btn" style={{ width: 'fit-content', margin: '0 auto' }}>Analysis</button>
                                        </td>
                                    </tr>
                                )) : activeTab === 'interview' && <tr><td colSpan="5" style={{ padding: '3rem', textAlign: 'center', color: '#9CA3AF' }}>No AI interview sessions found.</td></tr>}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ResultsAI;
