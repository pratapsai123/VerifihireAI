# AI Token & Cost Analysis Report
**Target:** HR & Management
**Scope:** Complete Candidate Evaluation Pipeline (Assessment + Interview)
**Provider:** Groq
**Date:** May 2026

## 1. Executive Cost Summary (Per Candidate)
The following analysis represents the cost for a candidate to complete a 40-question MCQ assessment, 2 coding challenges, and a 13-turn structured AI interview.

| Phase | AI Model | Token Usage | Actual Cost (USD) |
| :--- | :--- | :--- | :--- |
| **AI Assessment (8B Option)** | Llama 3.1 8B | ~16,000 | $0.001 |
| **AI Assessment (70B Option)** | Llama 3.3 70B | ~16,000 | $0.011 |
| **AI Interview Session** | Llama 3.3 70B | ~75,000 | $0.045 |
| **GRAND TOTAL** | **Hybrid** | **~91,000** | **$0.046** |

**Approximate cost per 1,000 candidates: $46.00 USD**

---

## 2. Groq Pricing Reference
Based on current production rates:
*   **Llama 3.1 8B Instant**: $0.05 per 1M Input | $0.08 per 1M Output
*   **Llama 3.3 70B Versatile**: $0.59 per 1M Input | $0.79 per 1M Output

---

## 3. Phase-wise Detail

### 3.1 AI Assessment Phase (Generation)

**Option A: Using Llama 3.1 8B (Standard)**
*   **Tokens**: ~8,000 Input / ~8,000 Output.
*   **Cost**: **$0.00104** (approx. 0.1 cents)
*   **Best for**: Fast, bulk generation of standard technical roles.

**Option B: Using Llama 3.3 70B (High Precision)**
*   **Tokens**: ~8,000 Input / ~8,000 Output.
*   **Cost**: **$0.01104** (approx. 1.1 cents)
*   **Best for**: Complex, senior roles or highly specialized architecture questions.

### 3.2 AI Interview Phase
*   **Process**: A 13-turn live conversation including resume parsing, project deep-dives, and scenario testing.
*   **Tokens**: ~70,000 Input (includes context history) / ~5,000 Output.
*   **Reasoning**: We use the **70B model** to ensure the interview feels human-like, technically accurate, and can reason through complex candidate answers.
*   **Cost**: $0.04525

---

## 4. Scalability Analysis
If the volume increases, the costs remain linear. There are no "idle" costs; you only pay for what you use.

| Volume | Total Cost (Est.) |
| :--- | :--- |
| 10 Candidates | $0.46 |
| 100 Candidates | $4.60 |
| 1,000 Candidates | $46.00 |
| 10,000 Candidates | $460.00 |

---

## 5. Summary
The VerifiHireAI system provides a top-tier candidate experience using the high-reasoning **Llama 70B** model while maintaining a cost of **less than 5 cents per candidate**. 
