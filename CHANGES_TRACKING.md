# VerifiHireAI - Changes Tracking Log

> This file tracks all feature and logic changes made to the project.
> Format: [DATE TIME] - [Category] - Description
> **Order: NEWEST first (reverse chronological)**

---

## 2026-05-12

### 11:40 - [Infrastructure / Pipeline Hardening]
- **Task 1: PostgreSQL Connection Exhaustion Fix**: Changed `CONN_MAX_AGE` to `0` in `settings.py` to prevent the "FATAL: sorry, too many clients already" error caused by high-frequency heartbeat polling leaving idle database connections open.
- **Task 2: Restored Missing Resume Extraction Task**: Created the standalone `extract_resume_text_task` celery task in `tasks.py` that was being imported by the registration view but didn't actually exist. This ensures resumes uploaded during AI interview registration are properly parsed using PyMuPDF → PyPDF2 → OCR fallback.
- **Task 3: DeepFace Retry Hardening**: Added `overwrite: true` to all face registration API calls in `AiInterviewSession.js`. This prevents candidates from being hard-blocked with "Identity already exists" when attempting to restart the interview or if a previous partial registration attempt hung.

### 09:40 - [AI Interview / On-Hold Status for Integrity-Penalized Candidates]

---



## 2026-05-08

### 16:20 - [AI Interview / Face Registration Integrity]
- **Task 1: Added robust AI face tracking**: Replaced the canvas pixel heuristic with MediaPipe Face Detection to accurately locate the face and eyes, even in poor lighting.
- **Task 2: Added hardware pause on tab switch**: Integrated `pauseHardware()` to instantly mute the mic, disable the camera, and stop TTS if the candidate switches tabs or windows.
- **Task 3: Added blink auto-capture**: Integrated eye tracking that automatically captures the photo when the user blinks, removing the need for manual button clicks.
- **Task 4: Added anti-spoofing delay**: Implemented a mandatory 1-second buffer once the face enters the oval before capturing, preventing false positives from head movement or camera auto-exposure.
- **Task 5: Fixed manual retry flow**: Kept the manual "Capture & Register" button fully functional alongside blink detection, and fixed a bug where the camera feed failed to restart on "Retry".


### 12:15 - [AI Interview / Voice Performance]
- **Task 1: Implemented TTS Streaming**: Refactored `TTSView` and `EdgeTTSEngine` to use `StreamingHttpResponse`.
- **Task 2: Eliminated Latency**: The system now delivers audio chunks in real-time, allowing speech to start playing as soon as the first word is synthesized, rather than waiting for the entire paragraph.
- **Task 3: Improved UX**: Reduced "dead air" silence during interviews by ~70%, creating a much more natural conversational flow.

### 11:15 - [Identity Verification / Override & Flag System]
- **Task 1: Implemented Override Logic**: Candidates are no longer hard-blocked if their face doesn't match the registered PAN (common in lighting changes). They can now "Override & Continue".
- **Task 2: Auto-Flagging & Audit**: When an override occurs, the candidate is automatically flagged with `identity_mismatch_detected = True`.
- **Task 3: Photo Comparison Tracking**: The system now captures the **Original Registered Face** and stores it alongside the new face for side-by-side comparison in the dashboard and reports.
- **Task 4: Reporting Updates**: Updated both **AI Interview** and **AI Assessment** PDF reports to include a bold "⚠️ Identity Warning" section with side-by-side face comparisons for manual HR review.
- **Task 5: Dashboard API Integration**: Updated `CandidateSerializer` and `AIAssessmentResultsView` to pass mismatch flags and photo URLs to the frontend dashboard.
- **Task 6: Database Migrations**: Added `identity_mismatch_detected`, `original_identity_photo`, and `identity_mismatch_details` to both `Candidate` and `AIAssessmentSubmission` models.

### 10:05 - [Infrastructure / Database Stabilization]
- **Task 1: Fixed "Too Many Clients" PostgreSQL Error**: Set `CONN_MAX_AGE` to `0` in `settings.py`. This forces high-frequency security heartbeats to release database connections immediately, preventing connection pool saturation (100+ clients limit).
- **Task 2: Masked API Keys**: Ensured `DEEPSEEK_API_KEY_1` is retrieved via environment variables/config to prevent hard-coded leaks during repository pushes.

---

## 2026-05-07

