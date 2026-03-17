import React, { useState } from 'react';
import { flushSync } from 'react-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import { SHARED_ROLES, STORAGE_KEYS } from '../utils/assessmentConstants';
import '../styles/TrueFalseQuestion.css';

function TrueFalseQuestion() {
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

  const [question, setQuestion] = useState('');
  const [assessmentName, setAssessmentName] = useState('');
  const [topicSkill, setTopicSkill] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [timeToAnswer, setTimeToAnswer] = useState('');
  const [timeError, setTimeError] = useState(null);
  const [correctAnswer, setCorrectAnswer] = useState(''); // 'A' (True) | 'B' (False)
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
    setQuestion('');
    setAssessmentName('');
    setTopicSkill('');
    setExperienceLevel('');
    setTimeToAnswer('');
    setTimeError(null);
    setCorrectAnswer('');
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
    const caid = assessmentContext?.customAssessmentId || assessmentContext?.id;
    if (!caid) {
      // eslint-disable-next-line no-alert
      alert('Custom assessment ID not found. Please go back to Review page and try again.');
      return;
    }

    const questionText = question.trim();
    const assessment = assessmentName.trim();
    const topic = topicSkill.trim();

    if (!questionText) {
      // eslint-disable-next-line no-alert
      alert('Please enter your question.');
      return;
    }
    if (!assessment) {
      // eslint-disable-next-line no-alert
      alert('Please select Assessment name.');
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
    if (!correctAnswer) {
      // eslint-disable-next-line no-alert
      alert('Please select the correct answer (True or False).');
      return;
    }

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
      question_type: 'TF',
      experience_level: experienceLevel,
      question: questionText,
      option_a: 'True',
      option_b: 'False',
      correct_answer: correctAnswer, // 'A' => True, 'B' => False
      time_to_answer: timeToAnswer,
      user_email: userEmail,
      organization_name: organizationName,
    };

    try {
      setIsSaving(true);
      await axios.post(`${API_BASE_URL}/questions/create/`, payload);
      navigate('/review-assessment', { state: { ...assessmentContext, refreshManual: true } });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error saving TF:', error);
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

  return (
    <div className="tfq-page">
      <Header />
      <div className="tfq-container">
        <div className="tfq-card">
          <div className="tfq-header-row">
            <button
              type="button"
              className="tfq-back-btn"
              onClick={handleBack}
              aria-label="Go back"
            >
              ← Back
            </button>
            <h1 className="tfq-title">Create True/False Question</h1>
            <div className="tfq-actions">
              <button
                type="button"
                className="tfq-btn tfq-btn-secondary"
                onClick={handleCancel}
              >
                Cancel
              </button>
              <button
                type="button"
                className="tfq-btn tfq-btn-primary"
                onClick={handleSave}
                disabled={isSaving || Boolean(timeError) || !timeToAnswer}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>

          <form className="tfq-form" onSubmit={(e) => e.preventDefault()}>
            {/* Question */}
            <div>
              <label className="tfq-field-label" htmlFor="question">
                Question
                <span className="tfq-required">*</span>
              </label>
              <textarea
                id="question"
                className="tfq-textarea"
                placeholder="Enter your question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
            </div>

            {/* Correct Answer */}
            <div>
              <label className="tfq-field-label">
                Correct Answer
                <span className="tfq-required">*</span>
              </label>
              <div className="tfq-tf-row">
                <button
                  type="button"
                  className={`tfq-tf-btn${correctAnswer === 'A' ? ' tfq-tf-btn--selected' : ''}`}
                  onClick={() => setCorrectAnswer('A')}
                >
                  True
                </button>
                <button
                  type="button"
                  className={`tfq-tf-btn${correctAnswer === 'B' ? ' tfq-tf-btn--selected' : ''}`}
                  onClick={() => setCorrectAnswer('B')}
                >
                  False
                </button>
              </div>
            </div>

            {/* Assessment, Topic/Skill, Experience, Time */}
            <div className="tfq-inline-row">
              <div>
                <label className="tfq-field-label" htmlFor="assessmentName">
                  Assessment name
                  <span className="tfq-required">*</span>
                </label>
                <select
                  id="assessmentName"
                  className="tfq-select"
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
                <label className="tfq-field-label" htmlFor="topicSkill">
                  Topic / Skill name
                  <span className="tfq-required">*</span>
                </label>
                <input
                  id="topicSkill"
                  type="text"
                  className="tfq-input"
                  placeholder="Enter topic/skill name"
                  value={topicSkill}
                  onChange={(e) => setTopicSkill(e.target.value)}
                />
              </div>

              <div>
                <label className="tfq-field-label" htmlFor="experienceLevel">
                  Experience Level
                  <span className="tfq-required">*</span>
                </label>
                <select
                  id="experienceLevel"
                  className="tfq-select"
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                >
                  <option value="">Select experience level</option>
                  <option value="entry">Entry Level (0-2 years)</option>
                  <option value="mid">Mid Level (2-5 years)</option>
                  <option value="senior">Senior Level (5-10 years)</option>
                  <option value="expert">Expert Level (10+ years)</option>
                </select>
              </div>

              <div>
                <label className="tfq-field-label" htmlFor="timeToAnswer">
                  Time to answer
                  <span className="tfq-required">*</span>
                </label>
                <input
                  id="timeToAnswer"
                  type="text"
                  className="tfq-input"
                  placeholder="mm:ss"
                  maxLength={5}
                  value={timeToAnswer}
                  onChange={handleTimeChange}
                  aria-invalid={Boolean(timeError)}
                />
                {timeError ? (
                  <p className="tfq-hint" style={{ color: '#dc2626' }}>
                    {timeError}
                  </p>
                ) : (
                  <p className="tfq-hint">Example: 01:30. Max allowed: 59:59.</p>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default TrueFalseQuestion;



