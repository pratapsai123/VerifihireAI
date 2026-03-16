import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import '../styles/ManualQuestions.css';

function ManualQuestions() {
  const navigate = useNavigate();
  const location = useLocation();
  const assessmentContext = location.state || null;

  const handleBack = () => {
    if (assessmentContext) {
      navigate('/review-assessment', { state: assessmentContext });
      return;
    }
    navigate(-1);
  };

  const handleQuestionTypeClick = (type) => {
    const navState = assessmentContext;
    // Navigate based on question type
    switch (type) {
      case 'multiple-choice':
        navigate('/multiple-choice-question', { state: navState });
        break;
      case 'multiple-selection':
        navigate('/multiple-selection-question', { state: navState });
        break;
      case 'true-false':
        navigate('/true-false-question', { state: navState });
        break;
      case 'pdf-upload':
        navigate('/pdf-upload-question', { state: navState });
        break;
      case 'coding-challenge':
        navigate('/coding-challenge-question', { state: navState });
        break;
      default:
        console.log('Unknown question type:', type);
    }
  };

  return (
    <div className="manual-questions-container">

      {/* Main Content */}
      <div className="page-container">
        <button
          type="button"
          className="manual-back-btn"
          onClick={handleBack}
          aria-label="Go back to review"
        >
          ← Back
        </button>
        <h2 className="page-title">Create Custom Questions</h2>
        <p className="page-subtitle">Select a question type to get started</p>

        <div className="question-types-grid">
          {/* Multiple Choice */}
          <div
            className="question-type-card"
            onClick={() => handleQuestionTypeClick('multiple-choice')}
            style={{ cursor: 'pointer' }}
          >
            <div className="question-type-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#3b82f6" strokeWidth="2" fill="none" />
                <circle cx="12" cy="12" r="3" fill="#3b82f6" />
                <path d="M12 2v4M12 18v4M22 12h-4M6 12H2" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <h3 className="question-type-title">Multiple Choice</h3>
            <p className="question-type-description">
              Create questions with single correct answer from multiple options
            </p>
          </div>

          {/* Multiple Selection */}
          <div
            className="question-type-card"
            onClick={() => handleQuestionTypeClick('multiple-selection')}
            style={{ cursor: 'pointer' }}
          >
            <div className="question-type-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="#10b981" strokeWidth="2" fill="none" />
                <path d="M7 8h10M7 12h10M7 16h10" stroke="#10b981" strokeWidth="2" strokeLinecap="round" />
                <rect x="5" y="7" width="3" height="3" rx="1" fill="#10b981" />
                <rect x="5" y="11" width="3" height="3" rx="1" fill="#10b981" />
                <rect x="5" y="15" width="3" height="3" rx="1" fill="#10b981" />
              </svg>
            </div>
            <h3 className="question-type-title">Multiple Selection</h3>
            <p className="question-type-description">
              Create questions with multiple correct answers from options
            </p>
          </div>

          {/* True or False */}
          <div
            className="question-type-card"
            onClick={() => handleQuestionTypeClick('true-false')}
            style={{ cursor: 'pointer' }}
          >
            <div className="question-type-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="6" width="18" height="12" rx="2" stroke="#f59e0b" strokeWidth="2" fill="none" />
                <circle cx="9" cy="12" r="3" fill="#10b981" />
                <path d="M7 12l1.5 1.5L11 10" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="15" cy="12" r="3" fill="#ef4444" />
                <path d="M13 12h4M15 10v4" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <h3 className="question-type-title">True or False</h3>
            <p className="question-type-description">
              Create simple true/false questions with binary answers
            </p>
          </div>

          {/* PDF Uploading */}
          <div
            className="question-type-card"
            onClick={() => handleQuestionTypeClick('pdf-upload')}
            style={{ cursor: 'pointer' }}
          >
            <div className="question-type-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                <polyline points="14 2 14 8 20 8" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                <line x1="16" y1="13" x2="8" y2="13" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" />
                <line x1="16" y1="17" x2="8" y2="17" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" />
                <polyline points="10 9 9 9 8 9" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                <path d="M12 21v-6M9 18l3-3 3 3" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
              </svg>
            </div>
            <h3 className="question-type-title">PDF Uploading</h3>
            <p className="question-type-description">
              Upload PDF documents with questions and answers
            </p>
          </div>

          {/* Coding Challenge */}
          <div
            className="question-type-card"
            onClick={() => handleQuestionTypeClick('coding-challenge')}
            style={{ cursor: 'pointer' }}
          >
            <div className="question-type-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                <path d="M8 8L4 8L4 4L8 4" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                <path d="M20 20L16 20L16 16L20 16" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
              </svg>
            </div>
            <h3 className="question-type-title">Coding Challenge</h3>
            <p className="question-type-description">
              Create programming questions with code evaluation
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}

export default ManualQuestions;