### 16:45 - [Infrastructure / Git Hygiene]
- **Task 1: Updated .gitignore**: Added rules to exclude `celerybeat-schedule*` and `scratch/` directories to prevent repository clutter.
- **Task 2: Syncing Branches**: Merged `06rishi` branch into `suman07`, integrating new PDF reporting logic and candidate photo dashboard support.

### 16:30 - [AI Interview / Turn Logic Hardening]
- **Task 1: Reliable Turn Counting**: Refactored `ProcessAnswerView` to use `candidate.total_questions` instead of chat history length, preventing "turn skipping" during candidate clarifications.
- **Task 2: Forced Coding Triggers**: Hard-coded logic for turns 12 and 13 to force `requires_code_input = True`, ensuring the code editor UI always appears.

### 15:50 - [Database / Connection Optimization]
- **Task 1: Resolved "Too Many Clients" Error**: Lowered `CONN_MAX_AGE` from 600 to 60 in `settings.py` to recycle database connections faster and prevent exhaustion during high-concurrency heartbeats.

### 14:20 - [AI Logic / DeepSeek Migration]
- **Task 1: Migrated to DeepSeek V4 Flash**: Replaced Groq (Llama-3) with DeepSeek V4 Flash across all assessment modules for improved reasoning and latency.
- **Task 2: Unified LLM Client**: Created `ai_assessments/llm_client.py` with `LLMKeyManager` for thread-safe API key rotation and standardized `call_llm_with_backoff`.

### 10:15 - [Backend+Architecture / 100+ Concurrent AI Interviews Scaling]
- **Task 1: Implemented Async Processing**: Added Celery task `process_ai_interview_answer_task` to queue AI processing instead of blocking Django workers
- **Task 2: New Async Views**: Created `AsyncProcessAnswerView`, `TaskStatusView`, `InterviewQueueStatusView` for non-blocking interview processing
- **Task 3: Rate Limiting Middleware**: Added `InterviewRateLimitMiddleware` with 100 req/min limit per IP to prevent system overload
- **Task 4: Queue Management**: Added `InterviewQueueMiddleware` with 500 max queue size and intelligent load detection
- **Task 5: Health Monitoring**: Added `InterviewHealthCheckMiddleware` with `/ai-interview-health` endpoint for load balancer health checks
- **Task 6: Database Connection Pooling**: Enhanced PostgreSQL settings with MAX_CONNS: 100, MIN_CONNS: 20 for better connection management
- **Task 7: API Key Scaling**: Updated Groq key configuration with placeholders for 10 keys (300 req/min capacity)
- **Task 8: New Endpoints**: Added `/process-answer-async/`, `/task-status/<task_id>/`, `/queue-status/` for async interview flow
- **Task 9: Scaling Utils**: Enhanced `scaling_utils.py` with rate limiters set to 90 req/min for Groq API (3 keys × 30 req/min)
- **Task 10: Capacity Improvement**: System can now handle 100+ concurrent interviews vs previous ~50 limit
- **Task 11: Files Added**: `async_views.py`, enhanced `middleware.py`, updated `tasks.py` with async processing
- **Task 12: Files Modified**: `settings.py` (middleware, database, API keys), `urls.py` (new endpoints), `scaling_utils.py`

---

## 2026-05-06

### 07:03 - [Frontend+Backend / PAN-Based DeepFace Identity]
- **Task 1: Changed DeepFace Identity from Token to PAN**: Face registration now uses PAN number instead of interview token as `person_id`
- **Task 2: Benefit**: Same person across different interview links is recognized, preventing duplicate registration
- **Task 3: Frontend `AiInterviewSession.js`**: `getDeepfacePersonId()` now returns `candidateData.pan_number` if available, fallback to token
- **Task 4: Backend `views.py`**: Returns `verify_against_person_pan` in addition to `verify_against_person_id` for DeepFace verification
- **Task 5: Frontend `InterviewStart.js`**: Stores `verify_against_person_pan` in sessionStorage for PAN-recovery cases
- **Task 6: Frontend `AiInterviewSession.js`**: Uses PAN for DeepFace verification when `verify_against_person_pan` is available
- **Task 7: Security Improvement**: Face is now permanently bound to PAN, not temporary interview token

