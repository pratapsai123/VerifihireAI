import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { jsPDF } from 'jspdf';

const parseDetailedRatings = (feedbackText, f) => {
    const ratings = {
        solutionApproach: null,
        codingLanguage: null,
        codeCompleteness: null,
        useCaseCoverage: null,
        overallRating: null
    };

    if (feedbackText) {
        // Attempt to parse out the ratings
        const solMatch = feedbackText.match(/-\s*Solution\s*Approach:\s*(\d+)\/5/i);
        const langMatch = feedbackText.match(/-\s*Coding\s*Language:\s*(\d+)\/5/i);
        const compMatch = feedbackText.match(/-\s*Code\s*Completeness:\s*(\d+)\/5/i);
        const useCaseMatch = feedbackText.match(/-\s*Use\s*Case\s*Coverage:\s*(\d+)\/5/i);
        const overallMatch = feedbackText.match(/-\s*Overall\s*Rating:\s*(\d+)\/5/i);

        if (solMatch) ratings.solutionApproach = parseInt(solMatch[1], 10);
        if (langMatch) ratings.codingLanguage = parseInt(langMatch[1], 10);
        if (compMatch) ratings.codeCompleteness = parseInt(compMatch[1], 10);
        if (useCaseMatch) ratings.useCaseCoverage = parseInt(useCaseMatch[1], 10);
        if (overallMatch) ratings.overallRating = parseInt(overallMatch[1], 10);
    }

    // Fallbacks for older data if not found in text
    if (ratings.solutionApproach === null) {
        ratings.solutionApproach = f.interviewer_technical_rating || null;
    }
    if (ratings.overallRating === null) {
        ratings.overallRating = f.interviewer_average_rating || f.interviewer_rating || null;
    }

    return ratings;
};

const renderRatingValue = (val) => {
    if (val === null || val === undefined) return 'N/A';
    return `${val}/5`;
};

const cleanFeedbackNotes = (text) => {
    if (!text) return '';
    return text.replace(/--- Detailed Ratings ---[\s\S]*?(?=---|$)/i, '').replace(/\n{3,}/g, '\n\n').trim();
};

