import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import Tesseract from 'tesseract.js';
import { FaceDetection } from '@mediapipe/face_detection';
import axios from 'axios';
import '../styles/CandidateDetails.css';
import { API_BASE_URL } from '../apiConfig';

// Validation rules
const validateField = (field, value) => {
  switch (field) {
    case "email":
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    case "phone":
      return /^[6-9][0-9]{9}$/.test(value);
    case "pan":
      return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value);
    default:
      return value.trim() !== "";
  }
};

const FloatingInput = ({ label, value, onChange, errorEmpty, type = "text", field, readOnly = false, required = true }) => {
  const hasValue = String(value || '').trim().length > 0;
  const formatValid = hasValue ? validateField(field, value) : true;

  const showRedBorder = errorEmpty || !formatValid;

  return (
    <div className="candidate-input-group">
      <div className="candidate-label-row">
        <label className="candidate-static-label" style={{ marginBottom: 0 }}>
          {label} {required && <span style={{ color: '#1d4ed8', marginLeft: '2px' }}>*</span>}
        </label>
      </div>
      <input
        type={type}
        value={value}
        placeholder={label}
        maxLength={
          field === "pan" ? 10 :
            (field === "firstName" || field === "lastName" || field === "email") ? 50 : undefined
        }
        onChange={(e) => {
          let val = e.target.value;

          if (field === "firstName" || field === "lastName") {
            val = val.replace(/[^a-zA-Z]/g, '');
          } else if (field === "phone") {
            val = val.replace(/[^0-9]/g, "").slice(0, 10);
            // Block first digit if not 6-9
            if (val.length > 0 && !/^[6-9]/.test(val)) {
              val = '';
            }
          } else if (field === "pan") {
            val = val.toUpperCase();

            if (val.length <= 5) {
              val = val.replace(/[^A-Z]/g, "");
            } else if (val.length <= 9) {
              const prefix = val.slice(0, 5).replace(/[^A-Z]/g, "");
              const numbers = val.slice(5).replace(/[^0-9]/g, "").slice(0, 4);
              val = prefix + numbers;
            } else {
              const prefix = val.slice(0, 5).replace(/[^A-Z]/g, "");
              const numbers = val.slice(5, 9).replace(/[^0-9]/g, "");
              const last = val.slice(9, 10).replace(/[^A-Z]/g, "");
              val = (prefix + numbers + last).slice(0, 10);
            }
          }

          onChange(val);
        }}
        readOnly={readOnly}
        className={`candidate-input ${showRedBorder ? 'candidate-input-error' : ''} ${readOnly ? 'read-only' : ''}`}
      />
    </div>
  );
};

// Function to detect blur in image using Laplacian variance
const detectBlur = (imageData) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const img = new Image();

  return new Promise((resolve) => {
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      const imageDataObj = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageDataObj.data;

      // Convert to grayscale and calculate Laplacian variance
      let sum = 0;
      let sumSquared = 0;
      const width = canvas.width;
      const height = canvas.height;

      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          const idx = (y * width + x) * 4;
          const gray = (data[idx] + data[idx + 1] + data[idx + 2]) / 3;

          // Laplacian kernel
          const laplacian = Math.abs(
            gray * 4 -
            (data[((y - 1) * width + x) * 4] + data[((y + 1) * width + x) * 4] +
              data[(y * width + x - 1) * 4] + data[(y * width + x + 1) * 4]) / 3
          );

          sum += laplacian;
          sumSquared += laplacian * laplacian;
        }
      }

      const mean = sum / ((width - 2) * (height - 2));
      const variance = (sumSquared / ((width - 2) * (height - 2))) - (mean * mean);

      // Threshold: values below 100 are considered blurry
      resolve(variance > 100);
    };
    img.src = imageData;
  });
};

const calculateBrightness = (data) => {
  let sum = 0;
  for (let i = 0; i < data.length; i += 4) {
    sum += (data[i] + data[i + 1] + data[i + 2]) / 3; // Average of R, G, B
  }
  return sum / (data.length / 4);
};

// Function to detect face in image using MediaPipe
const detectFace = async (imageSrc) => {
  return new Promise((resolve) => {
    const faceDetection = new FaceDetection({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
      }
    });

    faceDetection.setOptions({
      model: 'short',
      minDetectionConfidence: 0.5
    });

    faceDetection.onResults((results) => {
      try {
        resolve(results.detections && results.detections.length > 0);
      } catch (err) {
        console.warn('Face detection error:', err);
        resolve(false);
      }
    });

    const img = new Image();
    img.onload = () => {
      faceDetection.send({ image: img });
    };
    img.onerror = () => {
      resolve(false);
    };
    img.src = imageSrc;
  });
};