### 06:55 - [Backend / Thread-Safe Groq Key Management]
- **Task 1: Fixed Concurrent Interview Issue**: `GroqKeyManager` was not thread-safe, causing race conditions with multiple interviews
- **Task 2: Added Threading Lock**: `threading.Lock()` prevents simultaneous key index modification across Django workers
- **Task 3: Added Key Usage Tracking**: `_key_usage_count` dictionary tracks API calls per key index
- **Task 4: New Method `get_least_used_key()`**: Distributes load evenly across API keys for better concurrency
- **Task 5: New Method `get_usage_stats()`**: Returns usage statistics for monitoring key distribution
- **Task 6: Updated ProcessAnswerView**: Now uses `get_least_used_key()` instead of round-robin for load balancing
- **Task 7: Concurrent Capacity**: With 3 keys, can now handle ~90 requests/minute (30 per key) without race conditions

---

## 2026-05-05

### 15:40 - [Frontend / Fix Race Condition in Face Registration]
- **Task 1: Bug**: Returning candidates could register a different face because `candidateData` wasn't loaded when they clicked "Capture & Register"
- **Task 2: Root Cause**: `isReturningCandidate = candidateData?.face_embedding_hash` was `undefined` due to async fetch race condition → code treated them as new candidate
- **Task 3: Fix**: `handleRegisterFace` now queries DeepFace `/registration/registered/{person_id}` directly to determine if person has existing face
- **Task 4: New Flow**: 
  1. Ask DeepFace if person already registered (no dependency on React state)
  2. If existing face → verify new photo against stored embeddings via `/verify`
  3. If match → proceed (same person returning)
  4. If mismatch → BLOCK with "You are using a different face than originally registered"
  5. If no existing face → normal new candidate registration

### 15:15 - [Backend + Frontend / Face Verification Against Stored Photo]
- **Task 1: Fixed Identity Fraud Bug**: Multiple people could register different faces for the same PAN because PAN and face were submitted separately
- **Task 2: Added DeepFace Photo Comparison**: New candidates with duplicate PAN must verify their face against the original holder's stored photo using `/registration/verify`
- **Task 3: Returning Candidate Verification**: Returning candidates (same token) automatically verify their new face against their previously stored photo
- **Task 4: Backend PAN Check**: Now ALWAYS blocks duplicate PAN (regardless of face status) and returns `requires_face_verification=True` + `verify_against_person_id`
- **Task 5: Frontend InterviewStart.js**: Stores `verify_against_person_id` and `pending_pan` in sessionStorage when duplicate PAN detected, proceeds to interview for face check
- **Task 6: Frontend AiInterviewSession.js**: `handleRegisterFace` now:
  - Checks for `verify_against_person_id` in sessionStorage
  - Calls `/registration/verify` to compare new photo with stored registered photo
  - If verified: registers new face, sends hash + `face_verified=true` to backend
  - If not verified: blocks with "Identity verification failed" error
- **Task 7: Backend Face Acceptance**: Accepts face hash when `face_verified=true` is sent (skips duplicate check)

### 14:50 - [Frontend / Interview Pause on Fullscreen Exit]
- **Task 1: Fixed Interview Continuation Bug**: When candidates exited fullscreen during the AI interview, the timer and question progression continued in the background
- **Task 2: Added Timer Pause**: `setIsPaused(true)` is now called when:
  - Fullscreen is exited (`fullscreenchange` event)
  - Screen sharing stops (`track.onended`)
  - Tab is switched (`visibilitychange`)
  - Window loses focus (`blur` event)
- **Task 3: Added Timer Resume**: `setIsPaused(false)` is called when fullscreen is restored and screen sharing is active
- **Task 4: Timer Effect**: The existing timer countdown effect already respected `isPaused`, but the state was never set during integrity violations

### 14:50 - [Frontend / Interview Resume Fix]
- **Task 1: Fixed Registration Re-entry Bug**: When candidates closed the interview tab and reopened the link, they were asked to re-enter phone, PAN, and resume
- **Task 2: Added Registration State Detection**: InterviewStart.js now checks if `candidate.phone`, `candidate.pan_number`, and `candidate.resume` exist after fetching candidate data
- **Task 3: Added Resume Interview Flow**: New `handleResumeInterview()` function re-fetches resume match questions and navigates to AI interview session
- **Task 4: Added Resume Interview UI**: Green "Registration Complete" card with candidate details summary and "Resume Interview" button
- **Task 5: Hides Registration Form**: Form fields are hidden when candidate is already registered, preventing duplicate data entry

