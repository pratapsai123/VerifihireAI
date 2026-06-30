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
    if (!allowCopyPaste) {
      e.preventDefault();
      behaviorBuffer.current.push({
        type: 'blocked_action',
        value: 'Paste attempted',
        timestamp: new Date().toISOString()
      });
      return;
    }

    const now = Date.now();
    if (now - lastPasteTimeRef.current < 200) return; // Prevent duplicate logs for the same paste

    let pastedText = '';
    try {
      pastedText = e.clipboardData.getData('text') || '';
    } catch (err) {
      console.warn('Could not read clipboard data', err);
    }

    if (pastedText) {
      lastPasteTimeRef.current = now;
      const length = pastedText.length;
      behaviorBuffer.current.push({
        type: 'paste',
        value: `Pasted ${length} characters`,
        timestamp: new Date(now).toISOString()
      });

      // Simulate a burst of keystrokes to trigger the backend's >80 char burst threshold
      const simulatedCount = Math.min(length, 500); // Prevent overflow but satisfy burst threshold (>80)
      for (let i = 0; i < simulatedCount; i++) {
        keystrokesBuffer.current.push({
          key: 'p',
          timestamp: new Date(now).toISOString(),
          time_diff: 0,
        });
      }
      totalCharacters.current += length;
      console.log(`[Malpractice Hook] Paste event captured: ${length} characters. Pushed simulated events.`);
    }
  }, [allowCopyPaste]);

  // Monitor code changes directly to detect any copy-pastes (e.g. drag & drop, context menu)
  useEffect(() => {
    if (activeQuestionId !== prevQuestionIdRef.current) {
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

    // If change is large enough, treat it as bulk injection
    if (diff > 25) {
      if (now - lastPasteTimeRef.current < 200) return; // Already handled by paste event listener
      lastPasteTimeRef.current = now;

      behaviorBuffer.current.push({
        type: 'paste',
        value: `Pasted ${diff} characters (detected via code change)`,
        timestamp: new Date(now).toISOString()
      });

      const simulatedCount = Math.min(diff, 500);
      for (let i = 0; i < simulatedCount; i++) {
        keystrokesBuffer.current.push({
          key: 'p',
          timestamp: new Date(now).toISOString(),
          time_diff: 0,
        });
      }
      totalCharacters.current += diff;
      console.log(`[Malpractice Hook] Paste detected via code change: ${diff} characters. Pushed simulated events.`);
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

