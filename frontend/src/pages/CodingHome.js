import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    RefreshCw,
    Plus,
    Clock,
    BarChart,
    CheckCircle,
    Search,
    ChevronDown,
    ChevronUp,
    AlertCircle,
    Play,
    ArrowLeft
} from 'lucide-react';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import '../styles/Coding.css';

export default function CodingHome() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [items, setItems] = useState([]);
    const [selectedIds, setSelectedIds] = useState([]);
    const [langFilters, setLangFilters] = useState([]);
    const [diffFilter, setDiffFilter] = useState('');
    const [langDropdownOpen, setLangDropdownOpen] = useState(false);
    const langDropdownRef = useRef(null);
    const [inactiveWarning, setInactiveWarning] = useState(null);

    const load = async () => {
        setLoading(true);
        setError('');
        try {
            let orgName = '';
            try {
                const stored = localStorage.getItem('user');
                if (stored) {
                    const parsed = JSON.parse(stored);
                    orgName = parsed.organization_name || parsed.organizationName || '';
                }
            } catch {
                // ignore storage errors
            }

            const params = {};
            if (orgName) params.organization_name = orgName;

            const resp = await axios.get(`${API_BASE_URL}/coding/questions/`, { params });
            let results = resp.data?.results || [];

            if (results.length === 0 && orgName) {
                try {
                    const fallbackResp = await axios.get(`${API_BASE_URL}/coding/questions/`);
                    if ((fallbackResp.data?.results || []).length > 0) {
                        results = fallbackResp.data?.results || [];
                    }
                } catch (ignore) { }
            }

            setItems(results);
            setSelectedIds((prev) => (prev || []).filter((id) => results.some((q) => q.id === id)));
        } catch (e) {
            setError(e?.response?.data?.error || e?.message || 'Failed to load coding questions');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
        
        // Ensure scroll container starts from top when page is opened.
        const scrollContainer = document.querySelector('.app-scroll');
        if (scrollContainer) {
            scrollContainer.scrollTop = 0;
        }
        const scrollTimer = setTimeout(() => {
            const scrollContainer = document.querySelector('.app-scroll');
            if (scrollContainer) {
                scrollContainer.scrollTop = 0;
            }
        }, 100);
        return () => clearTimeout(scrollTimer);
    }, []);

    useEffect(() => {
        if (!langDropdownOpen) return undefined;
        const handleClick = (e) => {
            if (langDropdownRef.current && !langDropdownRef.current.contains(e.target)) {
                setLangDropdownOpen(false);
            }
        };
        window.addEventListener('mousedown', handleClick);
        return () => window.removeEventListener('mousedown', handleClick);
    }, [langDropdownOpen]);

    const toggleSelect = (id) => {
        setSelectedIds((prev) => {
            if (prev.includes(id)) return prev.filter((x) => x !== id);
            return [...prev, id];
        });
    };

    const filteredItems = useMemo(() => {
        return items.filter((q) => {
            if (langFilters.length > 0) {
                const qLangs = q.languages || [q.language];
                if (!qLangs.some(l => langFilters.includes(l))) return false;
            }
            if (diffFilter && q.difficulty !== diffFilter) return false;
            return true;
        });
    }, [items, langFilters, diffFilter]);

    const selectedItems = useMemo(() => items.filter((q) => selectedIds.includes(q.id)), [items, selectedIds]);

    const formatTime = (ms) => {
        const totalSeconds = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        if (hours > 0) return `${hours}h ${minutes}m`;
        return `${minutes}:${String(seconds).padStart(2, '0')}`;
    };

    return (
        <div className="coding-container">
            <Header />
            <div className="page-container">
                <div className="coding-header-row">
                    <div>
                        <h2 className="page-title">Coding Library</h2>
                        <div className="coding-muted">Manage and Create coding questions for your assessments.</div>
                    </div>
                    <div className="coding-header-actions">
                        <button type="button" className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }} onClick={() => navigate('/dashboard')}>
                            <ArrowLeft size={18} />
                            Back
                        </button>
                        <button type="button" className="btn coding-btn-refresh" onClick={load} disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <svg 
                                width="14" 
                                height="14" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                xmlns="http://www.w3.org/2000/svg" 
                                className={loading ? 'animate-spin' : ''}
                            >
                                <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                            Refresh
                        </button>
                        <button type="button" className="btn btn-primary" onClick={() => navigate('/coding/questions/new')} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Plus size={18} />
                            New Question
                        </button>
                    </div>
                </div>

                <div className="coding-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
                        <div>
                            <div className="coding-section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <CheckCircle size={20} color="var(--blue-accent)" />
                                Assessment Selection
                            </div>
                            <div className="coding-muted">
                                Select questions to bundle into a new technical assessment.
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <div className="coding-pill coding-pill-primary">
                                {selectedIds.length} questions selected
                            </div>
                            <button
                                type="button"
                                className="btn btn-primary"
                                disabled={selectedIds.length === 0}
                                onClick={() => {
                                    const inactiveQuestions = selectedItems.filter((q) => q.is_active === false);
                                    if (inactiveQuestions.length > 0) {
                                        setInactiveWarning(inactiveQuestions);
                                        return;
                                    }
                                    navigate('/coding/review', { state: { codingQuestions: selectedItems } });
                                }}
                                style={{ padding: '10px 24px', borderRadius: '12px' }}
                            >
                                Review & Create
                            </button>
                        </div>
                    </div>
                </div>

                <div className="coding-card" style={{ padding: '16px 24px' }}>
                    <div className="coding-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
                        <div className="coding-field coding-field-short">
                            <div className="coding-label" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Search size={16} /> Filter by Languages
                            </div>
                            <div className="coding-multiselect" ref={langDropdownRef}>
                                <button
                                    type="button"
                                    className="coding-multiselect-trigger"
                                    onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                                >
                                    <span>
                                        {langFilters.length === 0 ? 'All Languages' : `${langFilters.length} Selected`}
                                    </span>
                                    {langDropdownOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                                </button>
                                {langDropdownOpen && (
                                    <div className="coding-multiselect-menu">
                                        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                            {Array.from(new Set(items.flatMap(q => q.languages || [q.language]))).sort().map(lang => (
                                                <label key={lang} className="coding-checkbox-pill">
                                                    <input
                                                        type="checkbox"
                                                        checked={langFilters.includes(lang)}
                                                        onChange={() => {
                                                            setLangFilters(prev =>
                                                                prev.includes(lang) ? prev.filter(l => l !== lang) : [...prev, lang]
                                                            );
                                                        }}
                                                    />
                                                    <span style={{ fontSize: '14px' }}>{lang}</span>
                                                </label>
                                            ))}
                                        </div>
                                        <div style={{ borderTop: '1px solid #f1f5f9', marginTop: '12px', paddingTop: '12px', display: 'flex', gap: '8px' }}>
                                            <button className="btn btn-secondary" style={{ flex: 1, height: '36px', fontSize: '13px' }} onClick={() => setLangFilters([])}>Clear</button>
                                            <button className="btn btn-primary" style={{ flex: 1, height: '36px', fontSize: '13px' }} onClick={() => setLangDropdownOpen(false)}>Done</button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="coding-field coding-field-short">
                            <div className="coding-label" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <BarChart size={16} /> Filter by Difficulty
                            </div>
                            <select
                                className="coding-input"
                                style={{ height: '48px' }}
                                value={diffFilter}
                                onChange={(e) => setDiffFilter(e.target.value)}
                            >
                                <option value="">All Difficulties</option>
                                <option value="easy">Easy</option>
                                <option value="medium">Medium</option>
                                <option value="hard">Hard</option>
                            </select>
                        </div>
                    </div>
                </div>

                {loading ? (
                    <div className="coding-card" style={{ textAlign: 'center', padding: '60px' }}>
                        <RefreshCw size={40} className="animate-spin" style={{ color: 'var(--blue-accent)', marginBottom: '16px' }} />
                        <div className="coding-muted">Loading questions...</div>
                    </div>
                ) : error ? (
                    <div className="coding-card coding-error" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <AlertCircle size={24} />
                        {error}
                    </div>
                ) : filteredItems.length === 0 ? (
                    <div className="coding-card" style={{ textAlign: 'center', padding: '60px' }}>
                        <div className="coding-muted">No coding questions match your current filters.</div>
                        <button className="btn btn-secondary" style={{ marginTop: '16px' }} onClick={() => { setLangFilters([]); setDiffFilter(''); }}>
                            Clear All Filters
                        </button>
                    </div>
                ) : (
                    <div className="coding-list">
                        {filteredItems.map((q) => (
                            <div key={q.id} className="coding-item">
                                <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start', flex: 1 }}>
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.includes(q.id)}
                                        onChange={() => toggleSelect(q.id)}
                                        style={{ width: '20px', height: '20px', marginTop: '4px', cursor: 'pointer', accentColor: 'var(--blue-accent)' }}
                                    />
                                    <div>
                                        <div className="coding-item-title">
                                            {q.title}
                                            <span className={`coding-pill ${q.difficulty === 'easy' ? 'coding-pill-success' :
                                                q.difficulty === 'hard' ? 'coding-pill-danger' :
                                                    'coding-pill-muted'
                                                }`}>
                                                {q.difficulty}
                                            </span>
                                            {q.time_limit_ms != null && (
                                                <span className="coding-pill coding-pill-muted">
                                                    <Clock size={12} /> {formatTime(q.time_limit_ms)}
                                                </span>
                                            )}
                                        </div>
                                        <div className="coding-item-desc">{q.description || 'No description provided for this question.'}</div>
                                        <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                            {(q.languages || [q.language]).map(lang => (
                                                <span key={lang} style={{ fontSize: '11px', background: '#f8fafc', color: '#64748b', padding: '2px 8px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                                                    {lang}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                <div className="coding-item-actions">
                                    <Link className="btn btn-secondary" to={`/coding/questions/${q.id}/edit`} style={{ padding: '8px 16px', borderRadius: '8px' }}>
                                        Edit
                                    </Link>
                                    <Link className="btn btn-primary" to={`/coding/questions/${q.id}/attempt`} style={{ padding: '8px 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                        <Play size={14} fill="currentColor" />
                                        Open
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {inactiveWarning && (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(10, 25, 47, 0.6)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                    <div className="coding-card" style={{ maxWidth: '500px', width: '100%', maxHeight: '80vh', display: 'flex', flexDirection: 'column', padding: '32px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', color: '#dc2626' }}>
                            <AlertCircle size={28} />
                            <div className="coding-section-title" style={{ margin: 0, color: '#dc2626' }}>Inactive Questions</div>
                        </div>
                        <div className="coding-muted" style={{ marginBottom: '20px' }}>
                            You have selected some questions that are currently inactive. These cannot be used in a live assessment.
                        </div>
                        <div style={{ background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: '12px', padding: '16px', marginBottom: '24px', overflowY: 'auto', flex: 1 }}>
                            {inactiveWarning.map(q => (
                                <div key={q.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#991b1b', fontSize: '14px', fontWeight: 500 }}>
                                    • {q.title}
                                </div>
                            ))}
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                            <button className="btn btn-secondary" onClick={() => setInactiveWarning(null)}>Cancel</button>
                            <button className="btn btn-primary" style={{ background: '#dc2626', borderColor: '#dc2626' }} onClick={() => {
                                const activeItems = selectedItems.filter(q => q.is_active !== false);
                                setInactiveWarning(null);
                                navigate('/coding/review', { state: { codingQuestions: activeItems } });
                            }}>Proceed (Active Only)</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
