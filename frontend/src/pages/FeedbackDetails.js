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
                                    <div key={idx} style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', borderLeft: '4px solid #3b82f6', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <h2 style={{ margin: 0, color: '#0f172a', fontSize: '1.25rem' }}>
                                                    {headerText}
                                                </h2>
                                                <span style={{ 
                                                    fontSize: '0.75rem', 
                                                    fontWeight: '600', 
                                                    padding: '2px 8px', 
                                                    borderRadius: '12px', 
                                                    background: isPrimary ? '#dbeafe' : '#f1f5f9', 
                                                    color: isPrimary ? '#1e40af' : '#475569' 
                                                }}>
                                                    {isPrimary ? 'Interviewer' : 'Panel Member'}
                                                </span>
                                            </div>
                                            {f.participant_email && (
                                                <span style={{ fontSize: '0.875rem', color: '#64748b' }}>{f.participant_email}</span>
                                            )}
                                        </div>

                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', margin: '1rem 0' }}>
                                            <div>
                                                <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Overall Rating</div>
                                                {renderStars(f.interviewer_average_rating || f.interviewer_rating)}
                                            </div>
                                            {f.interviewer_technical_rating && (
                                                <div>
                                                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Technical Rating</div>
                                                    {renderStars(f.interviewer_technical_rating)}
                                                </div>
                                            )}
                                            {f.interviewer_communication_rating && (
                                                <div>
                                                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Communication Rating</div>
                                                    {renderStars(f.interviewer_communication_rating)}
                                                </div>
                                            )}
                                            {f.interviewer_team_fit_rating && (
                                                <div>
                                                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Team Fit Rating</div>
                                                    {renderStars(f.interviewer_team_fit_rating)}
                                                </div>
                                            )}
                                        </div>
                                        <div style={{ marginTop: '1rem' }}>
                                            <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#334155' }}>Feedback Notes:</strong>
                                            <div style={{ whiteSpace: 'pre-wrap', color: '#475569', lineHeight: '1.5', background: '#fff', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                                                {f.interviewer_feedback || 'No written feedback provided.'}
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
                            <div key={`cand-${idx}`} style={{ padding: '1.5rem', background: '#f8fafc', borderRadius: '8px', borderLeft: '4px solid #10b981', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                                <h2 style={{ marginTop: 0, color: '#0f172a', fontSize: '1.25rem' }}>Candidate's Experience</h2>
                                <div style={{ margin: '1rem 0' }}>
                                    <div style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.25rem' }}>Candidate Rating</div>
                                    {renderStars(f.candidate_rating)}
                                </div>
                                <div style={{ marginTop: '1rem' }}>
                                    <strong style={{ display: 'block', marginBottom: '0.5rem', color: '#334155' }}>Feedback Notes:</strong>
                                    <div style={{ whiteSpace: 'pre-wrap', color: '#475569', lineHeight: '1.5', background: '#fff', padding: '1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
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
        </div>
    );
}
