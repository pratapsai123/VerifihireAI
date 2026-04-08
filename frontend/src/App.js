// Main App entrance for VerifiHireAI
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
import ViewAssessment from './pages/ViewAssessment';
import InviteCandidates from './pages/InviteCandidates';
import TakeAssessment from './pages/TakeAssessment';
import Result from './pages/Result';
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
import AiInterview from './pages/AiInterview';
import AiAssessments from './pages/AiAssessments';
import CreateAssessment from './pages/CreateAssessment';
import ResumeMatcher from './pages/ResumeMatcher';
import InterviewStart from './pages/InterviewStart';
import AiTakeAssessment from './pages/AiTakeAssessment';
import AiInterviewSession from './pages/AiInterviewSession';
import AiAssessmentDetail from './pages/AiAssessmentDetail';
import ResultsAI from './pages/ResultsAI';
import FeedbackPage from './pages/FeedbackPage';
import FeedbackDetails from './pages/FeedbackDetails';
import Settings from './pages/Settings';
import BookInterview from './pages/BookInterview';
import AvailabilityManagement from './pages/AvailabilityManagement';
import ProtectedRoute from './components/ProtectedRoute';
import ThankYou from './pages/ThankYou';
import MyAccount from './pages/MyAccount';
import './styles/App.css';

import Header from './components/Header';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

// Global Axios Interceptors for JWT Authentication
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // List of public API paths that should not have the Authorization header
      // This prevents 401 errors if an expired token exists in localStorage
      const publicApiPatterns = [
        /^\/api\/invitations\/public\//,
        /^\/api\/candidate-details\//,
        /^\/api\/ai\/public\//,
        /^\/api\/ai\/submit\//,
        /^\/api\/ai\/submission\/\d+\/integrity\//,
        /^\/api\/ai\/submission\/\d+\/progress\//,
        /^\/api\/ai\/execute\//,
        /^\/api\/ai-candidates\/[0-9a-fA-F-]{36}/, // Matches UUID token paths
        /^\/api\/ai-candidates\/tts\//,
        /^\/api\/ai-candidates\/process-answer\//,
        /^\/api\/users\/accept-invite\//,
        /^\/api\/users\/invite\/[0-9a-fA-F-]{36}/, // Matches UUID token paths for getting invite
        /^\/api\/interviews\/slots\/[0-9a-fA-F-]{36}/ // Matches UUID token paths
      ];

      const urlPath = config.url ? new URL(config.url, window.location.origin).pathname : '';
      const isPublicApi = publicApiPatterns.some(pattern => pattern.test(urlPath));

      if (!isPublicApi) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // Check if error is 401 Unauthorized securely
    if (error.response && error.response.status === 401) {
      // Check if the current page is a public candidate-facing page
      const publicRoutes = [
        '/take-assessment/',
        '/take-ai-assessment/',
        '/ai-interview-session/',
        '/interview-start/',
        '/result/',
        '/live-interview',
        '/ai-interview',
        '/book-interview/',
        '/accept-invite'
      ];
      const isPublicPage = publicRoutes.some(path => window.location.pathname.startsWith(path));

      // ONLY logout and redirect if NOT on a public candidate page
      if (!isPublicPage) {
        console.error('Session expired or unauthorized. Logging out.');
        localStorage.removeItem('authToken');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');

        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      } else {
        console.warn('Unauthorized access on public page - avoiding redirect to login.');
      }
    }
    return Promise.reject(error);
  }
);

function AppContent() {
  const location = useLocation();
  const [showCookieBanner, setShowCookieBanner] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      setShowCookieBanner(true);
    }
  }, []);

  const handleAcceptCookies = () => {
    localStorage.setItem('cookieConsent', 'true');
    setShowCookieBanner(false);
  };

  // List of routes that should have the global header hidden for a full-screen experience
  const fullScreenRoutes = [
    '/',
    '/login',
    '/signup',
    '/forgot-password',
    '/live-interview',             // candidate — no main navbar
    '/live-interview-interviewer', // interviewer — no main navbar (has its own internal header)
    '/accept-invite',
    '/feedback-page',
  ];

  const isFullScreenPage =
    fullScreenRoutes.includes(location.pathname) ||
    location.pathname.startsWith('/interview-start/') ||
    location.pathname.startsWith('/take-assessment/') ||
    location.pathname.startsWith('/take-ai-assessment/') ||
    location.pathname.startsWith('/ai-interview-session/') ||
    location.pathname.startsWith('/book-interview/') ||
    location.pathname.startsWith('/result/') ||
    location.pathname.endsWith('/attempt');

  return (
    <div className="app-container">
      {!isFullScreenPage && <Header />}
      <div className="app-scroll" style={isFullScreenPage ? {
        top: 0,
        height: '100vh',
        overflowY: (location.pathname.startsWith('/ai-interview-session/') || location.pathname.startsWith('/live-interview')) ? 'hidden' : 'auto',
        overflowX: 'hidden'
      } : {}}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/assessments" element={<Assessment />} />
            <Route path="/view-assessment/:id" element={<ViewAssessment />} />
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
            <Route path="/ai-assessments" element={<AiAssessments />} />
            <Route path="/create-assessment" element={<CreateAssessment />} />
            <Route path="/resume-matcher" element={<ResumeMatcher />} />
            <Route path="/ai-assessments/:id" element={<AiAssessmentDetail />} />
            <Route path="/results-ai" element={<ResultsAI />} />
            <Route path="/feedback-page" element={<FeedbackPage />} />
            <Route path="/feedback-details" element={<FeedbackDetails />} />
            <Route path="/results" element={<Result />} />
            <Route path="/setting" element={<Settings />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/manage-availability" element={<AvailabilityManagement />} />
            <Route path="/my-account" element={<MyAccount />} />
          </Route>

          {/* Public / Candidate Routes */}
          <Route path="/result/:token" element={<Result />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/take-assessment/:token" element={<TakeAssessment />} />
          <Route path="/accept-invite" element={<AcceptInvite />} />
          <Route path="/coding/questions/:id/attempt" element={<CodingAttempt />} />
          <Route path="/live-interview" element={<LiveInterview />} />
          <Route path="/ai-interview" element={<AiInterview />} />
          <Route path="/interview-start/:token" element={<InterviewStart />} />
          <Route path="/take-ai-assessment/:token" element={<AiTakeAssessment />} />
          <Route path="/ai-interview-session/:token" element={<AiInterviewSession />} />
          <Route path="/book-interview/:token" element={<BookInterview />} />
          <Route path="/thank-you" element={<ThankYou />} />
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
                onClick={() => handleAcceptCookies()}
                className="cookie-btn cookie-accept-btn"
              >
                Accept
              </button>
              <button
                onClick={() => setShowCookieBanner(false)}
                className="cookie-btn cookie-decline-btn"
              >
                Decline
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;