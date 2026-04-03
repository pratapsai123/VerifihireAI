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

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }
        loadSettings();
        loadRequests();
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
            setError("Failed to load deletion requests.");
        } finally {
            setLoading(false);
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

    return (
        <div className="dashboard-container">
            <Header />
            <div className="page-container" style={{ maxWidth: '1100px', margin: '2rem auto', padding: '0 1rem' }}>
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

                {/* Reject Modal */}
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
