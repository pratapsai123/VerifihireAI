import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import '../styles/ReviewPage.css';

const DIFFICULTY_WEIGHTS = {
  easy: 1,
  medium: 2,
  hard: 3,
};

function msToHHMMSS(ms) {
  const totalSeconds = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds].map((v) => String(v).padStart(2, '0')).join(':');
}

function hhmmssToMs(str) {
  if (!str) return null;
  const parts = str.split(':');
  if (parts.length > 3) return null;
  const [h, m = '0', s = '0'] = parts;
  const hours = Number(h || 0);
  const minutes = Number(m || 0);
  const seconds = Number(s || 0);
  if ([hours, minutes, seconds].some((v) => Number.isNaN(v))) return null;
  if (hours > 23) return null;
  if (minutes > 59 || seconds > 59) return null;
  if (hours === 23 && (minutes > 59 || seconds > 59)) return null;
  return (hours * 3600 + minutes * 60 + seconds) * 1000;
}

function cleanLangList(value) {
  if (!value) return [];
  const arr = Array.isArray(value) ? value : String(value).split(',');
  const seen = new Set();
  const out = [];
  arr.forEach((v) => {
    const cleaned = String(v || '').trim().toLowerCase();
    if (!cleaned) return;
    if (!seen.has(cleaned)) {
      seen.add(cleaned);
      out.push(cleaned);
    }
  });
  return out;
}

