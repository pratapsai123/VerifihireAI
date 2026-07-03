import { useEffect, useRef, useState, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';



/**
 * Hook for malpractice detection in coding assessments.
 * @param {string} token - Assessment invitation token.
 * @param {string} currentCode - Current code in the editor.
 */
export const useMalpracticeDetection = (token, currentCode, options = {}) => {
  const { allowCopyPaste = false, activeQuestionId = null } = options;
  const [suspicionScore, setSuspicionScore] = useState(0);
  const [reasons, setReasons] = useState([]);

  const keystrokesBuffer = useRef([]);
  const behaviorBuffer = useRef([]);
  const lastKeystrokeTime = useRef(Date.now());
  const batchInterval = useRef(null);
  const snapshotInterval = useRef(null);

  const totalCharacters = useRef(0);
  const backspaceCount = useRef(0);

  const lastPasteTimeRef = useRef(0);
  const prevCodeRef = useRef(currentCode || '');
  const prevQuestionIdRef = useRef(activeQuestionId);

  // --- 1. Keystroke Tracking ---
  const handleKeyDown = useCallback((e) => {
    const now = Date.now();
    const timeDiff = now - lastKeystrokeTime.current;
    lastKeystrokeTime.current = now;

    const event = {
      key: e.key,
      timestamp: new Date(now).toISOString(),
      time_diff: timeDiff,
    };

    keystrokesBuffer.current.push(event);
    totalCharacters.current += 1;
    if (e.key === 'Backspace') backspaceCount.current += 1;

    // Security: Block certain shortcuts (Ctrl+C, Ctrl+X, or Ctrl+V if not allowed)
    const isCopyPasteShortcut = (e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'v' || e.key === 'x');
    if (isCopyPasteShortcut && !allowCopyPaste) {
      e.preventDefault();
      behaviorBuffer.current.push({
        type: 'blocked_shortcut',
        value: `Ctrl+${e.key.toUpperCase()}`,
        timestamp: new Date().toISOString()
      });
      return false;
    }
  }, [allowCopyPaste]);

  // --- 2. Focus & Tab Monitoring ---
  const handleVisibilityChange = useCallback(() => {
    if (document.hidden) {
      behaviorBuffer.current.push({
        type: 'tab_switch',
        value: 'Tab Hidden',
        timestamp: new Date().toISOString()
      });
    } else {
      behaviorBuffer.current.push({
        type: 'tab_switch',
        value: 'Tab Focused',
        timestamp: new Date().toISOString()
      });
    }
  }, []);

  const handleBlur = useCallback(() => {
    if (document.hidden) return;
    behaviorBuffer.current.push({
      type: 'window_blur',
      value: 'Window lost focus',
      timestamp: new Date().toISOString()
    });
  }, []);

  const handleFocus = useCallback(() => {
    behaviorBuffer.current.push({
      type: 'window_focus',
      value: 'Window focused',
      timestamp: new Date().toISOString()
    });
  }, []);

  // --- 3. Security Restrictions & Copy/Paste/Cut Detection ---
  const blockContextMenu = (e) => e.preventDefault();

  const blockCopyCut = (e) => {
    e.preventDefault();
    behaviorBuffer.current.push({
      type: 'blocked_action',
      value: `${e.type.charAt(0).toUpperCase() + e.type.slice(1)} attempted`,
      timestamp: new Date().toISOString()
    });
  };

  const handlePaste = useCallback((e) => {
    const now = Date.now();

    if (!allowCopyPaste) {
      // Block paste AND log the attempt
      e.preventDefault();
      behaviorBuffer.current.push({
        type: 'blocked_action',
        value: 'Paste attempted (blocked)',
        timestamp: new Date(now).toISOString()
      });
      return;
    }

    // allowCopyPaste=true: paste is ALLOWED but must still be LOGGED for the report
    if (now - lastPasteTimeRef.current < 200) return; // Debounce duplicate events

    let pastedText = '';
    try {
      pastedText = (e.clipboardData || window.clipboardData)?.getData('text') || '';
    } catch (err) {
      console.warn('[Malpractice] Could not read clipboard data', err);
    }

    if (!pastedText) return;

    lastPasteTimeRef.current = now;
    const length = pastedText.length;

    // Always log paste event for the behavioral report
    behaviorBuffer.current.push({
      type: 'paste',
      value: `Pasted ${length} characters (allowed)`,
      timestamp: new Date(now).toISOString()
    });

    // Push simulated keystroke events to trigger backend burst threshold (>80 per batch)
    // This is what makes the report show 'Bulk injection detected'
    const simulatedCount = Math.min(length, 500);
    for (let i = 0; i < simulatedCount; i++) {
      keystrokesBuffer.current.push({
        key: 'PASTE',
        timestamp: new Date(now).toISOString(),
        time_diff: 0,
      });
    }
    totalCharacters.current += length;
    console.log(`[Malpractice] Paste ALLOWED & LOGGED: ${length} chars. Simulated ${simulatedCount} burst events.`);
  }, [allowCopyPaste]);

  // Monitor code changes to detect Monaco editor pastes (drag-drop, context menu, Ctrl+V in Monaco)
  // Monaco Editor handles paste INTERNALLY and does NOT fire window 'paste' events.
  // This is the PRIMARY detection mechanism for coding editor bulk injections.
  useEffect(() => {
    if (activeQuestionId !== prevQuestionIdRef.current) {
      // Question changed — reset baseline, do not flag
      prevQuestionIdRef.current = activeQuestionId;
      prevCodeRef.current = currentCode || '';
      return;
    }

    const prev = prevCodeRef.current;
    const curr = currentCode || '';
    prevCodeRef.current = curr;

    if (prev === curr) return;

    const diff = curr.length - prev.length;
    const now = Date.now();

    // Threshold: >25 chars added in one React state update = bulk injection
    // (Normal typing adds 1 char per keystroke)
    if (diff > 25) {
      // Skip if already captured by the paste event listener (within 300ms)
      if (now - lastPasteTimeRef.current < 300) return;
      lastPasteTimeRef.current = now;

      behaviorBuffer.current.push({
        type: 'paste',
        value: `Bulk injection: +${diff} characters via Monaco editor`,
        timestamp: new Date(now).toISOString()
      });

      // Push simulated events to satisfy backend burst threshold (>80 per batch = 1 burst)
      const simulatedCount = Math.min(diff, 500);
      for (let i = 0; i < simulatedCount; i++) {
        keystrokesBuffer.current.push({
          key: 'PASTE',
          timestamp: new Date(now).toISOString(),
          time_diff: 0,
        });
      }
      totalCharacters.current += diff;
      console.log(`[Malpractice] Monaco bulk injection detected: +${diff} chars. Burst events: ${simulatedCount}.`);
    }
  }, [currentCode, activeQuestionId]);

  // --- 4. Fullscreen Enforcement ---
  const requestFullscreen = useCallback(() => {
    const element = document.documentElement;
    if (element.requestFullscreen) {
      element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
      element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) {
      element.msRequestFullscreen();
    }
  }, []);

  const handleFullscreenChange = useCallback(() => {
    if (!document.fullscreenElement) {
      behaviorBuffer.current.push({
        type: 'exit_fullscreen',
        value: 'Candidate exited fullscreen mode',
        timestamp: new Date().toISOString()
      });
    }
  }, []);

  // --- 5. DevTools Detection (Simple) ---
  useEffect(() => {
    const threshold = 160;
    const checkDevTools = () => {
      if (window.outerWidth - window.innerWidth > threshold ||
        window.outerHeight - window.innerHeight > threshold) {
        behaviorBuffer.current.push({
          type: 'devtools_detection',
          value: 'Possible DevTools open',
          timestamp: new Date().toISOString()
        });
      }
    };
    const interval = setInterval(checkDevTools, 5000);
    return () => clearInterval(interval);
  }, []);

  // --- 6. Batch Sending ---
  const sendBatch = useCallback(async () => {
    if (keystrokesBuffer.current.length === 0 && behaviorBuffer.current.length === 0) return;

    const payload = {
      token,
      keystrokes: [...keystrokesBuffer.current],
      behavior: [...behaviorBuffer.current],
      metadata: {
        totalCharacters: totalCharacters.current,
        backspaceRatio: totalCharacters.current > 0 ? backspaceCount.current / totalCharacters.current : 0
      }
    };

    keystrokesBuffer.current = [];
    behaviorBuffer.current = [];

    try {
      const response = await axios.post(`${API_BASE_URL}/track-events/`, payload);
      if (response.data.suspicion_score !== undefined) {
        setSuspicionScore(response.data.suspicion_score);
        setReasons(response.data.reasons || []);
      }
    } catch (err) {
      console.error('Failed to send malpractice events', err);
    }
  }, [token]);

  // --- 7. Code Snapshots ---
  useEffect(() => {
    snapshotInterval.current = setInterval(() => {
      if (currentCode) {
        behaviorBuffer.current.push({
          type: 'code_snapshot',
          value: currentCode,
          timestamp: new Date().toISOString()
        });
      }
    }, 10000); // 10 seconds
    return () => clearInterval(snapshotInterval.current);
  }, [currentCode]);

  // Setup listeners
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown, { capture: true });
    document.addEventListener('visibilitychange', handleVisibilityChange, { capture: true });
    window.addEventListener('blur', handleBlur, { capture: true });
    window.addEventListener('focus', handleFocus, { capture: true });
    window.addEventListener('paste', handlePaste, { capture: true });

    if (!allowCopyPaste) {
      window.addEventListener('contextmenu', blockContextMenu, { capture: true });
      window.addEventListener('copy', blockCopyCut, { capture: true });
      window.addEventListener('cut', blockCopyCut, { capture: true });
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange, { capture: true });

    batchInterval.current = setInterval(sendBatch, 7000); // Every 7 seconds

    return () => {
      window.removeEventListener('keydown', handleKeyDown, { capture: true });
      document.removeEventListener('visibilitychange', handleVisibilityChange, { capture: true });
      window.removeEventListener('blur', handleBlur, { capture: true });
      window.removeEventListener('focus', handleFocus, { capture: true });
      window.removeEventListener('paste', handlePaste, { capture: true });

      if (!allowCopyPaste) {
        window.removeEventListener('contextmenu', blockContextMenu, { capture: true });
        window.removeEventListener('copy', blockCopyCut, { capture: true });
        window.removeEventListener('cut', blockCopyCut, { capture: true });
      }

      document.removeEventListener('fullscreenchange', handleFullscreenChange, { capture: true });
      clearInterval(batchInterval.current);

      if (snapshotInterval.current) clearInterval(snapshotInterval.current);

      sendBatch();
    };
  }, [handleKeyDown, handleVisibilityChange, handleBlur, handleFocus, handlePaste, sendBatch, handleFullscreenChange, allowCopyPaste]);

  return { suspicionScore, reasons, requestFullscreen };
};

