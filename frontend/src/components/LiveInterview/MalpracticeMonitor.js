import React, { useEffect, useRef, useState } from 'react';
import { FaceDetection } from '@mediapipe/face_detection';
import * as tf from '@tensorflow/tfjs';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import axios from 'axios';
import { API_BASE_URL } from '../../apiConfig';

export const MalpracticeMonitor = ({
  sessionId,
  participantToken,
  videoRef,
  cameraReady,
  isCameraOn,
  sendMessage,
  showNotification,
  isScreenSharing // New prop to track screen sharing
}) => {
  const [mediaPipeLoaded, setMediaPipeLoaded] = useState(false);
  const faceDetectionRef = useRef(null);
  const handleFaceResultsRef = useRef(null);
  const [showFullscreenModal, setShowFullscreenModal] = useState(false);
  const [fullscreenExitCount, setFullscreenExitCount] = useState(0);

  const [cocoSsdModel, setCocoSsdModel] = useState(null);

  const noFaceStartTimeRef = useRef(null);
  const tabSwitchStartTimeRef = useRef(null);
  const extraPersonStartTimeRef = useRef(null);
  const mobilePhoneStartTimeRef = useRef(null);
  const isScreenSharingRef = useRef(isScreenSharing);

  const lastViolationTimeRef = useRef({}); // Cooldown tracker
  const recentViolationsRef = useRef({});

  // Check cooldown per violation type
  const isCooldown = (type, seconds = 10) => {
    const last = lastViolationTimeRef.current[type];
    if (!last) return false;
    return (Date.now() - last) < (seconds * 1000);
  };

  // Load Models
  useEffect(() => {
    let fd = null;
    try {
      fd = new FaceDetection({ locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
      }});
      fd.setOptions({
        model: 'short',
        minDetectionConfidence: 0.5,
      });
      fd.onResults((results) => {
        const detections = results.detections || [];
        if (handleFaceResultsRef.current) {
           handleFaceResultsRef.current(detections);
        }
      });
      faceDetectionRef.current = fd;
      setMediaPipeLoaded(true);
      console.log("✅ MediaPipe FaceDetection initialized");
    } catch (err) {
      console.error("❌ Failed to initialize MediaPipe:", err);
    }

    // Load COCO-SSD
    cocoSsd.load().then(model => {
      setCocoSsdModel(model);
      console.log("✅ COCO-SSD initialized");
    }).catch(err => {
      console.error("❌ Failed to load COCO-SSD:", err);
    });

    return () => {
      if (fd) fd.close();
    };
  }, []);

  // Screen Share Stopped Detection
  useEffect(() => {
    if (isScreenSharingRef.current && !isScreenSharing) {
      // Candidate stopped sharing
      if (!isCooldown('SCREEN_SHARE_STOPPED', 10)) {
        lastViolationTimeRef.current['SCREEN_SHARE_STOPPED'] = Date.now();
        triggerViolation('SCREEN_SHARE_STOPPED', 'HIGH', {
          message: 'Candidate stopped screen sharing'
        });
        if (showNotification) {
          showNotification("⚠️ You stopped screen sharing. Please resume sharing your screen immediately to avoid penalties.", "error");
        }
      }
    }
    isScreenSharingRef.current = isScreenSharing;
  }, [isScreenSharing]);

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
      if (!isFullscreen && !window.isScreenShareSelectionActive) {
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

  // Tab Switching Detection
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (window.isScreenShareSelectionActive) return;
      if (document.hidden) {
        if (!tabSwitchStartTimeRef.current) {
          tabSwitchStartTimeRef.current = Date.now();
        }
      } else {
        handleFocusReturn();
      }
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

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  useEffect(() => {
    handleFaceResultsRef.current = handleFaceResults;
  });

  // Run Models Every 2 Seconds
  useEffect(() => {
    if (!mediaPipeLoaded || !cameraReady || !isCameraOn) return;

    const interval = setInterval(async () => {
      if (!videoRef.current || videoRef.current.readyState !== 4 || videoRef.current.videoWidth === 0) {
        return;
      }
      
      const now = Date.now();

      // MediaPipe Face Detection
      try {
        if (faceDetectionRef.current) {
          await faceDetectionRef.current.send({ image: videoRef.current });
        }
      } catch (err) {
        console.error("FACE DETECTOR FAILURE", err);
      }

      // COCO-SSD Object Detection
      try {
        if (cocoSsdModel) {
          const predictions = await cocoSsdModel.detect(videoRef.current);
          const hasPhone = predictions.some(p => p.class === 'cell phone');

          if (hasPhone) {
            if (!mobilePhoneStartTimeRef.current) mobilePhoneStartTimeRef.current = now;
            if (now - mobilePhoneStartTimeRef.current >= 3000) {
              if (!isCooldown('MOBILE_PHONE_DETECTED', 10)) {
                lastViolationTimeRef.current['MOBILE_PHONE_DETECTED'] = now;
                triggerViolation('MOBILE_PHONE_DETECTED', 'HIGH', { message: 'Mobile phone detected in frame' });
              }
            }
          } else {
            mobilePhoneStartTimeRef.current = null;
          }
        }
      } catch (err) {
        console.error("COCO-SSD FAILURE", err);
      }

    }, 2000);

    return () => clearInterval(interval);
  }, [mediaPipeLoaded, cameraReady, isCameraOn, videoRef, cocoSsdModel]);

  const handleFaceResults = (detections) => {
    const faceCount = detections.length;
    const now = Date.now();

    if (faceCount === 0) {
      if (!noFaceStartTimeRef.current) {
        noFaceStartTimeRef.current = now;
      }
      const elapsed = now - noFaceStartTimeRef.current;
      if (elapsed >= 4000) {
        if (!isCooldown('NO_FACE', 10)) {
          lastViolationTimeRef.current['NO_FACE'] = now;
          triggerViolation('NO_FACE', 'HIGH', {
            message: 'No candidate face detected in frame for over 5 seconds.'
          });
        }
        noFaceStartTimeRef.current = null;
      }
      extraPersonStartTimeRef.current = null;
    } else {
      noFaceStartTimeRef.current = null;

      if (faceCount > 1) {
        if (!extraPersonStartTimeRef.current) extraPersonStartTimeRef.current = now;
        if (now - extraPersonStartTimeRef.current >= 3000) {
          if (!isCooldown('EXTRA_PERSON_DETECTED', 10)) {
            lastViolationTimeRef.current['EXTRA_PERSON_DETECTED'] = now;
            triggerViolation('EXTRA_PERSON_DETECTED', 'HIGH', {
              message: `Multiple persons detected in frame. Count: ${faceCount}`,
              face_count: faceCount
            });
          }
        }
      } else {
        extraPersonStartTimeRef.current = null;
      }
    }
  };

  // Capture canvas image, upload to server, and broadcast to socket
  const triggerViolation = (type, severity, details = {}, duration = 0) => {
    const now = Date.now();
    if (
      recentViolationsRef.current[type] &&
      now - recentViolationsRef.current[type] < 5000
    ) {
      console.log(`Duplicate ${type} prevented`);
      return;
    }
    recentViolationsRef.current[type] = now;

    if (showNotification && type !== 'SCREEN_SHARE_STOPPED') { // We already handled screen share stopped notification
      const label = type === 'NO_FACE' ? 'No Face Detected' :
                    type === 'EXTRA_PERSON_DETECTED' ? 'Multiple Faces Detected' :
                    type === 'MOBILE_PHONE_DETECTED' ? 'Mobile Phone Detected' :
                    type === 'TAB_SWITCH' ? 'Tab Switch Detected' : 'Fullscreen Exit Detected';
      showNotification(`⚠️ Proctoring Alert: ${label}`, severity === 'HIGH' ? 'error' : 'warning');
    }

    // Capture screenshot if required
    let screenshotBlobPromise = Promise.resolve(null);
    if (['EXTRA_PERSON_DETECTED', 'MOBILE_PHONE_DETECTED', 'NO_FACE', 'FULLSCREEN_EXIT', 'SCREEN_SHARE_STOPPED'].includes(type) && videoRef && videoRef.current) {
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
