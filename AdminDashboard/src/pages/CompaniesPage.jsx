import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import FilterBar from '../components/FilterBar';
import Pagination from '../components/Pagination';
import CompanyDetailPanel from '../components/CompanyDetailPanel';

const STATUS_COLORS = {
    pending: { bg: 'rgba(255, 181, 71, 0.1)', text: '#FFB547', border: 'rgba(255, 181, 71, 0.2)' },
    approved: { bg: 'rgba(5, 205, 153, 0.1)', text: '#05CD99', border: 'rgba(5, 205, 153, 0.2)' },
    rejected: { bg: 'rgba(238, 93, 80, 0.1)', text: '#EE5D50', border: 'rgba(238, 93, 80, 0.2)' },
};

function StatusBadge({ status }) {
    const c = STATUS_COLORS[status] || { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
    return (
        <span style={{
            padding: '4px 12px', borderRadius: '999px', fontSize: '0.65rem',
            fontWeight: 800, letterSpacing: '0.05em', background: c.bg,
            color: c.text, border: `1px solid ${c.border}`, textTransform: 'uppercase',
        }}>
            {status}
        </span>
    );
}

function Toast({ message, type, onClose }) {
    useEffect(() => {
        const t = setTimeout(onClose, 4000);
        return () => clearTimeout(t);
    }, [onClose]);
    return (
        <div style={{
            position: 'fixed', bottom: 30, right: 30, zIndex: 9999,
            padding: '16px 24px', borderRadius: 16,
            background: type === 'success' ? '#05CD99' : '#EE5D50',
            color: '#fff', fontWeight: 600, fontSize: '0.85rem',
            boxShadow: '0 12px 30px rgba(0,0,0,0.15)',
            display: 'flex', alignItems: 'center', gap: 12,
            animation: 'slideIn 0.3s ease',
        }}>
            <span>{type === 'success' ? '✅' : '❌'}</span>
            {message}
        </div>
    );
}

function CompanyRow({ company, onClick }) {
    const admin = company.primary_admin;

    return (
        <div style={{
            background: '#fff', borderRadius: 20, padding: '24px',
            display: 'flex', alignItems: 'center', gap: '24px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: '0 4px 15px rgba(112, 144, 176, 0.08)',
            border: '1px solid #f0f3f8', cursor: 'pointer'
        }}
            onClick={onClick}
            onMouseEnter={e => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 10px 20px rgba(112, 144, 176, 0.12)';
            }}
            onMouseLeave={e => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(112, 144, 176, 0.08)';
            }}
        >
            <div style={{
                width: 56, height: 56, borderRadius: 16,
                background: company.approval_status === 'approved' ? 'rgba(5, 205, 153, 0.1)' : '#F4F7FE',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: company.approval_status === 'approved' ? '#05CD99' : '#2B3674',
                fontWeight: 800, fontSize: '1.4rem', flexShrink: 0,
                border: '1px solid rgba(0,0,0,0.03)'
            }}>
                {company.name.charAt(0).toUpperCase()}
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
                    <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#2B3674', letterSpacing: '-0.3px' }}>{company.name}</span>
                    <StatusBadge status={company.approval_status} />
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', color: '#707EAE', fontSize: '0.8rem', fontWeight: 500 }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>🌐 {company.domain || 'No domain'}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>✉️ {admin?.email || 'No admin email'}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>👥 {company.user_count || 0} employees</span>
                </div>
            </div>

            <div style={{ textAlign: 'right', borderLeft: '1px solid #f0f3f8', paddingLeft: 20 }}>
                <div style={{ fontSize: '0.65rem', color: '#A3AED0', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.8px' }}>Member Since</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#2B3674', marginTop: 2 }}>
                    {new Date(company.created_at).toLocaleDateString('en-US', { day: 'numeric', month: 'numeric', year: 'numeric' })}
                </div>
            </div>
        </div>
    );
}

