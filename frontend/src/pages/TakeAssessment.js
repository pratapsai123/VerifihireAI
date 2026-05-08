import React, { Suspense, useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import CandidateDetails from './CandidateDetails';
import '../styles/CodingAttempt.css';
import '../styles/TakeAssessment.css';
import { API_BASE_URL } from '../apiConfig';
import { useMalpracticeDetection } from '../hooks/useMalpracticeDetection';
import { logCandidateActivity } from '../utils/activityLogger';

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

  // Create or load Session ID and configure Axios interceptor
  useEffect(() => {
    if (!token) return;
    let localSessionId = localStorage.getItem(`assessment_session_id_${token}`);
    if (!localSessionId) {
      localSessionId = window.crypto && window.crypto.randomUUID ? window.crypto.randomUUID() : Math.random().toString(36).substring(2) + Date.now();
      localStorage.setItem(`assessment_session_id_${token}`, localSessionId);
    }

    // Add request interceptor to attach session ID to all relevant requests
    const reqInterceptor = axios.interceptors.request.use((config) => {
      if (config.url && (config.url.includes('/invitations/public/') || config.url.includes('/candidate-details/'))) {
        if (!config.headers) config.headers = {};
        config.headers['X-Session-ID'] = localSessionId;
      }
      return config;
    });

    return () => {
      axios.interceptors.request.eject(reqInterceptor);
    };
  }, [token]);

  const [candidateDetailsCompleted, setCandidateDetailsCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [scheduleInfo, setScheduleInfo] = useState(null);
  // Pre-check: time window error shown BEFORE the candidate details form
  const [windowError, setWindowError] = useState('');
  const [windowStatus, setWindowStatus] = useState(null);
  const [windowSchedule, setWindowSchedule] = useState(null);
  const [precheckLoading, setPrecheckLoading] = useState(true);
  const [alreadySubmitted, setAlreadySubmitted] = useState(false);
  const [assessment, setAssessment] = useState(null);
  const [questions, setQuestions] = useState([]);
  const hasMcq = questions.length > 0;
  const [codingQuestions, setCodingQuestions] = useState([]);
  const [answersById, setAnswersById] = useState(() => {
    try {
      const saved = localStorage.getItem(`take_assessment_progress_${token}`);
      if (saved) return JSON.parse(saved).answersById || {};
    } catch { }
    return {};
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [remainingSeconds, setRemainingSeconds] = useState(null);
  const [codingState, setCodingState] = useState(() => {
    const initialState = {
      currentId: null,
      codeById: {},
      languageById: {},
      runResultById: {},
      runError: '',
      running: false,
      submittedIds: {},
    };
    try {
      const saved = localStorage.getItem(`take_assessment_progress_${token}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        initialState.submittedIds = parsed.submittedIds || {};
        initialState.codeById = parsed.codeById || {};
        initialState.languageById = parsed.languageById || {};
      }
    } catch { }
    return initialState;
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
  const [aiToast, setAiToast] = useState({ active: false, text: '', urgent: false });
  // ── Network connectivity — pause exam timer when offline ─────────────
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  const isOnlineRef = useRef(navigator.onLine);

  useEffect(() => {
    const goOffline = () => {
      setIsOnline(false);
      isOnlineRef.current = false;
      logCandidateActivity(token, 'Connection Lost', 'Candidate internet connection dropped — exam timer paused.');
    };
    const goOnline = () => {
      setIsOnline(true);
      isOnlineRef.current = true;
      logCandidateActivity(token, 'Connection Restored', 'Candidate internet connection restored — exam timer resumed.');
    };
    window.addEventListener('vh_network_offline', goOffline);
    window.addEventListener('vh_network_online', goOnline);
    // Also listen to native events as fallback
    window.addEventListener('offline', goOffline);
    window.addEventListener('online', goOnline);
    return () => {
      window.removeEventListener('vh_network_offline', goOffline);
      window.removeEventListener('vh_network_online', goOnline);
      window.removeEventListener('offline', goOffline);
      window.removeEventListener('online', goOnline);
    };
  }, [token]);

  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const detectorRef = useRef(null);
  const lastDetectionTimeRef = useRef(0);
  const lastCaptureTimeRef = useRef({ time: 0, type: null }); // For throttling tab_switch/window_blur
  const screenStreamRef = useRef(null);
  const screenCanvasRef = useRef(null);
  const [screenShareError, setScreenShareError] = useState(''); // eslint-disable-line no-unused-vars
  const wasFsRef = useRef(false);

  // Split Assessment State
  const [assessmentStage, setAssessmentStage] = useState('loading'); // loading, objective, transition, coding, completed
  const [objectiveSeconds, setObjectiveSeconds] = useState(null);
  const [codingSeconds, setCodingSeconds] = useState(null);
  // Track when each stage started to calculate elapsed time on refresh
  const [stageStartTimes, setStageStartTimes] = useState(() => {
    try {
      const saved = localStorage.getItem(`take_assessment_progress_${token}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          objective: parsed.objectiveStartTime || null,
          coding: parsed.codingStartTime || null
        };
      }
    } catch { }
    return { objective: null, coding: null };
  });
  const [objResult, setObjResult] = useState(null); // { passed, score, percentage, message }
  const [transitionTimer, setTransitionTimer] = useState(15);

  // New State for Exam Mode
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(() => {
    try {
      const saved = localStorage.getItem(`take_assessment_progress_${token}`);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.activeQuestionIndex !== undefined) return parsed.activeQuestionIndex;
      }
    } catch { }
    return 0;
  });
  const [markedReviewIds, setMarkedReviewIds] = useState(() => {
    try {
      const saved = localStorage.getItem(`take_assessment_progress_${token}`);
      if (saved) return JSON.parse(saved).markedReviewIds || {};
    } catch { }
    return {};
  });
  // Track visited questions to mark them as "Not Answered" (Red) vs "Not Visited" (Gray)
  const [visitedIds, setVisitedIds] = useState(() => {
    try {
      const saved = localStorage.getItem(`take_assessment_progress_${token}`);
      if (saved) return JSON.parse(saved).visitedIds || {};
    } catch { }
    return {};
  });

  // Cleanup old/large localStorage items to stay within quota
  useEffect(() => {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        // Clear old progress or details that don't match the current token
        if ((key.startsWith('take_assessment_progress_') || key.startsWith('candidate_details_')) && !key.endsWith(token)) {
          localStorage.removeItem(key);
        }
      });
    } catch (e) {
      console.warn('LocalStorage cleanup failed', e);
    }
  }, [token]);

  useEffect(() => {
    if (!token || submitted || assessmentStage === 'loading') return;
    try {
      const progress = {
        answersById,
        codeById: codingState.codeById,
        languageById: codingState.languageById,
        assessmentStage,
        activeQuestionIndex,
        markedReviewIds,
        visitedIds,
        remainingSeconds,
        objectiveSeconds,
        codingSeconds,
        objectiveStartTime: stageStartTimes.objective,
        codingStartTime: stageStartTimes.coding,
      };
      localStorage.setItem(`take_assessment_progress_${token}`, JSON.stringify(progress));
    } catch (e) {
      console.error('Failed to autosave progress', e);
    }
  }, [token, answersById, codingState.codeById, codingState.languageById, submitted, assessmentStage, activeQuestionIndex, markedReviewIds, visitedIds, remainingSeconds, objectiveSeconds, codingSeconds, stageStartTimes]);

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

  // Integrated Malpractice Detection Module
  const { suspicionScore: mpScore, reasons: mpReasons } = useMalpracticeDetection(
    token,
    activeCoding ? codingState.codeById[String(activeCoding.id)] : '',
    { allowCopyPaste: true } // Temporarily allow for standard assessments
  );


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

      logCandidateActivity(token, 'Assessment Submitted', isAutoSubmit ? 'Auto-submitted due to timeout.' : 'Manually submitted by candidate.');

      setSubmitted(true);
      localStorage.removeItem(`take_assessment_progress_${token}`);
      // End test -> show result page (pass autoSubmit flag for timeout popup)
      navigate(`/result/${token}`, { replace: true, state: { autoSubmit: auto } });
    } catch (e) {
      const msg = e?.response?.data?.error || e?.message || 'Submit failed';
      if (e?.response?.status === 403 || e?.response?.status === 409 || msg.toLowerCase().includes('time is over')) {
        setError(msg);
      } else {
        setSubmitError(msg);
      }
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

    return () => {
      window.removeEventListener('popstate', onPopState);
    };
  }, [submitted]);

  // Auto-start coding section after 15 seconds
  useEffect(() => {
    let timer;
    if (assessmentStage === 'transition' && transitionTimer > 0) {
      timer = setInterval(() => {
        setTransitionTimer((prev) => prev - 1);
      }, 1000);
    } else if (assessmentStage === 'transition' && transitionTimer === 0) {
      setAssessmentStage('coding');
      window.scrollTo(0, 0);
    }
    return () => clearInterval(timer);
  }, [assessmentStage, transitionTimer]);

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
                  window.dispatchEvent(new Event('vh_exam_started'));
                } else {
                  setCandidateDetailsCompleted(false);
                }
              })
              .catch(() => {
                // If backend check fails, use localStorage as fallback
                if (data.firstName && data.lastName && data.email && data.phone && data.pan && data.snapshot) {
                  setCandidateDetailsCompleted(true);
                  window.dispatchEvent(new Event('vh_exam_started'));
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
              window.dispatchEvent(new Event('vh_exam_started'));
            }
          })
          .catch(() => {
            // Not found in backend, show form
            setCandidateDetailsCompleted(false);
          });
      }
    }
  }, [token]);

  // Pre-check the assessment window as soon as the token is available.
  // This runs BEFORE showing the candidate details form so the candidate
  // doesn't waste time filling in details when the window is expired/not open.
  useEffect(() => {
    if (!token) return;
    setPrecheckLoading(true);
    axios.get(`${API_BASE_URL}/invitations/public/${token}/?check_only=1`)
      .then(() => {
        // Window is open — clear any prior error
        setWindowError('');
        setWindowSchedule(null);
        setPrecheckLoading(false);
      })
      .catch((err) => {
        const status = err?.response?.status;
        setWindowStatus(status);
        // 403 = not started yet, 410 = expired / window closed, 404 = invalid link
        if (status === 403 || status === 410 || status === 404) {
          setWindowError(err?.response?.data?.error || 'This assessment link is not accessible.');
          setWindowSchedule(err?.response?.data?.schedule || null);
        }
        // 409 = already submitted or session locked
        if (status === 409) {
          const errMsg = err?.response?.data?.error;
          if (errMsg && errMsg.includes('already in use')) {
            setWindowError(errMsg);
          } else {
            setAlreadySubmitted(true);
          }
        }
        setPrecheckLoading(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const resp = await axios.get(`${API_BASE_URL}/invitations/public/${token}/`);
        const data = resp.data;
        const assess = data.assessment || {};
        setAssessment(assess);
        setQuestions(data.questions || []);
        const cQuestions = data.coding_questions || [];
        setCodingQuestions(cQuestions);

        // Determine Stage & Timers
        // Check if objective already submitted?
        // We can infer from `data.invitation.status` or `data.submitted_coding_ids`.
        // Ideally backend should tell us if objective is done.
        // For now, check if we have objective score in submission? 
        // We don't have full submission object here, but we can check `data.coding_answers` existence logic.

        // BETTER: Assume if `data.questions` exist and not submitted, we are in objective.
        // If `data.questions` empty or we have evidence of objective done?

        // Let's use local storage or infer from time remaining?
        // Actually, `remaining_seconds` from backend is `expires_at - now`.
        // With split times, `expires_at` might be the FINAL deadline.
        // We need to manage stage-based timers client-side if backend doesn't explicitly track "current stage" in DB.
        // But we added `submit_objective_section`.

        const hasObjective = (data.questions || []).length > 0;
        // const hasCoding = (cQuestions || []).length > 0; // Unused

        // Parse time limits
        const objTimeLimit = parseTotalSeconds(assess.objective_time_limit || assess.total_time); // Fallback to total if split not set
        const codTimeLimit = parseTotalSeconds(assess.coding_time_limit || assess.coding_total_time);

        // Initial State Logic
        let initialStage = 'objective';
        if (!hasObjective) initialStage = 'coding';

        // If we have coding answers or submitted ids, we are likely in coding or done
        if ((data.submitted_coding_ids && data.submitted_coding_ids.length > 0) ||
          (data.coding_answers && Object.keys(data.coding_answers).length > 0)) {
          initialStage = 'coding';
        }

        try {
          const saved = localStorage.getItem(`take_assessment_progress_${token}`);
          if (saved) {
            const parsed = JSON.parse(saved);
            if (parsed.assessmentStage && parsed.assessmentStage !== 'loading') {
              if (parsed.assessmentStage === 'coding' || parsed.assessmentStage === 'transition') {
                initialStage = parsed.assessmentStage;
              }
            }
          }
        } catch { }

        // If assessment has `has_objective_cutoff` and we are in coding, it means we passed.

        setAssessmentStage(initialStage);

        // Record start times if not already set
        const nowMs = Date.now();
        let currentObjStart = stageStartTimes.objective;
        let currentCodStart = stageStartTimes.coding;

        if (initialStage === 'objective' && !currentObjStart) {
          currentObjStart = nowMs;
          setStageStartTimes(prev => ({ ...prev, objective: nowMs }));
        } else if (initialStage === 'coding' && !currentCodStart) {
          currentCodStart = nowMs;
          setStageStartTimes(prev => ({ ...prev, coding: nowMs }));
        }

        // Calculate remaining seconds for each stage based on elapsed time
        if (initialStage === 'objective' && currentObjStart) {
          const elapsed = Math.floor((nowMs - currentObjStart) / 1000);
          setObjectiveSeconds(Math.max(0, objTimeLimit - elapsed));
        } else {
          setObjectiveSeconds(objTimeLimit);
        }

        if (initialStage === 'coding' && currentCodStart) {
          const elapsed = Math.floor((nowMs - currentCodStart) / 1000);
          setCodingSeconds(Math.max(0, codTimeLimit - elapsed));
        } else {
          setCodingSeconds(codTimeLimit);
        }

        // Initialize global timer from backend (Total expiry) - ALWAYS trust backend for global time
        if (typeof data.remaining_seconds === 'number') {
          setRemainingSeconds(data.remaining_seconds);
        }

        // Restore partial coding state
        if (data.submitted_coding_ids || data.coding_answers) {
          setCodingState(prev => {
            const submittedIds = { ...prev.submittedIds };
            (data.submitted_coding_ids || []).forEach(id => {
              submittedIds[String(id)] = true;
            });
            return {
              ...prev,
              submittedIds,
              existingAnswers: data.coding_answers || {}
            };
          });
        }
      } catch (e) {
        const status = e?.response?.status;
        const message = e?.response?.data?.error || e?.message || 'Failed to load assessment';
        if (status === 409 && token) {
          if (message.includes('already in use')) {
            setError(message);
          } else {
            setAlreadySubmitted(true);
          }
          setLoading(false);
          return;
        }
        setScheduleInfo(e?.response?.data?.schedule || null);
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    // Only load assessment AFTER pre-check has completed and assessment is not already submitted
    if (token && candidateDetailsCompleted && !precheckLoading && !alreadySubmitted) load();
  }, [token, navigate, candidateDetailsCompleted, precheckLoading, alreadySubmitted]);

  // Integrity Tracking: Tab Switches / Leaving Window & Camera
  const showAiEvent = useCallback(async (text, urgent = false, eventType = null) => {
    setAiToast({ active: true, text, urgent });
    setTimeout(() => setAiToast({ active: false, text: '', urgent: false }), 3000);

    if (!eventType || !token || submitted || assessmentStage === 'loading' || assessmentStage === 'completed') {
      console.log('Skipping API call due to:', { eventType, token, submitted, assessmentStage });
      return;
    }

    // Throttling for screen-based events (tab_switch, window_blur)
    const isScreenEvent = ['tab_switch', 'window_blur', 'window_switch'].includes(eventType);
    if (isScreenEvent) {
      const now = Date.now();
      // Only throttle if it's the SAME event type within 2 seconds
      if (lastCaptureTimeRef.current.type === eventType && (now - lastCaptureTimeRef.current.time < 2000)) {
        console.log(`Throttling duplicate integrity event: ${eventType}`);
        return;
      }
      lastCaptureTimeRef.current = { time: now, type: eventType };
    }

    let screenshot = null;
    if (isScreenEvent && screenStreamRef.current && screenCanvasRef.current) {
      try {
        // Quick draw from the live stream track using ImageCapture if available,
        // otherwise rely on a pre-existing background video element.
        // For maximum compatibility and speed, we create a quick video element, 
        // but we don't wait for loadedmetadata if it takes too long.
        const video = document.createElement('video');
        video.srcObject = screenStreamRef.current;
        video.muted = true;
        video.playsInline = true;

        await new Promise((resolve) => {
          let resolved = false;
          // Fallback timeout because loadedmetadata might not fire if tab is fully backgrounded
          const fallback = setTimeout(() => {
            if (!resolved) { resolved = true; resolve(); }
          }, 300);

          video.onloadedmetadata = () => {
            video.play().then(() => {
              if (!resolved) {
                resolved = true;
                clearTimeout(fallback);
                setTimeout(resolve, 50); // slight delay to paint
              }
            }).catch(() => {
              if (!resolved) { resolved = true; clearTimeout(fallback); resolve(); }
            });
          };
          video.onerror = () => {
            if (!resolved) { resolved = true; clearTimeout(fallback); resolve(); }
          };
        });

        const canvas = screenCanvasRef.current;
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth || window.innerWidth || 1280;
        canvas.height = video.videoHeight || window.innerHeight || 720;

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        screenshot = canvas.toDataURL('image/jpeg', 0.5);

        video.pause();
        video.srcObject = null;
      } catch (e) {
        console.error('Failed to capture integrity snapshot', e);
      }
    }

    let webcamScreenshot = null;
    if (['multiface_detection', 'phone_detection', 'no_face_detection', 'face_detection_lost', 'face_detection_lost_rechecked'].includes(eventType) && videoRef.current && videoRef.current.readyState >= 2) {
      try {
        const camCanvas = document.createElement('canvas');
        camCanvas.width = videoRef.current.videoWidth || 640;
        camCanvas.height = videoRef.current.videoHeight || 480;
        const ctx = camCanvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0, camCanvas.width, camCanvas.height);
        webcamScreenshot = camCanvas.toDataURL('image/jpeg', 0.5);
      } catch (e) {
        console.error('Failed to capture webcam snapshot', e);
      }
    }

    try {
      console.log('Posting integrity event to:', `${API_BASE_URL}/invitations/public/${token}/integrity/`);
      const resp = await axios.post(`${API_BASE_URL}/invitations/public/${token}/integrity/`, {
        event_type: eventType,
        timestamp: new Date().toISOString(),
        screenshot: screenshot,
        webcam_screenshot: webcamScreenshot
      });
      console.log('Integrity API Response:', resp.data);
    } catch (err) {
      console.error('Failed to log integrity event', err.response?.data || err.message);
    }
  }, [token, submitted, assessmentStage]);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play().catch(() => { }); }
      streamRef.current = stream;
    } catch { showAiEvent('Camera Denied', true); }
  }, [showAiEvent]);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    if (screenStreamRef.current) {
      screenStreamRef.current.getTracks().forEach(t => t.stop());
      screenStreamRef.current = null;
    }
  }, []);

  const startScreenShare = useCallback(async () => {
    try {
      setFsError('');
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { displaySurface: 'monitor' },
        audio: false
      });

      const track = stream.getVideoTracks()[0];
      const settings = track.getSettings();

      // Enforce "Entire Screen" (monitor)
      if (settings.displaySurface !== 'monitor') {
        track.stop();
        setFsError('Please share your "Entire Screen" to proceed. Tab or Individual Window sharing is not allowed for security.');
        return false;
      }

      screenStreamRef.current = stream;

      // If user stops sharing manually
      track.onended = () => {
        showAiEvent('SCREEN SHARING STOPPED', true, 'window_switch');
        // Do not force exit fullscreen immediately to avoid jarring experience,
        // but set error to force them to click "Resume" which retriggers requestFullscreen
        setFsError('Screen sharing stopped. You must restart screen sharing to continue.');
      };

      return true;
    } catch (err) {
      console.error('Screen share error:', err);
      setFsError('Screen sharing permission (Entire Screen) is mandatory to take this assessment.');
      return false;
    }
  }, [showAiEvent]);

  const requestFullscreen = async () => {
    const elem = document.documentElement;
    try {
      setFsError('');

      // 1. Mandatory Screen Share FIRST
      // We request screen share before fullscreen because the browser's screen share dialog 
      // often forces the window out of fullscreen mode. By sharing first, we ensure 
      // that the subsequent fullscreen request stays active.
      if (!screenStreamRef.current || !screenStreamRef.current.active) {
        const success = await startScreenShare();
        if (!success) {
          // If they don't agree to screen share, we can't proceed
          return;
        }
      }

      // 2. Fullscreen request (after screen share dialog is resolved)
      if (elem.requestFullscreen) {
        await elem.requestFullscreen();
      } else if (elem.webkitRequestFullscreen) {
        await elem.webkitRequestFullscreen();
      } else if (elem.mozRequestFullScreen) {
        await elem.mozRequestFullScreen();
      } else if (elem.msRequestFullscreen) {
        await elem.msRequestFullscreen();
      }

      // Verify success
      const isFsNow = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
      if (!isFsNow) {
        throw new Error("Fullscreen request denied by browser.");
      }

      // 2. Mandatory Screen Share
      if (!screenStreamRef.current || !screenStreamRef.current.active) {
        const success = await startScreenShare();
        if (!success) {
          // Exit fullscreen if they don't agree to screen share
          if (document.exitFullscreen) document.exitFullscreen().catch(() => { });
          else if (document.webkitExitFullscreen) document.webkitExitFullscreen().catch(() => { });
          return;
        }

        // Re-check fullscreen - screen share often causes an exit
        const isFsAfterShare = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
        if (!isFsAfterShare) {
          if (elem.requestFullscreen) await elem.requestFullscreen();
          else if (elem.webkitRequestFullscreen) await elem.webkitRequestFullscreen();
        }
      }

      // 3. Camera (already started mostly, but ensure success)
      await startCamera();

    } catch (err) {
      console.error('Fullscreen error:', err);
      setFsError('Fullscreen mode is required. Please ensure browser permissions are allowed and try again.');
    }
  };

  // Fullscreen state listener & violation logging
  useEffect(() => {
    const update = () => {
      const isFs = Boolean(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
      );
      setIsFullscreen(isFs);

      // Log violation ONLY if they were previously in fullscreen and just exited
      if (wasFsRef.current && !isFs && candidateDetailsCompleted && !submitted && (assessmentStage === 'objective' || assessmentStage === 'coding')) {
        showAiEvent('FULLSCREEN EXITED', true, 'window_blur');
      }
      wasFsRef.current = isFs;
    };

    // Initial check without violation
    const initialFs = Boolean(
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.mozFullScreenElement ||
      document.msFullscreenElement
    );
    setIsFullscreen(initialFs);
    wasFsRef.current = initialFs;
    document.addEventListener('fullscreenchange', update);
    document.addEventListener('webkitfullscreenchange', update);
    document.addEventListener('mozfullscreenchange', update);
    document.addEventListener('MSFullscreenChange', update);
    return () => {
      document.removeEventListener('fullscreenchange', update);
      document.removeEventListener('webkitfullscreenchange', update);
      document.removeEventListener('mozfullscreenchange', update);
      document.removeEventListener('MSFullscreenChange', update);
    };
  }, [candidateDetailsCompleted, submitted, assessmentStage, showAiEvent]);



  useEffect(() => {
    if (error || windowError || submitted || assessmentStage === 'loading' || assessmentStage === 'completed' || assessmentStage === 'transition') return;

    startCamera();

    let detectInterval;
    const initMonitoring = async () => {
      if (window.cocoSsd) {
        detectorRef.current = await window.cocoSsd.load();
        detectInterval = setInterval(async () => {
          if (videoRef.current && detectorRef.current && videoRef.current.readyState === 4) {
            const now = Date.now();
            if (now - lastDetectionTimeRef.current > 1500) {
              lastDetectionTimeRef.current = now;
              const preds = await detectorRef.current.detect(videoRef.current);

              // Filter by confidence score
              const phones = preds.filter(p => p.class === 'cell phone' && p.score > 0.70);
              const people = preds.filter(p => p.class === 'person' && p.score > 0.55);

              let phoneActive = phones.length > 0;

              if (phoneActive) {
                showAiEvent('PHONE DETECTED', true, 'phone_detection');
              }

              if (people.length > 1) {
                showAiEvent('MULTIPLE PEOPLE', true, 'multiface_detection');
              } else if (people.length === 0 && !phoneActive) {
                // Only trigger face lost if no phone is obscuring the view
                showAiEvent('FACE NOT DETECTED', true, 'face_detection_lost');
              }
            }
          }
        }, 800);
      }
    };
    initMonitoring();

    const handleVisibilityChange = () => {
      if (document.hidden) {
        showAiEvent('TAB SWITCHED', true, 'tab_switch');
      }
    };

    const handleBlur = () => {
      showAiEvent('WINDOW BLURRED', true, 'window_switch');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange, { capture: true });
    window.addEventListener('blur', handleBlur, { capture: true });

    // Disable Copy/Paste/Right-click (Enhanced with capture phase)
    const preventAction = (e) => {
      e.preventDefault();
      e.stopPropagation();
      showAiEvent('ACTION PROHIBITED', true);
      return false;
    };
    document.addEventListener('copy', preventAction, { capture: true });
    document.addEventListener('cut', preventAction, { capture: true });
    document.addEventListener('paste', preventAction, { capture: true });
    document.addEventListener('contextmenu', preventAction, { capture: true });

    return () => {
      clearInterval(detectInterval);
      document.removeEventListener('visibilitychange', handleVisibilityChange, { capture: true });
      window.removeEventListener('blur', handleBlur, { capture: true });
      document.removeEventListener('copy', preventAction, { capture: true });
      document.removeEventListener('cut', preventAction, { capture: true });
      document.removeEventListener('paste', preventAction, { capture: true });
      document.removeEventListener('contextmenu', preventAction, { capture: true });
      stopCamera();
    };

  }, [showAiEvent, startCamera, stopCamera, submitted, assessmentStage, error, windowError]);

  // Continuous background tracking for "Tab 1 -> Tab 2" and "Window 1 -> Window 2" switches
  useEffect(() => {
    if (error || windowError || submitted || assessmentStage === 'loading' || assessmentStage === 'completed' || assessmentStage === 'transition') return;

    const bgInterval = setInterval(() => {
      // If candidate is actively looking at our tab, do nothing
      if (!document.hidden && document.hasFocus()) return;

      // If they are hidden (different tab) or blurred (different window), capture every 5s
      const eventType = document.hidden ? 'tab_switch' : 'window_switch';
      showAiEvent('BACKGROUND ACTIVITY DETECTED', true, eventType);
    }, 5000);

    return () => clearInterval(bgInterval);
  }, [showAiEvent, submitted, assessmentStage, error, windowError]);



  useEffect(() => {
    if (submitted || submitting) return;

    // We don't want to reset the interval every second, so we DON'T include remainingSeconds in deps.
    let lastTick = Date.now();
    const t = setInterval(() => {
      const now = Date.now();
      const deltaSecs = Math.floor((now - lastTick) / 1000);
      if (deltaSecs < 1) return;
      lastTick += deltaSecs * 1000;

      // Pause global timer if in transition
      if (assessmentStage !== 'transition') {
        setRemainingSeconds((s) => {
          if (s === null) return null;
          if (s <= 0) return 0;
          return Math.max(0, s - deltaSecs);
        });
      }

      // Stage-specific timers
      if (assessmentStage === 'objective') {
        setObjectiveSeconds(prev => {
          if (prev === null) return null;
          if (prev <= 0) return 0;
          return Math.max(0, prev - deltaSecs);
        });
      } else if (assessmentStage === 'coding') {
        setCodingSeconds(prev => {
          if (prev === null) return null;
          if (prev <= 0) return 0;
          return Math.max(0, prev - deltaSecs);
        });
      }
    }, 1000);

    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submitted, assessmentStage, submitting, codingState.running]);

  // Global timeout check
  useEffect(() => {
    if (remainingSeconds !== null && remainingSeconds <= 0 && !submitted) {
      submit(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remainingSeconds, submitted]);

  // Effect to handle stage timeouts
  useEffect(() => {
    if (assessmentStage === 'objective' && objectiveSeconds !== null && objectiveSeconds <= 0) {
      // Auto submit objective
      if (!submitting) {
        submitObjective(true);
      }
    }
    if (assessmentStage === 'coding' && codingSeconds !== null && codingSeconds <= 0) {
      // Auto submit coding / finish exam
      if (!submitted) {
        submit(true);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentStage, objectiveSeconds, codingSeconds]);

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
    setResultHeightPct(50); // Expand results area upon running
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

  const submitCode = () => {
    if (!activeCoding) return;
    // Check global timer - allow submitting code as long as total time remains
    if (remainingSeconds !== null && remainingSeconds <= 0) {
      setCodingState((prev) => ({ ...prev, runError: 'Time is over. The exam has ended.' }));
      return;
    }
    executeSubmitCode();
  };

  const executeSubmitCode = async () => {
    if (!activeCoding) return;
    const key = String(activeCoding.id);
    setResultHeightPct(50); // Expand results area upon submitting
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
        runResultById: { ...prev.runResultById, [key]: normalizeRunResult(resp.data) },
        running: false,
        submittedIds: { ...prev.submittedIds, [String(activeCoding.id)]: true },
      }));
    } catch (e) {
      setCodingState((prev) => ({ ...prev, running: false, runError: e?.response?.data?.error || e?.message || 'Submit failed' }));
    }
  };

  const startCoding = () => {
    setAssessmentStage('coding');
    window.scrollTo(0, 0);
  };

  const submitObjective = async (isAutoSubmit = false) => {
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
      const resp = await axios.post(`${API_BASE_URL}/invitations/public/${token}/submit-objective/`, {
        answers: answersById,
      });
      setObjResult(resp.data);
      if (resp.data.passed === false || resp.data.next_stage === 'finish') {
        // Redirect to feedback on fail OR if no coding section (Case 1 Fix)
        navigate(`/result/${token}`, { replace: true });
      } else {
        setAssessmentStage('transition');
        // Record coding start time when transitioning (will be used once stage becomes 'coding')
        setStageStartTimes(prev => ({ ...prev, coding: Date.now() }));
      }
    } catch (e) {
      setSubmitError(e?.response?.data?.error || e?.message || 'Failed to submit objective section');
    } finally {
      setSubmitting(false);
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
    ? (resultHeightPct > 30
      ? { flex: '0 0 auto', height: 'auto', maxHeight: 'none' }
      : { flex: `0 0 ${resultHeightPct}%`, maxHeight: '30vh' })
    : { display: 'none' };

  // Show a loading state to prevent CandidateDetails flicker
  if (precheckLoading) {
    return (
      <div className="take-page">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontSize: '18px', color: '#64748b' }}>
          Loading...
        </div>
      </div>
    );
  }

  // Show already submitted popup directly if precheck catches it
  if (alreadySubmitted) {
    return (
      <div className="take-page" style={{ position: 'relative' }}>
        <div className="take-shell" style={{ opacity: 0.5, pointerEvents: 'none', background: '#f8fafc', height: '100vh', width: '100vw' }}></div>
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999 }}>
          <div style={{ background: '#fff', padding: '40px', borderRadius: '12px', textAlign: 'center', maxWidth: '400px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
            <h2 style={{ margin: '0 0 12px', color: '#1e293b' }}>Assessment Submitted</h2>
            <p style={{ color: '#64748b', margin: '0 0 24px', lineHeight: '1.5' }}>You have already submitted this assessment. You can safely close this window.</p>
            <button onClick={() => window.close()} style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '10px 24px', borderRadius: '6px', fontSize: '16px', cursor: 'pointer', fontWeight: '500' }}>Close</button>
          </div>
        </div>
      </div>
    );
  }

  // Show window error BEFORE the candidate details form
  if (windowError) {
    const isNotStarted = windowError.toLowerCase().includes('not started yet');
    const isExpired = windowError.toLowerCase().includes('expired') || windowError.toLowerCase().includes('start window');
    const isCompleted = windowError === 'ALREADY_SUBMITTED' || windowError.toLowerCase().includes('completed');
    const scheduleData = windowSchedule;
    return (
      <div className="take-page">
        <div className="take-shell">
          <div className="take-card" style={{ maxWidth: 600, margin: '60px auto', padding: '40px 36px', borderRadius: 16, background: '#fff', boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }}>
            <div style={{ textAlign: 'center', marginBottom: 28 }}>
              <span style={{ fontSize: 48 }}>
                {isNotStarted ? '⏳' : isCompleted ? '✅' : isExpired ? '⏰' : '🔒'}
              </span>
              <h2 style={{ margin: '16px 0 8px', fontSize: 22, color: '#1e293b' }}>
                {isNotStarted ? 'Your Assessment Is Scheduled' : isCompleted ? 'Assessment Submitted' : isExpired ? 'Assessment Window Closed' : 'Access Denied'}
              </h2>
              <p style={{ color: '#64748b', fontSize: 15, margin: 0 }}>{windowError === 'ALREADY_SUBMITTED' ? 'You have already submitted this assessment.' : windowError}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show candidate details form if not completed
  if (!candidateDetailsCompleted) {
    return (
      <CandidateDetails
        token={token}
        onComplete={(candidateData) => {
          setCandidateDetailsCompleted(true);
          // Signal SecuritySessionGuard to begin monitoring now that exam is starting
          window.dispatchEvent(new Event('vh_exam_started'));
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
    const isNotStarted = msg.toLowerCase().includes('not started');
    const isExpired = msg.toLowerCase().includes('start window') || msg.toLowerCase().includes('expired');

    // Detailed "Assessment is Scheduled" page
    if (isNotStarted) {
      return (
        <div className="take-page">
          <div className="take-shell">
            <div className="take-card" style={{ maxWidth: 600, margin: '60px auto', padding: '40px 36px', borderRadius: 16, background: '#fff', boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }}>
              <div style={{ textAlign: 'center', marginBottom: 28 }}>
                <span style={{ fontSize: 48 }}>⏳</span>
                <h2 style={{ margin: '16px 0 8px', fontSize: 22, color: '#1e293b' }}>Your Assessment Is Scheduled</h2>
                <p style={{ color: '#64748b', fontSize: 15, margin: 0 }}>Thank you for your interest in this opportunity.</p>
              </div>
              <p style={{ color: '#334155', fontSize: 15, lineHeight: 1.6 }}>
                The assessment is not yet active and will be available at the scheduled time below:
              </p>
              {scheduleInfo && (
                <div style={{ border: '1px solid #e5e7eb', borderRadius: 10, overflow: 'hidden', fontSize: 12, margin: '20px 0' }}>
                  <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                    <tbody>
                      {scheduleInfo.start_date && (
                        <tr>
                          <td style={{ padding: '8px 12px 8px 0', fontWeight: 600, color: '#0369a1', whiteSpace: 'nowrap' }}>📅 Date</td>
                          <td style={{ padding: '8px 0', color: '#1e293b' }}>{scheduleInfo.start_date}</td>
                        </tr>
                      )}
                      {scheduleInfo.start_time_display && (
                        <tr>
                          <td style={{ padding: '8px 12px 8px 0', fontWeight: 600, color: '#0369a1', whiteSpace: 'nowrap' }}>🕒 Time</td>
                          <td style={{ padding: '8px 0', color: '#1e293b' }}>{scheduleInfo.start_time_display}{scheduleInfo.time_zone ? ` (${scheduleInfo.time_zone})` : ''}</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
              <div style={{ margin: '24px 0' }}>
                <p style={{ fontWeight: 600, color: '#334155', marginBottom: 10 }}>Please ensure:</p>
                <ul style={{ margin: 0, paddingLeft: 20, color: '#475569', lineHeight: 2 }}>
                  <li>You have a stable internet connection</li>
                  <li>You are using a supported browser</li>
                  <li>You log in a few minutes before the start time</li>
                </ul>
              </div>
              <p style={{ color: '#64748b', fontSize: 14 }}>
                Once the exam window opens, this page will automatically allow you to begin.
              </p>
              <p style={{ color: '#94a3b8', fontSize: 13, marginTop: 20 }}>
                If you need assistance, please contact our support team.
              </p>
              <p style={{ textAlign: 'center', fontSize: 16, marginTop: 24, color: '#334155' }}>
                We wish you the best of luck! 🚀
              </p>
            </div>
          </div>
        </div>
      );
    }

    // Expired / other error pages
    const title = (() => {
      const msgLower = msg.toLowerCase();
      const isExpiredPage = msgLower.includes('expired') || msgLower.includes('window') || msgLower.includes('closed') || msgLower.includes('start window');
      if (isExpiredPage) return 'Assessment Window Closed';
      if (msg === 'ALREADY_SUBMITTED' || msgLower.includes('complete')) return 'Exam Completed';
      if (msgLower.includes('time is over')) return 'Time is over';
      return 'Invalid or expired link';
    })();
    return (
      <div className="take-page">
        <div className="take-shell">
          <div className="take-card error" style={{ maxWidth: 560, margin: '60px auto', padding: '36px 32px', borderRadius: 16 }}>
            <div style={{ textAlign: 'center', marginBottom: 16 }}>
              <span style={{ fontSize: 44 }}>{isExpired ? '⏰' : '❌'}</span>
            </div>
            <div className="take-title" style={{ textAlign: 'center' }}>{title}</div>
            <div className="take-sub" style={{ textAlign: 'center', marginTop: 8 }}>{error}</div>
            <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: 13, marginTop: 16 }}>
              If you believe this is an error, please contact the assessment administrator.
            </p>
          </div>
        </div>
      </div>
    );
  }



  return (
    <div className="take-page take-exam-mode">
      {aiToast.active && (
        <div style={{ position: 'fixed', top: 100, left: '50%', transform: 'translateX(-50%)', zIndex: 99999, background: aiToast.urgent ? '#dc2626' : '#1d4ed8', color: 'white', padding: '10px 24px', borderRadius: 25, fontWeight: 700, fontSize: '0.82rem', boxShadow: '0 6px 24px rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', gap: 8, letterSpacing: 0.5 }}>
          <span style={{ fontSize: '1rem' }}>{aiToast.urgent ? '⚠️' : 'ℹ️'}</span>
          {aiToast.text}
        </div>
      )}
      <canvas ref={screenCanvasRef} style={{ display: 'none' }} width="1280" height="720" />
      <div className="take-shell-exam">
        {!isFullscreen && !submitted ? (
          <div className="fs-gate" role="dialog" aria-label="Enter full screen">
            <div className="fs-card">
              <div className="fs-title">{assessmentStage !== 'loading' && assessmentStage !== 'objective' ? 'Resume Assessment' : 'Start Exam'}</div>
              <div className="fs-sub">Fullscreen is required to {assessmentStage !== 'loading' && assessmentStage !== 'objective' ? 'continue' : 'start'} the exam.</div>
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
        {/* Floating Timer (Stage Based) */}
        {!submitted && assessmentStage !== 'loading' && assessmentStage !== 'transition' && assessmentStage !== 'completed' && (objectiveSeconds !== null || codingSeconds !== null) ? (
          <div className={`timer-box ${getTimerStage(assessmentStage === 'objective' ? objectiveSeconds : codingSeconds)}`}>
            <div className="timer-value">
              {formatCompactTime(
                assessmentStage === 'objective' ? objectiveSeconds : codingSeconds,
                assessmentStage === 'objective' ? parseTotalSeconds(assessment?.objective_time_limit || assessment?.total_time) : parseTotalSeconds(assessment?.coding_time_limit || assessment?.coding_total_time)
              )}
            </div>
            <div className="timer-label" style={{ fontSize: '0.75rem', textAlign: 'center', opacity: 0.9 }}>
              {assessmentStage === 'objective' ? 'Objective Section' : 'Coding Section'}
            </div>
          </div>
        ) : null}

        <div className="take-header">
          <div className="take-title">{assessment?.display_name || assessment?.name || 'Assessment'}</div>
          {(!submitted && assessmentStage !== 'loading' && assessmentStage !== 'completed') && (
            <div style={{ width: 44, height: 44, borderRadius: '50%', backgroundColor: '#1e293b', overflow: 'hidden', marginLeft: 'auto', marginRight: 15, border: '2px solid #e2e8f0', flexShrink: 0 }}>
              <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
            </div>
          )}
          {!isFullscreen ? <div className="take-note" style={{ marginLeft: submitted || assessmentStage === 'loading' ? 'auto' : 0 }}><span className="fs-badge">Fullscreen required</span></div> : null}
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

            {/* Transition Stage */}
            {assessmentStage === 'transition' && (
              <div className="take-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                <h2 style={{ fontSize: '2rem', marginBottom: '20px' }}>Objective Section Completed</h2>
                <div style={{ margin: '30px auto', padding: '20px', maxWidth: '500px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                  <p style={{ margin: 0, color: '#475569', fontSize: '1.1rem', fontWeight: '500' }}>
                    You have successfully completed the objective section of the assessment.
                  </p>
                </div>
                {objResult?.passed && (
                  <div style={{ marginTop: '40px' }}>
                    <p style={{ fontSize: '1.1rem', marginBottom: '20px', color: '#4b5563' }}>
                      You are about to start the coding section.<br />
                      <strong>Coding Time Limit: {assessment?.coding_time_limit || 'As per total time'}</strong>
                    </p>
                    <button className="btn btn-primary" onClick={startCoding} style={{ fontSize: '1.2rem', padding: '12px 36px', borderRadius: '8px' }}>
                      Start Coding Section (starts in {transitionTimer})
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Coding Section */}
            {assessmentStage === 'coding' && codingQuestionsOrdered.length > 0 ? (
              <div className="take-card coding-overview-card">
                <div className="coding-header-actions" style={{ alignItems: 'center', marginBottom: 6 }}>
                  <span className="pill gray" style={{ fontSize: '10px' }}>{codingQuestionsOrdered.length} coding tasks</span>
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

            {assessmentStage === 'coding' && codingQuestionsOrdered.length > 0 && activeCoding ? (
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
                          disabled={false}
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
                      <button type="button" className="btn btn-secondary" onClick={runCode} disabled={codingState.running || loading}>
                        {codingState.running ? 'Running…' : 'Run'}
                      </button>
                      <button type="button" className="btn btn-primary" onClick={submitCode} disabled={codingState.running || loading}>
                        {codingState.running ? 'Submitting…' : (codingState.submittedIds[String(activeCoding.id)] ? 'Resubmit Answer' : 'Submit Answer')}
                      </button>
                    </div>
                  </div>

                  {codingState.runError ? (
                    <div className="coding-card coding-error" style={{ margin: '10px 12px', padding: '10px 12px' }}>
                      {codingState.runError}
                    </div>
                  ) : null}

                  <div className="coding-editor-wrap" ref={codingEditorWrapRef} onClick={() => setResultHeightPct(30)}>
                    <div className="coding-monaco">
                      <Suspense fallback={<div className="coding-monaco-loading">Loading editor…</div>}>
                        <MonacoEditor
                          key={activeCoding.id}
                          height="100%"
                          defaultLanguage={monacoLanguage(activeLanguage)}
                          language={monacoLanguage(activeLanguage)}
                          value={activeCode}
                          options={{
                            contextmenu: true,
                            fontSize: 14,
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            automaticLayout: true,
                            readOnly: false,
                            domReadOnly: false,
                            wordWrap: 'on'
                          }}
                          onChange={(v) => {
                            const value = v ?? '';
                            setCodingState((prev) => ({
                              ...prev,
                              codeById: { ...prev.codeById, [String(activeCoding.id)]: value },
                            }));
                          }}
                          theme="vs-dark"
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

            {/* Finish Assessment button for coding stage if needed (e.g. coding only or end of test) */}
            {assessmentStage === 'coding' && !submitted ? (
              <div className="take-footer">
                <button className="submit-btn" type="button" onClick={() => submit(false)} disabled={submitting}>
                  {submitting ? 'Submitting…' : 'Finish Assessment'}
                </button>
              </div>
            ) : null}

            {/* Objective Questions Exam Mode Layout */}
            {assessmentStage === 'objective' && questions.length > 0 && currentQuestion ? (
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
                        <button className="submit-btn" type="button" onClick={() => submitObjective(false)} disabled={submitting}>
                          {submitting ? 'Submitting…' : (codingQuestionsOrdered.length > 0 ? 'Submit Objective Section' : 'Submit Assessment')}
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

                  {codingQuestionsOrdered.length === 0 && (
                    <div className="sidebar-submit-section">
                      <button className="submit-btn full-width" type="button" onClick={submit} disabled={submitting}>
                        {submitting ? 'Submitting…' : 'Submit Exam'}
                      </button>
                    </div>
                  )}
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