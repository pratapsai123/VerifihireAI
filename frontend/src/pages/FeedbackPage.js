import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/FeedbackPage.css';

const FeedbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // 1. Extract Details from URL
  const candidateName = searchParams.get('candidate') || 'Candidate Name';
  const interviewerName = searchParams.get('interviewer') || 'Interviewer Name';
  const totalTime = searchParams.get('time') || '00:00:00';
  const token = searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId') || '';

  // 2. State Management
  const [ratings, setRatings] = useState({
    solutionApproach: 0,
    codingLanguage: 0,
    codeCompleteness: 0,
    useCaseCoverage: 0,
    overallRating: 0
  });

  const [hoveredRatings, setHoveredRatings] = useState({
    solutionApproach: 0,
    codingLanguage: 0,
    codeCompleteness: 0,
    useCaseCoverage: 0,
    overallRating: 0
  });

  const [recommendToHire, setRecommendToHire] = useState('');
  const [comments, setComments] = useState('');

  const [skills, setSkills] = useState([
    { name: 'Problem Solving', score: 0, max: 5 },
    { name: 'Data Structures', score: 0, max: 5 },
    { name: 'Algorithms', score: 0, max: 5 },
    { name: 'Communication', score: 0, max: 5 }
  ]);

  const [isEditingSkills, setIsEditingSkills] = useState(false);
  const [editingSkills, setEditingSkills] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessPopup, setShowSuccessPopup] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // 3. Notifications Utility
  const showNotification = (message, type = 'info') => {
    const id = Date.now() + Math.random();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 4000);
  };

  // 4. Load Draft on Mount
  useEffect(() => {
    if (token) {
      const draftJson = localStorage.getItem(`feedback_draft_${token}`);
      if (draftJson) {
        try {
          const draft = JSON.parse(draftJson);
          setRatings({
            solutionApproach: draft.solutionApproach || 0,
            codingLanguage: draft.codingLanguage || 0,
            codeCompleteness: draft.codeCompleteness || 0,
            useCaseCoverage: draft.useCaseCoverage || 0,
            overallRating: draft.overallRating || 0
          });
          setRecommendToHire(draft.recommendToHire || '');
          setComments(draft.additionalComments || '');
          if (draft.skillsAssessment) {
            const loadedSkills = Object.keys(draft.skillsAssessment).map(name => ({
              name,
              score: draft.skillsAssessment[name].score || 0,
              max: draft.skillsAssessment[name].max || 5
            }));
            if (loadedSkills.length > 0) {
              setSkills(loadedSkills);
            }
          }
          showNotification('Draft loaded successfully!', 'info');
        } catch (e) {
          console.error('Error loading draft:', e);
        }
      }
    }
  }, [token]);

  // 5. Star Rating Actions
  const handleStarClick = (category, rating) => {
    setRatings(prev => ({ ...prev, [category]: rating }));
  };

  const handleStarMouseEnter = (category, rating) => {
    setHoveredRatings(prev => ({ ...prev, [category]: rating }));
  };

  const handleStarMouseLeave = (category) => {
    setHoveredRatings(prev => ({ ...prev, [category]: 0 }));
  };

  // 6. Skill Report Actions
  const handleStartEditSkills = () => {
    setEditingSkills(skills.map(s => ({ ...s })));
    setIsEditingSkills(true);
  };

  const handleEditSkillScore = (index, value) => {
    const next = [...editingSkills];
    next[index].score = Math.max(0, Math.min(5, Number(value) || 0));
    setEditingSkills(next);
  };

  const handleEditSkillName = (index, value) => {
    const next = [...editingSkills];
    next[index].name = value;
    setEditingSkills(next);
  };

  const handleAddNewSkill = () => {
    setEditingSkills(prev => [...prev, { name: '', score: 0, max: 5, isNew: true }]);
  };

  const handleSaveSkills = () => {
    const validated = editingSkills
      .filter(s => s.name.trim() !== '') // Remove unnamed skills
      .map(s => ({
        ...s,
        score: Math.max(0, Math.min(5, s.score))
      }));
    setSkills(validated);
    setIsEditingSkills(false);
    showNotification('Skills updated successfully!', 'success');
  };

  const handleCancelSkills = () => {
    setIsEditingSkills(false);
  };

  // 7. Form Validation
  const isFormValid =
    ratings.solutionApproach > 0 &&
    ratings.codingLanguage > 0 &&
    ratings.codeCompleteness > 0 &&
    ratings.useCaseCoverage > 0 &&
    ratings.overallRating > 0 &&
    recommendToHire !== '';

  // 8. Submit Feedback
  const handleSubmitFeedback = async () => {
    if (!token) {
      showNotification('Missing interview token.', 'error');
      return;
    }
    if (!isFormValid) {
      showNotification('Please fill out all required fields.', 'error');
      return;
    }

    setIsSubmitting(true);

    // Build structured skills assessment
    const skillsAssessment = {};
    skills.forEach(s => {
      skillsAssessment[s.name] = { score: s.score, max: s.max };
    });

    // Format legacy comments payload to preserve details on older backend models
    const formattedFeedback = `
Recommendation: ${recommendToHire}

--- Detailed Ratings ---
- Solution Approach: ${ratings.solutionApproach}/5
- Coding Language: ${ratings.codingLanguage}/5
- Code Completeness: ${ratings.codeCompleteness}/5
- Use Case Coverage: ${ratings.useCaseCoverage}/5
- Overall Rating: ${ratings.overallRating}/5

--- Skills Report ---
${skills.map(s => `- ${s.name}: ${s.score}/5`).join('\n')}

--- Detailed Comments ---
${comments || 'No additional comments provided.'}
    `.trim();

    const payload = {
      token: token,
      sessionId: token,
      feedback: formattedFeedback,
      rating: ratings.overallRating,
      technical_rating: ratings.solutionApproach,
      communication_rating: skills.find(s => s.name.toLowerCase().includes('comm'))?.score || ratings.overallRating,
      team_fit_rating: ratings.overallRating,
      role: 'interviewer',
      // Send modern structure as well
      candidateName,
      interviewerName,
      recommendToHire,
      additionalComments: comments,
      skillsAssessment
    };

    try {
      const response = await axios.post(`${API_BASE_URL}/submit-interview-feedback/`, payload);
      if (response.data && response.data.success) {
        setShowSuccessPopup(true);
        localStorage.removeItem(`feedback_draft_${token}`);
      } else {
        showNotification(response.data.error || 'Failed to submit feedback.', 'error');
      }
    } catch (err) {
      console.error('Error submitting feedback:', err);
      showNotification(err.response?.data?.error || 'An error occurred during submission.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 9. Save Draft
  const handleSaveDraft = () => {
    if (!token) {
      showNotification('Missing interview token.', 'error');
      return;
    }

    const skillsAssessment = {};
    skills.forEach(s => {
      skillsAssessment[s.name] = { score: s.score, max: s.max };
    });

    const draftData = {
      token: token,
      sessionId: token,
      candidateName: candidateName,
      interviewerName: interviewerName,
      solutionApproach: ratings.solutionApproach,
      codingLanguage: ratings.codingLanguage,
      codeCompleteness: ratings.codeCompleteness,
      useCaseCoverage: ratings.useCaseCoverage,
      overallRating: ratings.overallRating,
      recommendToHire: recommendToHire,
      additionalComments: comments,
      skillsAssessment,
      isDraft: true
    };

    localStorage.setItem(`feedback_draft_${token}`, JSON.stringify(draftData));
    showNotification('Draft saved successfully!', 'success');
  };

  // 10. Navigation Helpers
  const handleBackToInterview = () => {
    if (token) {
      window.location.href = `/live-interview/?token=${token}`;
    } else {
      navigate(-1);
    }
  };

  const handleCloseSuccessPopup = () => {
    setShowSuccessPopup(false);
    if (token) {
      window.location.href = `/candidate/`;
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="feedback-page">
      {/* Notifications Layer */}
      <div className="feedback-notifications-container">
        {notifications.map(n => (
          <div key={n.id} className={`feedback-notification ${n.type}`}>
            {n.message}
          </div>
        ))}
      </div>

      <div className="feedback-layout">
        {/* Header Block */}
        <header className="feedback-header-card">
          <button onClick={handleBackToInterview} className="feedback-back-btn">
            <i className="fas fa-arrow-left"></i> Back to Interview
          </button>

          <div className="feedback-participants-row">
            <div className="feedback-participant-item">
              <span className="label">Candidate:</span>
              <span className="value">{candidateName}</span>
            </div>
            <div className="feedback-participant-item">
              <span className="label">Interviewer:</span>
              <span className="value">{interviewerName}</span>
            </div>
            <div className="feedback-time-badge">
              <span className="time-lbl">TOTAL TIME</span>
              <span className="time-val">{totalTime}</span>
            </div>
          </div>
        </header>

        {/* Tab Row */}
        <div className="feedback-tabs-nav">
          <button className="tab-btn active">
            RATING & FEEDBACK
          </button>
        </div>

        {/* Dynamic Cards Grid */}
        <div className="feedback-grid">
          {/* Main Ratings Form */}
          <section className="feedback-card">
            <h3 className="card-title">
              My Feedback <span className="required">*</span>
            </h3>

            <div className="ratings-split-layout">
              {/* Star Ratings Left Column */}
              <div className="stars-column">
                {[
                  { key: 'solutionApproach', label: 'Solution approach' },
                  { key: 'codingLanguage', label: 'Coding language' },
                  { key: 'codeCompleteness', label: 'Code completeness' },
                  { key: 'useCaseCoverage', label: 'Use case coverage' }
                ].map(item => {
                  const currentRating = ratings[item.key];
                  const hoverRating = hoveredRatings[item.key];
                  const displayRating = hoverRating || currentRating;

                  return (
                    <div key={item.key} className="star-row">
                      <label className="star-label">{item.label}</label>
                      <div
                        className="stars-wrapper"
                        onMouseLeave={() => handleStarMouseLeave(item.key)}
                      >
                        {[1, 2, 3, 4, 5].map(star => (
                          <i
                            key={star}
                            className={`${star <= displayRating ? 'fas' : 'far'} fa-star interactive-star ${star <= displayRating ? 'filled' : ''}`}
                            onClick={() => handleStarClick(item.key, star)}
                            onMouseEnter={() => handleStarMouseEnter(item.key, star)}
                          ></i>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Overall & Recommendation Right Column */}
              <div className="comments-column">
                <div className="star-row">
                  <label className="star-label">Overall rating <span className="required">*</span></label>
                  <div
                    className="stars-wrapper"
                    onMouseLeave={() => handleStarMouseLeave('overallRating')}
                  >
                    {[1, 2, 3, 4, 5].map(star => (
                      <i
                        key={star}
                        className={`${star <= (hoveredRatings.overallRating || ratings.overallRating) ? 'fas' : 'far'} fa-star interactive-star ${star <= (hoveredRatings.overallRating || ratings.overallRating) ? 'filled' : ''}`}
                        onClick={() => handleStarClick('overallRating', star)}
                        onMouseEnter={() => handleStarMouseEnter('overallRating', star)}
                      ></i>
                    ))}
                  </div>
                </div>

                <div className="recommendation-group">
                  <label className="star-label">Recommend to hire? <span className="required">*</span></label>
                  <div className="radio-options-grid">
                    {['Qualified', 'Disqualified', 'On Hold', 'To be Rescheduled', 'No Show'].map(option => (
                      <label key={option} className="radio-label">
                        <input
                          type="radio"
                          name="hire"
                          value={option}
                          checked={recommendToHire === option}
                          onChange={(e) => {
                            setRecommendToHire(e.target.value);
                          }}
                          className="custom-radio"
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="comments-textarea-group">
                  <label className="star-label">Additional Comments</label>
                  <textarea
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    rows={4}
                    placeholder="Add any additional feedback or observations..."
                    className="feedback-textarea-input"
                  />
                </div>
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="feedback-actions">
              <button onClick={handleSaveDraft} className="btn-draft">
                Save as Draft
              </button>
              <button
                onClick={handleSubmitFeedback}
                disabled={!isFormValid || isSubmitting}
                className={`btn-submit-report ${!isFormValid ? 'disabled' : ''}`}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
              </button>
            </div>
          </section>

          {/* Skill Report Section */}
          <section className="feedback-card skill-report-card">
            <div className="card-header-row">
              <div>
                <h3 className="card-title">Skill Report</h3>
                <p className="card-subtitle">
                  Calculated with a weighted average of question difficulty
                </p>
              </div>
              {!isEditingSkills && (
                <button onClick={handleStartEditSkills} className="btn-edit-skills">
                  <i className="fas fa-edit"></i> Edit
                </button>
              )}
            </div>

            <div className="skills-content-area">
              {/* VIEW MODE */}
              {!isEditingSkills ? (
                <div className="skills-view-list">
                  <div className="skills-header-row">
                    <span>Skills</span>
                    <span>Score</span>
                  </div>
                  <div className="skills-grid-view">
                    {skills.map((skill, index) => (
                      <div key={index} className="skill-item-view-row">
                        <span className="skill-name">{skill.name}</span>
                        <span className="skill-score-badge">{skill.score}/5</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                /* EDIT MODE */
                <div className="skills-edit-list">
                  <div className="edit-list-container">
                    {editingSkills.map((skill, index) => (
                      <div key={index} className="skill-edit-item-row">
                        {skill.isNew ? (
                          <input
                            type="text"
                            placeholder="Skill Name"
                            value={skill.name}
                            onChange={(e) => handleEditSkillName(index, e.target.value)}
                            className="skill-name-input"
                          />
                        ) : (
                          <span className="skill-name-static">{skill.name}</span>
                        )}

                        <div className="score-input-wrapper">
                          <input
                            type="number"
                            min="0"
                            max="5"
                            value={skill.score}
                            onKeyDown={(e) => e.preventDefault()} // Block manual typing
                            onChange={(e) => handleEditSkillScore(index, e.target.value)}
                            className="skill-score-input"
                          />
                          <span className="score-max-lbl">/5</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="skills-edit-footer">
                    <button onClick={handleAddNewSkill} className="btn-add-skill">
                      <i className="fas fa-plus"></i> Add New Skill
                    </button>
                    <div className="edit-actions-group">
                      <button onClick={handleCancelSkills} className="btn-cancel-skills">
                        Cancel
                      </button>
                      <button onClick={handleSaveSkills} className="btn-save-skills">
                        Save
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>
      </div>

      {/* Success Modal Overlay */}
      {showSuccessPopup && (
        <div className="success-overlay-backdrop">
          <div className="success-modal-card">
            <div className="success-icon-badge">
              <i className="fas fa-check-circle"></i>
            </div>
            <h3 className="success-title">Feedback Submitted!</h3>
            <p className="success-msg">Your interview feedback was saved successfully.</p>
            <button onClick={handleCloseSuccessPopup} className="btn-close-success">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackPage;
