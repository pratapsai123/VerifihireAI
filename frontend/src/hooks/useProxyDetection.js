import { useState, useCallback, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../apiConfig';

export const useProxyDetection = (sessionId, cameraReady, isCameraOn, sendMessage) => {
  const [violationCount, setViolationCount] = useState(() => {
    const saved = sessionStorage.getItem(`violation_count_${sessionId}`);
    return saved ? parseInt(saved, 10) : 0;
  });
  const violationLimit = 4;
  const [isDetectionPaused, setIsDetectionPaused] = useState(false);
  
  const streamIntervalRef = useRef(null);
  const pauseTimeoutRef = useRef(null);
  const lastPersonDetectedTimeRef = useRef(Date.now());
  const noPersonPopupShownRef = useRef(false);

  // We need a ref to the thumbnail video to capture frames
  const thumbnailVideoRef = useRef(null);
  
  // Reuse the same canvas instead of creating a new one every frame
  const canvasRef = useRef(null);

  const registerViolation = useCallback((reason, showPopup, endInterviewCallback) => {
    const newCount = violationCount + 1;
    setViolationCount(newCount);
    sessionStorage.setItem(`violation_count_${sessionId}`, newCount.toString());

    sendMessage({
      type: 'proxy_violation',
      violation_type: reason,
      violation_count: newCount,
      violation_limit: violationLimit
    });

    if (newCount >= violationLimit) {
      if (showPopup) showPopup('❌ Maximum warnings reached. Interview is ending.');
      if (endInterviewCallback) endInterviewCallback();
    } else {
      if (showPopup) showPopup(`⚠️ Warning ${newCount}/${violationLimit}: ${reason}`);
      pauseDetection();
    }
  }, [violationCount, violationLimit, sessionId, sendMessage]);

  const pauseDetection = useCallback(() => {
    if (isDetectionPaused) return;
    setIsDetectionPaused(true);
    stopDetection();

    if (pauseTimeoutRef.current) clearTimeout(pauseTimeoutRef.current);
    pauseTimeoutRef.current = setTimeout(() => {
      setIsDetectionPaused(false);
    }, 7000);
  }, [isDetectionPaused]);

  const sendFrame = useCallback((showPopup, endInterviewCallback) => {
    if (!cameraReady || !isCameraOn || isDetectionPaused || !thumbnailVideoRef.current) return;

    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }

    const canvas = canvasRef.current;
    canvas.width = thumbnailVideoRef.current.videoWidth || 640;
    canvas.height = thumbnailVideoRef.current.videoHeight || 360;

    if (canvas.width === 0 || canvas.height === 0) return;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(thumbnailVideoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(blob => {
      if (!blob) return;
      const formData = new FormData();
      formData.append('image', blob, 'frame.jpg');

      fetch(`${API_BASE_URL}/video_stream/`, {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          const persons = data.persons || 0;
          const gadgets = data.gadgets || [];
          const now = Date.now();

          if (persons > 0) {
            lastPersonDetectedTimeRef.current = now;
            noPersonPopupShownRef.current = false;
          }

          const timeSincePerson = now - lastPersonDetectedTimeRef.current;
          if (persons === 0 && timeSincePerson >= 10000 && !noPersonPopupShownRef.current) {
            registerViolation('No participant detected for 10 seconds. Please stay in frame.', showPopup, endInterviewCallback);
            noPersonPopupShownRef.current = true;
          }

          if (persons > 1) {
            registerViolation('Multiple people detected', showPopup, endInterviewCallback);
          }

          if (gadgets.length > 0) {
            registerViolation('Electronic device detected: ' + gadgets.join(', '), showPopup, endInterviewCallback);
          }
        }
      })
      .catch(err => console.error('Proxy detection error:', err));
    }, 'image/jpeg', 0.8);
  }, [cameraReady, isCameraOn, isDetectionPaused, registerViolation]);

  const startDetection = useCallback((showPopup, endInterviewCallback) => {
    if (streamIntervalRef.current || isDetectionPaused || !cameraReady || !isCameraOn) return;
    streamIntervalRef.current = setInterval(() => {
      sendFrame(showPopup, endInterviewCallback);
    }, 1000);
  }, [isDetectionPaused, cameraReady, isCameraOn, sendFrame]);

  const stopDetection = useCallback(() => {
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      stopDetection();
      if (pauseTimeoutRef.current) clearTimeout(pauseTimeoutRef.current);
    };
  }, [stopDetection]);

  return {
    thumbnailVideoRef,
    violationCount,
    violationLimit,
    startDetection,
    stopDetection,
    pauseDetection
  };
};

export default useProxyDetection;
