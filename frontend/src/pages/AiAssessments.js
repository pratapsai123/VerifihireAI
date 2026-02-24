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

    // Modal States
    const [showInviteModal, setShowInviteModal] = useState(false);
    const [selectedAssessment, setSelectedAssessment] = useState(null);
    const [inviteType, setInviteType] = useState('individual');
    const [inviteData, setInviteData] = useState({ name: '', email: '' });
    const [inviteFile, setInviteFile] = useState(null);
    const [inviting, setInviting] = useState(false);

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

    const shareAssessment = (assessment) => {
        setSelectedAssessment(assessment);
        setShowInviteModal(true);
    };

    const deleteAssessment = async (id) => {
        if (!window.confirm('Are you sure you want to delete this assessment? This action cannot be undone.')) return;

        try {
            await axios.delete(`http://localhost:8001/api/ai/${id}/`);
            setAssessments(prev => prev.filter(a => a.id !== id));
        } catch (err) {
            console.error('Delete Error:', err);
            alert('Failed to delete assessment.');
        }
    };

    const handleInvite = async (e) => {
        e.preventDefault();
        if (!selectedAssessment) return;

        setInviting(true);
        const formData = new FormData();
        formData.append('assessment_id', selectedAssessment.id);
        formData.append('type', inviteType);

        if (inviteType === 'individual') {
            formData.append('name', inviteData.name);
            formData.append('email', inviteData.email);
        } else {
            if (!inviteFile) {
                alert('Please select a file');
                setInviting(false);
                return;
            }
            formData.append('file', inviteFile);
        }

        try {
            const response = await axios.post('http://localhost:8001/api/ai/invite/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert(`✅ ${response.data.message}`);
            setShowInviteModal(false);
            setInviteData({ name: '', email: '' });
            setInviteFile(null);
        } catch (err) {
            console.error('Invite Error:', err);
            const errMsg = err.response?.data?.error || 'Failed to send invites. Please check your connection.';
            alert(`❌ ${errMsg}`);
        } finally {
            setInviting(false);
        }
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
        <div className="dashboard-container" style={{ paddingTop: 0 }}>
            <div className="dashboard-main" style={{ paddingTop: '1rem' }}>
                <div style={{
                    background: 'white',
                    borderRadius: '24px',
                    padding: '2rem',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.03)',
                    border: '1px solid #f1f5f9'
                }}>
                    <div className="header" style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#111827', margin: 0, letterSpacing: '-0.025em' }}>
                                Assessments <span style={{ color: '#6366f1', fontWeight: '400' }}>Archive</span>
                            </h1>
                            <p style={{ color: '#6b7280', fontSize: '0.95rem', marginTop: '0.25rem' }}>Manage and share your AI-generated technical tests.</p>
                        </div>
                        <button
                            onClick={() => navigate('/create-assessment')}
                            style={{
                                padding: '0.6rem 1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
                                background: '#4318FF', color: 'white', border: 'none', borderRadius: '10px',
                                fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer', transition: 'all 0.2s',
                                boxShadow: '0 4px 12px rgba(67, 24, 255, 0.2)', width: 'fit-content'
                            }}
                        >
                            <i className="fa-solid fa-plus" style={{ fontSize: '0.8rem' }}></i>
                            <span>Create New</span>
                        </button>
                    </div>

                    {/* Filter Tabs */}
                    <div className="tabs" style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', background: '#F4F7FE', padding: '0.4rem', borderRadius: '12px', width: 'fit-content' }}>
                        {['ALL', 'SCHEDULED', 'ONGOING', 'COMPLETED'].map(status => (
                            <button
                                key={status}
                                onClick={() => setFilter(status)}
                                style={{
                                    background: filter === status ? 'white' : 'transparent',
                                    border: 'none', padding: '0.6rem 1.2rem', fontFamily: 'inherit', fontSize: '0.9rem',
                                    fontWeight: '600', color: filter === status ? '#4318FF' : '#A3AED0', cursor: 'pointer',
                                    transition: 'all 0.3s', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '0.5rem',
                                    boxShadow: filter === status ? '0 4px 10px rgba(0, 0, 0, 0.05)' : 'none'
                                }}
                            >
                                <i className={`fa-solid ${status === 'ALL' ? 'fa-list' :
                                    status === 'SCHEDULED' ? 'fa-calendar' :
                                        status === 'ONGOING' ? 'fa-spinner' : 'fa-check-circle'
                                    }`} style={{ fontSize: '0.9rem' }}></i>
                                {status.charAt(0) + status.slice(1).toLowerCase()}
                            </button>
                        ))}
                    </div>

                    {/* Assessments Table */}
                    <div className="table-container" style={{ background: 'white', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0, 0, 0, 0.02)', border: '1px solid #f1f5f9' }}>
                        <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead>
                                <tr>
                                    {['Assessment Title', 'Available From', 'Availability End', 'Attempts', 'Actions'].map((head, i) => (
                                        <th key={i} style={{ padding: '1rem 1.2rem', background: '#F8F9FF', color: '#A3AED0', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{head}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="5" style={{ textAlign: 'center', padding: '2rem' }}>Loading assessments...</td>
                                    </tr>
                                ) : error ? (
                                    <tr>
                                        <td colSpan="5" style={{ textAlign: 'center', color: '#EE5D50', padding: '2rem' }}>
                                            <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '1.5rem', marginBottom: '0.5rem', display: 'block' }}></i>
                                            {error}
                                        </td>
                                    </tr>
                                ) : filteredAssessments.length === 0 ? (
                                    <tr>
                                        <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: '#A3AED0' }}>No assessments found.</td>
                                    </tr>
                                ) : (
                                    filteredAssessments.map(assessment => (
                                        <tr key={assessment.id} style={{ borderBottom: '1px solid #F1F4F9' }}>
                                            <td style={{ padding: '1rem 1.2rem', fontWeight: '500', color: '#1B254B', fontSize: '0.9rem' }}>
                                                <div className="row-info" style={{ display: 'flex', alignItems: 'center' }}>
                                                    <div className="avatar-mini" style={{
                                                        width: '28px', height: '28px', borderRadius: '50%', background: '#4318FF',
                                                        color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                        fontWeight: '700', fontSize: '0.7rem', marginRight: '0.8rem'
                                                    }}>AI</div>
                                                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                        <span style={{ fontWeight: '700' }}>{assessment.job_description ? (assessment.job_description.substring(0, 30) + '...') : 'Untitled Assessment'}</span>
                                                        <span style={{ fontSize: '0.65rem', color: '#707EAE' }}>
                                                            {assessment.duration_minutes} mins | {assessment.required_skills}
                                                        </span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem 1.2rem', color: '#4318FF', fontSize: '0.8rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                                    <div style={{ fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                        <i className="fa-regular fa-clock" style={{ fontSize: '0.7rem' }}></i>
                                                        {new Date(assessment.available_from || assessment.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                    </div>
                                                    <div style={{ fontSize: '0.65rem', color: '#A3AED0', fontWeight: '500' }}>
                                                        {new Date(assessment.available_from || assessment.created_at).toLocaleDateString()}
                                                    </div>
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem 1.2rem', color: '#EE5D50', fontSize: '0.8rem' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                                    <div style={{ fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                        <i className="fa-regular fa-calendar-xmark" style={{ fontSize: '0.7rem' }}></i>
                                                        {assessment.available_until ? new Date(assessment.available_until).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'N/A'}
                                                    </div>
                                                    <div style={{ fontSize: '0.65rem', color: '#A3AED0', fontWeight: '500' }}>
                                                        {assessment.available_until ? new Date(assessment.available_until).toLocaleDateString() : 'No Limit'}
                                                    </div>
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem 1.2rem', fontWeight: '500', color: '#1B254B' }}>
                                                <div
                                                    onClick={() => navigate(`/ai-assessments/${assessment.id}?tab=submissions`)}
                                                    style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
                                                    title="View Submissions"
                                                >
                                                    <div style={{
                                                        minWidth: '35px', padding: '2px 8px', borderRadius: '15px',
                                                        background: assessment.candidate_count > 0 ? '#E6FBF5' : '#F4F7FE',
                                                        color: assessment.candidate_count > 0 ? '#05CD99' : '#A3AED0',
                                                        fontSize: '0.75rem', fontWeight: '800', textAlign: 'center'
                                                    }}>
                                                        {assessment.candidate_count}
                                                    </div>
                                                    <span style={{ fontSize: '0.75rem', color: '#4318FF', textDecoration: 'underline' }}>Attempts</span>
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem 1.2rem', fontWeight: '500', color: '#1B254B' }}>
                                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                    <button
                                                        className="action-btn"
                                                        onClick={() => navigate(`/ai-assessments/${assessment.id}?tab=questions`)}
                                                        style={{ background: '#F4F7FE', border: 'none', padding: '0.5rem 1rem', borderRadius: '8px', fontWeight: '700', fontSize: '0.85rem', color: '#4318FF', cursor: 'pointer' }}
                                                    >View</button>
                                                    <button
                                                        className="action-btn btn-share"
                                                        onClick={() => shareAssessment(assessment)}
                                                        style={{ background: '#10b981', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '8px', fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                                                    >
                                                        <i className="fa-solid fa-link"></i> Share
                                                    </button>
                                                    <button
                                                        className="action-btn"
                                                        onClick={() => deleteAssessment(assessment.id)}
                                                        style={{ background: '#FFF5F5', color: '#EE5D50', border: 'none', padding: '0.5rem 1rem', borderRadius: '8px', fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                                                    >
                                                        <i className="fa-solid fa-trash"></i>
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

            {/* Invite Modal */}
            {showInviteModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
                    background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(4px)'
                }}>
                    <div style={{
                        background: 'white', padding: '2rem', borderRadius: '24px',
                        width: '450px', boxShadow: '0 20px 50px rgba(0,0,0,0.2)',
                        position: 'relative', animation: 'slideUp 0.3s ease-out'
                    }}>
                        <button
                            onClick={() => setShowInviteModal(false)}
                            style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#A3AED0' }}
                        ><i className="fa-solid fa-xmark"></i></button>

                        <h2 style={{ fontSize: '1.5rem', fontWeight: '800', color: '#1B254B', marginBottom: '0.5rem' }}>Invite Candidates</h2>
                        <p style={{ color: '#707EAE', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                            {selectedAssessment?.job_description?.substring(0, 40)}...
                        </p>

                        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', background: '#F4F7FE', padding: '0.3rem', borderRadius: '12px' }}>
                            <button
                                onClick={() => setInviteType('individual')}
                                style={{
                                    flex: 1, padding: '0.6rem', border: 'none', borderRadius: '10px', fontSize: '0.85rem', fontWeight: '700',
                                    background: inviteType === 'individual' ? 'white' : 'transparent',
                                    color: inviteType === 'individual' ? '#4318FF' : '#A3AED0',
                                    boxShadow: inviteType === 'individual' ? '0 4px 10px rgba(0,0,0,0.05)' : 'none',
                                    cursor: 'pointer'
                                }}
                            >Individual</button>
                            <button
                                onClick={() => setInviteType('bulk')}
                                style={{
                                    flex: 1, padding: '0.6rem', border: 'none', borderRadius: '10px', fontSize: '0.85rem', fontWeight: '700',
                                    background: inviteType === 'bulk' ? 'white' : 'transparent',
                                    color: inviteType === 'bulk' ? '#4318FF' : '#A3AED0',
                                    boxShadow: inviteType === 'bulk' ? '0 4px 10px rgba(0,0,0,0.05)' : 'none',
                                    cursor: 'pointer'
                                }}
                            >Bulk (CSV/Excel)</button>
                        </div>

                        <form onSubmit={handleInvite}>
                            {inviteType === 'individual' ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                    <div>
                                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', color: '#1B254B', marginBottom: '0.4rem' }}>Candidate Name</label>
                                        <input
                                            type="text" required placeholder="Enter full name"
                                            value={inviteData.name} onChange={(e) => setInviteData({ ...inviteData, name: e.target.value })}
                                            style={{ width: '100%', padding: '0.8rem 1rem', borderRadius: '12px', border: '1px solid #E0E5F2', fontSize: '0.9rem', outline: 'none' }}
                                        />
                                    </div>
                                    <div>
                                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: '700', color: '#1B254B', marginBottom: '0.4rem' }}>Email Address</label>
                                        <input
                                            type="email" required placeholder="Enter email address"
                                            value={inviteData.email} onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
                                            style={{ width: '100%', padding: '0.8rem 1rem', borderRadius: '12px', border: '1px solid #E0E5F2', fontSize: '0.9rem', outline: 'none' }}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <div style={{
                                    border: '2px dashed #E0E5F2', borderRadius: '16px', padding: '2rem', textAlign: 'center',
                                    background: '#F8F9FF', cursor: 'pointer'
                                }} onClick={() => document.getElementById('bulk-file').click()}>
                                    <i className="fa-solid fa-cloud-arrow-up" style={{ fontSize: '2rem', color: '#4318FF', marginBottom: '1rem' }}></i>
                                    <p style={{ fontWeight: '700', color: '#1B254B', fontSize: '0.9rem', margin: 0 }}>
                                        {inviteFile ? inviteFile.name : 'Click to upload CSV or Excel'}
                                    </p>
                                    <p style={{ color: '#A3AED0', fontSize: '0.75rem', marginTop: '0.4rem' }}>Must contain 'name' and 'email' columns</p>
                                    <input
                                        type="file" id="bulk-file" hidden accept=".csv,.xlsx,.xls"
                                        onChange={(e) => setInviteFile(e.target.files[0])}
                                    />
                                </div>
                            )}

                            <button
                                type="submit" disabled={inviting}
                                style={{
                                    width: '100%', marginTop: '2rem', padding: '1rem', background: '#4318FF', color: 'white',
                                    border: 'none', borderRadius: '16px', fontWeight: '700', cursor: inviting ? 'not-allowed' : 'pointer',
                                    boxShadow: '0 10px 20px rgba(67, 24, 255, 0.2)', opacity: inviting ? 0.7 : 1
                                }}
                            >
                                {inviting ? 'Sending Invites...' : 'Send Invitations'}
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AiAssessments;
