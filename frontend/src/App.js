// Main App entrance for VerifiHireAI
import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import StudentRegister from './pages/StudentRegister';
import StudentLogin from './pages/StudentLogin';
import StudentCreateAssessment from './pages/StudentCreateAssessment';
import StudentPracticeResults from './pages/StudentPracticeResults';
import StudentWallet from './pages/StudentWallet';
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
import AiInterviewsOverview from './pages/AiInterviewsOverview';
import AiAssessments from './pages/AiAssessments';
import CreateAssessment from './pages/CreateAssessment';
import ResumeMatcher from './pages/ResumeMatcher';
import InterviewStart from './pages/InterviewStart';
import AiTakeAssessment from './pages/AiTakeAssessment';
import AiInterviewSession from './pages/AiInterviewSession';
import AiAssessmentDetail from './pages/AiAssessmentDetail';
import StudentAiInterview from './pages/StudentAiInterview';
import StudentFeedback from './pages/StudentFeedback';
import StudentSessions from './pages/StudentSessions';
import ResultsAI from './pages/ResultsAI';
import FeedbackPage from './pages/FeedbackPage';
import FeedbackDetails from './pages/FeedbackDetails';
import Settings from './pages/Settings';
import ReportPage from './pages/ReportPage';
import BookInterview from './pages/BookInterview';
import AvailabilityManagement from './pages/AvailabilityManagement';
import ProtectedRoute from './components/ProtectedRoute';
import ThankYou from './pages/ThankYou';
import MyAccount from './pages/MyAccount';
import Contact from './pages/Contact';
import SecurePrecheck from './pages/SecurePrecheck';
import Pricing from './pages/Pricing';
import InviteRedirect from './pages/InviteRedirect';
import SessionTerminated from './pages/SessionTerminated';
import SecuritySessionGuard from './components/SecuritySessionGuard';

import FeatureAiAssessments from './pages/FeatureAiAssessments';
import FeatureLiveInterview from './pages/FeatureLiveInterview';
import FeatureCustomizedAssessment from './pages/FeatureCustomizedAssessment';
import FeatureCodingAssessment from './pages/FeatureCodingAssessment';
import './styles/App.css';

import Header from './components/Header';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from './apiConfig';
import { getToken, setToken, clearToken } from './utils/authStorage';

