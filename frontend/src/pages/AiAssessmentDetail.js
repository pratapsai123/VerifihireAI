import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const AiAssessmentDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [assessment, setAssessment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    // Default to 'questions' if no tab param or invalid param
    const initialTab = searchParams.get('tab') === 'submissions' ? 'submissions' : 'questions';
    const [activeTab, setActiveTab] = useState(initialTab);
    const [selectedSubmission, setSelectedSubmission] = useState(null);

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const response = await axios.get(`http://localhost:8001/api/ai/${id}/`);
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

    if (loading) return <div className="loading">Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;
    if (!assessment) return <div>Assessment not found.</div>;

    const mcqs = assessment.generated_content?.mcqs || [];
    const coding = assessment.generated_content?.coding_challenges || [];
    const submissions = assessment.submissions || [];

    const getStatusStyle = (status) => {
        return status === 'selected'
            ? { background: '#E6FBF5', color: '#05CD99' }
            : { background: '#FFF5F5', color: '#EE5D50' };
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
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#A3AED0', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                                <i className="fa-regular fa-calendar-check"></i>
                                <span>Created on: <span style={{ fontWeight: '600', color: '#707EAE' }}>{assessment.created_at}</span></span>
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
                            onClick={() => setActiveTab('submissions')}
                            style={{ padding: '1rem 2rem', background: 'none', border: 'none', borderBottom: activeTab === 'submissions' ? '4px solid #4318FF' : 'none', color: activeTab === 'submissions' ? '#1B254B' : '#A3AED0', fontWeight: '700', fontSize: '1.1rem', cursor: 'pointer' }}
                        >
                            Candidate Submissions
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
                                                    {c.starter_code || '// Starter code not provided'}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
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
                                            {submissions.map((sub, i) => (
                                                <tr key={i} style={{ borderBottom: '1px solid #F4F7FE' }}>
                                                    <td style={{ padding: '1.2rem 1rem' }}>
                                                        <div style={{ fontWeight: '700', color: '#1B254B' }}>{sub.candidate_name}</div>
                                                        <div style={{ fontSize: '0.8rem', color: '#A3AED0' }}>{sub.candidate_email}</div>
                                                    </td>
                                                    <td style={{ padding: '1rem' }}>
                                                        <div style={{ fontSize: '1.1rem', fontWeight: '800', color: sub.percentage >= 60 ? '#05CD99' : '#EE5D50' }}>{sub.percentage}%</div>
                                                        <div style={{ fontSize: '0.75rem', color: '#A3AED0' }}>{sub.score}/{sub.total_questions} MCQs</div>
                                                    </td>
                                                    <td style={{ padding: '1rem' }}>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                            <div style={{ width: '60px', height: '8px', background: '#E0E5F2', borderRadius: '10px', overflow: 'hidden' }}>
                                                                <div style={{ width: `${sub.integrity_score}%`, height: '100%', background: sub.integrity_score >= 70 ? '#05CD99' : '#EE5D50' }}></div>
                                                            </div>
                                                            <span style={{ fontWeight: '700', color: sub.integrity_score >= 70 ? '#05CD99' : '#EE5D50' }}>{sub.integrity_score}%</span>
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

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '3rem' }}>
                                <div style={{ background: '#F8F9FF', padding: '1.5rem', borderRadius: '25px', textAlign: 'center' }}>
                                    <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>MCQ Score</div>
                                    <div style={{ fontSize: '2.5rem', fontWeight: '800', color: '#4318FF' }}>{selectedSubmission.percentage}%</div>
                                    <div style={{ color: '#1B254B', fontWeight: '600' }}>{selectedSubmission.score} Correct</div>
                                </div>
                                <div style={{ background: '#F8F9FF', padding: '1.5rem', borderRadius: '25px', textAlign: 'center' }}>
                                    <div style={{ color: '#A3AED0', fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '0.5rem' }}>Integrity Score</div>
                                    <div style={{ fontSize: '2.5rem', fontWeight: '800', color: selectedSubmission.integrity_score >= 70 ? '#05CD99' : '#EE5D50' }}>{selectedSubmission.integrity_score}%</div>
                                    <div style={{ color: '#1B254B', fontWeight: '600' }}>{selectedSubmission.integrity_score >= 70 ? 'High Trust' : 'Suspicious'}</div>
                                </div>
                            </div>

                            <h4 style={{ color: '#1B254B', marginBottom: '1.5rem' }}>Answer Verification</h4>
                            <div style={{ display: 'grid', gap: '1.5rem' }}>
                                {mcqs.map((q, i) => {
                                    const candAns = selectedSubmission.answers[`mcq_${i}`];
                                    const isCorrect = candAns === q.answer;
                                    return (
                                        <div key={i} style={{ padding: '1.5rem', borderRadius: '20px', border: '2px solid', borderColor: isCorrect ? '#05CD9922' : '#EE5D5022', background: isCorrect ? '#05CD9905' : '#EE5D5005' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                                <p style={{ fontWeight: '700', color: '#1B254B', margin: 0 }}>Q{i + 1}: {q.question}</p>
                                                {isCorrect ? (
                                                    <span style={{ color: '#05CD99', fontWeight: '800', fontSize: '0.8rem' }}><i className="fa-solid fa-circle-check"></i> CORRECT</span>
                                                ) : (
                                                    <span style={{ color: '#EE5D50', fontWeight: '800', fontSize: '0.8rem' }}><i className="fa-solid fa-circle-xmark"></i> INCORRECT</span>
                                                )}
                                            </div>
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                                                <div style={{ padding: '1rem', background: 'white', borderRadius: '12px', border: '1px solid #E0E5F2' }}>
                                                    <div style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: '700', textTransform: 'uppercase' }}>Candidate's Answer</div>
                                                    <div style={{ color: isCorrect ? '#05CD99' : '#EE5D50', fontWeight: '700', marginTop: '4px' }}>{candAns || '(Skipped)'}</div>
                                                </div>
                                                <div style={{ padding: '1rem', background: 'white', borderRadius: '12px', border: '1px solid #E0E5F2' }}>
                                                    <div style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: '700', textTransform: 'uppercase' }}>Correct Answer</div>
                                                    <div style={{ color: '#05CD99', fontWeight: '700', marginTop: '4px' }}>{q.answer}</div>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Coding Submissions */}
                            {coding.length > 0 && (
                                <div style={{ marginTop: '3rem' }}>
                                    <h4 style={{ color: '#1B254B', marginBottom: '1.5rem' }}>Coding Challenge Responses</h4>
                                    <div style={{ display: 'grid', gap: '2rem' }}>
                                        {coding.map((c, i) => (
                                            <div key={i}>
                                                <p style={{ fontWeight: '700', color: '#1B254B', marginBottom: '1rem' }}>Challenge: {c.title}</p>
                                                <div style={{ position: 'relative' }}>
                                                    <div style={{ position: 'absolute', top: '10px', right: '15px', color: '#707EAE', fontSize: '0.7rem', fontWeight: '700' }}>CANDIDATE CODE</div>
                                                    <textarea
                                                        readOnly
                                                        value={selectedSubmission.answers[`coding_${i}`] || '// No response submitted'}
                                                        style={{ width: '100%', minHeight: '300px', background: '#1B254B', color: '#05CD99', padding: '2rem 1.5rem 1.5rem', borderRadius: '20px', fontFamily: 'monospace', fontSize: '0.9rem', border: 'none', resize: 'none' }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default AiAssessmentDetail;
