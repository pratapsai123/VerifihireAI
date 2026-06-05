import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';

const cleanObjName = (repr) => {
    if (!repr) return '';
    let name = repr.replace(/^Submission for /i, '');
    name = name.replace(/\bNone\b/gi, '').replace(/\s+/g, ' ').trim();
    return name;
};

const getImageUrl = (url) => {
    if (!url) return '';
    if (url.startsWith('data:') || url.startsWith('http')) return url;
    return `${API_BASE_URL.replace('/api', '')}${url}`;
};

const cleanName = (name) => {
    return name ? name.replace(/\bNone\b/gi, '').replace(/\s+/g, ' ').trim() : '';
};

const parseHistory = (req) => {
    let history = [];
    let rawReason = req.reason || '';
    
    const restoredRegex = /\[RESTORED on (.*?)\]/g;
    let match;
    let originalReason = rawReason;
    while ((match = restoredRegex.exec(rawReason)) !== null) {
        history.push({ 
            action: 'Restored', 
            date: new Date(match[1]), 
            desc: `Restored` 
        });
        originalReason = originalReason.replace(match[0], '');
    }
    originalReason = originalReason.replace(/Admin Restored \| /g, '').trim();
    
    // Original request
    history.push({ 
        action: 'Request', 
        date: new Date(req.created_at), 
        desc: `Requested: ${originalReason || 'No reason specified'}` 
    });
    
    if ((req.status === 'approved' || req.status === 'restored') && req.actioned_at) {
        history.push({ 
            action: 'Approved', 
            date: new Date(req.actioned_at), 
            desc: `Approved by ${cleanName(req.approver_name) || 'Unknown'}` 
        });
    } else if (req.status === 'rejected' && req.actioned_at) {
        history.push({ 
            action: 'Rejected', 
            date: new Date(req.actioned_at), 
            desc: `Rejected: ${req.rejection_reason || 'No reason'}` 
        });
    }

    history.sort((a, b) => a.date - b.date);
    return history;
};

