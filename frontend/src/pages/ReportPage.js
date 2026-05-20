import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Download, ArrowLeft, Loader2, FileText, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import '../styles/ReportPage.css';

export default function ReportPage() {
    const { submissionId } = useParams();
    const navigate = useNavigate();
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pdfUrl, setPdfUrl] = useState(null);
    const [downloading, setDownloading] = useState(false);
    
    const [candidateName, setCandidateName] = useState('');
    const [assessmentName, setAssessmentName] = useState('');

    useEffect(() => {
        let active = true;
        let localPdfUrl = null;

        const loadReportAndDetails = async () => {
            if (!active) return;
            setLoading(true);
            setError(null);

            try {
                // 1. Fetch overview to find candidate name & assessment name for premium header
                try {
                    const overviewResp = await axios.get(`${API_BASE_URL}/results/`);
                    const allResults = overviewResp.data?.results || [];
                    const match = allResults.find(r => String(r.submission_id) === String(submissionId));
                    if (match && active) {
                        setCandidateName(match.candidate?.name || '');
                        setAssessmentName(match.assessment?.display_name || match.assessment?.name || 'Assessment');
                    }
                } catch (detailsErr) {
                    console.warn("Could not load candidate metadata, falling back to PDF header values:", detailsErr);
                }

                // 2. Fetch PDF blob securely (this passes JWT token in headers)
                const reportUrl = `${API_BASE_URL}/results/${submissionId}/report/`;
                const response = await axios.get(reportUrl, { responseType: 'blob' });

                if (!active) return;

                // 3. Create a local object URL to display the PDF inline
                const blob = new Blob([response.data], { type: 'application/pdf' });
                localPdfUrl = window.URL.createObjectURL(blob);
                setPdfUrl(localPdfUrl);

                // 4. Try parsing candidate name from Content-Disposition if not already resolved
                if (!candidateName) {
                    const contentDisposition = response.headers['content-disposition'];
                    if (contentDisposition) {
                        const matchName = contentDisposition.match(/filename="Report_(.+)\.pdf"/);
                        if (matchName && matchName[1]) {
                            setCandidateName(matchName[1].replace(/_/g, ' '));
                        }
                    }
                }
            } catch (err) {
                console.error("Failed to load PDF report:", err);
                if (active) {
                    setError(err.response?.data?.error || err.message || "Failed to load candidate report.");
                }
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        };

        loadReportAndDetails();

        // Cleanup object URL on unmount to prevent memory leaks
        return () => {
            active = false;
            if (localPdfUrl) {
                window.URL.revokeObjectURL(localPdfUrl);
            }
        };
    }, [submissionId]);

    const handleDownload = () => {
        if (downloading || !pdfUrl) return;
        setDownloading(true);
        try {
            const link = document.createElement('a');
            link.href = pdfUrl;
            
            // Clean up candidate name or use default filename
            const cleanName = candidateName ? candidateName.replace(/\s+/g, '_') : `Candidate_${submissionId}`;
            link.setAttribute('download', `Report_${cleanName}.pdf`);
            
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error("Failed to trigger local PDF download:", err);
            alert("Failed to download report.");
        } finally {
            setDownloading(false);
        }
    };

    return (
        <div className="report-page-container">
            
            {/* Glassmorphic control bar */}
            <div className="report-control-bar">
                <div className="report-bar-left">
                    <button 
                        className="btn-report-back" 
                        onClick={() => navigate('/results')}
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
        </div>
    );
}