// Helper to process image (rotate, contrast, etc.)
const processImage = (file, rotation = 0, strategy = 'Standard') => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // Handle rotation dimensions
      if (rotation === 90 || rotation === 270) {
        canvas.width = img.height;
        canvas.height = img.width;
      } else {
        canvas.width = img.width;
        canvas.height = img.height;
      }

      // Rotate context
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate((rotation * Math.PI) / 180);
      ctx.drawImage(img, -img.width / 2, -img.height / 2);

      // Get image data for pixel manipulation
      // We need to reset transform to get data from the whole canvas
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;

      // Apply strategies
      if (strategy === 'HighContrast') {
        // Simple high contrast / thresholding
        for (let i = 0; i < data.length; i += 4) {
          const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
          const val = avg > 128 ? 255 : 0; // Binary threshold
          data[i] = val;     // R
          data[i + 1] = val; // G
          data[i + 2] = val; // B
        }
      } else if (strategy === 'Denoised') {
        // Simple Grayscale + slight contrast increase (mimicking denoise for OCR)
        for (let i = 0; i < data.length; i += 4) {
          const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
          // Increase contrast slightly
          const contrast = 1.2;
          const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
          const val = factor * (avg - 128) + 128;

          data[i] = val;
          data[i + 1] = val;
          data[i + 2] = val;
        }
      }

      ctx.putImageData(imageData, 0, 0);
      resolve(canvas.toDataURL('image/jpeg'));
    };
    img.src = URL.createObjectURL(file);
  });
};

// Enhanced PAN Extraction Logic
const extractPanFromImage = async (file, updateStatus) => {
  const strategies = ['Standard'];
  const rotations = [0, 90, 180, 270];

  // PAN format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
  const panPattern = /[A-Z]{5}[0-9]{4}[A-Z]{1}/;

  for (const strategy of strategies) {
    for (const rotation of rotations) {
      // Silent rotation attempts
      try {
        const processedImageSrc = await processImage(file, rotation, strategy);

        const { data: { text } } = await Tesseract.recognize(processedImageSrc, 'eng', {
          // logger: (m) => console.log(m) // Quiet logs
        });

        // Check for exact match
        const matches = text.match(panPattern); // Use local regex without 'g' to find first match easily
        if (matches) {
          console.log(`PAN Found with ${strategy} at ${rotation}°:`, matches[0]);
          return matches[0].toUpperCase();
        }

        // Check for 10-char alphanumeric sequences and loose match
        const words = text.replace(/[^A-Z0-9]/g, ' '); // Replace non-alphanum with space
        const candidates = words.split(/\s+/);

        for (const word of candidates) {
          if (word.length === 10 && /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(word)) {
            console.log(`PAN Found (loose match) with ${strategy} at ${rotation}°:`, word);
            return word.toUpperCase();
          }
        }

      } catch (err) {
        console.warn(`Extraction failed for ${strategy}/${rotation}:`, err);
      }
    }
  }

  return null;
};

