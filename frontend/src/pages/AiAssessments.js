import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';
import { API_BASE_URL } from '../apiConfig';

const AiAssessments = () => {
    const navigate = useNavigate();
    const [assessments, setAssessments] = useState([]);
    const [filter, setFilter] = useState('ALL');
    const [currentPage, setCurrentPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Modal States
    const [showInviteModal, setShowInviteModal] = useState(false);
    const [selectedAssessment, setSelectedAssessment] = useState(null);
    const [inviteType, setInviteType] = useState('individual');
    const [inviteData, setInviteData] = useState({ name: '', email: '' });
    const [inviteFile, setInviteFile] = useState(null);
    const [inviting, setInviting] = useState(false);

    // Applicants Modal States
    const [showApplicantsModal, setShowApplicantsModal] = useState(false);
    const [applicantsLoading, setApplicantsLoading] = useState(false);
    const [applicantsData, setApplicantsData] = useState([]);
    const [selectedPoolName, setSelectedPoolName] = useState('');




    useEffect(() => {
        const fetchAssessments = async () => {
            try {
                // Using API_BASE_URL from config
                const response = await axios.get(`${API_BASE_URL}/ai/`);
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

    const getStatusInfo = (assessment) => {
        const now = new Date();
        const until = assessment.available_until ? new Date(assessment.available_until) : null;
        const invited = assessment.invited_count || 0;
        const completed = assessment.completed_count || 0;
        const started = assessment.candidate_count || 0;
        const isBulk = invited > 1;

        // 0. Explicit Generation State (from Pipeline)
        if (assessment.status === 'GENERATING') {
            return { type: 'SCHEDULED', label: 'AI Generating...', isGenerating: true, color: '#4318FF', bg: '#F4F7FE', icon: 'fa-spinner fa-spin' };
        }

        // 1. Completion-based (If fully completed, it stays Completed forever)
        if (completed > 0) {
            if (!isBulk || completed >= invited) {
                return { type: 'COMPLETED', label: 'Completed', isExpired: true, color: '#05CD99', bg: '#E6FBF5', icon: 'fa-check-circle' };
            }
        }

        // 2. Time-based Expiry (Absolute deadline - only triggers if NOT fully completed)
        if (until && now > until) {
            return { type: 'COMPLETED', label: 'Expired', isExpired: true, color: '#EE5D50', bg: '#FFF5F5', icon: 'fa-clock-rotate-left' };
        }

        // 3. Activity-based (Someone has started)
        if (started > 0) {
            const label = isBulk ? `Ongoing (${completed}/${invited})` : 'Ongoing';
            return { type: 'ONGOING', label, isExpired: true, color: '#4318FF', bg: '#F4F7FE', icon: 'fa-spinner fa-spin', isOngoing: true };
        }

        // 4. Capacity-based (Max candidates reached)
        if (invited >= (assessment.max_candidates_allowed || 1)) {
            // It is Full, but not completed yet. It should stay in SCHEDULED tab
            return { type: 'SCHEDULED', label: 'Full', isExpired: true, color: '#10b981', bg: '#E6FBF5', icon: 'fa-user-check' };
        }

        // 5. Default State (Fresh link)
        return { type: 'SCHEDULED', label: 'Share', isExpired: false, color: 'white', bg: '#10b981', icon: 'fa-link' };
    };

    const filteredAssessments = filter === 'ALL'
        ? assessments
        : assessments.filter(a => getStatusInfo(a).type === filter);

    // Pagination logic
    const indexOfLastItem = currentPage * 10;
    const indexOfFirstItem = indexOfLastItem - 10;
    const currentAssessments = filteredAssessments.slice(indexOfFirstItem, indexOfLastItem);
    const totalPages = Math.ceil(filteredAssessments.length / 10);

    const shareAssessment = (assessment) => {
        setSelectedAssessment(assessment);
        setShowInviteModal(true);
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
            const response = await axios.post(`${API_BASE_URL}/ai/invite/`, formData, {
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

    const fetchInvitedCandidates = async (assessment) => {
        setApplicantsLoading(true);
        setSelectedPoolName(assessment.batch_name || assessment.required_skills);
        setShowApplicantsModal(true);
        setSelectedAssessment(assessment); // Needed for resending invite
        try {
            const response = await axios.get(`${API_BASE_URL}/ai/${assessment.id}/invited-candidates/`);
            setApplicantsData(response.data.invited_candidates || []);
        } catch (err) {
            console.error('Error fetching invited candidates:', err);
        } finally {
            setApplicantsLoading(false);
        }
    };

    const handleResendInvite = async (email) => {
        if (!selectedAssessment) return;

        try {
            const response = await axios.post(`${API_BASE_URL}/ai/invite/resend/`, {
                assessment_id: selectedAssessment.id,
                email: email
            });
            alert(`✅ ${response.data.message}`);
        } catch (err) {
            console.error('Resend Invite Error:', err);
            const errMsg = err.response?.data?.error || 'Failed to resend invite.';
            alert(`❌ ${errMsg}`);
        }
    };

    const downloadSampleCSV = () => {
        const headers = "name,email\n";
        const sampleData = "John Doe,john@example.com\nJane Smith,jane@example.com";
        const csvContent = headers + sampleData;
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "bulk_invite_sample.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };




    return (
        <div className="dashboard-container" style={{ paddingTop: 0 }}>
            <div className="dashboard-main" style={{ paddingTop: '1rem' }}>
                <div>
                    <div style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                                onClick={() => { setFilter(status); setCurrentPage(1); }}
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
                    <div className="table-container" style={{ overflow: 'hidden' }}>
                        <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead>
                                <tr>
                                    {['Assessment Title', 'Type', 'Available From', 'Availability End', 'Applicants', 'Attempts', 'Actions'].map((head, i) => (
                                        <th key={i} style={{ padding: '1rem 1.2rem', background: '#F8F9FF', color: '#A3AED0', fontWeight: '700', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px', borderBottom: '2px solid #E2E8F0' }}>{head}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>Loading assessments...</td>
                                    </tr>
                                ) : error ? (
                                    <tr>
                                        <td colSpan="7" style={{ textAlign: 'center', color: '#EE5D50', padding: '2rem' }}>
                                            <i className="fa-solid fa-circle-exclamation" style={{ fontSize: '1.5rem', marginBottom: '0.5rem', display: 'block' }}></i>
                                            {error}
                                        </td>
                                    </tr>
                                ) : currentAssessments.length === 0 ? (
                                    <tr>
                                        <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: '#A3AED0' }}>No assessments found.</td>
                                    </tr>
                                ) : (
                                    currentAssessments.map(assessment => (
                                        <tr key={assessment.id} style={{ borderBottom: '1px solid #F1F4F9' }}>
                                            <td style={{ padding: '1rem 1.2rem', fontWeight: '500', color: '#1B254B', fontSize: '0.9rem' }}>
                                                <div className="row-info" style={{ display: 'flex', alignItems: 'center' }}>
                                                    <div className="avatar-mini" style={{
                                                        width: '28px', height: '28px', borderRadius: '50%', background: '#4318FF',
                                                        color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                        fontWeight: '700', fontSize: '0.7rem', marginRight: '0.8rem'
                                                    }}>AI</div>
                                                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                        <span style={{ fontWeight: '700' }}>
                                                            {assessment.batch_name || assessment.required_skills}
                                                        </span>
                                                        <span style={{ fontSize: '0.65rem', color: '#707EAE' }}>
                                                            {assessment.duration_minutes} mins | {assessment.job_description ? (assessment.job_description.substring(0, 30) + '...') : 'No Description'}
                                                        </span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td style={{ padding: '1rem 1.2rem', fontSize: '0.75rem' }}>
                                                <div style={{
                                                    display: 'inline-block',
                                                    padding: '0.35rem 0.8rem',
                                                    borderRadius: '6px',
                                                    fontWeight: '700',
                                                    textTransform: 'capitalize',
                                                    background: assessment.creation_type === 'automatic' ? '#E6FBF5' : '#F4F7FE',
                                                    color: assessment.creation_type === 'automatic' ? '#05CD99' : '#4318FF',
                                                    border: `1px solid ${assessment.creation_type === 'automatic' ? '#05CD99' : '#4318FF'}`
                                                }}>
                                                    {assessment.creation_type || 'manual'}
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
                                            <td style={{ padding: '1rem 1.2rem', color: '#1B254B', fontSize: '0.9rem' }}>
                                                <div
                                                    style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
                                                    onClick={() => fetchInvitedCandidates(assessment)}
                                                >
                                                    <span style={{ fontWeight: '700', color: '#4318FF', textDecoration: 'underline' }}>{assessment.invited_count || 0}</span>
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
                                                    {(() => {
                                                        const status = getStatusInfo(assessment);
                                                        // If it's Expired, Ongoing, or currently Generating, we hide the Share button and show the Badge
                                                        if (status.isExpired || status.isOngoing || status.isGenerating) {
                                                            return (
                                                                <div style={{
                                                                    background: status.bg,
                                                                    color: status.color,
                                                                    padding: '0.5rem 1rem',
                                                                    borderRadius: '8px',
                                                                    fontWeight: '700',
                                                                    fontSize: '0.85rem',
                                                                    display: 'flex',
                                                                    alignItems: 'center',
                                                                    gap: '0.4rem',
                                                                    border: `1px solid ${status.color}${status.isOngoing ? '20' : '40'}`
                                                                }}>
                                                                    <i className={`fa-solid ${status.icon}`}></i> {status.label}
                                                                </div>
                                                            );
                                                        }

                                                        // Otherwise, show the Share button
                                                        return (
                                                            <button
                                                                className="action-btn btn-share"
                                                                onClick={() => shareAssessment(assessment)}
                                                                style={{ background: '#10b981', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '8px', fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                                                            >
                                                                <i className="fa-solid fa-link"></i> Share
                                                            </button>
                                                        );
                                                    })()}


                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>

                        {/* Pagination Controls */}
                        {totalPages > 1 && (
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem', background: 'white', borderTop: '1px solid #e2e8f0' }}>
                                <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                                    Showing {indexOfFirstItem + 1} to {Math.min(indexOfLastItem, filteredAssessments.length)} of {filteredAssessments.length} entries
                                </span>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button
                                        onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                        disabled={currentPage === 1}
                                        style={{ padding: '0.5rem 1rem', background: currentPage === 1 ? '#f8fafc' : 'white', border: '1px solid #e2e8f0', borderRadius: '8px', cursor: currentPage === 1 ? 'not-allowed' : 'pointer', color: currentPage === 1 ? '#94a3b8' : '#475569', fontSize: '0.85rem', fontWeight: '500', transition: 'all 0.2s' }}
                                    >
                                        Previous
                                    </button>
                                    <div style={{ display: 'flex', alignItems: 'center', padding: '0 0.5rem', fontSize: '0.85rem', color: '#475569', fontWeight: '600' }}>
                                        Page {currentPage} of {totalPages}
                                    </div>
                                    <button
                                        onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                        disabled={currentPage === totalPages}
                                        style={{ padding: '0.5rem 1rem', background: currentPage === totalPages ? '#f8fafc' : 'white', border: '1px solid #e2e8f0', borderRadius: '8px', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer', color: currentPage === totalPages ? '#94a3b8' : '#475569', fontSize: '0.85rem', fontWeight: '500', transition: 'all 0.2s' }}
                                    >
                                        Next
                                    </button>
                                </div>
                            </div>
                        )}
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
                                            value={inviteData.name} onChange={(e) => {
                                                const val = e.target.value.replace(/[^a-zA-Z\s]/g, '');
                                                setInviteData({ ...inviteData, name: val });
                                            }}
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
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', marginTop: '0.4rem' }}>
                                        <p style={{ color: '#A3AED0', fontSize: '0.75rem', margin: 0 }}>Must contain 'name' and 'email' columns</p>
                                        <button
                                            type="button"
                                            onClick={(e) => { e.stopPropagation(); downloadSampleCSV(); }}
                                            style={{ background: 'none', border: 'none', color: '#4318FF', fontSize: '0.75rem', fontWeight: '700', cursor: 'pointer', textDecoration: 'underline', padding: 0 }}
                                        >
                                            Download Sample CSV
                                        </button>
                                    </div>
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

            {/* Applicants List Modal */}
            {showApplicantsModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
                    background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', zIndex: 1000, backdropFilter: 'blur(4px)'
                }}>
                    <div style={{
                        background: 'white', padding: '2rem', borderRadius: '24px',
                        width: '600px', maxWidth: '90%', maxHeight: '80vh', overflow: 'hidden',
                        display: 'flex', flexDirection: 'column',
                        position: 'relative', animation: 'slideUp 0.3s ease-out'
                    }}>
                        <button
                            onClick={() => setShowApplicantsModal(false)}
                            style={{ position: 'absolute', top: '1.5rem', right: '1.5rem', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#A3AED0' }}
                        ><i className="fa-solid fa-xmark"></i></button>

                        <h2 style={{ fontSize: '1.5rem', fontWeight: '800', color: '#1B254B', marginBottom: '0.2rem' }}>Invited Candidates</h2>
                        <p style={{ color: '#707EAE', fontSize: '0.9rem', marginBottom: '1.5rem' }}>{selectedPoolName}</p>

                        <div style={{ flex: 1, overflowY: 'auto', marginTop: '1rem' }}>
                            {applicantsLoading ? (
                                <div style={{ textAlign: 'center', padding: '2rem', color: '#A3AED0' }}>Loading applicants...</div>
                            ) : applicantsData.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '2rem', color: '#A3AED0' }}>No candidates invited yet.</div>
                            ) : (
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <thead>
                                        <tr style={{ textAlign: 'left', borderBottom: '2px solid #F4F7FE' }}>
                                            <th style={{ padding: '0.8rem', fontSize: '0.75rem', color: '#A3AED0', textTransform: 'uppercase' }}>Name</th>
                                            <th style={{ padding: '0.8rem', fontSize: '0.75rem', color: '#A3AED0', textTransform: 'uppercase' }}>Email</th>
                                            <th style={{ padding: '0.8rem', fontSize: '0.75rem', color: '#A3AED0', textTransform: 'uppercase' }}>Status</th>
                                            <th style={{ padding: '0.8rem', fontSize: '0.75rem', color: '#A3AED0', textTransform: 'uppercase', textAlign: 'center' }}>Action</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {applicantsData.map((cand, idx) => (
                                            <tr key={idx} style={{ borderBottom: '1px solid #F4F7FE' }}>
                                                <td style={{ padding: '0.8rem', fontSize: '0.9rem', color: '#1B254B', fontWeight: '600' }}>{cand.name}</td>
                                                <td style={{ padding: '0.8rem', fontSize: '0.85rem', color: '#707EAE' }}>{cand.email}</td>
                                                <td style={{ padding: '0.8rem' }}>
                                                    <span style={{
                                                        padding: '0.3rem 0.6rem', borderRadius: '8px', fontSize: '0.7rem', fontWeight: '700',
                                                        background: cand.status === 'completed' ? '#E6FBF5' : '#F4F7FE',
                                                        color: cand.status === 'completed' ? '#05CD99' : '#A3AED0'
                                                    }}>
                                                        {cand.status.charAt(0).toUpperCase() + cand.status.slice(1)}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '0.8rem', textAlign: 'center' }}>
                                                    {cand.status !== 'completed' && (
                                                        <button
                                                            onClick={() => handleResendInvite(cand.email)}
                                                            style={{
                                                                background: '#F4F7FE', color: '#4318FF', border: 'none', padding: '0.4rem 0.8rem',
                                                                borderRadius: '6px', fontSize: '0.75rem', fontWeight: '700', cursor: 'pointer',
                                                                display: 'inline-flex', alignItems: 'center', gap: '0.3rem'
                                                            }}
                                                            title="Resend Invitation Email"
                                                        >
                                                            <i className="fa-solid fa-paper-plane"></i> Resend
                                                        </button>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>

                        <button
                            onClick={() => setShowApplicantsModal(false)}
                            style={{
                                width: '100%', marginTop: '2.5rem', padding: '0.8rem', background: '#F4F7FE', color: '#4318FF',
                                border: 'none', borderRadius: '12px', fontWeight: '700', cursor: 'pointer'
                            }}
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

        </div>
    );
};


export default AiAssessments;