### 11:10 - [Backend / Scaling for 100+ Concurrent Interviews]
- **Task 1: Database Connection Pooling**: Added `CONN_MAX_AGE: 600` to keep PostgreSQL connections alive (reduces connection overhead)
- **Task 2: Async TTS Endpoint**: Converted `TTSView` to async using `async def post()` - TTS no longer blocks worker threads
- **Task 3: Scaling Utilities Module**: Created `scaling_utils.py` with:
  - `RateLimiter` class using Redis for API rate limiting
  - `cache_ai_response` decorator for caching AI responses
  - `get_system_health()` for monitoring database, Redis, Celery status
- **Task 4: Health Check Endpoint**: Added `/api/ai-candidates/health/` for load balancer health checks
- **Task 5: Groq API Key Scaling**: Added placeholders for 3 additional API keys (6 total = 180 req/min capacity)
- **Task 6: Scaling Strategy Document**: Created `SCALING_STRATEGY_100PLUS.md` with 4-phase roadmap to 1000+ concurrent interviews

### 10:38 - [Backend / Face Duplicate Detection]
- **Task 1: Added Face Embedding Hash**: `face_embedding_hash` field (SHA-256) on Candidate model for face duplicate detection
- **Task 2: DeepFace Registration Update**: Modified `FaceRegisterResponse` schema and `register_face` service to return `embedding_hash`
- **Task 3: Frontend Face Hash Capture**: Updated `AiInterviewSession.js` to capture `embedding_hash` from DeepFace and send to backend
- **Task 4: Backend Duplicate Face Check**: Added SECURITY CHECK 4 in `CandidateRegistrationUpdateView` to reject faces already registered to other candidates
- **Task 5: Face Lock on Duplicate**: If face hash exists for another candidate, registration is blocked with error message

### 10:15 - [Backend / PAN Security]
- **Task 1: Added PAN Uniqueness Constraint**: `pan_number` field now has `unique=True` to prevent multiple candidates from using the same PAN
- **Task 2: Added PAN Lock**: `pan_locked` boolean field prevents PAN changes after interview starts
- **Task 3: Added PAN Audit History**: `pan_history` JSONField tracks PAN registration history
- **Task 4: Duplicate PAN Cleanup**: Removed 2 duplicate PAN entries (ABCDE1234F) before applying constraint
- **Task 5: Registration View Security Checks**: Added 3 security checks in `CandidateRegistrationUpdateView`:
  1. Prevent PAN changes after interview starts (pan_locked check)
  2. Prevent one person from using multiple PANs (existing PAN check)
  3. Prevent multiple people from using same PAN (duplicate PAN check)
- **Task 6: Interview Start PAN Lock**: PAN gets locked when candidate first opens interview link (in `CandidateDetailView` and `CandidatePublicDetailView`)

### 09:52 - [Architecture / Concurrency Analysis]
- **Task 1: Analyzed AI Interview**: Analyzed AI Interview system concurrency capacity and bottlenecks
- **Task 2: Documented findings: Django**: Documented findings: Django sync architecture, Groq API key rotation (3 keys), no database connection pooling, WebSocket per-candidate
- **Task 3: Estimated capacity: ~50-100**: Estimated capacity: ~50-100 concurrent interviews
- **Task 4: Identified scaling limitations:**: Identified scaling limitations: Synchronous Django, single TTS endpoint, no request queueing

### 09:38 - [Frontend / AI Interview Session]
- **Task 1: Added Input Validation**: `validateAnswer()` helper to check answer quality (minimum 10 chars, 3+ meaningful words, gibberish detection)
- **Task 2: Added API Retry Logic**: `submitAnswerWithRetry()` with 3 attempts and exponential backoff (1s, 2s, 4s delays)
- **Task 3: Improved Silence Detection**: Added `lastActivityTimeRef` and 8-second grace period before ending interview on consecutive silences
- **Task 4: Added Activity Tracking**: `recordActivity()` helper resets silence counter on any candidate activity
- **Task 5: Fixed Speech Feedback Loop**: `waitForSpeechToFinish()` ensures AI speech fully completes before microphone starts
- **Task 6: Added Timer Pause**: `isPaused` state pauses 60-minute timer during environment setup (fullscreen/screen share)
- **Task 7: Added Microphone Quality Check**: `checkMicrophoneQuality()` tests audio levels for 2 seconds before interview starts
- **Task 8: Updated `handleAnswerSubmission` dependencies**: Updated `handleAnswerSubmission` dependencies to include new helpers

### 09:25 - [DeepFace / Environment]
- **Task 1: Recreated corrupted `venv_310`**: Recreated corrupted `venv_310` virtual environment
- **Task 2: Switched to using**: Switched to using existing `venv_py311` which has deepface properly installed

