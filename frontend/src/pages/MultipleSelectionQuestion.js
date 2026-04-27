import React, { useState } from 'react';
import { flushSync } from 'react-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import { SHARED_ROLES, STORAGE_KEYS } from '../utils/assessmentConstants';
import '../styles/MultipleSelectionQuestion.css';

function MultipleSelectionQuestion() {
  const navigate = useNavigate();
  const location = useLocation();
  // State preservation: Use location.state or fallback to a dedicated storage key if available
  const assessmentContext = location.state || (window.location.hash.includes('review') ? null : JSON.parse(localStorage.getItem('temp_assessment_context')));

  // Persist context to handle refreshes
  React.useEffect(() => {
    if (location.state) {
      localStorage.setItem('temp_assessment_context', JSON.stringify(location.state));
    }
  }, [location.state]);
  const assessmentOptions = SHARED_ROLES;

  const initialAnswers = [
    { label: 'A', text: '', isCorrect: false },
    { label: 'B', text: '', isCorrect: false },
    { label: 'C', text: '', isCorrect: false },
    { label: 'D', text: '', isCorrect: false },
  ];

  const [description, setDescription] = useState('');
  const [assessmentName, setAssessmentName] = useState(assessmentContext?.assessmentName || '');
  const [topicSkill, setTopicSkill] = useState('');
  const [answers, setAnswers] = useState(initialAnswers);
  const [experienceLevel, setExperienceLevel] = useState('');
  const [timeToAnswer, setTimeToAnswer] = useState('');
  const [timeError, setTimeError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const getTimeError = (value) => {
    const text = (value || '').trim();
    if (!text) return 'Time to answer is required.';
    const match = text.match(/^(\d{1,2}):(\d{2})$/);
    if (!match) return 'Time must be in mm:ss format (example: 05:30).';
    const minutes = Number(match[1]);
    const seconds = Number(match[2]);
    if (Number.isNaN(minutes) || Number.isNaN(seconds)) return 'Invalid time value.';
    if (minutes > 59) return 'Minutes cannot exceed 59.';
    if (seconds > 59) return 'Seconds cannot exceed 59.';
    return null;
  };

  const handleAnswerTextChange = (index, value) => {
    setAnswers((prev) =>
      prev.map((a, i) => (i === index ? { ...a, text: value } : a))
    );
  };

  const handleToggleCorrect = (index) => {
    // Multiple answers allowed
    setAnswers((prev) =>
      prev.map((a, i) => (i === index ? { ...a, isCorrect: !a.isCorrect } : a))
    );
  };

  const handleAddChoice = () => {
    if (answers.length >= 4) return;
    const usedLabels = answers.map((a) => a.label);
    let nextLabel = 'A';
    for (let i = 0; i < 26; i += 1) {
      const candidate = String.fromCharCode(65 + i);
      if (!usedLabels.includes(candidate)) {
        nextLabel = candidate;
        break;
      }
    }
    setAnswers((prev) => [...prev, { label: nextLabel, text: '', isCorrect: false }]);
  };

  const handleRemoveChoice = (index) => {
    if (answers.length <= 2) return; // keep at least two options
    const updated = answers.filter((_, i) => i !== index);
    // Re-label as A, B, C...
    const relabeled = updated.map((a, i) => ({
      ...a,
      label: String.fromCharCode(65 + i),
    }));
    setAnswers(relabeled);
  };

  const handleTimeChange = (e) => {
    // simple mm:ss formatter
    let value = e.target.value.replace(/[^\d]/g, '');
    if (value.length > 4) value = value.slice(0, 4);
    if (value.length > 2) {
      value = `${value.slice(0, value.length - 2)}:${value.slice(-2)}`;
    }
    setTimeToAnswer(value);
    setTimeError(getTimeError(value));
  };

  const resetForm = () => {
    setDescription('');
    setAssessmentName('');
    setTopicSkill('');
    setAnswers(initialAnswers);
    setExperienceLevel('');
    setTimeToAnswer('');
    setTimeError(null);
  };

  const handleCancel = () => {
    // eslint-disable-next-line no-alert
    const confirmed = window.confirm('Are you sure you want to erase all entered data?');
    if (!confirmed) return;
    flushSync(() => {
      resetForm();
    });
  };

  const handleBack = () => {
    flushSync(() => {
      resetForm();
    });
    navigate('/manual-questions', { replace: true, state: assessmentContext });
  };

  const handleSave = async () => {
    const caid = assessmentContext?.customAssessmentId ||
      assessmentContext?.id ||
      localStorage.getItem(STORAGE_KEYS.DRAFT_ID);
    if (!caid) {
      // eslint-disable-next-line no-alert
      alert('Custom assessment ID not found. Please go back to Review page and try again.');
      return;
    }

    const questionText = description.trim();
    const assessment = assessmentName.trim();
    const topic = topicSkill.trim();
    const filledAnswers = answers.map((a) => ({ ...a, text: a.text.trim() }));

    if (!questionText) {
      // eslint-disable-next-line no-alert
      alert('Please enter your question.');
      return;
    }
    if (!assessment) {
      // eslint-disable-next-line no-alert
      alert('Please enter Assessment name.');
      return;
    }
    if (!topic) {
      // eslint-disable-next-line no-alert
      alert('Please enter Topic / Skill name.');
      return;
    }
    if (!experienceLevel) {
      // eslint-disable-next-line no-alert
      alert('Please select Experience Level.');
      return;
    }
    const currentTimeError = getTimeError(timeToAnswer);
    if (currentTimeError) {
      // eslint-disable-next-line no-alert
      alert(currentTimeError);
      return;
    }
    if (!filledAnswers[0]?.text || !filledAnswers[1]?.text) {
      // eslint-disable-next-line no-alert
      alert('All options must be filled. Please complete the missing ones.');
      return;
    }

    const correctLabels = filledAnswers.filter((a) => a.isCorrect).map((a) => a.label);
    if (correctLabels.length < 2) {
      // eslint-disable-next-line no-alert
      alert('Please select at least two correct answers for a multiple selection question.');
      return;
    }

    const optionByLabel = Object.fromEntries(filledAnswers.map((a) => [a.label, a.text]));
    let userEmail = null;
    let organizationName = null;
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userObj = JSON.parse(storedUser);
        userEmail = (userObj.email || '').toString().trim().toLowerCase() || null;
        organizationName = (userObj.organization_name || userObj.organizationName || '')
          .toString()
          .trim() || null;
      }
    } catch {
      // ignore
    }
    const payload = {
      custom_assessment_id: caid,
      assessment,
      topic,
      question_type: 'MSQ',
      experience_level: experienceLevel,
      question: questionText,
      option_a: optionByLabel.A || '',
      option_b: optionByLabel.B || '',
      option_c: optionByLabel.C || '',
      option_d: optionByLabel.D || '',
      correct_answers: correctLabels,
      time_to_answer: timeToAnswer,
      user_email: userEmail,
      organization_name: organizationName,
    };

    try {
      setIsSaving(true);
      await axios.post(`${API_BASE_URL}/questions/create/`, payload);
      navigate('/review-assessment', { state: { ...assessmentContext, refreshManual: true, onlyManual: false } });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error saving MSQ:', error);
      const message =
        error.response?.data?.error ||
        error.message ||
        'Failed to save question. Please try again.';
      // eslint-disable-next-line no-alert
      alert(message);
    } finally {
      setIsSaving(false);
    }
  };

  const inputType = 'checkbox';

  return (
    <div className="msq-page">
      <Header />
      <div className="msq-container">
        <div className="msq-card">
          <div className="msq-header-row">
            <button
              type="button"
              className="msq-back-btn"
              onClick={handleBack}
              aria-label="Go back"
            >
              ← Back
            </button>
            <h1 className="msq-title">Create Multiple Selection Question</h1>
            <div className="msq-actions">
              <button
                type="button"
                className="msq-btn msq-btn-secondary"
                onClick={handleCancel}
              >
                Cancel
              </button>
              <button
                type="button"
                className="msq-btn msq-btn-primary"
                onClick={handleSave}
                disabled={isSaving || Boolean(timeError) || !timeToAnswer}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>

          <form className="msq-form" onSubmit={(e) => e.preventDefault()}>
            {/* Question */}
            <div>
              <label className="msq-field-label" htmlFor="description">
                Question
                <span className="msq-required">*</span>
              </label>
              <textarea
                id="description"
                className="msq-textarea"
                placeholder="Enter your question"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Answer Choices */}
            <div>
              <label className="msq-field-label">
                Answer Choices
                <span className="msq-required">*</span>
              </label>
              <div className="msq-answer-list">
                {answers.map((answer, index) => (
                  <div key={answer.label} className="msq-answer-row">
                    <label className="msq-answer-label-wrapper">
                      <input
                        type={inputType}
                        name={`correct-answer-${answer.label}`}
                        checked={answer.isCorrect}
                        onChange={() => handleToggleCorrect(index)}
                        style={{ display: 'none' }}
                      />
                      <span
                        className={`msq-answer-label${answer.isCorrect ? ' msq-answer-label--selected' : ''
                          }`}
                      >
                        {answer.label}
                      </span>
                    </label>
                    <input
                      type="text"
                      className="msq-input msq-answer-input"
                      placeholder="Enter answer choice"
                      value={answer.text}
                      onChange={(e) =>
                        handleAnswerTextChange(index, e.target.value)
                      }
                    />
                    <button
                      type="button"
                      className="msq-answer-remove"
                      onClick={() => handleRemoveChoice(index)}
                      aria-label="Remove choice"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
              {answers.length < 4 && (
                <button
                  type="button"
                  className="msq-add-choice"
                  onClick={handleAddChoice}
                >
                  + Add new answer choice
                </button>
              )}
            </div>

            {/* Topic / Skill, Experience Level, Time */}
            <div className="msq-inline-row">
              <div>
                <label className="msq-field-label" htmlFor="assessmentName">
                  Assessment name
                  <span className="msq-required">*</span>
                </label>
                <select
                  id="assessmentName"
                  className="msq-select"
                  value={assessmentName}
                  onChange={(e) => setAssessmentName(e.target.value)}
                >
                  <option value="">Select assessment</option>
                  {assessmentOptions.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="msq-field-label" htmlFor="topicSkill">
                  Topic / Skill name
                  <span className="msq-required">*</span>
                </label>
                <input
                  id="topicSkill"
                  type="text"
                  className="msq-input"
                  placeholder="Enter topic/skill name"
                  value={topicSkill}
                  onChange={(e) => setTopicSkill(e.target.value)}
                />
              </div>

              <div>
                <label className="msq-field-label" htmlFor="experienceLevel">
                  Experience Level
                  <span className="msq-required">*</span>
                </label>
                <select
                  id="experienceLevel"
                  className="msq-select"
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                >
                  <option value="" disabled hidden>Select experience level</option>
                  <option value="entry">Entry Level (0-2 years)</option>
                  <option value="mid">Mid Level (2-5 years)</option>
                  <option value="senior">Senior Level (5-10 years)</option>
                  <option value="expert">Expert Level (10+ years)</option>
                </select>
              </div>

              <div>
                <label className="msq-field-label" htmlFor="timeToAnswer">
                  Time to answer
                  <span className="msq-required">*</span>
                </label>
                <input
                  id="timeToAnswer"
                  type="text"
                  className="msq-input"
                  placeholder="mm:ss"
                  maxLength={5}
                  value={timeToAnswer}
                  onChange={handleTimeChange}
                  aria-invalid={Boolean(timeError)}
                />
                {timeError ? (
                  <p className="msq-hint" style={{ color: '#dc2626' }}>
                    {timeError}
                  </p>
                ) : (
                  <p className="msq-hint">Example: 01:30. Max allowed: 59:59.</p>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default MultipleSelectionQuestion;



