import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/Coding.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

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

            // Fallback: If we filtered by org and got nothing, try fetching all public/allowed questions
            // This fixes issues where the user's stored org name might be stale or slightly mismatched
            if (results.length === 0 && orgName) {
                try {
                    const fallbackResp = await axios.get(`${API_BASE_URL}/coding/questions/`);
                    if ((fallbackResp.data?.results || []).length > 0) {
                        results = fallbackResp.data?.results || [];
                    }
                } catch (ignore) {
                    // If fallback fails, just stick with the empty results from the first call
                }
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
            // Language filter: if any of the question's languages match selected filters
            // Or if the primary language matches
            if (langFilters.length > 0) {
                const qLangs = q.languages || [q.language];
                if (!qLangs.some(l => langFilters.includes(l))) return false;
            }
            // Difficulty filter
            if (diffFilter && q.difficulty !== diffFilter) return false;
            return true;
        });
    }, [items, langFilters, diffFilter]);

    const selectedItems = useMemo(() => filteredItems.filter((q) => selectedIds.includes(q.id)), [filteredItems, selectedIds]);

    const formatTime = (ms) => {
        const totalSeconds = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        return [hours, minutes, seconds].map((v) => String(v).padStart(2, '0')).join(':');
    };

    return (
        <div className="coding-container">
            <Header />
            <div className="page-container">
                <div className="coding-header-row">
                    <div>
                        <h2 className="page-title">Coding</h2>
                    </div>
                    <div className="coding-header-actions">
                        <button type="button" className="btn btn-secondary" onClick={load} disabled={loading}>
                            Refresh
                        </button>
                        <button type="button" className="btn btn-primary" onClick={() => navigate('/coding/questions/new')}>
                            + New Question
                        </button>
                    </div>
                </div>

                <div className="coding-card" style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div className="coding-section-title" style={{ marginBottom: '4px' }}>Selection</div>
                            <div className="coding-muted">
                                Choose one or more coding questions, then review and create an assessment.
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <div className="coding-pill coding-pill-primary">{selectedItems.length} selected</div>
                            <button
                                type="button"
                                className="btn btn-primary"
                                disabled={selectedItems.length === 0}
                                onClick={() => navigate('/coding/review', { state: { codingQuestions: selectedItems } })}
                            >
                                Review Selected
                            </button>
                        </div>
                    </div>
                </div>

                <div className="coding-card" style={{ marginBottom: '16px' }}>
                    <div className="coding-form-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                        <div className="coding-field">
                            <div className="coding-label">Filter by Languages</div>
                            <div className="coding-multiselect" style={{ width: '100%' }} ref={langDropdownRef}>
                                <button
                                    type="button"
                                    className="btn btn-secondary coding-multiselect-trigger"
                                    style={{ width: '100%', textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                                    onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                                >
                                    <span>
                                        {langFilters.length === 0
                                            ? 'All Languages'
                                            : `${langFilters.length} Selected`}
                                    </span>
                                    <span>{langDropdownOpen ? '▴' : '▾'}</span>
                                </button>
                                {langDropdownOpen && (
                                    <div className="coding-multiselect-menu" style={{ width: '100%', maxHeight: '300px', overflowY: 'auto' }}>
                                        {Array.from(new Set(items.flatMap(q => q.languages || [q.language]))).sort().map(lang => (
                                            <label key={lang} className="coding-checkbox-pill" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 8px', cursor: 'pointer' }}>
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
                                        {items.length > 0 && (
                                            <div style={{ borderTop: '1px solid #eee', marginTop: '12px', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
                                                <button className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '14px', flex: 1 }} onClick={() => setLangFilters([])}>Clear</button>
                                                <button className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '14px', flex: 1 }} onClick={() => setLangDropdownOpen(false)}>Done</button>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="coding-field">
                            <div className="coding-label">Filter by Difficulty</div>
                            <select
                                className="coding-input"
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
                    <div className="coding-card">Loading…</div>
                ) : error ? (
                    <div className="coding-card coding-error">{error}</div>
                ) : filteredItems.length === 0 ? (
                    <div className="coding-card">No coding questions match your filters.</div>
                ) : (
                    <div className="coding-list">
                        {filteredItems.map((q) => (
                            <div key={q.id} className="coding-item">
                                <div className="coding-item-main" style={{ display: 'flex', gap: '12px' }}>
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.includes(q.id)}
                                        onChange={() => toggleSelect(q.id)}
                                        style={{ marginTop: '6px' }}
                                    />
                                    <div>
                                        <div className="coding-item-title">
                                            {q.title}{' '}
                                            <span className={`coding-pill ${q.difficulty === 'easy' ? 'coding-pill-success' :
                                                q.difficulty === 'hard' ? 'coding-pill-danger' :
                                                    'coding-pill-muted'
                                                }`} style={{
                                                    textTransform: 'capitalize',
                                                    backgroundColor: q.difficulty === 'easy' ? '#dcfce7' : q.difficulty === 'hard' ? '#fee2e2' : '#f3f4f6',
                                                    color: q.difficulty === 'easy' ? '#166534' : q.difficulty === 'hard' ? '#991b1b' : '#374151',
                                                    borderColor: q.difficulty === 'easy' ? '#bbf7d0' : q.difficulty === 'hard' ? '#fecaca' : '#e5e7eb'
                                                }}>
                                                {q.difficulty}
                                            </span>
                                            {q.time_limit_ms != null && (
                                                <span className="coding-pill coding-pill-muted">⏱ {formatTime(q.time_limit_ms)}</span>
                                            )}
                                        </div>
                                        <div className="coding-item-desc">{q.description || '—'}</div>
                                    </div>
                                </div>
                                <div className="coding-item-actions">
                                    <Link className="btn btn-secondary" to={`/coding/questions/${q.id}/edit`}>
                                        Edit
                                    </Link>
                                    <Link className="btn btn-primary" to={`/coding/questions/${q.id}/attempt`}>
                                        Open
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}



