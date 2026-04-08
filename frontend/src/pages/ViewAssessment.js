import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import Header from '../components/Header';
import '../styles/ReviewPage.css';

const MANUAL_TOPIC_LABEL = 'Custom Questions';

export default function ViewAssessment() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAssessment = async () => {
      setLoading(true);
      try {
        const resp = await axios.get(`${API_BASE_URL}/assessments/${id}/`);
        setAssessment(resp.data);
      } catch (err) {
        setError(err?.response?.data?.error || err?.message || 'Failed to load assessment details');
      } finally {
        setLoading(false);
      }
    };
    fetchAssessment();
  }, [id]);

  if (loading) return <div className="review-page"><div className="loading-container">Loading assessment details...</div></div>;
  if (error) return <div className="review-page"><div className="error-container">{error}<br /><button onClick={() => navigate('/assessments')} className="btn-primary" style={{ marginTop: '20px' }}>Back to Assessments</button></div></div>;
  if (!assessment) return null;

  // Group questions by topic
  const questionsByTopic = {};
  const topics = [];

  // Objective Questions
  if (Array.isArray(assessment.questions)) {
    assessment.questions.forEach(q => {
      const topic = q.topic || MANUAL_TOPIC_LABEL;
      if (!questionsByTopic[topic]) {
        questionsByTopic[topic] = [];
        topics.push(topic);
      }
      questionsByTopic[topic].push(q);
    });
  }

  // Coding Questions
  if (Array.isArray(assessment.coding_questions) && assessment.coding_questions.length > 0) {
    questionsByTopic['Coding'] = assessment.coding_questions;
    topics.push('Coding');
  }

  return (
    <div className="review-page-container">
      <Header />
      <div className="page-container">
        <div className="review-wrapper">
          <div className="header-left" style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '2rem' }}>
            <button className="back-button" onClick={() => navigate('/assessments')} style={{ background: 'none', border: 'none', color: '#2563eb', cursor: 'pointer', fontSize: '1rem', fontWeight: '600' }}>
              ← Back
            </button>
            <h3 className="page-title-centered" style={{ margin: 0 }}>View Assessment</h3>
          </div>

          <div className="summary-section">
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Assessment Name:</span>
                <span className="summary-value">{assessment.display_name || assessment.name}</span>
              </div>

              <div className="summary-item">
                <span className="summary-label">Experience Level:</span>
                <span className="summary-value" style={{ textTransform: 'capitalize' }}>{assessment.experience_level || 'N/A'}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Total Time:</span>
                <span className="summary-value" style={{ color: '#16a34a', fontWeight: '900' }}>{assessment.total_time || '00:00:00'}</span>
              </div>

              {(assessment.questions || []).length > 0 && (
                <>
                  <div className="summary-item">
                    <span className="summary-label">Obj Questions:</span>
                    <span className="summary-value">{assessment.questions.length}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Obj Time (HH:MM:SS):</span>
                    <span className="summary-value">{assessment.objective_time_limit || assessment.total_time || '00:00:00'}</span>
                  </div>
                </>
              )}

              {(assessment.coding_questions || []).length > 0 && (
                <>
                  <div className="summary-item">
                    <span className="summary-label">Coding Questions:</span>
                    <span className="summary-value">{assessment.coding_questions.length}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Coding Time (HH:MM:SS):</span>
                    <span className="summary-value">{assessment.coding_time_limit || assessment.total_time || '00:00:00'}</span>
                  </div>
                </>
              )}

              <div className="summary-item">
                <span className="summary-label">Min Pass %:</span>
                <span className="summary-value">{assessment.min_pass_percentage}%</span>
              </div>

              {assessment.has_objective_cutoff && (
                <div className="summary-item">
                  <span className="summary-label">Obj Cutoff %:</span>
                  <span className="summary-value">{assessment.min_objective_pass_percentage}%</span>
                </div>
              )}

              {(assessment.questions || []).length > 0 && (assessment.coding_questions || []).length > 0 && (
                <div className="summary-item" style={{ gridColumn: '1 / -1', marginTop: '10px', padding: '10px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <strong>Weights:</strong>
                    <span>Objective: {assessment.weightage_objective}%</span>
                    <div style={{ flex: 1, height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                      <div style={{ width: `${assessment.weightage_objective}%`, background: '#3b82f6' }}></div>
                      <div style={{ width: `${assessment.weightage_coding}%`, background: '#10b981' }}></div>
                    </div>
                    <span>Coding: {assessment.weightage_coding}%</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="topics-section">
            <h2 className="section-title" style={{ fontSize: '1.1rem' }}>Assessment Content</h2>
            {topics.length === 0 ? (
              <div className="empty-state">No questions found in this assessment.</div>
            ) : (
              topics.map(topic => (
                <div key={topic} className="topic-group" style={{ marginBottom: '2rem' }}>
                  <h3 className="section-title" style={{ borderBottom: '2px solid #e9ecef', paddingBottom: '0.5rem', fontSize: '1rem' }}>{topic} Questions</h3>
                  <div className="all-questions-list">
                    {(questionsByTopic[topic] || []).map((q, idx) => (
                      <div key={q.id || idx} className="question-card">
                        <div className="question-header">
                          <span className="question-number">Q{idx + 1}</span>
                          <span className="question-title">{q.question || q.title || q.problem_statement}</span>
                          <span className={`question-difficulty ${q.difficulty?.toLowerCase()}`} style={{ marginLeft: 'auto' }}>
                            {q.difficulty}
                          </span>
                        </div>
                        <div className="question-content">
                          {/* Objective Options */}
                          {q.question_type !== 'CODING' && (
                            <div className="question-options">
                              {['A', 'B', 'C', 'D'].map(key => {
                                const optionText = q[`option_${key.toLowerCase()}`];
                                if (!optionText) return null;

                                const isCorrect = q.question_type === 'MSQ'
                                  ? (Array.isArray(q.correct_answers) && q.correct_answers.includes(key))
                                  : (q.correct_answer === key);

                                return (
                                  <label key={key} className={`option-item ${isCorrect ? 'option-correct' : ''}`}>
                                    <span className={`option-control ${q.question_type === 'MSQ' ? 'checkbox' : 'radio'} ${isCorrect ? 'correct' : ''}`}>
                                      {key}
                                    </span>
                                    <span className="option-text">{optionText}</span>
                                  </label>
                                );
                              })}
                            </div>
                          )}

                          {/* Coding Specifics */}
                          {topic === 'Coding' && (
                            <div className="coding-details-view" style={{ marginTop: '10px', fontSize: '0.9rem', color: '#4b5563' }}>
                              <div className="detail-row">
                                <strong>Allowed Languages:</strong> {Array.isArray(q.languages) ? q.languages.join(', ') : (q.language || 'All')}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>

          <footer className="form-actions" style={{ justifyContent: 'center', gap: '15px' }}>
            <button className="btn btn-secondary" onClick={() => navigate('/assessments')}>
              Close View
            </button>
            <button 
              className="btn btn-primary" 
              onClick={() => navigate(`/invite-candidates/${id}`)}
              style={{ backgroundColor: '#2563eb' }}
            >
              Invite
            </button>
          </footer>
        </div>
      </div>
    </div>
  );
}
