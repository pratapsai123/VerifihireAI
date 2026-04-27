// Centralized route constants for the application
// This ensures route paths are defined in one place and prevents hardcoded strings

export const ROUTES = {
  // Public / Candidate Routes
  INTERVIEW_START: '/interview-start/:token',
  AI_INTERVIEW_SESSION: '/ai-interview-session/:token',
  TAKE_AI_ASSESSMENT: '/take-ai-assessment/:token',
  TAKE_ASSESSMENT: '/take-assessment/:token',
  RESULT: '/result/:token',
  
  // Protected Routes
  DASHBOARD: '/dashboard',
  AI_INTERVIEW: '/ai-interview',
  AI_ASSESSMENTS: '/ai-assessments',
  RESULTS_AI: '/results-ai',
  CREATE_ASSESSMENT: '/create-assessment',
  RESUME_MATCHER: '/resume-matcher',
};

// Helper to generate path with params
export const generatePath = (route, params = {}) => {
  let path = route;
  Object.keys(params).forEach(key => {
    path = path.replace(`:${key}`, params[key]);
  });
  return path;
};