export default function FeedbackDetails() {
    const location = useLocation();
    const navigate = useNavigate();
    const { inv } = location.state || {};

    const [violationsData, setViolationsData] = useState(null);
    const [loadingViolations, setLoadingViolations] = useState(true);
    const [errorViolations, setErrorViolations] = useState('');
    const [modalImage, setModalImage] = useState(null);

    useEffect(() => {
        if (!inv || !inv.id) return;

        const fetchViolations = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/interviews/${inv.id}/violations/`);
                setViolationsData(response.data);
            } catch (err) {
                console.error("Error fetching violations:", err);
                setErrorViolations(err.response?.data?.error || "Failed to load malpractice summary.");
            } finally {
                setLoadingViolations(false);
            }
        };

        fetchViolations();
    }, [inv]);

    if (!inv) {
        return (
            <div style={{ padding: '2rem', textAlign: 'center' }}>
                <h2>No feedback data found</h2>
                <button className="btn-secondary" onClick={() => navigate('/live-interview-list')}>
                    Back to List
                </button>
            </div>
        );
    }

    const formatTime = (isoString) => {
        if (!isoString) return '-';
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString('en-IN', { hour12: false });
        } catch (e) {
            return '-';
        }
    };

    const getSeverityStyle = (severity) => {
        const sev = String(severity).toUpperCase();
        if (sev === 'HIGH') {
            return {
                backgroundColor: '#fee2e2',
                color: '#dc2626',
                border: '1px solid #fecaca',
                padding: '4px 10px',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: '700',
                display: 'inline-block',
                textTransform: 'uppercase'
            };
        } else if (sev === 'MEDIUM') {
            return {
                backgroundColor: '#ffedd5',
                color: '#ea580c',
                border: '1px solid #fed7aa',
                padding: '4px 10px',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: '700',
                display: 'inline-block',
                textTransform: 'uppercase'
            };
        } else {
            return {
                backgroundColor: '#fef9c3',
                color: '#ca8a04',
                border: '1px solid #fef08a',
                padding: '4px 10px',
                borderRadius: '9999px',
                fontSize: '0.75rem',
                fontWeight: '700',
                display: 'inline-block',
                textTransform: 'uppercase'
            };
        }
    };

    const getStatusIndicator = (status) => {
        const s = String(status || '').toLowerCase();
        if (s.includes('high')) {
            return { icon: '🔴', color: '#ef4444', bg: '#fef2f2', label: 'High Risk' };
        } else if (s.includes('suspicious')) {
            return { icon: '🟡', color: '#f97316', bg: '#fff7ed', label: 'Suspicious' };
        } else {
            return { icon: '🟢', color: '#10b981', bg: '#ecfdf5', label: 'Clean' };
        }
    };

    const convertViolationName = (name) => {
        if (!name) return 'Unknown';
        const mapping = {
            'MULTIPLE_FACES': 'Multiple Faces Detected',
            'EXTRA_PERSON_DETECTED': 'Extra Person Detected',
            'MOBILE_PHONE_DETECTED': 'Mobile Phone Detected',
            'SCREEN_SHARE_STOPPED': 'Screen Share Stopped',
            'NO_FACE': 'No Face Detected',
            'TAB_SWITCH': 'Tab Switching',
            'FULLSCREEN_EXIT': 'Fullscreen Exit'
        };
        return mapping[name] || name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    };

    const handleExport = () => {
        if (!inv) return;

        const doc = new jsPDF();
        let y = 20;
        const pageHeight = doc.internal.pageSize.height;
        const pageWidth = doc.internal.pageSize.width;
        const margin = 15;
        const contentWidth = pageWidth - 2 * margin;

        const checkPageOverflow = (lineHeight) => {
            if (y + lineHeight > pageHeight - margin) {
                doc.addPage();
                y = 20;
            }
        };

        // Title Header
        doc.setFont("helvetica", "bold");
        doc.setFontSize(18);
        doc.setTextColor(37, 99, 235); // #2563eb
        doc.text("VERIFIHIRE INTERVIEW FEEDBACK REPORT", margin, y);
        y += 10;

        doc.setDrawColor(226, 232, 240); // #e2e8f0
        doc.setLineWidth(0.5);
        doc.line(margin, y, pageWidth - margin, y);
        y += 10;

        // Candidate Details Section
        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.setTextColor(15, 23, 42); // #0f172a
        doc.text("CANDIDATE DETAILS", margin, y);
        y += 7;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(51, 65, 85); // #334155

        const details = [
            `Candidate Name: ${inv.name || 'N/A'}`,
            `Candidate Email: ${inv.email || 'N/A'}`,
            `Interview: ${inv.interview?.name || 'N/A'}`,
            `Scheduled Time: ${inv.start_time ? new Date(inv.start_time).toLocaleString() : 'N/A'}`
        ];

        details.forEach(detail => {
            checkPageOverflow(6);
            doc.text(detail, margin, y);
            y += 6;
        });
        y += 6;

        // Malpractice & Integrity Summary Section
        if (violationsData) {
            checkPageOverflow(15);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(12);
            doc.setTextColor(15, 23, 42);
            doc.text("MALPRACTICE & INTEGRITY SUMMARY", margin, y);
            y += 7;

            doc.setFont("helvetica", "normal");
            doc.setFontSize(10);
            doc.setTextColor(51, 65, 85);

            if (violationsData.violation_summary && Object.keys(violationsData.violation_summary).length > 0) {
                checkPageOverflow(6);
                doc.text("Violation Breakdown:", margin, y);
                y += 6;
                Object.entries(violationsData.violation_summary).forEach(([type, count]) => {
                    checkPageOverflow(6);
                    doc.text(`  - ${convertViolationName(type)}: ${count}`, margin, y);
                    y += 6;
                });
            }

            const stats = [
                `Total Violations: ${violationsData.total_violations || 0}`,
                `High Severity: ${violationsData.high_count || 0}`,
                `Medium Severity: ${violationsData.medium_count || 0}`,
                `Low Severity: ${violationsData.low_count || 0}`,
                `Overall Risk Score: ${violationsData.risk_score || 0}`,
                `Integrity Status: ${violationsData.integrity_status || 'Clean'}`
            ];

            y += 2;
            stats.forEach(stat => {
                checkPageOverflow(6);
                doc.text(stat, margin, y);
                y += 6;
            });
            y += 6;

            if (violationsData.violations && violationsData.violations.length > 0) {
                checkPageOverflow(15);
                doc.setFont("helvetica", "bold");
                doc.setFontSize(11);
                doc.setTextColor(15, 23, 42);
                doc.text("Violation Timeline:", margin, y);
                y += 7;

                doc.setFont("helvetica", "bold");
                doc.setFontSize(9);
                doc.setTextColor(100, 116, 139);
                doc.text("Time", margin, y);
                doc.text("Violation Type", margin + 25, y);
                doc.text("Severity", margin + 85, y);
                doc.text("Duration", margin + 125, y);
                y += 5;

                doc.setDrawColor(241, 245, 249);
                doc.line(margin, y, pageWidth - margin, y);
                y += 5;

                doc.setFont("helvetica", "normal");
                doc.setTextColor(51, 65, 85);
                violationsData.violations.forEach(v => {
                    checkPageOverflow(6);
                    const timeStr = formatTime(v.timestamp);
                    const typeStr = convertViolationName(v.violation_type);
                    const sevStr = String(v.severity);
                    const durStr = v.duration > 0 ? `${v.duration} sec` : '-';

                    doc.text(timeStr, margin, y);
                    doc.text(typeStr, margin + 25, y);
                    doc.text(sevStr, margin + 85, y);
                    doc.text(durStr, margin + 125, y);
                    y += 6;
                });
                y += 6;
            }
        }

        // Interviewer Feedback Details Section
        checkPageOverflow(15);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.setTextColor(15, 23, 42);
        doc.text("INTERVIEWER FEEDBACK DETAILS", margin, y);
        y += 7;

        if (inv.feedbacks && inv.feedbacks.length > 0) {
            inv.feedbacks.forEach((f, idx) => {
                const isInterviewer = !f.participant_email ||
                    (inv.interviewer_email && f.participant_email.toLowerCase() === inv.interviewer_email.toLowerCase());
                const role = isInterviewer ? 'Interviewer' : 'Panel Member';

                checkPageOverflow(12);
                doc.setFont("helvetica", "bold");
                doc.setFontSize(10);
                doc.setTextColor(15, 23, 42);
                doc.text(`[${role}] ${f.participant_name || f.participant_email || 'Panelist'}`, margin, y);
                y += 6;

                doc.setFont("helvetica", "normal");
                doc.setFontSize(10);
                doc.setTextColor(51, 65, 85);

                const detailedRatings = parseDetailedRatings(f.interviewer_feedback, f);
                const ratingsList = [
                    `Solution Approach: ${renderRatingValue(detailedRatings.solutionApproach)}`,
                    `Coding Language: ${renderRatingValue(detailedRatings.codingLanguage)}`,
                    `Code Completeness: ${renderRatingValue(detailedRatings.codeCompleteness)}`,
                    `Use Case Coverage: ${renderRatingValue(detailedRatings.useCaseCoverage)}`,
                    `Overall Rating: ${renderRatingValue(detailedRatings.overallRating)}`
                ];

                ratingsList.forEach(ratingStr => {
                    checkPageOverflow(6);
                    doc.text(`- ${ratingStr}`, margin, y);
                    y += 6;
                });

                // Feedback Notes
                checkPageOverflow(8);
                doc.setFont("helvetica", "bold");
                doc.text("Feedback Notes:", margin, y);
                y += 5;

                doc.setFont("helvetica", "normal");
                const notes = cleanFeedbackNotes(f.interviewer_feedback) || 'No written feedback provided.';
                const splitNotes = doc.splitTextToSize(notes, contentWidth);
                splitNotes.forEach(line => {
                    checkPageOverflow(5);
                    doc.text(line, margin, y);
                    y += 5;
                });
                
                y += 6;
                doc.setDrawColor(226, 232, 240);
                doc.line(margin, y, pageWidth - margin, y);
                y += 10;
            });
        } else {
            checkPageOverflow(8);
            doc.setFont("helvetica", "normal");
            doc.text("No interviewer feedback recorded.", margin, y);
        }

        doc.save(`Feedback_Report_${inv.name || 'Candidate'}.pdf`);
    };

    const renderStars = (rating) => {
        const r = parseFloat(rating || 0);
        return (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                {[1, 2, 3, 4, 5].map((star) => (
                    <i
                        key={star}
                        className={`${star <= Math.round(r) ? 'fas' : 'far'} fa-star`}
                        style={{ color: star <= Math.round(r) ? '#f59e0b' : '#cbd5e1', fontSize: '18px' }}
                    ></i>
                ))}
                <span style={{ marginLeft: '8px', fontSize: '16px', fontWeight: 600, color: '#475569' }}>
                    {r > 0 ? r.toFixed(1) : 'No rating'}
                </span>
            </div>
        );
    };

    return (
        <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto', fontFamily: "'Inter', system-ui, sans-serif", color: '#1e293b' }}>
            
            {/* Header controls */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <button 
                    className="btn-secondary" 
                    onClick={() => navigate('/live-interview-list')}
                    style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        cursor: 'pointer'
                    }}
                >
                    &larr; Back to Interviews
                </button>
                <button 
                    onClick={handleExport} 
                    style={{
                        backgroundColor: '#2563eb',
                        color: '#fff',
                        border: 'none',
                        padding: '0.625rem 1.25rem',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontWeight: '600',
                        fontSize: '0.875rem',
                        boxShadow: '0 4px 12px rgba(37, 99, 235, 0.2)',
                        transition: 'all 0.2s ease-in-out'
                    }}
                >
                    <i className="fas fa-download"></i> Export Feedback Report
                </button>
            </div>

            {/* Main Feedback & Ratings Card */}
            <div style={{ background: '#fff', borderRadius: '12px', padding: '2.5rem', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05)', border: '1px solid #f1f5f9', marginBottom: '2rem' }}>
                <h1 style={{ marginTop: 0, marginBottom: '0.5rem', color: '#0f172a', fontSize: '1.75rem', fontWeight: '800' }}>Interview Feedback</h1>
                <p style={{ color: '#64748b', fontSize: '0.95rem', marginBottom: '2rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem' }}>
                    <strong>Candidate:</strong> {inv.name || 'N/A'} &nbsp;|&nbsp;
                    <strong>Interview:</strong> {inv.interview?.name || 'N/A'}
                </p>

                {inv.feedbacks && inv.feedbacks.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                        {/* Interviewer/Panelist Feedback */}
                        {(() => {
                            let panelistCount = 0;
                            return inv.feedbacks.filter(f => f.interviewer_feedback || f.interviewer_rating).map((f, idx) => {
                                const isPrimary = !f.participant_email || 
                                    (inv.interviewer_email && f.participant_email.toLowerCase() === inv.interviewer_email.toLowerCase());
                                
                                let headerText = "";
                                if (isPrimary) {
                                    headerText = inv.interviewer_name ? `${inv.interviewer_name}'s Feedback` : "Interviewer's Feedback";
                                } else {
                                    if (f.participant_name) {
                                        headerText = `${f.participant_name}'s Feedback`;
                                    } else {
                                        panelistCount += 1;
                                        headerText = `Panelist ${panelistCount} Feedback`;
                                    }
                                }

                                return (
                                    <div key={idx} style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '10px', borderLeft: '4px solid #3b82f6', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.2rem', fontWeight: '700' }}>
                                                    {headerText}
                                                </h2>
                                                <span style={{ 
                                                    fontSize: '0.75rem', 
                                                    fontWeight: '700', 
                                                    padding: '2px 8px', 
                                                    borderRadius: '12px', 
                                                    background: isPrimary ? '#dbeafe' : '#f1f5f9', 
                                                    color: isPrimary ? '#1e40af' : '#475569' 
                                                }}>
                                                    {isPrimary ? 'Interviewer' : 'Panel Member'}
                                                </span>
                                            </div>
                                            {f.participant_email && (
                                                <span style={{ fontSize: '0.875rem', color: '#64748b', fontFamily: 'monospace' }}>{f.participant_email}</span>
                                            )}
                                        </div>

                                        {(() => {
                                            const detailedRatings = parseDetailedRatings(f.interviewer_feedback, f);
                                            return (
                                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1.25rem', margin: '1rem 0', padding: '1rem', background: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                                                    <div>
                                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem', fontWeight: '500' }}>Solution Approach</div>
                                                        <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1e293b' }}>
                                                            {renderRatingValue(detailedRatings.solutionApproach)}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem', fontWeight: '500' }}>Coding Language</div>
                                                        <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1e293b' }}>
                                                            {renderRatingValue(detailedRatings.codingLanguage)}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem', fontWeight: '500' }}>Code Completeness</div>
                                                        <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1e293b' }}>
                                                            {renderRatingValue(detailedRatings.codeCompleteness)}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem', fontWeight: '500' }}>Use Case Coverage</div>
                                                        <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1e293b' }}>
                                                            {renderRatingValue(detailedRatings.useCaseCoverage)}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem', fontWeight: '500' }}>Overall Rating</div>
                                                        <div style={{ fontSize: '1.125rem', fontWeight: '700', color: '#1e293b' }}>
                                                            {renderRatingValue(detailedRatings.overallRating)}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })()}
                                        <div style={{ marginTop: '1.25rem' }}>
                                            <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#334155', fontSize: '0.9rem' }}>Feedback Notes:</strong>
                                            <div style={{ whiteSpace: 'pre-wrap', color: '#334155', fontSize: '0.925rem', lineHeight: '1.6', background: '#fff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                                                {cleanFeedbackNotes(f.interviewer_feedback) || 'No written feedback provided.'}
                                            </div>
                                        </div>
                                        {f.updated_at && (
                                            <div style={{ marginTop: '1rem', textAlign: 'right', fontSize: '0.75rem', color: '#94a3b8' }}>
                                                Submitted on: {new Date(f.updated_at).toLocaleString()}
                                            </div>
                                        )}
                                    </div>
                                );
                            });
                        })()}

                        {/* Candidate Feedback Section */}
                        {inv.feedbacks.filter(f => f.candidate_feedback || f.candidate_rating).map((f, idx) => (
                            <div key={`cand-${idx}`} style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '10px', borderLeft: '4px solid #10b981', boxShadow: '0 2px 8px rgba(0,0,0,0.02)' }}>
                                <h2 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.2rem', fontWeight: '700' }}>Candidate's Experience</h2>
                                <div style={{ margin: '1rem 0' }}>
                                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem', fontWeight: '500' }}>Candidate Rating</div>
                                    {renderStars(f.candidate_rating)}
                                </div>
                                <div style={{ marginTop: '1rem' }}>
                                    <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#334155', fontSize: '0.9rem' }}>Feedback Notes:</strong>
                                    <div style={{ whiteSpace: 'pre-wrap', color: '#334155', fontSize: '0.925rem', lineHeight: '1.6', background: '#fff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                                        {f.candidate_feedback || 'No written feedback provided.'}
                                    </div>
                                </div>
                            </div>
                        ))}

                    </div>
                ) : (
                    <div style={{ padding: '2rem', textAlign: 'center', background: '#f1f5f9', borderRadius: '8px' }}>
                        <i className="fas fa-info-circle" style={{ fontSize: '2rem', color: '#94a3b8', marginBottom: '1rem' }}></i>
                        <p style={{ margin: 0, color: '#64748b' }}>No feedback has been submitted for this interview yet.</p>
                    </div>
                )}
            </div>

            {/* Malpractice Proctoring & Summary Section */}
            <div style={{ background: '#fff', borderRadius: '12px', padding: '2.5rem', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05)', border: '1px solid #f1f5f9' }}>
                <h2 style={{ marginTop: 0, marginBottom: '1.5rem', color: '#0f172a', fontSize: '1.4rem', fontWeight: '800', borderBottom: '2px solid #f1f5f9', paddingBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <i className="fas fa-shield-alt" style={{ color: '#dc2626' }}></i>
                    Malpractice & Proctoring Summary
                </h2>

                {loadingViolations ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div style={{ border: '3px solid #f3f3f3', borderTop: '3px solid #3b82f6', borderRadius: '50%', width: '24px', height: '24px', animation: 'spin 1s linear infinite', margin: '0 auto 10px' }} />
                        <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>Loading malpractice details...</p>
                        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
                    </div>
                ) : errorViolations ? (
                    <div style={{ padding: '1.5rem', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#991b1b', fontSize: '0.875rem' }}>
                        <i className="fas fa-exclamation-triangle" style={{ marginRight: '8px' }}></i>
                        {errorViolations}
                    </div>
                ) : violationsData ? (
                    <div>
                        {/* Summary Cards Row */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                            
                            {/* Violation Breakdown Card */}
                            <div style={{ padding: '1.5rem', backgroundColor: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                                <div style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>
                                    Malpractice Summary
                                </div>
                                {violationsData.violation_summary && Object.keys(violationsData.violation_summary).length > 0 ? (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem', textAlign: 'left', marginBottom: '0.75rem' }}>
                                            <thead>
                                                <tr style={{ borderBottom: '1px solid #cbd5e1' }}>
                                                    <th style={{ paddingBottom: '0.5rem', fontWeight: '600', color: '#475569' }}>Violation Type</th>
                                                    <th style={{ paddingBottom: '0.5rem', fontWeight: '600', color: '#475569', textAlign: 'right' }}>Count</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {Object.entries(violationsData.violation_summary).map(([type, count]) => (
                                                    <tr key={type} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                                        <td style={{ padding: '0.5rem 0', fontWeight: '500', color: '#1e293b' }}>
                                                            {convertViolationName(type)}
                                                        </td>
                                                        <td style={{ padding: '0.5rem 0', fontWeight: '700', color: '#1e293b', textAlign: 'right' }}>
                                                            {count}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontWeight: '700', fontSize: '0.95rem', color: '#0f172a', borderTop: '2px solid #e2e8f0', paddingTop: '0.75rem' }}>
                                            <span>Total Violations:</span>
                                            <span>{violationsData.total_violations}</span>
                                        </div>
                                    </div>
                                ) : (
                                    <div style={{ color: '#64748b', fontSize: '0.875rem', padding: '1rem 0' }}>
                                        No violations recorded.
                                    </div>
                                )}
                            </div>

                            {/* Risk & Integrity Status Card */}
                            {(() => {
                                const statusMeta = getStatusIndicator(violationsData.integrity_status);
                                return (
                                    <div style={{ padding: '1.5rem', backgroundColor: statusMeta.bg, borderRadius: '10px', border: `1px solid ${statusMeta.color}20`, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                                        <div>
                                            <div style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                                                Integrity Status
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem' }}>
                                                <span style={{ fontSize: '1.5rem' }}>{statusMeta.icon}</span>
                                                <span style={{ fontSize: '1.35rem', fontWeight: '800', color: statusMeta.color }}>
                                                    {statusMeta.label}
                                                </span>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', borderTop: `1px solid ${statusMeta.color}20`, paddingTop: '0.75rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#475569' }}>
                                                <span>High Severity:</span>
                                                <span style={{ fontWeight: '700', color: '#dc2626' }}>{violationsData.high_count}</span>
                                            </div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#475569' }}>
                                                <span>Medium Severity:</span>
                                                <span style={{ fontWeight: '700', color: '#ea580c' }}>{violationsData.medium_count}</span>
                                            </div>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#475569' }}>
                                                <span>Low Severity:</span>
                                                <span style={{ fontWeight: '700', color: '#ca8a04' }}>{violationsData.low_count}</span>
                                            </div>
                                            <hr style={{ border: 0, borderTop: `1px dashed ${statusMeta.color}20`, margin: '0.25rem 0' }} />
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                                                <span style={{ fontSize: '0.875rem', color: '#475569', fontWeight: '500' }}>Overall Risk Score:</span>
                                                <span style={{ fontSize: '1.6rem', fontWeight: '900', color: statusMeta.color }}>
                                                    {violationsData.risk_score}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })()}

                        </div>

                        {/* Violation Timeline Table */}
                        <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#0f172a', marginBottom: '0.75rem' }}>
                            Violation Timeline
                        </h3>
                        {violationsData.violations && violationsData.violations.length > 0 ? (
                            <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                                    <thead>
                                        <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                            <th style={{ padding: '0.75rem 1rem', fontWeight: '600', color: '#475569' }}>Time</th>
                                            <th style={{ padding: '0.75rem 1rem', fontWeight: '600', color: '#475569' }}>Violation</th>
                                            <th style={{ padding: '0.75rem 1rem', fontWeight: '600', color: '#475569' }}>Severity</th>
                                            <th style={{ padding: '0.75rem 1rem', fontWeight: '600', color: '#475569' }}>Duration</th>
                                            <th style={{ padding: '0.75rem 1rem', fontWeight: '600', color: '#475569' }}>Evidence</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {violationsData.violations.map((v, i) => (
                                            <tr key={v.id || i} style={{ borderBottom: i < violationsData.violations.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                                                <td style={{ padding: '1rem', color: '#475569', fontWeight: '500', fontFamily: 'monospace' }}>
                                                    {formatTime(v.timestamp)}
                                                </td>
                                                <td style={{ padding: '1rem', color: '#0f172a', fontWeight: '600' }}>
                                                    {convertViolationName(v.violation_type)}
                                                </td>
                                                <td style={{ padding: '1rem' }}>
                                                    <span style={getSeverityStyle(v.severity)}>
                                                        {v.severity}
                                                    </span>
                                                </td>
                                                <td style={{ padding: '1rem', color: '#475569', fontWeight: '500' }}>
                                                    {v.duration > 0 ? `${v.duration} sec` : '-'}
                                                </td>
                                                <td style={{ padding: '1rem' }}>
                                                    {v.screenshot_path ? (
                                                        <img
                                                            src={v.screenshot_path}
                                                            alt="Violation proof thumbnail"
                                                            style={{
                                                                width: '56px',
                                                                height: '38px',
                                                                objectFit: 'cover',
                                                                borderRadius: '4px',
                                                                border: '1px solid #cbd5e1',
                                                                cursor: 'pointer',
                                                                transition: 'transform 0.1s ease-in-out'
                                                            }}
                                                            onClick={() => setModalImage(v.screenshot_path)}
                                                            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                                                            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                                                        />
                                                    ) : (
                                                        <span style={{ color: '#94a3b8' }}>-</span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', color: '#64748b' }}>
                                <i className="fas fa-check-circle" style={{ fontSize: '1.5rem', color: '#10b981', marginBottom: '0.5rem', display: 'block' }}></i>
                                No malpractice violations recorded for this candidate.
                            </div>
                        )}
                    </div>
                ) : (
                    <div style={{ color: '#64748b', fontSize: '0.875rem' }}>No summary data available.</div>
                )}
            </div>

            {/* Modal for Screenshot Preview */}
            {modalImage && (
                <div 
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        backgroundColor: 'rgba(15, 23, 42, 0.85)',
                        backdropFilter: 'blur(4px)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 9999,
                        cursor: 'zoom-out'
                    }}
                    onClick={() => setModalImage(null)}
                >
                    <div style={{ position: 'relative', maxWidth: '85%', maxHeight: '85%' }} onClick={(e) => e.stopPropagation()}>
                        <button 
                            onClick={() => setModalImage(null)} 
                            style={{
                                position: 'absolute',
                                top: '-45px',
                                right: '0',
                                background: 'rgba(255,255,255,0.1)',
                                border: 'none',
                                color: '#fff',
                                width: '36px',
                                height: '36px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '18px',
                                cursor: 'pointer',
                                transition: 'background-color 0.2s'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.2)'}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'}
                        >
                            ✕
                        </button>
                        <img 
                            src={modalImage} 
                            alt="Full Violation Evidence" 
                            style={{
                                maxWidth: '100%',
                                maxHeight: '80vh',
                                borderRadius: '8px',
                                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
                                border: '3px solid rgba(255, 255, 255, 0.1)'
                            }}
                        />
                    </div>
                </div>
            )}

        </div>
    );
}
