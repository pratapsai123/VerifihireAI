import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Zap, Plus, Check, Wallet } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';

const PRESET_AMOUNTS = [100, 200, 500, 1000];
const CREDITS_PER_RUPEE = 3;

const StudentWallet = () => {
    const navigate = useNavigate();
    const [credits, setCredits] = useState(0);
    const [creditsOnHold, setCreditsOnHold] = useState(0);
    const [history, setHistory] = useState([]);
    const [selectedAmount, setSelectedAmount] = useState(null);
    const [customAmount, setCustomAmount] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(null);
    const [error, setError] = useState(null);
    const [expandedTx, setExpandedTx] = useState(null);
    const [teamData, setTeamData] = useState(null);
    const [distributeModal, setDistributeModal] = useState(null); // { memberId, memberName, action: 'distribute'|'revoke' }
    const [distributeAmount, setDistributeAmount] = useState('');
    const [distributeLoading, setDistributeLoading] = useState(false);
    const [creditRequests, setCreditRequests] = useState([]);
    const [approveAmounts, setApproveAmounts] = useState({});
    const [requestModal, setRequestModal] = useState(false);
    const [requestAmount, setRequestAmount] = useState('');
    const [requestReason, setRequestReason] = useState('');
    const [requestLoading, setRequestLoading] = useState(false);

    // Check if user can add credits (students always can, company only admin)
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const canAddCredits = user.role === 'student' || user.role === 'company_admin' || user.role === 'application_admin';
    const isCompanyAdmin = user.role === 'company_admin';

    useEffect(() => {
        const fetchCredits = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE_URL}/students/wallet/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setCredits(res.data.ai_credits || 0);
                setCreditsOnHold(res.data.credits_on_hold || 0);
                setHistory(res.data.history || []);
            } catch (err) {
                console.error('Failed to fetch credits:', err);
            }
        };
        const fetchTeam = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE_URL}/students/credits/team/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setTeamData(res.data);
            } catch (e) {}
        };
        fetchCredits();
        if (isCompanyAdmin) fetchTeam();
        // Fetch credit requests for both admin and members
        const fetchRequests = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE_URL}/students/credits/requests/`, { headers: { Authorization: `Bearer ${token}` } });
                setCreditRequests(res.data || []);
            } catch (e) {}
        };
        if (user.role !== 'student') fetchRequests();
    }, []);

    const activeAmount = selectedAmount || (customAmount ? parseInt(customAmount) : 0);
    const creditsPreview = activeAmount > 0 ? activeAmount * CREDITS_PER_RUPEE : 0;

    const handleRequestCredits = async () => {
        if (!requestAmount || parseInt(requestAmount) < 1) return;
        setRequestLoading(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`${API_BASE_URL}/students/credits/requests/`, {
                amount: parseInt(requestAmount),
                reason: requestReason,
            }, { headers: { Authorization: `Bearer ${token}` } });
            setRequestModal(false);
            setRequestAmount('');
            setRequestReason('');
            // Refresh requests
            const res = await axios.get(`${API_BASE_URL}/students/credits/requests/`, { headers: { Authorization: `Bearer ${token}` } });
            setCreditRequests(res.data || []);
        } catch (err) {
            alert(err.response?.data?.error || 'Failed to submit request.');
        } finally {
            setRequestLoading(false);
        }
    };

    const handleReviewRequest = async (requestId, action) => {
        try {
            const token = localStorage.getItem('token');
            const payload = { request_id: requestId, action };
            if (action === 'approve' && approveAmounts[requestId]) {
                payload.approved_amount = parseInt(approveAmounts[requestId]);
            }
            await axios.put(`${API_BASE_URL}/students/credits/requests/`, payload, { headers: { Authorization: `Bearer ${token}` } });
            // Refresh everything
            const [walletRes, teamRes, reqRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/students/wallet/`, { headers: { Authorization: `Bearer ${token}` } }),
                axios.get(`${API_BASE_URL}/students/credits/team/`, { headers: { Authorization: `Bearer ${token}` } }),
                axios.get(`${API_BASE_URL}/students/credits/requests/`, { headers: { Authorization: `Bearer ${token}` } }),
            ]);
            setCredits(walletRes.data.ai_credits || 0);
            setHistory(walletRes.data.history || []);
            setTeamData(teamRes.data);
            setCreditRequests(reqRes.data || []);
        } catch (err) {
            alert(err.response?.data?.error || 'Failed to process request.');
        }
    };

    const handleDistributeRevoke = async () => {
        if (!distributeModal || !distributeAmount || parseInt(distributeAmount) < 1) return;
        setDistributeLoading(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`${API_BASE_URL}/students/credits/distribute/`, {
                action: distributeModal.action,
                member_id: distributeModal.memberId,
                amount: parseInt(distributeAmount),
            }, { headers: { Authorization: `Bearer ${token}` } });
            // Refresh data
            const [walletRes, teamRes] = await Promise.all([
                axios.get(`${API_BASE_URL}/students/wallet/`, { headers: { Authorization: `Bearer ${token}` } }),
                axios.get(`${API_BASE_URL}/students/credits/team/`, { headers: { Authorization: `Bearer ${token}` } }),
            ]);
            setCredits(walletRes.data.ai_credits || 0);
            setHistory(walletRes.data.history || []);
            setTeamData(teamRes.data);
            setDistributeModal(null);
            setDistributeAmount('');
        } catch (err) {
            alert(err.response?.data?.error || 'Failed. Please try again.');
        } finally {
            setDistributeLoading(false);
        }
    };

    const handlePresetClick = (amount) => {
        setSelectedAmount(amount);
        setCustomAmount('');
        setError(null);
        setSuccess(null);
    };

    const handleCustomChange = (e) => {
        setCustomAmount(e.target.value);
        setSelectedAmount(null);
        setError(null);
        setSuccess(null);
    };

    const handleAddCredits = async () => {
        if (!activeAmount || activeAmount < 10) {
            setError('Minimum amount is ₹10.');
            return;
        }
        if (activeAmount > 100000) {
            setError('Maximum amount is ₹1,00,000.');
            return;
        }

        setLoading(true);
        setError(null);
        setSuccess(null);

        try {
            const token = localStorage.getItem('token');
            // Step 1: Create Razorpay order on backend
            const orderRes = await axios.post(`${API_BASE_URL}/students/payment/create-order/`,
                { amount: activeAmount },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            const { order_id, key_id, amount_paise, credits_to_add } = orderRes.data;

            // Step 2: Open Razorpay checkout popup
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const options = {
                key: key_id,
                amount: amount_paise,
                currency: 'INR',
                name: 'VerifiHireAI',
                description: `Add ${credits_to_add} AI Credits`,
                order_id: order_id,
                handler: async function (response) {
                    // Step 3: Verify payment on backend
                    try {
                        const verifyRes = await axios.post(`${API_BASE_URL}/students/payment/verify/`, {
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                            amount: activeAmount,
                        }, { headers: { Authorization: `Bearer ${token}` } });

                        setCredits(verifyRes.data.ai_credits);
                        setSuccess(`Payment successful! Added ${verifyRes.data.credits_added} AI credits.`);
                        setSelectedAmount(null);
                        setCustomAmount('');

                        // Refresh history
                        const histRes = await axios.get(`${API_BASE_URL}/students/wallet/`, {
                            headers: { Authorization: `Bearer ${token}` }
                        });
                        setHistory(histRes.data.history || []);
                    } catch (verifyErr) {
                        setError('Payment made but verification failed. Contact support with your payment ID.');
                    }
                    setLoading(false);
                },
                prefill: {
                    name: `${user.first_name || ''} ${user.last_name || ''}`.trim(),
                    email: user.email || '',
                },
                theme: {
                    color: '#6366f1',
                },
                modal: {
                    ondismiss: function () {
                        setLoading(false);
                        setError('Payment cancelled.');
                    }
                }
            };

            const razorpay = new window.Razorpay(options);
            razorpay.on('payment.failed', function (resp) {
                setError(`Payment failed: ${resp.error.description}`);
                setLoading(false);
            });
            razorpay.open();

        } catch (err) {
            setError(err.response?.data?.error || 'Failed to initiate payment. Please try again.');
            setLoading(false);
        }
    };

    return (
        <div style={styles.wrapper}>
            <div style={styles.meshBg}></div>
            <div style={styles.content}>

                {/* Header */}
                <div style={styles.header}>
                    <button onClick={() => navigate('/dashboard')} style={styles.backBtn}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 style={styles.title}>AI Credits Wallet</h1>
                        <p style={styles.subtitle}>Add credits to use AI-powered features</p>
                    </div>
                </div>

                {/* Credits Balance Card */}
                <div style={styles.balanceCard}>
                    <div style={styles.balanceIcon}>
                        <Zap size={28} />
                    </div>
                    <div style={{ flex: 1 }}>
                        <p style={styles.balanceLabel}>Available Credits</p>
                        <p style={styles.balanceValue}>{credits.toLocaleString()}</p>
                    </div>
                    {creditsOnHold > 0 && (
                        <div style={{ textAlign: 'right' }}>
                            <p style={{ margin: 0, fontSize: '0.7rem', color: 'rgba(255,255,255,0.7)', fontWeight: 600, textTransform: 'uppercase' }}>On Hold</p>
                            <p style={{ margin: '2px 0 0', fontSize: '1.3rem', fontWeight: 800, color: '#fbbf24' }}>{creditsOnHold.toLocaleString()}</p>
                        </div>
                    )}
                </div>

                {/* Request Credits Button (non-admin company members) */}
                {!isCompanyAdmin && user.role !== 'student' && user.role !== 'interviewer' && (
                    <div style={{ marginBottom: '1.5rem' }}>
                        <button
                            onClick={() => setRequestModal(true)}
                            style={{ width: '100%', padding: '0.85rem', borderRadius: '14px', border: '2px dashed #c7d2fe', background: '#fafafe', color: '#6366f1', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                        >
                            <Plus size={18} /> Request Credits from Admin
                        </button>
                        {creditRequests.length > 0 && (
                            <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                                {creditRequests.map(r => (
                                    <div key={r.id} style={{ padding: '0.6rem 1rem', borderRadius: '10px', background: r.status === 'pending' ? '#fef3c7' : r.status === 'approved' ? '#f0fdf4' : '#fef2f2', border: '1px solid', borderColor: r.status === 'pending' ? '#fde68a' : r.status === 'approved' ? '#bbf7d0' : '#fecaca', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between' }}>
                                        <span>{r.amount} credits {r.reason && `— ${r.reason}`}</span>
                                        <span style={{ fontWeight: 700, textTransform: 'uppercase', fontSize: '0.7rem', color: r.status === 'pending' ? '#92400e' : r.status === 'approved' ? '#065f46' : '#991b1b' }}>{r.status}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Add Credits Section */}
                {canAddCredits && (
                <div style={styles.addSection}>
                    <h2 style={styles.addTitle}>
                        <Plus size={20} style={{ color: '#6366f1' }} />
                        Add Credits
                    </h2>
                    <p style={styles.addSubtitle}>Select or enter an amount to add credits</p>

                    {/* Preset Amounts */}
                    <div style={styles.presetGrid}>
                        {PRESET_AMOUNTS.map((amount) => (
                            <button
                                key={amount}
                                onClick={() => handlePresetClick(amount)}
                                style={{
                                    ...styles.presetBtn,
                                    ...(selectedAmount === amount ? styles.presetBtnActive : {}),
                                }}
                            >
                                <span style={styles.presetAmount}>₹{amount}</span>
                                <span style={styles.presetCredits}>{amount * CREDITS_PER_RUPEE} credits</span>
                            </button>
                        ))}
                    </div>

                    {/* Custom Amount */}
                    <div style={styles.customSection}>
                        <label style={styles.customLabel}>Or enter custom amount (₹)</label>
                        <div style={styles.customInputWrapper}>
                            <span style={styles.currencySymbol}>₹</span>
                            <input
                                type="number"
                                min="10"
                                max="100000"
                                placeholder="Enter amount..."
                                value={customAmount}
                                onChange={handleCustomChange}
                                style={styles.customInput}
                            />
                        </div>
                    </div>

                    {/* Credits Preview */}
                    {creditsPreview > 0 && (
                        <div style={styles.previewBox}>
                            <Zap size={18} style={{ color: '#6366f1' }} />
                            <span style={styles.previewText}>
                                You'll receive <strong>{creditsPreview.toLocaleString()}</strong> AI credits for <strong>₹{activeAmount}</strong>
                            </span>
                        </div>
                    )}

                    {/* Error / Success Messages */}
                    {error && <div style={styles.errorMsg}>{error}</div>}
                    {success && <div style={styles.successMsg}><Check size={16} /> {success}</div>}

                    {/* Add Button */}
                    <button
                        onClick={handleAddCredits}
                        disabled={loading || !activeAmount}
                        style={{
                            ...styles.addBtn,
                            opacity: (loading || !activeAmount) ? 0.6 : 1,
                            cursor: (loading || !activeAmount) ? 'not-allowed' : 'pointer',
                        }}
                    >
                        {loading ? 'Processing...' : `Pay ₹${activeAmount > 0 ? activeAmount : '0'} → ${creditsPreview > 0 ? creditsPreview.toLocaleString() + ' Credits' : 'Select Amount'}`}
                    </button>
                </div>
                )}

                {/* Team Credits Section (Company Admin Only) */}
                {isCompanyAdmin && teamData && (
                    <div style={styles.historySection}>
                        <h2 style={styles.historyTitle}>
                            <Wallet size={20} style={{ color: '#6366f1' }} />
                            Team Credits
                        </h2>
                        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
                            <div style={{ padding: '0.75rem 1.25rem', background: '#eef2ff', borderRadius: '10px', border: '1px solid #c7d2fe' }}>
                                <p style={{ margin: 0, fontSize: '0.7rem', color: '#6366f1', fontWeight: 600, textTransform: 'uppercase' }}>Your Pool</p>
                                <p style={{ margin: '2px 0 0', fontSize: '1.1rem', fontWeight: 800, color: '#4338ca' }}>{teamData.admin_pool}</p>
                            </div>
                            <div style={{ padding: '0.75rem 1.25rem', background: '#f0fdf4', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
                                <p style={{ margin: 0, fontSize: '0.7rem', color: '#10b981', fontWeight: 600, textTransform: 'uppercase' }}>Total Company</p>
                                <p style={{ margin: '2px 0 0', fontSize: '1.1rem', fontWeight: 800, color: '#065f46' }}>{teamData.total_company_credits}</p>
                            </div>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {/* Pending Requests */}
                            {creditRequests.length > 0 && (
                                <div style={{ marginBottom: '1rem', padding: '1rem', background: '#fef3c7', borderRadius: '12px', border: '1px solid #fde68a' }}>
                                    <p style={{ margin: '0 0 0.75rem', fontSize: '0.8rem', fontWeight: 700, color: '#92400e', textTransform: 'uppercase' }}>Pending Requests</p>
                                    {creditRequests.map(r => (
                                        <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.6rem 0', borderBottom: '1px solid #fde68a', gap: '0.75rem', flexWrap: 'wrap' }}>
                                            <div style={{ flex: 1 }}>
                                                <p style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600, color: '#1e293b' }}>{r.requester_name} requests <strong>{r.amount}</strong> credits</p>
                                                {r.reason && <p style={{ margin: '2px 0 0', fontSize: '0.72rem', color: '#92400e' }}>"{r.reason}"</p>}
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                                <input
                                                    type="number"
                                                    min="1"
                                                    defaultValue={r.amount}
                                                    onChange={(e) => setApproveAmounts(prev => ({ ...prev, [r.id]: e.target.value }))}
                                                    style={{ width: '60px', padding: '4px 6px', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem', fontWeight: 600, textAlign: 'center' }}
                                                />
                                                <button onClick={() => handleReviewRequest(r.id, 'approve')} style={{ padding: '4px 10px', borderRadius: '6px', border: 'none', background: '#10b981', color: 'white', fontSize: '0.7rem', fontWeight: 700, cursor: 'pointer' }}>Approve</button>
                                                <button onClick={() => handleReviewRequest(r.id, 'reject')} style={{ padding: '4px 10px', borderRadius: '6px', border: '1px solid #fecaca', background: 'white', color: '#dc2626', fontSize: '0.7rem', fontWeight: 700, cursor: 'pointer' }}>Reject</button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                            {teamData.team.map((m) => (
                                <div key={m.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.85rem 1rem', borderRadius: '12px', background: '#fafafa', border: '1px solid #f1f5f9' }}>
                                    <div>
                                        <p style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600, color: '#1e293b' }}>{m.name}</p>
                                        <p style={{ margin: '2px 0 0', fontSize: '0.72rem', color: '#94a3b8' }}>{m.email} • {m.role?.replace('_', ' ')}</p>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#4338ca' }}>{m.credits}</span>
                                        <button onClick={() => { setDistributeModal({ memberId: m.id, memberName: m.name, action: 'distribute' }); setDistributeAmount(''); }} style={{ padding: '4px 10px', borderRadius: '6px', border: 'none', background: '#6366f1', color: 'white', fontSize: '0.7rem', fontWeight: 600, cursor: 'pointer' }}>Give</button>
                                        {m.credits > 0 && (
                                            <button onClick={() => { setDistributeModal({ memberId: m.id, memberName: m.name, action: 'revoke' }); setDistributeAmount(''); }} style={{ padding: '4px 10px', borderRadius: '6px', border: '1px solid #fecaca', background: '#fef2f2', color: '#dc2626', fontSize: '0.7rem', fontWeight: 600, cursor: 'pointer' }}>Revoke</button>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {teamData.team.length === 0 && (
                                <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: '0.85rem', padding: '1rem' }}>No team members found.</p>
                            )}
                        </div>
                    </div>
                )}

                {/* Distribute/Revoke Modal */}
                {distributeModal && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
                        <div style={{ background: 'white', borderRadius: '20px', padding: '2rem', maxWidth: '380px', width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
                            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.1rem', fontWeight: 700, color: '#1e293b' }}>
                                {distributeModal.action === 'distribute' ? 'Give Credits' : 'Revoke Credits'}
                            </h3>
                            <p style={{ margin: '0 0 1rem', fontSize: '0.85rem', color: '#64748b' }}>
                                {distributeModal.action === 'distribute'
                                    ? `Transfer credits from your pool to ${distributeModal.memberName}`
                                    : `Take back credits from ${distributeModal.memberName} to your pool`
                                }
                            </p>
                            <input
                                type="number"
                                min="1"
                                placeholder="Enter amount"
                                value={distributeAmount}
                                onChange={(e) => setDistributeAmount(e.target.value)}
                                style={{ width: '100%', padding: '0.85rem', border: '2px solid #e2e8f0', borderRadius: '12px', fontSize: '1rem', fontWeight: 600, outline: 'none', marginBottom: '1rem', boxSizing: 'border-box' }}
                            />
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <button onClick={() => setDistributeModal(null)} style={{ flex: 1, padding: '0.8rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: 'white', color: '#475569', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                                <button onClick={handleDistributeRevoke} disabled={distributeLoading || !distributeAmount} style={{ flex: 1, padding: '0.8rem', borderRadius: '12px', border: 'none', background: distributeModal.action === 'distribute' ? '#6366f1' : '#dc2626', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', opacity: (distributeLoading || !distributeAmount) ? 0.6 : 1 }}>
                                    {distributeLoading ? '...' : distributeModal.action === 'distribute' ? 'Give' : 'Revoke'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Request Credits Modal (non-admin members) */}
                {requestModal && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
                        <div style={{ background: 'white', borderRadius: '20px', padding: '2rem', maxWidth: '380px', width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
                            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.1rem', fontWeight: 700, color: '#1e293b' }}>Request Credits</h3>
                            <p style={{ margin: '0 0 1rem', fontSize: '0.85rem', color: '#64748b' }}>Your admin will review this request.</p>
                            <input
                                type="number"
                                min="1"
                                placeholder="How many credits?"
                                value={requestAmount}
                                onChange={(e) => setRequestAmount(e.target.value)}
                                style={{ width: '100%', padding: '0.85rem', border: '2px solid #e2e8f0', borderRadius: '12px', fontSize: '1rem', fontWeight: 600, outline: 'none', marginBottom: '0.75rem', boxSizing: 'border-box' }}
                            />
                            <input
                                type="text"
                                placeholder="Reason (optional)"
                                value={requestReason}
                                onChange={(e) => setRequestReason(e.target.value)}
                                style={{ width: '100%', padding: '0.85rem', border: '2px solid #e2e8f0', borderRadius: '12px', fontSize: '0.9rem', outline: 'none', marginBottom: '1rem', boxSizing: 'border-box' }}
                            />
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <button onClick={() => setRequestModal(false)} style={{ flex: 1, padding: '0.8rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: 'white', color: '#475569', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                                <button onClick={handleRequestCredits} disabled={requestLoading || !requestAmount} style={{ flex: 1, padding: '0.8rem', borderRadius: '12px', border: 'none', background: '#6366f1', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', opacity: (requestLoading || !requestAmount) ? 0.6 : 1 }}>
                                    {requestLoading ? '...' : 'Submit Request'}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Transaction History */}
                <div style={styles.historySection}>
                    <h2 style={styles.historyTitle}>
                        <Wallet size={20} style={{ color: '#6366f1' }} />
                        Transaction History
                    </h2>
                    {history.length === 0 ? (
                        <p style={{ color: '#94a3b8', fontSize: '0.9rem', textAlign: 'center', padding: '2rem' }}>No transactions yet.</p>
                    ) : (
                        <div style={styles.historyList}>
                            {history.map((tx, i) => (
                                <div key={i}>
                                    <div
                                        style={{ ...styles.historyItem, cursor: 'pointer' }}
                                        onClick={() => setExpandedTx(expandedTx === i ? null : i)}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <div style={{
                                                width: '36px', height: '36px', borderRadius: '10px',
                                                background: tx.type === 'added' ? '#f0fdf4' : tx.type === 'refund' ? '#f0fdf4' : tx.type === 'hold' ? '#fef3c7' : '#fef2f2',
                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            }}>
                                                {tx.type === 'added'
                                                    ? <Plus size={16} style={{ color: '#10b981' }} />
                                                    : tx.type === 'refund'
                                                    ? <Plus size={16} style={{ color: '#10b981' }} />
                                                    : tx.type === 'hold'
                                                    ? <Wallet size={16} style={{ color: '#f59e0b' }} />
                                                    : <Zap size={16} style={{ color: '#ef4444' }} />
                                                }
                                            </div>
                                            <div>
                                                <p style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600, color: '#1e293b' }}>
                                                    {tx.description}
                                                    {tx.type === 'hold' && <span style={{ marginLeft: '6px', fontSize: '0.7rem', background: '#fef3c7', color: '#92400e', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>ON HOLD</span>}
                                                    {tx.type === 'refund' && <span style={{ marginLeft: '6px', fontSize: '0.7rem', background: '#d1fae5', color: '#065f46', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>REFUND</span>}
                                                </p>
                                                <p style={{ margin: '2px 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
                                                    {new Date(tx.date).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true })}
                                                </p>
                                            </div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <p style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: (tx.type === 'added' || tx.type === 'refund') ? '#10b981' : tx.type === 'hold' ? '#f59e0b' : '#ef4444' }}>
                                                {(tx.type === 'added' || tx.type === 'refund') ? '+' : '-'}{tx.amount}
                                            </p>
                                            <p style={{ margin: '2px 0 0', fontSize: '0.7rem', color: '#94a3b8' }}>Bal: {tx.balance_after}</p>
                                        </div>
                                    </div>
                                    {/* Expanded Details */}
                                    {expandedTx === i && (
                                        <div style={{ margin: '0 0 0.5rem', padding: '1rem 1.25rem', background: '#f8fafc', borderRadius: '0 0 12px 12px', border: '1px solid #e2e8f0', borderTop: 'none', fontSize: '0.8rem', color: '#475569' }}>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                                                <div>
                                                    <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Transaction Type</p>
                                                    <p style={{ margin: '2px 0 0', fontWeight: 600 }}>{tx.type === 'added' ? 'Credits Added' : tx.type === 'used' ? 'Credits Used' : tx.type === 'hold' ? 'Credits On Hold' : 'Credits Refunded'}</p>
                                                </div>
                                                <div>
                                                    <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Amount</p>
                                                    <p style={{ margin: '2px 0 0', fontWeight: 600 }}>{tx.amount} credits</p>
                                                </div>
                                                <div>
                                                    <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Date & Time</p>
                                                    <p style={{ margin: '2px 0 0', fontWeight: 600 }}>{new Date(tx.date).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true })}</p>
                                                </div>
                                                <div>
                                                    <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Balance After</p>
                                                    <p style={{ margin: '2px 0 0', fontWeight: 600 }}>{tx.balance_after} credits</p>
                                                </div>
                                                <div style={{ gridColumn: '1 / -1' }}>
                                                    <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Description</p>
                                                    <p style={{ margin: '2px 0 0', fontWeight: 600 }}>{tx.description}</p>
                                                </div>
                                                {tx.batch_id && (
                                                    <div style={{ gridColumn: '1 / -1' }}>
                                                        <p style={{ margin: 0, fontSize: '0.7rem', color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase' }}>Batch ID</p>
                                                        <p style={{ margin: '2px 0 0', fontWeight: 600, fontFamily: 'monospace', fontSize: '0.75rem' }}>{tx.batch_id}</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

const styles = {
    wrapper: { minHeight: '100vh', background: '#f8fafc', position: 'relative' },
    meshBg: { position: 'fixed', inset: 0, background: 'radial-gradient(ellipse at 20% 0%, rgba(99,102,241,0.08) 0%, transparent 50%), radial-gradient(ellipse at 80% 100%, rgba(168,85,247,0.06) 0%, transparent 50%)', pointerEvents: 'none', zIndex: 0 },
    content: { position: 'relative', zIndex: 1, maxWidth: '900px', margin: '0 auto', padding: '2rem 1.5rem 4rem' },
    header: { display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' },
    backBtn: { background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', width: '42px', height: '42px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#6366f1', boxShadow: '0 2px 8px rgba(99,102,241,0.08)' },
    title: { margin: 0, fontSize: '1.5rem', fontWeight: 800, color: '#0f172a' },
    subtitle: { margin: '4px 0 0', fontSize: '0.85rem', color: '#64748b' },
    balanceCard: { background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', borderRadius: '20px', padding: '2rem', display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '2rem', boxShadow: '0 8px 30px rgba(99,102,241,0.3)' },
    balanceIcon: { width: '56px', height: '56px', borderRadius: '16px', background: 'rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' },
    balanceLabel: { margin: 0, fontSize: '0.8rem', color: 'rgba(255,255,255,0.8)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' },
    balanceValue: { margin: '4px 0 0', fontSize: '2.5rem', fontWeight: 900, color: 'white', lineHeight: 1 },
    addSection: { background: 'white', borderRadius: '20px', padding: '2rem', border: '1px solid #e2e8f0', boxShadow: '0 2px 12px rgba(0,0,0,0.03)' },
    addTitle: { margin: '0 0 0.25rem', fontSize: '1.1rem', fontWeight: 700, color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' },
    addSubtitle: { margin: '0 0 1.5rem', fontSize: '0.82rem', color: '#94a3b8', fontWeight: 500 },
    presetGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' },
    presetBtn: { padding: '1.25rem 1rem', borderRadius: '14px', border: '2px solid #e2e8f0', background: '#fafafa', cursor: 'pointer', textAlign: 'center', transition: 'all 0.2s', display: 'flex', flexDirection: 'column', gap: '4px' },
    presetBtnActive: { borderColor: '#6366f1', background: '#eef2ff', boxShadow: '0 0 0 3px rgba(99,102,241,0.1)' },
    presetAmount: { fontSize: '1.2rem', fontWeight: 800, color: '#1e293b' },
    presetCredits: { fontSize: '0.75rem', color: '#6366f1', fontWeight: 600 },
    customSection: { marginBottom: '1.5rem' },
    customLabel: { display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#64748b', marginBottom: '0.5rem' },
    customInputWrapper: { display: 'flex', alignItems: 'center', border: '2px solid #e2e8f0', borderRadius: '12px', overflow: 'hidden', transition: 'border-color 0.2s' },
    currencySymbol: { padding: '0 0.75rem', fontSize: '1.1rem', fontWeight: 700, color: '#64748b', background: '#f8fafc' },
    customInput: { flex: 1, padding: '0.85rem', border: 'none', outline: 'none', fontSize: '1rem', fontWeight: 600, color: '#1e293b' },
    previewBox: { display: 'flex', alignItems: 'center', gap: '10px', padding: '1rem', background: '#eef2ff', borderRadius: '12px', marginBottom: '1.25rem', border: '1px solid #c7d2fe' },
    previewText: { fontSize: '0.88rem', color: '#4338ca' },
    errorMsg: { padding: '0.75rem 1rem', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', color: '#dc2626', fontSize: '0.85rem', fontWeight: 500, marginBottom: '1rem' },
    successMsg: { padding: '0.75rem 1rem', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '10px', color: '#16a34a', fontSize: '0.85rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '6px' },
    addBtn: { width: '100%', padding: '1rem', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', border: 'none', borderRadius: '14px', fontSize: '1rem', fontWeight: 700, boxShadow: '0 4px 14px rgba(99,102,241,0.3)', transition: 'all 0.2s' },
    historySection: { background: 'white', borderRadius: '20px', padding: '2rem', border: '1px solid #e2e8f0', boxShadow: '0 2px 12px rgba(0,0,0,0.03)', marginTop: '1.5rem' },
    historyTitle: { margin: '0 0 1.25rem', fontSize: '1.1rem', fontWeight: 700, color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' },
    historyList: { display: 'flex', flexDirection: 'column', gap: '0.5rem' },
    historyItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.85rem 1rem', borderRadius: '12px', background: '#fafafa', border: '1px solid #f1f5f9' },
};

export default StudentWallet;
