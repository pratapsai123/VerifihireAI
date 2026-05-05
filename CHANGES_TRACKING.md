# VerifiHireAI - Changes Tracking Log

> This file tracks all feature and logic changes made to the project.
> Format: [DATE TIME] - [Category] - Description
> **Order: NEWEST first (reverse chronological)**

---

## 2026-05-05

### 15:40 - [Frontend / Fix Race Condition in Face Registration]
- **Bug**: Returning candidates could register a different face because `candidateData` wasn't loaded when they clicked "Capture & Register"
- **Root Cause**: `isReturningCandidate = candidateData?.face_embedding_hash` was `undefined` due to async fetch race condition → code treated them as new candidate
- **Fix**: `handleRegisterFace` now queries DeepFace `/registration/registered/{person_id}` directly to determine if person has existing face
- **New Flow**:
  1. Ask DeepFace if person already registered (no dependency on React state)
  2. If existing face → verify new photo against stored embeddings via `/verify`
  3. If match → proceed (same person returning)
  4. If mismatch → BLOCK with "You are using a different face than originally registered"
  5. If no existing face → normal new candidate registration

### 15:15 - [Backend + Frontend / Face Verification Against Stored Photo]
- **Fixed Identity Fraud Bug**: Multiple people could register different faces for the same PAN because PAN and face were submitted separately
- **Added DeepFace Photo Comparison**: New candidates with duplicate PAN must verify their face against the original holder's stored photo using `/registration/verify`
- **Returning Candidate Verification**: Returning candidates (same token) automatically verify their new face against their previously stored photo
- **Backend PAN Check**: Now ALWAYS blocks duplicate PAN (regardless of face status) and returns `requires_face_verification=True` + `verify_against_person_id`
- **Frontend InterviewStart.js**: Stores `verify_against_person_id` and `pending_pan` in sessionStorage when duplicate PAN detected, proceeds to interview for face check
- **Frontend AiInterviewSession.js**: `handleRegisterFace` now:
  - Checks for `verify_against_person_id` in sessionStorage
  - Calls `/registration/verify` to compare new photo with stored registered photo
  - If verified: registers new face, sends hash + `face_verified=true` to backend
  - If not verified: blocks with "Identity verification failed" error
- **Backend Face Acceptance**: Accepts face hash when `face_verified=true` is sent (skips duplicate check)

### 14:50 - [Frontend / Interview Pause on Fullscreen Exit]
- **Fixed Interview Continuation Bug**: When candidates exited fullscreen during the AI interview, the timer and question progression continued in the background
- **Added Timer Pause**: `setIsPaused(true)` is now called when:
  - Fullscreen is exited (`fullscreenchange` event)
  - Screen sharing stops (`track.onended`)
  - Tab is switched (`visibilitychange`)
  - Window loses focus (`blur` event)
- **Added Timer Resume**: `setIsPaused(false)` is called when fullscreen is restored and screen sharing is active
- **Timer Effect**: The existing timer countdown effect already respected `isPaused`, but the state was never set during integrity violations

### 14:50 - [Frontend / Interview Resume Fix]
- **Fixed Registration Re-entry Bug**: When candidates closed the interview tab and reopened the link, they were asked to re-enter phone, PAN, and resume
- **Added Registration State Detection**: InterviewStart.js now checks if `candidate.phone`, `candidate.pan_number`, and `candidate.resume` exist after fetching candidate data
- **Added Resume Interview Flow**: New `handleResumeInterview()` function re-fetches resume match questions and navigates to AI interview session
- **Added Resume Interview UI**: Green "Registration Complete" card with candidate details summary and "Resume Interview" button
- **Hides Registration Form**: Form fields are hidden when candidate is already registered, preventing duplicate data entry

### 11:10 - [Backend / Scaling for 100+ Concurrent Interviews]
- **Database Connection Pooling**: Added `CONN_MAX_AGE: 600` to keep PostgreSQL connections alive (reduces connection overhead)
- **Async TTS Endpoint**: Converted `TTSView` to async using `async def post()` - TTS no longer blocks worker threads
- **Scaling Utilities Module**: Created `scaling_utils.py` with:
  - `RateLimiter` class using Redis for API rate limiting
  - `cache_ai_response` decorator for caching AI responses
  - `get_system_health()` for monitoring database, Redis, Celery status
- **Health Check Endpoint**: Added `/api/ai-candidates/health/` for load balancer health checks
- **Groq API Key Scaling**: Added placeholders for 3 additional API keys (6 total = 180 req/min capacity)
- **Scaling Strategy Document**: Created `SCALING_STRATEGY_100PLUS.md` with 4-phase roadmap to 1000+ concurrent interviews

### 10:38 - [Backend / Face Duplicate Detection]
- **Added Face Embedding Hash**: `face_embedding_hash` field (SHA-256) on Candidate model for face duplicate detection
- **DeepFace Registration Update**: Modified `FaceRegisterResponse` schema and `register_face` service to return `embedding_hash`
- **Frontend Face Hash Capture**: Updated `AiInterviewSession.js` to capture `embedding_hash` from DeepFace and send to backend
- **Backend Duplicate Face Check**: Added SECURITY CHECK 4 in `CandidateRegistrationUpdateView` to reject faces already registered to other candidates
- **Face Lock on Duplicate**: If face hash exists for another candidate, registration is blocked with error message

