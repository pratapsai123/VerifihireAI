import React, { useState } from 'react';

function FilterBar({
    // Status filter
    statusOptions = [],
    statusValue = '',
    onStatusChange,
    // Date range
    showDateRange = true,
    dateFrom = '',
    dateTo = '',
    onDateFromChange,
    onDateToChange,
    // Role filter
    roleOptions = [],
    roleValue = '',
    onRoleChange,
    // Sort
    sortOptions = [],
    sortValue = '',
    onSortChange,
    sortDirection = 'desc',
    onSortDirectionChange,
    // Reset
    onReset,
    // CSV Export
    onExportCSV,
    // Bulk actions
    selectedCount = 0,
    onBulkApprove,
    onBulkReject,
}) {
    const [expanded, setExpanded] = useState(false);
    const hasFilters = statusValue || dateFrom || dateTo || roleValue || sortValue;

    return (
        <div style={{ marginBottom: '1.5rem' }}>
            {/* Bulk Action Bar */}
            {selectedCount > 0 && (
                <div style={{
                    background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
                    borderRadius: 16, padding: '14px 20px',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    marginBottom: 12, animation: 'slideIn 0.3s ease',
                    boxShadow: '0 8px 24px rgba(79, 70, 229, 0.3)',
                }}>
                    <span style={{ color: '#fff', fontWeight: 700, fontSize: '0.85rem' }}>
                        ✓ {selectedCount} item{selectedCount > 1 ? 's' : ''} selected
                    </span>
                    <div style={{ display: 'flex', gap: 10 }}>
                        {onBulkApprove && (
                            <button onClick={onBulkApprove} style={{
                                padding: '8px 18px', borderRadius: 10, border: 'none',
                                background: '#05CD99', color: '#fff', fontWeight: 700,
                                fontSize: '0.78rem', cursor: 'pointer',
                            }}>✅ Approve All ({selectedCount})</button>
                        )}
                        {onBulkReject && (
                            <button onClick={onBulkReject} style={{
                                padding: '8px 18px', borderRadius: 10,
                                border: '1.5px solid rgba(255,255,255,0.4)', background: 'transparent',
                                color: '#fff', fontWeight: 700, fontSize: '0.78rem', cursor: 'pointer',
                            }}>❌ Reject All ({selectedCount})</button>
                        )}
                    </div>
                </div>
            )}

            {/* Filter Bar */}
            <div style={{
                background: '#fff', borderRadius: 16, padding: '12px 16px',
                border: '1px solid #f0f3f8',
                boxShadow: '0 4px 12px rgba(112, 144, 176, 0.04)',
            }}>
                {/* Row 1: Toggle + Quick Actions */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
                    <button
                        onClick={() => setExpanded(!expanded)}
                        style={{
                            display: 'flex', alignItems: 'center', gap: 8,
                            padding: '8px 14px', borderRadius: 10, border: '1px solid #e9edf7',
                            background: expanded ? '#F4F7FE' : 'transparent',
                            cursor: 'pointer', fontWeight: 700, fontSize: '0.78rem',
                            color: 'var(--text-main)', transition: 'all 0.2s ease',
                        }}
                    >
                        <span style={{ transition: 'transform 0.2s ease', transform: expanded ? 'rotate(180deg)' : 'rotate(0)' }}>🔽</span>
                        Filters {hasFilters && <span style={{
                            width: 6, height: 6, borderRadius: '50%', background: '#4F46E5',
                        }} />}
                    </button>

                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        {/* Status Quick Tabs */}
                        {statusOptions.length > 0 && (
                            <div style={{ display: 'flex', gap: 4, background: '#F4F7FE', borderRadius: 10, padding: 3 }}>
                                {statusOptions.map(opt => (
                                    <button key={opt.value} onClick={() => onStatusChange(opt.value)} style={{
                                        padding: '6px 14px', borderRadius: 8, border: 'none',
                                        background: statusValue === opt.value ? '#4F46E5' : 'transparent',
                                        color: statusValue === opt.value ? '#fff' : 'var(--text-secondary)',
                                        fontWeight: 700, fontSize: '0.72rem', cursor: 'pointer',
                                        transition: 'all 0.2s ease',
                                    }}>{opt.label}</button>
                                ))}
                            </div>
                        )}

                        {hasFilters && (
                            <button onClick={onReset} style={{
                                padding: '6px 12px', borderRadius: 8, border: '1px solid #fee2e2',
                                background: 'transparent', color: '#EE5D50', fontWeight: 700,
                                fontSize: '0.72rem', cursor: 'pointer',
                            }}>✕ Reset</button>
                        )}

                        {onExportCSV && (
                            <button onClick={onExportCSV} style={{
                                padding: '8px 16px', borderRadius: 10, border: '1px solid #e9edf7',
                                background: 'transparent', fontWeight: 700, fontSize: '0.75rem',
                                cursor: 'pointer', color: 'var(--text-main)',
                                display: 'flex', alignItems: 'center', gap: 6,
                                transition: 'all 0.2s ease',
                            }}
                                onMouseEnter={e => { e.currentTarget.style.background = '#F4F7FE'; }}
                                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                            >📥 Export CSV</button>
                        )}
                    </div>
                </div>

                {/* Row 2: Expanded Filters */}
                {expanded && (
                    <div style={{
                        display: 'flex', gap: 12, marginTop: 14, paddingTop: 14,
                        borderTop: '1px solid #f0f3f8', flexWrap: 'wrap',
                        animation: 'slideIn 0.2s ease',
                    }}>
                        {showDateRange && (
                            <>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                    <label style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>From</label>
                                    <input type="date" value={dateFrom} onChange={e => onDateFromChange(e.target.value)} style={{
                                        padding: '8px 12px', borderRadius: 8, border: '1px solid #e9edf7',
                                        fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)',
                                        outline: 'none', background: '#F4F7FE',
                                    }} />
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                    <label style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>To</label>
                                    <input type="date" value={dateTo} onChange={e => onDateToChange(e.target.value)} style={{
                                        padding: '8px 12px', borderRadius: 8, border: '1px solid #e9edf7',
                                        fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)',
                                        outline: 'none', background: '#F4F7FE',
                                    }} />
                                </div>
                            </>
                        )}

                        {roleOptions.length > 0 && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                <label style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Role</label>
                                <select value={roleValue} onChange={e => onRoleChange(e.target.value)} style={{
                                    padding: '8px 12px', borderRadius: 8, border: '1px solid #e9edf7',
                                    fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)',
                                    outline: 'none', background: '#F4F7FE', cursor: 'pointer',
                                }}>
                                    <option value="">All Roles</option>
                                    {roleOptions.map(r => (
                                        <option key={r.value} value={r.value}>{r.label}</option>
                                    ))}
                                </select>
                            </div>
                        )}

                        {sortOptions.length > 0 && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                <label style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Sort By</label>
                                <div style={{ display: 'flex', gap: 4 }}>
                                    <select value={sortValue} onChange={e => onSortChange(e.target.value)} style={{
                                        padding: '8px 12px', borderRadius: 8, border: '1px solid #e9edf7',
                                        fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)',
                                        outline: 'none', background: '#F4F7FE', cursor: 'pointer',
                                    }}>
                                        <option value="">Default</option>
                                        {sortOptions.map(s => (
                                            <option key={s.value} value={s.value}>{s.label}</option>
                                        ))}
                                    </select>
                                    <button onClick={() => onSortDirectionChange(sortDirection === 'asc' ? 'desc' : 'asc')} style={{
                                        padding: '8px 10px', borderRadius: 8, border: '1px solid #e9edf7',
                                        background: '#F4F7FE', cursor: 'pointer', fontSize: '0.8rem',
                                    }}>
                                        {sortDirection === 'asc' ? '↑' : '↓'}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <style>{`
                @keyframes slideIn { from { transform: translateY(-8px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `}</style>
        </div>
    );
}

export default FilterBar;
