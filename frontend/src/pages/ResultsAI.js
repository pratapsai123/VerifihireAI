import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { getToken } from '../utils/authStorage';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import '../styles/Dashboard.css';
import '../styles/ResultsAI.css';

/**
 * Lazy-loading integrity screenshot component.
 * Fetches the image only when it scrolls into view using IntersectionObserver.
 */

const normalizeImageUrl = (url) => {
    if (!url) return null;
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    if (url.startsWith('/')) {
        const baseUrl = API_BASE_URL.replace(/\/api\/?$/, '');
        return `${baseUrl}${url}`;
    }
    return `data:image/jpeg;base64,${url}`;
};

const LazyIntegrityImage = ({ screenshotId, type, fallbackBase64, fallbackUrl, alt, style }) => {
    const [src, setSrc] = useState(null);
    const [loading, setLoading] = useState(true);
    const imgRef = useRef(null);
    const fetchedRef = useRef(false);

    useEffect(() => {
        // If we already have a URL (from assessment screenshots), use it directly
        if (fallbackUrl) {
            setSrc(normalizeImageUrl(fallbackUrl));
            setLoading(false);
            return;
        }
        // If we have inline base64 already, use it
        if (fallbackBase64) {
            setSrc(normalizeImageUrl(fallbackBase64));
            setLoading(false);
            return;
        }
        // No screenshot_id means no image to fetch
        if (!screenshotId) {
            setLoading(false);
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && !fetchedRef.current) {
                    fetchedRef.current = true;
                    observer.disconnect();
                    // Fetch the image lazily
                    const token = getToken();
                    axios.get(`${API_BASE_URL}/ai-candidates/integrity-screenshot/${screenshotId}/?type=${type || 'webcam'}`, {
                        headers: { Authorization: `Bearer ${token}` }
                    }).then(resp => {
                        if (resp.data?.image) {
                            setSrc(resp.data.image);
                        }
                    }).catch(() => {
                        // silent fail - will show placeholder
                    }).finally(() => {
                        setLoading(false);
                    });
                }
            },
            { threshold: 0.1 }
        );

        if (imgRef.current) {
            observer.observe(imgRef.current);
        }

        return () => observer.disconnect();
    }, [screenshotId, type, fallbackBase64, fallbackUrl]);

    return (
        <div ref={imgRef} style={{ ...style, position: 'relative' }}>
            {loading ? (
                <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F4F7FE' }}>
                    <div style={{ width: '20px', height: '20px', border: '2px solid #7C3AED', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                </div>
            ) : src ? (
                <img
                    src={src}
                    alt={alt}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                    onError={(e) => { e.target.src = 'https://placehold.co/100x100?text=Error'; }}
                />
            ) : (
                <img
                    src="https://placehold.co/100x100?text=No+Data"
                    alt={alt}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                />
            )}
        </div>
    );
};

const ResultsAI = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'assessment');
    const [statusFilter, setStatusFilter] = useState('all'); // 'all' | 'pass' | 'fail' | 'on-hold'
    const [currentPage, setCurrentPage] = useState(1);
    const [batchPage, setBatchPage] = useState(1);
    const [sortField, setSortField] = useState('score'); // Default: sort by score
    const [sortDirection, setSortDirection] = useState('desc'); // 'asc' | 'desc' (highest first)

    // Auth context
    const me = (() => {
        try { return JSON.parse(localStorage.getItem('user') || '{}'); }
        catch { return {}; }
    })();
    const myRole = (me?.role || '').toLowerCase();
    // All internal roles can trigger deletion — backend enforces the correct workflow per role:
    // company_admin → direct delete (audit logged), hr_manager/hr → sends approval request upward
    const canDelete = ['application_admin', 'company_admin', 'hr_manager', 'hr'].includes(myRole);


    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);
    const [confirmDelete, setConfirmDelete] = useState(null); // { items: [...] }
    const [selected, setSelected] = useState(new Set()); // Set of _deleteKey strings

    // Qualification request state (HR/HRM approval flow)
    const [qualReasonPopup, setQualReasonPopup] = useState(null); // { row, status, candidateName, aiSubmissionId }
    const [qualReason, setQualReason] = useState('');
    const [qualSubmitting, setQualSubmitting] = useState(false);

    // Derive admin status from localStorage
    const aiResultsCurrentUser = (() => { try { return JSON.parse(localStorage.getItem('user') || '{}'); } catch { return {}; } })();
    const aiResultsIsAdmin = ['company_admin', 'application_admin'].includes((aiResultsCurrentUser?.role || '').toLowerCase());

    const submitQualAiRequest = async () => {
        if (!qualReasonPopup || !qualReason.trim()) { showToast('error', 'Please provide a reason.'); return; }
        setQualSubmitting(true);
        try {
            // AI assessments use ai_submission_id; we POST to the qualification-requests endpoint directly
            const resp = await axios.post(`${API_BASE_URL}/workflow/qualification-requests/ai/`, {
                ai_submission_id: qualReasonPopup.aiSubmissionId,
                requested_result: qualReasonPopup.status,
                reason: qualReason.trim(),
                candidate_name: qualReasonPopup.candidateName,
                candidate_email: qualReasonPopup.candidateEmail || '',
            }, { headers: { Authorization: `Bearer ${getToken()}` } });
            showToast('success', resp.data?.message || 'Qualification request submitted.');
            setQualReasonPopup(null);
            setQualReason('');
            fetchData();
        } catch (err) {
            showToast('error', err.response?.data?.error || 'Failed to submit request.');
        } finally {
            setQualSubmitting(false);
        }
    };

    const submitPhotoApproval = async () => {
        if (!photoApprovalCandidate) return;
        const pk = photoApprovalCandidate.ai_candidate_pk;
        if (!pk) {
            showToast('error', 'Missing candidate id; cannot approve photo.');
            return;
        }
        setPhotoApprovalSubmitting(true);
        try {
            // Determine correct endpoint based on candidate type
            const isAiCandidate = !!photoApprovalCandidate.is_ai_candidate || String(photoApprovalCandidate.submission_id || '').startsWith('aicand_');
            const url = isAiCandidate
                ? `${API_BASE_URL}/ai-candidates/${pk}/approve-photo/`
                : `${API_BASE_URL}/ai/submission/${pk}/approve-photo/`;
            const resp = await axios.post(
                url,
                {},
                { headers: { Authorization: `Bearer ${getToken()}` } }
            );
            showToast('success', resp.data?.message || 'Photo approved and updated.');
            setPhotoApprovalCandidate(null);
            fetchData();
            if (viewedSubmission && viewedSubmission.id === pk) {
                setViewedSubmission(prev => ({
                    ...prev,
                    identity_mismatch_detected: false,
                    photo_update_approved: true,
                    photo_update_pending: false,
                    // Snap the UI to the newly approved photo so they see the change immediately
                    candidate_photo_url: prev.intruder_photo_url || prev.pending_identity_photo_url || prev.candidate_photo_url
                }));
            }
        } catch (err) {
            showToast('error', err.response?.data?.error || 'Failed to approve photo.');
        } finally {
            setPhotoApprovalSubmitting(false);
        }
    };

    const [aiAssessments, setAiAssessments] = useState([]);
    const [groupedData, setGroupedData] = useState({}); // { roleName: { resume: [], assessment: [], interview: [] } }
    const [viewMode, setViewMode] = useState('overview'); // 'overview' | 'detail' | 'transcript'
    const [selectedRole, setSelectedRole] = useState(null);
    const [showTranscriptDetail, setShowTranscriptDetail] = useState(null);
    const [viewedSubmission, setViewedSubmission] = useState(null); // Submission object for assessment
    const [timelineCandidate, setTimelineCandidate] = useState(null);
    const [showLogsModal, setShowLogsModal] = useState(false);
    const [timelineLogs, setTimelineLogs] = useState([]);
    const [loadingTimeline, setLoadingTimeline] = useState(false);
    const [downloadingId, setDownloadingId] = useState(null);
    const [analyticsAnimateIn, setAnalyticsAnimateIn] = useState(false);
    // Photo-approval workflow (per-candidate identity mismatch override)
    const [photoApprovalCandidate, setPhotoApprovalCandidate] = useState(null);
    const [photoApprovalSubmitting, setPhotoApprovalSubmitting] = useState(false);

    const showToast = (type, message) => {
        setToast({ type, message });
        setTimeout(() => setToast(null), 3500);
    };

    const handleDownloadReport = async (candidate) => {
        if (!candidate) return;
        const sid = String(candidate.submission_id || '');

        let endpoint = '';
        let realId = '';

        if (sid.startsWith('ai_')) {
            // AI Assessment Submission
            realId = sid.replace('ai_', '');
            endpoint = `${API_BASE_URL}/ai/submission/${realId}/download-report/`;
        } else {
            // AI Interview / Candidate Report — strip all suffixes to get pure numeric ID
            realId = sid.replace('aicand_', '').replace('_resume', '').replace('_interview', '').replace('_assessment', '');
            endpoint = `${API_BASE_URL}/ai-candidates/${realId}/download-report/`;
        }

        setDownloadingId(realId);
        try {
            const response = await axios.get(endpoint, {
                responseType: 'blob',
                headers: {
                    'Authorization': `Bearer ${getToken()}`
                }
            });

            const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
            const link = document.createElement('a');
            link.href = url;
            const safeName = (candidate.full_name || 'Candidate').replace(/\s+/g, '_');
            link.setAttribute('download', `VerifiHire_Report_${safeName}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            showToast('success', 'Report downloaded successfully!');
        } catch (err) {
            console.error('Error downloading report:', err);
            showToast('error', 'Failed to generate report. Please try again.');
        } finally {
            setDownloadingId(null);
        }
    };


    const fetchData = useCallback(async () => {
        setLoading(true);
        setSelected(new Set());
        try {
            // Use unified results endpoint + roles list
            const [resultsResp, rolesResp] = await Promise.all([
                axios.get(`${API_BASE_URL}/results/`),
                axios.get(`${API_BASE_URL}/job-roles/`)
            ]);

            const allResultsRaw = Array.isArray(resultsResp.data) ? resultsResp.data : (resultsResp.data?.results || []);
            const rolesList = Array.isArray(rolesResp.data) ? rolesResp.data : (rolesResp.data?.results || []);

            // Categorize and clean results
            const allResults = allResultsRaw.map(r => r);

            // Separate into types for UI tabs
            const resResults = [];
            const assessResults = [];
            const intResults = [];
            const manResults = [];

            allResults.forEach(r => {
                const sid = String(r.submission_id || '');
                // Categorize based on prefix and total_questions
                if (sid.startsWith('ai_')) {
                    assessResults.push({
                        ...r,
                        total_possible: r.total || r.total_possible || 100,
                        // Ensure it has nested assessment object for compatibility if not fully unified
                        assessment: r.assessment || {
                            display_name: r.full_name || 'AI Assessment',
                            name: r.full_name || 'AI Assessment'
                        }
                    });
                } else if (sid.startsWith('aicand_')) {
                    // For aicand_ records, the SINGLE record contains data for ALL stages
                    // We need to create separate stage entries that will be grouped by email

                    const hasResume = r.resume_score > 0 || ['Resume Passed', 'Resume Failed', 'Extraction Failed'].includes(r.status);
                    // For aicand_ records, technical assessment data is provided by separate 'ai_' prefixed records.
                    // We only create an assessment entry here if we have explicit MCQ/Coding data that isn't from the interview.
                    const hasAssessment = r.is_fully_automatic && (r.mcq_score > 0 || r.coding_score > 0);
                    const hasInterview = r.is_ai_interview || r.interview_summary?.length > 0 || ['Interview Passed', 'Interview Failed', 'Completed', 'Hired', 'Rejected', 'On-Hold'].includes(r.status);

                    // ALWAYS add resume entry if we have resume data
                    if (hasResume) {
                        resResults.push({
                            ...r,
                            _type: 'resume',
                            submission_id: `${sid}_resume`,
                            resume_score: r.resume_score || 0,
                            status: r.status === 'Resume Passed' || r.resume_score >= 70 ? 'Resume Passed' : 'Resume Failed'
                        });
                    }

                    // ALWAYS add assessment entry if we have assessment data
                    if (hasAssessment) {
                        assessResults.push({
                            ...r,
                            _type: 'ai_assessment',
                            submission_id: `${sid}_assessment`,
                            id: r.id, // Keep original candidate ID for Quiz button
                            candidate_name: r.full_name || r.candidate?.name,
                            candidate_email: r.email || r.candidate?.email,
                            assessment_name: r.job_title || r.assessment?.display_name || 'AI Assessment',
                            submitted_at: r.submitted_at || r.completed_at || r.created_at,
                            percentage: r.percentage || r.score || 0,
                            total_questions: r.total_questions,
                            status: r.status === 'Completed' || r.status === 'Hired' ? 'selected' : (r.percentage >= 50 ? 'selected' : 'rejected'),
                            assessment: r.assessment || {
                                display_name: r.job_title || 'AI Assessment',
                                name: r.job_title || 'AI Assessment',
                                role: r.job_title || 'General'
                            },
                            answers: r.answers || {},
                            results_breakdown: r.results_breakdown || {},
                            is_resume_screening: false
                        });
                    }

                    // ALWAYS add interview entry if we have interview data
                    if (hasInterview) {
                        intResults.push({
                            ...r,
                            _type: 'ai_interview',
                            submission_id: `${sid}_interview`,
                            score: r.score || 0,
                            interview_summary: r.interview_summary,
                            status: ['Completed', 'Hired', 'Interview Passed', 'Rejected', 'On-Hold'].includes(r.status) ? r.status : 'Interviewing'
                        });
                    }

                    // If no stages detected but has a status, put in appropriate bucket
                    if (!hasResume && !hasAssessment && !hasInterview) {
                        const resumeStatuses = ['Resume Passed', 'Resume Failed', 'Extraction Failed'];
                        const interviewStatuses = ['Interview Passed', 'Interview Failed', 'Completed', 'Hired', 'Rejected', 'On-Hold'];

                        if (resumeStatuses.includes(r.status)) {
                            resResults.push({ ...r, _type: 'resume', submission_id: `${sid}_resume` });
                        } else if (interviewStatuses.includes(r.status)) {
                            intResults.push({ ...r, _type: 'interview', submission_id: `${sid}_interview` });
                        } else {
                            // Default to resume for unknown
                            resResults.push({ ...r, _type: 'resume', submission_id: `${sid}_resume` });
                        }
                    }
                } else {
                    // Collect standard/manual assessment results
                    manResults.push({
                        ...r,
                        _type: 'manual_assessment',
                        assessment: r.assessment || {
                            display_name: r.full_name || 'Standard Assessment',
                            name: r.full_name || 'Standard Assessment'
                        }
                    });
                }
            });

            // State setters for categorized results are not needed as we use groupedData for UI
            // but we keep aiAssessments for the submission detail lookup logic
            const allSorted = [...resResults, ...assessResults, ...intResults, ...manResults]
                .sort((a, b) => new Date(b.submitted_at || b.created_at || 0) - new Date(a.submitted_at || a.created_at || 0));
            setAiAssessments(allSorted);

            const normalizeRoleName = (role) => {
                if (!role) return 'Other';
                let normalized = String(role).toLowerCase()
                    .replace(/assessment/g, '')
                    .replace(/role[:\s]+/g, '')
                    .replace(/job title[:\s]+/g, '')
                    .trim();

                // Common aliases to catch fuzzy matches
                if (normalized.includes('python') && normalized.includes('developer')) return 'python developer';
                if (normalized.includes('java') && normalized.includes('developer')) return 'java developer';

                return normalized || 'Other';
            };

            const groups = {};

            const addToGroup = (item, type) => {
                const rawRole = item.assessment?.role || item.assessment?.display_name || item.assessment?.name || item.job_title || 'General';
                const baseLabel = item.batch_name || `${normalizeRoleName(rawRole)}_Archive`;
                const groupKey = item.is_fully_automatic ? `AUTO_${baseLabel}` : `MANUAL_${baseLabel}`;

                if (!groups[groupKey]) {
                    groups[groupKey] = {
                        resume: [],
                        assessment: [],
                        interview: [],
                        standard: [],
                        total: 0,
                        role: rawRole,
                        batch_name: baseLabel,
                        is_fully_automatic: item.is_fully_automatic || false
                    };
                }
                groups[groupKey][type].push(item);
                groups[groupKey].total += 1;
            };

            resResults.forEach(r => addToGroup(r, 'resume'));
            intResults.forEach(r => addToGroup(r, 'interview'));
            assessResults.forEach(s => addToGroup(s, 'assessment'));
            manResults.forEach(m => addToGroup(m, 'standard'));

            Object.values(groups).forEach(g => {
                if (g.is_fully_automatic) {
                    const emails = new Set();
                    [...g.resume, ...g.assessment, ...g.interview].forEach(item => {
                        const email = (item.email || item.candidate?.email || `anon_${item.submission_id || item.id}`).toLowerCase();
                        emails.add(email);
                    });
                    g.unique_candidates = emails.size;
                }
            });

            setGroupedData(groups);

            setSelectedRole(prev => {
                if (prev && !groups[prev]) {
                    setTimeout(() => setViewMode('overview'), 0);
                    return null;
                }
                return prev;
            });
        } catch (err) {
            console.error('Error fetching AI results:', err);
            showToast('error', 'Failed to load results. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    // Analytics panel entrance animation
    useEffect(() => {
        if (viewMode === 'detail' && activeTab === 'interview') {
            setAnalyticsAnimateIn(false);
            setTimeout(() => setAnalyticsAnimateIn(true), 50);
        }
    }, [viewMode, selectedRole, activeTab]);

    // Compute batch metrics for the analytics panel
    const computeBatchMetrics = (rows) => {
        const total = rows.length;
        if (total === 0) return { total: 0, passed: 0, failed: 0, onHold: 0, avgScore: 'N/A', completionRate: 'N/A' };
        const onHold = rows.filter(r => r.status === 'On-Hold').length;
        const passed = rows.filter(r => isPass(r, 'interview') && r.status !== 'On-Hold').length;
        const ongoing = rows.filter(r => r.status && ['ongoing', 'started', 'in-progress'].includes(r.status.toLowerCase())).length;
        const failed = total - passed - onHold - ongoing;
        const scores = rows.map(r => getScoreValue(r));
        const avgScore = Math.round(scores.reduce((sum, s) => sum + s, 0) / total);
        const completed = rows.filter(r => r.completed_at || r.submitted_at).length;
        const completionRate = Math.round((completed / total) * 100);
        return { total, passed, failed, onHold, avgScore, completionRate };
    };


    // Sync URL subId with viewedSubmission modal
    useEffect(() => {
        const subId = searchParams.get('subId');
        if (subId) {
            let active = true;
            const fetchDetail = async () => {
                try {
                    const token = getToken();
                    const resp = await axios.get(`${API_BASE_URL}/results/${subId}/detail/`, {
                        headers: { Authorization: `Bearer ${token}` }
                    });
                    if (active && resp.data) {
                        setViewedSubmission(resp.data);
                    }
                } catch (err) {
                    console.error("Error fetching submission details:", err);
                    // Fallback to list search if detail endpoint fails
                    const found = aiAssessments.find(a =>
                        String(a.submission_id) === String(subId) ||
                        String(a.id) === String(subId) ||
                        String(a.submission_id) === `ai_${subId}`
                    );
                    if (active && found) {
                        setViewedSubmission(found);
                    }
                }
            };
            fetchDetail();
            return () => { active = false; };
        } else {
            setViewedSubmission(null);
        }
    }, [searchParams, aiAssessments]);

    // Automatically fetch detail photos when photoApprovalCandidate modal is opened without photos (list view fallback)
    useEffect(() => {
        if (photoApprovalCandidate && !photoApprovalCandidate.pending_identity_photo_url) {
            const pk = photoApprovalCandidate.ai_candidate_pk || photoApprovalCandidate.id;
            const subId = photoApprovalCandidate.submission_id || 
                          (photoApprovalCandidate.is_ai_candidate || String(photoApprovalCandidate.submission_id || '').startsWith('aicand_')
                              ? `aicand_${pk}`
                              : `ai_${pk}`);
            const fetchApprovalDetail = async () => {
                try {
                    const token = getToken();
                    const resp = await axios.get(`${API_BASE_URL}/results/${subId}/detail/`, {
                        headers: { Authorization: `Bearer ${token}` }
                    });
                    if (resp.data) {
                        setPhotoApprovalCandidate(prev => {
                            if (!prev || String(prev.ai_candidate_pk || prev.id) !== String(pk)) return prev;
                            return {
                                ...prev,
                                master_photo_url: resp.data.master_photo_url || resp.data.original_identity_photo_url,
                                original_identity_photo_url: resp.data.original_identity_photo_url,
                                candidate_photo_url: resp.data.candidate_photo_url,
                                pending_identity_photo_url: resp.data.pending_identity_photo_url || resp.data.intruder_photo_url,
                            };
                        });
                    }
                } catch (err) {
                    console.error("Error fetching approval photo details:", err);
                }
            };
            fetchApprovalDetail();
        }
    }, [photoApprovalCandidate]);



    // Automatically fetch timeline for the side drawer when viewedSubmission changes
    useEffect(() => {
        if (viewedSubmission) {
            const realId = viewedSubmission.ai_candidate_pk || String(viewedSubmission.submission_id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '').replace('resume-', '').replace('interview-', '');
            const currentTimelineId = timelineCandidate?.ai_candidate_pk || String(timelineCandidate?.submission_id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '').replace('resume-', '').replace('interview-', '');

            if (realId !== currentTimelineId) {
                fetchTimeline(viewedSubmission);
            }
        }
    }, [viewedSubmission]);

    // Also fetch timeline when viewing interview transcript report
    useEffect(() => {
        if (showTranscriptDetail && viewMode === 'transcript') {
            const realId = showTranscriptDetail.ai_candidate_pk || String(showTranscriptDetail.submission_id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '').replace('resume-', '').replace('interview-', '');
            const currentTimelineId = timelineCandidate?.ai_candidate_pk || String(timelineCandidate?.submission_id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '').replace('resume-', '').replace('interview-', '');

            if (realId !== currentTimelineId) {
                fetchTimeline(showTranscriptDetail);
            }
        }
    }, [showTranscriptDetail, viewMode]);

    const fetchTimeline = async (candidate, openModal = false) => {
        if (!candidate) return;
        setTimelineCandidate(candidate);
        if (openModal) setShowLogsModal(true);
        setLoadingTimeline(true);
        // Don't clear logs immediately to allow 'refresh' feel, 
        // but for a NEW candidate selection, we should.
        if (timelineCandidate?.submission_id !== candidate.submission_id) {
            setTimelineLogs([]);
        }

        try {
            const isAssessment = !candidate.is_ai_candidate && (candidate.is_assessment || !!candidate.assessment_name || !!candidate.assessment || String(candidate.submission_id || '').startsWith('ai_'));
            let resp;

            if (isAssessment) {
                // Fetch AI Assessment timeline
                const realId = String(candidate.submission_id || candidate.id || '').replace('ai_', '');
                resp = await axios.get(`${API_BASE_URL}/ai/submission/${realId}/timeline/`, {
                    headers: { Authorization: `Bearer ${getToken()}` }
                });
            } else {
                // Fetch AI Interview timeline
                const realId = candidate.ai_candidate_pk || String(candidate.submission_id || candidate.id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '').replace('resume-', '').replace('interview-', '');
                resp = await axios.get(`${API_BASE_URL}/ai-candidates/${realId}/timeline/`, {
                    headers: { Authorization: `Bearer ${getToken()}` }
                });
            }

            // Scoping: Filter logs by current batch_id if it exists to avoid history pollution from other applications
            let filteredLogs = resp.data;
            if (candidate.batch_id) {
                filteredLogs = resp.data.filter(log => !log.batch_id || log.batch_id === candidate.batch_id);
            }

            // Enhanced Phase Inference for legacy logs (where phase is GENERAL)
            filteredLogs = filteredLogs.map(log => {
                if (log.phase === 'GENERAL') {
                    const msg = log.message.toLowerCase();
                    if (msg.includes('resume') || msg.includes('screening')) return { ...log, phase: 'RESUME' };
                    if (msg.includes('assessment') || msg.includes('pool') || msg.includes('quiz')) return { ...log, phase: 'ASSESSMENT' };
                    if (msg.includes('interview')) return { ...log, phase: 'INTERVIEW' };
                }
                return log;
            });

            setTimelineLogs(filteredLogs);
        } catch (err) {
            console.error('Error fetching timeline:', err);
            showToast('error', 'Failed to load timeline history.');
        } finally {
            setLoadingTimeline(false);
        }
    };

    const fetchAssessmentByCandidateEmail = async (options) => {
        try {
            const params = {};
            if (typeof options === 'string') {
                params.candidate_email = options;
            } else {
                if (options.email) params.candidate_email = options.email;
                if (options.batchName && options.batchName !== 'All Roles') {
                    params.batch_name = options.batchName.replace('AUTO_', '').replace('MANUAL_', '');
                }
                if (options.batchId) params.batch_id = options.batchId;
                if (options.subId && !options.subId.toString().startsWith('aicand_')) {
                    params.submission_id = options.subId.toString().replace('ai_', '');
                }
            }

            const resp = await axios.get(`${API_BASE_URL}/ai/submissions/`, { params });
            let submissions = resp.data?.results || resp.data || [];

            // If no results with batch filters, try email alone as fallback
            if (submissions.length === 0 && params.candidate_email && (params.batch_name || params.batch_id)) {
                const fallbackParams = { candidate_email: params.candidate_email };
                const fallbackResp = await axios.get(`${API_BASE_URL}/ai/submissions/`, { params: fallbackParams });
                submissions = fallbackResp.data?.results || fallbackResp.data || [];
            }

            if (submissions.length > 0) {
                const sub = submissions[0];
                const newSub = {
                    ...sub,
                    submission_id: `ai_${sub.id}`,
                    candidate_name: sub.candidate_name,
                    candidate_email: sub.candidate_email,
                    assessment_name: sub.assessment?.display_name || sub.assessment?.name || 'AI Assessment'
                };
                setAiAssessments(prev => {
                    if (!prev.find(a => a.id === newSub.id)) {
                        return [...prev, newSub];
                    }
                    return prev;
                });
                return newSub;
            }
            return null;
        } catch (err) {
            console.error('Error fetching assessment by email:', err);
            return null;
        }
    };

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        setSearchParams({ tab });
        setSelected(new Set());
        setStatusFilter('all');
        setCurrentPage(1);
        setBatchPage(1);
        setSortField('score');
        setSortDirection('desc');
    };

    const getStatusStyle = (rawStatus) => {
        const s = rawStatus?.toLowerCase();
        if (s === 'selected' || s === 'resume passed') return { background: '#E6FBF5', color: '#05CD99' };
        if (s === 'hold' || s === 'on-hold') return { background: '#FFF8E1', color: '#F59E0B' };
        if (s === 'rejected' || s === 'resume failed') return { background: '#FFF5F5', color: '#EE5D50' };
        if (s === 'completed' || s === 'hired') return { background: '#E6FBF5', color: '#05CD99' };
        if (s === 'extraction failed') return { background: '#FFF5F5', color: '#EE5D50' };
        return { background: '#F4F7FE', color: '#A3AED0' };
    };

    const getStatusLabel = (rawStatus) => {
        const map = {
            'Resume Passed': 'Pass ',
            'Resume Failed': 'Fail ',
            'selected': 'Qualified ',
            'hold': 'Hold - Manual Review',
            'On-Hold': 'On-Hold ⚠️',
            'rejected': 'Not Qualified',
            'Qualified': 'Qualified ',
            'Not Qualified': 'Not Qualified',
            'Completed': 'Completed',
            'Hired': 'Hired',
            'New': 'Pending',
            'Invited': 'Invited',
            'Interview': 'Interviewing',
        };
        return map[rawStatus] || rawStatus;
    };

    const unifyAutomaticResults = (roleData) => {
        const candidateMap = {};

        // Gather all stage items
        const allItems = [];
        if (roleData.resume) roleData.resume.forEach(item => allItems.push({ ...item, _stageType: 'resume' }));
        if (roleData.assessment) roleData.assessment.forEach(item => allItems.push({ ...item, _stageType: 'assessment' }));
        if (roleData.interview) roleData.interview.forEach(item => allItems.push({ ...item, _stageType: 'interview' }));

        // Sort by date descending so the newest item sets the mapping fields first
        allItems.sort((a, b) => {
            const dateA = new Date(a.created_at || a.submitted_at || a.completed_at || 0).getTime();
            const dateB = new Date(b.created_at || b.submitted_at || b.completed_at || 0).getTime();
            return dateB - dateA;
        });

        allItems.forEach(item => {
            const sid = String(item.submission_id || '');
            const email = (item.email || item.candidate?.email || `anon_${item.submission_id || item.id}`).toLowerCase();
            const type = item._stageType;
            if (!candidateMap[email]) {
                candidateMap[email] = {
                    email,
                    full_name: item.full_name || item.candidate?.name || 'Candidate',
                    resume: null, assessment: null, interview: null,
                    batch_id: item.batch_id,
                    batch_name: item.batch_name,
                    identity_mismatch_detected: !!item.identity_mismatch_detected,
                    photo_update_pending: !!item.photo_update_pending,
                    ai_candidate_pk: item.ai_candidate_pk || null,
                    pending_identity_photo_url: item.pending_identity_photo_url || null,
                    original_identity_photo_url: item.original_identity_photo_url || null,
                    master_photo_url: item.master_photo_url || null,
                    candidate_photo_url: item.candidate_photo_url || null,
                };
            } else {
                // Merge photo fields from later items if current entry has nulls
                const c = candidateMap[email];
                if (!c.master_photo_url && item.master_photo_url) c.master_photo_url = item.master_photo_url;
                if (!c.original_identity_photo_url && item.original_identity_photo_url) c.original_identity_photo_url = item.original_identity_photo_url;
                if (!c.pending_identity_photo_url && item.pending_identity_photo_url) c.pending_identity_photo_url = item.pending_identity_photo_url;
                if (!c.candidate_photo_url && item.candidate_photo_url) c.candidate_photo_url = item.candidate_photo_url;
                if (!c.ai_candidate_pk && item.ai_candidate_pk) c.ai_candidate_pk = item.ai_candidate_pk;
                if (item.identity_mismatch_detected) c.identity_mismatch_detected = true;
                if (item.photo_update_pending) c.photo_update_pending = true;
            }
            if (!candidateMap[email][type]) {
                candidateMap[email][type] = item;
            }
        });

        return Object.values(candidateMap).map(c => ({
            ...c,
            _type: 'fully_automatic_candidate',
            _deleteKey: c.email
        }));
    };

    const isPass = (r, type) => {
        if (type === 'fully_automatic') {
            if (r.interview) return isPass(r.interview, 'interview');
            if (r.assessment) return isPass(r.assessment, 'assessment');
            if (r.resume) return isPass(r.resume, 'resume');
            return false;
        }
        if (type === 'resume') return r.status === 'Resume Passed' || (r.status !== 'Resume Failed' && r.resume_score > 0 && r.resume_score >= 70);
        if (type === 'assessment') return r.status === 'selected' || r.status === 'Qualified' || (r.percentage != null && r.percentage >= 50);
        if (type === 'interview') {
            const possible = 140; // Always 14 questions * 10 points max
            return r.status === 'Completed' || (r.score != null && (r.score / possible) >= 0.5);
        }
        return false;
    };

    // ── Score extraction helper for sorting ──
    const getScoreValue = (r) => {
        if (activeTab === 'resume') return r.resume_score || 0;
        if (activeTab === 'assessment' || activeTab === 'standard') return r.percentage ?? 0;
        if (activeTab === 'interview') {
            if (r.interview_summary?.length > 0) {
                return Math.round((r.interview_summary.reduce((s, q) => s + (parseInt(q.score || q.marks) || 0), 0) / 140) * 100);
            }
            return 0;
        }
        if (activeTab === 'fully_automatic') {
            // Use best available stage score
            if (r.interview?.interview_summary?.length > 0) {
                return Math.round((r.interview.interview_summary.reduce((s, q) => s + (parseInt(q.score || q.marks) || 0), 0) / 140) * 100);
            }
            if (r.assessment) return r.assessment.percentage ?? 0;
            if (r.resume) return r.resume.resume_score ?? 0;
        }
        return 0;
    };

    const handleSort = (field) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('desc');
        }
        setCurrentPage(1);
    };

    // ── CSV export for candidates (selected or all) ──
    const exportResultsCSV = () => {
        // If some items are selected, export only those. Otherwise, export all current filtered/sorted rows.
        const items = selected.size > 0
            ? currentRows.filter(r => selected.has(r._deleteKey))
            : currentRows;

        if (items.length === 0) {
            showToast('error', 'No candidates to export.');
            return;
        }

        const headers = ['Name', 'Email', 'Role/Job Title', 'Score (%)', 'Status', 'Date'];
        const csvRows = [headers.join(',')];

        items.forEach(r => {
            const name = (r.full_name || r.candidate?.name || 'N/A').replace(/,/g, ' ');
            const email = (r.email || r.candidate?.email || 'N/A').replace(/,/g, ' ');
            const role = (r.batch_name || r.job_title || r.assessment?.name || r.assessment?.display_name || 'N/A').replace(/,/g, ' ');
            const score = getScoreValue(r);
            const status = activeTab === 'fully_automatic'
                ? (r.interview?.status || r.assessment?.status || r.resume?.status || 'N/A')
                : (r.status || 'N/A');

            // Use the most relevant date field available
            const rawDate = r.completed_at || r.submitted_at || r.created_at || r.link_opened_at || r.submission_date || null;
            const date = rawDate ? new Date(rawDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A';

            csvRows.push([`"${name}"`, `"${email}"`, `"${role}"`, score, `"${status}"`, `"${date}"`].join(','));
        });

        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const batchLabel = selectedRole ? selectedRole.replace('AUTO_', '').replace('MANUAL_', '') : 'results';
        link.setAttribute('download', `VerifiHire_${batchLabel}_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        showToast('success', `Exported ${items.length} candidate(s) to CSV.`);
    };

    const getDataForActiveContext = () => {
        if (!selectedRole || !groupedData[selectedRole]) return [];
        const roleData = groupedData[selectedRole];
        if (activeTab === 'fully_automatic') return unifyAutomaticResults(roleData);
        if (activeTab === 'resume') return roleData.resume.map(r => ({ ...r, _type: 'candidate', _deleteKey: r.submission_id }));
        if (activeTab === 'assessment') return roleData.assessment.map(r => ({ ...r, _type: 'ai_assessment', _deleteKey: r.submission_id }));
        if (activeTab === 'interview') return roleData.interview.map(r => ({ ...r, _type: 'candidate', _deleteKey: r.submission_id }));
        if (activeTab === 'standard') return roleData.standard.map(r => ({ ...r, _type: 'manual_assessment', _deleteKey: r.submission_id }));
        return [];
    };

    const allRows = viewMode === 'detail' ? getDataForActiveContext() : [];

    const currentRows = (() => {
        let rows = statusFilter === 'all'
            ? allRows
            : allRows.filter(r => {
                const currentStatus = activeTab === 'fully_automatic' 
                    ? (r.interview?.status || r.assessment?.status || r.resume?.status) 
                    : r.status;
                
                const isOngoing = typeof currentStatus === 'string' && ['ongoing', 'started', 'in-progress'].includes(currentStatus.toLowerCase());

                if (statusFilter === 'on-hold') {
                    return currentStatus === 'On-Hold' || currentStatus === 'hold';
                }
                const pass = isPass(r, activeTab);
                if (statusFilter === 'pass') return pass && currentStatus !== 'On-Hold' && currentStatus !== 'hold' && !isOngoing;
                return !pass && currentStatus !== 'On-Hold' && currentStatus !== 'hold' && !isOngoing;
            });

        // Apply sorting (works for all tabs)
        if (sortField) {
            rows = [...rows].sort((a, b) => {
                let cmp = 0;
                if (sortField === 'score') {
                    cmp = getScoreValue(a) - getScoreValue(b);
                } else if (sortField === 'name') {
                    const nameA = (a.full_name || a.candidate?.name || '').toLowerCase();
                    const nameB = (b.full_name || b.candidate?.name || '').toLowerCase();
                    cmp = nameA.localeCompare(nameB);
                } else if (sortField === 'date') {
                    const dateA = new Date(a.created_at || a.submitted_at || a.completed_at || 0).getTime();
                    const dateB = new Date(b.created_at || b.submitted_at || b.completed_at || 0).getTime();
                    cmp = dateA - dateB;
                }
                return sortDirection === 'asc' ? cmp : -cmp;
            });
        }

        return rows;
    })();

    const itemsPerPage = 20;
    const indexOfLastRow = currentPage * itemsPerPage;
    const indexOfFirstRow = indexOfLastRow - itemsPerPage;
    const paginatedRows = currentRows.slice(indexOfFirstRow, indexOfLastRow);

    const allKeys = currentRows.map(r => r._deleteKey);
    const allSelected = allKeys.length > 0 && allKeys.every(k => selected.has(k));
    const someSelected = allKeys.some(k => selected.has(k));

    const toggleSelectAll = () => {
        if (allSelected) {
            setSelected(prev => { const s = new Set(prev); allKeys.forEach(k => s.delete(k)); return s; });
        } else {
            setSelected(prev => { const s = new Set(prev); allKeys.forEach(k => s.add(k)); return s; });
        }
    };

    const toggleSelect = (key) => {
        setSelected(prev => {
            const s = new Set(prev);
            s.has(key) ? s.delete(key) : s.add(key);
            return s;
        });
    };

    const requestDelete = (items) => {
        const isAdmin = myRole === 'company_admin' || myRole === 'application_admin';
        if (isAdmin) {
            if (window.confirm("CRITICAL: Once you delete, you cannot restore. Proceed?")) {
                performDelete(items, 'Internal Admin Cleanup');
            }
        } else {
            setConfirmDelete({ items });
        }
    };
    const cancelDelete = () => setConfirmDelete(null);

    const performDelete = async (items, reason) => {
        const ids = new Set(items.map(i => i._deleteKey));

        let actuallyDeletedCount = 0;
        let pendingRequestCount = 0;
        let failCount = 0;
        let requestMessage = '';

        await Promise.all(items.map(async (item) => {
            try {
                let resp;
                if (item.submission_id && item.submission_id.startsWith('aicand_')) {
                    const realId = item.submission_id.replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '');
                    resp = await axios.delete(`${API_BASE_URL}/ai-candidates/${realId}/`, { data: { reason } });
                } else if (item._type === 'candidate') {
                    const realId = String(item.submission_id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '');
                    resp = await axios.delete(`${API_BASE_URL}/ai-candidates/${realId}/`, { data: { reason } });
                } else if (item._type === 'ai_assessment') {
                    const subId = String(item.submission_id).replace('ai_', '').replace(/_(resume|interview|assessment)$/, '');
                    resp = await axios.delete(`${API_BASE_URL}/ai/submission/${subId}/`, { data: { reason } });
                } else if (item._type === 'fully_automatic_candidate') {
                    const realId = item.ai_candidate_pk || (item.interview?.submission_id || item.resume?.submission_id || item.assessment?.submission_id || '').replace('aicand_', '').replace(/_(resume|interview|assessment)$/, '');
                    if (realId) {
                        resp = await axios.delete(`${API_BASE_URL}/ai-candidates/${realId}/`, { data: { reason } });
                    }
                }

                // Status 201 means it was just a pending request created, 200 means actually deleted
                if (resp && resp.status === 201) {
                    pendingRequestCount++;
                } else if (resp && resp.status === 200) {
                    actuallyDeletedCount++;
                }

                if (resp?.data?.message && !requestMessage) requestMessage = resp.data.message;
            } catch (err) {
                console.error('Delete failed for', item._deleteKey, err);
                failCount++;
            }
        }));

        if (actuallyDeletedCount > 0 || pendingRequestCount > 0) {
            setSelected(prev => { const s = new Set(prev); ids.forEach(k => s.delete(k)); return s; });
        }

        if (actuallyDeletedCount > 0) {
            setAiAssessments(prev => prev.filter(r => !ids.has(r.submission_id)));
            fetchData();
        }

        if (requestMessage) {
            showToast(actuallyDeletedCount > 0 ? 'success' : 'info', requestMessage);
        } else if (actuallyDeletedCount > 0 && failCount === 0) {
            showToast('success', `${actuallyDeletedCount} result${actuallyDeletedCount > 1 ? 's' : ''} deleted.`);
        } else if (pendingRequestCount > 0 && failCount === 0) {
            showToast('info', `${pendingRequestCount} deletion request(s) submitted.`);
        } else if (failCount > 0) {
            showToast('error', `${failCount} deletion(s) failed.`);
        }
    };

    const confirmAndDelete = async (reason) => {
        if (!confirmDelete) return;
        const items = confirmDelete.items;
        setConfirmDelete(null);
        await performDelete(items, reason);
    };

    const selectedItems = currentRows.filter(r => selected.has(r._deleteKey));

    const selectedCount = selectedItems.length;

    const handleRoleClick = (roleName) => {
        setSelectedRole(roleName);
        setViewMode('detail');
        setSearchParams({ tab: activeTab });
        setCurrentPage(1);
    };

    const handleBackToOverview = () => {
        setViewMode('overview');
        setSelectedRole(null);
        setShowTranscriptDetail(null);
    };

    const renderTranscriptReport = (data) => {
        if (!data) return null;
        // Total possible marks is always strictly 140 (14 questions * 10 points max)
        const totalPossible = 140;
        const baseScore = data.score || 0;
        const basePercentage = Math.round((baseScore / totalPossible) * 100);

        // Integrity Score (no penalty on raw score — only affects status)
        const integrityScore = data.integrity?.integrity_score ?? 100;
        const finalPercentage = basePercentage;

        return (
            <div className="report-container">
                <div className="report-header">
                    <div className="report-title-section" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                        <button className="report-breadcrumb" onClick={() => setViewMode('detail')} style={{ margin: 0 }}>
                            <i className="fa-solid fa-arrow-left"></i> Back
                        </button>
                        <h1 style={{ fontSize: '1.4rem', fontWeight: '900', color: '#1e293b', margin: 0 }}>Interview Report</h1>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0, fontWeight: '600', opacity: 0.8 }}>Performance breakdown & transcript</p>
                    </div>

                    <button
                        onClick={() => handleDownloadReport(data)}
                        disabled={downloadingId !== null}
                        className="download-report-btn"
                        style={{
                            background: '#4F46E5', color: 'white', border: 'none',
                            padding: '0.7rem 1.4rem', borderRadius: '12px', fontWeight: '800',
                            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
                            boxShadow: '0 4px 12px rgba(79, 70, 229, 0.25)',
                            transition: 'all 0.2s'
                        }}
                    >
                        {downloadingId !== null ? (
                            <i className="fa-solid fa-spinner fa-spin"></i>
                        ) : (
                            <i className="fa-solid fa-file-pdf"></i>
                        )}
                        {downloadingId !== null ? 'Generating PDF...' : 'Download Full PDF Report'}
                    </button>
                </div>

                <div className="report-grid">
                    <aside className="report-sidebar">
                        <div className="sidebar-card">
                            <span className="sidebar-label">Candidate</span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', color: '#4F46E5' }}>
                                    <i className="fa-solid fa-user"></i>
                                </div>
                                <div>
                                    <div className="sidebar-value">{data.full_name || data.candidate?.name || 'Extraction Failed'}</div>
                                    <div style={{ fontSize: '0.85rem', color: '#64748b' }}>{data.email || data.candidate?.email || 'N/A'}</div>
                                    {data.identity_mismatch_detected && (
                                        <div style={{
                                            marginTop: '0.5rem',
                                            background: '#FFF5F5',
                                            color: '#EE5D50',
                                            padding: '0.3rem 0.6rem',
                                            borderRadius: '8px',
                                            fontSize: '0.7rem',
                                            fontWeight: '800',
                                            display: 'inline-flex',
                                            alignItems: 'center',
                                            gap: '4px',
                                            border: '1px solid #EE5D5033'
                                        }}>
                                            <i className="fa-solid fa-triangle-exclamation"></i>
                                            Identity Mismatch
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="sidebar-card">
                            <span className="sidebar-label">Overall Performance</span>
                            <div style={{ fontSize: '2.2rem', fontWeight: '900', color: '#4F46E5', lineHeight: 1 }}>{finalPercentage}%</div>
                            <div style={{ width: '100%', height: '6px', background: '#f1f5f9', borderRadius: '3px', marginTop: '0.6rem', overflow: 'hidden' }}>
                                <div style={{ width: `${finalPercentage}%`, height: '100%', background: 'linear-gradient(90deg, #4f46e5, #9333ea)', borderRadius: '3px' }}></div>
                            </div>
                            {integrityScore < 75 && (
                                <p style={{ fontSize: '0.7rem', color: '#EE5D50', marginTop: '0.5rem', fontWeight: '700' }}>
                                    <i className="fa-solid fa-triangle-exclamation" style={{ marginRight: '4px' }}></i>
                                    Integrity Score: {Math.round(integrityScore)}% (below 75% threshold)
                                </p>
                            )}
                        </div>

                        <div className="sidebar-card">
                            <span className="sidebar-label">Total Marks</span>
                            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.3rem' }}>
                                <div style={{ fontSize: '1.8rem', fontWeight: '900', color: '#059669' }}>{data.score || 0}</div>
                                <div style={{ color: '#94a3b8', fontSize: '0.9rem', fontWeight: '700' }}>/ {totalPossible}</div>
                            </div>
                        </div>

                        {/* Integrity Evidence Gallery */}
                        {(timelineLogs?.length > 0 || data.integrity_screenshots?.length > 0 || data.integrity_logs?.length > 0) && (
                            <div className="sidebar-card">
                                <span className="sidebar-label">Integrity Evidence</span>
                                <div className="integrity-gallery-scroll">
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
                                        {(timelineLogs?.length > 0 ? timelineLogs.filter(l => l.phase === 'INTEGRITY' || String(l.id || '').startsWith('integrity_') || l.has_screenshot || l.has_webcam_screenshot || l.screenshot_base64 || l.webcam_screenshot_base64 || l.screenshot_url || l.webcam_screenshot_url) : (data.integrity_screenshots || data.integrity_logs || [])).map((log, lIdx) => {
                                            const eventLower = (log.event_type || '').toLowerCase();
                                            const isScreenEvent = ['tab_switch', 'window_blur', 'screen_stop'].includes(eventLower);

                                            const hasScreen = log.has_screenshot || log.screenshot_base64 || log.screenshot_url;
                                            const hasWebcam = log.has_webcam_screenshot || log.webcam_screenshot_base64 || log.webcam_screenshot_url;

                                            // Determine which image type to show and what source to use
                                            const imgType = (isScreenEvent && hasScreen) ? 'screen' : (hasWebcam ? 'webcam' : 'screen');
                                            const fallbackUrl = imgType === 'screen' ? log.screenshot_url : log.webcam_screenshot_url;
                                            const fallbackBase64 = imgType === 'screen' ? log.screenshot_base64 : log.webcam_screenshot_base64;

                                            return (
                                                <div key={lIdx} style={{
                                                    position: 'relative', borderRadius: '12px', overflow: 'hidden',
                                                    border: '1px solid #E2E8F0', boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                                                    cursor: 'pointer', aspectRatio: '1/1'
                                                }}>
                                                    {(!hasScreen && !hasWebcam) ? (
                                                        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F8F9FA' }}>
                                                            <i className="fa-solid fa-clock-rotate-left" style={{ fontSize: '1.5rem', color: '#CBD5E1' }}></i>
                                                        </div>
                                                    ) : (
                                                        <LazyIntegrityImage
                                                            screenshotId={log.screenshot_id}
                                                            type={imgType}
                                                            fallbackBase64={fallbackBase64}
                                                            fallbackUrl={fallbackUrl}
                                                            alt={log.event_type}
                                                            style={{ width: '100%', height: '100%' }}
                                                        />
                                                    )}
                                                    <div style={{
                                                        position: 'absolute', bottom: 0, left: 0, right: 0,
                                                        background: 'rgba(27, 37, 75, 0.85)', color: 'white',
                                                        fontSize: '9px', padding: '4px 2px', textAlign: 'center',
                                                        fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.5px'
                                                    }}>
                                                        {(log.event_type || '').replace(/_/g, ' ')}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                                <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.75rem', fontWeight: '500' }}>
                                    <i className="fa-solid fa-circle-info" style={{ marginRight: '4px' }}></i>
                                    Click images to enlarge
                                </p>
                            </div>
                        )}

                        <div className="sidebar-card" style={{ background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)', color: 'white' }}>
                            <span className="sidebar-label" style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.6rem' }}>Applied Role</span>
                            <div style={{ fontSize: '1rem', fontWeight: '800' }}>{selectedRole ? selectedRole.replace('AUTO_', '').replace('MANUAL_', '') : (data.job_title || 'General')}</div>
                        </div>
                    </aside>

                    <main className="report-main">
                        <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem', display: 'flex', alignItems: 'baseline', gap: '1rem' }}>
                            <h2 style={{ fontSize: '1.2rem', fontWeight: '900', color: '#1e293b', margin: 0 }}>Conversation Transcript</h2>
                            <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0, fontWeight: '500' }}>Full record of candidate responses</p>
                        </div>

                        <div className="transcript-timeline">
                            {(!data.interview_summary || data.interview_summary.length === 0) ? (
                                (data.full_conversation && data.full_conversation.length > 0) ? (
                                    <div className="raw-transcript">
                                        <div style={{ padding: '1rem', background: '#FEF3C7', color: '#92400E', borderRadius: '8px', marginBottom: '2rem', fontSize: '0.9rem', fontWeight: '600' }}>
                                            <i className="fa-solid fa-circle-info" style={{ marginRight: '8px' }}></i>
                                            Candidate exited before completing any scored answers. Showing raw chat history below:
                                        </div>
                                        {data.full_conversation.map((msg, i) => (
                                            <div key={i} className="timeline-turn" style={{ borderLeft: msg.sender === 'ai' ? '3px solid #8B5CF6' : '3px solid #10B981', opacity: 0.9 }}>
                                                <div className="ai-prompt" style={{ marginBottom: 0 }}>
                                                    <div className="ai-icon" style={{ background: msg.sender === 'ai' ? '#ede9fe' : '#d1fae5', color: msg.sender === 'ai' ? '#8B5CF6' : '#10B981' }}>
                                                        <i className={`fa-solid ${msg.sender === 'ai' ? 'fa-robot' : 'fa-user'}`}></i>
                                                    </div>
                                                    <div className="ai-text">
                                                        <span className="ai-label">{msg.sender === 'ai' ? 'Indu (AI Interviewer)' : 'Candidate'}</span>
                                                        <p className="ai-question" style={{ fontWeight: msg.sender === 'user' ? '400' : '600', color: msg.sender === 'user' ? '#475569' : '#1e293b' }}>
                                                            {msg.text || msg.content || <span style={{ fontStyle: 'italic', opacity: 0.5 }}>[Silent/Skipped]</span>}
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div style={{ textAlign: 'center', color: '#A3AED0', padding: '3rem' }}>
                                        <i className="fa-solid fa-microphone-slash" style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}></i>
                                        <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>No conversational data recorded.</p>
                                    </div>
                                )
                            ) : (
                                data.interview_summary.map((turn, i) => (
                                    <div key={i} className="timeline-turn" style={turn.is_clarification ? { opacity: 0.85, borderLeft: '3px solid #60a5fa' } : {}}>
                                        {turn.is_clarification ? (
                                            <div className="marks-badge" style={{
                                                background: '#eff6ff',
                                                color: '#2563eb'
                                            }}>
                                                <i className="fa-solid fa-rotate-right" style={{ marginRight: '4px', fontSize: '0.7rem' }}></i>
                                                Clarification
                                            </div>
                                        ) : (
                                            <div className="marks-badge" style={{
                                                background: (turn.score || turn.marks) >= 7 ? '#ecfdf5' : (turn.score || turn.marks) >= 4 ? '#fffbeb' : '#fff1f2',
                                                color: (turn.score || turn.marks) >= 7 ? '#059669' : (turn.score || turn.marks) >= 4 ? '#b45309' : '#e11d48'
                                            }}>
                                                {(turn.score || turn.marks)}/10 Points
                                            </div>
                                        )}

                                        <div className="ai-prompt">
                                            <div className="ai-icon">
                                                <i className="fa-solid fa-robot"></i>
                                            </div>
                                            <div className="ai-text">
                                                <span className="ai-label">Indu (AI Interviewer)</span>
                                                <p className="ai-question">{turn.question}</p>
                                            </div>
                                        </div>

                                        <div className="candidate-block">
                                            <span className="candidate-label">{turn.is_clarification ? 'Candidate Request' : 'Candidate Response'}</span>
                                            <p className="candidate-answer">
                                                {turn.answer || <span style={{ fontStyle: 'italic', opacity: 0.5 }}>[Candidate remained silent/skipped]</span>}
                                            </p>
                                        </div>

                                        {(turn.reason || turn.justification) && (
                                            <div style={{ marginTop: '1.5rem', padding: '1rem 1.5rem', background: turn.is_clarification ? '#EFF6FF' : '#F1F5F9', borderRadius: '12px', borderLeft: `4px solid ${turn.is_clarification ? '#3b82f6' : '#4F46E5'}`, fontSize: '0.9rem' }}>
                                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: turn.is_clarification ? '#3b82f6' : '#4F46E5', textTransform: 'uppercase', marginBottom: '0.3rem' }}>{turn.is_clarification ? 'Note' : 'AI Feedback'}</div>
                                                <p style={{ margin: 0, color: '#475569', fontWeight: '600', lineHeight: 1.5 }}>{turn.reason || turn.justification}</p>
                                            </div>
                                        )}
                                    </div>
                                ))
                            )}
                        </div>
                    </main>
                </div>
            </div>
        );
    };

    return (
        <div className="results-page">
            <div className="bg-shape shape-1"></div>
            <div className="bg-shape shape-2"></div>
            <div className="bg-shape shape-3"></div>

            {toast && (
                <div style={{
                    position: 'fixed', top: '6.5rem', right: '1.5rem', zIndex: 9999,
                    background: toast.type === 'success' ? '#ECFDF5' : '#FFF5F5',
                    border: `1px solid ${toast.type === 'success' ? '#6EE7B7' : '#FECACA'}`,
                    color: toast.type === 'success' ? '#065F46' : '#B91C1C',
                    padding: '0.9rem 1.4rem', borderRadius: '12px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                    display: 'flex', alignItems: 'center', gap: '0.6rem', fontWeight: '600',
                }}>
                    <i className={`fa-solid ${toast.type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}`} />
                    {toast.message}
                </div>
            )}

            {confirmDelete && (
                <div className="glass-modal-overlay">
                    <div className="glass-modal-content" style={{ padding: '2.5rem', maxWidth: '420px', width: '90%', textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🗑️</div>
                        <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: '#111827', marginBottom: '0.5rem' }}>
                            {confirmDelete.items.length > 1 ? `Delete ${confirmDelete.items.length} Results` : 'Delete Result'}?
                        </h2>
                        <p style={{ color: '#475569', marginBottom: '1.25rem', lineHeight: '1.6', fontSize: '0.95rem' }}>
                            {confirmDelete.items.length === 1
                                ? <>This will initiate a deletion request for <strong>{confirmDelete.items[0].full_name || confirmDelete.items[0].candidate?.name || 'this candidate'}</strong>.</>
                                : <>This will initiate a deletion request for <strong>{confirmDelete.items.length} selected results</strong>.</>}
                        </p>

                        <div style={{ marginBottom: '1.5rem', textAlign: 'left' }}>
                            <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#64748b', display: 'block', marginBottom: '0.5rem' }}>Reason for Deletion (Required)</label>
                            <textarea
                                id="delete-reason-input"
                                style={{ width: '100%', borderRadius: '8px', border: '1px solid #e2e8f0', padding: '0.75rem', fontSize: '0.9rem', minHeight: '80px', fontFamily: 'inherit' }}
                                placeholder="Please provide a valid reason..."
                                required
                            />
                        </div>

                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                            <button onClick={cancelDelete} style={{ padding: '0.7rem 1.5rem', border: '1px solid #cbd5e1', borderRadius: '12px', background: 'white', cursor: 'pointer', fontWeight: '700' }}>Cancel</button>
                            <button
                                onClick={() => {
                                    const reason = document.getElementById('delete-reason-input')?.value;
                                    if (!reason || reason.trim().length < 5) {
                                        alert("Please provide a meaningful reason (at least 5 characters).");
                                        return;
                                    }
                                    confirmAndDelete(reason);
                                }}
                                style={{ padding: '0.7rem 1.5rem', border: 'none', borderRadius: '12px', background: '#EF4444', color: 'white', cursor: 'pointer', fontWeight: '700' }}
                            >
                                Submit Request
                            </button>
                        </div>
                    </div>
                </div>
            )}


            {viewedSubmission && (
                <div className="glass-modal-overlay" style={{ zIndex: 10000, background: 'rgba(27, 37, 75, 0.4)', backdropFilter: 'blur(8px)' }}>
                    <div className="glass-modal-content" style={{
                        width: '95%', maxWidth: '1200px', height: '90vh',
                        display: 'flex', flexDirection: 'column', padding: 0,
                        background: '#F4F7FE', borderRadius: '30px'
                    }}>
                        {/* Modal Header */}
                        <div style={{
                            padding: '1.5rem 2.5rem', background: 'white', borderBottom: '1px solid #E2E8F0',
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            borderTopLeftRadius: '30px', borderTopRightRadius: '30px'
                        }}>
                            <div>
                                <h2 style={{ fontSize: '1.5rem', fontWeight: '900', color: '#1B254B', margin: 0 }}>
                                    {viewedSubmission.candidate_name} <span style={{ color: '#707EAE', fontWeight: '400', fontSize: '1.1rem' }}>Review</span>
                                </h2>
                                <p style={{ fontSize: '0.9rem', color: '#A3AED0', margin: '0.25rem 0 0', fontWeight: '600' }}>
                                    Assessment: <span style={{ color: '#4318FF' }}>{viewedSubmission.assessment_name}</span>
                                    <span style={{ margin: '0 0.75rem', color: '#CBD5E1' }}>|</span>
                                    Submitted {new Date(viewedSubmission.submitted_at).toLocaleString()}
                                </p>
                            </div>
                            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                                <button
                                    onClick={() => handleDownloadReport({ ...viewedSubmission, submission_id: `ai_${viewedSubmission.id}`, full_name: viewedSubmission.candidate_name })}
                                    disabled={downloadingId !== null}
                                    style={{
                                        padding: '0.6rem 1.2rem', background: 'white', color: '#4318FF',
                                        border: '1px solid #E2E8F0', borderRadius: '12px', fontWeight: '800',
                                        cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px',
                                        boxShadow: '0 4px 10px rgba(0,0,0,0.03)', fontSize: '0.85rem'
                                    }}
                                >
                                    {downloadingId === String(viewedSubmission.id) ? (
                                        <i className="fa-solid fa-spinner fa-spin" />
                                    ) : (
                                        <i className="fa-solid fa-file-pdf" />
                                    )}
                                    {downloadingId === String(viewedSubmission.id) ? 'Generating...' : 'Download Report'}
                                </button>
                                <button
                                    onClick={() => {
                                        const newParams = new URLSearchParams(searchParams);
                                        newParams.delete('subId');
                                        setSearchParams(newParams);
                                    }}
                                    style={{
                                        background: '#F4F7FE', border: 'none', borderRadius: '50%',
                                        width: '44px', height: '44px', cursor: 'pointer',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        color: '#4318FF', transition: 'all 0.2s', boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
                                    }}
                                >
                                    <i className="fa-solid fa-xmark" style={{ fontSize: '1.25rem' }} />
                                </button>
                            </div>
                        </div>

                        {/* Modal Body */}
                        <div style={{ flex: 1, overflowY: 'auto', padding: '2.5rem' }}>
                            <div style={{ maxWidth: '1000px', margin: '0 auto' }}>

                                {/* 3-Card Summary (Matching AiAssessmentDetail.js) */}

                                {viewedSubmission._type === 'ai_interview' ? (
                                    <div style={{ marginBottom: '3rem' }}>
                                        <div style={{ background: '#F8F9FF', padding: '2.5rem', borderRadius: '30px', border: '1px solid #4318FF44' }}>
                                            <h4 style={{ color: '#1B254B', marginTop: 0, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.2rem', fontWeight: '800' }}>
                                                <i className="fa-solid fa-microphone-lines" style={{ color: '#4318FF' }}></i>
                                                AI Interview Transcript & Feedback
                                            </h4>
                                            <div style={{
                                                background: 'white',
                                                padding: '2rem',
                                                borderRadius: '20px',
                                                color: '#1B254B',
                                                lineHeight: '1.8',
                                                fontSize: '1rem',
                                                whiteSpace: 'pre-wrap',
                                                boxShadow: '0 10px 30px rgba(0,0,0,0.03)',
                                                border: '1px solid #E2E8F0'
                                            }}>
                                                {typeof viewedSubmission.interview_summary === 'string'
                                                    ? viewedSubmission.interview_summary
                                                    : JSON.stringify(viewedSubmission.interview_summary || viewedSubmission.results_breakdown?.interview_summary, null, 2)}
                                            </div>
                                        </div>
                                    </div>
                                ) : viewedSubmission._type === 'resume' ? (
                                    <div style={{ marginBottom: '3rem' }}>
                                        <div style={{ background: '#F8F9FF', padding: '2.5rem', borderRadius: '30px', border: '1px solid #4318FF44' }}>
                                            <h4 style={{ color: '#1B254B', marginTop: 0, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.2rem', fontWeight: '800' }}>
                                                <i className="fa-solid fa-file-pdf" style={{ color: '#4318FF' }}></i>
                                                Resume Screening Results
                                            </h4>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                                                <div style={{ background: 'white', padding: '1.5rem', borderRadius: '16px', border: '1px solid #E2E8F0', textAlign: 'center' }}>
                                                    <div style={{ color: '#64748B', fontSize: '0.9rem', fontWeight: '700', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Match Score</div>
                                                    <div style={{ color: '#4318FF', fontSize: '2.5rem', fontWeight: '900' }}>{viewedSubmission.resume_score}%</div>
                                                </div>
                                                <div style={{ background: 'white', padding: '1.5rem', borderRadius: '16px', border: '1px solid #E2E8F0', textAlign: 'center' }}>
                                                    <div style={{ color: '#64748B', fontSize: '0.9rem', fontWeight: '700', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Status</div>
                                                    <div style={{ color: viewedSubmission.resume_score >= 70 ? '#05CD99' : '#EE5D50', fontSize: '1.5rem', fontWeight: '800', marginTop: '0.5rem' }}>{viewedSubmission.status}</div>
                                                </div>
                                            </div>
                                            {viewedSubmission.interview_questions?.length > 0 && (
                                                <div style={{ background: 'white', padding: '2rem', borderRadius: '20px', border: '1px solid #E2E8F0' }}>
                                                    <h5 style={{ margin: '0 0 1rem 0', color: '#1B254B', fontSize: '1.1rem', fontWeight: '700' }}>Generated Interview Questions</h5>
                                                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#334155', lineHeight: '1.8' }}>
                                                        {viewedSubmission.interview_questions.map((q, idx) => (
                                                            <li key={idx} style={{ marginBottom: '0.5rem' }}>{q}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        {/* Assessment Report Header - Interview Report Style */}
                                        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                                            <h1 style={{
                                                color: '#4F46E5',
                                                fontSize: '2rem',
                                                fontWeight: '700',
                                                margin: '0 0 0.5rem 0'
                                            }}>
                                                VerifiHireAI — Assessment Report
                                            </h1>
                                            <h2 style={{
                                                color: '#1B254B',
                                                fontSize: '1.25rem',
                                                fontWeight: '600',
                                                margin: 0
                                            }}>
                                                Candidate: {viewedSubmission.candidate_name}
                                            </h2>
                                        </div>

                                        {/* Candidate Information Section */}
                                        <div style={{ marginBottom: '3rem' }}>
                                            <h3 style={{
                                                color: '#1B254B',
                                                fontSize: '1.1rem',
                                                fontWeight: '700',
                                                fontStyle: 'italic',
                                                marginBottom: '1rem'
                                            }}>
                                                Candidate Information
                                            </h3>

                                            {viewedSubmission.identity_mismatch_detected && (
                                                <div style={{
                                                    background: '#FEF2F2',
                                                    border: '1px solid #F87171',
                                                    borderRadius: '12px',
                                                    padding: '1rem',
                                                    marginBottom: '1.5rem',
                                                    display: 'flex',
                                                    alignItems: 'flex-start',
                                                    gap: '1rem'
                                                }}>
                                                    <i className="fa-solid fa-triangle-exclamation" style={{ color: '#DC2626', fontSize: '1.5rem', marginTop: '4px' }}></i>
                                                    <div>
                                                        <h4 style={{ color: '#991B1B', margin: '0 0 0.5rem 0', fontWeight: 'bold' }}>IDENTITY MISMATCH DETECTED (HR REVIEW REQUIRED)</h4>
                                                        <p style={{ color: '#7F1D1D', margin: 0, fontSize: '0.9rem', lineHeight: '1.4' }}>
                                                            The candidate failed the automated facial verification check when starting the assessment.
                                                            They chose to "Override & Continue", meaning the assessment was completed using a <strong>different face</strong> than what was initially registered.
                                                            Please compare the original face with the overriding assessment face below.
                                                        </p>
                                                    </div>
                                                </div>
                                            )}

                                            {(() => {
                                                // Get candidate photo - use intruder/assessment photo when mismatch detected (same as Box 2),
                                                // otherwise use backend-provided URL, then fall back to integrity screenshot via lazy load
                                                let candidatePhoto = viewedSubmission.identity_mismatch_detected
                                                    ? (viewedSubmission.pending_identity_photo_url || viewedSubmission.intruder_photo_url || viewedSubmission.candidate_photo_url || null)
                                                    : (viewedSubmission.candidate_photo_url || null);

                                                if (!candidatePhoto) {
                                                    const logs = timelineLogs?.length > 0 ? timelineLogs.filter(l => l.phase === 'INTEGRITY' || String(l.id || '').startsWith('integrity_') || l.has_webcam_screenshot || l.webcam_screenshot_base64 || l.webcam_screenshot_url) : (viewedSubmission.integrity_screenshots || viewedSubmission.integrity_logs || []);
                                                    const sortedLogs = [...logs].sort((a, b) => {
                                                        const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
                                                        const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
                                                        return timeA - timeB;
                                                    });
                                                    const firstWebcam = sortedLogs.find(log => {
                                                        if (log.event_type && log.event_type.toLowerCase().includes('face_not_detected')) return false;
                                                        return log.webcam_screenshot_url || log.webcam_screenshot_base64 || log.has_webcam_screenshot;
                                                    });
                                                    if (firstWebcam) {
                                                        candidatePhoto = firstWebcam.webcam_screenshot_url || firstWebcam.webcam_screenshot_base64 || null;
                                                    }
                                                }
                                                // Normalize the URL
                                                candidatePhoto = normalizeImageUrl(candidatePhoto);

                                                // Find the screenshot_id for lazy loading if no direct image available
                                                const candidatePhotoScreenshotId = !candidatePhoto ? (() => {
                                                    const logs = timelineLogs?.length > 0 ? timelineLogs.filter(l => (l.phase === 'INTEGRITY' || String(l.id || '').startsWith('integrity_')) && l.has_webcam_screenshot) : [];
                                                    const sorted = [...logs].sort((a, b) => {
                                                        const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
                                                        const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
                                                        return timeA - timeB;
                                                    });
                                                    const first = sorted.find(log => {
                                                        if (log.event_type && log.event_type.toLowerCase().includes('face_not_detected')) return false;
                                                        return log.has_webcam_screenshot;
                                                    });
                                                    return first?.screenshot_id || null;
                                                })() : null;

                                                return (
                                                    <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flexShrink: 0 }}>

                                                            {/* Always show single registered face at top */}
                                                            <div style={{
                                                                width: '180px', height: '180px', background: '#F4F7FE',
                                                                borderRadius: '12px', display: 'flex', alignItems: 'center',
                                                                justifyContent: 'center', overflow: 'hidden',
                                                                border: '1px solid #E0E5F2'
                                                            }}>
                                                                {candidatePhoto ? (
                                                                    <img src={candidatePhoto} alt="Candidate" style={{ width: '100%', height: '100%', objectFit: 'cover' }} onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
                                                                ) : candidatePhotoScreenshotId ? (
                                                                    <LazyIntegrityImage
                                                                        screenshotId={candidatePhotoScreenshotId}
                                                                        type="webcam"
                                                                        alt="Candidate"
                                                                        style={{ width: '100%', height: '100%' }}
                                                                    />
                                                                ) : null}
                                                                <div style={{ display: (candidatePhoto || candidatePhotoScreenshotId) ? 'none' : 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                                    <i className="fa-solid fa-user" style={{ fontSize: '4rem', color: '#A3AED0' }}></i>
                                                                </div>
                                                            </div>

                                                            {viewedSubmission.pan_photo && (
                                                                <div style={{ width: '180px', height: '120px', background: '#F4F7FE', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #E0E5F2', overflow: 'hidden' }}>
                                                                    <img src={viewedSubmission.pan_photo} alt="PAN Card" style={{ width: '100%', height: '100%', objectFit: 'contain' }} onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }} />
                                                                    <div style={{ display: 'none', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                                        <i className="fa-solid fa-id-card" style={{ fontSize: '4rem', color: '#A3AED0' }}></i>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                        <div style={{ flex: 1 }}>
                                                            <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', border: '1px solid #E0E5F2', borderRadius: '12px', overflow: 'hidden' }}>
                                                                <tbody>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B', width: '35%' }}>Full Name</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B' }}>{viewedSubmission.candidate_name}</td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Email</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B' }}>{viewedSubmission.candidate_email || 'N/A'}</td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Phone</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B' }}>{viewedSubmission.phone || 'N/A'}</td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>PAN Number</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B', fontWeight: '700' }}>{viewedSubmission.pan_number || 'N/A'}</td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>PAN Verified</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: viewedSubmission.pan_verified ? '#05CD99' : '#EE5D50', fontWeight: '700' }}>{viewedSubmission.pan_verified ? '✓ Verified' : '✗ Not Verified'}</td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Job Title</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B' }}>{viewedSubmission.assessment?.name || viewedSubmission.assessment?.display_name || viewedSubmission.job_title || viewedSubmission.role || viewedSubmission.role_title || viewedSubmission.required_skills || 'N/A'}</td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>MCQ Score</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B', fontWeight: '700' }}>
                                                                            {viewedSubmission.results_breakdown?.mcq?.possible_points > 0 ? Math.round((viewedSubmission.results_breakdown.mcq.scored_points / viewedSubmission.results_breakdown.mcq.possible_points) * 100) : 0}% ({viewedSubmission.results_breakdown?.mcq?.scored_points || 0} / {viewedSubmission.candidate_questions?.mcqs?.length || 0} Correct)
                                                                        </td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Coding Score</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B', fontWeight: '700' }}>
                                                                            {viewedSubmission.results_breakdown?.coding?.possible_points > 0 ? Math.round((viewedSubmission.results_breakdown.coding.scored_points / viewedSubmission.results_breakdown.coding.possible_points) * 100) : 0}% ({viewedSubmission.results_breakdown?.coding?.scored_points || 0} / {viewedSubmission.results_breakdown?.coding?.possible_points || 0} pts)
                                                                        </td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Integrity Score</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: (viewedSubmission.integrity?.integrity_score ?? 100) >= 50 ? '#05CD99' : '#EE5D50', fontWeight: '700' }}>
                                                                            {viewedSubmission.integrity?.integrity_score ?? 100}% {(viewedSubmission.integrity?.integrity_score ?? 100) >= 50 ? '✓ Reliable' : '⚠ Suspicious'}
                                                                        </td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Overall Result</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: (viewedSubmission.status === 'selected' || viewedSubmission.status === 'Qualified') ? '#05CD99' : (viewedSubmission.status === 'hold' || viewedSubmission.status === 'On-Hold') ? '#F59E0B' : '#EE5D50', fontWeight: '800' }}>
                                                                            {viewedSubmission.percentage}%
                                                                        </td>
                                                                    </tr>
                                                                    <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Status</td>
                                                                        <td style={{ padding: '0.75rem 1rem', fontWeight: '700', textTransform: 'uppercase' }}>
                                                                            {(() => {
                                                                                const st = viewedSubmission.status;
                                                                                if (st === 'selected' || st === 'Qualified') return <span style={{ color: '#05CD99' }}>✓ Assessment Passed</span>;
                                                                                if (st === 'hold' || st === 'On-Hold') return <span style={{ color: '#F59E0B' }}>⚠ HOLD — Manual Review Required</span>;
                                                                                return <span style={{ color: '#EE5D50' }}>✗ Not Qualified</span>;
                                                                            })()}
                                                                        </td>
                                                                    </tr>
                                                                    <tr>
                                                                        <td style={{ padding: '0.75rem 1rem', background: '#F8F9FF', fontWeight: '600', color: '#1B254B' }}>Submission Date</td>
                                                                        <td style={{ padding: '0.75rem 1rem', color: '#1B254B' }}>{viewedSubmission.submitted_at ? new Date(viewedSubmission.submitted_at).toLocaleString('en-US', { month: 'long', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A'}</td>
                                                                    </tr>
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                );
                                            })()}

                                        </div>
                                    </>
                                )}

                                {!viewedSubmission.is_resume_screening && (
                                    <>
                                        {/* Answer Verification (MCQs) */}
                                        <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-list-check" style={{ color: '#4318FF' }}></i> MCQ Answer Verification
                                        </h4>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '4rem' }}>
                                            {viewedSubmission.candidate_questions?.mcqs?.map((q, i) => {
                                                const candAns = viewedSubmission.answers[`mcq_${i}`];
                                                const isCorrect = candAns === q.answer;
                                                return (
                                                    <div key={i} style={{
                                                        padding: '2rem', borderRadius: '30px',
                                                        border: '1px solid #E0E5F2', background: 'white',
                                                        boxShadow: '0 10px 30px rgba(0,0,0,0.02)'
                                                    }}>
                                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                                            <div style={{ flex: 1 }}>
                                                                <span style={{ fontSize: '0.75rem', fontWeight: '800', color: '#707EAE', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Question {i + 1}</span>
                                                                <p style={{ fontWeight: '700', color: '#1B254B', fontSize: '1.1rem', margin: '0.5rem 0 0', lineHeight: 1.5 }}>{q.question}</p>
                                                            </div>
                                                            <div style={{
                                                                padding: '0.5rem 1rem', borderRadius: '12px',
                                                                background: isCorrect ? '#E6FBF5' : '#FFF5F5',
                                                                color: isCorrect ? '#05CD99' : '#EE5D50',
                                                                fontWeight: '800', fontSize: '0.75rem',
                                                                display: 'flex', alignItems: 'center', gap: '6px',
                                                                border: `1px solid ${isCorrect ? '#05CD9944' : '#EE5D5044'}`
                                                            }}>
                                                                <i className={`fa-solid ${isCorrect ? 'fa-circle-check' : 'fa-circle-xmark'}`}></i>
                                                                {isCorrect ? 'CORRECT' : 'INCORRECT'}
                                                            </div>
                                                        </div>

                                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                                            {q.options.map((opt, oi) => {
                                                                const isSelected = opt === candAns;
                                                                const isAnswer = opt === q.answer;

                                                                let bg = 'white';
                                                                let border = '1px solid #E0E5F2';
                                                                let color = '#1B254B';
                                                                let icon = null;

                                                                if (isAnswer) {
                                                                    bg = '#E6FBF5';
                                                                    border = '2px solid #05CD99';
                                                                    color = '#05CD99';
                                                                    icon = <i className="fa-solid fa-check-circle" style={{ marginLeft: 'auto' }}></i>;
                                                                } else if (isSelected && !isCorrect) {
                                                                    bg = '#FFF5F5';
                                                                    border = '2px solid #EE5D50';
                                                                    color = '#EE5D50';
                                                                    icon = <i className="fa-solid fa-circle-xmark" style={{ marginLeft: 'auto' }}></i>;
                                                                }

                                                                return (
                                                                    <div key={oi} style={{
                                                                        padding: '1rem 1.25rem', background: bg, borderRadius: '16px', border,
                                                                        color: color, fontWeight: (isAnswer || isSelected) ? '700' : '500',
                                                                        fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '10px'
                                                                    }}>
                                                                        <span style={{ opacity: 0.5, fontSize: '0.8rem', flexShrink: 0 }}>{String.fromCharCode(65 + oi)}.</span>
                                                                        <span style={{ flex: 1 }}>{opt}</span>
                                                                        {icon}
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>

                                                        {!isCorrect && (
                                                            <div style={{
                                                                marginTop: '1.25rem', padding: '1rem 1.5rem',
                                                                background: 'linear-gradient(135deg, #E6FBF5, #D1F7ED)',
                                                                borderRadius: '16px', display: 'flex', alignItems: 'center', gap: '12px',
                                                                border: '1px solid #05CD9933'
                                                            }}>
                                                                <i className="fa-solid fa-circle-check" style={{ color: '#05CD99', fontSize: '1.2rem' }} />
                                                                <div>
                                                                    <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#05CD99', textTransform: 'uppercase' }}>Correct Solution</div>
                                                                    <div style={{ fontWeight: '700', color: '#1B254B', fontSize: '0.95rem' }}>{q.answer}</div>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </>
                                )}

                                {/* Coding Challenges */}
                                {viewedSubmission.candidate_questions?.coding_challenges?.length > 0 && (
                                    <div style={{ marginBottom: '4rem' }}>
                                        <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-code" style={{ color: '#4318FF' }}></i> Coding Verification
                                        </h4>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                                            {viewedSubmission.candidate_questions.coding_challenges.map((c, i) => {
                                                const candCode = viewedSubmission.answers[`coding_${i}`];
                                                const res = viewedSubmission.results_breakdown?.coding_results?.[c.id] || {};
                                                return (
                                                    <div key={i} style={{ background: 'white', borderRadius: '30px', padding: '2rem', border: '1px solid #E0E5F2', boxShadow: '0 10px 30px rgba(0,0,0,0.02)' }}>
                                                        <div style={{ marginBottom: '2rem' }}>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                                <div>
                                                                    <h5 style={{ color: '#1B254B', fontSize: '1.2rem', fontWeight: '800', margin: '0 0 0.5rem 0' }}>{c.title}</h5>
                                                                    <p style={{ color: '#707EAE', fontSize: '0.95rem', lineHeight: '1.5', margin: 0 }}>{c.problem_statement}</p>
                                                                </div>
                                                                <div style={{ textAlign: 'right', background: '#F4F7FE', padding: '0.5rem 1rem', borderRadius: '12px' }}>
                                                                    <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#A3AED0', textTransform: 'uppercase' }}>Passed Tests</div>
                                                                    <div style={{ fontSize: '1.2rem', fontWeight: '900', color: (res.passed || 0) === (res.total || c.test_cases?.length || 0) ? '#05CD99' : '#F59E0B' }}>
                                                                        {res.passed || 0}/{res.total || c.test_cases?.length || 0}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div style={{ position: 'relative' }}>
                                                            <div style={{
                                                                position: 'absolute', top: '-14px', left: '24px',
                                                                background: '#4318FF', color: 'white', padding: '4px 14px',
                                                                borderRadius: '8px', fontSize: '0.75rem', fontWeight: '800', zIndex: 1
                                                            }}>CANDIDATE SUBMISSION</div>
                                                            <div style={{
                                                                background: '#1B254B', borderRadius: '20px',
                                                                padding: '2.5rem 2rem 2rem', boxShadow: '0 15px 35px rgba(0,0,0,0.1)'
                                                            }}>
                                                                <pre style={{
                                                                    margin: 0, color: '#05CD99',
                                                                    fontFamily: "'Fira Code', 'Courier New', monospace",
                                                                    fontSize: '0.95rem', lineHeight: '1.6', whiteSpace: 'pre-wrap'
                                                                }}>
                                                                    {candCode || '// No code submitted'}
                                                                </pre>
                                                            </div>
                                                        </div>

                                                        {/* Reference Solution (Correct Answer) */}
                                                        {c.reference_solution && (
                                                            <div style={{ position: 'relative', marginTop: '1.5rem' }}>
                                                                <div style={{
                                                                    position: 'absolute', top: '-14px', left: '24px',
                                                                    background: '#05CD99', color: 'white', padding: '4px 14px',
                                                                    borderRadius: '8px', fontSize: '0.75rem', fontWeight: '800', zIndex: 1
                                                                }}>✓ REFERENCE SOLUTION (ANSWER KEY)</div>
                                                                <div style={{
                                                                    background: '#0D1117', borderRadius: '20px',
                                                                    padding: '2.5rem 2rem 2rem', boxShadow: '0 15px 35px rgba(0,0,0,0.1)',
                                                                    border: '1px solid #30363D'
                                                                }}>
                                                                    <pre style={{
                                                                        margin: 0, color: '#7EE787',
                                                                        fontFamily: "'Fira Code', 'Courier New', monospace",
                                                                        fontSize: '0.95rem', lineHeight: '1.6', whiteSpace: 'pre-wrap'
                                                                    }}>
                                                                        {c.reference_solution}
                                                                    </pre>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}

                                {/* Integrity Violations */}
                                {(timelineLogs?.length > 0 || viewedSubmission.integrity_screenshots?.length > 0 || viewedSubmission.integrity_logs?.length > 0) && (
                                    <div style={{ marginTop: '4rem' }}>
                                        <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-shield-halved" style={{ color: '#EE5D50' }}></i> Integrity Violations Log
                                        </h4>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                                            {(timelineLogs?.length > 0 ? timelineLogs.filter(l => l.phase === 'INTEGRITY' || String(l.id || '').startsWith('integrity_') || l.has_screenshot || l.has_webcam_screenshot || l.screenshot_base64 || l.webcam_screenshot_base64 || l.screenshot_url || l.webcam_screenshot_url) : (viewedSubmission.integrity_screenshots || viewedSubmission.integrity_logs || [])).map((snap, sIdx) => (
                                                <div key={sIdx} style={{ background: 'white', borderRadius: '20px', padding: '12px', border: '1px solid #E0E5F2', textAlign: 'center' }}>
                                                    <div style={{
                                                        width: '100%', height: '160px', background: '#F4F7FE',
                                                        borderRadius: '15px', overflow: 'hidden', marginBottom: '10px',
                                                        position: 'relative', border: '1px solid #E0E5F2'
                                                    }}>
                                                        {(!snap.has_screenshot && !snap.has_webcam_screenshot && !snap.screenshot_base64 && !snap.webcam_screenshot_base64 && !snap.screenshot_url && !snap.webcam_screenshot_url && !snap.details?.screenshot) ? (
                                                            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F8F9FA' }}>
                                                                <i className="fa-solid fa-clock-rotate-left" style={{ fontSize: '2.5rem', color: '#CBD5E1' }}></i>
                                                            </div>
                                                        ) : (
                                                            <LazyIntegrityImage
                                                                screenshotId={snap.screenshot_id}
                                                                type={snap.has_screenshot ? "screen" : "webcam"}
                                                                fallbackBase64={snap.has_screenshot ? snap.screenshot_base64 : snap.webcam_screenshot_base64}
                                                                fallbackUrl={snap.has_screenshot ? snap.screenshot_url : (snap.webcam_screenshot_url || snap.details?.screenshot)}
                                                                alt={snap.event_type}
                                                                style={{ width: '100%', height: '100%' }}
                                                            />
                                                        )}
                                                        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(27, 37, 75, 0.8)', color: 'white', fontSize: '0.65rem', padding: '6px', fontWeight: '700' }}>
                                                            {(snap.event_type || '').replace(/_/g, ' ').toUpperCase()}
                                                        </div>
                                                    </div>
                                                    <div style={{ color: '#A3AED0', fontSize: '0.75rem', fontWeight: '700' }}>
                                                        {snap.timestamp ? new Date(snap.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : ''}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* ── IDENTITY EVIDENCE — Two-face comparison ── */}
                                {viewedSubmission.identity_mismatch_detected && (
                                    <div style={{ marginTop: '4rem' }}>
                                        <h4 style={{ color: '#991B1B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-triangle-exclamation" style={{ color: '#DC2626' }}></i> Identity Evidence — Face Comparison
                                        </h4>
                                        <div style={{ background: '#FEF2F2', border: '1px solid #F87171', borderRadius: '30px', padding: '2rem', display: 'flex', gap: '2rem', alignItems: 'flex-start', flexWrap: 'wrap', boxShadow: '0 10px 30px rgba(220, 38, 38, 0.05)' }}>
                                            {/* BOX 1: Registered Face (original_identity_photo) */}
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{ width: '160px', height: '160px', background: '#F4F7FE', borderRadius: '12px', overflow: 'hidden', border: '2px solid #05CD99', position: 'relative', marginBottom: '0.5rem' }}>
                                                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, background: '#05CD99', color: 'white', fontSize: '0.65rem', padding: '2px', textAlign: 'center', fontWeight: 'bold', zIndex: 2 }}>
                                                        ✓ REGISTERED FACE
                                                    </div>
                                                    {normalizeImageUrl(viewedSubmission.master_photo_url || viewedSubmission.original_identity_photo_url || viewedSubmission.candidate_photo_url) ? (
                                                        <img
                                                            src={normalizeImageUrl(viewedSubmission.master_photo_url || viewedSubmission.original_identity_photo_url || viewedSubmission.candidate_photo_url)}
                                                            alt="Registered Face"
                                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                                                        />
                                                    ) : null}
                                                    <div style={{ display: normalizeImageUrl(viewedSubmission.master_photo_url || viewedSubmission.original_identity_photo_url || viewedSubmission.candidate_photo_url) ? 'none' : 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                        <i className="fa-solid fa-user" style={{ fontSize: '3rem', color: '#A3AED0' }}></i>
                                                    </div>
                                                </div>
                                                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#065f46' }}>Original Candidate</div>
                                            </div>

                                            <div style={{ display: 'flex', alignItems: 'center', fontSize: '2rem', color: '#DC2626', fontWeight: 'bold', paddingTop: '60px' }}>≠</div>

                                            {/* BOX 2: Person who joined mid-exam (intruder_photo) */}
                                            <div style={{ textAlign: 'center' }}>
                                                <div style={{ width: '160px', height: '160px', background: '#F4F7FE', borderRadius: '12px', overflow: 'hidden', border: '2px dashed #DC2626', position: 'relative', marginBottom: '0.5rem' }}>
                                                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, background: '#DC2626', color: 'white', fontSize: '0.65rem', padding: '2px', textAlign: 'center', fontWeight: 'bold', zIndex: 2 }}>
                                                        ⚠ DIFFERENT PERSON DETECTED
                                                    </div>
                                                    {(() => {
                                                        const pan = viewedSubmission.pan_number ? viewedSubmission.pan_number.toLowerCase().trim() : '';
                                                        const token = viewedSubmission.assessment?.share_token || viewedSubmission.share_token || '';
                                                        const assessmentFaceUrl = (pan && token) ? `${API_BASE_URL || ''}/ai/registration/face/${pan}/assessments/${token}/` : null;
                                                        
                                                        const intruderPhoto = assessmentFaceUrl || normalizeImageUrl(viewedSubmission.pending_identity_photo_url || viewedSubmission.intruder_photo_url || viewedSubmission.original_identity_photo_url || (() => {
                                                            const snaps = timelineLogs?.length > 0 ? timelineLogs.filter(l => l.phase === 'INTEGRITY' || String(l.id || '').startsWith('integrity_') || l.has_screenshot || l.has_webcam_screenshot || l.screenshot_base64 || l.webcam_screenshot_base64 || l.screenshot_url || l.webcam_screenshot_url) : (viewedSubmission.integrity_screenshots || viewedSubmission.integrity_logs || []);
                                                            const mismatchSnap = snaps.find(s => s && ['face_mismatch', 'verification_failed', 'face_mismatch_on_reentry'].includes((s.event_type || '').toLowerCase()));
                                                            let srcVal = null;
                                                            if (mismatchSnap) {
                                                                srcVal = mismatchSnap.screenshot_url || mismatchSnap.webcam_screenshot_url || mismatchSnap.screenshot_base64 || mismatchSnap.webcam_screenshot_base64 || mismatchSnap.details?.screenshot;
                                                            } else if (snaps.length > 0) {
                                                                const lastSnap = snaps[snaps.length - 1];
                                                                srcVal = lastSnap.screenshot_url || lastSnap.webcam_screenshot_url || lastSnap.screenshot_base64 || lastSnap.webcam_screenshot_base64 || lastSnap.details?.screenshot;
                                                            }
                                                            return srcVal;
                                                        })());
                                                        if (intruderPhoto) {
                                                            return (
                                                                <>
                                                                    <img
                                                                        src={intruderPhoto}
                                                                        alt="Intruder Face"
                                                                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                                        onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                                                                    />
                                                                    <div style={{ display: 'none', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                                        <i className="fa-solid fa-user-secret" style={{ fontSize: '3rem', color: '#DC2626' }}></i>
                                                                    </div>
                                                                </>
                                                            );
                                                        }
                                                        return (
                                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                                <i className="fa-solid fa-user-secret" style={{ fontSize: '3rem', color: '#DC2626' }}></i>
                                                            </div>
                                                        );
                                                    })()}
                                                </div>
                                                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#991B1B' }}>Person During Assessment</div>
                                            </div>

                                            <div style={{ flex: 1, minWidth: '200px', paddingTop: '30px' }}>
                                                <p style={{ color: '#7F1D1D', fontSize: '0.85rem', lineHeight: 1.6, margin: 0 }}>
                                                    <strong>HR Action Required:</strong> The AI proctoring system detected that the person completing the assessment does not match the registered candidate. Please verify identity before making a hiring decision.
                                                </p>
                                                {viewedSubmission.identity_mismatch_details?.mismatch_at && (
                                                    <p style={{ color: '#9ca3af', fontSize: '0.75rem', marginTop: '0.5rem' }}>
                                                        Detected at: {new Date(viewedSubmission.identity_mismatch_details.mismatch_at).toLocaleString()}
                                                    </p>
                                                )}
                                                <button
                                                    onClick={() => setPhotoApprovalCandidate({
                                                        ...viewedSubmission,
                                                        ai_candidate_pk: viewedSubmission.id,
                                                        is_assessment: true,
                                                        master_photo_url: viewedSubmission.original_identity_photo_url,
                                                        pending_identity_photo_url: viewedSubmission.intruder_photo_url,
                                                        full_name: viewedSubmission.candidate_name,
                                                        email: viewedSubmission.candidate_email,
                                                        candidate_photo_url: viewedSubmission.candidate_photo_url,
                                                    })}
                                                    style={{
                                                        marginTop: '1rem',
                                                        padding: '10px 20px',
                                                        background: '#EE5D50',
                                                        color: '#fff',
                                                        border: 'none',
                                                        borderRadius: '10px',
                                                        cursor: 'pointer',
                                                        fontWeight: '800',
                                                        display: 'inline-flex',
                                                        alignItems: 'center',
                                                        gap: '8px',
                                                        boxShadow: '0 4px 12px rgba(238, 93, 80, 0.2)',
                                                        transition: 'all 0.2s ease',
                                                    }}
                                                    onMouseEnter={(e) => e.target.style.background = '#E04E41'}
                                                    onMouseLeave={(e) => e.target.style.background = '#EE5D50'}
                                                >
                                                    <i className="fa-solid fa-user-check"></i>
                                                    Approve & Update Registered Face
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Modal Footer */}
                        <div style={{
                            padding: '1.5rem 2.5rem', background: 'white', borderTop: '1px solid #E2E8F0',
                            textAlign: 'right', borderBottomLeftRadius: '30px', borderBottomRightRadius: '30px'
                        }}>
                            <button
                                onClick={() => {
                                    const newParams = new URLSearchParams(searchParams);
                                    newParams.delete('subId');
                                    setSearchParams(newParams);
                                }}
                                style={{
                                    padding: '0.8rem 2.5rem', background: '#4318FF', color: 'white',
                                    border: 'none', borderRadius: '15px', fontWeight: '800', cursor: 'pointer',
                                    boxShadow: '0 10px 20px rgba(67, 24, 255, 0.2)', fontSize: '0.95rem'
                                }}
                            >
                                Finished Review
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Main Application Container */}
            <div className="dashboard-main" style={{
                width: '100%',
                height: '100%',
                display: 'flex', flexDirection: 'column',
                overflow: 'hidden'
            }}>
                {/* Global Dashboard Header (Only on overview/detail) */}
                {viewMode !== 'transcript' && (
                    <header style={{ marginBottom: '1rem', textAlign: 'center', flexShrink: 0, paddingTop: '1rem' }}>
                        <h1 style={{ fontSize: '2rem', fontWeight: '900', color: '#111827', margin: 0 }}>
                            {activeTab === 'resume' ? 'Resume Screening' :
                                activeTab === 'assessment' ? 'AI Assessment' :
                                    activeTab === 'interview' ? 'AI Interview' :
                                        activeTab === 'fully_automatic' ? 'Fully Automatic' : 'AI'} <span style={{ color: '#4F46E5' }}>Results</span>
                        </h1>
                    </header>
                )}

                <div style={{
                    flex: 1,
                    display: viewMode === 'transcript' ? 'flex' : 'block',
                    flexDirection: 'column',
                    overflow: viewMode === 'transcript' ? 'hidden' : 'auto',
                    padding: viewMode === 'transcript' ? '0' : '0 2rem 3rem'
                }}>
                    {viewMode === 'detail' && (
                        <div style={{ marginTop: '1rem' }}>
                            <button onClick={handleBackToOverview} style={{
                                background: 'none', border: 'none', padding: '0',
                                cursor: 'pointer', fontWeight: '800', color: '#4F46E5',
                                display: 'flex', alignItems: 'center', gap: '0.5rem',
                                marginBottom: '1rem', fontSize: '0.9rem'
                            }}>
                                <i className="fa-solid fa-arrow-left" /> Back to Archive
                            </button>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                <div>
                                    <h1 style={{ fontSize: '1.8rem', fontWeight: '900', color: '#111827', margin: 0 }}>
                                        {(selectedRole || '').replace('AUTO_', '').replace('MANUAL_', '').split('_')[0]} <span style={{ color: '#94A3B8', fontWeight: '400', fontSize: '1rem' }}>Batch Results</span>
                                    </h1>
                                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', fontWeight: '700', color: '#4F46E5' }}>
                                            <i className="fa-solid fa-layer-group" />
                                            <span style={{ color: '#94A3B8' }}>Batch:</span>
                                            <span>{selectedRole}</span>
                                        </div>
                                    </div>
                                </div>
                                <div style={{
                                    background: 'white', padding: '1rem 2rem', borderRadius: '18px',
                                    boxShadow: '0 4px 15px rgba(0,0,0,0.05)', textAlign: 'center',
                                    border: '1px solid #F1F5F9'
                                }}>
                                    <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#94A3B8', textTransform: 'uppercase' }}>Submissions</div>
                                    <div style={{ fontSize: '1.8rem', fontWeight: '900', color: '#4F46E5' }}>{currentRows.length}</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {viewMode === 'transcript' ? renderTranscriptReport(showTranscriptDetail) : (
                        <>
                            {viewMode === 'overview' && (
                                <div style={{ maxWidth: '800px', margin: '0 auto', marginTop: '1rem' }}>
                                    <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                        <div style={{ width: '4px', height: '20px', background: '#4F46E5', borderRadius: '2px' }} />
                                        <h2 style={{ fontSize: '1.2rem', fontWeight: '800', margin: 0, color: '#1E293B' }}>{activeTab.replace('_', ' ').toUpperCase()} Archive</h2>
                                        <span style={{ fontSize: '0.8rem', color: '#64748B', fontWeight: '600', marginLeft: 'auto' }}>
                                            {Object.entries(groupedData).filter(([_, d]) => {
                                                if (activeTab === 'resume') return d.resume.length > 0 && !d.is_fully_automatic;
                                                if (activeTab === 'assessment') return d.assessment.length > 0 && !d.is_fully_automatic;
                                                if (activeTab === 'interview') return d.interview.length > 0 && !d.is_fully_automatic;
                                                if (activeTab === 'fully_automatic') return d.is_fully_automatic;
                                                return true;
                                            }).length} Batches Found
                                        </span>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                        {(() => {
                                            const filteredBatches = Object.entries(groupedData)
                                                .filter(([_, data]) => {
                                                    if (activeTab === 'resume') return data.resume.length > 0 && !data.is_fully_automatic;
                                                    if (activeTab === 'assessment') return data.assessment.length > 0 && !data.is_fully_automatic;
                                                    if (activeTab === 'interview') return data.interview.length > 0 && !data.is_fully_automatic;
                                                    if (activeTab === 'fully_automatic') return data.is_fully_automatic;
                                                    return true;
                                                })
                                                .sort(([, a], [, b]) => {
                                                    // Helper to extract DD-MM-YYYY_HH:MM from batch name
                                                    const extractBatchTime = (bName) => {
                                                        const match = bName?.match(/_(\d{2})-(\d{2})-(\d{4})_(\d{2}):(\d{2})/);
                                                        if (match) {
                                                            const [_, day, month, year, hour, minute] = match;
                                                            return new Date(`${year}-${month}-${day}T${hour}:${minute}:00`).getTime();
                                                        }
                                                        return null;
                                                    };

                                                    const timeA = extractBatchTime(a.batch_name);
                                                    const timeB = extractBatchTime(b.batch_name);

                                                    // If both have timestamps in their names, sort by that
                                                    if (timeA && timeB) {
                                                        return timeB - timeA;
                                                    }

                                                    // Fallback: Sort by most recent submission/creation date (newest first)
                                                    const getLatest = (d) => {
                                                        const all = [...(d.resume || []), ...(d.assessment || []), ...(d.interview || [])];
                                                        const dates = all.map(r => r.submitted_at || r.created_at).filter(Boolean);
                                                        return dates.length > 0 ? new Date(Math.max(...dates.map(date => new Date(date)))) : new Date(0);
                                                    };
                                                    return getLatest(b) - getLatest(a);
                                                });

                                            const batchesPerPage = 20;
                                            const indexOfLastBatch = batchPage * batchesPerPage;
                                            const indexOfFirstBatch = indexOfLastBatch - batchesPerPage;
                                            const currentBatches = filteredBatches.slice(indexOfFirstBatch, indexOfLastBatch);

                                            return (
                                                <>
                                                    {currentBatches.map(([roleName, data]) => (
                                                        <div key={roleName} onClick={() => handleRoleClick(roleName)} className="glass-table-card role-card" style={{
                                                            padding: '1.2rem 1.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                                            transition: 'all 0.2s', borderLeft: '4px solid #4318FF'
                                                        }}>
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '1.2rem' }}>
                                                                <div style={{ width: '42px', height: '42px', borderRadius: '12px', background: 'linear-gradient(135deg, #4318FF, #9333ea)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', boxShadow: '0 8px 15px rgba(67, 24, 255, 0.2)' }}>
                                                                    <i className="fa-solid fa-layer-group" />
                                                                </div>
                                                                <div>
                                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                                        <h3 style={{ fontSize: '1.05rem', fontWeight: '800', margin: 0, color: '#1B254B' }}>{data.batch_name}</h3>
                                                                        <span style={{
                                                                            padding: '0.15rem 0.6rem', borderRadius: '6px', fontSize: '0.65rem', fontWeight: '900',
                                                                            background: data.is_fully_automatic ? '#EEF2FF' : '#F4F7FE',
                                                                            color: data.is_fully_automatic ? '#4F46E5' : '#707EAE',
                                                                            border: `1px solid ${data.is_fully_automatic ? '#4F46E533' : '#707EAE33'}`,
                                                                            textTransform: 'uppercase', letterSpacing: '0.05em'
                                                                        }}>
                                                                            {data.is_fully_automatic ? 'Automatic' : 'Manual'}
                                                                        </span>
                                                                    </div>
                                                                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.3rem' }}>
                                                                        <span style={{ fontSize: '0.75rem', color: '#707EAE', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                                            <i className="fa-solid fa-users-viewfinder" style={{ fontSize: '0.7rem' }} />
                                                                            {(activeTab === 'resume' ? data.resume.length : activeTab === 'assessment' ? data.assessment.length : activeTab === 'interview' ? data.interview.length : (data.is_fully_automatic ? data.unique_candidates : data.total))} Candidate{(activeTab === 'resume' ? data.resume.length : activeTab === 'assessment' ? data.assessment.length : activeTab === 'interview' ? data.interview.length : (data.is_fully_automatic ? data.unique_candidates : data.total)) !== 1 ? 's' : ''}
                                                                        </span>
                                                                        <span style={{ fontSize: '0.75rem', color: '#707EAE', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                                            <i className="fa-solid fa-circle-check" style={{ fontSize: '0.7rem', color: '#05CD99' }} />
                                                                            {(activeTab === 'resume' ? data.resume.length : activeTab === 'assessment' ? data.assessment.length : activeTab === 'interview' ? data.interview.length : (data.is_fully_automatic ? data.unique_candidates : (data.assessment.length + data.resume.length + data.interview.length)))} Total Results
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div style={{ color: '#4318FF', fontSize: '1.2rem' }} className="arrow-icon">
                                                                <i className="fa-solid fa-circle-chevron-right" />
                                                            </div>
                                                        </div>
                                                    ))}

                                                    {filteredBatches.length > batchesPerPage && (
                                                        <div style={{
                                                            padding: '1rem 1.5rem', borderTop: '1px solid #F1F5F9',
                                                            display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', background: 'white', borderRadius: '12px',
                                                            boxShadow: '0 4px 15px rgba(0,0,0,0.03)'
                                                        }}>
                                                            <div style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: '700' }}>
                                                                Showing <span style={{ color: '#1B254B' }}>{indexOfFirstBatch + 1}</span> to <span style={{ color: '#1B254B' }}>{Math.min(indexOfLastBatch, filteredBatches.length)}</span> of <span style={{ color: '#1B254B' }}>{filteredBatches.length}</span> batches
                                                            </div>
                                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                                <button
                                                                    disabled={batchPage === 1}
                                                                    onClick={() => setBatchPage(p => Math.max(1, p - 1))}
                                                                    style={{
                                                                        padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #E2E8F0',
                                                                        background: 'white', cursor: batchPage === 1 ? 'not-allowed' : 'pointer',
                                                                        fontSize: '0.8rem', fontWeight: '700', color: batchPage === 1 ? '#CBD5E1' : '#4F46E5',
                                                                        display: 'flex', alignItems: 'center', gap: '0.4rem'
                                                                    }}
                                                                >
                                                                    <i className="fa-solid fa-chevron-left" /> Prev
                                                                </button>
                                                                <div style={{ display: 'flex', alignItems: 'center', padding: '0 0.5rem', fontSize: '0.85rem', fontWeight: '800', color: '#1B254B' }}>
                                                                    {batchPage}
                                                                </div>
                                                                <button
                                                                    disabled={indexOfLastBatch >= filteredBatches.length}
                                                                    onClick={() => setBatchPage(p => p + 1)}
                                                                    style={{
                                                                        padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #E2E8F0',
                                                                        background: 'white', cursor: indexOfLastBatch >= filteredBatches.length ? 'not-allowed' : 'pointer',
                                                                        fontSize: '0.8rem', fontWeight: '700', color: indexOfLastBatch >= filteredBatches.length ? '#CBD5E1' : '#4F46E5',
                                                                        display: 'flex', alignItems: 'center', gap: '0.4rem'
                                                                    }}
                                                                >
                                                                    Next <i className="fa-solid fa-chevron-right" />
                                                                </button>
                                                            </div>
                                                        </div>
                                                    )}
                                                </>
                                            );
                                        })()}
                                    </div>
                                </div>
                            )}

                            {viewMode === 'detail' && (
                                <>
                                    {!groupedData[selectedRole]?.is_fully_automatic && (
                                        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
                                            <div style={{ display: 'flex', gap: '0.4rem', background: '#F4F7FE', padding: '0.3rem', borderRadius: '10px' }}>
                                                {[
                                                    { id: 'resume', label: 'Resume', icon: 'fa-file-magnifying-glass' },
                                                    { id: 'assessment', label: 'AI Assess', icon: 'fa-brain' },
                                                    { id: 'standard', label: 'Standard', icon: 'fa-vial-circle-check' },
                                                    { id: 'interview', label: 'Interviews', icon: 'fa-microphone-lines' }
                                                ].filter(tab => {
                                                    const d = groupedData[selectedRole];
                                                    if (!d) return false;
                                                    // This part is redundant now since we hide for automatic, but keeping for safety
                                                    if (d.is_fully_automatic) return true;
                                                    if (activeTab === 'resume' && tab.id === 'resume') return true;
                                                    if (activeTab === 'assessment' && tab.id === 'assessment') return true;
                                                    if (activeTab === 'interview' && tab.id === 'interview') return true;
                                                    if (activeTab === 'standard' && tab.id === 'standard') return true;
                                                    return false;
                                                }).map(tab => (
                                                    <button key={tab.id} onClick={() => handleTabChange(tab.id)} style={{
                                                        background: activeTab === tab.id ? 'white' : 'transparent',
                                                        border: 'none', padding: '0.5rem 1rem', borderRadius: '8px',
                                                        fontWeight: '700', color: activeTab === tab.id ? '#4F46E5' : '#718096',
                                                        cursor: 'pointer', fontSize: '0.85rem'
                                                    }}>
                                                        <i className={`fa-solid ${tab.icon}`} style={{ marginRight: '0.4rem' }} />
                                                        {tab.label}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* ═══ CINEMATIC BATCH ANALYTICS PANEL (Interview Tab Only) ═══ */}
                                    {activeTab === 'interview' && allRows.length > 0 && (() => {
                                        const metrics = computeBatchMetrics(allRows);
                                        const pieData = [
                                            { name: 'Passed', value: metrics.passed, fill: '#34D399' },
                                            { name: 'Failed', value: metrics.failed, fill: '#F87171' },
                                            { name: 'On-Hold', value: metrics.onHold, fill: '#FBBF24' },
                                        ].filter(d => d.value > 0);

                                        // Score distribution: group candidates into ranges
                                        const scoreRanges = [
                                            { range: '0-20%', min: 0, max: 20, fill: '#F87171' },
                                            { range: '21-40%', min: 21, max: 40, fill: '#FB923C' },
                                            { range: '41-60%', min: 41, max: 60, fill: '#FBBF24' },
                                            { range: '61-80%', min: 61, max: 80, fill: '#60A5FA' },
                                            { range: '81-100%', min: 81, max: 100, fill: '#34D399' },
                                        ];
                                        const barData = scoreRanges.map(sr => ({
                                            range: sr.range,
                                            count: allRows.filter(r => {
                                                const s = getScoreValue(r);
                                                return s >= sr.min && s <= sr.max;
                                            }).length,
                                            fill: sr.fill
                                        }));

                                        return (
                                            <div style={{
                                                background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
                                                borderRadius: '16px',
                                                padding: '1.2rem 1.5rem',
                                                marginBottom: '1rem',
                                                opacity: analyticsAnimateIn ? 1 : 0,
                                                transform: analyticsAnimateIn ? 'translateY(0)' : 'translateY(10px)',
                                                transition: 'opacity 300ms ease, transform 300ms ease',
                                                boxShadow: '0 10px 30px rgba(15, 12, 41, 0.3)',
                                                position: 'relative',
                                                overflow: 'hidden'
                                            }}>
                                                {/* Decorative orbs */}
                                                <div style={{ position: 'absolute', top: '-40px', right: '-40px', width: '200px', height: '200px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />
                                                <div style={{ position: 'absolute', bottom: '-60px', left: '-30px', width: '250px', height: '250px', borderRadius: '50%', background: 'radial-gradient(circle, rgba(168, 85, 247, 0.1) 0%, transparent 70%)', pointerEvents: 'none' }} />

                                                {/* Header */}
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem', position: 'relative', zIndex: 1 }}>
                                                    <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '0.9rem', boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)' }}>
                                                        <i className="fa-solid fa-chart-pie" />
                                                    </div>
                                                    <h3 style={{ margin: 0, color: 'white', fontSize: '1.1rem', fontWeight: '800', letterSpacing: '-0.02em' }}>Batch Analytics</h3>
                                                    <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)', fontWeight: '600', background: 'rgba(255,255,255,0.08)', padding: '0.25rem 0.75rem', borderRadius: '20px' }}>
                                                        <i className="fa-solid fa-sparkles" style={{ marginRight: '4px' }} />LIVE
                                                    </span>
                                                </div>

                                                {/* Stats Row */}
                                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '0.5rem', marginBottom: '1rem', position: 'relative', zIndex: 1 }}>
                                                    {[
                                                        { label: 'Total', value: metrics.total, color: '#60A5FA', icon: 'fa-users' },
                                                        { label: 'Passed', value: metrics.passed, color: '#34D399', icon: 'fa-user-check' },
                                                        { label: 'Failed', value: metrics.failed, color: '#F87171', icon: 'fa-user-xmark' },
                                                        { label: 'On-Hold', value: metrics.onHold, color: '#FBBF24', icon: 'fa-user-clock' },
                                                        { label: 'Avg Score', value: typeof metrics.avgScore === 'number' ? `${metrics.avgScore}%` : 'N/A', color: '#A78BFA', icon: 'fa-chart-line' },
                                                        { label: 'Completion', value: typeof metrics.completionRate === 'number' ? `${metrics.completionRate}%` : 'N/A', color: '#2DD4BF', icon: 'fa-circle-check' },
                                                    ].map((stat, i) => (
                                                        <div key={stat.label} style={{ textAlign: 'center', padding: '0.6rem 0.4rem', background: 'rgba(255,255,255,0.04)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)' }}>
                                                            <i className={`fa-solid ${stat.icon}`} style={{ color: stat.color, fontSize: '0.8rem', marginBottom: '0.3rem', display: 'block' }} />
                                                            <div style={{ fontSize: '1.2rem', fontWeight: '900', color: 'white' }}>{stat.value}</div>
                                                            <div style={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.5)', fontWeight: '700', textTransform: 'uppercase' }}>{stat.label}</div>
                                                        </div>
                                                    ))}
                                                </div>

                                                {/* Charts Row */}
                                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '1rem', position: 'relative', zIndex: 1 }}>
                                                    {/* Pie Chart - Pass/Fail Distribution */}
                                                    <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '12px', padding: '0.75rem 1rem', border: '1px solid rgba(255,255,255,0.08)' }}>
                                                        <h4 style={{ margin: '0 0 0.4rem', color: 'rgba(255,255,255,0.8)', fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                                            <i className="fa-solid fa-chart-pie" style={{ marginRight: '6px', color: '#a78bfa' }} />Result Distribution
                                                        </h4>
                                                        <ResponsiveContainer width="100%" height={120}>
                                                            <PieChart>
                                                                <Pie
                                                                    data={pieData}
                                                                    cx="50%"
                                                                    cy="50%"
                                                                    innerRadius={35}
                                                                    outerRadius={52}
                                                                    paddingAngle={3}
                                                                    dataKey="value"
                                                                    stroke="none"
                                                                >
                                                                    {pieData.map((entry, index) => (
                                                                        <Cell key={`cell-${index}`} fill={entry.fill} />
                                                                    ))}
                                                                </Pie>
                                                                <Tooltip
                                                                    contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: 'white', fontSize: '0.8rem' }}
                                                                    itemStyle={{ color: 'white' }}
                                                                />
                                                                <Legend
                                                                    wrapperStyle={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.7)' }}
                                                                    formatter={(value) => <span style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.7rem' }}>{value}</span>}
                                                                />
                                                            </PieChart>
                                                        </ResponsiveContainer>
                                                    </div>

                                                    {/* Bar Chart - Score Distribution */}
                                                    <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '12px', padding: '0.75rem 1rem', border: '1px solid rgba(255,255,255,0.08)' }}>
                                                        <h4 style={{ margin: '0 0 0.4rem', color: 'rgba(255,255,255,0.8)', fontSize: '0.7rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                                            <i className="fa-solid fa-chart-bar" style={{ marginRight: '6px', color: '#60a5fa' }} />Score Distribution
                                                        </h4>
                                                        <ResponsiveContainer width="100%" height={120}>
                                                            <BarChart data={barData} margin={{ top: 5, right: 10, left: -15, bottom: 5 }}>
                                                                <XAxis
                                                                    dataKey="range"
                                                                    tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 10 }}
                                                                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                                                                    tickLine={false}
                                                                />
                                                                <YAxis
                                                                    tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 10 }}
                                                                    axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                                                                    tickLine={false}
                                                                    allowDecimals={false}
                                                                />
                                                                <Tooltip
                                                                    contentStyle={{ background: '#1e1b4b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: 'white', fontSize: '0.8rem' }}
                                                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                                                />
                                                                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                                                                    {barData.map((entry, index) => (
                                                                        <Cell key={`bar-${index}`} fill={entry.fill} />
                                                                    ))}
                                                                </Bar>
                                                            </BarChart>
                                                        </ResponsiveContainer>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })()}

                                    <div style={{ display: 'flex', gap: '0.8rem', marginBottom: '0.8rem', alignItems: 'center', flexWrap: 'wrap' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                            <span style={{ fontSize: '0.7rem', fontWeight: '800', color: '#9CA3AF', textTransform: 'uppercase' }}>Type:</span>
                                            {[{ key: 'all', label: 'All' }, { key: 'pass', label: 'Pass' }, { key: 'fail', label: 'Fail' }, ...((activeTab === 'interview' || activeTab === 'assessment') ? [{ key: 'on-hold', label: '⚠️ On-Hold' }] : [])].map(f => (
                                                <button key={f.key} onClick={() => { setStatusFilter(f.key); setCurrentPage(1); }} style={{
                                                    padding: '0.25rem 0.75rem', borderRadius: '15px', border: '1px solid',
                                                    fontSize: '0.75rem', fontWeight: '700', cursor: 'pointer',
                                                    borderColor: statusFilter === f.key ? '#4F46E5' : '#E5E7EB',
                                                    background: statusFilter === f.key ? '#EEF2FF' : 'white',
                                                    color: statusFilter === f.key ? '#4F46E5' : '#6B7280',
                                                }}>{f.label}</button>
                                            ))}
                                        </div>

                                        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', color: '#9CA3AF', fontWeight: '700' }}>{currentRows.length} results</span>

                                        {/* Download/Export CSV — visible for all tabs in detail view */}
                                        <button
                                            onClick={exportResultsCSV}
                                            style={{
                                                padding: '0.3rem 0.85rem', borderRadius: '10px',
                                                border: '1px solid #059669', background: '#ECFDF5',
                                                color: '#059669', fontWeight: '700', fontSize: '0.75rem',
                                                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem',
                                                boxShadow: '0 2px 5px rgba(5, 150, 105, 0.1)'
                                            }}
                                            title={someSelected ? "Export selected candidates as CSV" : "Download all current results as CSV"}
                                        >
                                            <i className="fa-solid fa-file-csv" />
                                            {someSelected ? `Export Selected (${selectedCount})` : "Download CSV"}
                                        </button>

                                        {/* Bulk Delete — only visible to authorised roles when at least one row is selected */}
                                        {canDelete && someSelected && (
                                            <button
                                                onClick={() => requestDelete(selectedItems)}
                                                style={{
                                                    padding: '0.3rem 0.85rem', borderRadius: '10px',
                                                    border: '1px solid #ef4444', background: '#FFF5F5',
                                                    color: '#ef4444', fontWeight: '700', fontSize: '0.75rem',
                                                    cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem'
                                                }}
                                                title={myRole === 'company_admin' || myRole === 'application_admin' ? 'Delete selected' : 'Request deletion for selected'}
                                            >
                                                <i className="fa-solid fa-trash" />
                                                Delete ({selectedCount})
                                            </button>
                                        )}
                                    </div>

                                    <div className="glass-table-card" style={{ marginBottom: '1rem' }}>
                                        {loading ? (
                                            <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
                                                <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '1.5rem', color: '#4F46E5' }} />
                                                <p>Loading...</p>
                                            </div>
                                        ) : (
                                            <div style={{ overflowX: 'auto' }}>
                                                <table className="results-table">
                                                    <thead>
                                                        <tr>
                                                            <th style={{ width: '40px', textAlign: 'center' }}>
                                                                <input type="checkbox" checked={allSelected} onChange={toggleSelectAll} />
                                                            </th>
                                                            {activeTab === 'interview' ? (
                                                                <th
                                                                    style={{ cursor: 'pointer', userSelect: 'none' }}
                                                                    onClick={() => handleSort('name')}
                                                                    title="Sort by name"
                                                                >
                                                                    Candidate Info
                                                                    {sortField === 'name' && (
                                                                        <i className={`fa-solid fa-caret-${sortDirection === 'asc' ? 'up' : 'down'}`}
                                                                            style={{ marginLeft: '6px', color: '#4F46E5' }} />
                                                                    )}
                                                                </th>
                                                            ) : (
                                                                <th
                                                                    style={{ cursor: 'pointer', userSelect: 'none' }}
                                                                    onClick={() => handleSort('name')}
                                                                    title="Sort by name"
                                                                >
                                                                    Candidate Info
                                                                    {sortField === 'name' && (
                                                                        <i className={`fa-solid fa-caret-${sortDirection === 'asc' ? 'up' : 'down'}`}
                                                                            style={{ marginLeft: '6px', color: '#4F46E5' }} />
                                                                    )}
                                                                </th>
                                                            )}
                                                            {activeTab === 'fully_automatic' ? (
                                                                <>
                                                                    <th style={{ minWidth: '400px' }}>Pipeline Status</th>
                                                                </>
                                                            ) : activeTab === 'interview' ? (
                                                                <>
                                                                    <th
                                                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                                                        onClick={() => handleSort('score')}
                                                                        title="Sort by score"
                                                                    >
                                                                        Result
                                                                        {sortField === 'score' && (
                                                                            <i className={`fa-solid fa-caret-${sortDirection === 'asc' ? 'up' : 'down'}`}
                                                                                style={{ marginLeft: '6px', color: '#4F46E5' }} />
                                                                        )}
                                                                    </th>
                                                                    <th
                                                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                                                        onClick={() => handleSort('date')}
                                                                        title="Sort by date"
                                                                    >
                                                                        Date
                                                                        {sortField === 'date' && (
                                                                            <i className={`fa-solid fa-caret-${sortDirection === 'asc' ? 'up' : 'down'}`}
                                                                                style={{ marginLeft: '6px', color: '#4F46E5' }} />
                                                                        )}
                                                                    </th>
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <th
                                                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                                                        onClick={() => handleSort('score')}
                                                                        title="Sort by score"
                                                                    >
                                                                        Result
                                                                        {sortField === 'score' && (
                                                                            <i className={`fa-solid fa-caret-${sortDirection === 'asc' ? 'up' : 'down'}`}
                                                                                style={{ marginLeft: '6px', color: '#4F46E5' }} />
                                                                        )}
                                                                    </th>
                                                                    <th
                                                                        style={{ cursor: 'pointer', userSelect: 'none' }}
                                                                        onClick={() => handleSort('date')}
                                                                        title="Sort by date"
                                                                    >
                                                                        Date
                                                                        {sortField === 'date' && (
                                                                            <i className={`fa-solid fa-caret-${sortDirection === 'asc' ? 'up' : 'down'}`}
                                                                                style={{ marginLeft: '6px', color: '#4F46E5' }} />
                                                                        )}
                                                                    </th>
                                                                </>
                                                            )}
                                                            <th>Status</th>
                                                            <th>Action</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {currentRows.length === 0 && (
                                                            <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center' }}>No candidates found.</td></tr>
                                                        )}
                                                        {paginatedRows.map((r) => {
                                                            const isSelected = selected.has(r._deleteKey);
                                                            return (
                                                                <tr key={r._deleteKey} className={isSelected ? 'selected' : ''}>
                                                                    <td style={{ textAlign: 'center' }}>
                                                                        <input type="checkbox" checked={isSelected} onChange={() => toggleSelect(r._deleteKey)} />
                                                                    </td>
                                                                    <td>
                                                                        <div style={{ fontWeight: '800', fontSize: '0.9rem', color: (r.full_name === 'Extraction Failed' || r.candidate?.name === 'Extraction Failed') ? '#EE5D50' : 'inherit', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                                                                            {r.full_name || r.candidate?.name || 'Candidate'}
                                                                            {r.identity_mismatch_detected && (
                                                                                <i className="fa-solid fa-triangle-exclamation" style={{ color: '#EE5D50' }} title="Identity mismatch detected during registration"></i>
                                                                            )}
                                                                            {r.photo_update_pending && r.ai_candidate_pk && (
                                                                                <button
                                                                                    onClick={(e) => { e.stopPropagation(); setPhotoApprovalCandidate(r); }}
                                                                                    title="Review and approve the new identity photo"
                                                                                    style={{
                                                                                        padding: '0.2rem 0.55rem', borderRadius: '6px', border: '1px solid #f59e0b',
                                                                                        background: '#FFFBEB', color: '#B45309',
                                                                                        fontSize: '0.7rem', fontWeight: '700', cursor: 'pointer',
                                                                                        display: 'inline-flex', alignItems: 'center', gap: '4px'
                                                                                    }}
                                                                                >
                                                                                    <i className="fa-solid fa-user-check" />
                                                                                    Update Photo
                                                                                </button>
                                                                            )}
                                                                        </div>
                                                                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                                                                            {r.email || r.candidate?.email || 'N/A'}
                                                                        </div>
                                                                    </td>
                                                                    {activeTab === 'fully_automatic' ? (
                                                                        <td style={{ padding: '1rem' }}>
                                                                            <div style={{ display: 'flex', gap: '1.2rem', alignItems: 'flex-start' }}>
                                                                                {[
                                                                                    { label: 'Resume', data: r.resume, scoreKey: 'resume_score' },
                                                                                    { label: 'Assessment', data: r.assessment, scoreKey: 'percentage' },
                                                                                    { label: 'Interview', data: r.interview, scoreKey: 'score', isInt: true }
                                                                                ].map((stage, idx) => {
                                                                                    const hasData = stage.isInt
                                                                                        ? (!!stage.data && !['New', 'Invited', 'Resume Passed', 'Resume Failed', 'Extraction Failed'].includes(stage.data.status))
                                                                                        : !!(stage.data && (stage.data.id || stage.data.submission_id || stage.data.status));
                                                                                    const score = stage.isInt
                                                                                        ? (stage.data?.interview_summary?.length > 0 ? Math.round((stage.data.interview_summary.reduce((s, q) => s + (parseInt(q.score || q.marks) || 0), 0) / 140) * 100) : 0)
                                                                                        : (stage.data?.[stage.scoreKey] || 0);
                                                                                    const date = stage.data?.created_at || stage.data?.submitted_at || stage.data?.completed_at;
                                                                                    return (
                                                                                        <div key={idx} style={{ flex: 1, minWidth: '110px' }}>
                                                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px' }}>
                                                                                                <i className={`fa-solid ${hasData ? 'fa-square-check' : 'fa-square'}`}
                                                                                                    style={{ color: hasData ? '#05CD99' : '#CBD5E1', fontSize: '0.9rem' }} />
                                                                                                <span style={{ fontSize: '0.7rem', fontWeight: '800', color: '#1B254B', textTransform: 'uppercase' }}>{stage.label}</span>
                                                                                            </div>
                                                                                            {hasData ? (
                                                                                                <div style={{ paddingLeft: '18px' }}>
                                                                                                    <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#4F46E5' }}>{score}%</div>
                                                                                                    <div style={{ fontSize: '0.62rem', color: '#94A3B8', fontWeight: '600' }}>{new Date(date).toLocaleDateString()}</div>
                                                                                                </div>
                                                                                            ) : (
                                                                                                <div style={{ paddingLeft: '18px', fontSize: '0.62rem', color: '#CBD5E1', fontStyle: 'italic' }}>Pending</div>
                                                                                            )}
                                                                                        </div>
                                                                                    );
                                                                                })}
                                                                            </div>
                                                                        </td>
                                                                    ) : (
                                                                        <>
                                                                            <td style={{ fontSize: '0.9rem', fontWeight: '600' }}>
                                                                                {activeTab === 'resume' ? `${r.resume_score || 0}%` :
                                                                                    activeTab === 'assessment' || activeTab === 'standard' ? `${r.percentage ?? 0}%` :
                                                                                        `${r.interview_summary?.length > 0 ? Math.round((r.interview_summary.reduce((s, q) => s + (parseInt(q.score || q.marks) || 0), 0) / 140) * 100) : 0}%`}
                                                                            </td>
                                                                            <td style={{ fontSize: '0.85rem', minWidth: '100px' }}>
                                                                                <div style={{ fontWeight: '700', color: '#1B254B' }}>{new Date(r.created_at || r.submitted_at || r.completed_at).toLocaleDateString()}</div>
                                                                                <div style={{ fontSize: '0.7rem', color: '#94A3B8', fontWeight: '600' }}>{new Date(r.created_at || r.submitted_at || r.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                                                                            </td>
                                                                        </>
                                                                    )}
                                                                    <td>
                                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                                                                            {(() => {
                                                                                const rawStatus = activeTab === 'fully_automatic' ? (r.interview?.status || r.assessment?.status || r.resume?.status) : r.status;
                                                                                return (
                                                                                    <span style={{ padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.65rem', fontWeight: '800', ...getStatusStyle(rawStatus) }}>
                                                                                        {getStatusLabel(rawStatus)}
                                                                                    </span>
                                                                                );
                                                                            })()}
                                                                            {/* Pending qualification badge */}
                                                                            {r.qual_pending && (
                                                                                <span title="Qualification change pending admin approval" style={{ fontSize: '0.62rem', fontWeight: '800', background: '#fffbeb', color: '#d97706', border: '1px solid #fde68a', borderRadius: '999px', padding: '1px 6px', whiteSpace: 'nowrap' }}>⏳ Pending</span>
                                                                            )}
                                                                            {(() => {
                                                                                const currentStatus = activeTab === 'fully_automatic' ? (r.interview?.status || r.assessment?.status || r.resume?.status) : r.status;
                                                                                const currentSubmissionId = activeTab === 'fully_automatic' ? (r.assessment?.submission_id || r.interview?.submission_id || r.resume?.submission_id) : r.submission_id;
                                                                                if (!r.qual_pending && (currentStatus === 'hold' || currentStatus === 'On-Hold') && currentSubmissionId) {
                                                                                    const sid = String(currentSubmissionId || '');
                                                                                    const aiId = sid.replace('ai_', '').replace('aicand_', '').replace('_assessment', '').replace('_interview', '');
                                                                                    return (
                                                                                        <>
                                                                                            <button
                                                                                                onClick={(e) => {
                                                                                                    e.stopPropagation();
                                                                                                    if (aiResultsIsAdmin) {
                                                                                                        if (window.confirm(`Mark ${r.full_name || r.candidate?.name || 'this candidate'} as Qualified?`)) {
                                                                                                            axios.post(`${API_BASE_URL}/workflow/qualification-requests/ai/`, { ai_submission_id: aiId, requested_result: 'selected', reason: 'Admin Update', candidate_name: r.full_name || r.candidate?.name, candidate_email: r.email || r.candidate?.email }, { headers: { Authorization: `Bearer ${getToken()}` } })
                                                                                                                .then(() => { showToast('success', 'Marked as Qualified.'); fetchData(); })
                                                                                                                .catch(err => showToast('error', err.response?.data?.error || 'Failed.'));
                                                                                                        }
                                                                                                    } else {
                                                                                                        setQualReason('');
                                                                                                        setQualReasonPopup({ row: r, status: 'selected', candidateName: r.full_name || r.candidate?.name || 'Candidate', candidateEmail: r.email || r.candidate?.email, aiSubmissionId: aiId });
                                                                                                    }
                                                                                                }}
                                                                                                title="Mark as Qualified"
                                                                                                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#05CD99', padding: '0.1rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center' }}
                                                                                            >
                                                                                                <i className="fa-solid fa-user-check" />
                                                                                            </button>
                                                                                            <button
                                                                                                onClick={(e) => {
                                                                                                    e.stopPropagation();
                                                                                                    if (aiResultsIsAdmin) {
                                                                                                        if (window.confirm(`Mark ${r.full_name || r.candidate?.name || 'this candidate'} as Not Qualified?`)) {
                                                                                                            axios.post(`${API_BASE_URL}/workflow/qualification-requests/ai/`, { ai_submission_id: aiId, requested_result: 'rejected', reason: 'Admin Update', candidate_name: r.full_name || r.candidate?.name, candidate_email: r.email || r.candidate?.email }, { headers: { Authorization: `Bearer ${getToken()}` } })
                                                                                                                .then(() => { showToast('success', 'Marked as Not Qualified.'); fetchData(); })
                                                                                                                .catch(err => showToast('error', err.response?.data?.error || 'Failed.'));
                                                                                                        }
                                                                                                    } else {
                                                                                                        setQualReason('');
                                                                                                        setQualReasonPopup({ row: r, status: 'rejected', candidateName: r.full_name || r.candidate?.name || 'Candidate', candidateEmail: r.email || r.candidate?.email, aiSubmissionId: aiId });
                                                                                                    }
                                                                                                }}
                                                                                                title="Mark as Not Qualified"
                                                                                                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#EE5D50', padding: '0.1rem', fontSize: '0.95rem', display: 'flex', alignItems: 'center' }}
                                                                                            >
                                                                                                <i className="fa-solid fa-user-xmark" />
                                                                                            </button>
                                                                                        </>
                                                                                    );
                                                                                }
                                                                                return null;
                                                                            })()}
                                                                            <button
                                                                                onClick={(e) => { e.stopPropagation(); fetchTimeline(activeTab === 'fully_automatic' ? (r.resume || r.assessment || r.interview) : r, true); }}
                                                                                title={activeTab === 'manual_ai' || (activeTab === 'fully_automatic' && r.assessment) ? "View Assessment Logs" : "View Interview Logs"}
                                                                                style={{
                                                                                    background: 'none', border: 'none', cursor: 'pointer',
                                                                                    color: '#A3AED0', fontSize: '0.85rem', padding: '0.2rem',
                                                                                    display: 'flex', alignItems: 'center'
                                                                                }}
                                                                            >
                                                                                <i className="fa-solid fa-clock-rotate-left"></i>
                                                                            </button>
                                                                            {
                                                                                r.delete_requested && (
                                                                                    <span title="Deletion pending approval" style={{ cursor: 'help' }}>⏳</span>
                                                                                )
                                                                            }
                                                                        </div >
                                                                    </td >
                                                                    <td>
                                                                        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                                                                            {activeTab === 'fully_automatic' ? (
                                                                                <>
                                                                                    {r.assessment && (
                                                                                        <button
                                                                                            onClick={async (e) => {
                                                                                                e.stopPropagation();
                                                                                                const email = r.assessment.candidate_email || r.email || r.candidate?.email;
                                                                                                if (email) {
                                                                                                    const submission = await fetchAssessmentByCandidateEmail({
                                                                                                        email: email,
                                                                                                        batchName: selectedRole, // The group name is the batch_name for automatic records
                                                                                                        subId: r.assessment?.submission_id || r.submission_id,
                                                                                                        batchId: r.batch_id
                                                                                                    });
                                                                                                    if (submission) {
                                                                                                        setSearchParams({ ...Object.fromEntries(searchParams), subId: submission.submission_id });
                                                                                                    } else {
                                                                                                        showToast('error', 'No assessment submission found for this candidate');
                                                                                                    }
                                                                                                } else {
                                                                                                    showToast('error', 'Candidate email not found');
                                                                                                }
                                                                                            }}
                                                                                            title="View Assessment"
                                                                                            style={{
                                                                                                padding: '0.4rem 0.6rem', borderRadius: '8px', border: 'none',
                                                                                                background: '#EEF2FF', color: '#4F46E5', fontSize: '0.75rem', fontWeight: '800', cursor: 'pointer'
                                                                                            }}
                                                                                        >Quiz</button>
                                                                                    )}
                                                                                    {r.interview && (
                                                                                        <button
                                                                                            onClick={(e) => { e.stopPropagation(); setShowTranscriptDetail(r.interview); setViewMode('transcript'); }}
                                                                                            title="View Interview Transcript"
                                                                                            style={{
                                                                                                padding: '0.4rem 0.6rem', borderRadius: '8px', border: 'none',
                                                                                                background: '#E6FBF5', color: '#05CD99', fontSize: '0.75rem', fontWeight: '800', cursor: 'pointer'
                                                                                            }}
                                                                                        >Log</button>
                                                                                    )}
                                                                                </>
                                                                            ) : (
                                                                                <>
                                                                                    {activeTab === 'interview' || (activeTab === 'resume' && r.total_questions > 0) ? (
                                                                                        <div style={{ display: 'flex', gap: '0.4rem' }}>
                                                                                            <button
                                                                                                onClick={(e) => { e.stopPropagation(); setShowTranscriptDetail(r); setViewMode('transcript'); }}
                                                                                                style={{
                                                                                                    padding: '0.5rem 1rem', borderRadius: '10px', border: 'none',
                                                                                                    background: 'linear-gradient(135deg, #05CD99 0%, #04b082 100%)',
                                                                                                    color: 'white', fontWeight: '700', fontSize: '0.8rem', cursor: 'pointer'
                                                                                                }}
                                                                                            >Review</button>
                                                                                            <button
                                                                                                onClick={(e) => { e.stopPropagation(); handleDownloadReport(r); }}
                                                                                                disabled={downloadingId !== null}
                                                                                                title="Download PDF Report"
                                                                                                style={{
                                                                                                    width: '36px', height: '36px', borderRadius: '10px', border: '1px solid #E2E8F0',
                                                                                                    background: 'white', color: '#4318FF', fontSize: '1rem', cursor: 'pointer',
                                                                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                                                                    boxShadow: '0 4px 10px rgba(0,0,0,0.03)', transition: 'all 0.2s',
                                                                                                    padding: 0
                                                                                                }}
                                                                                            >
                                                                                                {downloadingId === String(r.submission_id || '').replace('ai_', '').replace('aicand_', '').replace('resume-', '').replace('interview-', '') ?
                                                                                                    <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '0.8rem' }} /> :
                                                                                                    <i className="fa-solid fa-file-pdf" />}
                                                                                            </button>
                                                                                        </div>
                                                                                    ) : activeTab === 'assessment' || activeTab === 'standard' ? (
                                                                                        <div style={{ display: 'flex', gap: '0.4rem' }}>
                                                                                            <button
                                                                                                onClick={(e) => { e.stopPropagation(); setSearchParams({ ...Object.fromEntries(searchParams), subId: r.submission_id || r.id || r.candidate_id }); }}
                                                                                                style={{
                                                                                                    padding: '0.5rem 1rem', borderRadius: '10px', border: 'none',
                                                                                                    background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)',
                                                                                                    color: 'white', fontWeight: '700', fontSize: '0.8rem', cursor: 'pointer'
                                                                                                }}
                                                                                            >View</button>
                                                                                            <button
                                                                                                onClick={(e) => { e.stopPropagation(); handleDownloadReport(r); }}
                                                                                                disabled={downloadingId !== null}
                                                                                                title="Download PDF Report"
                                                                                                style={{
                                                                                                    width: '36px', height: '36px', borderRadius: '10px', border: '1px solid #E2E8F0',
                                                                                                    background: 'white', color: '#4318FF', fontSize: '1rem', cursor: 'pointer',
                                                                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                                                                    boxShadow: '0 4px 10px rgba(0,0,0,0.03)', transition: 'all 0.2s',
                                                                                                    padding: 0
                                                                                                }}
                                                                                            >
                                                                                                {downloadingId === String(r.submission_id || '').replace('ai_', '').replace('aicand_', '').replace('resume-', '').replace('interview-', '') ?
                                                                                                    <i className="fa-solid fa-spinner fa-spin" style={{ fontSize: '0.8rem' }} /> :
                                                                                                    <i className="fa-solid fa-file-pdf" />}
                                                                                            </button>
                                                                                        </div>
                                                                                    ) : null}
                                                                                </>
                                                                            )}
                                                                            {canDelete && (
                                                                                <button
                                                                                    onClick={(e) => { e.stopPropagation(); requestDelete(activeTab === 'fully_automatic' ? [r.resume, r.assessment, r.interview].filter(Boolean) : [r]); }}
                                                                                    title={myRole === 'company_admin' || myRole === 'application_admin' ? 'Delete' : 'Request deletion'}
                                                                                    style={{
                                                                                        padding: '0.4rem 0.5rem', borderRadius: '8px',
                                                                                        border: '1px solid #ef4444', background: '#FFF5F5',
                                                                                        color: '#ef4444', cursor: 'pointer', fontSize: '0.75rem'
                                                                                    }}
                                                                                >
                                                                                    <i className="fa-solid fa-trash" />
                                                                                </button>
                                                                            )}
                                                                        </div>
                                                                    </td>
                                                                </tr >
                                                            );
                                                        })}
                                                    </tbody >
                                                </table >
                                            </div >
                                        )}

                                        {/* Pagination Footer */}
                                        {
                                            !loading && currentRows.length > itemsPerPage && (
                                                <div style={{
                                                    padding: '1rem 1.5rem', borderTop: '1px solid #F1F5F9',
                                                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                                                }}>
                                                    <div style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: '700' }}>
                                                        Showing <span style={{ color: '#1B254B' }}>{indexOfFirstRow + 1}</span> to <span style={{ color: '#1B254B' }}>{Math.min(indexOfLastRow, currentRows.length)}</span> of <span style={{ color: '#1B254B' }}>{currentRows.length}</span> entries
                                                    </div>
                                                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                        <button
                                                            disabled={currentPage === 1}
                                                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                                            style={{
                                                                padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #E2E8F0',
                                                                background: 'white', cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                                                                fontSize: '0.8rem', fontWeight: '700', color: currentPage === 1 ? '#CBD5E1' : '#4F46E5',
                                                                display: 'flex', alignItems: 'center', gap: '0.4rem'
                                                            }}
                                                        >
                                                            <i className="fa-solid fa-chevron-left" /> Prev
                                                        </button>
                                                        <div style={{ display: 'flex', alignItems: 'center', px: '0.5rem', fontSize: '0.85rem', fontWeight: '800', color: '#1B254B' }}>
                                                            {currentPage}
                                                        </div>
                                                        <button
                                                            disabled={indexOfLastRow >= currentRows.length}
                                                            onClick={() => setCurrentPage(p => p + 1)}
                                                            style={{
                                                                padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid #E2E8F0',
                                                                background: 'white', cursor: indexOfLastRow >= currentRows.length ? 'not-allowed' : 'pointer',
                                                                fontSize: '0.8rem', fontWeight: '700', color: indexOfLastRow >= currentRows.length ? '#CBD5E1' : '#4F46E5',
                                                                display: 'flex', alignItems: 'center', gap: '0.4rem'
                                                            }}
                                                        >
                                                            Next <i className="fa-solid fa-chevron-right" />
                                                        </button>
                                                    </div>
                                                </div>
                                            )
                                        }
                                    </div >
                                </>
                            )}
                        </>
                    )}
                </div >
            </div >
            {/* Timeline Modal */}
            {
                showLogsModal && timelineCandidate && (
                    <div className="glass-modal-overlay" style={{ zIndex: 11000 }}>
                        <div className="glass-modal-content" style={{ maxWidth: '500px', width: '90%', padding: '2rem', borderRadius: '24px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                <div>
                                    <h3 style={{ margin: 0, color: '#1B254B', fontSize: '1.2rem', fontWeight: '800' }}>
                                        {timelineCandidate.is_assessment || String(timelineCandidate.submission_id || '').startsWith('ai_') ? 'AI Assessment Logs' : 'Interview Logs'}
                                    </h3>
                                    <p style={{ margin: '0.25rem 0 0', color: '#707EAE', fontSize: '0.85rem' }}>{timelineCandidate.full_name || timelineCandidate.candidate?.name}</p>
                                </div>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <button
                                        onClick={() => fetchTimeline(timelineCandidate)}
                                        disabled={loadingTimeline}
                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#4318FF', fontSize: '1.1rem', transition: 'transform 0.2s' }}
                                        title="Refresh history"
                                    >
                                        <i className={`fa-solid fa-arrows-rotate ${loadingTimeline ? 'fa-spin' : ''}`}></i>
                                    </button>
                                    <button onClick={() => setShowLogsModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#A3AED0', fontSize: '1.2rem' }}>
                                        <i className="fa-solid fa-xmark"></i>
                                    </button>
                                </div>
                            </div>

                            {loadingTimeline ? (
                                <div style={{ textAlign: 'center', padding: '2rem' }}>
                                    <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
                                    <p style={{ color: '#707EAE', fontSize: '0.9rem' }}>Fetching logs...</p>
                                </div>
                            ) : timelineLogs.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '2rem', color: '#A3AED0' }}>
                                    <i className="fa-solid fa-list-ul" style={{ fontSize: '2rem', marginBottom: '1rem', opacity: 0.5 }}></i>
                                    <p>No logs found for this candidate yet.</p>
                                </div>
                            ) : (
                                <div style={{ maxHeight: '60vh', overflowY: 'auto', paddingRight: '0.5rem' }} className="custom-scrollbar">
                                    <div className="timeline-container" style={{ position: 'relative', paddingLeft: '2rem' }}>
                                        <div style={{ position: 'absolute', left: '7px', top: '5px', bottom: '5px', width: '2px', background: '#E2E8F0' }}></div>
                                        {timelineLogs.map((log, i) => {
                                            const isError = log.status === 'FAILURE';
                                            const isSuccess = log.status === 'SUCCESS';
                                            return (
                                                <div key={log.id} style={{ position: 'relative', marginBottom: '1.8rem' }}>
                                                    <div style={{
                                                        position: 'absolute', left: '-2rem', top: '0', width: '16px', height: '16px',
                                                        borderRadius: '50%', background: isError ? '#EE5D50' : isSuccess ? '#05CD99' : '#4318FF',
                                                        border: '3px solid white', boxShadow: '0 0 0 2px #E2E8F0', zIndex: 1
                                                    }}></div>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                                                        <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#A3AED0', textTransform: 'uppercase' }}>
                                                            {log.timestamp_formatted}
                                                        </div>
                                                        {log.phase && log.phase !== 'GENERAL' && (
                                                            <span style={{
                                                                fontSize: '0.6rem', fontWeight: '800', padding: '0.1rem 0.4rem', borderRadius: '4px',
                                                                background: log.phase === 'RESUME' ? '#E0E7FF' : log.phase === 'ASSESSMENT' ? '#FEF3C7' : '#D1FAE5',
                                                                color: log.phase === 'RESUME' ? '#4318FF' : log.phase === 'ASSESSMENT' ? '#D97706' : '#059669',
                                                                textTransform: 'uppercase'
                                                            }}>
                                                                {log.phase.replace('_', ' ')}
                                                            </span>
                                                        )}
                                                    </div>
                                                    <div style={{ fontSize: '0.95rem', fontWeight: '700', color: isError ? '#EE5D50' : '#1B254B', marginBottom: '0.2rem' }}>
                                                        {log.message}
                                                    </div>
                                                    {log.details && Object.keys(log.details).length > 0 && (
                                                        <div style={{ fontSize: '0.78rem', color: '#707EAE', background: '#F4F7FE', padding: '0.5rem 0.75rem', borderRadius: '8px', marginTop: '0.3rem' }}>
                                                            {Object.entries(log.details).map(([k, v]) => (
                                                                <div key={k} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.1rem' }}>
                                                                    <span style={{ fontWeight: '800', color: '#4318FF', minWidth: '90px', textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}:</span>
                                                                    <span style={{ wordBreak: 'break-all' }}>{String(v)}</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                                <button onClick={() => setShowLogsModal(false)} style={{ padding: '0.6rem 1.5rem', borderRadius: '12px', border: 'none', background: '#F4F7FE', color: '#1B254B', fontWeight: '700', cursor: 'pointer' }}>
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
            {/* ── AI Qualification Request Reason Modal ── */}
            {
                qualReasonPopup && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, backdropFilter: 'blur(4px)' }}>
                        <div style={{ background: '#fff', borderRadius: '20px', padding: '36px', width: '100%', maxWidth: '460px', boxShadow: '0 30px 80px rgba(0,0,0,0.25)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                                <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: '800', color: '#111827' }}>Request Qualification Change</h3>
                                <button onClick={() => { setQualReasonPopup(null); setQualReason(''); }} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.3rem', color: '#9ca3af' }}>✕</button>
                            </div>
                            <p style={{ color: '#6b7280', fontSize: '0.88rem', marginBottom: '18px', lineHeight: 1.5 }}>
                                You are requesting to mark <strong style={{ color: '#111827' }}>{qualReasonPopup.candidateName}</strong> as{' '}
                                <strong style={{ color: qualReasonPopup.status === 'selected' ? '#059669' : '#dc2626' }}>
                                    {qualReasonPopup.status === 'selected' ? '✅ Qualified' : '❌ Not Qualified'}
                                </strong>. This requires admin approval.
                            </p>
                            <div style={{ background: '#f9fafb', borderRadius: '10px', padding: '12px 14px', marginBottom: '16px', border: '1px solid #e5e7eb' }}>
                                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: '800', color: '#374151', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    Reason <span style={{ color: '#ef4444' }}>*</span>
                                </label>
                                <textarea
                                    value={qualReason}
                                    onChange={e => setQualReason(e.target.value)}
                                    placeholder="Explain why this candidate should be Qualified / Not Qualified..."
                                    rows={4}
                                    style={{ width: '100%', border: 'none', background: 'transparent', outline: 'none', resize: 'vertical', fontSize: '0.88rem', color: '#111827', fontFamily: 'inherit', boxSizing: 'border-box' }}
                                />
                            </div>
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button onClick={() => { setQualReasonPopup(null); setQualReason(''); }} style={{ flex: 1, padding: '11px', background: '#fff', border: '1px solid #d1d5db', borderRadius: '10px', cursor: 'pointer', fontWeight: '600', color: '#374151' }}>Cancel</button>
                                <button
                                    onClick={submitQualAiRequest}
                                    disabled={qualSubmitting || !qualReason.trim()}
                                    style={{ flex: 1, padding: '11px', background: qualSubmitting || !qualReason.trim() ? '#9ca3af' : (qualReasonPopup.status === 'selected' ? '#059669' : '#dc2626'), color: '#fff', border: 'none', borderRadius: '10px', cursor: qualSubmitting || !qualReason.trim() ? 'not-allowed' : 'pointer', fontWeight: '700' }}
                                >
                                    {qualSubmitting ? '⏳ Submitting...' : '📨 Submit for Approval'}
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }

            {/* ── Photo Approval Modal (admin promotes pending identity photo) ── */}
            {
                photoApprovalCandidate && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999, backdropFilter: 'blur(6px)' }}>
                        <div style={{ background: '#fff', borderRadius: '20px', padding: '32px', width: '100%', maxWidth: '720px', boxShadow: '0 30px 80px rgba(0,0,0,0.3)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                                <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '800', color: '#111827', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <i className="fa-solid fa-id-badge" style={{ color: '#f59e0b' }} />
                                    Identity Photo Update Required
                                </h3>
                                <button onClick={() => setPhotoApprovalCandidate(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.3rem', color: '#9ca3af' }}>✕</button>
                            </div>
                            <p style={{ color: '#6b7280', fontSize: '0.88rem', marginBottom: '18px', lineHeight: 1.5 }}>
                                <strong style={{ color: '#111827' }}>{photoApprovalCandidate.full_name || photoApprovalCandidate.candidate?.name || 'This candidate'}</strong>
                                {' '}joined a session with a face that did not match the previously registered photo. The new photo is awaiting your approval. Approving will replace the master face used for proctoring on subsequent interviews.
                            </p>
                            <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginBottom: '20px', flexWrap: 'wrap' }}>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ width: '180px', height: '180px', borderRadius: '14px', overflow: 'hidden', border: '2px solid #d1d5db', background: '#f3f4f6' }}>
                                        {(photoApprovalCandidate.master_photo_url || photoApprovalCandidate.original_identity_photo_url || photoApprovalCandidate.candidate_photo_url) ? (
                                            <img src={photoApprovalCandidate.master_photo_url || photoApprovalCandidate.original_identity_photo_url || photoApprovalCandidate.candidate_photo_url} alt="Currently registered" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                        ) : (
                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', color: '#9ca3af' }}>
                                                <i className="fa-solid fa-user" style={{ fontSize: '3rem' }} />
                                            </div>
                                        )}
                                    </div>
                                    <div style={{ marginTop: '8px', fontSize: '0.78rem', fontWeight: '700', color: '#374151' }}>Currently Registered</div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', fontSize: '1.6rem', color: '#f59e0b', fontWeight: '900' }}>→</div>
                                <div style={{ textAlign: 'center' }}>
                                    <div style={{ width: '180px', height: '180px', borderRadius: '14px', overflow: 'hidden', border: '2px dashed #f59e0b', background: '#fffbeb', position: 'relative' }}>
                                        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, background: '#f59e0b', color: 'white', fontSize: '0.65rem', padding: '3px', textAlign: 'center', fontWeight: '800', zIndex: 2 }}>
                                            ⚠ AWAITING APPROVAL
                                        </div>
                                        {photoApprovalCandidate.pending_identity_photo_url ? (
                                            <img src={photoApprovalCandidate.pending_identity_photo_url} alt="Pending" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                        ) : (
                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%', color: '#9ca3af' }}>
                                                <i className="fa-solid fa-camera" style={{ fontSize: '3rem' }} />
                                            </div>
                                        )}
                                    </div>
                                    <div style={{ marginTop: '8px', fontSize: '0.78rem', fontWeight: '700', color: '#B45309' }}>New Photo (Pending)</div>
                                </div>
                            </div>
                            <div style={{ background: '#fef3c7', borderRadius: '10px', padding: '12px 14px', marginBottom: '18px', border: '1px solid #fcd34d', fontSize: '0.82rem', color: '#78350f', lineHeight: 1.5 }}>
                                <i className="fa-solid fa-circle-info" style={{ marginRight: '6px' }} />
                                Approve only if the new photo clearly belongs to the same person. This action overwrites the registered face for this PAN and clears the mismatch flag.
                            </div>
                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button onClick={() => setPhotoApprovalCandidate(null)} style={{ flex: 1, padding: '12px', background: '#fff', border: '1px solid #d1d5db', borderRadius: '10px', cursor: 'pointer', fontWeight: '700', color: '#374151' }}>
                                    Cancel
                                </button>
                                <button
                                    onClick={submitPhotoApproval}
                                    disabled={photoApprovalSubmitting}
                                    style={{ flex: 1, padding: '12px', background: photoApprovalSubmitting ? '#9ca3af' : '#059669', color: '#fff', border: 'none', borderRadius: '10px', cursor: photoApprovalSubmitting ? 'not-allowed' : 'pointer', fontWeight: '800' }}
                                >
                                    {photoApprovalSubmitting ? '⏳ Updating...' : '✅ Approve & Update'}
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default ResultsAI;