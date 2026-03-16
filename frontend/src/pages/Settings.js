import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';

const Settings = () => {
    const [user, setUser] = useState(null);
    const [settings, setSettings] = useState({ require_delete_permission: true });
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('requests'); // 'requests' or 'config'
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

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
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '2rem' }}>
                        {/* Pending Approvals Section */}
                        <div>
                            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#92400e' }}>
                                <i className="fa-solid fa-hourglass-half" style={{ color: '#f59e0b' }}></i>
                                Pending Approvals
                                {requests.filter(r => r.status === 'pending').length > 0 && (
                                    <span style={{ background: '#f59e0b', color: 'white', borderRadius: '999px', padding: '2px 8px', fontSize: '0.75rem' }}>
                                        {requests.filter(r => r.status === 'pending').length}
                                    </span>
                                )}
                            </h3>
                            {loading ? <p>Loading...</p> : (
                                requests.filter(r => r.status === 'pending').length === 0 ?
                                <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>✅ No pending requests.</p> : (
                                    <div style={{ display: 'grid', gap: '1rem' }}>
                                        {requests.filter(r => r.status === 'pending').map(req => (
                                            <div key={req.id} style={{ background: '#fffbeb', padding: '1rem', borderRadius: '12px', border: '1px solid #fde68a', boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                    <span style={{ color: '#78350f', fontSize: '0.75rem', fontWeight: '700' }}>{req.content_type}</span>
                                                    <span style={{ color: '#9ca3af', fontSize: '0.7rem' }}>{new Date(req.created_at).toLocaleString()}</span>
                                                </div>
                                                <div style={{ fontWeight: 'bold', fontSize: '1rem', marginBottom: '0.25rem', color: '#1f2937' }}>
                                                    {req.object_repr || `ID ${req.object_id}`}
                                                </div>
                                                <div style={{ fontSize: '0.8rem', color: '#374151', marginBottom: '0.25rem' }}>
                                                    <strong>From:</strong> {req.requester_name} <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>({req.requester_role})</span>
                                                </div>
                                                {req.reason && (
                                                    <div style={{ fontSize: '0.8rem', marginTop: '0.5rem', color: '#374151', background: '#fef9c3', padding: '6px 10px', borderRadius: '6px', borderLeft: '3px solid #fbbf24', fontStyle: 'italic' }}>
                                                        <strong>Reason:</strong> "{req.reason}"
                                                    </div>
                                                )}

                                                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                                                    {(isCompanyAdmin || req.approver_email === user?.email) ? (
                                                        <>
                                                            <button
                                                                onClick={() => handleAction(req.id, 'approve')}
                                                                style={{ flex: 1, padding: '8px', background: '#d1fae5', color: '#065f46', border: '1px solid #6ee7b750', borderRadius: '8px', cursor: 'pointer', fontWeight: '700', fontSize: '0.82rem' }}
                                                            >✅ Approve & Delete</button>
                                                            <button
                                                                onClick={() => setRejectModal({ requestId: req.id })}
                                                                style={{ flex: 1, padding: '8px', background: '#fee2e2', color: '#991b1b', border: '1px solid #fca5a550', borderRadius: '8px', cursor: 'pointer', fontWeight: '700', fontSize: '0.82rem' }}
                                                            >❌ Reject</button>
                                                        </>
                                                    ) : (
                                                        <div style={{ fontSize: '0.75rem', color: '#9ca3af', fontStyle: 'italic', paddingTop: '4px' }}>
                                                            ⏳ Waiting for {req.approver_name}'s approval
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )
                            )}
                        </div>

                        {/* Recycle Bin / Audit Log Section */}
                        <div style={{ borderLeft: '1px solid #f3f4f6', paddingLeft: '1.5rem' }}>
                            <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#374151' }}>
                                <i className="fa-solid fa-trash-can" style={{ color: '#6366f1' }}></i>
                                Recycle Bin (Audit Log)
                            </h3>
                            {loading ? <p>Loading...</p> : (
                                requests.filter(r => r.status !== 'pending').length === 0 ?
                                <p style={{ color: '#6b7280', fontSize: '0.9rem' }}>No deleted items in history.</p> : (
                                    <div style={{ display: 'grid', gap: '1rem' }}>
                                        {requests.filter(r => r.status !== 'pending').map(req => (
                                            <div key={req.id} style={{
                                                background: req.status === 'approved' ? '#f8faff' : '#fff8f8',
                                                padding: '1rem', borderRadius: '12px',
                                                border: `1px solid ${req.status === 'approved' ? '#c7d2fe' : '#fecaca'}`,
                                            }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                                    <span style={{ color: '#6b7280', fontSize: '0.72rem' }}>
                                                        {req.content_type} • {new Date(req.actioned_at || req.created_at).toLocaleDateString()}
                                                    </span>
                                                    <span style={{
                                                        fontSize: '0.65rem', fontWeight: '800', padding: '2px 8px', borderRadius: '999px',
                                                        background: req.status === 'approved' ? '#e0e7ff' : '#fee2e2',
                                                        color: req.status === 'approved' ? '#3730a3' : '#dc2626',
                                                        textTransform: 'uppercase'
                                                    }}>
                                                        {req.status === 'approved' ? '🗑 Deleted' : '✖ Rejected'}
                                                    </span>
                                                </div>
                                                <div style={{ fontWeight: '700', fontSize: '0.95rem', color: '#111827' }}>{req.object_repr}</div>
                                                <div style={{ fontSize: '0.78rem', marginTop: '0.4rem', color: '#4b5563' }}>
                                                    <div>Requested by: <strong>{req.requester_name}</strong> <span style={{ color: '#9ca3af' }}>({req.requester_role})</span></div>
                                                    <div>Actioned by: <strong>{req.approver_name}</strong> <span style={{ color: '#9ca3af' }}>({req.approver_role})</span></div>
                                                </div>
                                                {req.reason && (
                                                    <div style={{ fontSize: '0.75rem', marginTop: '0.4rem', color: '#374151', background: '#f3f4f6', padding: '5px 9px', borderRadius: '5px', fontStyle: 'italic' }}>
                                                        Reason: "{req.reason}"
                                                    </div>
                                                )}
                                                {req.rejection_reason && (
                                                    <div style={{ fontSize: '0.75rem', marginTop: '0.4rem', color: '#991b1b', background: '#fef2f2', padding: '5px 9px', borderRadius: '5px' }}>
                                                        Rejected: {req.rejection_reason}
                                                    </div>
                                                )}
                                                {req.status === 'approved' && isCompanyAdmin && (
                                                    <button
                                                        onClick={() => handleRestore(req.id)}
                                                        style={{ marginTop: '0.75rem', width: '100%', padding: '7px', background: '#ede9fe', color: '#5b21b6', border: '1px solid #c4b5fd', borderRadius: '8px', cursor: 'pointer', fontWeight: '700', fontSize: '0.8rem' }}
                                                    >
                                                        ↩ Restore
                                                    </button>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )
                            )}
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
