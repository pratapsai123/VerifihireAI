# VerifiHireAI — Deep Token & Cost Analysis
## Per Candidate: 40 MCQs + 2 Coding Challenges + 1 AI Interview

**Date:** May 2026  
**Scope:** Single candidate complete journey (Assessment Generation + AI Interview)  
**AI Provider:** Groq (Llama models)  
**Models Used:** `llama-3.1-8b-instant` (fast generation), `llama-3.3-70b-versatile` (deep reasoning / interview)

---

## 1. EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| **AI Interview Questions Asked** | **13 structured turns** |
| **Assessment Generation API Calls** | ~5–7 calls |
| **Interview API Calls** | ~14–15 calls (13 turns + 1–2 clarifications) |
| **Total Input Tokens** | **~78,000 tokens** |
| **Total Output Tokens** | **~13,000 tokens** |
| **Total Tokens (In + Out)** | **~91,000 tokens** |
| **Estimated Cost (Groq)** | **$55 – $70 USD per candidate** |

---

## 2. HOW MANY QUESTIONS DOES THE AI ASK IN THE INTERVIEW?

The AI interview engine (`ProcessAnswerView` in `ai_candidates/views.py`) runs a **fixed 13-turn structured interview** defined by `TOTAL_INTERVIEW_QUESTIONS = 13`.

### Turn-by-Turn Breakdown

| Turn | Category | What the AI Asks |
|------|----------|------------------|
| 1 | **INTRO** | Warm greeting + opening question (e.g., "Tell me about yourself") |
| 2 | **JD-Q1** | Job Description question #1 — tests fit with role requirements |
| 3 | **JD-Q2** | Job Description question #2 — deeper role-specific probe |
| 4 | **JD-Q3** | Job Description question #3 — technical or process fit |
| 5 | **JD-Q4** | Job Description question #4 — advanced or culture fit |
| 6 | **RESUME-SKILL-Q1** | Specific skill from the candidate's resume |
| 7 | **RESUME-SKILL-Q2** | Another specific skill from the resume |
| 8 | **PROJECT-Q1** | Deep-dive into a specific project mentioned on the resume |
| 9 | **PROJECT-Q2** | Second project question or deeper architecture probe |
| 10 | **SCENARIO-Q1** | Hypothetical workplace scenario based on the Job Description |
| 11 | **SCENARIO-Q2** | Second scenario question — problem-solving under pressure |
| 12 | **SYNTAX-Q1** | Live coding or syntax question (candidate types answer) |
| 13 | **SYNTAX-Q2** | Second coding/syntax challenge |
| 14+ | **EXIT** | Interview ends, goodbye message |

### Clarification Turns (Extra)
If the candidate says *"repeat that"*, *"pardon"*, *"I don't understand"*, or asks for clarification, the AI **stays on the same turn** and generates a rephrased question. This consumes **1 additional API call per clarification**. Typical interviews see **1–2 clarifications**.

---

## 3. AI ASSESSMENT TOKEN BREAKDOWN (40 MCQs + 2 Coding)

This happens **once per assessment** (if `same_questions_for_all=True`, it is reused across candidates; if unique questions, it is per-candidate).

### 3A. MCQ Pool Generation — 40 Questions

**Code Reference:** `_generate_mcq_pool_ai_only()` in `ai_assessments/ai_logic.py`

**Logic:**
- Default difficulty split for 40 MCQs: **20 Easy / 12 Medium / 8 Hard**
- Generated in **batches of 15** (scales down if API returns 413 "too large")
- Estimated batches: **4 API calls** (15 Easy + 5 Easy + 12 Medium + 8 Hard)

| Per Batch | Tokens |
|-----------|--------|
| System prompt (senior interviewer persona) | ~50 tokens |
| Job Description + Required Skills | ~300–500 tokens |
| Task instructions + JSON format example | ~400 tokens |
| Rules (descriptive options, no placeholders, uniqueness) | ~200 tokens |
| Blacklist / avoid list (grows per batch) | ~300–700 tokens |
| **Total Input per Call** | **~1,300 tokens** |
| **Total Output per Call** (15 MCQs in JSON) | **~1,200–1,500 tokens** |

**Subtotal for 4 batches:**
- Input: ~5,200 tokens
- Output: ~5,200 tokens
- Retry overhead (~10%): ~520 input + ~520 output

### 3B. Coding Challenge Generation — 2 Challenges

