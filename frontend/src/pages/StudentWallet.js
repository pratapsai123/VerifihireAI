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
    const [history, setHistory] = useState([]);
    const [selectedAmount, setSelectedAmount] = useState(null);
    const [customAmount, setCustomAmount] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCredits = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get(`${API_BASE_URL}/students/wallet/`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setCredits(res.data.ai_credits || 0);
                setHistory(res.data.history || []);
            } catch (err) {
                console.error('Failed to fetch credits:', err);
            }
        };
        fetchCredits();
    }, []);

    const activeAmount = selectedAmount || (customAmount ? parseInt(customAmount) : 0);
    const creditsPreview = activeAmount > 0 ? activeAmount * CREDITS_PER_RUPEE : 0;

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
        if (!activeAmount || activeAmount < 1) {
            setError('Please select or enter an amount.');
            return;
        }
        if (activeAmount > 10000) {
            setError('Maximum amount is ₹10,000.');
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
                    <div>
                        <p style={styles.balanceLabel}>Available Credits</p>
                        <p style={styles.balanceValue}>{credits.toLocaleString()}</p>
                    </div>
                </div>

                {/* Add Credits Section */}
                <div style={styles.addSection}>
                    <h2 style={styles.addTitle}>
                        <Plus size={20} style={{ color: '#6366f1' }} />
                        Add Credits
                    </h2>
                    <p style={styles.addSubtitle}>₹1 = {CREDITS_PER_RUPEE} AI Credits</p>

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
                                min="1"
                                max="10000"
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
                                <div key={i} style={styles.historyItem}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <div style={{
                                            width: '36px', height: '36px', borderRadius: '10px',
                                            background: tx.type === 'added' ? '#f0fdf4' : '#fef2f2',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        }}>
                                            {tx.type === 'added'
                                                ? <Plus size={16} style={{ color: '#10b981' }} />
                                                : <Zap size={16} style={{ color: '#ef4444' }} />
                                            }
                                        </div>
                                        <div>
                                            <p style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600, color: '#1e293b' }}>{tx.description}</p>
                                            <p style={{ margin: '2px 0 0', fontSize: '0.75rem', color: '#94a3b8' }}>
                                                {new Date(tx.date).toLocaleString('en-IN', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true })}
                                            </p>
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <p style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: tx.type === 'added' ? '#10b981' : '#ef4444' }}>
                                            {tx.type === 'added' ? '+' : '-'}{tx.amount}
                                        </p>
                                        <p style={{ margin: '2px 0 0', fontSize: '0.7rem', color: '#94a3b8' }}>Bal: {tx.balance_after}</p>
                                    </div>
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