// Global Axios Interceptors for JWT Authentication
axios.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      // List of public API paths that should not have the Authorization header
      // This prevents 401 errors if an expired token exists in localStorage
      const publicApiPatterns = [
        /^\/api\/login\//,
        /^\/api\/verify-login-otp\//,
        /^\/api\/register\//,
        /^\/api\/send-otp\//,
        /^\/api\/verify-otp\//,
        /^\/api\/reset-password\//,
        /^\/api\/invitations\/public\//,
        /^\/api\/candidate-details\//,
        /^\/api\/ai\/public\//,
        /^\/api\/ai\/submit\//,
        /^\/api\/ai\/submission\/\d+\/integrity\//,
        /^\/api\/ai\/submission\/\d+\/progress\//,
        /^\/api\/ai\/execute\//,
        /^\/api\/ai-candidates\/[0-9a-fA-F-]{36}/,
        /^\/api\/ai-candidates\/tts\//,
        /^\/api\/ai-candidates\/process-answer\//,
        /^\/api\/users\/accept-invite\//,
        /^\/api\/users\/invite\/[0-9a-fA-F-]{36}/,
        /^\/api\/interviews\/slots\/[0-9a-fA-F-]{36}/,
        /^\/api\/token\/refresh\//
      ];

      // List of candidate-facing routes that should NEVER send a recruiter token
      const publicRoutes = [
        '/precheck/',
        '/session-terminated',
        '/invite/',
        '/interview/',
        '/take-assessment/',
        '/take-ai-assessment/',
        '/ai-interview-session/',
        '/interview-start/',
        '/result/',
        '/live-interview',
        '/book-interview/',
        '/accept-invite'
      ];

      const urlPath = config.url ? new URL(config.url, window.location.origin).pathname : '';
      const isPublicApi = publicApiPatterns.some(pattern => pattern.test(urlPath));
      const isOnPublicPage = publicRoutes.some(path =>
        window.location.pathname === path || (path.endsWith('/') && window.location.pathname.startsWith(path))
      );

      // 🛡️ SECURITY: Only attach token if NOT a public API and NOT on a public candidate page.
      // This prevents "401 Unauthorized" errors when a candidate has an old/expired recruiter token in their browser.
      if (!isPublicApi && !isOnPublicPage) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    // 🛡️ SECURITY: Only send credentials (cookies) to our backend API.
    // This prevents CORS issues with local agents (like localhost:5001) that don't support credentials.
    if (config.url && config.url.startsWith(API_BASE_URL)) {
      config.withCredentials = true;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Prevent infinite loop if the refresh token endpoint itself returns 401
    if (originalRequest.url && originalRequest.url.includes('/token/refresh/')) {
      return Promise.reject(error);
    }

    // Check if error is 401 Unauthorized securely
    if (error.response && error.response.status === 401) {
      // 🛡️ CRITICAL: If database mismatch is detected, logout IMMEDIATELY.
      // A database mismatch cannot be fixed by refreshing tokens.
      if (error.response.data && error.response.data.code === 'db_mismatch') {
        console.error('Database context mismatch detected. Forced logout.');
        clearToken();
        localStorage.removeItem('user');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      if (originalRequest._retry) {
        // If we already tried refreshing and it failed again with 401, logout.
        console.error('Unauthorized after retry. Logging out.');
        clearToken();
        localStorage.removeItem('user');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          originalRequest._retry = true;
          return axios(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Attempt to refresh the token using the HttpOnly cookie
        const refreshResponse = await axios.post(`${API_BASE_URL}/token/refresh/`, {}, {
          withCredentials: true // Important for sending the cookie
        });

        if (refreshResponse.data && refreshResponse.data.token) {
          // Cross-origin session check: Ensure the refreshed token belongs to the current app's user
          const currentUserStr = localStorage.getItem('user');
          if (currentUserStr && refreshResponse.data.user_email) {
            try {
              const currentUser = JSON.parse(currentUserStr);
              if (currentUser.email && currentUser.email.toLowerCase() !== refreshResponse.data.user_email.toLowerCase()) {
                console.error("Refreshed token belongs to a different user (cross-app login detected). Logging out.");
                clearToken();
                localStorage.removeItem('user');
                if (window.location.pathname !== '/login') {
                  window.location.href = '/login';
                }
                return Promise.reject(new Error("Cross-app session hijacking prevented."));
              }
            } catch (e) {
              // ignore parse errors
            }
          }

          const newToken = refreshResponse.data.token;
          setToken(newToken);

          processQueue(null, newToken);
          isRefreshing = false;

          // Retry original request with new token
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
        console.error("Token refresh failed", refreshError);
      }

      // Check if the current page is a public candidate-facing page
      const publicRoutes = [
        '/precheck/',
        '/session-terminated',
        '/invite/',
        '/interview/',
        '/take-assessment/',
        '/take-ai-assessment/',
        '/ai-interview-session/',
        '/interview-start/',
        '/result/',
        '/live-interview',
        '/book-interview/',
        '/accept-invite'
      ];
      const isPublicPage = publicRoutes.some(path =>
        window.location.pathname === path || (path.endsWith('/') && window.location.pathname.startsWith(path))
      );

      // ONLY logout and redirect if NOT on a public candidate page
      if (!isPublicPage) {
        console.error('Session expired or unauthorized. Logging out.');
        clearToken();
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
  const [isInitializing, setIsInitializing] = useState(true);

  // Proactive Session Recovery
  // On page refresh, the in-memory access token is lost. This effect tries to 
  // refresh it using the HttpOnly cookie before any other component starts fetching data.
  useEffect(() => {
    const initializeAuth = async () => {
      const storedUser = localStorage.getItem('user');
      if (storedUser && !getToken()) {
        try {
          // Silent refresh call
          const response = await axios.post(`${API_BASE_URL}/token/refresh/`, {}, {
            withCredentials: true
          });

          if (response.data && response.data.token) {
            // Cross-origin session check: Ensure the refreshed token belongs to the current app's user
            const currentUserStr = localStorage.getItem('user');
            if (currentUserStr && response.data.user_email) {
              try {
                const currentUser = JSON.parse(currentUserStr);
                if (currentUser.email && currentUser.email.toLowerCase() !== response.data.user_email.toLowerCase()) {
                  console.error("Refreshed token belongs to a different user (cross-app login detected). Clearing state.");
                  clearToken();
                  localStorage.removeItem('user');
                  setIsInitializing(false);
                  return;
                }
              } catch (e) {
                // ignore parse errors
              }
            }

            setToken(response.data.token);
            console.log("Session recovered successfully.");
          }
        } catch (err) {
          console.warn("Session recovery failed or expired:", err.response?.status);
          // If 401, the refresh token is invalid/expired. We should clear the stale user data.
          if (err.response && err.response.status === 401) {
            clearToken();
            localStorage.removeItem('user');
          }
        }
      }
      setIsInitializing(false);
    };

    initializeAuth();

    // Cross-tab synchronization: if another tab logs in/out, reload this tab
    // so it doesn't use stale memory tokens or mismatched state.
    const handleStorageChange = (e) => {
      if (e.key === 'user') {
        // If user was removed (logged out), or changed to a different user (logged in)
        if (!e.newValue) {
          clearToken();
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        } else if (e.oldValue !== e.newValue) {
          console.log("User session changed in another tab. Reloading...");
          window.location.reload();
        }
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Global scroll-to-top on route changes
  useEffect(() => {
    window.scrollTo(0, 0);
    const appScrollEl = document.querySelector('.app-scroll');
    if (appScrollEl) {
      appScrollEl.scrollTop = 0;
    }
  }, [location.pathname]);

  // List of routes that should have the global header hidden for a full-screen experience
  const fullScreenRoutes = [
    '/',
    '/login',
    '/signup',
    '/student/login',
    '/student/register',
    '/forgot-password',
    '/live-interview',             // candidate — no main navbar
    '/live-interview-interviewer', // interviewer — no main navbar (has its own internal header)
    '/accept-invite',
    '/feedback-page',
    '/contact',
    '/session-terminated',
    '/features/ai-assessments',
    '/features/live-interview',
    '/features/customized-assessment',
    '/features/coding-assessment',
    '/pricing',
  ];

  const isFullScreenPage =
    fullScreenRoutes.includes(location.pathname) ||
    location.pathname.startsWith('/interview-start/') ||
    location.pathname.startsWith('/precheck/') ||
    location.pathname.startsWith('/take-assessment/') ||
    location.pathname.startsWith('/take-ai-assessment/') ||
    location.pathname.startsWith('/ai-interview-session/') ||
    location.pathname.startsWith('/book-interview/') ||
    location.pathname.startsWith('/result/') ||
    location.pathname.includes('/report-view') ||
    location.pathname.endsWith('/attempt');

  // Proactive Session Validation (Heartbeat)
  // Polls the backend periodically to detect if the database context has changed.
  // If the DB context changes (e.g., backend restarted with new DB), the next poll will fail with 401,
  // triggering the global axios interceptor to log out the user immediately.
  useEffect(() => {
    const token = getToken();
    if (!token) return;

    // Skip polling on public candidate/invite pages
    const publicRoutes = [
      '/precheck/', '/session-terminated', '/invite/', '/interview/',
      '/login', '/signup', '/forgot-password', '/take-assessment/',
      '/take-ai-assessment/', '/ai-interview-session/', '/interview-start/',
      '/result/', '/live-interview', '/book-interview/', '/accept-invite'
    ];
    const isPublicPage = publicRoutes.some(path =>
      location.pathname === path || (path.endsWith('/') && location.pathname.startsWith(path))
    );
    if (isPublicPage) return;

    const intervalId = setInterval(async () => {
      try {
        // Use the lightweight heartbeat endpoint
        await axios.get(`${API_BASE_URL}/heartbeat/`);
      } catch (err) {
        // 401 errors are handled by the global interceptor (logs out user)
        // We ignore other errors (like network down) to prevent premature logout 
        // while the backend is restarting.
        if (err.response && err.response.status === 401) {
          console.warn("Heartbeat failed: Database context mismatch or session expired.");
        }
      }
    }, 15000); // Check every 15 seconds for proactive logout

    return () => clearInterval(intervalId);
  }, [location.pathname]);

  if (isInitializing) {
    return (
      <div className="initial-loading-container">
        <div className="loader-content">
          <div className="loader-logo">VerifiHire<span>AI</span></div>
          <div className="loader-spinner"></div>
          <p>Recovering session...</p>
        </div>
      </div>
    );
  }

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
          <Route path="/student/login" element={<StudentLogin />} />
          <Route path="/student/register" element={<StudentRegister />} />
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
            <Route path="/ai-interview" element={<AiInterview />} />
            <Route path="/student/ai-interview" element={<StudentAiInterview />} />
            <Route path="/student/create-assessment" element={<StudentCreateAssessment />} />
            <Route path="/student/results" element={<StudentPracticeResults />} />
            <Route path="/student/sessions" element={<StudentSessions />} />
            <Route path="/student/feedback/:token" element={<StudentFeedback />} />
            <Route path="/student/wallet" element={<StudentWallet />} />
            <Route path="/ai-interviews-overview" element={<AiInterviewsOverview />} />
            <Route path="/ai-assessments" element={<AiAssessments />} />
            <Route path="/create-assessment" element={<CreateAssessment />} />
            <Route path="/resume-matcher" element={<ResumeMatcher />} />
            <Route path="/ai-assessments/:id" element={<AiAssessmentDetail />} />
            <Route path="/results-ai" element={<ResultsAI />} />
            <Route path="/feedback-page" element={<FeedbackPage />} />
            <Route path="/feedback-details" element={<FeedbackDetails />} />
            <Route path="/results" element={<Result />} />
            <Route path="/results/:submissionId/report-view" element={<ReportPage />} />
            <Route path="/setting" element={<Settings />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/manage-availability" element={<AvailabilityManagement />} />
            <Route path="/my-account" element={<MyAccount />} />
          </Route>

          {/* Public / Candidate Routes */}
          <Route path="/invite/:token" element={<InviteRedirect type="assessment" />} />
          <Route path="/interview/:token" element={<InviteRedirect type="interview" />} />
          <Route path="/ai-assessment/:token" element={<InviteRedirect type="ai_assessment" />} />
          <Route path="/ai-interview/:token" element={<InviteRedirect type="ai_interview" />} />
          <Route path="/precheck/:token" element={<SecurePrecheck />} />
          <Route path="/session-terminated" element={<SessionTerminated />} />
          <Route path="/result/:token" element={<Result />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/take-assessment/:token" element={<SecuritySessionGuard sessionType="assessment"><TakeAssessment /></SecuritySessionGuard>} />
          <Route path="/accept-invite" element={<AcceptInvite />} />
          <Route path="/coding/questions/:id/attempt" element={<CodingAttempt />} />
          <Route path="/live-interview" element={<LiveInterview />} />
          <Route path="/interview-start/:token" element={<InterviewStart />} />
          <Route path="/take-ai-assessment/:token" element={<SecuritySessionGuard sessionType="ai_assessment"><AiTakeAssessment /></SecuritySessionGuard>} />
          <Route path="/ai-interview-session/:token" element={<SecuritySessionGuard sessionType="ai_interview"><AiInterviewSession /></SecuritySessionGuard>} />
          <Route path="/book-interview/:token" element={<BookInterview />} />
          <Route path="/thank-you" element={<ThankYou />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/pricing" element={<Pricing />} />

          {/* Features Dropdown Pages */}
          <Route path="/features/ai-assessments" element={<FeatureAiAssessments />} />
          <Route path="/features/live-interview" element={<FeatureLiveInterview />} />
          <Route path="/features/customized-assessment" element={<FeatureCustomizedAssessment />} />
          <Route path="/features/coding-assessment" element={<FeatureCodingAssessment />} />
        </Routes>


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
