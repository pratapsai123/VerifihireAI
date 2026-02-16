import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import Tesseract from 'tesseract.js';
import { FaceDetection } from '@mediapipe/face_detection';
import axios from 'axios';
import '../styles/CandidateDetails.css';

// Validation rules
const validateField = (field, value) => {
  switch (field) {
    case "email":
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    case "phone":
      return /^[0-9]{10}$/.test(value);
    case "pan":
      return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value);
    default:
      return value.trim() !== "";
  }
};

const FloatingInput = ({ label, value, onChange, errorEmpty, type = "text", field }) => {
  const hasValue = value.trim().length > 0;
  const formatValid = hasValue ? validateField(field, value) : true;

  const showRedBorder = errorEmpty || !formatValid;

  return (
    <div className="candidate-input-group">
      <label className="candidate-static-label">{label}</label>
      <input
        type={type}
        value={value}
        placeholder={label}
        maxLength={field === "pan" ? 10 : undefined}
        onChange={(e) => {
          let val = e.target.value;

          if (field === "phone") {
            val = val.replace(/[^0-9]/g, "").slice(0, 10);
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
        className={`candidate-input ${showRedBorder ? 'candidate-input-error' : ''}`}
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
      resolve(results.detections && results.detections.length > 0);
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

// Function to extract PAN number from image using OCR
const extractPanFromImage = async (file) => {
  try {
    const { data: { text } } = await Tesseract.recognize(file, 'eng', {
      logger: (m) => console.log(m) // Optional: log progress
    });

    // PAN format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)
    const panPattern = /[A-Z]{5}[0-9]{4}[A-Z]{1}/g;
    const matches = text.match(panPattern);

    if (matches && matches.length > 0) {
      // Return the first match (usually the main PAN number on the card)
      return matches[0].toUpperCase();
    }

    // If no exact match, try to find any 10-character alphanumeric sequence
    const altPattern = /[A-Z0-9]{10}/g;
    const altMatches = text.match(altPattern);
    if (altMatches) {
      // Filter to find PAN-like patterns (5 letters, 4 digits, 1 letter)
      for (const match of altMatches) {
        if (/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(match)) {
          return match.toUpperCase();
        }
      }
    }

    return null;
  } catch (error) {
    console.error('OCR Error:', error);
    return null;
  }
};

const CandidateDetails = ({ token, onComplete }) => {
  const webcamRef = useRef(null);
  const [snapshot, setSnapshot] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [showError, setShowError] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const [isBlurry, setIsBlurry] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [captureStatus, setCaptureStatus] = useState(''); // Status message for capture button
  const detectionIntervalRef = useRef(null);

  const [data, setData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    pan: "",
    panFile: null,
    panFileValid: null,
    panFileError: null,
    extractedPan: null,
    panMatch: null,
    isExtractingPan: false,
    snapshotValid: false, // Whether captured snapshot has face and is not blurry
  });

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
          const hasFace = results.detections && results.detections.length > 0;
          setFaceDetected(hasFace);

          // Detect blur
          if (webcamRef.current && webcamRef.current.video) {
            const video = webcamRef.current.video;
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            const imageData = canvas.toDataURL('image/jpeg');

            detectBlur(imageData).then((notBlurry) => {
              setIsBlurry(!notBlurry);

              // Update status message
              if (!hasFace) {
                setCaptureStatus('No face detected. Please position yourself in front of the camera.');
              } else if (!notBlurry) {
                setCaptureStatus('Image is blurry. Please hold still and ensure good lighting.');
              } else {
                setCaptureStatus('Face detected and image is clear. Ready to capture!');
              }
            });
          }
        });

        // Use interval to detect face from video stream
        if (webcamRef.current && webcamRef.current.video) {
          const detectionInterval = setInterval(async () => {
            if (webcamRef.current && webcamRef.current.video && webcamRef.current.video.readyState === 4) {
              await faceDetection.send({ image: webcamRef.current.video });
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
      const panMatches = enteredPan === data.extractedPan;
      setData(prev => ({
        ...prev,
        panMatch: panMatches,
        panFileError: panMatches ? null : "PAN number doesn't match the PAN card image"
      }));
    }
  }, [data.pan, data.extractedPan]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);

    const emptyInvalid =
      !data.firstName ||
      !data.lastName ||
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

    // Check if PAN number matches extracted PAN from image
    // For images: must match extracted PAN
    // For PDFs: manual verification (no OCR), so we allow if PAN is entered and valid format
    const isPdf = data.panFile && data.panFile.type === 'application/pdf';
    const panMismatch = !isPdf && data.extractedPan && data.panMatch === false;
    const panNotExtracted = !isPdf && data.panFile && !data.extractedPan && !data.isExtractingPan;

    const isInvalid = emptyInvalid || formatInvalid || panMismatch || panNotExtracted;
    setShowError(isInvalid);

    if (isInvalid) {
      if (panMismatch) {
        setData(prev => ({
          ...prev,
          panFileError: "Invalid PAN card: Entered PAN number doesn't match the PAN number in the uploaded image. Please verify and try again."
        }));
      } else if (panNotExtracted) {
        setData(prev => ({
          ...prev,
          panFileError: "Could not verify PAN card. Please upload a clear image of your PAN card."
        }));
      } else if (!snapshot || !data.snapshotValid) {
        // Error message will be shown in the error text area
      }
      return;
    }

    if (!isInvalid) {
      // Send candidate details to backend
      const formData = new FormData();
      formData.append('token', token);
      formData.append('first_name', data.firstName);
      formData.append('last_name', data.lastName);
      formData.append('email', data.email);
      formData.append('phone', data.phone);
      formData.append('pan_number', data.pan);
      formData.append('snapshot', snapshot);

      // Add PAN file if available
      if (data.panFile) {
        formData.append('pan_file', data.panFile);
      }

      // Send to backend API
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

      axios.post(`${API_BASE_URL}/candidate-details/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
        .then((response) => {
          if (response.data.success) {
            // Store success in localStorage for quick check
            localStorage.setItem(`candidate_details_${token}`, JSON.stringify({
              ...data,
              snapshot,
              token,
              saved: true,
              id: response.data.id,
            }));

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
          alert('Error: ' + errorMessage);
        });
    }
  };

  return (
    <div className="candidate-page">
      <header className="candidate-header">Candidate Portal</header>

      <main className="candidate-container">
        <form onSubmit={handleSubmit}>
          {/* GENERAL */}
          <section className="candidate-card">
            <div className="candidate-section-title">General Information</div>
            <div className="candidate-row">
              <FloatingInput
                label="First Name"
                field="firstName"
                value={data.firstName}
                errorEmpty={submitted && !data.firstName}
                onChange={(v) => setData({ ...data, firstName: v })}
              />
              <FloatingInput
                label="Last Name"
                field="lastName"
                value={data.lastName}
                errorEmpty={submitted && !data.lastName}
                onChange={(v) => setData({ ...data, lastName: v })}
              />
            </div>
            <div className="candidate-row">
              <FloatingInput
                label="Email"
                type="email"
                field="email"
                value={data.email}
                errorEmpty={submitted && !data.email}
                onChange={(v) => setData({ ...data, email: v })}
              />
              <FloatingInput
                label="Phone Number"
                type="tel"
                field="phone"
                value={data.phone}
                errorEmpty={submitted && !data.phone}
                onChange={(v) => setData({ ...data, phone: v })}
              />
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
                <label className="candidate-static-label">Upload PAN Card</label>
                <input
                  type="file"
                  accept=".png,.jpg,.jpeg,.pdf"
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
                      const isValidSize = file.size <= 5 * 1024 * 1024; // 5MB (increased from 2MB for PAN card images)

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

                        // ✅ Accept valid PAN card file and extract PAN number
                        setData(prev => ({
                          ...prev,
                          panFile: file,
                          panFileValid: true,
                          panFileError: null,
                          isExtractingPan: isImage, // Only extract from images
                          extractedPan: null,
                          panMatch: null
                        }));

                        // Extract PAN from image using OCR (only for images, not PDFs)
                        if (isImage) {
                          extractPanFromImage(file).then((extractedPan) => {
                            setData(prev => {
                              if (extractedPan) {
                                const enteredPan = (prev.pan || '').toUpperCase().trim();
                                const panMatches = enteredPan === extractedPan;

                                return {
                                  ...prev,
                                  extractedPan,
                                  panMatch: panMatches,
                                  isExtractingPan: false,
                                  panFileError: panMatches ? null : "PAN number in image doesn't match entered PAN number"
                                };
                              } else {
                                return {
                                  ...prev,
                                  extractedPan: null,
                                  panMatch: false,
                                  isExtractingPan: false,
                                  panFileError: "Could not extract PAN number from image. Please ensure the image is clear and readable."
                                };
                              }
                            });
                          }).catch((error) => {
                            console.error('OCR extraction failed:', error);
                            setData(prev => ({
                              ...prev,
                              extractedPan: null,
                              panMatch: false,
                              isExtractingPan: false,
                              panFileError: "Failed to process image. Please try uploading a clearer image."
                            }));
                          });
                        } else {
                          // For PDFs, we can't extract automatically, so require manual verification
                          setData(prev => ({
                            ...prev,
                            extractedPan: null,
                            panMatch: null, // Will be checked on submit
                            isExtractingPan: false,
                            panFileError: "PDF uploaded. Please ensure the PAN number matches your uploaded document."
                          }));
                        }
                      } else {
                        // ❌ Reject invalid file with specific error message
                        let errorMsg = "Invalid file. ";
                        if (!isValidType) {
                          errorMsg += "Please upload PNG, JPG, or PDF file. ";
                        }
                        if (!isValidSize) {
                          errorMsg += `File size (${(file.size / 1024 / 1024).toFixed(2)}MB) exceeds 5MB limit.`;
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
                    🔍 Extracting PAN number from image...
                  </div>
                )}
                {!data.isExtractingPan && data.panFileValid === true && data.panFile && data.panFile.type === 'application/pdf' && (
                  <div className="candidate-info-text">
                    📄 PDF uploaded. Please ensure the PAN number matches your document.
                  </div>
                )}
                {!data.isExtractingPan && data.panFileValid === true && data.extractedPan && data.panMatch === true && (
                  <div className="candidate-success-text">
                    ✅ PAN Card verified: PAN number matches ({data.extractedPan})
                  </div>
                )}
                {!data.isExtractingPan && data.panFileValid === true && data.extractedPan && data.panMatch === false && (
                  <div className="candidate-error-text">
                    ❌ PAN Mismatch: Entered PAN ({data.pan.toUpperCase()})
                  </div>
                )}
                {!data.isExtractingPan && data.panFileValid === true && !data.extractedPan && data.panFile && data.panFile.type.startsWith('image/') && (
                  <div className="candidate-error-text">
                    ⚠️ Could not extract PAN from image. Please ensure image is clear and readable.
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
                {submitted && data.panFile && data.panMatch === false && (
                  <div className="candidate-error-text">⚠️ Invalid PAN card: PAN number doesn't match the uploaded image. Please verify your details.</div>
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
                  {modelsLoaded && <Webcam ref={webcamRef} width={320} />}
                  {captureStatus && (
                    <div className={`candidate-status-message ${faceDetected && !isBlurry ? 'candidate-status-success' : 'candidate-status-warning'}`}>
                      {isDetecting ? '🔍 Detecting...' : captureStatus}
                    </div>
                  )}
                  <div className="candidate-button-row">
                    <button
                      type="button"
                      className={`candidate-button-small ${faceDetected && !isBlurry && !isDetecting ? 'candidate-button-ready' : 'candidate-button-disabled'}`}
                      onClick={async () => {
                        if (!webcamRef.current) return;

                        // Check if face is detected and image is not blurry
                        if (!faceDetected) {
                          alert('⚠️ No face detected. Please position yourself in front of the camera.');
                          return;
                        }

                        if (isBlurry) {
                          alert('⚠️ Image is blurry. Please hold still and ensure good lighting.');
                          return;
                        }

                        // Capture snapshot
                        const imageSrc = webcamRef.current.getScreenshot();
                        if (!imageSrc) return;

                        // Validate captured image
                        setIsDetecting(true);
                        const hasFace = await detectFace(imageSrc);
                        const notBlurry = await detectBlur(imageSrc);

                        if (!hasFace) {
                          alert('❌ No face detected in captured image. Please try again.');
                          setIsDetecting(false);
                          return;
                        }

                        if (!notBlurry) {
                          alert('❌ Captured image is blurry. Please try again with better lighting.');
                          setIsDetecting(false);
                          return;
                        }

                        // Image is valid
                        setSnapshot(imageSrc);
                        setData(prev => ({ ...prev, snapshotValid: true }));
                        setIsDetecting(false);

                        // Clear detection interval
                        if (detectionIntervalRef.current) {
                          clearInterval(detectionIntervalRef.current);
                        }
                      }}
                      disabled={!faceDetected || isBlurry || isDetecting || !modelsLoaded}
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
            <button type="submit" className="candidate-button">Submit Application</button>
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
      </main>
    </div>
  );
};

export default CandidateDetails;