const Settings = () => {
    const [user, setUser] = useState(null);
    const [settings, setSettings] = useState({ require_delete_permission: true });
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('requests'); // 'requests' or 'config'
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [filterDate, setFilterDate] = useState('');

    // Qualification Requests state
    const [qualRequests, setQualRequests] = useState([]);
    const [qualLoading, setQualLoading] = useState(false);
    const [qualReviewPopup, setQualReviewPopup] = useState(null); // { req }
    const [qualRejectReason, setQualRejectReason] = useState('');
    const [qualRejectMode, setQualRejectMode] = useState(false);
    const [downloadingQualId, setDownloadingQualId] = useState(null);

    // Face Approvals state
    const [faceRequests, setFaceRequests] = useState([]);
    const [faceLoading, setFaceLoading] = useState(false);
    const [faceReviewPopup, setFaceReviewPopup] = useState(null); // { req }
    const [faceAdminNote, setFaceAdminNote] = useState('');
    const [faceApprovedChoice, setFaceApprovedChoice] = useState(true);
    const [integrityApprovedChoice, setIntegrityApprovedChoice] = useState(true);
    const [faceActionSubmitting, setFaceActionSubmitting] = useState(false);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }

        // Fetch fresh profile from the server to correct any stale user roles (like Rishidar made Admin)
        const fetchFreshProfile = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/profile/`);
                if (res.data) {
                    setUser(res.data);
                    localStorage.setItem('user', JSON.stringify(res.data));
                }
            } catch (err) {
                console.error("Failed to fetch fresh user profile:", err);
            }
        };
        fetchFreshProfile();

        loadSettings();
        loadRequests();
        loadQualRequests();
        loadFaceRequests();
    }, []);

    const loadSettings = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/settings/deletion/`);
            setSettings(res.data);
        } catch (err) {
            console.error("Failed to load settings");
        }
    };

    const loadRequests = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/workflow/deletion-requests/`);
            setRequests(res.data);
        } catch (err) {
            setError('Failed to load deletion requests.');
        } finally {
            setLoading(false);
        }
    };

    const loadQualRequests = async () => {
        setQualLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/workflow/qualification-requests/`);
            setQualRequests(res.data);
        } catch (err) {
            console.error('Failed to load qualification requests.');
        } finally {
            setQualLoading(false);
        }
    };

    const loadFaceRequests = async () => {
        setFaceLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/workflow/face-requests/`);
            setFaceRequests(res.data);
        } catch (err) {
            console.error('Failed to load face update requests.');
        } finally {
            setFaceLoading(false);
        }
    };

    const handleFaceAction = async (reqId, faceApproved, integrityApproved, adminNote = '') => {
        setFaceActionSubmitting(true);
        try {
            await axios.post(`${API_BASE_URL}/workflow/face-requests/${reqId}/action/`, {
                face_approved: faceApproved,
                integrity_approved: integrityApproved,
                admin_note: adminNote
            });
            setMessage(`Review request submitted successfully.`);
            setFaceReviewPopup(null);
            setFaceAdminNote('');
            loadFaceRequests();
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setError(err.response?.data?.error || `Failed to submit review request.`);
            setTimeout(() => setError(''), 4000);
        } finally {
            setFaceActionSubmitting(false);
        }
    };

    const handleQualAction = async (reqId, action, reason = '') => {
        try {
            await axios.post(`${API_BASE_URL}/workflow/qualification-requests/${reqId}/action/`, { action, reason });
            setMessage(`Request ${action}ed successfully.`);
            setQualReviewPopup(null);
            setQualRejectMode(false);
            setQualRejectReason('');
            loadQualRequests();
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setError(err.response?.data?.error || `Failed to ${action} request.`);
        }
    };

    const handleDownloadQualReport = async (req) => {
        if (!req.report_url) return;
        setDownloadingQualId(req.id);
        try {
            const resp = await axios.get(`${API_BASE_URL}${req.report_url}`, { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([resp.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Report_${req.candidate_name || req.id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            setError('Failed to download report.');
        } finally {
            setDownloadingQualId(null);
        }
    };

    const handleToggleSettings = async () => {
        try {
            const newVal = !settings.require_delete_permission;
            await axios.post(`${API_BASE_URL}/settings/deletion/`, {
                require_delete_permission: newVal
            });
            setSettings({ ...settings, require_delete_permission: newVal });
            setMessage("Settings updated successfully.");
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setError("Failed to update settings.");
        }
    };

    const handleAction = async (requestId, action, reason = '') => {
        try {
            await axios.post(`${API_BASE_URL}/workflow/deletion-requests/${requestId}/action/`, {
                action,
                reason
            });
            setMessage(`Request ${action}ed successfully.`);
            loadRequests();
            setTimeout(() => setMessage(''), 3000);
        } catch (err) {
            setError(err.response?.data?.error || `Failed to ${action} request.`);
        }
    };

    const isCompanyAdmin = user?.role === 'company_admin' || user?.role === 'application_admin';

    const [rejectModal, setRejectModal] = useState(null); // { requestId }

    const handleRestore = async (requestId) => {
        if (!window.confirm('Are you sure you want to restore this item? It will reappear in the application.')) return;
        try {
            const res = await axios.post(`${API_BASE_URL}/workflow/deletion-requests/${requestId}/restore/`);
            setMessage(res.data.message || 'Item restored successfully.');
            loadRequests();
            setTimeout(() => setMessage(''), 4000);
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to restore item.');
        }
    };

    const filteredRequests = requests.filter(req => {
        const matchesStatus = filterStatus === 'all' || req.status === filterStatus;
        const searchLower = searchTerm.toLowerCase();
        
        const candidateName = cleanObjName(req.object_repr);
        const reqName = cleanName(req.requester_name);
        
        const matchesSearch = 
            (candidateName.toLowerCase().includes(searchLower)) ||
            (reqName.toLowerCase().includes(searchLower));

        let matchesDate = true;
        if (filterDate) {
            const reqDate = new Date(req.created_at).toISOString().split('T')[0];
            matchesDate = reqDate === filterDate;
        }

        return matchesStatus && matchesSearch && matchesDate;
    });

    const filteredFaceRequests = faceRequests.filter(req => {
        const matchesStatus = filterStatus === 'all' || req.status === filterStatus;
        const searchLower = searchTerm.toLowerCase();
        
        const candidateName = req.candidate_name || '';
        const hrName = req.hr_name || '';
        
        const matchesSearch = 
            candidateName.toLowerCase().includes(searchLower) ||
            hrName.toLowerCase().includes(searchLower);

        let matchesDate = true;
        if (filterDate) {
            const reqDate = new Date(req.requested_at).toISOString().split('T')[0];
            matchesDate = reqDate === filterDate;
        }

        return matchesStatus && matchesSearch && matchesDate;
    });

    return (
        <div className="dashboard-container">
            <Header />
            <div className="page-container" style={{ maxWidth: '1100px', margin: '5rem auto', padding: '0 1rem' }}>
                <h1 style={{ marginBottom: '1.5rem', color: '#1d2686' }}>Settings & Workflows</h1>

                {message && <div style={{ padding: '12px', backgroundColor: '#d1fae5', color: '#065f46', borderRadius: '8px', marginBottom: '1rem', fontWeight: '600' }}>{message}</div>}
                {error && <div style={{ padding: '12px', backgroundColor: '#fee2e2', color: '#991b1b', borderRadius: '8px', marginBottom: '1rem', fontWeight: '600' }}>{error}</div>}

                <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid #e5e7eb' }}>
                    <button
                        onClick={() => setTab('requests')}
                        style={{
                            padding: '10px 20px', border: 'none', background: 'none',
                            borderBottom: tab === 'requests' ? '3px solid #1d2686' : 'none',
                            color: tab === 'requests' ? '#1d2686' : '#6b7280', fontWeight: 'bold', cursor: 'pointer'
                        }}
                    >
                        🗑️ Deletion Requests
                    </button>
                    <button
                        onClick={() => { setTab('qualification'); loadQualRequests(); }}
                        style={{
                            padding: '10px 20px', border: 'none', background: 'none',
                            borderBottom: tab === 'qualification' ? '3px solid #059669' : 'none',
                            color: tab === 'qualification' ? '#059669' : '#6b7280', fontWeight: 'bold', cursor: 'pointer'
                        }}
                    >
                        🏅 Qualification Requests
                        {qualRequests.filter(r => r.status === 'pending').length > 0 && (
                            <span style={{ marginLeft: '6px', background: '#dc2626', color: '#fff', borderRadius: '999px', padding: '1px 7px', fontSize: '0.72rem', fontWeight: '800' }}>
                                {qualRequests.filter(r => r.status === 'pending').length}
                            </span>
                        )}
                    </button>
                    <button
                        onClick={() => { setTab('face_approvals'); loadFaceRequests(); }}
                        style={{
                            padding: '10px 20px', border: 'none', background: 'none',
                            borderBottom: tab === 'face_approvals' ? '3px solid #3b82f6' : 'none',
                            color: tab === 'face_approvals' ? '#3b82f6' : '#6b7280', fontWeight: 'bold', cursor: 'pointer'
                        }}
                    >
                        👤 Face Approvals
                        {faceRequests.filter(r => r.status === 'pending').length > 0 && (
                            <span style={{ marginLeft: '6px', background: '#dc2626', color: '#fff', borderRadius: '999px', padding: '1px 7px', fontSize: '0.72rem', fontWeight: '800' }}>
                                {faceRequests.filter(r => r.status === 'pending').length}
                            </span>
                        )}
                    </button>
                    {isCompanyAdmin && (
                        <button
                            onClick={() => setTab('config')}
                            style={{
                                padding: '10px 20px', border: 'none', background: 'none',
                                borderBottom: tab === 'config' ? '3px solid #1d2686' : 'none',
                                color: tab === 'config' ? '#1d2686' : '#6b7280', fontWeight: 'bold', cursor: 'pointer'
                            }}
                        >
                            ⚙️ Global Configuration
                        </button>
                    )}
                </div>

                {tab === 'config' && isCompanyAdmin && (
                    <div style={{ background: '#fff', padding: '1.5rem', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                        <h3 style={{ marginBottom: '1rem' }}>Data Integrity Workflow</h3>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                            <label className="switch">
                                <input type="checkbox" checked={settings.require_delete_permission} onChange={handleToggleSettings} />
                                <span className="slider round"></span>
                            </label>
                            <div>
                                <strong>Require Multi-level Deletion Approval</strong>
                                <p style={{ margin: 0, fontSize: '0.9rem', color: '#6b7280' }}>
                                    When enabled, HR/HRM users cannot delete records directly. They must request permission from their hierarchy.
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {tab === 'requests' && (
                    <div style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                <span style={{ fontWeight: '600', color: '#374151' }}>Filter:</span>
                                <select
                                    value={filterStatus}
                                    onChange={e => setFilterStatus(e.target.value)}
                                    style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1d5db', outline: 'none', background: '#f9fafb', fontSize: '0.9rem' }}
                                >
                                    <option value="all">All Requests</option>
                                    <option value="pending">⏳ Pending</option>
                                    <option value="approved">🗑️ Deleted</option>
                                    <option value="rejected">❌ Rejected</option>
                                <option value="restored">↩️ Restored</option>
</select>
                            </div>
                            <div style={{ flex: '1', minWidth: '200px', maxWidth: '400px' }}>
                                <input 
                                    type="text" 
                                    placeholder="Search by name, email, requester..." 
                                    value={searchTerm}
                                    onChange={e => setSearchTerm(e.target.value)}
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1d5db', outline: 'none', fontSize: '0.9rem' }}
                                />
                            </div>
                            <div style={{ flex: '1', minWidth: '150px', maxWidth: '200px' }}>
                                <input 
                                    type="date" 
                                    value={filterDate}
                                    onChange={e => setFilterDate(e.target.value)}
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1d5db', outline: 'none', fontSize: '0.9rem' }}
                                />
                            </div>
                        </div>
                        
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                                <thead style={{ background: '#f3f4f6', color: '#4b5563', textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>
                                    <tr>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb', minWidth: '350px' }}>Candidate Details & Timeline</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Requested By</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Status</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading ? (
                                        <tr>
                                            <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>Loading...</td>
                                        </tr>
                                    ) : filteredRequests.length === 0 ? (
                                        <tr>
                                            <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                                               No requests found matching your filters.
                                            </td>
                                        </tr>
                                    ) : (
                                        filteredRequests.map(req => (
                                            <tr key={req.id} style={{ borderBottom: '1px solid #e5e7eb', background: req.status === 'pending' ? '#fffbeb' : req.status === 'approved' ? '#f8faff' : '#fff8f8' }}>
                                                <td style={{ padding: '12px 16px' }}>
                                                    <div style={{ fontWeight: '700', color: '#111827', marginBottom: '8px', fontSize: '1rem' }}>
                                                        <i className="fa-regular fa-user" style={{ marginRight: '6px', color: '#6b7280' }}></i>
                                                        {cleanObjName(req.object_repr) || `ID ${req.object_id}`}
                                                    </div>
                                                    <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#374151' }}>
                                                        <div style={{ fontWeight: '600', color: '#6b7280', marginBottom: '2px' }}>Timeline:</div>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                                                            {parseHistory(req).map((evt, idx) => (
                                                                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '2px 0' }}>
                                                                    <span style={{ fontWeight: '500', color: evt.action === 'Request' ? '#3b82f6' : evt.action === 'Approved' ? '#10b981' : evt.action === 'Rejected' ? '#ef4444' : '#f59e0b' }}>
                                                                        • {evt.desc}
                                                                    </span>
                                                                    <span style={{ color: '#9ca3af', whiteSpace: 'nowrap' }}>
                                                                        {evt.date.toLocaleDateString()} {evt.date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                                    </span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                    <div style={{ color: '#111827', fontWeight: '500' }}>{cleanName(req.requester_name)}</div>
                                                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{req.requester_role}</div>
                                                </td>
                                                <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                    <span style={{
                                                        display: 'inline-flex', alignItems: 'center', padding: '4px 10px', borderRadius: '999px', fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase',
                                                        background: req.status === 'pending' ? '#fef3c7' : req.status === 'approved' ? '#e0e7ff' :  req.status === 'rejected' ? '#fee2e2' : '#ede9fe',
                                                        color: req.status === 'pending' ? '#92400e' : req.status === 'approved' ? '#3730a3' :  req.status === 'rejected' ? '#dc2626' : '#5b21b6'
                                                    }}>
                                                        {req.status === 'pending' ? '⏳ Pending' : req.status === 'approved' ? '🗑 Deleted' : req.status === 'rejected' ? '✖ Rejected' : req.status === 'restored' ? '↩ Restored' : req.status.toUpperCase()}
                                                    </span>
                                                    {req.status === 'rejected' && req.rejection_reason && (
                                                        <div style={{ fontSize: '0.7rem', color: '#991b1b', marginTop: '4px', background: '#fef2f2', padding: '4px 8px', borderRadius: '4px' }}>{req.rejection_reason}</div>
                                                    )}
                                                    {req.status !== 'pending' && req.approver_name && (
                                                        <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '4px' }}>By: {cleanName(req.approver_name)}</div>
                                                    )}
                                                </td>
                                                <td style={{ padding: '12px 16px' }}>
                                                    {req.status === 'pending' ? (
                                                        (isCompanyAdmin || req.approver_email === user?.email) ? (
                                                            <div style={{ display: 'flex', gap: '0.5rem', flexDirection: 'row' }}>
                                                                <button onClick={() => handleAction(req.id, 'approve')} style={{ padding: '6px 12px', background: '#d1fae5', color: '#065f46', border: '1px solid #6ee7b750', borderRadius: '6px', cursor: 'pointer', fontWeight: '700', fontSize: '0.75rem', flex: 1 }}>✅ Approve</button>
                                                                <button onClick={() => setRejectModal({ requestId: req.id })} style={{ padding: '6px 12px', background: '#fee2e2', color: '#991b1b', border: '1px solid #fca5a550', borderRadius: '6px', cursor: 'pointer', fontWeight: '700', fontSize: '0.75rem', flex: 1 }}>❌ Reject</button>
                                                            </div>
                                                        ) : (
                                                            <span style={{ fontSize: '0.75rem', color: '#9ca3af', fontStyle: 'italic' }}>Waiting for {cleanName(req.approver_name)}</span>
                                                        )
                                                    ) : (
                                                        req.status === 'approved' && isCompanyAdmin ? (
                                                            <button onClick={() => handleRestore(req.id)} style={{ padding: '6px 12px', background: '#ede9fe', color: '#5b21b6', border: '1px solid #c4b5fd', borderRadius: '6px', cursor: 'pointer', fontWeight: '700', fontSize: '0.75rem', width: '100%' }}>↩ Restore</button>
                                                        ) : (
                                                            <span style={{ color: '#9ca3af' }}>-</span>
                                                        )
                                                    )}
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* ── Qualification Requests Tab ── */}
                {tab === 'qualification' && (
                    <div style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                            <h3 style={{ margin: 0, color: '#059669', fontWeight: '800' }}>🏅 Qualification Requests</h3>
                            <button onClick={loadQualRequests} style={{ padding: '6px 14px', border: '1px solid #d1d5db', borderRadius: '8px', background: '#f9fafb', cursor: 'pointer', fontWeight: '600', fontSize: '0.85rem' }}>🔄 Refresh</button>
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem', textAlign: 'left' }}>
                                <thead style={{ background: '#f3f4f6', color: '#4b5563', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: '0.05em' }}>
                                    <tr>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Candidate</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Requested Change</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Requested By</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Reason</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Status</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {qualLoading ? (
                                        <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>Loading...</td></tr>
                                    ) : qualRequests.length === 0 ? (
                                        <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>No qualification requests found.</td></tr>
                                    ) : qualRequests.map(req => (
                                        <tr key={req.id} style={{ borderBottom: '1px solid #e5e7eb', background: req.status === 'pending' ? '#f0fdf4' : '#fff' }}>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <div style={{ fontWeight: '700', color: '#111827' }}>{req.candidate_name || '—'}</div>
                                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{req.candidate_email}</div>
                                                <div style={{ fontSize: '0.7rem', color: '#9ca3af', marginTop: '2px' }}>{new Date(req.created_at).toLocaleDateString()}</div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <span style={{ fontWeight: '700', padding: '3px 10px', borderRadius: '999px', fontSize: '0.78rem', background: req.requested_result === 'selected' ? '#d1fae5' : '#fee2e2', color: req.requested_result === 'selected' ? '#065f46' : '#991b1b' }}>
                                                    {req.requested_result === 'selected' ? '✅ Qualified' : '❌ Not Qualified'}
                                                </span>
                                                <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '4px' }}>{req.content_type === 'ai_assessment' ? 'AI Assessment' : 'Standard Assessment'}</div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <div style={{ fontWeight: '600' }}>{req.requester_name}</div>
                                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{req.requester_role}</div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top', maxWidth: '200px' }}>
                                                <div style={{ fontSize: '0.82rem', color: '#374151', background: '#f9fafb', padding: '6px 10px', borderRadius: '6px', border: '1px solid #e5e7eb', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                                                    {req.reason}
                                                </div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <span style={{ display: 'inline-flex', alignItems: 'center', padding: '3px 10px', borderRadius: '999px', fontSize: '0.75rem', fontWeight: '700', background: req.status === 'pending' ? '#fef3c7' : req.status === 'approved' ? '#d1fae5' : '#fee2e2', color: req.status === 'pending' ? '#92400e' : req.status === 'approved' ? '#065f46' : '#991b1b' }}>
                                                    {req.status === 'pending' ? '⏳ Pending' : req.status === 'approved' ? '✅ Approved' : '❌ Rejected'}
                                                </span>
                                                {req.status === 'rejected' && req.rejection_reason && (
                                                    <div style={{ fontSize: '0.7rem', color: '#991b1b', marginTop: '4px', background: '#fef2f2', padding: '4px 8px', borderRadius: '4px' }}>{req.rejection_reason}</div>
                                                )}
                                                {req.status !== 'pending' && req.actioned_by_name && (
                                                    <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '4px' }}>By: {req.actioned_by_name}</div>
                                                )}
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                {req.status === 'pending' && isCompanyAdmin ? (
                                                    <button
                                                        onClick={() => { setQualReviewPopup({ req }); setQualRejectMode(false); setQualRejectReason(''); }}
                                                        style={{ padding: '6px 14px', background: '#1d2686', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '700', fontSize: '0.8rem' }}
                                                    >
                                                        🔍 Review & Decide
                                                    </button>
                                                ) : req.status === 'pending' ? (
                                                    <span style={{ fontSize: '0.75rem', color: '#9ca3af', fontStyle: 'italic' }}>Awaiting admin</span>
                                                ) : (
                                                    <span style={{ color: '#9ca3af' }}>—</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* ── Face Mismatch Approvals Tab ── */}
                {tab === 'face_approvals' && (
                    <div style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
                        <div style={{ padding: '1.5rem', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
                            <h3 style={{ margin: 0, color: '#3b82f6', fontWeight: '800' }}>👤 Face Mismatch Approvals</h3>
                            <button onClick={loadFaceRequests} style={{ padding: '6px 14px', border: '1px solid #d1d5db', borderRadius: '8px', background: '#f9fafb', cursor: 'pointer', fontWeight: '600', fontSize: '0.85rem' }}>🔄 Refresh</button>
                        </div>
                        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                <span style={{ fontWeight: '600', color: '#374151' }}>Filter:</span>
                                <select
                                    value={filterStatus}
                                    onChange={e => setFilterStatus(e.target.value)}
                                    style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1d5db', outline: 'none', background: '#f9fafb', fontSize: '0.9rem' }}
                                >
                                    <option value="all">All Requests</option>
                                    <option value="pending">⏳ Pending</option>
                                    <option value="approved">✅ Approved</option>
                                    <option value="rejected">❌ Rejected</option>
                                </select>
                            </div>
                            <div style={{ flex: '1', minWidth: '200px', maxWidth: '400px' }}>
                                <input 
                                    type="text" 
                                    placeholder="Search by name or HR recruiter..." 
                                    value={searchTerm}
                                    onChange={e => setSearchTerm(e.target.value)}
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1d5db', outline: 'none', fontSize: '0.9rem' }}
                                />
                            </div>
                            <div style={{ flex: '1', minWidth: '150px', maxWidth: '200px' }}>
                                <input 
                                    type="date" 
                                    value={filterDate}
                                    onChange={e => setFilterDate(e.target.value)}
                                    style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1d5db', outline: 'none', fontSize: '0.9rem' }}
                                />
                            </div>
                        </div>
                        
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem', textAlign: 'left' }}>
                                <thead style={{ background: '#f3f4f6', color: '#4b5563', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: '0.05em' }}>
                                    <tr>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Candidate</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Requested By</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>HR Reason</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Requested At</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Status</th>
                                        <th style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {faceLoading ? (
                                        <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>Loading...</td></tr>
                                    ) : filteredFaceRequests.length === 0 ? (
                                        <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>No face update requests found.</td></tr>
                                    ) : filteredFaceRequests.map(req => (
                                        <tr key={req.id} style={{ borderBottom: '1px solid #e5e7eb', background: req.status === 'pending' ? '#f0f9ff' : '#fff' }}>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <div style={{ fontWeight: '700', color: '#111827' }}>{req.candidate_name || '—'}</div>
                                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{req.candidate_email}</div>
                                                <div style={{ fontSize: '0.7rem', color: '#9ca3af', marginTop: '2px' }}>PAN: {req.candidate_pan}</div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <div style={{ fontWeight: '600' }}>{req.hr_name}</div>
                                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{req.hr_role}</div>
                                                <div style={{ fontSize: '0.7rem', color: '#9ca3af' }}>{req.hr_email}</div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top', maxWidth: '250px' }}>
                                                <div style={{ fontSize: '0.82rem', color: '#374151', background: '#f9fafb', padding: '6px 10px', borderRadius: '6px', border: '1px solid #e5e7eb', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                                                    {req.hr_reason}
                                                </div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <div>{new Date(req.requested_at).toLocaleDateString()}</div>
                                                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{new Date(req.requested_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                <span style={{ display: 'inline-flex', alignItems: 'center', padding: '3px 10px', borderRadius: '999px', fontSize: '0.75rem', fontWeight: '700', background: req.status === 'pending' ? '#fef3c7' : req.status === 'approved' ? '#d1fae5' : '#fee2e2', color: req.status === 'pending' ? '#92400e' : req.status === 'approved' ? '#065f46' : '#991b1b' }}>
                                                    {req.status === 'pending' ? '⏳ Pending' : req.status === 'approved' ? '✅ Approved' : '❌ Rejected'}
                                                </span>
                                                {req.status === 'rejected' && req.admin_note && (
                                                    <div style={{ fontSize: '0.7rem', color: '#991b1b', marginTop: '4px', background: '#fef2f2', padding: '4px 8px', borderRadius: '4px' }}>Note: {req.admin_note}</div>
                                                )}
                                                {req.status === 'approved' && req.admin_name && (
                                                    <div style={{ fontSize: '0.7rem', color: '#6b7280', marginTop: '4px' }}>By: {req.admin_name}</div>
                                                )}
                                                {req.status === 'approved' && req.admin_note && (
                                                    <div style={{ fontSize: '0.7rem', color: '#4b5563', marginTop: '4px', background: '#f0fdf4', padding: '4px 8px', borderRadius: '4px' }}>Note: {req.admin_note}</div>
                                                )}
                                            </td>
                                            <td style={{ padding: '12px 16px', verticalAlign: 'top' }}>
                                                {req.status === 'pending' && isCompanyAdmin ? (
                                                    <button
                                                        onClick={() => { 
                                                            setFaceReviewPopup({ req }); 
                                                            setFaceAdminNote('');
                                                            setFaceApprovedChoice(true);
                                                            setIntegrityApprovedChoice(true);
                                                        }}
                                                        style={{ padding: '6px 14px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '700', fontSize: '0.8rem' }}
                                                    >
                                                        🔍 Review & Decide
                                                    </button>
                                                ) : req.status === 'pending' ? (
                                                    <span style={{ fontSize: '0.75rem', color: '#9ca3af', fontStyle: 'italic' }}>Awaiting admin review</span>
                                                ) : (
                                                    <span style={{ color: '#9ca3af' }}>—</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* ── Face Mismatch & Combined Integrity Review Popup ── */}
                {faceReviewPopup && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1300, backdropFilter: 'blur(4px)' }}>
                        <div style={{ background: '#fff', borderRadius: '20px', padding: '36px', width: '100%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto', boxShadow: '0 30px 80px rgba(0,0,0,0.25)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '800', color: '#111827' }}>
                                    🔍 {faceReviewPopup.req.integrity_flagged ? "Review Identity Mismatch & Proctoring Integrity" : "Review Face Mismatch Request"}
                                </h3>
                                <button 
                                    disabled={faceActionSubmitting} 
                                    onClick={() => { setFaceReviewPopup(null); setFaceAdminNote(''); }} 
                                    style={{ background: 'none', border: 'none', cursor: faceActionSubmitting ? 'not-allowed' : 'pointer', fontSize: '1.3rem', color: '#9ca3af' }}
                                >
                                    ✕
                                </button>
                            </div>

                            <div style={{ background: '#f9fafb', borderRadius: '12px', padding: '16px', marginBottom: '20px', border: '1px solid #e5e7eb' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', fontSize: '0.85rem' }}>
                                    <div>
                                        <span style={{ color: '#6b7280', fontWeight: '600' }}>Candidate Details:</span><br/>
                                        <strong>{faceReviewPopup.req.candidate_name}</strong><br/>
                                        <span style={{ color: '#6b7280', fontSize: '0.78rem' }}>{faceReviewPopup.req.candidate_email}</span><br/>
                                        <span style={{ color: '#6b7280', fontSize: '0.78rem' }}>PAN: {faceReviewPopup.req.candidate_pan}</span>
                                    </div>
                                    <div>
                                        <span style={{ color: '#6b7280', fontWeight: '600' }}>Requested By:</span><br/>
                                        <strong>{faceReviewPopup.req.hr_name}</strong><br/>
                                        <span style={{ color: '#6b7280', fontSize: '0.78rem' }}>{faceReviewPopup.req.hr_role}</span><br/>
                                        <span style={{ color: '#6b7280', fontSize: '0.78rem' }}>{faceReviewPopup.req.hr_email}</span>
                                    </div>
                                    <div style={{ gridColumn: '1/-1' }}>
                                        <span style={{ color: '#6b7280', fontWeight: '600' }}>HR Reason for Approval Request:</span><br/>
                                        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '8px 12px', marginTop: '4px', fontSize: '0.85rem', color: '#374151', fontStyle: 'italic' }}>
                                            "{faceReviewPopup.req.hr_reason}"
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Side by side photo comparison */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                    <span style={{ fontSize: '0.75rem', fontWeight: '800', color: '#4b5563', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Original Registered Face</span>
                                    <div style={{ width: '100%', aspectRatio: '4/3', borderRadius: '12px', overflow: 'hidden', border: '2px solid #e5e7eb', background: '#f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        {faceReviewPopup.req.original_face_url ? (
                                            <img src={getImageUrl(faceReviewPopup.req.original_face_url)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="Original Registered" />
                                        ) : (
                                            <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>No image available</span>
                                        )}
                                    </div>
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                    <span style={{ fontSize: '0.75rem', fontWeight: '800', color: '#ef4444', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Captured Mismatch Face</span>
                                    <div style={{ width: '100%', aspectRatio: '4/3', borderRadius: '12px', overflow: 'hidden', border: '2px solid #fee2e2', background: '#fdf2f2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        {faceReviewPopup.req.captured_face_url ? (
                                            <img src={getImageUrl(faceReviewPopup.req.captured_face_url)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="Captured Mismatch" />
                                        ) : (
                                            <span style={{ color: '#ef4444', fontSize: '0.8rem' }}>No image available</span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Proctoring Integrity Violations Log (if flagged) */}
                            {faceReviewPopup.req.integrity_flagged && faceReviewPopup.req.integrity_details && (
                                <div style={{ marginTop: '10px', marginBottom: '24px', padding: '20px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '12px', borderLeft: '5px solid #f59e0b', color: '#78350f' }}>
                                    <h4 style={{ margin: '0 0 12px 0', fontSize: '1rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        ⚠️ Proctoring Integrity Violations Log
                                    </h4>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px', fontSize: '0.8rem', marginBottom: '16px' }}>
                                        <div style={{ background: '#fff', padding: '8px 12px', borderRadius: '8px', border: '1px solid #fde68a' }}>
                                            <span style={{ color: '#92400e', fontWeight: '600' }}>Integrity Score:</span><br/>
                                            <strong style={{ fontSize: '1rem', color: '#b45309' }}>{faceReviewPopup.req.integrity_details.integrity_score}%</strong>
                                        </div>
                                        <div style={{ background: '#fff', padding: '8px 12px', borderRadius: '8px', border: '1px solid #fde68a' }}>
                                            <span style={{ color: '#92400e', fontWeight: '600' }}>Tab Switches:</span><br/>
                                            <strong>{faceReviewPopup.req.integrity_details.tab_switches}</strong>
                                        </div>
                                        <div style={{ background: '#fff', padding: '8px 12px', borderRadius: '8px', border: '1px solid #fde68a' }}>
                                            <span style={{ color: '#92400e', fontWeight: '600' }}>Phone Detections:</span><br/>
                                            <strong>{faceReviewPopup.req.integrity_details.phone_detections}</strong>
                                        </div>
                                        <div style={{ background: '#fff', padding: '8px 12px', borderRadius: '8px', border: '1px solid #fde68a' }}>
                                            <span style={{ color: '#92400e', fontWeight: '600' }}>Multi-face:</span><br/>
                                            <strong>{faceReviewPopup.req.integrity_details.multiface_detections}</strong>
                                        </div>
                                        <div style={{ background: '#fff', padding: '8px 12px', borderRadius: '8px', border: '1px solid #fde68a' }}>
                                            <span style={{ color: '#92400e', fontWeight: '600' }}>No face:</span><br/>
                                            <strong>{faceReviewPopup.req.integrity_details.no_face_detections}</strong>
                                        </div>
                                    </div>
                                    
                                    {faceReviewPopup.req.integrity_details.suspicion_reasons && faceReviewPopup.req.integrity_details.suspicion_reasons.length > 0 && (
                                        <div style={{ marginBottom: '16px', fontSize: '0.82rem' }}>
                                            <span style={{ fontWeight: '700', color: '#92400e' }}>Suspicion Reasons:</span>
                                            <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px', lineHeight: '1.4' }}>
                                                {faceReviewPopup.req.integrity_details.suspicion_reasons.map((r, idx) => <li key={idx}>{r}</li>)}
                                            </ul>
                                        </div>
                                    )}

                                    {/* Proctoring Screenshots Grid */}
                                    {faceReviewPopup.req.integrity_screenshots && faceReviewPopup.req.integrity_screenshots.length > 0 && (
                                        <div>
                                            <span style={{ fontWeight: '700', color: '#92400e', fontSize: '0.82rem', display: 'block', marginBottom: '8px' }}>Captured Violation Screenshots:</span>
                                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(170px, 1fr))', gap: '15px' }}>
                                                {faceReviewPopup.req.integrity_screenshots.map((snap, idx) => (
                                                    <div key={idx} style={{ background: '#fff', borderRadius: '8px', padding: '8px', border: '1px solid #fde68a', display: 'flex', flexDirection: 'column' }}>
                                                        <div style={{ width: '100%', aspectRatio: '4/3', overflow: 'hidden', borderRadius: '6px', border: '1px solid #e5e7eb', background: '#f3f4f6', display: 'flex', alignItems: 'center', justify: 'center' }}>
                                                            {snap.screenshot_url || snap.webcam_screenshot_url ? (
                                                                <img 
                                                                    src={getImageUrl(snap.screenshot_url || snap.webcam_screenshot_url)} 
                                                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                                                                    alt={snap.event_type} 
                                                                />
                                                            ) : (
                                                                <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>No image</span>
                                                            )}
                                                        </div>
                                                        <span style={{ fontSize: '0.72rem', fontWeight: '700', color: '#111827', marginTop: '6px', textTransform: 'capitalize' }}>
                                                            {snap.event_type.replace(/_/g, ' ')}
                                                        </span>
                                                        <span style={{ fontSize: '0.65rem', color: '#6b7280', marginTop: '2px' }}>
                                                            {new Date(snap.timestamp).toLocaleString()}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Decisions & Note Section */}
                            <div style={{ background: '#f9fafb', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                                <h4 style={{ margin: '0 0 16px 0', fontSize: '0.92rem', fontWeight: '800', color: '#111827', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    ⚙️ {faceReviewPopup.req.integrity_flagged ? "Combined Verification Decisions" : "Verification Decisions"}
                                </h4>
                                
                                {/* Face Decision Block */}
                                <div style={{ marginBottom: '20px' }}>
                                    <span style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '8px' }}>
                                        1. Face Identity Mismatch Approval:
                                    </span>
                                    <div style={{ display: 'flex', gap: '20px' }}>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: faceActionSubmitting ? 'not-allowed' : 'pointer', fontSize: '0.85rem', opacity: faceActionSubmitting ? 0.65 : 1 }}>
                                            <input 
                                                type="radio" 
                                                name="face_decision_opt" 
                                                disabled={faceActionSubmitting}
                                                checked={faceApprovedChoice === true} 
                                                onChange={() => setFaceApprovedChoice(true)} 
                                            />
                                            <span style={{ color: '#047857', fontWeight: '700' }}>Approve (Face matches candidate)</span>
                                        </label>
                                        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: faceActionSubmitting ? 'not-allowed' : 'pointer', fontSize: '0.85rem', opacity: faceActionSubmitting ? 0.65 : 1 }}>
                                            <input 
                                                type="radio" 
                                                name="face_decision_opt" 
                                                disabled={faceActionSubmitting}
                                                checked={faceApprovedChoice === false} 
                                                onChange={() => setFaceApprovedChoice(false)} 
                                            />
                                            <span style={{ color: '#b91c1c', fontWeight: '700' }}>Reject (Face does not match)</span>
                                        </label>
                                    </div>
                                </div>

                                {/* Integrity Decision Block (only if flagged) */}
                                {faceReviewPopup.req.integrity_flagged && (
                                    <div style={{ marginBottom: '20px', paddingTop: '12px', borderTop: '1px solid #e5e7eb' }}>
                                        <span style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '8px' }}>
                                            2. Proctoring Integrity Approval:
                                        </span>
                                        <div style={{ display: 'flex', gap: '20px' }}>
                                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: faceActionSubmitting ? 'not-allowed' : 'pointer', fontSize: '0.85rem', opacity: faceActionSubmitting ? 0.65 : 1 }}>
                                                <input 
                                                    type="radio" 
                                                    name="integrity_decision_opt" 
                                                    disabled={faceActionSubmitting}
                                                    checked={integrityApprovedChoice === true} 
                                                    onChange={() => setIntegrityApprovedChoice(true)} 
                                                />
                                                <span style={{ color: '#047857', fontWeight: '700' }}>Approve (Override/accept flags)</span>
                                            </label>
                                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: faceActionSubmitting ? 'not-allowed' : 'pointer', fontSize: '0.85rem', opacity: faceActionSubmitting ? 0.65 : 1 }}>
                                                <input 
                                                    type="radio" 
                                                    name="integrity_decision_opt" 
                                                    disabled={faceActionSubmitting}
                                                    checked={integrityApprovedChoice === false} 
                                                    onChange={() => setIntegrityApprovedChoice(false)} 
                                                />
                                                <span style={{ color: '#b91c1c', fontWeight: '700' }}>Reject (Disqualify candidate)</span>
                                            </label>
                                        </div>
                                    </div>
                                )}

                                {/* Expected Status Preview */}
                                <div style={{
                                    background: (faceApprovedChoice && (!faceReviewPopup.req.integrity_flagged || integrityApprovedChoice)) ? '#ecfdf5' : '#fef2f2',
                                    border: '1px solid',
                                    borderColor: (faceApprovedChoice && (!faceReviewPopup.req.integrity_flagged || integrityApprovedChoice)) ? '#a7f3d0' : '#fecaca',
                                    borderRadius: '8px',
                                    padding: '12px 16px',
                                    marginBottom: '20px',
                                    fontSize: '0.85rem',
                                    fontWeight: '800',
                                    color: (faceApprovedChoice && (!faceReviewPopup.req.integrity_flagged || integrityApprovedChoice)) ? '#047857' : '#b91c1c',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}>
                                    {(faceApprovedChoice && (!faceReviewPopup.req.integrity_flagged || integrityApprovedChoice)) ? (
                                        <>✅ Candidate status will change to: Qualified (Selected)</>
                                    ) : (
                                        <>❌ Candidate status will change to: Not Qualified (Rejected)</>
                                    )}
                                </div>

                                {/* Admin Note */}
                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{ display: 'block', fontWeight: '700', fontSize: '0.85rem', color: '#374151', marginBottom: '6px' }}>
                                        Admin Notes / Audit Justification (Optional)
                                    </label>
                                    <textarea
                                        value={faceAdminNote}
                                        onChange={e => setFaceAdminNote(e.target.value)}
                                        placeholder="Add notes explaining your decision (e.g., ID verified manually, proctoring snapshots inspected)..."
                                        rows={3}
                                        disabled={faceActionSubmitting}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '0.9rem', fontFamily: 'inherit', outline: 'none', resize: 'vertical', boxSizing: 'border-box' }}
                                    />
                                </div>

                                {/* Actions */}
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <button 
                                        disabled={faceActionSubmitting}
                                        onClick={() => { setFaceReviewPopup(null); setFaceAdminNote(''); }} 
                                        style={{ flex: 1, padding: '12px', background: '#fff', border: '1px solid #d1d5db', borderRadius: '10px', cursor: faceActionSubmitting ? 'not-allowed' : 'pointer', fontWeight: '600', opacity: faceActionSubmitting ? 0.6 : 1 }}
                                    >
                                        Cancel
                                    </button>
                                    <button 
                                        disabled={faceActionSubmitting}
                                        onClick={() => handleFaceAction(faceReviewPopup.req.id, faceApprovedChoice, faceReviewPopup.req.integrity_flagged ? integrityApprovedChoice : null, faceAdminNote)} 
                                        style={{
                                            flex: 2,
                                            padding: '12px',
                                            background: faceActionSubmitting ? '#94a3b8' : '#3b82f6',
                                            color: '#fff',
                                            border: 'none',
                                            borderRadius: '10px',
                                            cursor: faceActionSubmitting ? 'not-allowed' : 'pointer',
                                            fontWeight: '700',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '8px'
                                        }}
                                    >
                                        {faceActionSubmitting ? '⏳ Submitting...' : 'Submit Decisions'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* ── Qualification Review Popup ── */}
                {qualReviewPopup && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1300, backdropFilter: 'blur(4px)' }}>
                        <div style={{ background: '#fff', borderRadius: '20px', padding: '36px', width: '100%', maxWidth: '520px', boxShadow: '0 30px 80px rgba(0,0,0,0.25)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '800', color: '#111827' }}>🔍 Review Qualification Request</h3>
                                <button onClick={() => { setQualReviewPopup(null); setQualRejectMode(false); setQualRejectReason(''); }} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.3rem', color: '#9ca3af' }}>✕</button>
                            </div>

                            <div style={{ background: '#f9fafb', borderRadius: '12px', padding: '16px', marginBottom: '16px', border: '1px solid #e5e7eb' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.85rem' }}>
                                    <div><span style={{ color: '#6b7280', fontWeight: '600' }}>Candidate:</span><br/><strong>{qualReviewPopup.req.candidate_name}</strong><br/><span style={{ color: '#9ca3af', fontSize: '0.78rem' }}>{qualReviewPopup.req.candidate_email}</span></div>
                                    <div><span style={{ color: '#6b7280', fontWeight: '600' }}>Requested by:</span><br/><strong>{qualReviewPopup.req.requester_name}</strong><br/><span style={{ color: '#9ca3af', fontSize: '0.78rem' }}>{qualReviewPopup.req.requester_role}</span></div>
                                    <div style={{ gridColumn: '1/-1' }}><span style={{ color: '#6b7280', fontWeight: '600' }}>Change Requested:</span><br/>
                                        <span style={{ fontWeight: '800', padding: '3px 12px', borderRadius: '999px', fontSize: '0.85rem', background: qualReviewPopup.req.requested_result === 'selected' ? '#d1fae5' : '#fee2e2', color: qualReviewPopup.req.requested_result === 'selected' ? '#065f46' : '#991b1b' }}>
                                            {qualReviewPopup.req.requested_result === 'selected' ? '✅ Mark as Qualified' : '❌ Mark as Not Qualified'}
                                        </span>
                                    </div>
                                    <div style={{ gridColumn: '1/-1' }}><span style={{ color: '#6b7280', fontWeight: '600' }}>Reason from HR:</span><br/>
                                        <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '8px 12px', marginTop: '4px', fontSize: '0.85rem', color: '#374151', whiteSpace: 'pre-wrap' }}>{qualReviewPopup.req.reason}</div>
                                    </div>
                                </div>
                            </div>

                            {qualReviewPopup.req.report_url && (
                                <button
                                    onClick={() => handleDownloadQualReport(qualReviewPopup.req)}
                                    disabled={downloadingQualId === qualReviewPopup.req.id}
                                    style={{ width: '100%', padding: '12px', background: downloadingQualId === qualReviewPopup.req.id ? '#9ca3af' : '#4f46e5', color: '#fff', border: 'none', borderRadius: '10px', cursor: downloadingQualId === qualReviewPopup.req.id ? 'not-allowed' : 'pointer', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                                >
                                    {downloadingQualId === qualReviewPopup.req.id ? '⏳ Downloading...' : '📄 Download Candidate Report'}
                                </button>
                            )}

                            {!qualRejectMode ? (
                                <div style={{ display: 'flex', gap: '10px' }}>
                                    <button onClick={() => setQualRejectMode(true)} style={{ flex: 1, padding: '12px', background: '#fee2e2', color: '#991b1b', border: '1px solid #fca5a5', borderRadius: '10px', cursor: 'pointer', fontWeight: '700' }}>❌ Reject</button>
                                    <button onClick={() => handleQualAction(qualReviewPopup.req.id, 'approve')} style={{ flex: 1, padding: '12px', background: '#059669', color: '#fff', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: '700' }}>✅ Approve</button>
                                </div>
                            ) : (
                                <div>
                                    <label style={{ display: 'block', fontWeight: '700', fontSize: '0.85rem', color: '#374151', marginBottom: '6px' }}>Rejection Reason <span style={{ color: '#ef4444' }}>*</span></label>
                                    <textarea
                                        value={qualRejectReason}
                                        onChange={e => setQualRejectReason(e.target.value)}
                                        placeholder="Explain why you are rejecting this request..."
                                        rows={3}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '0.9rem', fontFamily: 'inherit', outline: 'none', resize: 'vertical', boxSizing: 'border-box', marginBottom: '10px' }}
                                    />
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <button onClick={() => setQualRejectMode(false)} style={{ flex: 1, padding: '10px', background: '#fff', border: '1px solid #d1d5db', borderRadius: '10px', cursor: 'pointer', fontWeight: '600' }}>Back</button>
                                        <button
                                            onClick={() => { if (!qualRejectReason.trim()) { alert('Please provide a rejection reason.'); return; } handleQualAction(qualReviewPopup.req.id, 'reject', qualRejectReason); }}
                                            disabled={!qualRejectReason.trim()}
                                            style={{ flex: 1, padding: '10px', background: qualRejectReason.trim() ? '#dc2626' : '#9ca3af', color: '#fff', border: 'none', borderRadius: '10px', cursor: qualRejectReason.trim() ? 'pointer' : 'not-allowed', fontWeight: '700' }}
                                        >Confirm Reject</button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Reject Modal (Deletion) */}
                {rejectModal && (
                    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1200, backdropFilter: 'blur(4px)' }}>
                        <div style={{ background: 'white', padding: '2rem', borderRadius: '16px', width: '400px', boxShadow: '0 20px 50px rgba(0,0,0,0.2)' }}>
                            <h3 style={{ marginBottom: '1rem', color: '#991b1b' }}>❌ Reject Deletion Request</h3>
                            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '0.5rem' }}>Reason for Rejection</label>
                            <textarea
                                id="reject-reason-field"
                                style={{ width: '100%', borderRadius: '8px', border: '1px solid #e5e7eb', padding: '0.75rem', fontSize: '0.9rem', minHeight: '80px', fontFamily: 'inherit', outline: 'none' }}
                                placeholder="Explain why this request is being rejected..."
                            />
                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.25rem', justifyContent: 'flex-end' }}>
                                <button onClick={() => setRejectModal(null)} style={{ padding: '8px 18px', border: '1px solid #e5e7eb', borderRadius: '10px', cursor: 'pointer', fontWeight: '700', background: 'white' }}>Cancel</button>
                                <button
                                    onClick={() => {
                                        const reason = document.getElementById('reject-reason-field')?.value;
                                        if (!reason || reason.trim().length < 5) { alert("Please provide a meaningful reason."); return; }
                                        handleAction(rejectModal.requestId, 'reject', reason);
                                        setRejectModal(null);
                                    }}
                                    style={{ padding: '8px 18px', border: 'none', borderRadius: '10px', background: '#ef4444', color: 'white', cursor: 'pointer', fontWeight: '700' }}
                                >
                                    Confirm Reject
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <style>{`
                .switch {
                    position: relative;
                    display: inline-block;
                    width: 50px;
                    height: 24px;
                }
                .switch input { 
                    opacity: 0;
                    width: 0;
                    height: 0;
                }
                .slider {
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: .4s;
                }
                .slider:before {
                    position: absolute;
                    content: "";
                    height: 16px;
                    width: 16px;
                    left: 4px;
                    bottom: 4px;
                    background-color: white;
                    transition: .4s;
                }
                input:checked + .slider {
                    background-color: #1d2686;
                }
                input:checked + .slider:before {
                    transform: translateX(26px);
                }
                .slider.round {
                    border-radius: 34px;
                }
                .slider.round:before {
                    border-radius: 50%;
                }
            `}</style>
        </div>
    );
};

export default Settings;
