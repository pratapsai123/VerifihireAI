import React, { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import CandidateDetails from './CandidateDetails';
import '../styles/CodingAttempt.css';
import '../styles/TakeAssessment.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

const DEFAULT_LANGS = [
  'cpp',
  'java',
  'python3',
  'python',
  'javascript',
  'typescript',
  'csharp',
  'c',
  'go',
  'kotlin',
  'swift',
  'rust',
  'ruby',
  'php',
  'dart',
  'scala',
];

const MonacoEditor = React.lazy(() => import('@monaco-editor/react'));

function monacoLanguage(lang) {
  switch ((lang || '').toLowerCase()) {
    case 'python':
      return 'python';
    case 'python3':
      return 'python';
    case 'javascript':
      return 'javascript';
    case 'typescript':
      return 'typescript';
    case 'java':
      return 'java';
    case 'c':
      return 'c';
    case 'cpp':
      return 'cpp';
    case 'csharp':
      return 'csharp';
    case 'go':
      return 'go';
    case 'kotlin':
      return 'kotlin';
    case 'swift':
      return 'swift';
    case 'rust':
      return 'rust';
    case 'ruby':
      return 'ruby';
    case 'php':
      return 'php';
    case 'dart':
      return 'dart';
    case 'scala':
      return 'scala';
    case 'sql':
      return 'sql';
    default:
      return 'plaintext';
  }
}

function normalizeRunResult(data) {
  if (!data) return data;

  // Handle array response (list of results)
  if (Array.isArray(data)) {
    const passedCheck = data.filter((r) => String(r.status || '').toLowerCase() === 'passed');
    return {
      results: data,
      passed_count: passedCheck.length,
      total_tests: data.length,
      status: passedCheck.length === data.length ? 'passed' : 'failed',
      execution_time_ms: 0,
    };
  }

  if (typeof data !== 'object') return data;
  if (Array.isArray(data.results)) return data;

  const exitCode = Number.isFinite(data.exit_code) ? Number(data.exit_code) : null;
  const hasError = Boolean((data.stderr || '').trim());
  const ok = !hasError && (data.ok === true || exitCode === 0);
  const statusLabel = ok ? 'passed' : 'failed';
  const resultRow = {
    status: statusLabel,
    stdout: data.stdout || '',
    stderr: data.stderr || '',
    is_hidden: false,
  };
  return {
    status: statusLabel,
    passed_count: ok ? 1 : 0,
    total_tests: 1,
    execution_time_ms: data.time_limit_ms ?? 0,
    submission_id: data.submission_id,
    results: [resultRow],
  };
}

// Default main method templates for each language
function getDefaultTemplate(lang) {
  const templates = {
    'cpp': `#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    // Your code here
    return 0;
}`,
    'java': `public class Main {
    public static void main(String[] args) {
        // Your code here
    }
}`,
    'python3': `def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()`,
    'python': `def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()`,
    'javascript': `function main() {
    // Your code here
}

main();`,
    'typescript': `function main(): void {
    // Your code here
}

main();`,
    'csharp': `using System;

class Program {
    static void Main(string[] args) {
        // Your code here
    }
}`,
    'c': `#include <stdio.h>

int main() {
    // Your code here
    return 0;
}`,
    'go': `package main

import "fmt"

func main() {
    // Your code here
}`,
    'kotlin': `fun main() {
    // Your code here
}`,
    'swift': `import Foundation

// Your code here`,
    'rust': `fn main() {
    // Your code here
}`,
    'ruby': `def main
    # Your code here
end

main`,
    'php': `<?php
// Your code here
?>`,
    'dart': `void main() {
    // Your code here
}`,
    'scala': `object Main {
    def main(args: Array[String]): Unit = {
        // Your code here
    }
}`,
  };
  return templates[lang] || '// Your code here';
}

// Extract template for a specific language from multi-language starter code
function extractLanguageTemplate(starterCode, lang) {
  if (!starterCode || !starterCode.trim()) {
    return getDefaultTemplate(lang);
  }

  // Check if starter code contains multiple language templates (has "// ===" markers)
  if (starterCode.includes('// ===')) {
    // Try to find the specific language's template
    const langLabels = {
      'cpp': 'C\\+\\+',
      'java': 'Java',
      'python3': 'Python3',
      'python': 'Python',
      'javascript': 'JavaScript',
      'typescript': 'TypeScript',
      'csharp': 'C#',
      'c': 'C',
      'go': 'Go',
      'kotlin': 'Kotlin',
      'swift': 'Swift',
      'rust': 'Rust',
      'ruby': 'Ruby',
      'php': 'PHP',
      'dart': 'Dart',
      'scala': 'Scala',
      'sql': 'SQL', // Added SQL support here too
    };

    const langLabel = langLabels[lang] || lang;
    // Match: // === Language === followed by content until next // === or end
    const regex = new RegExp(`//\\s*===\\s*${langLabel}\\s*===\\s*\\n([\\s\\S]*?)(?=\\n\\n\\s*//\\s*===|$)`, 'i');
    const match = starterCode.match(regex);

    if (match && match[1]) {
      return match[1].trim();
    }

    // If not found in multi-language format, return default template
    return getDefaultTemplate(lang);
  }

  // If starter code doesn't have language markers, return it as-is (might be single language)
  return starterCode;
}

function formatDuration(ms) {
  const totalSeconds = Math.max(0, Math.floor((ms || 0) / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

export default function TakeAssessment() {
  const navigate = useNavigate();
  const { token } = useParams();
  const [candidateDetailsCompleted, setCandidateDetailsCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [assessment, setAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [codingQuestions, setCodingQuestions] = useState([]);
  const [answersById, setAnswersById] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [remainingSeconds, setRemainingSeconds] = useState(null);
  const [codingState, setCodingState] = useState({
    currentId: null,
    codeById: {},
    languageById: {},
    runResultById: {},
    runError: '',
    running: false,
    submittedIds: {},
  });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [fsError, setFsError] = useState('');
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(false);
  const [leftWidth, setLeftWidth] = useState(44);
  const [lastExpandedWidth, setLastExpandedWidth] = useState(44);
  const [isDragging, setIsDragging] = useState(false);
  const [showResultPanel, setShowResultPanel] = useState(true);
  const [resultHeightPct, setResultHeightPct] = useState(30);
  const [isResultDragging, setIsResultDragging] = useState(false);

  // New State for Exam Mode
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(0);
  const [markedReviewIds, setMarkedReviewIds] = useState({});
  // Track visited questions to mark them as "Not Answered" (Red) vs "Not Visited" (Gray)
  const [visitedIds, setVisitedIds] = useState({});

  useEffect(() => {
    // Mark current question as visited whenever index changes
    if (questions.length > 0) {
      const currentQ = questions[activeQuestionIndex];
      if (currentQ) {
        setVisitedIds((prev) => ({ ...prev, [String(currentQ.id)]: true }));
      }
    }
  }, [activeQuestionIndex, questions]);

  const handleNext = () => {
    if (activeQuestionIndex < questions.length - 1) {
      setActiveQuestionIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (activeQuestionIndex > 0) {
      setActiveQuestionIndex((prev) => prev - 1);
    }
  };

  const handleQuestionPaletteClick = (index) => {
    setActiveQuestionIndex(index);
  };

  const handleClearResponse = (qid) => {
    setAnswersById((prev) => {
      const copy = { ...prev };
      delete copy[String(qid)];
      return copy;
    });
  };

  const handleMarkForReview = (qid) => {
    const id = String(qid);
    setMarkedReviewIds((prev) => {
      const next = { ...prev };
      if (next[id]) delete next[id];
      else next[id] = true;
      return next;
    });
  };

  const getQuestionStatus = (q, index) => {
    const id = String(q.id);

    const answered = isAnswered(q);
    const marked = markedReviewIds[id];
    const visited = visitedIds[id];

    // Status Priority Logic:
    // 1. Current (highlighted separately in UI, but color-wise?)
    // 2. Marked (Blue/Purple) - Overrides answered/unanswered validity in terms of "Action needed"
    // 3. Answered (Green)
    // 4. Not Answered (Red) - IF visited
    // 5. Not Visited (Gray)

    if (marked) return 'marked';
    if (answered) return 'answered';
    if (visited) return 'not_answered';
    return 'not_visited';
  };

  const currentQuestion = questions[activeQuestionIndex];

  const getSelected = (qid) => answersById[String(qid)];

  const setSelected = (qid, value) => {
    setAnswersById((prev) => ({ ...prev, [String(qid)]: value }));
  };

  const isAnswered = (q) => {
    const qid = String(q.id);
    const v = answersById[qid];
    if (q.question_type === 'MSQ') return Array.isArray(v) && v.length > 0;
    return typeof v === 'string' && v.trim() !== '';
  };

  const buildOptions = (q) => {
    // If backend sends shuffled options, use them
    if (Array.isArray(q.options) && q.options.length > 0) {
      return q.options;
    }
    // Default A-D options if present
    const opts = [];
    if (q.option_a) opts.push({ key: 'A', text: q.option_a });
    if (q.option_b) opts.push({ key: 'B', text: q.option_b });
    if (q.option_c) opts.push({ key: 'C', text: q.option_c });
    if (q.option_d) opts.push({ key: 'D', text: q.option_d });

    // If TF but options missing, provide True/False
    if ((q.question_type || '').toUpperCase() === 'TF' && opts.length === 0) {
      return [
        { key: 'A', text: 'True' },
        { key: 'B', text: 'False' },
      ];
    }
    return opts;
  };

  const firstUnansweredId = useMemo(() => {
    for (const q of questions) {
      // If the question has no options/inputs, checking if it's answered is impossible and blocks submission
      const opts = buildOptions(q);
      if (opts.length === 0) continue;

      if (!isAnswered(q)) return String(q.id);
    }
    return null;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questions, answersById]);


  const codingQuestionsOrdered = useMemo(() => {
    const list = [...codingQuestions];
    list.sort((a, b) => (a.order || 0) - (b.order || 0));
    return list;
  }, [codingQuestions]);

  const activeCoding = useMemo(() => {
    if (!codingQuestionsOrdered.length) return null;
    if (codingState.currentId == null) return codingQuestionsOrdered[0];
    return codingQuestionsOrdered.find((q) => String(q.id) === String(codingState.currentId)) || codingQuestionsOrdered[0];
  }, [codingQuestionsOrdered, codingState.currentId]);

  const formatHHMMSS = (secs) => {
    const s = Math.max(0, Number(secs) || 0);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const r = s % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
  };

  const parseTotalSeconds = (value) => {
    try {
      const parts = String(value || '').split(':').map((x) => Number(x));
      if (parts.length === 2) {
        const [m, s] = parts;
        return Math.max(0, (m || 0) * 60 + (s || 0));
      }
      if (parts.length === 3) {
        const [h, m, s] = parts;
        return Math.max(0, (h || 0) * 3600 + (m || 0) * 60 + (s || 0));
      }
      return 0;
    } catch {
      return 0;
    }
  };

  const formatCompactTime = (secs, total) => {
    const s = Math.max(0, Number(secs) || 0);
    const t = Math.max(0, Number(total) || 0);
    if (t > 0 && t < 3600) {
      const m = Math.floor(s / 60);
      const r = s % 60;
      return `${String(m).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
    }
    return formatHHMMSS(s);
  };

  const getTimerStage = (secs) => {
    const s = Math.max(0, Number(secs) || 0);
    if (s <= 120) return 'danger'; // last 2 min
    if (s <= 300) return 'warning'; // last 5 min
    return 'ok';
  };

  // Refs for coding UI panels
  const codingShellRef = useRef(null);
  const codingResultRef = useRef(null);
  const codingEditorWrapRef = useRef(null);

  // Note: Individual per-question timers removed - using global assessment timer instead
  // Candidates can submit any question at any time within the total duration

  const activeCodingLanguages = useMemo(() => {
    if (!activeCoding) return [];
    // Only show languages that are both globally allowed for this assessment AND supported by this specific question.
    // This prevents "mixed languages" in the dropdown for questions that don't support all of them.
    const allowed = Array.isArray(activeCoding.allowed_languages) ? activeCoding.allowed_languages : [];
    const supported = Array.isArray(activeCoding.languages) ? activeCoding.languages : [];

    let options = [];
    if (allowed.length > 0 && supported.length > 0) {
      options = allowed.filter(l => supported.includes(l));
    }

    // If intersection is empty or one list is missing, fallback to whatever we have
    if (options.length === 0) {
      options = allowed.length > 0 ? allowed : (supported.length > 0 ? supported : []);
    }

    const uniq = options.filter((v, idx) => options.indexOf(v) === idx && v);
    return uniq.length > 0 ? uniq : DEFAULT_LANGS;
  }, [activeCoding]);

  useEffect(() => {
    if (!codingQuestionsOrdered.length) return;
    setCodingState((prev) => {
      const nextCode = { ...prev.codeById };
      const nextLang = { ...prev.languageById };
      codingQuestionsOrdered.forEach((cq) => {
        const key = String(cq.id);
        if (nextCode[key] == null || nextLang[key] == null) {
          // If we have existing answers from backend (after refresh), use them
          const existing = codingState.existingAnswers?.[key];

          const allowed = Array.isArray(cq.allowed_languages) ? cq.allowed_languages : [];
          const supported = Array.isArray(cq.languages) ? cq.languages : [];
          let filtered = [];
          if (allowed.length > 0 && supported.length > 0) {
            filtered = allowed.filter(l => supported.includes(l));
          }
          if (filtered.length === 0) {
            filtered = allowed.length > 0 ? allowed : (supported.length > 0 ? supported : DEFAULT_LANGS);
          }
          const initialLang = existing?.language || filtered[0] || '';

          if (nextCode[key] == null) {
            if (existing?.code) {
              nextCode[key] = existing.code;
            } else {
              const starter = cq.starter_code || '';
              nextCode[key] = extractLanguageTemplate(starter, initialLang);
            }
          }
          if (nextLang[key] == null) {
            nextLang[key] = initialLang;
          }
        }
      });
      return {
        ...prev,
        codeById: nextCode,
        languageById: nextLang,
        currentId: prev.currentId ?? codingQuestionsOrdered[0].id,
      };
    });
  }, [codingQuestionsOrdered, codingState.existingAnswers]);

  useEffect(() => {
    if (!isDragging) return undefined;
    const handleMove = (e) => {
      if (!codingShellRef.current) return;
      const rect = codingShellRef.current.getBoundingClientRect();
      const pct = ((e.clientX - rect.left) / rect.width) * 100;
      const clamped = Math.max(18, Math.min(70, pct));
      setLeftWidth(clamped);
      setLastExpandedWidth(clamped);
    };
    const handleUp = () => setIsDragging(false);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [isDragging]);

  useEffect(() => {
    if (!isResultDragging) return undefined;
    const handleMove = (e) => {
      if (!codingEditorWrapRef.current) return;
      const rect = codingEditorWrapRef.current.getBoundingClientRect();
      const pctBottom = ((rect.height - (e.clientY - rect.top)) / rect.height) * 100;
      const clamped = Math.max(5, Math.min(90, pctBottom)); // allow dragging from ~5% up to ~90%
      setResultHeightPct(clamped);
    };
    const handleUp = () => setIsResultDragging(false);
    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [isResultDragging]);

  const toggleMSQ = (qid, key) => {
    const id = String(qid);
    const prev = answersById[id];
    const arr = Array.isArray(prev) ? prev : [];
    const exists = arr.includes(key);
    const next = exists ? arr.filter((x) => x !== key) : [...arr, key];
    setSelected(id, next);
  };

  const submit = async (isAutoSubmit = false) => {
    const auto = isAutoSubmit === true;
    setSubmitError('');
    if (!auto && firstUnansweredId) {
      setSubmitError('Please answer all questions before submitting.');
      const el = document.getElementById(`q-${firstUnansweredId}`);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    setSubmitting(true);
    try {
      // 1. Submit MCQ answers if any
      if (hasMcq) {
        await axios.post(`${API_BASE_URL}/invitations/public/${token}/submit/`, {
          answers: answersById,
        });
      }

      // 2. Finalize Coding if any
      if (codingQuestionsOrdered.length > 0) {
        // Build a map of codes + languages to send
        const codeMap = {};
        codingQuestionsOrdered.forEach(cq => {
          const key = String(cq.id);
          codeMap[key] = {
            code: codingState.codeById[key] || '',
            language: codingState.languageById[key] || cq.allowed_languages?.[0] || 'python3'
          };
        });

        await axios.post(`${API_BASE_URL}/invitations/public/${token}/coding/finalize/`, {
          code_map: codeMap
        });
      }

      setSubmitted(true);
      // End test -> show result page (pass autoSubmit flag for timeout popup)
      navigate(`/result/${token}`, { replace: true, state: { autoSubmit: auto } });
    } catch (e) {
      setSubmitError(e?.response?.data?.error || e?.message || 'Submit failed');
    } finally {
      setSubmitting(false);
    }
  };

  // Best-effort: discourage leaving / back navigation during exam
  useEffect(() => {
    if (submitted) return;
    const blockBack = () => {
      window.history.pushState(null, '', window.location.href);
    };

    const onPopState = () => {
      // push forward again
      blockBack();
      setSubmitError('Navigation is disabled while the exam is in progress.');
    };

    // seed
    blockBack();
    window.addEventListener('popstate', onPopState);

    const onBeforeUnload = (e) => {
      // Some browsers will show default confirm dialog
      e.preventDefault();
      e.returnValue = '';
      return '';
    };
    window.addEventListener('beforeunload', onBeforeUnload);

    return () => {
      window.removeEventListener('popstate', onPopState);
      window.removeEventListener('beforeunload', onBeforeUnload);
    };
  }, [submitted]);

  // Check if candidate details are already completed
  useEffect(() => {
    if (token) {
      // First check localStorage for quick check
      const stored = localStorage.getItem(`candidate_details_${token}`);
      if (stored) {
        try {
          const data = JSON.parse(stored);
          if (data && data.saved) {
            // Verify with backend
            axios.get(`${API_BASE_URL}/candidate-details/${token}/`)
              .then((response) => {
                if (response.data.success) {
                  setCandidateDetailsCompleted(true);
                } else {
                  setCandidateDetailsCompleted(false);
                }
              })
              .catch(() => {
                // If backend check fails, use localStorage as fallback
                if (data.firstName && data.lastName && data.email && data.phone && data.pan && data.snapshot) {
                  setCandidateDetailsCompleted(true);
                } else {
                  setCandidateDetailsCompleted(false);
                }
              });
          } else {
            setCandidateDetailsCompleted(false);
          }
        } catch (e) {
          // Invalid stored data, show candidate details form
          setCandidateDetailsCompleted(false);
        }
      } else {
        // Also check backend directly
        axios.get(`${API_BASE_URL}/candidate-details/${token}/`)
          .then((response) => {
            if (response.data.success) {
              setCandidateDetailsCompleted(true);
            }
          })
          .catch(() => {
            // Not found in backend, show form
            setCandidateDetailsCompleted(false);
          });
      }
    }
  }, [token]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const resp = await axios.get(`${API_BASE_URL}/invitations/public/${token}/`);
        setAssessment(resp.data?.assessment || null);
        setQuestions(resp.data?.questions || []);
        setCodingQuestions(resp.data?.coding_questions || []);
        setRemainingSeconds(typeof resp.data?.remaining_seconds === 'number' ? resp.data.remaining_seconds : null);

        // Restore partial coding state
        if (resp.data?.submitted_coding_ids || resp.data?.coding_answers) {
          setCodingState(prev => {
            const submittedIds = { ...prev.submittedIds };
            (resp.data.submitted_coding_ids || []).forEach(id => {
              submittedIds[String(id)] = true;
            });
            return {
              ...prev,
              submittedIds,
              existingAnswers: resp.data.coding_answers || {}
            };
          });
        }
      } catch (e) {
        const status = e?.response?.status;
        const message = e?.response?.data?.error || e?.message || 'Failed to load assessment';
        // If already completed, send to thank-you page
        if (status === 409 && token) {
          navigate(`/result/${token}`, { replace: true });
          return;
        }
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    if (token && candidateDetailsCompleted) load();
  }, [token, navigate, candidateDetailsCompleted]);

  // Fullscreen state listener
  useEffect(() => {
    const update = () => {
      setIsFullscreen(Boolean(document.fullscreenElement));
    };
    update();
    document.addEventListener('fullscreenchange', update);
    return () => document.removeEventListener('fullscreenchange', update);
  }, []);

  const requestFullscreen = async () => {
    try {
      setFsError('');
      const root = document.documentElement;
      if (root.requestFullscreen) await root.requestFullscreen();
    } catch {
      setFsError('Fullscreen permission is required to start the exam. Please click "Enter Full Screen".');
    }
  };

  // Countdown timer (starts when candidate opens the link)
  useEffect(() => {
    if (submitted) return;
    if (remainingSeconds === null) return;
    if (remainingSeconds <= 0) {
      // auto-submit when time ends
      submit(true);
      return;
    }
    const t = setInterval(() => {
      setRemainingSeconds((s) => (s === null ? s : Math.max(0, s - 1)));
    }, 1000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remainingSeconds, submitted]);

  const activeCode = activeCoding ? codingState.codeById[String(activeCoding.id)] || '' : '';
  const activeLanguage = activeCoding ? (codingState.languageById[String(activeCoding.id)] || activeCodingLanguages[0] || '') : '';
  const activeRunResult = activeCoding ? codingState.runResultById[String(activeCoding.id)] : null;

  useEffect(() => {
    if (activeRunResult && codingResultRef.current) {
      codingResultRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [activeRunResult]);

  useEffect(() => {
    if (activeCoding) {
      setCodingState((prev) => ({ ...prev, runError: '' }));
    }
  }, [activeCoding]);

  const runCode = async () => {
    if (!activeCoding) return;
    // Check global timer - allow running code as long as total time remains
    if (remainingSeconds !== null && remainingSeconds <= 0) {
      setCodingState((prev) => ({ ...prev, runError: 'Time is over. The exam has ended.' }));
      return;
    }
    const key = String(activeCoding.id);
    setCodingState((prev) => ({
      ...prev,
      running: true,
      runError: '',
      runResultById: { ...prev.runResultById, [key]: null },
    }));
    try {
      const resp = await axios.post(`${API_BASE_URL}/invitations/public/${token}/coding/run/`, {
        acq_id: activeCoding.id,
        code: activeCode,
        language: activeLanguage || activeCodingLanguages[0] || '',
      });
      setCodingState((prev) => ({
        ...prev,
        runResultById: { ...prev.runResultById, [key]: normalizeRunResult(resp.data) },
        running: false,
      }));
    } catch (e) {
      setCodingState((prev) => ({ ...prev, running: false, runError: e?.response?.data?.error || e?.message || 'Run failed' }));
    }
  };

  const submitCode = async () => {
    if (!activeCoding) return;
    // Check global timer - allow submitting code as long as total time remains
    if (remainingSeconds !== null && remainingSeconds <= 0) {
      setCodingState((prev) => ({ ...prev, runError: 'Time is over. The exam has ended.' }));
      return;
    }
    if (!window.confirm('Are you sure you want to submit your code?')) {
      return;
    }
    const key = String(activeCoding.id);
    setCodingState((prev) => ({
      ...prev,
      running: true,
      runError: '',
      runResultById: { ...prev.runResultById, [key]: null },
    }));
    try {
      const resp = await axios.post(`${API_BASE_URL}/invitations/public/${token}/coding/submit/`, {
        acq_id: activeCoding.id,
        code: activeCode,
        language: activeLanguage || activeCodingLanguages[0] || '',
      });
      setCodingState((prev) => ({
        ...prev,
        runResultById: { ...prev.runResultById, [key]: resp.data },
        running: false,
        submittedIds: { ...prev.submittedIds, [String(activeCoding.id)]: true },
      }));
      // Move to next coding question if exists
      const idx = codingQuestionsOrdered.findIndex((q) => String(q.id) === String(activeCoding.id));
      const next = codingQuestionsOrdered[idx + 1];
      if (next) {
        setCodingState((prev) => ({ ...prev, currentId: next.id, runError: '' }));
      }
    } catch (e) {
      setCodingState((prev) => ({ ...prev, running: false, runError: e?.response?.data?.error || e?.message || 'Submit failed' }));
    }
  };

  const toggleLeftPane = () => {
    if (isLeftCollapsed) {
      setIsLeftCollapsed(false);
      setLeftWidth(lastExpandedWidth || 40);
    } else {
      setLastExpandedWidth(leftWidth);
      setIsLeftCollapsed(true);
    }
  };

  const startDrag = (e) => {
    if (isLeftCollapsed) return;
    setIsDragging(true);
    e.preventDefault();
  };

  const toggleResultPanel = () => {
    setShowResultPanel((v) => !v);
  };

  const startResultDrag = (e) => {
    if (!showResultPanel || !activeRunResult) return;
    setIsResultDragging(true);
    e.preventDefault();
  };

  const leftPaneStyle = isLeftCollapsed
    ? { flex: '0 0 34px', minWidth: '34px' }
    : { flex: `0 0 ${leftWidth}%`, minWidth: '260px' };

  const resultPaneStyle = showResultPanel && activeRunResult
    ? { flex: `0 0 ${resultHeightPct}%`, maxHeight: '70vh' }
    : { display: 'none' };

  // Show candidate details form if not completed
  if (!candidateDetailsCompleted) {
    return (
      <CandidateDetails
        token={token}
        onComplete={(candidateData) => {
          setCandidateDetailsCompleted(true);
          // Optionally send candidate data to backend here
        }}
      />
    );
  }

  if (loading) {
    return (
      <div className="take-page">
        <div className="take-shell">
          <div className="take-card">Loading assessment…</div>
        </div>
      </div>
    );
  }

  if (error) {
    const msg = String(error || '');
    const title = (() => {
      if (msg.toLowerCase().includes('not started')) return 'Exam not started yet';
      if (msg.toLowerCase().includes('start window')) return 'Start window expired';
      if (msg.toLowerCase().includes('completed')) return 'Exam already completed';
      if (msg.toLowerCase().includes('expired')) return 'Link expired';
      if (msg.toLowerCase().includes('time is over')) return 'Time is over';
      return 'Invalid or expired link';
    })();
    return (
      <div className="take-page">
        <div className="take-shell">
          <div className="take-card error">
            <div className="take-title">{title}</div>
            <div className="take-sub">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  const hasMcq = questions.length > 0;



  return (
    <div className="take-page take-exam-mode">
      <div className="take-shell-exam">
        {!isFullscreen && !submitted ? (
          <div className="fs-gate" role="dialog" aria-label="Enter full screen">
            <div className="fs-card">
              <div className="fs-title">Start Exam</div>
              <div className="fs-sub">Fullscreen is required to start the exam.</div>
              {fsError ? <div className="fs-error">{fsError}</div> : null}
              <div className="fs-actions">
                <button
                  className="fs-primary"
                  type="button"
                  onClick={requestFullscreen}
                >
                  Enter Full Screen
                </button>
              </div>
            </div>
          </div>
        ) : null}

        {/* Floating Timer (Restored for ALL modes) */}
        {typeof remainingSeconds === 'number' && !submitted ? (
          <div className={`timer-box ${getTimerStage(remainingSeconds)}`}>
            <div className="timer-value">
              {formatCompactTime(remainingSeconds, parseTotalSeconds(assessment?.total_time))}
            </div>
          </div>
        ) : null}

        <div className="take-header">
          <div className="take-title">{assessment?.display_name || assessment?.name || 'Assessment'}</div>
          {!isFullscreen ? <div className="take-note"><span className="fs-badge">Fullscreen required</span></div> : null}
        </div>

        {submitted ? (
          <div className="take-card">
            <div className="take-title">Submitted successfully</div>
            <div className="take-sub">You can close this window now.</div>
          </div>
        ) : (
          <>
            {submitError ? (
              <div className="take-card error" style={{ marginBottom: 12 }}>
                <div className="take-title">Cannot submit</div>
                <div className="take-sub">{submitError}</div>
              </div>
            ) : null}

            {/* Coding Section (Keep as is, above the exam grid) */}
            {codingQuestionsOrdered.length > 0 ? (
              <div className="take-card coding-overview-card">
                <div className="coding-header-row" style={{ marginBottom: 10 }}>
                  <div>
                    <div className="take-title">Coding Questions</div>
                    <div className="take-sub">Solve coding problems in the Monaco editor.</div>
                  </div>
                  <div className="coding-header-actions" style={{ alignItems: 'center' }}>
                    <span className="pill gray">{codingQuestionsOrdered.length} questions</span>
                  </div>
                </div>
                <div className="coding-tablist">
                  {codingQuestionsOrdered.map((cq, idx) => {
                    const isActive = String(cq.id) === String(activeCoding?.id);
                    return (
                      <button
                        key={cq.id}
                        type="button"
                        className={`coding-tab ${isActive ? 'active' : ''}`}
                        onClick={() => setCodingState((prev) => ({ ...prev, currentId: cq.id }))}
                      >
                        <span>Coding Q{idx + 1}</span>
                        {codingState.submittedIds[String(cq.id)] ? <span className="coding-tab-badge">Submitted</span> : null}
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : null}

            {codingQuestionsOrdered.length > 0 && activeCoding ? (
              <div className="coding-attempt-shell take-coding-shell" ref={codingShellRef} style={{ marginBottom: '2rem' }}>
                <div
                  className={`coding-pane coding-pane-left ${isLeftCollapsed ? 'is-collapsed' : ''}`}
                  style={leftPaneStyle}
                >
                  <button
                    type="button"
                    className="coding-collapse-btn"
                    onClick={toggleLeftPane}
                    aria-label={isLeftCollapsed ? 'Expand question panel' : 'Collapse question panel'}
                  >
                    {isLeftCollapsed ? '▶' : '◀'}
                  </button>
                  {!isLeftCollapsed && (
                    <div className="coding-pane-left-content">
                      <div className="coding-pane-header">
                        <div>
                          <div className="coding-title">{activeCoding.title || 'Coding question'}</div>
                          <div className="coding-meta">
                            {activeCodingLanguages.map((lang) => (
                              <span key={lang} className="coding-pill coding-pill-muted">{lang}</span>
                            ))}
                            {activeCoding.mode ? <span className="coding-pill coding-pill-muted">{activeCoding.mode}</span> : null}
                          </div>
                        </div>
                        {/* Note: Using global assessment timer (top right) for all coding questions */}
                      </div>
                      <div className="coding-pane-body">
                        <div className="coding-problem">{activeCoding.description || 'No description provided.'}</div>
                      </div>
                    </div>
                  )}
                </div>

                <div
                  className={`coding-resizer ${isDragging ? 'dragging' : ''} ${isLeftCollapsed ? 'disabled' : ''}`}
                  onMouseDown={startDrag}
                  role="separator"
                  aria-label="Resize panels"
                  aria-orientation="vertical"
                />

                <div className="coding-pane coding-pane-right">
                  <div className="coding-pane-header">
                    <div className="coding-title">Code Editor</div>
                    <div className="coding-toolbar">
                      {activeCodingLanguages.length > 0 ? (
                        <select
                          className="coding-input coding-language-select"
                          value={activeLanguage || activeCodingLanguages[0] || ''}
                          disabled={!!codingState.submittedIds[String(activeCoding.id)]}
                          onChange={(e) => {
                            const newLang = e.target.value;
                            setCodingState((prev) => {
                              // Auto-update code template if switching language and code is essentially empty/default
                              const currentCode = prev.codeById[String(activeCoding.id)] || '';
                              const starterCode = activeCoding.starter_code || '';
                              const langSpecificCode = extractLanguageTemplate(starterCode, newLang);

                              // Heuristic: update if code is empty, or looks like a template
                              const isStillTemplate = currentCode.trim() === '' ||
                                currentCode.includes('// Your code here') ||
                                currentCode.includes('# Your code here') ||
                                currentCode.includes('// ===') ||
                                currentCode === starterCode ||
                                currentCode === extractLanguageTemplate(starterCode, activeLanguage);

                              const nextCode = { ...prev.codeById };
                              if (isStillTemplate) {
                                nextCode[String(activeCoding.id)] = langSpecificCode;
                              }

                              return {
                                ...prev,
                                languageById: { ...prev.languageById, [String(activeCoding.id)]: newLang },
                                codeById: nextCode,
                              };
                            });
                          }}
                        >
                          {activeCodingLanguages.map((lang) => (
                            <option key={lang} value={lang}>{lang}</option>
                          ))}
                        </select>
                      ) : (
                        <span className="coding-pill coding-pill-muted">{activeLanguage || 'No language'}</span>
                      )}
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={toggleResultPanel}
                        disabled={!activeRunResult}
                      >
                        Test Cases
                      </button>
                      <button type="button" className="btn btn-secondary" onClick={runCode} disabled={codingState.running || loading || !!codingState.submittedIds[String(activeCoding.id)]}>
                        {codingState.running ? 'Running…' : 'Run'}
                      </button>
                      <button type="button" className="btn btn-primary" onClick={submitCode} disabled={codingState.running || loading || !!codingState.submittedIds[String(activeCoding.id)]}>
                        {codingState.running ? 'Submitting…' : (codingState.submittedIds[String(activeCoding.id)] ? 'Submitted' : 'Submit Answer')}
                      </button>
                    </div>
                  </div>

                  {codingState.runError ? (
                    <div className="coding-card coding-error" style={{ margin: '10px 12px', padding: '10px 12px' }}>
                      {codingState.runError}
                    </div>
                  ) : null}

                  <div className="coding-editor-wrap" ref={codingEditorWrapRef}>
                    <div className="coding-monaco">
                      <Suspense fallback={<div className="coding-monaco-loading">Loading editor…</div>}>
                        <MonacoEditor
                          key={activeCoding.id}
                          height="100%"
                          defaultLanguage={monacoLanguage(activeLanguage)}
                          language={monacoLanguage(activeLanguage)}
                          value={activeCode}
                          onChange={(v) => {
                            const value = v ?? '';
                            setCodingState((prev) => ({
                              ...prev,
                              codeById: { ...prev.codeById, [String(activeCoding.id)]: value },
                            }));
                          }}
                          theme="vs-dark"
                          options={{
                            fontSize: 13,
                            minimap: { enabled: false },
                            automaticLayout: true,
                            scrollBeyondLastLine: false,
                            wordWrap: 'on',
                            readOnly: !!codingState.submittedIds[String(activeCoding.id)],
                          }}
                        />
                      </Suspense>
                    </div>

                    {activeRunResult ? (
                      <div
                        className={`coding-horizontal-resizer ${isResultDragging ? 'dragging' : ''} ${!showResultPanel ? 'disabled' : ''}`}
                        onMouseDown={startResultDrag}
                        role="separator"
                        aria-label="Resize editor and test cases"
                        aria-orientation="horizontal"
                      />
                    ) : null}

                    {activeRunResult ? (
                      <div className="coding-result" ref={codingResultRef} style={resultPaneStyle}>
                        {activeRunResult.results ? (
                          <>
                            <div className="coding-result-summary">
                              Status: <b>{activeRunResult.status}</b> • Passed: <b>{activeRunResult.passed_count}</b> / {activeRunResult.total_tests} • Time:{' '}
                              {formatDuration(activeRunResult.execution_time_ms)}{' '}
                              {activeRunResult.submission_id ? `• Submission #${activeRunResult.submission_id}` : ''}
                            </div>
                            <div className="coding-table">
                              <div className="coding-table-head">
                                <div>Test</div>
                                <div>Status</div>
                                <div>stdout</div>
                                <div>stderr</div>
                              </div>
                              {activeRunResult.results.map((r, idx) => {
                                const isHidden = r.is_hidden ?? r.hidden ?? false;
                                return (
                                  <div key={r.testcase_id ?? idx} className="coding-table-row">
                                    <div className="coding-test-label">
                                      <span className={isHidden ? 'coding-pill-hidden' : 'coding-pill-visible'}>
                                        {isHidden ? 'Hidden' : 'Visible'}
                                      </span>
                                      <span className="coding-test-name">Test {idx + 1}</span>
                                    </div>
                                    <div className={`coding-status coding-status-${String(r.status || '').toLowerCase()}`}>{r.status}</div>
                                    <div className="coding-mono">
                                      {(activeLanguage || '').toLowerCase() === 'sql' && String(r.status || '').toLowerCase() !== 'passed' && String(r.status || '').toLowerCase() !== 'pass' ? (
                                        <span style={{ color: '#666', fontStyle: 'italic' }}>(Hidden until passed)</span>
                                      ) : (
                                        (r.stdout || '').trim() || '—'
                                      )}
                                    </div>
                                    <div className="coding-mono">{(r.stderr || '').trim() || '—'}</div>
                                  </div>
                                );
                              })}
                            </div>
                          </>
                        ) : (
                          <pre className="coding-mono">{JSON.stringify(activeRunResult, null, 2)}</pre>
                        )}
                      </div>
                    ) : null}
                  </div>
                </div>
              </div>
            ) : null}

            {/* Finish Assessment button for coding-only assessments */}
            {codingQuestionsOrdered.length > 0 && questions.length === 0 && !submitted ? (
              <div className="take-footer">
                <button className="submit-btn" type="button" onClick={() => submit(false)} disabled={submitting}>
                  {submitting ? 'Submitting…' : 'Finish Assessment'}
                </button>
              </div>
            ) : null}

            {/* Objective Questions Exam Mode Layout */}
            {questions.length > 0 && currentQuestion ? (
              <div className="take-exam-layout">
                {/* Main Question Area */}
                <div className="take-exam-main">
                  <div className="take-card-single">
                    <div className="q-top">
                      <div className="q-num">Question {activeQuestionIndex + 1}</div>
                      <div className="q-meta">
                        {currentQuestion.skill ? <span className="pill">{currentQuestion.skill}</span> : null}
                        {currentQuestion.question_type ? <span className="pill gray">{currentQuestion.question_type}</span> : null}
                      </div>
                    </div>
                    <div className="q-text">{currentQuestion.question}</div>

                    <div className="q-options">
                      {buildOptions(currentQuestion).map((opt) => {
                        const qid = String(currentQuestion.id);
                        const qt = (currentQuestion.question_type || '').toUpperCase();
                        const isMSQ = qt === 'MSQ';
                        const selected = getSelected(qid);
                        const checked = isMSQ ? (Array.isArray(selected) ? selected.includes(opt.key) : false) : selected === opt.key;

                        return (
                          <label className={`opt opt-select ${checked ? 'checked' : ''} ${isMSQ ? 'opt-msq' : ''}`} key={`${qid}-${opt.key}`}>
                            <input
                              className="opt-input"
                              type={isMSQ ? 'checkbox' : 'radio'}
                              name={`q-${qid}`}
                              value={opt.key}
                              checked={checked}
                              onChange={() => {
                                if (isMSQ) toggleMSQ(qid, opt.key);
                                else setSelected(qid, opt.key);
                              }}
                            />
                            <span className="opt-k">{opt.key}</span>
                            <span className="opt-text">{opt.text}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>

                  {/* Actions Footer */}
                  <div className="take-exam-footer">
                    <button className="btn-exam-action secondary" onClick={handlePrev} disabled={activeQuestionIndex === 0}>
                      ← Previous
                    </button>
                    <button className="btn-exam-action warning" onClick={() => handleClearResponse(currentQuestion.id)}>
                      Clear Response
                    </button>
                    <button className="btn-exam-action info" onClick={() => handleMarkForReview(currentQuestion.id)}>
                      {markedReviewIds[String(currentQuestion.id)] ? 'Unmark Review' : 'Mark for Review'}
                    </button>
                    {activeQuestionIndex === questions.length - 1 ? (
                      <div style={{ flex: 1, textAlign: 'right' }}>
                        <button className="submit-btn" type="button" onClick={submit} disabled={submitting}>
                          {submitting ? 'Submitting…' : 'Submit Exam'}
                        </button>
                      </div>
                    ) : (
                      <button className="btn-exam-action primary" onClick={handleNext}>
                        Save & Next →
                      </button>
                    )}
                  </div>
                </div>

                {/* Right Sidebar: Palette */}
                <div className="take-exam-sidebar">

                  <div className="question-palette-card">
                    <div className="palette-title">QUESTION PALETTE</div>

                    <div className="palette-legend">
                      <div className="legend-item"><span className="dot answered"></span> Answered</div>
                      <div className="legend-item"><span className="dot not_answered"></span> Not Answered</div>
                      <div className="legend-item"><span className="dot marked"></span> Marked</div>
                      <div className="legend-item"><span className="dot not_visited"></span> Not Visited</div>
                    </div>

                    <div className="palette-grid">
                      {questions.map((q, idx) => {
                        const status = getQuestionStatus(q, idx);
                        const isCurrent = idx === activeQuestionIndex;
                        return (
                          <button
                            key={q.id}
                            className={`palette-item ${status} ${isCurrent ? 'current' : ''}`}
                            onClick={() => handleQuestionPaletteClick(idx)}
                          >
                            {idx + 1}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div className="sidebar-submit-section">
                    <button className="submit-btn full-width" type="button" onClick={submit} disabled={submitting}>
                      {submitting ? 'Submitting…' : 'Submit Exam'}
                    </button>
                  </div>
                </div>
              </div>
            ) : null}

            {questions.length === 0 && codingQuestionsOrdered.length === 0 ? (
              <div className="take-card">No questions found for this assessment.</div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}

