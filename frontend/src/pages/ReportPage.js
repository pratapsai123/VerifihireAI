import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Download, ArrowLeft, Loader2, AlertCircle, ShieldCheck, ShieldAlert } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import '../styles/ReportPage.css';

export default function ReportPage() {
    const { submissionId } = useParams();
    const navigate = useNavigate();
    
    // Derive user role from localStorage
    const currentUser = (() => { try { return JSON.parse(localStorage.getItem('user') || '{}'); } catch { return {}; } })();
    const currentRole = (currentUser?.role || '').toLowerCase();
    const isAdmin = currentRole === 'company_admin' || currentRole === 'application_admin';
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pdfUrl, setPdfUrl] = useState(null);
    const [downloading, setDownloading] = useState(false);
    
    const [candidateName, setCandidateName] = useState('');
    const [assessmentName, setAssessmentName] = useState('');

    // Identity mismatch / approval state
    const [candidateRow, setCandidateRow] = useState(null);
    const [approveModalOpen, setApproveModalOpen] = useState(false);
    const [approvalReason, setApprovalReason] = useState('');
    const [approving, setApproving] = useState(false);

    const loadReportAndDetails = useCallback(async (silent = false) => {
        if (!silent) {
            setLoading(true);
            setError(null);
        }

        try {
            // 1. Fetch detailed result metadata directly for this submission
            try {
                const detailResp = await axios.get(`${API_BASE_URL}/results/${submissionId}/detail/`);
                const match = detailResp.data;
                if (match) {
                    setCandidateName(match.candidate?.name || '');
                    setAssessmentName(match.assessment?.display_name || match.assessment?.name || 'Assessment');
                    setCandidateRow(match);
                }
            } catch (detailsErr) {
                console.warn('Could not load candidate metadata:', detailsErr);
            }

            if (!silent) {
                // 2. Fetch PDF blob securely (passes JWT token in headers)
                const isAi = String(submissionId).startsWith('ai_');
                const reportUrl = isAi
                    ? `${API_BASE_URL}/ai/submission/${String(submissionId).replace('ai_', '')}/download-report/`
                    : `${API_BASE_URL}/results/${submissionId}/report/`;
                const response = await axios.get(reportUrl, { responseType: 'blob' });

                const blob = new Blob([response.data], { type: 'application/pdf' });
                const localPdfUrl = window.URL.createObjectURL(blob);
                setPdfUrl(prev => {
                    if (prev) window.URL.revokeObjectURL(prev);
                    return localPdfUrl;
                });

                // Try parsing candidate name from Content-Disposition if not already resolved
                if (!candidateName) {
                    const contentDisposition = response.headers['content-disposition'];
                    if (contentDisposition) {
                        const matchName = contentDisposition.match(/filename="Report_(.+)\.pdf"/);
                        if (matchName?.[1]) {
                            setCandidateName(matchName[1].replace(/_/g, ' '));
                        }
                    }
                }
            }
        } catch (err) {
            console.error('Failed to load PDF report:', err);
            if (!silent) {
                setError(err.response?.data?.error || err.message || 'Failed to load candidate report.');
            }
        } finally {
            if (!silent) setLoading(false);
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [submissionId]);

    useEffect(() => {
        let active = true;

        const run = async () => {
            if (!active) return;
            await loadReportAndDetails(false);
        };

        run();

        return () => {
            active = false;
            setPdfUrl(prev => {
                if (prev) window.URL.revokeObjectURL(prev);
                return null;
            });
        };
    }, [loadReportAndDetails]);

    const handleDownload = () => {
        if (downloading || !pdfUrl) return;
        setDownloading(true);
        try {
            const link = document.createElement('a');
            link.href = pdfUrl;
            const cleanName = candidateName ? candidateName.replace(/\s+/g, '_') : `Candidate_${submissionId}`;
            link.setAttribute('download', `Report_${cleanName}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Failed to trigger local PDF download:', err);
            alert('Failed to download report.');
        } finally {
            setDownloading(false);
        }
    };

    const handleApprove = async () => {
        if (!isAdmin && !approvalReason.trim()) {
            alert('Please provide an approval reason for the audit trail.');
            return;
        }
        setApproving(true);
        try {
            const tokenVal = localStorage.getItem('token');
            const config = tokenVal ? { headers: { Authorization: `Bearer ${tokenVal}` } } : {};
            const resp = await axios.post(
                `${API_BASE_URL}/results/${submissionId}/request-photo-update/`,
                { reason: approvalReason.trim() },
                config
            );

            alert(resp.data.message || 'Identity manual review request submitted to Admin successfully.');

            const newStatus = resp.data?.photo_update_status || (isAdmin ? 'approved' : 'pending');
            setCandidateRow(prev => prev ? {
                ...prev,
                photo_update_status: newStatus,
                photo_update_reason: approvalReason.trim(),
                photo_update_approved: newStatus === 'approved',
                photo_update_approved_by: newStatus === 'approved' ? 'Company Admin' : prev.photo_update_approved_by
            } : prev);

            setApproveModalOpen(false);
            setApprovalReason('');

            await loadReportAndDetails(false);
        } catch (err) {
            alert(err.response?.data?.error || err.message || 'Failed to submit approval request.');
        } finally {
            setApproving(false);
        }
    };

    const hasMismatch = candidateRow?.identity_mismatch_detected === true || candidateRow?.identity_mismatch === true;
    const isApproved = candidateRow?.photo_update_approved === true;

    return (
        <div className="report-page-container">
            
            {/* Glassmorphic control bar */}
            <div className="report-control-bar">
                <div className="report-bar-left">
                    <button 
                        className="btn-report-back" 
                        onClick={() => navigate(currentRole === 'student' ? '/student/results' : '/results')}
                        title="Back to Results list"
                    >
                        <ArrowLeft size={16} />
                        Back to Results
                    </button>
                    
                    <div className="report-title-container">
                        <h1>
                            {candidateName ? `${candidateName}'s Report` : 'Candidate Report'}
                        </h1>
                        <p>
                            {assessmentName ? `Assessment: ${assessmentName}` : `Submission ID: ${submissionId}`}
                        </p>
                    </div>
                </div>
                
                <div className="report-bar-right">
                    {/* Pending badge */}
                    {hasMismatch && candidateRow?.photo_update_status === 'pending' && (
                        <div className="report-pending-badge" title="Approval request has been sent to Admin. Pending review.">
                            Pending Admin Approval
                        </div>
                    )}

                    {/* Rejected badge */}
                    {hasMismatch && candidateRow?.photo_update_status === 'rejected' && (
                        <div className="report-rejected-badge" title={`Request was rejected by Admin: ${candidateRow?.photo_update_admin_note || ''}`}>
                            <ShieldAlert size={15} />
                            Approval Request Rejected
                        </div>
                    )}

                    {/* Identity Mismatch Request Button - rendered when no active approved/pending/rejected request exists */}
                    {hasMismatch && !isApproved && candidateRow?.photo_update_status !== 'pending' && candidateRow?.photo_update_status !== 'rejected' && (
                        <button
                            className="btn-report-approve-mismatch"
                            onClick={() => { setApproveModalOpen(true); setApprovalReason(''); }}
                            title="HR manual review: Request photo update approval from Admin"
                        >
                            <ShieldAlert size={16} />
                            Approve &amp; Update Registered Face
                        </button>
                    )}

                    {/* Approved badge */}
                    {hasMismatch && isApproved && (
                        <div className="report-approved-badge" title={`Approved by ${candidateRow?.photo_update_approved_by || 'HR'} — mismatch evidence retained for audit`}>
                            <ShieldCheck size={15} />
                            Identity Mismatch Approved
                        </div>
                    )}

                    {currentRole !== 'student' && (
                        <button 
                            className="btn-report-download" 
                            onClick={handleDownload} 
                            disabled={loading || error || !pdfUrl || downloading}
                            title="Save PDF report to your device"
                        >
                            {downloading ? (
                                <>
                                    <Loader2 size={16} className="report-loading-spinner" style={{ margin: 0, animation: 'spin 1s linear infinite' }} />
                                    Downloading...
                                </>
                            ) : (
                                <>
                                    <Download size={16} />
                                    Download PDF Report
                                </>
                            )}
                        </button>
                    )}
                </div>
            </div>

            {/* Viewer content area */}
            <div className="report-viewer-content">
                {loading ? (
                    <div className="report-viewer-card">
                        <div className="report-loading-state">
                            <Loader2 size={44} className="report-loading-spinner" />
                            <p>Fetching candidate records</p>
                        </div>
                    </div>
                ) : error ? (
                    <div className="report-viewer-card">
                        <div className="report-error-state">
                            <AlertCircle size={48} className="report-error-icon" />
                            <h3>Failed to Generate Report</h3>
                            <p>{error}</p>
                            <button 
                                className="btn-report-retry" 
                                onClick={() => window.location.reload()}
                            >
                                Retry Generating
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="report-viewer-card">
                        {pdfUrl ? (
                            <iframe 
                                className="report-iframe" 
                                src={`${pdfUrl}#toolbar=0&navpanes=0&view=FitH`} 
                                title={`${candidateName || 'Candidate'} Report Viewer`}
                            />
                        ) : (
                            <div className="report-error-state">
                                <AlertCircle size={48} className="report-error-icon" />
                                <h3>Failed to render PDF</h3>
                                <p>The PDF URL could not be initialized locally.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* ── Approve & Update Face Confirmation Modal ── */}
            {approveModalOpen && (
                <div className="report-modal-overlay">
                    <div className="report-modal-box">
                        {/* Header */}
                        <div className="report-modal-header">
                            <h3>Approve &amp; Update Registered Face</h3>
                            <button
                                className="report-modal-close"
                                onClick={() => { setApproveModalOpen(false); setApprovalReason(''); }}
                                disabled={approving}
                            >
                                ✕
                            </button>
                        </div>

                        {/* Critical warning */}
                        <div className="report-modal-warning">
                            ⚠️ <strong>CRITICAL NOTE:</strong> {isAdmin ? "This action marks the identity mismatch as approved and updates the registered baseline face." : "This action submits a photo update approval request to the Admin. The registered baseline face will NOT be updated until the Admin reviews and approves this request."}
                            It does <strong>NOT</strong> remove mismatch history, flags, or evidence from reports, logs, or dashboards.
                            All mismatch proof is permanently retained for compliance and audit.
                        </div>

                        {/* Face comparison */}
                        <div className="report-modal-photos">
                            <div className="report-modal-photo-col">
                                <span className="report-modal-photo-label">Original Registered Face</span>
                                <div className="report-modal-photo-frame">
                                    {candidateRow?.original_identity_photo_url ? (
                                        <img src={candidateRow.original_identity_photo_url} alt="Original registered face" />
                                    ) : (
                                        <span className="report-modal-no-img">No Image</span>
                                    )}
                                </div>
                            </div>
                            <div className="report-modal-photo-col">
                                <span className="report-modal-photo-label">Captured During Assessment</span>
                                <div className="report-modal-photo-frame report-modal-photo-frame--captured">
                                    {candidateRow?.candidate_photo_url ? (
                                        <img src={candidateRow.candidate_photo_url} alt="Captured face" />
                                    ) : (
                                        <span className="report-modal-no-img">No Image</span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Reason field */}
                        <div className="report-modal-reason-wrap">
                            <label className="report-modal-reason-label">
                                Approval Reason (Audit Trail) {!isAdmin && <span style={{ color: '#ef4444' }}>*</span>}
                            </label>
                            <textarea
                                className="report-modal-reason-input"
                                value={approvalReason}
                                onChange={e => setApprovalReason(e.target.value)}
                                placeholder="Explain why this identity mismatch is being approved (e.g., manual PAN card verification confirmed candidate identity)..."
                                rows={4}
                                disabled={approving}
                            />
                        </div>

                        {/* Actions */}
                        <div className="report-modal-actions">
                            <button
                                className="report-modal-btn-cancel"
                                onClick={() => { setApproveModalOpen(false); setApprovalReason(''); }}
                                disabled={approving}
                            >
                                Cancel
                            </button>
                            <button
                                className="report-modal-btn-confirm"
                                onClick={handleApprove}
                                disabled={approving || (!isAdmin && !approvalReason.trim())}
                            >
                                {approving ? (
                                    <>
                                        <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
                                        Approving...
                                    </>
                                ) : (
                                    <>
                                        <ShieldCheck size={15} />
                                        {isAdmin ? 'Confirm Update' : 'Confirm Approval'}
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