export default function CodingReview() {
  const navigate = useNavigate();
  const location = useLocation();
  const initialQuestions = useMemo(() => location.state?.codingQuestions || [], [location.state?.codingQuestions]);

  const [questions, setQuestions] = useState([]);
  const [assessmentName, setAssessmentName] = useState('');
  const [allowedLanguages, setAllowedLanguages] = useState('');
  const [minPassPercentage, setMinPassPercentage] = useState(60);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Initialize state from location
  useEffect(() => {
    if (!initialQuestions || initialQuestions.length === 0) {
      navigate('/coding', { replace: true });
      return;
    }

    // Initialize editable state
    const mapped = initialQuestions.map(q => ({
      ...q,
      // Default to question's value, fallback to medium/3000ms
      difficulty: (q.difficulty || 'medium').toLowerCase(),
      originalDifficulty: (q.difficulty || 'medium').toLowerCase(),
      time_limit_ms: Number(q.time_limit_ms) || 3000,
      originalTimeMs: Number(q.time_limit_ms) || 3000,
      // working state for time input
      timeInput: msToHHMMSS(Number(q.time_limit_ms) || 3000),
      timeError: '',
    }));
    setQuestions(mapped);

    // Name
    if (location.state?.assessmentName) {
      setAssessmentName(location.state.assessmentName);
    } else if (mapped.length === 1 && mapped[0]?.title) {
      setAssessmentName(mapped[0].title);
    } else {
      setAssessmentName('Coding Assessment');
    }

    // Languages
    const langs = [];
    mapped.forEach((q) => {
      const list = Array.isArray(q.languages) && q.languages.length > 0
        ? q.languages
        : q.language
          ? [q.language]
          : [];
      list.forEach((l) => langs.push(l));
    });
    setAllowedLanguages(cleanLangList(langs).join(', '));

  }, [initialQuestions, navigate, location.state]);

  // Calculations
  const totalQuestions = questions.length;

  const totalPoints = useMemo(() => {
    return questions.reduce((sum, q) => {
      const w = DIFFICULTY_WEIGHTS[q.difficulty] || 2;
      return sum + (100 * w);
    }, 0);
  }, [questions]);

  const totalCodingTimeSeconds = useMemo(() => {
    return questions.reduce((sum, q) => {
      // Sum only if not error
      if (q.timeError) return sum;
      return sum + Math.max(0, Math.floor((q.time_limit_ms || 0) / 1000));
    }, 0);
  }, [questions]);


  const updateQuestion = (idx, field, value) => {
    setQuestions(prev => {
      const next = [...prev];
      const item = { ...next[idx] };

      if (field === 'difficulty') {
        item.difficulty = value;
      } else if (field === 'timeInput') {
        let val = value.replace(/\D/g, '');
        if (val.length > 6) val = val.slice(0, 6);

        let formatted = val;
        if (val.length >= 5) {
          formatted = `${val.slice(0, 2)}:${val.slice(2, 4)}:${val.slice(4)}`;
        } else if (val.length >= 3) {
          formatted = `${val.slice(0, 2)}:${val.slice(2)}`;
        }

        item.timeInput = formatted;
        if (!formatted) {
          item.timeError = 'Required';
          item.time_limit_ms = null;
        } else {
          const ms = hhmmssToMs(formatted);
          if (ms == null) {
            item.timeError = 'Invalid time (max 23:59:59)';
            item.time_limit_ms = null;
          } else {
            item.timeError = '';
            item.time_limit_ms = ms;
          }
        }
      }

      next[idx] = item;
      return next;
    });
  };

  const createDraftCustomAssessment = async () => {
    const body = {
      user: {},
      assessment: {
        role: 'coding',
        number_of_questions: totalQuestions,
        time: msToHHMMSS(totalCodingTimeSeconds * 1000),
        auto_time: msToHHMMSS(totalCodingTimeSeconds * 1000),
        weights: { common: 70, role: 15, resume: 15 },
        question_distribution: {},
        removed_skills: [],
        extracted_skills: [],
        suggested_skills: [],
        common_skills: [],
      },
    };
    const resp = await axios.post(`${API_BASE_URL}/custom-assessments/`, body);
    return resp?.data?.id || null;
  };

  const handleCreate = async () => {
    setError('');
    if (questions.length === 0) {
      setError('No coding questions selected.');
      return;
    }
    if (questions.some(q => q.timeError || !q.time_limit_ms)) {
      setError('Please fix the errors in time allocation before proceeding.');
      return;
    }

    const allowed = cleanLangList(allowedLanguages);
    let customAssessmentId = location.state?.customAssessmentId || null;

    try {
      setSaving(true);
      if (!customAssessmentId) {
        customAssessmentId = await createDraftCustomAssessment();
      }
    } catch (e) {
      setSaving(false);
      setError(e?.response?.data?.error || e?.message || 'Failed to create draft custom assessment');
      return;
    }

    // Build coding_questions payload with overrides
    // Send [{id: ..., difficulty: ..., time_limit_ms: ...}]
    const codingQuestionsPayload = questions.map(q => ({
      id: q.id,
      difficulty: q.difficulty,
      time_limit_ms: q.time_limit_ms
    }));

    const payload = {
      custom_assessment_id: customAssessmentId,
      question_ids: [],
      coding_question_ids: codingQuestionsPayload, // SEND FULL OBJECTS NOW
      min_pass_percentage: Number(minPassPercentage),
      total_points: totalPoints,
      total_time: msToHHMMSS(totalCodingTimeSeconds * 1000), // Total time from all questions
      weightage_objective: 0,
      weightage_coding: 100,
    };

    if (allowed.length > 0) payload.coding_allowed_languages = allowed;
    if (assessmentName) {
      payload.name = assessmentName;
      payload.display_name = assessmentName;
    }
    if (location.state?.role) payload.role = location.state.role;
    if (location.state?.experienceLevel) payload.experience_level = location.state.experienceLevel;

    try {
      setSaving(true);
      const resp = await axios.post(`${API_BASE_URL}/assessments/`, payload);
      const newId = resp?.data?.assessment_id;
      if (!newId) {
        throw new Error('Assessment created, but no ID returned.');
      }
      alert('Assessment created successfully!');
      navigate(`/invite-candidates/${newId}`, { state: { assessmentName: assessmentName || 'Assessment' } });
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to create assessment');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="review-page-container">
      <Header />
      <div className="page-container">
        <div className="review-wrapper">
          <h3 className="page-title-centered">Review Coding Assessment</h3>

          <div className="summary-section">
            <div className="summary-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              <div className="summary-item">
                <span className="summary-label">Assessment Name</span>
                <input
                  className="coding-input"
                  value={assessmentName}
                  onChange={(e) => setAssessmentName(e.target.value)}
                  placeholder="Enter assessment name"
                  style={{ width: '100%', marginTop: '6px' }}
                />
              </div>
              <div className="summary-item">
                <span className="summary-label">Allowed Languages</span>
                <input
                  className="coding-input"
                  value={allowedLanguages}
                  onChange={(e) => setAllowedLanguages(e.target.value)}
                  placeholder="e.g. python, javascript"
                  style={{ width: '100%', marginTop: '6px' }}
                />
              </div>

              {/* Added Assessment Fields */}
              <div className="summary-item">
                <span className="summary-label">Questions Count</span>
                <span className="summary-value" style={{ fontSize: '1.2rem', marginTop: '6px', display: 'block' }}>{totalQuestions}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Min Pass % (Default 60%)</span>
                <input
                  type="number"
                  className="coding-input"
                  value={minPassPercentage}
                  onChange={(e) => {
                    const val = e.target.value;
                    if (val === '') {
                      setMinPassPercentage('');
                      return;
                    }
                    const num = Number(val);
                    if (num > 100) setMinPassPercentage(100);
                    else if (num < 0) setMinPassPercentage(0);
                    else setMinPassPercentage(val);
                  }}
                  min="0"
                  max="100"
                  style={{ width: '100%', marginTop: '6px' }}
                />
              </div>
              <div className="summary-item">
                <span className="summary-label">Total Possible Points</span>
                <span className="summary-value" style={{ fontSize: '1.2rem', marginTop: '6px', display: 'block', color: '#007bff' }}>{totalPoints}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Total Assessment Time</span>
                <span className="summary-value" style={{ fontSize: '1.2rem', marginTop: '6px', display: 'block', color: '#16a34a', fontWeight: 900 }}>
                  {msToHHMMSS(totalCodingTimeSeconds * 1000)}
                </span>
                <span style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px', display: 'block' }}>
                  (Sum of all question times)
                </span>
              </div>
            </div>
          </div>

          <div className="topics-section">
            <div className="all-questions-list">
              {questions.length === 0 ? (
                <div className="no-questions">
                  <p>No coding questions selected.</p>
                </div>
              ) : (
                <div className="questions-list">
                  {questions.map((q, idx) => (
                    <div key={q.id || idx} className="question-card">
                      <div className="question-header" style={{ justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                          <span className="question-number">Q{idx + 1}</span>
                          <span className="question-skill-badge">{(q.language || 'Coding').toString()}</span>
                        </div>
                        <button
                          className="btn-remove"
                          onClick={() => {
                            if (window.confirm('Remove this question?')) {
                              setQuestions(prev => prev.filter((_, i) => i !== idx));
                            }
                          }}
                          style={{
                            background: 'none',
                            border: 'none',
                            color: '#dc3545',
                            cursor: 'pointer',
                            fontSize: '0.9rem',
                            textDecoration: 'underline',
                            padding: 0
                          }}
                        >
                          Remove
                        </button>
                      </div>
                      <p className="question-text" style={{ margin: '0.5rem 0' }}>{q.title || q.description || 'Coding question'}</p>

                      {/* Editable Fields Grid */}
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'minmax(120px, auto) minmax(140px, auto) minmax(120px, auto) minmax(140px, auto)',
                        columnGap: '1.5rem',
                        marginTop: '1rem',
                        alignItems: 'start',
                        background: '#f8f9fa',
                        padding: '1rem',
                        borderRadius: '8px',
                        border: '1px solid #e9ecef'
                      }}>

                        {/* 1: Original Difficulty */}
                        <div>
                          <label style={{ fontSize: '0.75rem', color: '#6b7280', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.025em', fontWeight: '600' }}>Original Difficulty</label>
                          <div style={{ fontWeight: '500', textTransform: 'capitalize', padding: '6px 0', fontSize: '0.95rem' }}>{q.originalDifficulty}</div>
                        </div>

                        {/* 2: Difficulty Level */}
                        <div style={{ marginRight: '3rem' }}>
                          <label style={{ fontSize: '0.75rem', color: '#6b7280', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.025em', fontWeight: '600' }}>Difficulty Level</label>
                          <select
                            className="coding-input"
                            style={{ padding: '6px 8px', fontSize: '0.9rem', width: '100%', height: '36px' }}
                            value={q.difficulty}
                            onChange={(e) => updateQuestion(idx, 'difficulty', e.target.value)}
                          >
                            <option value="easy">Easy (1x)</option>
                            <option value="medium">Medium (2x)</option>
                            <option value="hard">Hard (3x)</option>
                          </select>
                        </div>

                        {/* 3: Original Time */}
                        <div>
                          <label style={{ fontSize: '0.75rem', color: '#6b7280', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.025em', fontWeight: '600' }}>Original Time</label>
                          <div style={{ fontWeight: '500', padding: '6px 0', fontSize: '0.95rem' }}>{msToHHMMSS(q.originalTimeMs)}</div>
                        </div>

                        {/* 4: Time Allocation */}
                        <div>
                          <label style={{ fontSize: '0.75rem', color: '#6b7280', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.025em', fontWeight: '600' }}>Time Allocation</label>
                          <input
                            className="coding-input"
                            style={{ padding: '6px 8px', fontSize: '0.9rem', width: '100px', height: '36px', borderColor: q.timeError ? '#dc3545' : undefined }}
                            value={q.timeInput}
                            placeholder="HH:MM:SS"
                            maxLength={8}
                            onChange={(e) => updateQuestion(idx, 'timeInput', e.target.value)}
                          />
                          {q.timeError && (
                            <div style={{ color: '#dc3545', fontSize: '0.7rem', marginTop: '4px', fontWeight: '500' }}>{q.timeError}</div>
                          )}
                        </div>

                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Footer Summary */}
          <div className="summary-section" style={{ marginTop: '2rem' }}>
            <div className="summary-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
              <div className="summary-item">
                <span className="summary-label">Coding Time (Total)</span>
                <span className="summary-value">{msToHHMMSS(totalCodingTimeSeconds * 1000)}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Total Points</span>
                <span className="summary-value" style={{ color: '#007bff' }}>{totalPoints}</span>
              </div>
            </div>
          </div>

          {error ? <div className="error-container"><p className="error-message">{error}</p></div> : null}

          <div className="form-actions" style={{ marginTop: '2rem' }}>
            <button type="button" onClick={() => navigate('/coding')} className="btn btn-secondary">
              Back
            </button>
            <button type="button" onClick={handleCreate} className="btn btn-primary" disabled={saving}>
              {saving ? 'Creating…' : 'Create Assessment'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