const CandidateDetails = ({ token, onComplete }) => {
  const webcamRef = useRef(null);
  const [snapshot, setSnapshot] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [showError, setShowError] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const [isBlurry, setIsBlurry] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [peopleCount, setPeopleCount] = useState(0);
  const [isHalfFace, setIsHalfFace] = useState(false);
  const [isAligned, setIsAligned] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [captureStatus, setCaptureStatus] = useState(''); // Status message for capture button
  const detectionIntervalRef = useRef(null);
  const alignmentStatusRef = useRef(null);

  const [data, setData] = useState({
    fullName: "",
    email: "",
    phone: "",
    pan: "",
    panFile: null,
    panFileValid: null,
    panFileError: null,
    extractedPan: null,
    panMatch: null,
    isExtractingPan: false,
    extractionFailed: false, // New: track if all strategies failed
    extractionStatus: '',    // New: show current strategy/rotation
    extractionReason: null,  // New: reason for failure from backend
    manualConfirmation: false, // New: user overrides validaton
    snapshotValid: false, // Whether captured snapshot has face and is not blurry
    invitedEmail: null, // Store the email they were invited with for validation
    submissionError: null, // New: for identity mismatch or critical errors
  });

  // Live re-verification of PAN when input changes
  useEffect(() => {
    if (data.extractedPan && data.pan && data.pan.trim().length === 10) {
      const currentPan = data.pan.toUpperCase().trim();
      const extracted = data.extractedPan.toUpperCase().trim();
      const isMatch = currentPan === extracted;

      // Update state ONLY if mismatch state needs to change
      if (isMatch !== data.panMatch) {
        setData(prev => ({
          ...prev,
          panMatch: isMatch,
          // If it matches now, clear the extraction failure flag
          extractionFailed: !isMatch,
          extractionStatus: isMatch ? 'Verified' : (prev.extractionStatus || 'Mismatch')
        }));
      }
    }
  }, [data.pan, data.extractedPan, data.panMatch]);

  // Fetch invitation data to pre-fill fields
  useEffect(() => {
    const fetchInvitationData = async () => {
      if (!token) {
        // Fallback to localStorage if no token (e.g., during testing)
        const recentName = localStorage.getItem('recentCandidateName');

        if (recentName) {
          setData(prev => ({
            ...prev,
            fullName: recentName || prev.fullName,
          }));
        }
        return;
      }

      try {
        const response = await axios.get(`${API_BASE_URL}/invitations/public/${token}/?check_only=true`);
        if (response.data && response.data.invitation) {
          const { name, email, pan_number, phone } = response.data.invitation;

          setData(prev => ({
            ...prev,
            fullName: name || prev.fullName,
            invitedEmail: email || null, // Store official email for validation
            // STOP auto-filling email
            phone: phone || prev.phone,
            pan: pan_number || prev.pan,
          }));
        }
      } catch (err) {
        console.warn("Failed to fetch invitation for pre-fill:", err);

        // Fallback to localStorage on error
        const recentName = localStorage.getItem('recentCandidateName');

        if (recentName) {
          setData(prev => ({
            ...prev,
            fullName: recentName || prev.fullName,
          }));
        }
      }
    };

    fetchInvitationData();
  }, [token]);

  // Initialize MediaPipe face detection on component mount
  useEffect(() => {
    setModelsLoaded(true); // MediaPipe loads models on-demand, so we can set this to true
    console.log('Face detection ready');
  }, []);

  // Continuous face detection on webcam using MediaPipe
  useEffect(() => {
    if (!modelsLoaded || snapshot || !webcamRef.current) return;

    let faceDetection = null;

    const initializeDetection = async () => {
      try {
        faceDetection = new FaceDetection({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`;
          }
        });

        faceDetection.setOptions({
          model: 'short',
          minDetectionConfidence: 0.5
        });

        faceDetection.onResults((results) => {
          try {
            const detections = results.detections || [];
            const count = detections.length;
            setPeopleCount(count);
            const hasFace = count > 0;
            setFaceDetected(hasFace);

            let halfFace = false;
            let isAlignedFrame = false;

            // Helper variables for alignment checks
            let isCenteredX = false;
            let isCenteredY = false;
            let isGoodSize = false;
            let isContainedX = false;
            let isContainedY = false;

            if (hasFace) {
              const bbox = detections[0].boundingBox;
              // boundingBox is relative [0, 1]
              let x, y;
              if (bbox.xmin !== undefined) {
                x = bbox.xmin;
                y = bbox.ymin;
              } else {
                x = bbox.xCenter - bbox.width / 2;
                y = bbox.yCenter - bbox.height / 2;
              }

              const width = bbox.width;
              const height = bbox.height;
              const xCenter = x + width / 2;
              const yCenter = y + height / 2;

              // If the face is too close to the edges, consider it half face
              // Using a small margin like 0.01 or 1%
              if (x < 0.01 ||
                y < 0.01 ||
                x + width > 0.99 ||
                y + height > 0.99) {
                halfFace = true;
              }

              // Check if face is inside the oval/box overlay
              // Overlay is centered: width 140px (0.4375), height 180px (0.75)
              // Oval Bounds (Normalized):
              // X: 0.28 to 0.72
              // Y: 0.125 to 0.875

              // We define "Full face in oval" as:
              // 1. Center must be close to frame center
              // 2. Face edges must be largely within the oval bounds (with slight tolerance)
              // 3. Face must be large enough to fill the oval somewhat

              const ovalMinX = 0.25; // slightly wider tolerance than 0.28
              const ovalMaxX = 0.75; // slightly wider tolerance than 0.72
              const ovalMinY = 0.10; // slightly wider than 0.125
              const ovalMaxY = 0.90; // slightly wider than 0.875

              const faceLeft = x;
              const faceRight = x + width;
              const faceTop = y;
              const faceBottom = y + height;

              // Strict containment checks
              isContainedX = faceLeft > ovalMinX - 0.1 && faceRight < ovalMaxX + 0.1; // Allow 10% spill
              isContainedY = faceTop > ovalMinY - 0.05 && faceBottom < ovalMaxY + 0.05; // Allow 5% spill

              // Center check
              isCenteredX = Math.abs(xCenter - 0.5) < 0.15;
              isCenteredY = Math.abs(yCenter - 0.5) < 0.15;

              // Size check: Face shouldn't be tiny
              isGoodSize = width > 0.25 && height > 0.35;

              isAlignedFrame = isContainedX && isContainedY && isCenteredX && isCenteredY && isGoodSize && !halfFace;

              setIsAligned(isAlignedFrame);
            } else {
              setIsAligned(false);
            }
            // Store alignment details in ref for async callback
            alignmentStatusRef.current = {
              isCenteredX, isCenteredY, isGoodSize, isContainedX, isContainedY, isAlignedFrame, hasFace, halfFace, count
            };

            setIsHalfFace(halfFace);

            // Detect blur and brightness
            if (webcamRef.current && webcamRef.current.video) {
              const video = webcamRef.current.video;
              const canvas = document.createElement('canvas');
              canvas.width = video.videoWidth;
              canvas.height = video.videoHeight;
              const ctx = canvas.getContext('2d');
              ctx.drawImage(video, 0, 0);

              const imageDataObj = ctx.getImageData(0, 0, canvas.width, canvas.height);
              const data = imageDataObj.data;
              const imageDataUrl = canvas.toDataURL('image/jpeg');

              // Brightness check
              const brightness = calculateBrightness(data);
              const dark = brightness < 60; // Threshold for dark environment
              setIsDark(dark);

              detectBlur(imageDataUrl).then((notBlurry) => {
                setIsBlurry(!notBlurry);

                // Get latest status from ref
                const status = alignmentStatusRef.current;
                // If status is not yet available (rare race condition), skip update or use defaults
                if (!status) return;

                // Update status message
                if (status.count === 0) {
                  setCaptureStatus('No face detected. Please position yourself in front of the camera.');
                } else if (status.count > 1) {
                  setCaptureStatus('Multiple people detected. Only one person is allowed.');
                } else if (status.halfFace) {
                  setCaptureStatus('Face not fully visible. Please center your face.');
                } else if (status.hasFace && !status.isAlignedFrame) {
                  if (!status.isCenteredX || !status.isCenteredY) {
                    setCaptureStatus('Please center your face.');
                  } else if (!status.isGoodSize) { // Too small
                    setCaptureStatus('Please move closer to the camera.');
                  } else if (!status.isContainedX || !status.isContainedY) { // Too big / spilling out
                    setCaptureStatus('Please move back slightly.');
                  } else {
                    setCaptureStatus('Please position your face clearly.');
                  }
                } else if (dark) {
                  setCaptureStatus('Environment is too dark. Please ensure better lighting.');
                } else if (!notBlurry) {
                  setCaptureStatus('Image is blurry. Please hold still.');
                } else {
                  setCaptureStatus('Perfect! Face detected and clear. Ready to capture.');
                }
              });
            }
          } catch (err) {
            console.warn('Face detection processing error:', err);
          } finally {
            // Ensure the try-catch block is properly closed
          }
        });

        // Use interval to detect face from video stream
        if (webcamRef.current && webcamRef.current.video) {
          const detectionInterval = setInterval(async () => {
            if (webcamRef.current && webcamRef.current.video && webcamRef.current.video.readyState === 4) {
              try {
                await faceDetection.send({ image: webcamRef.current.video });
              } catch (err) {
                // Silently ignore MediaPipe WASM errors - they don't affect functionality
                console.warn('Face detection frame error:', err);
              }
            }
          }, 1000);

          // Store interval for cleanup
          detectionIntervalRef.current = detectionInterval;
        }
      } catch (error) {
        console.error('Face detection initialization error:', error);
      }
    };

    initializeDetection();

    return () => {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
    };
  }, [modelsLoaded, snapshot]);

  // Check PAN match when PAN number is entered
  React.useEffect(() => {
    if (data.pan && data.extractedPan) {
      const enteredPan = data.pan.toUpperCase().trim();
      // Strict check: match is only valid if no_face was NOT detected
      const isNoFace = data.extractionReason === 'no_face';
      const panMatches = enteredPan === data.extractedPan && !isNoFace;
      
      setData(prev => ({
        ...prev,
        panMatch: panMatches,
        panFileError: isNoFace ? prev.extractionStatus : (panMatches ? null : "PAN number doesn't match the PAN card image")
      }));
    }
  }, [data.pan, data.extractedPan, data.extractionReason]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);

    const emptyInvalid =
      !data.fullName ||
      !data.email ||
      !data.phone ||
      !data.pan ||
      !data.panFile ||
      !snapshot ||
      !data.snapshotValid; // Must have valid snapshot with face and not blurry

    const formatInvalid =
      (data.email && !validateField("email", data.email)) ||
      (data.phone && !validateField("phone", data.phone)) ||
      (data.pan && !validateField("pan", data.pan));

    // Check if PAN number matches extracted PAN
    // PDFs now use the same automated verification flow as images
    let panMismatch = false;
    let panNotExtracted = false;

    if (data.isExtractingPan) {
      alert("Please wait for PAN verification to complete.");
      return;
    }

    if (data.panFile) {
      if (data.extractedPan) {
        // Extraction result is in
        panMismatch = data.panMatch === false && !data.manualConfirmation;
      } else if (data.extractionFailed) {
        // Extraction failed, must have manual confirmation
        if (!data.manualConfirmation) {
          panNotExtracted = true;
        }
      } else {
        // No result yet and not currently extracting (but we already checked isExtractingPan above)
        panNotExtracted = true;
      }
    }

    // Check if entered email matches invited email
    const emailMismatch = data.invitedEmail && data.email.toLowerCase().trim() !== data.invitedEmail.toLowerCase().trim();

    const isInvalid = emptyInvalid || formatInvalid || panMismatch || panNotExtracted || emailMismatch;
    setShowError(isInvalid);

    if (isInvalid) {
      if (emailMismatch) {
        alert("Enter valid email. The email you entered does not match our records.");
      }
      if (panMismatch) {
        setData(prev => ({
          ...prev,
          panFileError: "Invalid PAN card: Entered PAN number doesn't match the PAN number in the uploaded image. Please verify and try again."
        }));
      } else if (panNotExtracted) {
        setData(prev => ({
          ...prev,
          panFileError: data.extractionFailed
            ? "Automatic verification failed. Please check the confirmation box to proceed manually."
            : "Could not verify PAN card. Please upload a clear image of your PAN card."
        }));
      } else if (!snapshot || !data.snapshotValid) {
        // Error message will be shown in the error text area
      }
      return;
    }

    if (!isInvalid) {
      // Split full name into first and last name for backend processing
      // Clear split names - we'll let the backend handle the full name directly
      // const nameParts = data.fullName.trim().split(/\s+/);
      // const firstName = nameParts[0] || "";
      // const lastName = nameParts.length > 1 ? nameParts.slice(1).join(" ") : " ";

      // Send candidate details to backend
      const formData = new FormData();
      formData.append('token', token);
      formData.append('full_name', data.fullName);
      // removed first_name and last_name formData.append('first_name', firstName);
      // removed first_name and last_name formData.append('last_name', lastName);
      formData.append('email', data.email);
      formData.append('phone', data.phone);
      formData.append('pan_number', data.pan);
      formData.append('snapshot', snapshot);

      // Add PAN file if available
      if (data.panFile) {
        formData.append('pan_file', data.panFile);
      }

      formData.append('entered_with_consent', data.manualConfirmation);

      // Send to backend API
      axios.post(`${API_BASE_URL}/candidate-details/`, formData, {
        headers: {
          // 'Content-Type': 'multipart/form-data', // Let the browser set the boundary
        },
      })
        .then((response) => {
          if (response.data.success) {
            // Store success in localStorage for quick check (STRICTLY Metadata ONLY to avoid QuotaExceededError)
            const leanData = {
              fullName: data.fullName,
              email: data.email,
              phone: data.phone,
              pan: data.pan,
              token: token,
              saved: true,
              id: response.data.id,
            };
            localStorage.setItem(`candidate_details_${token}`, JSON.stringify(leanData));

            // Log activity before proceeding
            import('../utils/activityLogger').then(({ logCandidateActivity }) => {
              logCandidateActivity(token, 'Assessment Started', 'Candidate submitted details and started the assessment.');
            });

            // Call onComplete callback to proceed to exam
            if (onComplete) {
              onComplete({ ...data, snapshot, token, id: response.data.id });
            }
          } else {
            alert('Failed to save candidate details: ' + (response.data.error || 'Unknown error'));
          }
        })
        .catch((error) => {
          console.error('Error saving candidate details:', error);
          const errorMessage = error?.response?.data?.error || error?.message || 'Failed to save candidate details';
          
          if (error?.response?.status === 403 && errorMessage.includes("Identity Mismatch")) {
            setData(prev => ({ ...prev, submissionError: errorMessage }));
          } else {
            alert('Error: ' + errorMessage);
          }
        });
    }
  };

  return (
    <div className="candidate-page">
      <header className="candidate-header">Candidate Portal</header>

      <main className="candidate-container">
        {data.submissionError ? (
          <div className="candidate-critical-error">
            <div className="candidate-error-icon">🚫</div>
            <h2>Access Denied</h2>
            <p>{data.submissionError}</p>
            <div className="candidate-error-footer">
              Please contact the recruitment team if you believe this is an error.
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
          {/* GENERAL */}
          <section className="candidate-card">
            <div className="candidate-section-title">General Information</div>
            <div className="candidate-row-full">
              <FloatingInput
                label="Full Name"
                field="fullName"
                value={data.fullName}
                errorEmpty={submitted && !data.fullName}
                onChange={(v) => setData({ ...data, fullName: v })}
                readOnly={true}
              />
            </div>
            <div className="candidate-row">
              <div className="candidate-input-group">
                <FloatingInput
                  label="Email"
                  type="email"
                  field="email"
                  value={data.email}
                  errorEmpty={submitted && data.email.trim() !== "" && data.invitedEmail && data.email.toLowerCase().trim() !== data.invitedEmail.toLowerCase().trim()}
                  onChange={(v) => setData({ ...data, email: v })}
                />
                {submitted && data.email.trim() !== "" && data.invitedEmail && data.email.toLowerCase().trim() !== data.invitedEmail.toLowerCase().trim() && (
                  <div className="candidate-error-text" style={{ textAlign: 'left', marginTop: '4px' }}>
                    Enter valid email
                  </div>
                )}
              </div>
              <div style={{ position: 'relative' }}>
                <FloatingInput
                  label="Phone Number"
                  type="tel"
                  field="phone"
                  value={data.phone}
                  errorEmpty={submitted && !data.phone}
                  onChange={(v) => setData({ ...data, phone: v })}
                />
                {data.phone && !/^[6-9]/.test(data.phone) && (
                  <div style={{ position: 'absolute', top: '100%', left: 0, color: '#ef4444', fontSize: '12px', marginTop: '2px', whiteSpace: 'nowrap' }}>
                    Enter valid phone number (must start with 6, 7, 8 or 9)
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* KYC */}
          <section className="candidate-card">
            <div className="candidate-section-title">KYC</div>
            <div className="candidate-row">
              <FloatingInput
                label="PAN Card Number"
                field="pan"
                value={data.pan}
                errorEmpty={submitted && !data.pan}
                onChange={(v) => setData({ ...data, pan: v })}
              />
              <div className="candidate-input-group">
                <div className="candidate-label-row">
                  <label className="candidate-static-label" style={{ marginBottom: 0, whiteSpace: 'nowrap' }}>
                    Upload PAN Card <span style={{ color: '#1d4ed8', marginLeft: '2px' }}>*</span> <span className="candidate-hint-text" style={{ marginLeft: '10px', fontWeight: '600', opacity: 0.9 }}>(Allowed formats: .png, .jpg, .jpeg, .pdf, Max 2.5MB)</span>
                  </label>
                </div>
                <input
                  type="file"
                  accept=".png,.jpg,.jpeg,.pdf"
                  disabled={!data.pan || data.pan.trim().length !== 10}
                  className={`candidate-input ${submitted && !data.panFile ? 'candidate-input-error' : ''}`}
                  onChange={(e) => {
                    const file = e.target.files?.[0] || null;
                    if (file) {
                      // Check file extension as fallback (some browsers may have different MIME types)
                      const fileName = file.name.toLowerCase();
                      const validExtensions = ['.png', '.jpg', '.jpeg', '.pdf'];
                      const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));

                      // Check MIME type
                      const validMimeTypes = [
                        "image/png",
                        "image/jpeg",
                        "image/jpg",  // Some browsers use jpg instead of jpeg
                        "application/pdf"
                      ];
                      const isValidMimeType = validMimeTypes.includes(file.type);

                      // Accept if either MIME type or extension is valid
                      const isValidType = isValidMimeType || hasValidExtension;
                      const isValidSize = file.size <= 2.5 * 1024 * 1024; // 2.5MB limit

                      // Debug logging
                      console.log('File validation:', {
                        name: file.name,
                        type: file.type,
                        size: file.size,
                        isValidType,
                        isValidSize,
                        hasValidExtension
                      });

                      if (isValidType && isValidSize) {
                        // Check if it's an image (not PDF) for OCR extraction
                        const isImage = file.type.startsWith('image/');
                        // Helper to call backend verification
                        const triggerBackendVerification = (targetFile) => {
                          setData(prev => ({ ...prev, extractionStatus: 'Verifying with server...' }));

                          const enteredPan = (data.pan || '').toUpperCase().trim();
                          const formData = new FormData();
                          formData.append('pan_number', enteredPan);
                          formData.append('pan_file', targetFile);
                          axios.post(`${API_BASE_URL}/candidate-details/verify-pan/`, formData)
                            .then(response => {
                              const { verified, extracted_pan, message, reason } = response.data;
                              console.log("Backend verification response:", response.data);

                              setData(prev => ({
                                ...prev,
                                extractedPan: extracted_pan || prev.extractedPan,
                                panMatch: verified === true,
                                isExtractingPan: false,
                                extractionFailed: !verified,
                                extractionReason: reason || null,
                                extractionStatus: verified ? 'Verified' : (message || 'Validation failed'),
                                panFileError: null
                              }));
                            })
                            .catch(err => {
                              console.warn("Backend verification failed:", err);
                              setData(prev => ({
                                ...prev,
                                panMatch: false,
                                isExtractingPan: false,
                                extractionFailed: true,
                                extractionStatus: 'Failed',
                                panFileError: null
                              }));
                            });
                        };

                        // ALWAYS extract PAN number whether image OR pdf
                        setData(prev => ({
                          ...prev,
                          panFile: file,
                          panFileValid: true,
                          panFileError: null,
                          isExtractingPan: true,
                          extractedPan: null,
                          panMatch: null,
                          extractionFailed: false,
                          extractionStatus: '',
                          manualConfirmation: false,
                        }));

                        // ALWAYS trigger backend verification to ensure face check is performed
                        triggerBackendVerification(file);
                      } else {
                        // ❌ Reject invalid file with specific error message
                        let errorMsg = "Invalid file. ";
                        if (!isValidType) {
                          errorMsg += "Please upload PNG, JPG, JPEG, or PDF file. ";
                        }
                        if (!isValidSize) {
                          errorMsg += `File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds 2.5MB limit.`;
                        }
                        setData({ ...data, panFile: null, panFileValid: false, panFileError: errorMsg });
                        e.target.value = "";
                      }
                    }
                  }}
                />
                {/* Show feedback */}
                {data.isExtractingPan && (
                  <div className="candidate-info-text">
                    🔍 {data.extractionStatus || 'Initializing extraction...'}
                  </div>
                )}
                {/* No special bypass for PDF - it now uses standard automated verification */}
                {!data.isExtractingPan && data.panFileValid === true && data.extractedPan && data.panMatch === true && (
                  <div className="candidate-success-text">
                    ✅ PAN Card verified: PAN number matches ({data.extractedPan})
                  </div>
                )}
                {!data.isExtractingPan && data.panFileValid === true && data.extractionFailed && (
                  <div className="candidate-warning-box">
                    <div className="candidate-error-text" style={{ fontSize: '15px' }}>
                      ❌ {data.extractionStatus || 'Verification Failed'}
                    </div>
                    {/* Only show manual confirmation if it's NOT a no_face error */}
                    {data.extractionReason !== 'no_face' ? (
                      <div style={{ marginTop: '10px' }}>
                        <label className="candidate-checkbox-label">
                          <input
                            type="checkbox"
                            checked={data.manualConfirmation}
                            onChange={(e) => setData({ ...data, manualConfirmation: e.target.checked, panFileError: null })}
                          />
                          <span>I confirm the uploaded document is my valid PAN card and the details entered above are correct.</span>
                        </label>
                      </div>
                    ) : (
                      <div className="candidate-hint-text" style={{ marginTop: '8px', color: '#ef4444', fontWeight: '500' }}>
                        Please upload a clear, high-quality image of your PAN card that clearly shows your face and PAN details.
                      </div>
                    )}
                  </div>
                )}
                {data.panFileValid === false && data.panFileError && (
                  <div className="candidate-error-text">
                    ❌ {data.panFileError}
                  </div>
                )}
                {data.panFileValid === false && !data.panFileError && (
                  <div className="candidate-error-text">
                    ❌ Invalid PAN Card file
                  </div>
                )}
                {submitted && !data.panFile && (
                  <div className="candidate-error-text">⚠️ Please upload a valid PAN Card file</div>
                )}
                {submitted && data.panFile && data.panMatch === false && !data.manualConfirmation && (
                  <div className="candidate-error-text">⚠️ Invalid PAN card: PAN number doesn't match the uploaded image. Please verify your details or upload a clear image.</div>
                )}
              </div>
            </div>
          </section>

          {/* SNAPSHOT */}
          <section className="candidate-card">
            <div className="candidate-section-title">Identity Verification</div>
            <div className="candidate-webcam-container">
              {!modelsLoaded && (
                <div className="candidate-info-text">
                  ⏳ Loading face detection models... Please wait.
                </div>
              )}
              {!snapshot ? (
                <>
                  {modelsLoaded && (
                    <div className={`candidate-webcam-frame ${(!faceDetected || isBlurry || isDark || isHalfFace || peopleCount !== 1 || !isAligned) ? 'face-not-detected' : 'face-detected'}`}>
                      <Webcam ref={webcamRef} width={320} height={240} disablePictureInPicture={true} />
                    </div>
                  )}
                  {captureStatus && (
                    <div className={`candidate-status-message ${faceDetected && !isBlurry && !isDark && !isHalfFace && peopleCount === 1 && !isDetecting ? 'candidate-status-success' : 'candidate-status-warning'}`}>
                      {isDetecting ? '🔍 Detecting...' : captureStatus}
                    </div>
                  )}
                  <div className="candidate-button-row">
                    <button
                      type="button"
                      className={`candidate-button-small ${faceDetected && !isBlurry && !isDark && !isHalfFace && peopleCount === 1 && isAligned && !isDetecting ? 'candidate-button-ready' : 'candidate-button-disabled'}`}
                      onClick={async () => {
                        if (!webcamRef.current) return;

                        if (!faceDetected) {
                          alert('⚠️ No face detected.');
                          return;
                        }

                        if (!isAligned) {
                          alert('⚠️ Face not centered or clearly visible.');
                          return;
                        }

                        if (peopleCount > 1) {
                          alert('⚠️ Multiple people detected.');
                          return;
                        }

                        if (isHalfFace) {
                          alert('⚠️ Face not fully visible.');
                          return;
                        }

                        if (isDark) {
                          alert('⚠️ Environment is too dark.');
                          return;
                        }

                        if (isBlurry) {
                          alert('⚠️ Image is blurry. Please hold still.');
                          return;
                        }

                        // Capture snapshot
                        const imageSrc = webcamRef.current.getScreenshot();
                        if (!imageSrc) return;

                        // Validate captured image
                        setIsDetecting(true);
                        const hasFace = await detectFace(imageSrc);

                        // We skip strict brightness/blur check re-eval here to avoid double alert if live check was okay
                        // But good to double check basic face presence

                        if (!hasFace) {
                          console.warn('Face check failed on static image');
                        }

                        // Image is valid (we trust live checks mostly for UX speed)
                        setSnapshot(imageSrc);
                        setData(prev => ({ ...prev, snapshotValid: true }));
                        setIsDetecting(false);

                        // Clear detection interval
                        if (detectionIntervalRef.current) {
                          clearInterval(detectionIntervalRef.current);
                        }
                      }}
                      disabled={!faceDetected || isBlurry || isDark || isHalfFace || peopleCount !== 1 || !isAligned || isDetecting || !modelsLoaded}
                    >
                      {isDetecting ? 'Processing...' : 'Take Snapshot'}
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <img src={snapshot} width={320} alt="snap" />
                  <div className="candidate-button-row">
                    <button
                      type="button"
                      className="candidate-button-small"
                      onClick={() => {
                        setSnapshot(null);
                        setData(prev => ({ ...prev, snapshotValid: false }));
                        setFaceDetected(false);
                        setIsBlurry(false);
                        setCaptureStatus('');
                      }}
                    >
                      Retake Snapshot
                    </button>
                  </div>
                </>
              )}
            </div>
          </section>

          {/* SUBMIT */}
          <div className="candidate-button-row">
            <button
              type="submit"
              className={`candidate-button ${(!data.fullName || !data.email || !data.phone || !data.pan || !data.panFile || !snapshot || !data.snapshotValid || data.isExtractingPan || (data.panMatch === false && !data.manualConfirmation) || (data.extractionFailed && !data.manualConfirmation)) ? 'candidate-button-disabled' : ''}`}
              disabled={!data.fullName || !data.email || !data.phone || !data.pan || !data.panFile || !snapshot || !data.snapshotValid || data.isExtractingPan || (data.panMatch === false && !data.manualConfirmation) || (data.extractionFailed && !data.manualConfirmation)}
            >
              Submit Application
            </button>
          </div>

          {showError && (
            <div className="candidate-error-text">
              Please correct the highlighted fields
              {submitted && (!snapshot || !data.snapshotValid) && (
                <div style={{ marginTop: '8px' }}>
                  ⚠️ Please capture a valid photo with your face clearly visible and not blurry.
                </div>
              )}
            </div>
          )}
        </form>
        )}
      </main>
    </div>
  );
};

export default CandidateDetails;