### 10:15 - [Backend / PAN Security]
- **Added PAN Uniqueness Constraint**: `pan_number` field now has `unique=True` to prevent multiple candidates from using the same PAN
- **Added PAN Lock**: `pan_locked` boolean field prevents PAN changes after interview starts
- **Added PAN Audit History**: `pan_history` JSONField tracks PAN registration history
- **Duplicate PAN Cleanup**: Removed 2 duplicate PAN entries (ABCDE1234F) before applying constraint
- **Registration View Security Checks**: Added 3 security checks in `CandidateRegistrationUpdateView`:
  1. Prevent PAN changes after interview starts (pan_locked check)
  2. Prevent one person from using multiple PANs (existing PAN check)
  3. Prevent multiple people from using same PAN (duplicate PAN check)
- **Interview Start PAN Lock**: PAN gets locked when candidate first opens interview link (in `CandidateDetailView` and `CandidatePublicDetailView`)

### 09:52 - [Architecture / Concurrency Analysis]
- Analyzed AI Interview system concurrency capacity and bottlenecks
- Documented findings: Django sync architecture, Groq API key rotation (3 keys), no database connection pooling, WebSocket per-candidate
- Estimated capacity: ~50-100 concurrent interviews
- Identified scaling limitations: Synchronous Django, single TTS endpoint, no request queueing

### 09:38 - [Frontend / AI Interview Session]
- **Added Input Validation**: `validateAnswer()` helper to check answer quality (minimum 10 chars, 3+ meaningful words, gibberish detection)
- **Added API Retry Logic**: `submitAnswerWithRetry()` with 3 attempts and exponential backoff (1s, 2s, 4s delays)
- **Improved Silence Detection**: Added `lastActivityTimeRef` and 8-second grace period before ending interview on consecutive silences
- **Added Activity Tracking**: `recordActivity()` helper resets silence counter on any candidate activity
- **Fixed Speech Feedback Loop**: `waitForSpeechToFinish()` ensures AI speech fully completes before microphone starts
- **Added Timer Pause**: `isPaused` state pauses 60-minute timer during environment setup (fullscreen/screen share)
- **Added Microphone Quality Check**: `checkMicrophoneQuality()` tests audio levels for 2 seconds before interview starts
- Updated `handleAnswerSubmission` dependencies to include new helpers

### 09:25 - [DeepFace / Environment]
- Recreated corrupted `venv_310` virtual environment
- Switched to using existing `venv_py311` which has deepface properly installed

### 09:17 - [Backend / Migrations]
- Fixed migration `0104_merge_20260503_1815.py` - Removed non-existent dependency `0103_alter_identitylink_unique_together_and_more`
- Deleted duplicate merge migration file `0104_merge_20260503_1815.py` to resolve conflict with `0104_merge_20260504_0956.py`

### 09:11 - [Git Operations]
- Pulled code from `rishi4` branch and overrode local codebase

---

## 2026-04-30

### [Frontend / Results Pages]
- **Fixed Resume Results Filter**: Removed incorrect `aicand_` filter that was hiding AI candidate resume entries
- **Fixed Assessment Results Filter**: Removed incorrect `aicand_` filter that was hiding AI candidate assessment entries
- **Fixed Interview Results Filter**: Removed incorrect `aicand_` filter that was hiding AI candidate interview entries
- **Fixed Assessment Categorization**: Removed `r.score` (interview score) from `hasAssessment` check to prevent interview-only candidates appearing in assessment tab

### [Backend / Email]
- Updated SMTP settings: Switched from port 587 (TLS) to port 465 (SSL) to bypass Gmail rate limiting
- Later reverted to SMTP config with new credentials `edumala.rakesh@gmail.com`

### [Backend / Static Files]
- Configured Django static file serving in development mode (`STATIC_URL`, `STATICFILES_DIRS`)

### [Secure Agent]
- Updated download URLs in `SecurePrecheck.js` to point to local Django server (`localhost:8001`)
- Added build scripts in `secureAgent/package.json` for packaging with `pkg`

### [Backend / Migrations]
- Created `fix_migrations.py` to delete problematic migration records from `django_migrations` table
- Created `fake_migrations.py` to mark all existing migrations as applied
- Fixed `SyntaxError` in `candidate_assessment_views.py` (missing comma)

### [Git Operations]
- Created and pushed branch `suman30` with all local changes

---

## 2026-04-29 (Previous Session)

### [Backend / AI Candidates]
- Added PAN card verification with OCR (EasyOCR/Groq Vision)
- Integrated phone number, PAN number, PAN photo upload into `InterviewStart.js`
- Added PAN card image and biodata to AI interview PDF report
- Fixed `CandidateRegistrationUpdateView` parameter mismatch (`token` → `public_token`)
- Fixed logger definition syntax error in `ai_candidates/views.py`

### [Backend / Email Testing]
- Created `test_email.py` for SMTP diagnostics
- Created `test_bulk_email.py` for bulk invite testing

---

*Last updated: 2026-05-05 09:59*
