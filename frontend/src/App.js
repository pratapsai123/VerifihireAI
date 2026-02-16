import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import ForgotPassword from './pages/ForgotPassword';
import CustomAssessment from './pages/CustomAssessment';
import ReviewPage from './pages/ReviewPage';
import Assessment from './pages/Assessment';
import InviteCandidates from './pages/InviteCandidates';
import TakeAssessment from './pages/TakeAssessment';
import Result from './pages/Result';
import CandidatePage from './pages/CandidatePage';
import ManualQuestions from './pages/ManualQuestions';
import MultipleChoiceQuestion from './pages/MultipleChoiceQuestion';
import MultipleSelectionQuestion from './pages/MultipleSelectionQuestion';
import TrueFalseQuestion from './pages/TrueFalseQuestion';
import PdfUploadQuestion from './pages/PdfUploadQuestion';
import AcceptInvite from './pages/AcceptInvite';
import TeamMembers from './pages/TeamMembers';
import CodingHome from './pages/CodingHome';
import CodingQuestionForm from './pages/CodingQuestionForm';
import CodingAttempt from './pages/CodingAttempt';
import CodingReview from './pages/CodingReview';
import LiveInterview from './pages/LiveInterview';
import LiveInterviewInterviewer from './pages/LiveInterviewInterviewer';
import LiveInterviewList from './pages/LiveInterviewList';
import InterviewInvite from './pages/InterviewInvite';
import './App.css';

function App() {
  const [showCookieBanner, setShowCookieBanner] = useState(false);

  useEffect(() => {
    // Cookie consent
    if (!localStorage.getItem('cookie_consent')) {
      setTimeout(() => {
        setShowCookieBanner(true);
      }, 2000);
    }
  }, []);

  const handleCookieConsent = (consent) => {
    localStorage.setItem('cookie_consent', consent);
    setShowCookieBanner(false);
  };

  return (
    <BrowserRouter>
      <div className="App">
        <div className="app-scroll">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/assessments" element={<Assessment />} />
            <Route path="/candidates" element={<CandidatePage />} />
            <Route path="/results" element={<Result />} />
            <Route path="/result/:token" element={<Result />} />
            <Route path="/custom-assessment" element={<CustomAssessment />} />
            <Route path="/review-assessment" element={<ReviewPage />} />
            <Route path="/invite-candidates/:assessmentId" element={<InviteCandidates />} />
            <Route path="/team-members" element={<TeamMembers />} />
            <Route path="/manual-questions" element={<ManualQuestions />} />
            <Route path="/live-interview-list" element={<LiveInterviewList />} />
            <Route path="/send-invite" element={<InterviewInvite />} />
            {/* Question Types */}
            <Route path="/multiple-choice-question" element={<MultipleChoiceQuestion />} />
            <Route path="/multiple-selection-question" element={<MultipleSelectionQuestion />} />
            <Route path="/true-false-question" element={<TrueFalseQuestion />} />
            <Route path="/pdf-upload-question" element={<PdfUploadQuestion />} />
            {/* Recruiter Coding Views */}
            <Route path="/coding" element={<CodingHome />} />
            <Route path="/coding/questions/new" element={<CodingQuestionForm />} />
            <Route path="/coding/questions/:id/edit" element={<CodingQuestionForm />} />
            <Route path="/coding/review" element={<CodingReview />} />
            <Route path="/coding-challenge-question" element={<CodingQuestionForm />} />
            {/* Interviewer View */}
            <Route path="/live-interview-interviewer" element={<LiveInterviewInterviewer />} />

            {/* Public / Candidate Routes */}
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/take-assessment/:token" element={<TakeAssessment />} />
            <Route path="/accept-invite" element={<AcceptInvite />} />
            <Route path="/coding/questions/:id/attempt" element={<CodingAttempt />} />
            <Route path="/live-interview" element={<LiveInterview />} />
          </Routes>

          {/* Cookie Consent Banner */}
          <div
            id="cookie-banner"
            style={{
              transform: showCookieBanner ? 'translateY(0)' : 'translateY(100%)',
            }}
          >
            <div className="cookie-content">
              <p className="cookie-text">
                We use cookies to enhance your experience. By continuing to visit
                this site you agree to our use of cookies.
              </p>
              <div className="cookie-buttons">
                <button
                  onClick={() => handleCookieConsent('accepted')}
                  className="cookie-btn cookie-accept-btn"
                >
                  Accept
                </button>
                <button
                  onClick={() => handleCookieConsent('declined')}
                  className="cookie-btn cookie-decline-btn"
                >
                  Decline
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
