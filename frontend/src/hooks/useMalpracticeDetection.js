import { useEffect, useRef, useState, useCallback } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';



/**
 * Hook for malpractice detection in coding assessments.
 * @param {string} token - Assessment invitation token.
 * @param {string} currentCode - Current code in the editor.
 */
export const useMalpracticeDetection = (token, currentCode) => {
  const [suspicionScore, setSuspicionScore] = useState(0);
  const [reasons, setReasons] = useState([]);
  
  const keystrokesBuffer = useRef([]);
  const behaviorBuffer = useRef([]);
  const lastKeystrokeTime = useRef(Date.now());
  const batchInterval = useRef(null);
  const snapshotInterval = useRef(null);
  
  const totalCharacters = useRef(0);
  const backspaceCount = useRef(0);

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

    // Security: Block certain shortcuts
    if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'v' || e.key === 'x')) {
      e.preventDefault();
      behaviorBuffer.current.push({
        type: 'blocked_shortcut',
        value: `Ctrl+${e.key.toUpperCase()}`,
        timestamp: new Date().toISOString()
      });
      return false;
    }
  }, []);

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

  // --- 3. Security Restrictions ---
  const blockContextMenu = (e) => e.preventDefault();
  const blockCopyPaste = (e) => {
    e.preventDefault();
    behaviorBuffer.current.push({
        type: 'blocked_action',
        value: 'Copy/Paste attempted',
        timestamp: new Date().toISOString()
    });
  };

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

  // --- 5. Batch Sending ---
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

    // Clear buffers before sending to avoid duplicates if request takes long
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

  // --- 6. Code Snapshots ---
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
    window.addEventListener('contextmenu', blockContextMenu, { capture: true });
    window.addEventListener('copy', blockCopyPaste, { capture: true });
    window.addEventListener('paste', blockCopyPaste, { capture: true });
    window.addEventListener('cut', blockCopyPaste, { capture: true });
    document.addEventListener('fullscreenchange', handleFullscreenChange, { capture: true });

    batchInterval.current = setInterval(sendBatch, 7000); // Every 7 seconds

    return () => {
      window.removeEventListener('keydown', handleKeyDown, { capture: true });
      document.removeEventListener('visibilitychange', handleVisibilityChange, { capture: true });
      window.removeEventListener('blur', handleBlur, { capture: true });
      window.removeEventListener('focus', handleFocus, { capture: true });
      window.removeEventListener('contextmenu', blockContextMenu, { capture: true });
      window.removeEventListener('copy', blockCopyPaste, { capture: true });
      window.removeEventListener('paste', blockCopyPaste, { capture: true });
      window.removeEventListener('cut', blockCopyPaste, { capture: true });
      document.removeEventListener('fullscreenchange', handleFullscreenChange, { capture: true });
      clearInterval(batchInterval.current);

      if (snapshotInterval.current) clearInterval(snapshotInterval.current);
      
      // Send final batch on unmount
      sendBatch();
    };
  }, [handleKeyDown, handleVisibilityChange, handleBlur, handleFocus, sendBatch, handleFullscreenChange]);


  return { suspicionScore, reasons, requestFullscreen };
};

