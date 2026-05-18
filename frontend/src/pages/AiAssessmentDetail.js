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
    
    // Invited Candidates State
    const [invitedCandidates, setInvitedCandidates] = useState([]);
    const [candidatePointsInfo, setCandidatePointsInfo] = useState(null);
    const [loadingInvited, setLoadingInvited] = useState(false);

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

    // Fetch invited candidates data
    useEffect(() => {
        const fetchInvitedCandidates = async () => {
            setLoadingInvited(true);
            try {
                const response = await axios.get(`${API_BASE_URL}/ai/${id}/invited-candidates/`);
                setInvitedCandidates(response.data.invited_candidates || []);
                setCandidatePointsInfo(response.data.candidate_points || null);
            } catch (err) {
                console.error('Error fetching invited candidates:', err);
            } finally {
                setLoadingInvited(false);
            }
        };
        
        if (assessment) {
            fetchInvitedCandidates();
        }
    }, [id, assessment]);

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
    const MCQ_WEIGHT = 1;  // 1 point per MCQ
    const codingWeights = { 'Easy': 100, 'Medium': 200, 'Hard': 300 };

    const possibleMcqPoints = mcqs.length * MCQ_WEIGHT;
    const possibleCodingPoints = coding.reduce((sum, c) => sum + (codingWeights[c.difficulty] || 200), 0);
    const totalPossiblePoints = possibleMcqPoints + possibleCodingPoints;

    // Scoring weights from assessment (default 40/60)
    const mcqWeight = assessment.mcq_weight || 40;
    const codingWeight = assessment.coding_weight || (100 - mcqWeight);

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
                    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1.5rem' }}>
                        <div style={{ flex: '1 1 min-content', minWidth: 0 }}>
                            <div style={{ fontSize: '0.9rem', color: '#4318FF', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '0.4rem' }}>Assessment Results</div>
                            <h1 style={{ color: '#1B254B', fontSize: '2.2rem', fontWeight: '800', margin: 0, wordBreak: 'break-word', overflowWrap: 'anywhere', lineHeight: '1.2' }}>
                                {assessment.required_skills}
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
                        <div style={{ background: 'white', padding: '1rem 1.5rem', borderRadius: '20px', boxShadow: '0 10px 30px rgba(0,0,0,0.03)', textAlign: 'center', flexShrink: 0 }}>
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

                                                {/* Starter Code Preview */}
                                                <div style={{ background: '#1B254B', color: '#05CD99', padding: '1rem', borderRadius: '12px', fontFamily: 'monospace', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                                                    {typeof c.starter_code === 'object' && c.starter_code
                                                        ? (c.starter_code.python || c.starter_code.javascript || '// Multiple language snippets available')
                                                        : (c.starter_code || '// Starter code not provided')}
                                                </div>

                                                {/* Example Input/Output */}
                                                <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                                    <div style={{ background: '#F4F7FE', padding: '1rem', borderRadius: '12px' }}>
                                                        <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#A3AED0', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Example Input</div>
                                                        <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.85rem', color: '#1B254B', whiteSpace: 'pre-wrap' }}>{c.example_input || 'N/A'}</pre>
                                                    </div>
                                                    <div style={{ background: '#E6FBF5', padding: '1rem', borderRadius: '12px' }}>
                                                        <div style={{ fontSize: '0.7rem', fontWeight: '800', color: '#05CD99', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Expected Output</div>
                                                        <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.85rem', color: '#05CD99', fontWeight: '700', whiteSpace: 'pre-wrap' }}>{c.example_output || 'N/A'}</pre>
                                                    </div>
                                                </div>

                                                {/* Reference Solution (AI-Generated Answer) */}
                                                {c.reference_solution && (
                                                    <div style={{ marginTop: '1.5rem' }}>
                                                        <h5 style={{ fontSize: '0.8rem', color: '#707EAE', textTransform: 'uppercase', marginBottom: '0.8rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                            <i className="fa-solid fa-check-double" style={{ color: '#05CD99' }}></i> Verified Reference Solution (Python)
                                                        </h5>
                                                        <div style={{ position: 'relative' }}>
                                                            <div style={{
                                                                position: 'absolute', top: '-10px', right: '16px',
                                                                background: '#05CD99', color: 'white', padding: '3px 12px',
                                                                borderRadius: '8px', fontSize: '0.65rem', fontWeight: '800', zIndex: 1,
                                                                textTransform: 'uppercase', letterSpacing: '0.5px'
                                                            }}>✓ Execution Verified</div>
                                                            <div style={{
                                                                background: '#0D1117', borderRadius: '16px',
                                                                padding: '2rem 1.5rem 1.5rem', boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
                                                                border: '1px solid #30363D'
                                                            }}>
                                                                <pre style={{
                                                                    margin: 0, color: '#7EE787',
                                                                    fontFamily: "'Fira Code', 'Courier New', monospace",
                                                                    fontSize: '0.85rem', lineHeight: '1.7', whiteSpace: 'pre-wrap',
                                                                    overflowX: 'auto'
                                                                }}>
                                                                    {c.reference_solution}
                                                                </pre>
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Generated Hidden Test Cases */}
                                                {c.test_cases && c.test_cases.length > 0 && (
                                                    <div style={{ marginTop: '1.5rem' }}>
                                                        <h5 style={{ fontSize: '0.8rem', color: '#707EAE', textTransform: 'uppercase', marginBottom: '0.8rem', fontWeight: '800' }}>
                                                            Execution-Verified Test Cases
                                                        </h5>
                                                        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1rem' }}>
                                                            {c.test_cases.map((tc, j) => (
                                                                <div key={j} style={{ background: 'white', borderRadius: '12px', padding: '1rem', border: '1px solid #E0E5F2' }}>
                                                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                                        <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#4318FF' }}>TEST CASE {j + 1}</div>
                                                                        <div style={{ fontSize: '0.75rem', fontWeight: '800', color: tc.verified ? '#05CD99' : '#F59E0B' }}>
                                                                            {tc.verified ? '✓ Executed' : '⚠ Fallback'}
                                                                        </div>
                                                                    </div>
                                                                    <div style={{ fontSize: '0.8rem', color: '#707EAE', marginBottom: '0.25rem', fontWeight: 'bold' }}>Input:</div>
                                                                    <pre style={{ margin: '0 0 0.8rem 0', padding: '0.5rem', background: '#F8F9FF', borderRadius: '8px', fontSize: '0.8rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{tc.input}</pre>

                                                                    <div style={{ fontSize: '0.8rem', color: '#707EAE', marginBottom: '0.25rem', fontWeight: 'bold' }}>Expected Output:</div>
                                                                    <pre style={{ margin: 0, padding: '0.5rem', background: '#F8F9FF', borderRadius: '8px', fontSize: '0.8rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{tc.output}</pre>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Scoring Footer */}
                            <div style={{ marginTop: '3rem', paddingTop: '2rem', borderTop: '2px solid #E0E5F2' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2rem', marginBottom: '2rem' }}>
                                    {/* Candidate Points Card */}
                                    <div style={{ background: '#E6F7FF', padding: '1.5rem', borderRadius: '20px', borderLeft: '4px solid #4318FF' }}>
                                        <div style={{ fontSize: '0.8rem', color: '#4318FF', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Per Candidate Assessment</div>
                                        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', marginBottom: '0.8rem' }}>
                                            <div style={{ fontSize: '2rem', fontWeight: '800', color: '#1B254B', lineHeight: '1' }}>
                                                {(() => {
                                                    const divisor = assessment.same_questions_for_all ? 1 : (assessment.num_applicants || 1);
                                                    const cMcqs = candidatePointsInfo?.mcq_count || Math.floor(mcqs.length / divisor);
                                                    const cCoding = candidatePointsInfo?.coding_count || Math.floor(coding.length / divisor);
                                                    // Correct per-candidate coding points: use difficulty-based weights
                                                    const perCandidateCodingPts = coding
                                                        .slice(0, cCoding)
                                                        .reduce((s, c) => s + (codingWeights[c.difficulty] || 200), 0);
                                                    return (cMcqs * 1 + perCandidateCodingPts);
                                                })()}
                                            </div>
                                            <div style={{ fontSize: '0.9rem', color: '#707EAE', paddingBottom: '4px' }}>pts</div>
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: '#707EAE' }}>
                                            {(() => {
                                                const divisor = assessment.same_questions_for_all ? 1 : (assessment.num_applicants || 1);
                                                const cMcqs = candidatePointsInfo?.mcq_count || Math.floor(mcqs.length / divisor);
                                                const cCoding = candidatePointsInfo?.coding_count || Math.floor(coding.length / divisor);
                                                const codingDesc = coding.slice(0, cCoding).map(c => `${c.difficulty}(${codingWeights[c.difficulty] || 200}pts)`).join(', ');
                                                return `${cMcqs} MCQs × 1pt${cCoding > 0 ? ` + Coding: ${codingDesc}` : ''}`;
                                            })()}
                                        </div>
                                    </div>

                                    {/* Invited Candidates Card */}
                                    <div style={{ background: '#FFF4E6', padding: '1.5rem', borderRadius: '20px', borderLeft: '4px solid #FF9500' }}>
                                        <div style={{ fontSize: '0.8rem', color: '#FF9500', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Invited Candidates</div>
                                        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', marginBottom: '0.8rem' }}>
                                            <div style={{ fontSize: '2rem', fontWeight: '800', color: '#1B254B', lineHeight: '1' }}>
                                                {invitedCandidates.length} / {assessment.max_candidates_allowed || 1}
                                            </div>
                                            <div style={{ fontSize: '0.9rem', color: '#FF9500', paddingBottom: '4px' }}>candidates</div>
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: '#707EAE' }}>
                                            {assessment.max_candidates_allowed - invitedCandidates.length > 0 
                                                ? `${assessment.max_candidates_allowed - invitedCandidates.length} slot(s) available`
                                                : '🔒 No more slots available'}
                                        </div>
                                    </div>

                                    {/* Duration Card */}
                                    <div style={{ background: '#F4F7FE', padding: '1.5rem', borderRadius: '20px' }}>
                                        <div style={{ fontSize: '0.8rem', color: '#A3AED0', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Assessment Duration</div>
                                        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
                                            <div style={{ fontSize: '2rem', fontWeight: '800', color: '#1B254B', lineHeight: '1' }}>{assessment.duration_minutes}</div>
                                            <div style={{ fontSize: '0.9rem', color: '#707EAE', paddingBottom: '4px' }}>mins</div>
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: '#A3AED0', marginTop: '0.5rem' }}>
                                            Total allocated assessment duration
                                        </div>
                                    </div>

                                    {/* Scoring Weight Card */}
                                    <div style={{ background: 'linear-gradient(135deg, #EEF2FF, #F5F3FF)', padding: '1.5rem', borderRadius: '20px', border: '1px solid #E0E7FF' }}>
                                        <div style={{ fontSize: '0.8rem', color: '#6366F1', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Score Weighting</div>
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <span style={{ fontSize: '0.85rem', color: '#1B254B', fontWeight: '600' }}>MCQ</span>
                                                <span style={{ fontSize: '1rem', fontWeight: '800', color: '#6366F1' }}>{mcqWeight}%</span>
                                            </div>
                                            <div style={{ height: '6px', borderRadius: '6px', background: `linear-gradient(to right, #6366F1 ${mcqWeight}%, #E0E7FF ${mcqWeight}%)` }} />
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <span style={{ fontSize: '0.85rem', color: '#1B254B', fontWeight: '600' }}>Coding</span>
                                                <span style={{ fontSize: '1rem', fontWeight: '800', color: '#8B5CF6' }}>{codingWeight}%</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Invited Candidates List */}
                                {invitedCandidates.length > 0 && (
                                    <div style={{ marginTop: '2.5rem' }}>
                                        <h4 style={{ color: '#1B254B', fontSize: '1.1rem', fontWeight: '700', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <i className="fa-solid fa-envelope" style={{ color: '#FF9500' }}></i> 
                                            Invited Candidates ({invitedCandidates.length})
                                        </h4>
                                        <div style={{ background: '#F8F9FF', borderRadius: '15px', overflow: 'hidden', border: '1px solid #E0E5F2' }}>
                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr style={{ background: '#E6F7FF', borderBottom: '2px solid #D0E1FF' }}>
                                                        <th style={{ padding: '1rem', textAlign: 'left', color: '#4318FF', fontWeight: '700', fontSize: '0.9rem' }}>Sn.</th>
                                                        <th style={{ padding: '1rem', textAlign: 'left', color: '#4318FF', fontWeight: '700', fontSize: '0.9rem' }}>Name</th>
                                                        <th style={{ padding: '1rem', textAlign: 'left', color: '#4318FF', fontWeight: '700', fontSize: '0.9rem' }}>Email</th>
                                                        <th style={{ padding: '1rem', textAlign: 'left', color: '#4318FF', fontWeight: '700', fontSize: '0.9rem' }}>Invited At</th>
                                                        <th style={{ padding: '1rem', textAlign: 'left', color: '#4318FF', fontWeight: '700', fontSize: '0.9rem' }}>Status</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {invitedCandidates.map((candidate, idx) => (
                                                        <tr key={idx} style={{ borderBottom: '1px solid #E0E5F2', background: idx % 2 === 0 ? 'white' : '#F9FAFB' }}>
                                                            <td style={{ padding: '1rem', color: '#707EAE', fontSize: '0.9rem', fontWeight: '700' }}>{idx + 1}</td>
                                                            <td style={{ padding: '1rem', color: '#1B254B', fontSize: '0.9rem', fontWeight: '600' }}>{candidate.name}</td>
                                                            <td style={{ padding: '1rem' }}>
                                                                <a href={`mailto:${candidate.email}`} style={{ color: '#4318FF', textDecoration: 'none', fontWeight: '600', fontSize: '0.9rem' }}>
                                                                    {candidate.email}
                                                                </a>
                                                            </td>
                                                            <td style={{ padding: '1rem', color: '#707EAE', fontSize: '0.85rem' }}>
                                                                {new Date(candidate.invited_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit' })}
                                                            </td>
                                                            <td style={{ padding: '1rem' }}>
                                                                <span style={{
                                                                    padding: '0.4rem 0.8rem',
                                                                    borderRadius: '20px',
                                                                    fontSize: '0.8rem',
                                                                    fontWeight: '700',
                                                                    background: candidate.status === 'invited' ? '#E6FBF5' : candidate.status === 'completed' ? '#E6FBF5' : '#FFF5F5',
                                                                    color: candidate.status === 'invited' ? '#FF9500' : candidate.status === 'completed' ? '#05CD99' : '#EE5D50'
                                                                }}>
                                                                    {candidate.status.charAt(0).toUpperCase() + candidate.status.slice(1)}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}
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
                                                            {(() => {
                                                                const st = sub.status;
                                                                if (st === 'selected' || st === 'Qualified') return '✓ PASSED';
                                                                if (st === 'hold') return '⚠ HOLD';
                                                                return '✗ ' + st;
                                                            })()}
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
                                            Candidate: {selectedSubmission.candidate_name}
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
                                        </h3>

                                        {selectedSubmission.identity_mismatch_detected && (
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
                                            // Get candidate photo exclusively from the authorized registration
                                            const candidatePhoto = selectedSubmission.candidate_photo_url;
                                            return (
                                        <div style={{
                                            display: 'flex',
                                            gap: '2rem',
                                            alignItems: 'flex-start'
                                        }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', flexShrink: 0 }}>
                                            {/* Candidate Photo / Override Check */}
                                            {selectedSubmission.identity_mismatch_detected && (selectedSubmission.original_identity_photo_url || selectedSubmission.intruder_photo_url) ? (
                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', width: '180px' }}>
                                                    {/* ORIGINAL FACE */}
                                                    <div style={{
                                                        width: '180px',
                                                        height: '180px',
                                                        background: '#F4F7FE',
                                                        borderRadius: '12px',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        border: '2px solid #EE5D50',
                                                        overflow: 'hidden',
                                                        position: 'relative'
                                                    }}>
                                                        <div style={{
                                                            position: 'absolute', top: 0, left: 0, right: 0,
                                                            background: '#EE5D50', color: 'white',
                                                            fontSize: '0.7rem', padding: '2px', textAlign: 'center',
                                                            fontWeight: 'bold', zIndex: 2
                                                        }}>
                                                            ORIGINAL FACE
                                                        </div>
                                                        <img
                                                            src={selectedSubmission.original_identity_photo_url}
                                                            alt="Original Candidate"
                                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                                                        />
                                                        <div style={{ display: 'none', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                            <i className="fa-solid fa-user" style={{ fontSize: '4rem', color: '#A3AED0' }}></i>
                                                        </div>
                                                    </div>

                                                    {/* OVERRIDE FACE */}
                                                    <div style={{
                                                        width: '180px',
                                                        height: '180px',
                                                        background: '#F4F7FE',
                                                        borderRadius: '12px',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        border: '2px dashed #F59E0B',
                                                        overflow: 'hidden',
                                                        position: 'relative'
                                                    }}>
                                                        <div style={{
                                                            position: 'absolute', top: 0, left: 0, right: 0,
                                                            background: '#F59E0B', color: 'white',
                                                            fontSize: '0.7rem', padding: '2px', textAlign: 'center',
                                                            fontWeight: 'bold', zIndex: 2
                                                        }}>
                                                            ASSESSMENT FACE
                                                        </div>
                                                        <img
                                                            src={selectedSubmission.intruder_photo_url || candidatePhoto}
                                                            alt="Assessment Candidate"
                                                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                                            onError={(e) => { e.target.style.display = 'none'; e.target.nextSibling.style.display = 'flex'; }}
                                                        />
                                                        <div style={{ display: 'none', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%' }}>
                                                            <i className="fa-solid fa-user" style={{ fontSize: '4rem', color: '#A3AED0' }}></i>
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div style={{
                                                    width: '180px',
                                                    height: '180px',
                                                    background: '#F4F7FE',
                                                    borderRadius: '12px',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    border: '1px solid #E0E5F2',
                                                    overflow: 'hidden'
                                                }}>
                                                    {candidatePhoto ? (
                                                        <img
                                                            src={candidatePhoto}
                                                            alt="Candidate"
                                                            style={{
                                                                width: '100%',
                                                                height: '100%',
                                                                objectFit: 'cover'
                                                            }}
                                                            onError={(e) => {
                                                                e.target.style.display = 'none';
                                                                e.target.nextSibling.style.display = 'flex';
                                                            }}
                                                        />
                                                    ) : null}
                                                    <div style={{
                                                        display: candidatePhoto ? 'none' : 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        width: '100%',
                                                        height: '100%'
                                                    }}>
                                                        <i className="fa-solid fa-user" style={{
                                                            fontSize: '4rem',
                                                            color: '#A3AED0'
                                                        }}></i>
                                                    </div>
                                                </div>
                                            )}

                                            {/* PAN Card Photo */}
                                            {selectedSubmission.pan_photo && (
                                                <div style={{
                                                    width: '180px',
                                                    height: '120px',
                                                    background: '#F4F7FE',
                                                    borderRadius: '12px',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    border: '1px solid #E0E5F2',
                                                    overflow: 'hidden'
                                                }}>
                                                    <img
                                                        src={selectedSubmission.pan_photo}
                                                        alt="PAN Card"
                                                        style={{
                                                            width: '100%',
                                                            height: '100%',
                                                            objectFit: 'contain'
                                                        }}
                                                        onError={(e) => {
                                                            e.target.style.display = 'none';
                                                            e.target.nextSibling.style.display = 'flex';
                                                        }}
                                                    />
                                                    <div style={{
                                                        display: 'none',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        width: '100%',
                                                        height: '100%'
                                                    }}>
                                                        <i className="fa-solid fa-id-card" style={{
                                                            fontSize: '4rem',
                                                            color: '#A3AED0'
                                                        }}></i>
                                                    </div>
                                                </div>
                                            )}
                                            </div>

                                            {/* Information Table */}
                                            <div style={{ flex: 1 }}>
                                                <table style={{ 
                                                    width: '100%', 
                                                    borderCollapse: 'collapse',
                                                    background: 'white',
                                                    border: '1px solid #E0E5F2',
                                                    borderRadius: '12px',
                                                    overflow: 'hidden'
                                                }}>
                                                    <tbody>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B',
                                                                width: '35%'
                                                            }}>Full Name</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: '#1B254B' 
                                                            }}>{selectedSubmission.candidate_name}</td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Email</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: '#1B254B' 
                                                            }}>{selectedSubmission.candidate_email || 'N/A'}</td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Job Title</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: '#1B254B' 
                                                            }}>{assessment?.required_skills || assessment?.role_title || 'N/A'}</td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>MCQ Score</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: '#1B254B',
                                                                fontWeight: '700'
                                                            }}>
                                                                {selectedSubmission.results_breakdown?.mcq?.possible_points > 0
                                                                    ? Math.round((selectedSubmission.results_breakdown.mcq.scored_points / selectedSubmission.results_breakdown.mcq.possible_points) * 100)
                                                                    : 0}% ({Math.round(selectedSubmission.results_breakdown?.mcq?.scored_points || 0)} / {(selectedSubmission.candidate_questions?.mcqs || assessment?.generated_content?.mcqs || []).length} Correct)
                                                            </td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Coding Score</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: '#1B254B',
                                                                fontWeight: '700'
                                                            }}>
                                                                {selectedSubmission.results_breakdown?.coding?.possible_points > 0
                                                                    ? Math.round((selectedSubmission.results_breakdown.coding.scored_points / selectedSubmission.results_breakdown.coding.possible_points) * 100)
                                                                    : 0}% ({selectedSubmission.results_breakdown?.coding?.scored_points || 0} / {selectedSubmission.results_breakdown?.coding?.possible_points || 0} pts)
                                                            </td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Integrity Score</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: (selectedSubmission.integrity_score || 0) >= 50 ? '#05CD99' : '#EE5D50',
                                                                fontWeight: '700'
                                                            }}>
                                                                {selectedSubmission.integrity_score || 0}% {(selectedSubmission.integrity_score || 0) >= 50 ? '✓ Reliable' : '⚠ Suspicious'}
                                                            </td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Overall Result</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: (selectedSubmission.status === 'selected' || selectedSubmission.status === 'Qualified') ? '#05CD99' : selectedSubmission.status === 'hold' ? '#F59E0B' : '#EE5D50',
                                                                fontWeight: '800'
                                                            }}>
                                                                {selectedSubmission.percentage}%
                                                            </td>
                                                        </tr>
                                                        <tr style={{ borderBottom: '1px solid #E0E5F2' }}>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Status</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                fontWeight: '700',
                                                                textTransform: 'uppercase'
                                                            }}>
                                                                {(() => {
                                                                    const st = selectedSubmission.status;
                                                                    if (st === 'selected' || st === 'Qualified') return <span style={{ color: '#05CD99' }}>✓ Assessment Passed</span>;
                                                                    if (st === 'hold') return <span style={{ color: '#F59E0B' }}>⚠ HOLD — Manual Review Required</span>;
                                                                    return <span style={{ color: '#EE5D50' }}>✗ Not Qualified</span>;
                                                                })()}
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                background: '#F8F9FF',
                                                                fontWeight: '600',
                                                                color: '#1B254B'
                                                            }}>Submission Date</td>
                                                            <td style={{ 
                                                                padding: '0.75rem 1rem', 
                                                                color: '#1B254B' 
                                                            }}>{selectedSubmission.submitted_at}</td>
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

                            {!selectedSubmission.is_resume_screening && (
                                <>
                                    <h4 style={{ color: '#1B254B', marginBottom: '1.5rem', fontWeight: '800', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <i className="fa-solid fa-list-check" style={{ color: '#4318FF' }}></i> MCQ Answer Verification
                                    </h4>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '4rem' }}>
                                        {(selectedSubmission.candidate_questions?.mcqs || assessment?.generated_content?.mcqs || []).map((q, i) => {
                                            const actualAnswer = q.answer || q.correct_answer || q.ans || q.correct_option;
                                            const candAns = selectedSubmission.answers[`mcq_${i}`];
                                            const isCorrect = candAns === actualAnswer;
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
                                                            const isAnswer = opt === actualAnswer;

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
                                                                <div style={{ fontWeight: '700', color: '#1B254B', fontSize: '0.95rem' }}>{actualAnswer}</div>
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
                                                const resultsObj = selectedSubmission.results_breakdown?.coding_results || {};
                                                const res = resultsObj[i] || resultsObj[String(i)] || {};
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

                                                        {/* Generated Hidden Test Cases */}
                                                        {c.test_cases && c.test_cases.length > 0 && (
                                                            <div style={{ marginTop: '2rem' }}>
                                                                <h5 style={{ color: '#1B254B', fontSize: '1rem', fontWeight: '800', marginBottom: '1rem', textTransform: 'uppercase' }}>
                                                                    Execution-Verified Test Cases
                                                                </h5>
                                                                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1rem' }}>
                                                                    {c.test_cases.map((tc, j) => (
                                                                        <div key={j} style={{ background: '#F4F7FE', borderRadius: '12px', padding: '1rem', border: '1px solid #E0E5F2' }}>
                                                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                                                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#4318FF' }}>TEST CASE {j + 1}</div>
                                                                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: tc.verified ? '#05CD99' : '#F59E0B' }}>
                                                                                    {tc.verified ? '✓ Executed' : '⚠ Fallback'}
                                                                                </div>
                                                                            </div>
                                                                            <div style={{ fontSize: '0.85rem', color: '#707EAE', marginBottom: '0.25rem', fontWeight: 'bold' }}>Input:</div>
                                                                            <pre style={{ margin: '0 0 1rem 0', padding: '0.5rem', background: 'white', borderRadius: '8px', fontSize: '0.8rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{tc.input}</pre>

                                                                            <div style={{ fontSize: '0.85rem', color: '#707EAE', marginBottom: '0.25rem', fontWeight: 'bold' }}>Expected Output:</div>
                                                                            <pre style={{ margin: 0, padding: '0.5rem', background: 'white', borderRadius: '8px', fontSize: '0.8rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{tc.output}</pre>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
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