**Code Reference:** `_generate_execution_verified_coding_pool()` → `_generate_coding_pool_ai_only()` in `ai_assessments/ai_logic.py`

**Logic:**
- Uses **pre-verified math skeletons** from `coding_skeletons.py` — AI only writes the *story/scenario*
- **1 API call per challenge** = 2 calls total
- Test cases are generated locally via the Code Executor (0 AI tokens)

| Per Challenge | Tokens |
|---------------|--------|
| Job Description (truncated to 1000 chars) | ~250 tokens |
| Required Skills (truncated to 500 chars) | ~125 tokens |
| Skeleton metadata (pattern, logic, difficulty) | ~200 tokens |
| Format instructions + JSON schema | ~200 tokens |
| **Total Input per Call** | **~800 tokens** |
| **Total Output per Call** (title + statement + explanation + constraints) | **~500 tokens** |

**Subtotal for 2 challenges:**
- Input: ~1,600 tokens
- Output: ~1,000 tokens

### 3C. Repair / Refinement (Conditional)

**Code Reference:** `_repair_pool_shortfall()` and `_expert_assessment_refiner()` in `ai_assessments/ai_logic.py`

- **Expert Refiner is BYPASSED** when pool > 25 MCQs (40 MCQs bypasses this gate to save latency)
- **Repair** triggers only if generation falls short (~20% probability for large pools)
- Estimated repair impact: **~1,000 input + ~1,000 output tokens**

### 3D. Assessment Generation Total

| | Input | Output |
|--|-------|--------|
| MCQ Generation | ~5,700 | ~5,700 |
| Coding Generation | ~1,600 | ~1,000 |
| Repair/Refinement | ~1,000 | ~1,000 |
| **Assessment Total** | **~8,300** | **~7,700** |

**Model:** `llama-3.1-8b-instant`  
**Estimated Cost:** ~$1.50 – $2.50 USD

---

## 4. AI INTERVIEW TOKEN BREAKDOWN (13 Turns)

### 4A. Resume Pre-Processing (1 Call)

**Code Reference:** `process_resume_batch_task()` in `ai_candidates/tasks.py`

Before the interview starts, the system extracts the resume and makes **1 Groq call** to:
- Extract candidate name & email
- Calculate resume-to-JD match percentage
- Generate **7 seed interview questions** (used as context, not asked directly)

| Component | Tokens |
|-----------|--------|
| Resume text (up to 10,000 chars) | ~2,500–3,000 tokens |
| Job Description | ~500 tokens |
| Scoring rules + instructions | ~300 tokens |
| JSON format requirement | ~100 tokens |
| **Total Input** | **~3,000–3,500 tokens** |
| **Total Output** (name, email, match%, summary, 7 questions) | **~800–1,200 tokens** |

**Model:** `llama-3.3-70b-versatile`

### 4B. Live Interview Turns (13 Calls)

**Code Reference:** `ProcessAnswerView` in `ai_candidates/views.py`

Each turn sends a **massive prompt** containing the full interview state. The model returns feedback, the next question, a score, and a score reason in strict JSON.

**Prompt Composition per Turn:**

| Component | Size |
|-----------|------|
| System persona ("Indu", tone rules, banned phrases) | ~800 tokens |
| Job Description context (truncated to 1500 chars) | ~400 tokens |
| Resume context (truncated to 3000 chars) | ~750 tokens |
| Experience level & difficulty instructions | ~200 tokens |
| Category map + current turn instruction | ~150 tokens |
| Conversation history (grows each turn) | ~500–2,000 tokens |
| Scoring guide (0-10 scale, generosity rules) | ~300 tokens |
| JSON response schema | ~200 tokens |
| Current question + candidate answer | ~100–300 tokens |
| **Total Input per Turn** | **~4,000–5,000 tokens** |
| **Total Output per Turn** (feedback + next Q + score + reason) | **~250–350 tokens** |

**Subtotal for 13 turns:**
- Input: ~58,500 tokens
- Output: ~3,900 tokens

### 4C. Clarification Calls (1–2 Extra Calls)

When the candidate asks for repetition or clarification, `is_clarification=true` and the same prompt structure is sent again.

- Estimated extra calls: **1–2 per interview**
- Extra tokens: ~8,000 input + ~600 output

### 4D. Interview Total

