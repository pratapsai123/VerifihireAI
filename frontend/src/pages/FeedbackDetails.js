import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export default function FeedbackDetails() {
    const location = useLocation();
    const navigate = useNavigate();
    const { inv } = location.state || {};

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

    const { feedback } = inv;

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
        <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', fontFamily: 'sans-serif' }}>
            <button className="btn-secondary" style={{ marginBottom: '1rem' }} onClick={() => navigate('/live-interview-list')}>
                &larr; Back to Interviews
            </button>

            <div style={{ background: '#fff', borderRadius: '8px', padding: '2rem', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
                <h1 style={{ marginTop: 0, marginBottom: '0.5rem', color: '#1e293b' }}>Interview Feedback</h1>
                <p style={{ color: '#64748b', marginBottom: '2rem' }}>
                    <strong>Candidate:</strong> {inv.name || 'N/A'} &nbsp;|&nbsp;
                    <strong>Interviewer:</strong> {inv.interviewer_name || 'N/A'} &nbsp;|&nbsp;
                    <strong>Role:</strong> {inv.interview?.name || 'N/A'}
                </p>

                {feedback ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                        {/* Interviewer Feedback Section */}
                        <div style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', borderLeft: '4px solid #3b82f6' }}>
                            <h2 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.25rem' }}>Interviewer's Assessment</h2>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', margin: '1rem 0' }}>
                                <div>
                                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Overall Rating</div>
                                    {renderStars(feedback.interviewer_average_rating || feedback.interviewer_rating)}
                                </div>
                                {feedback.interviewer_technical_rating && (
                                    <div>
                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Technical Rating</div>
                                        {renderStars(feedback.interviewer_technical_rating)}
                                    </div>
                                )}
                                {feedback.interviewer_communication_rating && (
                                    <div>
                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Communication Rating</div>
                                        {renderStars(feedback.interviewer_communication_rating)}
                                    </div>
                                )}
                                {feedback.interviewer_team_fit_rating && (
                                    <div>
                                        <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Team Fit Rating</div>
                                        {renderStars(feedback.interviewer_team_fit_rating)}
                                    </div>
                                )}
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#334155' }}>Feedback Notes:</strong>
                                <div style={{ whiteSpace: 'pre-wrap', color: '#475569', lineHeight: '1.5', background: '#fff', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                                    {feedback.interviewer_feedback || 'No written feedback provided.'}
                                </div>
                            </div>
                        </div>

                        {/* Candidate Feedback Section */}
                        <div style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
                            <h2 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.25rem' }}>Candidate's Experience</h2>
                            <div style={{ margin: '1rem 0' }}>
                                <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Candidate Rating</div>
                                {renderStars(feedback.candidate_rating)}
                            </div>
                            <div style={{ marginTop: '1rem' }}>
                                <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#334155' }}>Feedback Notes:</strong>
                                <div style={{ whiteSpace: 'pre-wrap', color: '#475569', lineHeight: '1.5', background: '#fff', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                                    {feedback.candidate_feedback || 'No written feedback provided.'}
                                </div>
                            </div>
                        </div>

                    </div>
                ) : (
                    <div style={{ padding: '2rem', textAlign: 'center', background: '#f1f5f9', borderRadius: '8px' }}>
                        <i className="fas fa-info-circle" style={{ fontSize: '2rem', color: '#94a3b8', marginBottom: '1rem' }}></i>
                        <p style={{ margin: 0, color: '#64748b' }}>No feedback has been submitted for this interview yet.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
