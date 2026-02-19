import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const AiAssessments = () => {
    const navigate = useNavigate();
    const [assessments, setAssessments] = useState([]);
    const [filter, setFilter] = useState('ALL');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAssessments = async () => {
            try {
                // Using localhost:8001 as per original html
                const response = await axios.get('http://localhost:8001/api/ai/');
                setAssessments(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching assessments:', err);
                setError('Error loading assessments. Is the backend running?');
                setLoading(false);
            }
        };

        fetchAssessments();
    }, []);

    const filteredAssessments = filter === 'ALL'
        ? assessments
        : assessments.filter(a => a.status === filter);

    const shareAssessment = (token) => {
        // Construct share URL - pointing to the React route we will create later or existing one
        const shareUrl = `${window.location.origin}/take-ai-assessment/${token}`;
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('✅ Assessment link copied to clipboard!');
        }).catch(() => {
            prompt('Copy this link:', shareUrl);
        });
    };

    const getStatusStyle = (status) => {
        switch (status) {
            case 'SCHEDULED': return { background: '#E6FBF5', color: '#05CD99' };
            case 'ONGOING': return { background: '#FFF8E6', color: '#FFA800' };
            case 'COMPLETED': return { background: '#EBF3FF', color: '#4318FF' };
            default: return { background: '#F4F7FE', color: '#A3AED0' };
        }
    };

    return (
        <div className="dashboard-container" style={{ paddingTop: '2rem' }}>
            <div className="card" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(10px)',
                borderRadius: '30px',
                padding: '3rem',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.3)'
            }}>
                <div className="header" style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                    <div>
                        <h1 style={{ fontFamily: "'Poppins', sans-serif", fontSize: '2.2rem', fontWeight: '700', margin: '0 0 0.5rem', color: '#1B254B' }}>Assessments</h1>
                        <p style={{ color: '#A3AED0', fontSize: '1.1rem', margin: '0' }}>Manage and share your AI-generated technical tests.</p>
                    </div>
                    <button
                        className="action-btn status-approved"
                        onClick={() => navigate('/create-assessment')}
                        style={{
                            padding: '0.8rem 1.5rem', display: 'flex', alignItems: 'center', gap: '0.8rem',
                            background: '#EBF3FF', color: '#4318FF', border: 'none', borderRadius: '10px',
                            fontWeight: '700', fontSize: '0.9rem', cursor: 'pointer', transition: 'all 0.2s'
                        }}
                    >
                        <i className="fa-solid fa-plus"></i> Create New
                    </button>
                </div>

                {/* Filter Tabs */}
                <div className="tabs" style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', background: '#F4F7FE', padding: '0.5rem', borderRadius: '16px', width: 'fit-content' }}>
                    {['ALL', 'SCHEDULED', 'ONGOING', 'COMPLETED'].map(status => (
                        <button
                            key={status}
                            onClick={() => setFilter(status)}
                            style={{
                                background: filter === status ? 'white' : 'transparent',
                                border: 'none', padding: '0.8rem 1.5rem', fontFamily: 'inherit', fontSize: '0.95rem',
                                fontWeight: '600', color: filter === status ? '#4318FF' : '#A3AED0', cursor: 'pointer',
                                transition: 'all 0.3s', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '0.6rem',
                                boxShadow: filter === status ? '0 4px 12px rgba(0, 0, 0, 0.05)' : 'none'
                            }}
                        >
                            <i className={`fa-solid ${status === 'ALL' ? 'fa-list' :
                                status === 'SCHEDULED' ? 'fa-calendar' :
                                    status === 'ONGOING' ? 'fa-spinner' : 'fa-check-circle'
                                }`}></i>
                            {status.charAt(0) + status.slice(1).toLowerCase()}
                        </button>
                    ))}
                </div>

                {/* Assessments Table */}
                <div className="table-container" style={{ background: 'white', borderRadius: '20px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0, 0, 0, 0.02)' }}>
                    <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead>
                            <tr>
                                {['Job Description', 'Skills', 'Status', 'Duration', 'Actions'].map((head, i) => (
                                    <th key={i} style={{ padding: '1.2rem 1.5rem', background: '#F8F9FF', color: '#A3AED0', fontWeight: '700', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{head}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="5" style={{ textAlign: 'center', padding: '3rem' }}>Loading assessments...</td>
                                </tr>
                            ) : error ? (
                                <tr>
                                    <td colSpan="5" style={{ textAlign: 'center', color: '#EE5D50', padding: '2rem' }}>
                                        <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '2rem', marginBottom: '1rem', display: 'block' }}></i>
                                        {error}
                                    </td>
                                </tr>
                            ) : filteredAssessments.length === 0 ? (
                                <tr>
                                    <td colSpan="5" style={{ textAlign: 'center', padding: '3rem', color: '#A3AED0' }}>No assessments found.</td>
                                </tr>
                            ) : (
                                filteredAssessments.map(assessment => (
                                    <tr key={assessment.id} style={{ borderBottom: '1px solid #F1F4F9' }}>
                                        <td style={{ padding: '1.2rem 1.5rem', fontWeight: '500', color: '#1B254B' }}>
                                            <div className="row-info" style={{ display: 'flex', alignItems: 'center' }}>
                                                <div className="avatar-mini" style={{
                                                    width: '32px', height: '32px', borderRadius: '50%', background: '#4318FF',
                                                    color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontWeight: '700', fontSize: '0.75rem', marginRight: '0.8rem'
                                                }}>AI</div>
                                                <span>{assessment.job_description ? (assessment.job_description.substring(0, 40) + '...') : 'Untitled Assessment'}</span>
                                            </div>
                                        </td>
                                        <td style={{ padding: '1.2rem 1.5rem', fontWeight: '500', color: '#1B254B' }}>{assessment.required_skills}</td>
                                        <td style={{ padding: '1.2rem 1.5rem', fontWeight: '500', color: '#1B254B' }}>
                                            <span style={{ padding: '0.5rem 1rem', borderRadius: '12px', fontSize: '0.85rem', fontWeight: '700', ...getStatusStyle(assessment.status) }}>
                                                {assessment.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: '1.2rem 1.5rem', fontWeight: '500', color: '#1B254B' }}>{assessment.duration_minutes}m</td>
                                        <td style={{ padding: '1.2rem 1.5rem', fontWeight: '500', color: '#1B254B' }}>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    className="action-btn"
                                                    onClick={() => navigate(`/assessments/${assessment.id}`)}
                                                    style={{ background: '#F4F7FE', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '10px', fontWeight: '700', fontSize: '0.9rem', color: '#4318FF', cursor: 'pointer' }}
                                                >View</button>
                                                <button
                                                    className="action-btn btn-share"
                                                    onClick={() => shareAssessment(assessment.share_token)}
                                                    style={{ background: '#10b981', color: 'white', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '10px', fontWeight: '700', fontSize: '0.9rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                                                >
                                                    <i className="fa-solid fa-link"></i> Share
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AiAssessments;
