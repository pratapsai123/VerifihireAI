import React, { useEffect, useRef, useState } from 'react';
import * as faceapi from 'face-api.js';
import axios from 'axios';
import { API_BASE_URL } from '../../apiConfig';

export const MalpracticeMonitor = ({
  sessionId,
  participantToken,
  videoRef,
  cameraReady,
  isCameraOn,
  sendMessage,
  showNotification
}) => {
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [showFullscreenModal, setShowFullscreenModal] = useState(false);
  const [fullscreenExitCount, setFullscreenExitCount] = useState(0);

  const lastFaceTimeRef = useRef(Date.now());
  const noFaceViolationLoggedRef = useRef(false);
  const tabSwitchStartTimeRef = useRef(null);
  const lastViolationTimeRef = useRef({}); // Cooldown tracker

  // Check cooldown per violation type
  const isCooldown = (type, seconds = 10) => {
    const last = lastViolationTimeRef.current[type];
    if (!last) return false;
    return (Date.now() - last) < (seconds * 1000);
  };

  // Load face-api.js models from local public folder
  useEffect(() => {
    const loadModels = async () => {
      try {
        // Load Tiny Face Detector from /models (public directory)
        await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
        setModelsLoaded(true);
        console.log("✅ face-api.js models loaded successfully from local public folder");
      } catch (err) {
        console.error("❌ Failed to load face-api.js models:", err);
      }
    };
    loadModels();
  }, []);

  // Enter Fullscreen on Start
  useEffect(() => {
    const startInterviewEvent = () => {
      // Prompt candidate to enter fullscreen
      setShowFullscreenModal(true);
    };

    window.addEventListener('vh_exam_started', startInterviewEvent);
    // Also trigger immediately if already active
    if (!showFullscreenModal && document.fullscreenElement === null) {
      setShowFullscreenModal(true);
    }

    return () => {
      window.removeEventListener('vh_exam_started', startInterviewEvent);
    };
  }, []);

  // Fullscreen Exit Detection
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isFullscreen = document.fullscreenElement !== null;
      if (!isFullscreen) {
        setShowFullscreenModal(true);

        if (!isCooldown('FULLSCREEN_EXIT', 8)) {
          lastViolationTimeRef.current['FULLSCREEN_EXIT'] = Date.now();
          setFullscreenExitCount(prev => {
            const newCount = prev + 1;
            triggerViolation('FULLSCREEN_EXIT', 'MEDIUM', {
              message: `Exited fullscreen mode. Total exits: ${newCount}`
            });
            return newCount;
          });
        }
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Tab Switching & Window Blur Detection
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        if (!tabSwitchStartTimeRef.current) {
          tabSwitchStartTimeRef.current = Date.now();
        }
      } else {
        handleFocusReturn();
      }
    };

    const handleBlur = () => {
      if (!tabSwitchStartTimeRef.current) {
        tabSwitchStartTimeRef.current = Date.now();
      }
    };

    const handleFocus = () => {
      handleFocusReturn();
    };

    const handleFocusReturn = () => {
      if (tabSwitchStartTimeRef.current) {
        const start = tabSwitchStartTimeRef.current;
        tabSwitchStartTimeRef.current = null;
        const duration = Math.round((Date.now() - start) / 1000);

        // Save tab switch violation if duration > 0 and not on immediate layout shift
        if (duration >= 1 && !isCooldown('TAB_SWITCH', 5)) {
          lastViolationTimeRef.current['TAB_SWITCH'] = Date.now();
          triggerViolation('TAB_SWITCH', 'MEDIUM', {
            message: `Switched tabs or minimized browser.`,
            start_time: new Date(start).toLocaleTimeString(),
            return_time: new Date().toLocaleTimeString()
          }, duration);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  // Run Face Detection Every 2 Seconds
  useEffect(() => {
    if (!modelsLoaded || !cameraReady || !isCameraOn || !videoRef || !videoRef.current) return;

    const interval = setInterval(async () => {
      if (videoRef.current && videoRef.current.readyState === 4) {
        try {
          const options = new faceapi.TinyFaceDetectorOptions({ inputSize: 160, scoreThreshold: 0.5 });
          const detections = await faceapi.detectAllFaces(videoRef.current, options);
          handleFaceResults(detections);
        } catch (e) {
          console.error("Face detection error:", e);
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [modelsLoaded, cameraReady, isCameraOn, videoRef]);

  const handleFaceResults = (detections) => {
    const faceCount = detections.length;
    const now = Date.now();

    if (faceCount > 0) {
      lastFaceTimeRef.current = now;
      noFaceViolationLoggedRef.current = false;
    }

    if (faceCount === 0) {
      const timeSinceLastFace = now - lastFaceTimeRef.current;
      if (timeSinceLastFace >= 5000 && !noFaceViolationLoggedRef.current && !isCooldown('NO_FACE', 10)) {
        lastViolationTimeRef.current['NO_FACE'] = now;
        noFaceViolationLoggedRef.current = true;
        triggerViolation('NO_FACE', 'HIGH', {
          message: 'No candidate face detected in frame for over 5 seconds.'
        });
      }
    } else if (faceCount > 1) {
      if (!isCooldown('MULTIPLE_FACES', 10)) {
        lastViolationTimeRef.current['MULTIPLE_FACES'] = now;
        triggerViolation('MULTIPLE_FACES', 'HIGH', {
          message: `Multiple faces detected in frame. Count: ${faceCount}`,
          face_count: faceCount
        });
      }
    }
  };

  // Capture canvas image, upload to server, and broadcast to socket
  const triggerViolation = (type, severity, details = {}, duration = 0) => {
    if (showNotification) {
      const label = type === 'NO_FACE' ? 'No Face Detected' :
                    type === 'MULTIPLE_FACES' ? 'Multiple Faces Detected' :
                    type === 'TAB_SWITCH' ? 'Tab Switch Detected' : 'Fullscreen Exit Detected';
      showNotification(`⚠️ proctoring Alert: ${label}`, severity === 'HIGH' ? 'error' : 'warning');
    }

    // Capture screenshot if required (Multiple Faces, No Face, Fullscreen Exit)
    let screenshotBlobPromise = Promise.resolve(null);
    if (['MULTIPLE_FACES', 'NO_FACE', 'FULLSCREEN_EXIT'].includes(type) && videoRef && videoRef.current) {
      screenshotBlobPromise = new Promise((resolve) => {
        try {
          const video = videoRef.current;
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth || 640;
          canvas.height = video.videoHeight || 360;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.8);
        } catch (e) {
          console.error("Screenshot capture failed:", e);
          resolve(null);
        }
      });
    }

    screenshotBlobPromise.then((blob) => {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('violation_type', type);
      formData.append('severity', severity);
      formData.append('duration', duration);
      formData.append('details', JSON.stringify(details));
      if (blob) {
        formData.append('screenshot', blob, `${type.toLowerCase()}_violation.jpg`);
      }

      axios.post(`${API_BASE_URL}/interviews/violations/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      .then((res) => {
        const responseData = res.data;
        // Broadcast via WebSocket
        sendMessage({
          type: 'violation',
          violation_type: type,
          severity: severity,
          timestamp: responseData.timestamp || new Date().toISOString(),
          details: details,
          duration: duration,
          screenshot_url: responseData.screenshot_path
        });
      })
      .catch((err) => {
        console.error("Failed to log violation to server:", err);
      });
    });
  };

  const requestEnterFullscreen = () => {
    const element = document.documentElement;
    const requestMethod = element.requestFullscreen ||
                          element.webkitRequestFullscreen ||
                          element.mozRequestFullScreen ||
                          element.msRequestFullscreen;

    if (requestMethod) {
      requestMethod.call(element)
        .then(() => {
          setShowFullscreenModal(false);
        })
        .catch((err) => {
          console.error("Failed to enter fullscreen:", err);
          if (showNotification) {
            showNotification("Please enable fullscreen to proceed.", "error");
          }
        });
    } else {
      setShowFullscreenModal(false);
    }
  };

  return (
    <>
      {showFullscreenModal && (
        <div className="fullscreen-warning-overlay">
          <div className="fullscreen-warning-modal">
            <div className="warning-icon-wrapper">
              <i className="fas fa-expand warning-pulse-icon"></i>
            </div>
            <h2>Fullscreen Mode Required</h2>
            <p>
              To maintain the integrity of this interview, you must operate in fullscreen mode.
              Please click below to continue.
            </p>
            <button className="btn-return-fullscreen" onClick={requestEnterFullscreen}>
              Return to Fullscreen
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default MalpracticeMonitor;
