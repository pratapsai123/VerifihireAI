import React from 'react';

function Pagination({
    currentPage,
    totalItems,
    pageSize,
    onPageChange,
    onPageSizeChange,
    pageSizeOptions = [10, 25, 50, 100]
}) {
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
    const startIndex = (currentPage - 1) * pageSize + 1;
    const endIndex = Math.min(startIndex + pageSize - 1, totalItems);

    if (totalItems === 0) return null;

    // Generate page numbers
    const getPageNumbers = () => {
        const pages = [];
        const maxVisible = 5;
        
        if (totalPages <= maxVisible) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            if (currentPage <= 3) {
                for (let i = 1; i <= 4; i++) pages.push(i);
                pages.push('...');
                pages.push(totalPages);
            } else if (currentPage >= totalPages - 2) {
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
            } else {
                pages.push(1);
                pages.push('...');
                pages.push(currentPage - 1);
                pages.push(currentPage);
                pages.push(currentPage + 1);
                pages.push('...');
                pages.push(totalPages);
            }
        }
        return pages;
    };

    return (
        <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '16px 20px', background: '#fff', borderRadius: 16,
            border: '1px solid #f0f3f8', marginTop: '1.5rem',
            boxShadow: '0 4px 12px rgba(112, 144, 176, 0.04)',
            flexWrap: 'wrap', gap: 16,
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                    Showing <span style={{ color: 'var(--text-main)', fontWeight: 800 }}>{startIndex}</span> to <span style={{ color: 'var(--text-main)', fontWeight: 800 }}>{endIndex}</span> of <span style={{ color: 'var(--text-main)', fontWeight: 800 }}>{totalItems}</span> results
                </span>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Items per page:</span>
                    <select
                        value={pageSize}
                        onChange={(e) => {
                            onPageSizeChange(Number(e.target.value));
                            onPageChange(1);
                        }}
                        style={{
                            padding: '4px 8px', borderRadius: 8, border: '1px solid #e9edf7',
                            background: '#F4F7FE', outline: 'none', cursor: 'pointer',
                            fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-main)',
                        }}
                    >
                        {pageSizeOptions.map(opt => (
                            <option key={opt} value={opt}>{opt}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <button
                    disabled={currentPage === 1}
                    onClick={() => onPageChange(currentPage - 1)}
                    style={{
                        width: 32, height: 32, borderRadius: 8, border: '1px solid #e9edf7',
                        background: currentPage === 1 ? '#f8fafc' : '#fff',
                        color: currentPage === 1 ? '#cbd5e1' : 'var(--text-main)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s ease', fontWeight: 700, fontSize: '0.8rem',
                    }}
                >
                    &lt;
                </button>
                
                {getPageNumbers().map((num, i) => (
                    num === '...' ? (
                        <span key={`dots-${i}`} style={{ padding: '0 4px', color: 'var(--text-secondary)', fontWeight: 700 }}>...</span>
                    ) : (
                        <button
                            key={num}
                            onClick={() => onPageChange(num)}
                            style={{
                                width: 32, height: 32, borderRadius: 8, border: 'none',
                                background: currentPage === num ? '#4F46E5' : 'transparent',
                                color: currentPage === num ? '#fff' : 'var(--text-secondary)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                cursor: 'pointer', transition: 'all 0.2s ease',
                                fontWeight: 700, fontSize: '0.8rem',
                            }}
                            onMouseEnter={e => { if (currentPage !== num) e.currentTarget.style.background = '#F4F7FE'; }}
                            onMouseLeave={e => { if (currentPage !== num) e.currentTarget.style.background = 'transparent'; }}
                        >
                            {num}
                        </button>
                    )
                ))}

                <button
                    disabled={currentPage === totalPages}
                    onClick={() => onPageChange(currentPage + 1)}
                    style={{
                        width: 32, height: 32, borderRadius: 8, border: '1px solid #e9edf7',
                        background: currentPage === totalPages ? '#f8fafc' : '#fff',
                        color: currentPage === totalPages ? '#cbd5e1' : 'var(--text-main)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                        transition: 'all 0.2s ease', fontWeight: 700, fontSize: '0.8rem',
                    }}
                >
                    &gt;
                </button>
            </div>
        </div>
    );
}

export default Pagination;