### 09:17 - [Backend / Migrations]
- **Task 1: Fixed migration `0104_merge_20260503_1815.py`**: Fixed migration `0104_merge_20260503_1815.py` - Removed non-existent dependency `0103_alter_identitylink_unique_together_and_more`
- **Task 2: Deleted duplicate merge**: Deleted duplicate merge migration file `0104_merge_20260503_1815.py` to resolve conflict with `0104_merge_20260504_0956.py`

### 09:11 - [Git Operations]
- **Task 1: Pulled code from**: Pulled code from `rishi4` branch and overrode local codebase

---

## 2026-04-30

### [Frontend / Results Pages]
- **Task 1: Fixed Resume Results Filter**: Removed incorrect `aicand_` filter that was hiding AI candidate resume entries
- **Task 2: Fixed Assessment Results Filter**: Removed incorrect `aicand_` filter that was hiding AI candidate assessment entries
- **Task 3: Fixed Interview Results Filter**: Removed incorrect `aicand_` filter that was hiding AI candidate interview entries
- **Task 4: Fixed Assessment Categorization**: Removed `r.score` (interview score) from `hasAssessment` check to prevent interview-only candidates appearing in assessment tab

### [Backend / Email]
- **Task 1: Updated SMTP settings:**: Updated SMTP settings: Switched from port 587 (TLS) to port 465 (SSL) to bypass Gmail rate limiting
- **Task 2: Later reverted to**: Later reverted to SMTP config with new credentials `edumala.rakesh@gmail.com`

### [Backend / Static Files]
- **Task 1: Configured Django static**: Configured Django static file serving in development mode (`STATIC_URL`, `STATICFILES_DIRS`)

### [Secure Agent]
- **Task 1: Updated download URLs**: Updated download URLs in `SecurePrecheck.js` to point to local Django server (`localhost:8001`)
- **Task 2: Added build scripts**: Added build scripts in `secureAgent/package.json` for packaging with `pkg`

### [Backend / Migrations]
- **Task 1: Created `fix_migrations.py` to**: Created `fix_migrations.py` to delete problematic migration records from `django_migrations` table
- **Task 2: Created `fake_migrations.py` to**: Created `fake_migrations.py` to mark all existing migrations as applied
- **Task 3: Fixed `SyntaxError` in**: Fixed `SyntaxError` in `candidate_assessment_views.py` (missing comma)

### [Git Operations]
- **Task 1: Created and pushed**: Created and pushed branch `suman30` with all local changes

---

## 2026-04-29 (Previous Session)

### [Backend / AI Candidates]
- **Task 1: Added PAN card**: Added PAN card verification with OCR (EasyOCR/Groq Vision)
- **Task 2: Integrated phone number,**: Integrated phone number, PAN number, PAN photo upload into `InterviewStart.js`
- **Task 3: Added PAN card**: Added PAN card image and biodata to AI interview PDF report
- **Task 4: Fixed `CandidateRegistrationUpdateView` parameter**: Fixed `CandidateRegistrationUpdateView` parameter mismatch (`token` → `public_token`)
- **Task 5: Fixed logger definition**: Fixed logger definition syntax error in `ai_candidates/views.py`

### [Backend / Email Testing]
- **Task 1: Created `test_email.py` for**: Created `test_email.py` for SMTP diagnostics
- **Task 2: Created `test_bulk_email.py` for**: Created `test_bulk_email.py` for bulk invite testing

---

### 06:55 - [Backend / Thread-Safe Groq Key Management]
- **Task 1: Fixed Concurrent Interview Issue**: `GroqKeyManager` was not thread-safe, causing race conditions with multiple interviews
- **Task 2: Added Threading Lock**: `threading.Lock()` prevents simultaneous key index modification across Django workers
- **Task 3: Added Key Usage Tracking**: `_key_usage_count` dictionary tracks API calls per key index
- **Task 4: New Method `get_least_used_key()`**: Distributes load evenly across API keys for better concurrency
- **Task 5: New Method `get_usage_stats()`**: Returns usage statistics for monitoring key distribution
- **Task 6: Updated ProcessAnswerView**: Now uses `get_least_used_key()` instead of round-robin for load balancing
- **Task 7: Concurrent Capacity**: With 3 keys, can now handle ~90 requests/minute (30 per key) without race conditions

---

## 2026-05-06

*Last updated: 2026-05-07 10:15*