function CompaniesPage() {
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [toast, setToast] = useState(null);

    // Selected company for drill-down
    const [selectedCompany, setSelectedCompany] = useState(null);

    // Filters & Pagination state
    const [statusFilter, setStatusFilter] = useState('');
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [sortBy, setSortBy] = useState('date');
    const [sortDir, setSortDir] = useState('desc');
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);

    const fetchCompanies = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const res = await axios.get(`${API_BASE_URL}/superadmin/companies/`);
            setCompanies(res.data.companies || []);
        } catch (err) {
            console.error('Failed to load companies:', err);
        } finally {
            if (!silent) setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchCompanies();
        const interval = setInterval(() => fetchCompanies(true), 30000);
        return () => clearInterval(interval);
    }, [fetchCompanies]);

    // Derived filtered data
    const getFilteredAndSorted = () => {
        let result = [...companies];

        if (search) {
            const s = search.toLowerCase();
            result = result.filter(c =>
                c.name.toLowerCase().includes(s) ||
                (c.primary_admin?.email || '').toLowerCase().includes(s) ||
                (c.domain || '').toLowerCase().includes(s)
            );
        }
        if (statusFilter) {
            result = result.filter(c => c.approval_status === statusFilter);
        }
        if (dateFrom) {
            const fd = new Date(dateFrom);
            result = result.filter(c => new Date(c.created_at) >= fd);
        }
        if (dateTo) {
            const td = new Date(dateTo);
            td.setHours(23, 59, 59, 999);
            result = result.filter(c => new Date(c.created_at) <= td);
        }

        result.sort((a, b) => {
            let cmp = 0;
            if (sortBy === 'name') cmp = a.name.localeCompare(b.name);
            else if (sortBy === 'users') cmp = (a.user_count || 0) - (b.user_count || 0);
            else cmp = new Date(a.created_at) - new Date(b.created_at); // default date
            
            return sortDir === 'asc' ? cmp : -cmp;
        });

        return result;
    };

    const filtered = getFilteredAndSorted();
    const paginated = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);

    // CSV Export
    const handleExportCSV = () => {
        if (filtered.length === 0) return;
        const headers = ['ID', 'Name', 'Domain', 'Status', 'Users', 'Admin Email', 'Created At'];
        const csvContent = [
            headers.join(','),
            ...filtered.map(c => [
                c.id,
                `"${c.name}"`,
                `"${c.domain || ''}"`,
                c.approval_status,
                c.user_count || 0,
                `"${c.primary_admin?.email || ''}"`,
                new Date(c.created_at).toISOString()
            ].join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `verifihire-companies-${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleApproveCompany = async (id) => {
        try {
            await axios.post(`${API_BASE_URL}/superadmin/companies/${id}/approve/`);
            setToast({ type: 'success', message: 'Company approved.' });
            fetchCompanies(true);
            if (selectedCompany?.id === id) {
                setSelectedCompany({ ...selectedCompany, approval_status: 'approved' });
            }
        } catch (err) {
            console.error('Company approval failed:', err);
            setToast({ type: 'error', message: 'Company approval failed.' });
        }
    };

    const handleRejectCompany = async (id, reason) => {
        try {
            await axios.post(`${API_BASE_URL}/superadmin/companies/${id}/reject/`, { reason });
            setToast({ type: 'success', message: 'Company rejected.' });
            fetchCompanies(true);
            if (selectedCompany?.id === id) {
                setSelectedCompany({ ...selectedCompany, approval_status: 'rejected', rejected_reason: reason });
            }
        } catch (err) {
            console.error('Rejection failed:', err);
            setToast({ type: 'error', message: 'Rejection failed.' });
        }
    };

    return (
        <div style={{ animation: 'slideIn 0.4s ease-out' }}>
            <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800, color: '#2B3674', letterSpacing: '-0.5px' }}>
                        Enterprise Directory
                    </h1>
                    <p style={{ margin: '6px 0 0', color: '#707EAE', fontSize: '0.9rem', fontWeight: 500 }}>
                        Manage and approve organization workspaces. Total: <span style={{ color: '#4318FF', fontWeight: 700 }}>{companies.length}</span>
                    </p>
                </div>

                <div style={{ position: 'relative' }}>
                    <span style={{
                        position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)',
                        fontSize: '1rem', color: '#A3AED0',
                    }}>🔍</span>
                    <input
                        type="text" placeholder="Search workspaces..."
                        value={search} onChange={e => { setSearch(e.target.value); setCurrentPage(1); }}
                        style={{
                            padding: '14px 20px 14px 48px', borderRadius: '16px',
                            border: '1px solid #f0f3f8', fontSize: '0.9rem', outline: 'none',
                            width: 340, background: '#fff', boxShadow: '0 4px 15px rgba(0,0,0,0.03)',
                            color: '#2B3674', fontWeight: 600
                        }}
                    />
                </div>
            </div>

            <FilterBar
                statusOptions={[{label:'Pending',value:'pending'},{label:'Approved',value:'approved'},{label:'Rejected',value:'rejected'}]}
                statusValue={statusFilter} onStatusChange={v => { setStatusFilter(v); setCurrentPage(1); }}
                dateFrom={dateFrom} dateTo={dateTo}
                onDateFromChange={v => { setDateFrom(v); setCurrentPage(1); }}
                onDateToChange={v => { setDateTo(v); setCurrentPage(1); }}
                sortOptions={[{label:'Name',value:'name'},{label:'User Count',value:'users'}]}
                sortValue={sortBy} onSortChange={v => { setSortBy(v); setCurrentPage(1); }}
                sortDirection={sortDir} onSortDirectionChange={setSortDir}
                onReset={() => { setStatusFilter(''); setDateFrom(''); setDateTo(''); setSortBy('date'); setSortDir('desc'); setSearch(''); setCurrentPage(1); }}
                onExportCSV={handleExportCSV}
            />

            {loading ? (
                <div style={{ textAlign: 'center', padding: '6rem' }}>
                    <div className="spinner" style={{
                        width: 48, height: 48, border: '4px solid #f3f3f3',
                        borderTop: '4px solid #4318FF', borderRadius: '50%',
                        margin: '0 auto 16px', animation: 'spin 1.5s linear infinite'
                    }} />
                    <span style={{ fontWeight: 700, fontSize: '1rem', color: '#A3AED0', letterSpacing: '1px' }}>SYNCHRONIZING DIRECTORY...</span>
                </div>
            ) : filtered.length === 0 ? (
                <div style={{
                    textAlign: 'center', padding: '6rem', background: '#fff', borderRadius: 32,
                    boxShadow: '0 20px 40px rgba(112, 144, 176, 0.08)', color: '#A3AED0'
                }}>
                    <div style={{ fontSize: '5rem', marginBottom: 24 }}>🏢</div>
                    <div style={{ fontWeight: 800, fontSize: '1.4rem', color: '#2B3674' }}>No Organizations Found</div>
                </div>
            ) : (
                <>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                        {paginated.map(company => (
                            <CompanyRow 
                                key={company.id} 
                                company={company} 
                                onClick={() => setSelectedCompany(company)}
                            />
                        ))}
                    </div>
                    
                    <Pagination
                        currentPage={currentPage}
                        totalItems={filtered.length}
                        pageSize={pageSize}
                        onPageChange={setCurrentPage}
                        onPageSizeChange={setPageSize}
                    />
                </>
            )}

            {selectedCompany && (
                <CompanyDetailPanel
                    company={selectedCompany}
                    onClose={() => setSelectedCompany(null)}
                    onApprove={handleApproveCompany}
                    onReject={handleRejectCompany}
                />
            )}

            {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
            `}</style>
        </div>
    );
}

export default CompaniesPage;
