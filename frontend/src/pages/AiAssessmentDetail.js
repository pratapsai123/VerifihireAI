import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';
import { API_BASE_URL } from '../apiConfig';

const AiAssessmentDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const initialTab = searchParams.get('tab') || 'overview';
    const subIdParam = searchParams.get('subId');

    const [assessment, setAssessment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState(initialTab);
    const [selectedSubmission, setSelectedSubmission] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);

    // Interviewer Assignment State
    const [availableInterviewers, setAvailableInterviewers] = useState([]);
    const [loadingInterviewers, setLoadingInterviewers] = useState(false);
    const [assigning, setAssigning] = useState(false);

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/ai/${id}/`);
                setAssessment(response.data);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching assessment detail:', err);
                setError('Failed to load assessment details.');
                setLoading(false);
            }
        };
        fetchDetail();
    }, [id]);

    useEffect(() => {
        if (!loading && assessment && subIdParam && !selectedSubmission) {
            const sub = (assessment.submissions || []).find(s => String(s.id) === String(subIdParam));
            if (sub) {
                setSelectedSubmission(sub);
                setActiveTab('submissions');
            }
        }
    }, [loading, assessment, subIdParam, selectedSubmission]);

    useEffect(() => {
        if (activeTab === 'interviewers') {
            const fetchAvailable = async () => {
                setLoadingInterviewers(true);
                try {
                    const response = await axios.get(`${API_BASE_URL}/ai/${id}/available-interviewers/`);
                    setAvailableInterviewers(response.data);
                } catch (err) {
                    console.error('Error fetching available interviewers:', err);
                } finally {
                    setLoadingInterviewers(false);
                }
            };
            fetchAvailable();
        }
    }, [id, activeTab]);

    const handleToggleInterviewer = async (interviewerId) => {
        const currentlyAssigned = assessment.assigned_interviewers.map(i => i.id);
        let newIds;
        if (currentlyAssigned.includes(interviewerId)) {
            newIds = currentlyAssigned.filter(id => id !== interviewerId);
        } else {
            newIds = [...currentlyAssigned, interviewerId];
        }

        setAssigning(true);
        try {
            await axios.post(`${API_BASE_URL}/ai/${id}/assign-interviewers/`, {
                interviewer_ids: newIds
            });
            // Refresh detail to get updated assigned list
            const resp = await axios.get(`${API_BASE_URL}/ai/${id}/`);
            setAssessment(resp.data);
        } catch (err) {
            console.error('Error assigning interviewer:', err);
            alert('Failed to update interviewer assignment.');
        } finally {
            setAssigning(false);
        }
    };

    if (loading) return <div className="loading">Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;
    if (!assessment) return <div>Assessment not found.</div>;

    const mcqs = assessment.generated_content?.mcqs || [];
    const coding = assessment.generated_content?.coding_challenges || [];
    const submissions = assessment.submissions || [];

    // Pagination logic for submissions
    const itemsPerPage = 10;
    const indexOfLastSubmission = currentPage * itemsPerPage;
    const indexOfFirstSubmission = indexOfLastSubmission - itemsPerPage;
    const currentSubmissions = submissions.slice(indexOfFirstSubmission, indexOfLastSubmission);
    const totalPages = Math.ceil(submissions.length / itemsPerPage);

    // Calculate points based on backend logic (SubmitAssessmentView)
    const MCQ_WEIGHT = 20;
    const codingWeights = { 'Easy': 100, 'Medium': 200, 'Hard': 300 };

    const possibleMcqPoints = mcqs.length * MCQ_WEIGHT;
    const possibleCodingPoints = coding.reduce((sum, c) => sum + (codingWeights[c.difficulty] || 200), 0);
    const totalPossiblePoints = possibleMcqPoints + possibleCodingPoints;

    const getStatusStyle = (status) => {
        const s = status?.toLowerCase();
        if (s === 'selected' || s === 'qualified') return { background: '#E6FBF5', color: '#05CD99' };
        if (s === 'rejected' || s === 'not qualified') return { background: '#FFF5F5', color: '#EE5D50' };
        return { background: '#F4F7FE', color: '#A3AED0' };
    };

    return (
        <div className="dashboard-container" style={{ background: '#F4F7FE', minHeight: '100vh', padding: '2rem' }}>
            <div className="dashboard-main" style={{ maxWidth: '1200px', margin: '0 auto' }}>

                {/* Back Button & Header */}
                <div style={{ marginBottom: '2rem' }}>
                    <button
                        onClick={() => navigate('/ai-assessments')}
                        style={{ background: 'none', border: 'none', color: '#4318FF', fontWeight: '700', cursor: 'pointer', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}
                    >
                        <i className="fa-solid fa-arrow-left"></i> Back to Archive
                    </button>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                            <h1 style={{ color: '#1B254B', fontSize: '2.2rem', fontWeight: '800', margin: 0 }}>
                                {assessment.required_skills} <span style={{ color: '#707EAE', fontWeight: '400', fontSize: '1.2rem' }}>Assessment Results</span>
                            </h1>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', color: '#A3AED0', marginTop: '0.8rem', fontSize: '0.85rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <i className="fa-regular fa-calendar-plus" style={{ color: '#4318FF' }}></i>
                                    <span>Available From: <span style={{ fontWeight: '700', color: '#1B254B' }}>{assessment.available_from ? new Date(assessment.available_from).toLocaleString() : new Date(assessment.created_at).toLocaleString()}</span></span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <i className="fa-regular fa-calendar-xmark" style={{ color: '#EE5D50' }}></i>
                                    <span>Available Until: <span style={{ fontWeight: '700', color: '#1B254B' }}>{assessment.available_until ? new Date(assessment.available_until).toLocaleString() : 'No Limit'}</span></span>
                                </div>
                            </div>
                        </div>
                        <div style={{ background: 'white', padding: '1rem 1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', textAlign: 'center' }}>
                            <div style={{ fontSize: '0.8rem', color: '#A3AED0', fontWeight: '700', textTransform: 'uppercase' }}>Submissions</div>
                            <div style={{ fontSize: '1.8rem', fontWeight: '800', color: '#4318FF' }}>{submissions.length}</div>
                        </div>
                    </div>
                </div>

                {/* Main Tabs - Only show if NO specific tab requested in URL (optional, or just hide always if strict) 
                    But user asked for "when I click view... only question paper", implying strict separation.
                    Let's hide tabs if 'tab' param is present.
                */}
                {!searchParams.get('tab') && (
                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '2px solid #E0E5F2' }}>
                        <button
                            onClick={() => { setActiveTab('questions'); setSelectedSubmission(null); }}
                            style={{ padding: '1rem 2rem', background: 'none', border: 'none', borderBottom: activeTab === 'questions' ? '4px solid #4318FF' : 'none', color: activeTab === 'questions' ? '#1B254B' : '#A3AED0', fontWeight: '700', fontSize: '1.1rem', cursor: 'pointer' }}
                        >
                            Question Paper
                        </button>
                        <button
                            onClick={() => { setActiveTab('submissions'); setCurrentPage(1); }}
                            style={{ padding: '1rem 2rem', background: 'none', border: 'none', borderBottom: activeTab === 'submissions' ? '4px solid #4318FF' : 'none', color: activeTab === 'submissions' ? '#1B254B' : '#A3AED0', fontWeight: '700', fontSize: '1.1rem', cursor: 'pointer' }}
                        >
                            Candidate Submissions
                        </button>
                        <button
                            onClick={() => { setActiveTab('interviewers'); setSelectedSubmission(null); }}
                            style={{ padding: '1rem 2rem', background: 'none', border: 'none', borderBottom: activeTab === 'interviewers' ? '4px solid #4318FF' : 'none', color: activeTab === 'interviewers' ? '#1B254B' : '#A3AED0', fontWeight: '700', fontSize: '1.1rem', cursor: 'pointer' }}
                        >
                            Interviewer Pool
                        </button>
                    </div>
                )}

                {/* Content Area */}
                <div className="card" style={{ background: 'white', borderRadius: '30px', padding: '2.5rem', boxShadow: '0 20px 50px rgba(0,0,0,0.03)' }}>

                    {activeTab === 'questions' && (
                        <div>
                            <h3 style={{ color: '#1B254B', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <i className="fa-solid fa-file-lines" style={{ color: '#4318FF' }}></i> Generated Question Set
                            </h3>

                            {/* MCQs */}
                            <div style={{ marginBottom: '3rem' }}>
                                <h4 style={{ color: '#707EAE', textTransform: 'uppercase', fontSize: '0.9rem', letterSpacing: '1px', marginBottom: '1.5rem' }}>Multiple Choice Questions ({mcqs.length})</h4>
                                <div style={{ display: 'grid', gap: '1.5rem' }}>
                                    {mcqs.map((q, i) => (
                                        <div key={i} style={{ padding: '1.5rem', background: '#F8F9FF', borderRadius: '20px', border: '1px solid #E0E5F2' }}>
                                            <p style={{ fontWeight: '700', color: '#1B254B', fontSize: '1.1rem', marginBottom: '1rem' }}>Q{i + 1}: {q.question}</p>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                                {q.options.map((opt, oi) => (
                                                    <div key={oi} style={{ padding: '0.8rem 1rem', background: opt === q.answer ? '#E6FBF5' : 'white', borderRadius: '12px', border: '1px solid', borderColor: opt === q.answer ? '#05CD99' : '#E0E5F2', color: opt === q.answer ? '#05CD99' : '#1B254B', fontWeight: opt === q.answer ? '700' : '500', fontSize: '0.9rem' }}>
                                                        {opt} {opt === q.answer && <i className="fa-solid fa-check-circle" style={{ marginLeft: '5px' }}></i>}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Coding */}
                            {coding.length > 0 && (
                                <div>
                                    <h4 style={{ color: '#707EAE', textTransform: 'uppercase', fontSize: '0.9rem', letterSpacing: '1px', marginBottom: '1.5rem' }}>Coding Challenges ({coding.length})</h4>
                                    <div style={{ display: 'grid', gap: '1.5rem' }}>
                                        {coding.map((c, i) => (
                                            <div key={i} style={{ padding: '1.5rem', background: '#F8F9FF', borderRadius: '20px', border: '1px solid #E0E5F2' }}>
                                                <p style={{ fontWeight: '700', color: '#1B254B', fontSize: '1.1rem', marginBottom: '0.5rem' }}>{c.title}</p>
                                                <p style={{ color: '#707EAE', fontSize: '0.95rem', marginBottom: '1rem' }}>{c.problem_statement}</p>
                                                <div style={{ background: '#1B254B', color: '#05CD99', padding: '1rem', borderRadius: '12px', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                                    {typeof c.starter_code === 'object' && c.starter_code
                                                        ? (c.starter_code.python || c.starter_code.javascript || '// Multiple language snippets available')
                                                        : (c.starter_code || '// Starter code not provided')}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Scoring Footer */}
                            <div style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '2px solid #E0E5F2', display: 'flex', gap: '2rem', justifyContent: 'flex-start' }}>
                                <div style={{ background: '#F4F7FE', padding: '1.5rem', borderRadius: '20px', minWidth: '200px' }}>
                                    <div style={{ fontSize: '0.8rem', color: '#A3AED0', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Total Possible Points</div>
                                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
                                        <div style={{ fontSize: '2rem', fontWeight: '800', color: '#1B254B', lineHeight: '1' }}>{totalPossiblePoints}</div>
                                        <div style={{ fontSize: '0.9rem', color: '#707EAE', paddingBottom: '4px' }}>pts</div>
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: '#A3AED0', marginTop: '0.5rem' }}>
                                        ({mcqs.length} MCQs × {MCQ_WEIGHT} pts + {coding.length} Coding Tasks)
                                    </div>
                                </div>

                                <div style={{ background: '#F4F7FE', padding: '1.5rem', borderRadius: '20px', minWidth: '200px' }}>
                                    <div style={{ fontSize: '0.8rem', color: '#A3AED0', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Coding Time</div>
                                    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
                                        <div style={{ fontSize: '2rem', fontWeight: '800', color: '#1B254B', lineHeight: '1' }}>{assessment.duration_minutes}</div>
                                        <div style={{ fontSize: '0.9rem', color: '#707EAE', paddingBottom: '4px' }}>mins</div>
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: '#A3AED0', marginTop: '0.5rem' }}>
                                        Total allocated assessment duration
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'submissions' && !selectedSubmission && (
                        <div>
                            <h3 style={{ color: '#1B254B', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <i className="fa-solid fa-users" style={{ color: '#4318FF' }}></i> Candidate Performance
                            </h3>
                            {submissions.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '3rem', color: '#A3AED0' }}>
                                    <i className="fa-solid fa-hourglass" style={{ fontSize: '3rem', marginBottom: '1rem', display: 'block' }}></i>
                                    No submissions yet for this assessment.
                                </div>
                            ) : (
                                <div className="table-container">
                                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                        <thead>
                                            <tr style={{ textAlign: 'left', borderBottom: '2px solid #E0E5F2' }}>
                                                <th style={{ padding: '1rem', color: '#A3AED0', fontSize: '0.8rem', textTransform: 'uppercase' }}>Candidate</th>
                                                <th style={{ padding: '1rem', color: '#A3AED0', fontSize: '0.8rem', textTransform: 'uppercase' }}>Score</th>
                                                <th style={{ padding: '1rem', color: '#A3AED0', fontSize: '0.8rem', textTransform: 'uppercase' }}>Integrity</th>
                                                <th style={{ padding: '1rem', color: '#A3AED0', fontSize: '0.8rem', textTransform: 'uppercase' }}>Status</th>
                                                <th style={{ padding: '1rem', color: '#A3AED0', fontSize: '0.8rem', textTransform: 'uppercase' }}>Action</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {currentSubmissions.map((sub, i) => (
                                                <tr key={i} style={{ borderBottom: '1px solid #F4F7FE' }}>
                                                    <td style={{ padding: '1.2rem 1rem' }}>
                                                        <div style={{ fontWeight: '700', color: '#1B254B' }}>{sub.candidate_name}</div>
                                                        <div style={{ fontSize: '0.8rem', color: '#A3AED0' }}>{sub.candidate_email}</div>
                                                    </td>
                                                    <td style={{ padding: '1rem' }}>
                                                        <div style={{ fontSize: '1.1rem', fontWeight: '800', color: sub.percentage >= assessment.pass_threshold ? '#05CD99' : '#EE5D50' }}>{sub.percentage}%</div>
                                                        <div style={{ fontSize: '0.75rem', color: '#A3AED0' }}>{sub.score} / {sub.results_breakdown?.total_possible || assessment.total_points || 'N/A'} pts</div>
                                                    </td>
                                                    <td style={{ padding: '1rem' }}>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                            <div style={{ width: '60px', height: '8px', background: '#E0E5F2', borderRadius: '10px', overflow: 'hidden' }}>
                                                                <div style={{ width: `${sub.integrity_score}%`, height: '100%', background: sub.integrity_score >= 50 ? '#05CD99' : '#EE5D50' }}></div>
                                                            </div>
                                                            <span style={{ fontWeight: '700', color: sub.integrity_score >= 50 ? '#05CD99' : '#EE5D50' }}>{sub.integrity_score}%</span>
                                                        </div>
                                                    </td>
                                                    <td style={{ padding: '1rem' }}>
                                                        <span style={{ padding: '0.4rem 0.8rem', borderRadius: '10px', fontSize: '0.75rem', fontWeight: '800', textTransform: 'uppercase', ...getStatusStyle(sub.status) }}>
                                                            {sub.status}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: '1rem' }}>
                                                        <button
                                                            onClick={() => setSelectedSubmission(sub)}
                                                            style={{ background: '#4318FF', color: 'white', border: 'none', padding: '0.6rem 1.2rem', borderRadius: '12px', fontWeight: '700', fontSize: '0.85rem', cursor: 'pointer', boxShadow: '0 4px 10px rgba(67, 24, 255, 0.2)' }}
                                                        >
                                                            View Details
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>

                                    {/* Pagination Controls */}
                                    {totalPages > 1 && (
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem', background: 'white', borderTop: '1px solid #e2e8f0' }}>
                                            <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>
                                                Showing {indexOfFirstSubmission + 1} to {Math.min(indexOfLastSubmission, submissions.length)} of {submissions.length} entries
                                            </span>
                                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                                <button
                                                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                                    disabled={currentPage === 1}
                                                    style={{ padding: '0.5rem 1rem', background: currentPage === 1 ? '#f8fafc' : 'white', border: '1px solid #e2e8f0', borderRadius: '8px', cursor: currentPage === 1 ? 'not-allowed' : 'pointer', color: currentPage === 1 ? '#94a3b8' : '#475569', fontSize: '0.85rem', fontWeight: '500', transition: 'all 0.2s' }}
                                                >
                                                    Previous
                                                </button>
                                                <div style={{ display: 'flex', alignItems: 'center', padding: '0 0.5rem', fontSize: '0.85rem', color: '#475569', fontWeight: '600' }}>
                                                    Page {currentPage} of {totalPages}
                                                </div>
                                                <button
                                                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                                    disabled={currentPage === totalPages}
                                                    style={{ padding: '0.5rem 1rem', background: currentPage === totalPages ? '#f8fafc' : 'white', border: '1px solid #e2e8f0', borderRadius: '8px', cursor: currentPage === totalPages ? 'not-allowed' : 'pointer', color: currentPage === totalPages ? '#94a3b8' : '#475569', fontSize: '0.85rem', fontWeight: '500', transition: 'all 0.2s' }}
                                                >
                                                    Next
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'submissions' && selectedSubmission && (
                        <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                                <button
                                    onClick={() => setSelectedSubmission(null)}
                                    style={{ background: 'none', border: 'none', color: '#707EAE', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
                                >
                                    <i className="fa-solid fa-arrow-left"></i> Back to List
                                </button>
                                <div style={{ textAlign: 'right' }}>
                                    <h4 style={{ margin: 0, color: '#1B254B' }}>{selectedSubmission.candidate_name}</h4>
                                    <span style={{ fontSize: '0.85rem', color: '#A3AED0' }}>{selectedSubmission.submitted_at}</span>
                                </div>
                            </div>

                            {selectedSubmission.is_resume_screening ? (
                                <div style={{ marginBottom: '3rem' }}>
                                    <div style={{ background: '#F8F9FF', padding: '2rem', borderRadius: '30px', border: '1px solid #4318FF44' }}>
                                        <h4 style={{ color: '#1B254B', marginTop: 0, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-file-lines" style={{ color: '#4318FF' }}></i>
                                            Candidate Written Paper (AI Interview Feedback)
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
                                            border: '1px solid #E0E5F2'
                                        }}>
                                            {typeof selectedSubmission.interview_summary === 'string'
                                                ? selectedSubmission.interview_summary
                                                : JSON.stringify(selectedSubmission.interview_summary, null, 2)}
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
                                        {/* MCQ Card */}
                                        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '25px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2' }}>
                                            <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>MCQ Score</div>
                                            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#4318FF' }}>
                                                {selectedSubmission.results_breakdown?.mcq?.total > 0
                                                    ? Math.round((selectedSubmission.mcq_score / selectedSubmission.results_breakdown.mcq.total) * 100)
                                                    : 0}%
                                            </div>
                                            <div style={{ color: '#1B254B', fontWeight: '600', fontSize: '0.9rem' }}>
                                                {Math.round(selectedSubmission.mcq_score / MCQ_WEIGHT)} / {(selectedSubmission.candidate_questions?.mcqs || assessment?.generated_content?.mcqs || []).length} Correct
                                            </div>
                                        </div>

                                        {/* Coding Card */}
                                        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '25px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2' }}>
                                            <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Coding Score</div>
                                            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#4318FF' }}>
                                                {selectedSubmission.results_breakdown?.coding?.total > 0
                                                    ? Math.round((selectedSubmission.coding_score / selectedSubmission.results_breakdown.coding.total) * 100)
                                                    : 0}%
                                            </div>
                                            <div style={{ color: '#1B254B', fontWeight: '600', fontSize: '0.9rem' }}>
                                                {selectedSubmission.coding_score} / {selectedSubmission.results_breakdown?.coding?.total || 0} pts
                                            </div>
                                        </div>

                                        {/* Integrity Card */}
                                        <div style={{ background: 'white', padding: '1.5rem', borderRadius: '25px', textAlign: 'center', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', border: '1px solid #E0E5F2' }}>
                                            <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Integrity</div>
                                            <div style={{ fontSize: '2.5rem', fontWeight: '800', color: (selectedSubmission.integrity_score || 0) >= 50 ? '#05CD99' : '#EE5D50' }}>
                                                {selectedSubmission.integrity_score || 0}%
                                            </div>
                                            <div style={{ color: (selectedSubmission.integrity_score || 0) >= 50 ? '#05CD99' : '#EE5D50', fontWeight: '800', textTransform: 'uppercase', fontSize: '0.8rem' }}>
                                                {(selectedSubmission.integrity_score || 0) >= 50 ? '✓ Reliable' : '⚠ Suspicious'}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Overall Result Banner */}
                                    <div style={{
                                        background: (selectedSubmission.status === 'selected' || selectedSubmission.status === 'Qualified' || selectedSubmission.status === 'Resume Passed') ? '#E6FBF5' : '#FFF5F5',
                                        padding: '1.5rem', borderRadius: '25px', textAlign: 'center', marginBottom: '3rem',
                                        border: `1px solid ${(selectedSubmission.status === 'selected' || selectedSubmission.status === 'Qualified' || selectedSubmission.status === 'Resume Passed') ? '#05CD99' : '#EE5D50'}`
                                    }}>
                                        <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.3rem' }}>Overall Result</div>
                                        <div style={{ fontSize: '2.5rem', fontWeight: '800', color: (selectedSubmission.status === 'selected' || selectedSubmission.status === 'Qualified' || selectedSubmission.status === 'Resume Passed') ? '#05CD99' : '#EE5D50' }}>{selectedSubmission.percentage}%</div>
                                        <div style={{ color: '#1B254B', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px' }}>{selectedSubmission.status}</div>
                                    </div>
                                </>
                            )}

                            {!selectedSubmission.is_resume_screening && (
                                <>
                                <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <i className="fa-solid fa-list-check" style={{ color: '#4318FF' }}></i> MCQ Answer Verification
                                </h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '4rem' }}>
                                    {(selectedSubmission.candidate_questions?.mcqs || assessment?.generated_content?.mcqs || []).map((q, i) => {
                                        const candAns = selectedSubmission.answers[`mcq_${i}`];
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
                                <div style={{ marginBottom: '4rem' }}>
                                    <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <i className="fa-solid fa-code" style={{ color: '#4318FF' }}></i> Coding Verification
                                    </h4>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
                                        {(selectedSubmission.candidate_questions?.coding_challenges || assessment?.generated_content?.coding_challenges || []).map((c, i) => {
                                            const candCode = selectedSubmission.answers[`coding_${i}`];
                                            const res = selectedSubmission.results_breakdown?.coding_results?.[i] || selectedSubmission.results_breakdown?.coding_results?.[String(i)] || {};
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
                                                                <div style={{ fontSize: '1.2rem', fontWeight: '900', color: res.pass_count === res.total_count ? '#05CD99' : '#F59E0B' }}>
                                                                    {res.pass_count || 0}/{res.total_count || 10}
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
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                                </>
                    )}

                    {/* Integrity Violations Log */}
                    {selectedSubmission.integrity_screenshots && selectedSubmission.integrity_screenshots.length > 0 && (
                        <div style={{ marginTop: '4rem' }}>
                            <h4 style={{ color: '#1B254B', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <i className="fa-solid fa-shield-halved" style={{ color: '#EE5D50' }}></i> Integrity Violations Log
                            </h4>
                            <p style={{ color: '#707EAE', marginBottom: '2rem', fontSize: '0.95rem' }}>
                                The following screenshots were captured automatically when integrity warnings were triggered.
                            </p>

                            {(() => {
                                // Group by event type
                                const groups = selectedSubmission.integrity_screenshots.reduce((acc, snap) => {
                                    let groupName = snap.event_type;
                                    const evt = snap.event_type;
                                    if (['window_switch', 'window_blur'].includes(evt)) groupName = 'Window Switch';
                                    else if (['face_detection_lost', 'face_detection_lost_rechecked'].includes(evt)) groupName = 'No Face Detection';
                                    else if (evt === 'multiface_detection') groupName = 'Multipeople Detection';
                                    else if (evt === 'tab_switch') groupName = 'Tab Switch';
                                    else if (evt === 'phone_detection') groupName = 'Phone Detection';
                                    else groupName = evt.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

                                    if (!acc[groupName]) acc[groupName] = [];
                                    acc[groupName].push(snap);
                                    return acc;
                                }, {});

                                return Object.entries(groups).map(([groupName, snaps], idx) => (
                                    <div key={idx} style={{ marginBottom: '3rem' }}>
                                        <h5 style={{ color: '#1B254B', fontSize: '1.1rem', fontWeight: '800', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{ color: '#EE5D50' }}>Warning:</span> {groupName}
                                        </h5>
                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
                                            {snaps.map((snap, sIdx) => (
                                                <div key={sIdx} style={{ background: '#F8F9FF', borderRadius: '15px', padding: '10px', border: '1px solid #E0E5F2', textAlign: 'center' }}>
                                                    <div style={{ width: '100%', height: '140px', background: '#e2e8f0', borderRadius: '10px', overflow: 'hidden', marginBottom: '10px', position: 'relative' }}>
                                                        <img
                                                            src={snap.screenshot_url || snap.webcam_screenshot_url}
                                                            alt={snap.event_type}
                                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                            onError={(e) => { e.target.src = 'https://placehold.co/400x300?text=Image+Not+Found'; }}
                                                        />
                                                        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(27, 37, 75, 0.7)', color: 'white', fontSize: '0.7rem', padding: '4px' }}>
                                                            {snap.screenshot_url ? 'Screen View' : 'Webcam View'}
                                                        </div>
                                                    </div>
                                                    <div style={{ color: '#707EAE', fontSize: '0.75rem', fontWeight: '600' }}>
                                                        {new Date(snap.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ));
                            })()}
                        </div>
                    )}
                </div>
                    )}

                {activeTab === 'interviewers' && (
                    <div>
                        <div style={{ marginBottom: '2rem' }}>
                            <h3 style={{ color: '#1B254B', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <i className="fa-solid fa-user-tie" style={{ color: '#4318FF' }}></i> Interviewer Assignment Pool
                            </h3>
                            <p style={{ color: '#707EAE', fontSize: '0.95rem' }}>
                                Assign team members who will be available to conduct live interviews for candidates of this assessment.
                                Candidates will book slots based on the aggregate availability of this pool.
                            </p>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
                            {loadingInterviewers ? (
                                <p>Loading team members...</p>
                            ) : availableInterviewers.length === 0 ? (
                                <p>No team members found. Invite them first in the Team Members page.</p>
                            ) : (
                                availableInterviewers.map(member => {
                                    const isAssigned = assessment.assigned_interviewers.some(i => i.id === member.id);
                                    return (
                                        <div
                                            key={member.id}
                                            style={{
                                                padding: '1.5rem',
                                                borderRadius: '20px',
                                                border: '2px solid',
                                                borderColor: isAssigned ? '#4318FF' : '#E0E5F2',
                                                background: isAssigned ? '#F4F7FE' : 'white',
                                                transition: 'all 0.2s',
                                                position: 'relative',
                                                opacity: assigning ? 0.7 : 1,
                                                pointerEvents: assigning ? 'none' : 'auto'
                                            }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                                                <div style={{
                                                    width: '45px', height: '45px', borderRadius: '12px', background: isAssigned ? '#4318FF' : '#F4F7FE',
                                                    color: isAssigned ? 'white' : '#4318FF', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontSize: '1.2rem', fontWeight: '800'
                                                }}>
                                                    {member.name.charAt(0)}
                                                </div>
                                                <button
                                                    onClick={() => handleToggleInterviewer(member.id)}
                                                    style={{
                                                        padding: '0.4rem 1rem', borderRadius: '10px', border: 'none',
                                                        background: isAssigned ? '#EE5D50' : '#4318FF',
                                                        color: 'white', fontWeight: '700', fontSize: '0.8rem', cursor: 'pointer'
                                                    }}
                                                >
                                                    {isAssigned ? 'Remove' : 'Assign'}
                                                </button>
                                            </div>
                                            <div style={{ fontWeight: '700', color: '#1B254B', fontSize: '1rem' }}>{member.name}</div>
                                            <div style={{ color: '#707EAE', fontSize: '0.85rem' }}>{member.email}</div>
                                            <div style={{
                                                display: 'inline-block', marginTop: '0.8rem', padding: '2px 8px',
                                                borderRadius: '6px', background: '#E0E5F2', color: '#1B254B',
                                                fontSize: '0.7rem', fontWeight: '800', textTransform: 'uppercase'
                                            }}>
                                                {member.role.replace('ROLE_', '').replace('_', ' ')}
                                            </div>
                                            {isAssigned && (
                                                <div style={{ position: 'absolute', top: '10px', right: '10px', color: '#4318FF' }}>
                                                    <i className="fa-solid fa-circle-check"></i>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>

                        {assessment.assigned_interviewers.length > 0 && (
                            <div style={{ marginTop: '2.5rem', padding: '1.5rem', background: '#E6FBF5', borderRadius: '15px', border: '1px solid #05CD99' }}>
                                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', color: '#05CD99', fontWeight: '700' }}>
                                    <i className="fa-solid fa-circle-info"></i>
                                    <span>Candidate View Ready</span>
                                </div>
                                <p style={{ color: '#1B254B', fontSize: '0.9rem', marginTop: '0.5rem', margin: 0 }}>
                                    Candidates can now book interview slots based on the combined availability of these {assessment.assigned_interviewers.length} interviewers.
                                </p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
        </div >

    );
};

export default AiAssessmentDetail;