| | Input | Output |
|--|-------|--------|
| Resume Pre-Processing | ~3,000 | ~1,000 |
| 13 Interview Turns | ~58,500 | ~3,900 |
| Clarifications (1–2) | ~8,000 | ~600 |
| **Interview Total** | **~69,500** | **~5,500** |

**Model:** `llama-3.3-70b-versatile` (primary), with fallback to `llama-3.1-8b-instant` on rate limits  
**Estimated Cost:** ~$52 – $68 USD

---

## 5. GRAND TOTAL PER CANDIDATE

### Token Summary

| Phase | Input Tokens | Output Tokens | Total Tokens |
|-------|-------------|---------------|--------------|
| **Assessment Generation** (40 MCQ + 2 Coding) | ~8,300 | ~7,700 | ~16,000 |
| **AI Interview** (Resume + 13 Turns + Clarifications) | ~69,500 | ~5,500 | ~75,000 |
| **GRAND TOTAL** | **~77,800** | **~13,200** | **~91,000** |

### Cost Summary (Groq Reference Pricing)

| Model | Input Rate | Output Rate | Input Cost | Output Cost | Subtotal |
|-------|-----------|-------------|------------|-------------|----------|
| `llama-3.1-8b-instant` (Assessment) | ~$0.10 / 1M | ~$0.10 / 1M | ~$0.83 | ~$0.77 | ~$1.60 |
| `llama-3.3-70b-versatile` (Interview) | ~$0.79 / 1M | ~$0.99 / 1M | ~$54.90 | ~$5.45 | ~$60.35 |
| **TOTAL ESTIMATED COST** | | | | | **~$55 – $70 USD** |

> **Note:** Actual cost varies based on:
> - Exact Groq pricing tier and any discounts
> - Rate-limit fallbacks to cheaper models (8b instead of 70b)
> - Retry attempts due to invalid JSON or rate limits
> - Length of resume and job description
> - Number of clarification requests from the candidate

---

## 6. KEY ARCHITECTURAL FINDINGS FROM CODEBASE

### 6A. Interview Engine (`ai_candidates/views.py`)
- `TOTAL_INTERVIEW_QUESTIONS = 13` is hardcoded
- `category_map` strictly controls the topic of each turn (JD → Resume Skills → Projects → Scenarios → Syntax)
- Each turn = **1 separate Groq API call** with full conversation history
- Scores are awarded **per turn** (0–10) and persisted in `interview_summary`
- The `ProcessAnswerView` prompt alone is **~4,000–5,000 tokens** of input

### 6B. Assessment Engine (`ai_assessments/views.py` + `ai_logic.py`)
- `GenerateAssessmentView` uses `PRIMARY_MODEL = "llama-3.1-8b-instant"`
- For 40 MCQs: `_generate_mcq_pool_ai_only()` batches by difficulty (Easy → Medium → Hard)
- For 2 Coding: `_generate_execution_verified_coding_pool()` uses **skeleton-based generation** — AI only writes the problem *story*, not the solution code
- Expert refiner is **bypassed** for pools > 25 MCQs to avoid 3-minute latency
- Self-healing repair (`_repair_pool_shortfall`) triggers only on shortfalls

### 6C. Grading
- **MCQs:** Direct string matching against the `answer` field — **0 AI tokens**
- **Coding:** Executed against auto-generated test cases via local Code Executor — **0 AI tokens**
- **Interview:** Scored live inside each `ProcessAnswerView` turn — **included in interview tokens**

---

## 7. OPTIMIZATION OPPORTUNITIES

If you want to reduce cost per candidate, consider:

1. **Reduce interview turns** from 13 → 8–10 (saves ~15,000–20,000 input tokens)
2. **Truncate conversation history** sent to the model (currently sends full history every turn)
3. **Use `llama-3.1-8b-instant`** for interview turns instead of 70b (could cut interview cost by ~80%)
4. **Pre-generate assessments** for common roles and cache them (eliminates generation cost for repeat roles)
5. **Limit resume text** to 5,000 chars instead of 10,000 (saves ~500–1,000 tokens per interview turn)

---

## 8. CONCLUSION

For **one candidate** completing the full VerifiHireAI pipeline:
- **40 MCQs + 2 Coding:** Generated once (~16K tokens, ~$1.60)
- **AI Interview:** 13 structured questions + resume analysis (~75K tokens, ~$55–$68)
- **Total:** ~91,000 tokens at an estimated **$55–$70 USD** on Groq

This document is ready for PDF conversion. Paste the entire content into Claude or any Markdown-to-PDF converter.
