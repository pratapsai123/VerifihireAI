import React, { useState, useEffect, useMemo, useRef } from 'react';
import axios from 'axios';
import '../styles/Coding.css'; // Reusing existing styles for consistency
import { API_BASE_URL } from '../apiConfig';

export default function CodingQuestionSelector({ onClose, onAdd, alreadySelectedIds = [] }) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [items, setItems] = useState([]);
    const [selectedIds, setSelectedIds] = useState([]);

    // Filters
    const [langFilters, setLangFilters] = useState([]);
    const [diffFilter, setDiffFilter] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    const [langDropdownOpen, setLangDropdownOpen] = useState(false);
    const langDropdownRef = useRef(null);

    useEffect(() => {
        loadQuestions();
    }, []);

    const loadQuestions = async () => {
        setLoading(true);
        setError('');
        try {
            const resp = await axios.get(`${API_BASE_URL}/coding/questions/`);
            setItems(resp.data?.results || []);
        } catch (e) {
            setError(e?.response?.data?.error || e?.message || 'Failed to load coding questions');
        } finally {
            setLoading(false);
        }
    };

    // Close dropdown on click outside
    useEffect(() => {
        if (!langDropdownOpen) return;
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
            // Exclude already selected in the parent page (optional, but good UX)
            if (alreadySelectedIds.includes(q.id)) return false;

            // Exclude inactive questions
            if (q.is_active === false || q.status === 'inactive') return false;

            // Search Filter
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                if (!q.title?.toLowerCase().includes(query) && !q.description?.toLowerCase().includes(query)) {
                    return false;
                }
            }

            // Language filter
            if (langFilters.length > 0) {
                const qLangs = q.languages || [q.language];
                if (!qLangs.some(l => langFilters.includes(l))) return false;
            }

            // Difficulty filter
            if (diffFilter && q.difficulty !== diffFilter) return false;

            return true;
        });
    }, [items, langFilters, diffFilter, searchQuery, alreadySelectedIds]);

    const handleAdd = () => {
        const selectedQuestions = items.filter(q => selectedIds.includes(q.id));
        onAdd(selectedQuestions);
    };

    const formatTime = (ms) => {
        const totalSeconds = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes}:${String(seconds).padStart(2, '0')}`;
    };

    // Unique languages for filter
    const allLanguages = useMemo(() => {
        const langs = new Set();
        items.forEach(q => {
            (q.languages || [q.language]).forEach(l => {
                if (l) langs.add(l);
            });
        });
        return Array.from(langs).sort();
    }, [items]);

    return (
        <div className="coding-selector-overlay" style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000
        }}>
            <div className="coding-selector-modal" style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                width: '90%',
                maxWidth: '900px',
                height: '85vh',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}>
                {/* Header */}
                <div style={{ padding: '16px 24px', borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, fontSize: '1.25rem' }}>Select Coding Questions</h3>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}>&times;</button>
                </div>

                {/* Filters */}
                <div style={{ padding: '16px 24px', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: '16px', flexWrap: 'wrap', backgroundColor: '#f9fafb' }}>
                    {/* Search */}
                    <div style={{ flex: '1 1 200px' }}>
                        <input
                            type="text"
                            placeholder="Search questions..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{ width: '100%', padding: '8px 12px', borderRadius: '4px', border: '1px solid #d1d5db' }}
                        />
                    </div>

                    {/* Language Filter */}
                    <div style={{ position: 'relative', width: '200px' }} ref={langDropdownRef}>
                        <button
                            type="button"
                            onClick={() => setLangDropdownOpen(!langDropdownOpen)}
                            style={{ width: '100%', padding: '8px 12px', borderRadius: '4px', border: '1px solid #d1d5db', background: 'white', textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                        >
                            <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {langFilters.length === 0 ? 'All Languages' : `${langFilters.length} Selected`}
                            </span>
                            <span>{langDropdownOpen ? '▴' : '▾'}</span>
                        </button>
                        {langDropdownOpen && (
                            <div style={{ position: 'absolute', top: '100%', left: 0, right: 0, maxHeight: '300px', overflowY: 'auto', backgroundColor: 'white', border: '1px solid #d1d5db', borderRadius: '4px', marginTop: '4px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', zIndex: 10 }}>
                                <div style={{ padding: '8px' }}>
                                    {allLanguages.map(lang => (
                                        <label key={lang} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px', cursor: 'pointer', borderRadius: '4px' }} className="hover:bg-gray-100">
                                            <input
                                                type="checkbox"
                                                checked={langFilters.includes(lang)}
                                                onChange={() => {
                                                    setLangFilters(prev =>
                                                        prev.includes(lang) ? prev.filter(l => l !== lang) : [...prev, lang]
                                                    );
                                                }}
                                            />
                                            <span>{lang}</span>
                                        </label>
                                    ))}
                                    {allLanguages.length === 0 && <div style={{ padding: '8px', color: '#6b7280' }}>No languages found</div>}
                                </div>
                                <div style={{ borderTop: '1px solid #e5e7eb', padding: '8px', display: 'flex', gap: '8px' }}>
                                    <button onClick={() => setLangFilters([])} style={{ flex: 1, padding: '6px', border: '1px solid #d1d5db', background: 'white', borderRadius: '4px', cursor: 'pointer' }}>Clear</button>
                                    <button onClick={() => setLangDropdownOpen(false)} style={{ flex: 1, padding: '6px', border: 'none', background: '#3b82f6', color: 'white', borderRadius: '4px', cursor: 'pointer' }}>Done</button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Difficulty Filter */}
                    <select
                        value={diffFilter}
                        onChange={(e) => setDiffFilter(e.target.value)}
                        style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #d1d5db', width: '150px' }}
                    >
                        <option value="">All Difficulties</option>
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                    </select>
                </div>

                {/* List */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '16px 24px' }}>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
                    ) : error ? (
                        <div style={{ color: 'red', textAlign: 'center', padding: '40px' }}>{error}</div>
                    ) : filteredItems.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>No questions match your filters.</div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {filteredItems.map(q => (
                                <div key={q.id} style={{
                                    border: '1px solid #e5e7eb',
                                    borderRadius: '8px',
                                    padding: '16px',
                                    display: 'flex',
                                    gap: '16px',
                                    alignItems: 'flex-start',
                                    cursor: 'pointer',
                                    backgroundColor: selectedIds.includes(q.id) ? '#eff6ff' : 'white',
                                    borderColor: selectedIds.includes(q.id) ? '#bfdbfe' : '#e5e7eb'
                                }} onClick={() => toggleSelect(q.id)}>
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.includes(q.id)}
                                        onChange={() => toggleSelect(q.id)}
                                        style={{ marginTop: '4px', cursor: 'pointer' }}
                                    />
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <div style={{ fontWeight: 600 }}>{q.title}</div>
                                            <div style={{ display: 'flex', gap: '8px' }}>
                                                {q.difficulty && (
                                                    <span style={{
                                                        fontSize: '0.75rem',
                                                        padding: '2px 8px',
                                                        borderRadius: '999px',
                                                        textTransform: 'capitalize',
                                                        backgroundColor: q.difficulty === 'easy' ? '#dcfce7' : q.difficulty === 'hard' ? '#fee2e2' : '#f3f4f6',
                                                        color: q.difficulty === 'easy' ? '#166534' : q.difficulty === 'hard' ? '#991b1b' : '#374151'
                                                    }}>
                                                        {q.difficulty}
                                                    </span>
                                                )}
                                                {q.time_limit_ms != null && (
                                                    <span style={{ fontSize: '0.75rem', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                        ⏱ {formatTime(q.time_limit_ms)}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        <div style={{ fontSize: '0.875rem', color: '#4b5563', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                            {q.description || 'No description provided.'}
                                        </div>
                                        <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
                                            {(q.languages || [q.language]).map(l => (
                                                <span key={l} style={{ fontSize: '0.75rem', backgroundColor: '#e5e7eb', padding: '2px 6px', borderRadius: '4px' }}>
                                                    {l}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div style={{ padding: '16px 24px', borderTop: '1px solid #e5e7eb', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                    <button onClick={onClose} style={{ padding: '8px 16px', borderRadius: '4px', border: '1px solid #d1d5db', background: 'white', cursor: 'pointer' }}>Cancel</button>
                    <button
                        onClick={handleAdd}
                        disabled={selectedIds.length === 0}
                        style={{
                            padding: '8px 16px',
                            borderRadius: '4px',
                            border: 'none',
                            background: selectedIds.length === 0 ? '#9ca3af' : '#2563eb',
                            color: 'white',
                            cursor: selectedIds.length === 0 ? 'not-allowed' : 'pointer'
                        }}
                    >
                        Add Selected ({selectedIds.length})
                    </button>
                </div>
            </div>
        </div>
    );
}
