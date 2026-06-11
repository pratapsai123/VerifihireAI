import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/Dashboard.css';
import '../styles/ResumeMatcher.css';

const MAX_CODING_TASKS = 50;
const STORAGE_KEY = 'resume_screening_form_data';

const ResumeMatcher = () => {
    const [files, setFiles] = useState([]);
    const [jobDescription, setJobDescription] = useState('');
    const [threshold, setThreshold] = useState(70);
    const [experienceLevel, setExperienceLevel] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isRetrying, setIsRetrying] = useState(false);
    const [results, setResults] = useState(null);
    const [batchId, setBatchId] = useState(null);
    const [progress, setProgress] = useState({ processed: 0, total: 0 });
    const [matchMode, setMatchMode] = useState('automatic');
    const [customRoleTitle, setCustomRoleTitle] = useState('');
    const [sameQuestionsForAll, setSameQuestionsForAll] = useState(false);

    const [jobRoles, setJobRoles] = useState([]);
    const [selectedRoleId, setSelectedRoleId] = useState('');



    React.useEffect(() => {
        const fetchRoles = async () => {
            try {
                const res = await axios.get(`${API_BASE_URL}/job-roles/`);
                setJobRoles(res.data);
            } catch (err) {
                console.error("Error fetching job roles:", err);
            }
        };
        fetchRoles();
    }, []);

    // --- Polling Logic ---
    React.useEffect(() => {
        let interval;
        if (batchId && isAnalyzing) {
            interval = setInterval(async () => {
                try {
                    const response = await axios.get(`${API_BASE_URL}/ai-candidates/batch-progress/${batchId}/`);
                    const data = response.data;
                    setProgress({ processed: data.processed, total: data.total });

                    // Live Console Feedback for Browser
                    console.log(`📊 Batch Progress: ${data.processed}/${data.total} candidates processed.`);
                    if (data.results && data.results.length > 0) {
                        const lastResult = data.results[data.results.length - 1];
                        if (lastResult.candidate_name) {
                            console.log(`✅ Latest screened: ${lastResult.candidate_name} (Score: ${lastResult.match_percentage}%)`);
                        }
                    }

                    if (data.is_complete) {
                        console.log("✨ BATCH COMPLETE! Rendering results...");
                        setResults(data.results);
                        setBatchId(null);
                        setIsAnalyzing(false);
                        if (matchMode === 'automatic') {
                            // Backend has finished generating assessments
                        }
                        sessionStorage.removeItem(STORAGE_KEY); // Full clear once complete
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                }
            }, 3000); // Poll every 3 seconds
        }
        return () => clearInterval(interval);
    }, [batchId, isAnalyzing]);

    const [mcqDuration, setMcqDuration] = useState(10);
    const [codingDuration, setCodingDuration] = useState(30);
    const [mcqDurationManual, setMcqDurationManual] = useState(false);
    const [mcqCount, setMcqCount] = useState(10);
    const [codingCount, setCodingCount] = useState(1);
    const [passThreshold, setPassThreshold] = useState(60);
    const [interviewPassThreshold, setInterviewPassThreshold] = useState(50);
    const [mcqWeight, setMcqWeight] = useState(40);
    const [codingChallenges, setCodingChallenges] = useState([{ id: 1, difficulty: '' }]);

    // Auto-adjust scoring weights when counts are 0
    React.useEffect(() => {
        if (mcqCount === 0 && codingCount > 0) {
            setMcqWeight(0);
        } else if (codingCount === 0 && mcqCount > 0) {
            setMcqWeight(100);
        }
    }, [mcqCount, codingCount]);

    // Auto-calculate MCQ duration (1 min per Q)
    React.useEffect(() => {
        if (!mcqDurationManual) {
            setMcqDuration(mcqCount || 0);
        }
    }, [mcqCount, mcqDurationManual]);

    // Auto-adjust coding duration based on tasks
    React.useEffect(() => {
        if (codingCount === 0) {
            setCodingDuration(0);
        } else if (codingDuration === 0 && codingCount > 0) {
            setCodingDuration(30); // reset to a default if they add tasks again
        }
    }, [codingCount]);



    const [assessmentStartDate, setAssessmentStartDate] = useState('');
    const [assessmentStartTime, setAssessmentStartTime] = useState('');
    const [assessmentEndDate, setAssessmentEndDate] = useState('');
    const [assessmentEndTime, setAssessmentEndTime] = useState('');

    const [interviewStartDate, setInterviewStartDate] = useState('');
    const [interviewStartTime, setInterviewStartTime] = useState('');
    const [interviewEndDate, setInterviewEndDate] = useState('');
    const [interviewEndTime, setInterviewEndTime] = useState('');

    // Ensure interview dates are strictly after assessment dates
    React.useEffect(() => {
        if (assessmentEndDate && interviewStartDate) {
            const minDate = new Date(assessmentEndDate);
            minDate.setDate(minDate.getDate() + 1);
            const minDateString = minDate.toISOString().split('T')[0];

            if (interviewStartDate < minDateString) {
                setInterviewStartDate('');
                setInterviewEndDate('');
            }
        }
    }, [assessmentEndDate, interviewStartDate]);

    // --- Persistence Logic ---
    const isDirty = React.useRef(false);
    const isInitialRender = React.useRef(true);

    // 1. Initial Load / Hydration
    React.useEffect(() => {
        // Start completely fresh on page reload
        sessionStorage.removeItem(STORAGE_KEY);
        isDirty.current = false;
        window._matcher_init = true;
    }, []);

    // 2. Active Sync to sessionStorage
    // GUARD: Skip the very first render (mount with defaults) to prevent
    // writing empty/default data before the user fills anything in.
    // After that, only save if the form has been marked as dirty
    // (either by hydration restoring data, or by user interaction).
    const initialDataHash = React.useRef(null);
    if (!initialDataHash.current) {
        initialDataHash.current = JSON.stringify({
            jobDescription, threshold, matchMode, customRoleTitle, selectedRoleId, experienceLevel,
            mcqDuration, codingDuration, mcqCount, codingCount, passThreshold, codingChallenges,
            assessmentStartDate, assessmentStartTime, assessmentEndDate, assessmentEndTime,
            interviewStartDate, interviewStartTime, interviewEndDate, interviewEndTime,
            batchId, isAnalyzing
        });
    }

    React.useEffect(() => {
        const formData = {
            jobDescription, threshold, matchMode, customRoleTitle, selectedRoleId, experienceLevel,
            mcqDuration, codingDuration, mcqCount, codingCount, passThreshold, codingChallenges,
            sameQuestionsForAll,
            assessmentStartDate, assessmentStartTime, assessmentEndDate, assessmentEndTime,
            interviewStartDate, interviewStartTime, interviewEndDate, interviewEndTime,
            batchId, isAnalyzing // Persist active session state
        };
        const currentDataStr = JSON.stringify(formData);

        if (!isDirty.current && currentDataStr === initialDataHash.current) {
            return;
        }

        // Any state divergence from the defaults means user interaction or hydration — mark dirty and save
        isDirty.current = true;
        sessionStorage.setItem(STORAGE_KEY, currentDataStr);
    }, [
        jobDescription, threshold, matchMode, customRoleTitle, selectedRoleId, experienceLevel,
        mcqDuration, codingDuration, mcqCount, codingCount, passThreshold, codingChallenges,
        assessmentStartDate, assessmentStartTime, assessmentEndDate, assessmentEndTime,
        interviewStartDate, interviewStartTime, interviewEndDate, interviewEndTime,
        batchId, isAnalyzing
    ]);

    const handleCodingCountChange = (val) => {
        if (val === '') {
            setCodingCount('');
            setCodingChallenges([]);
            return;
        }
        const count = Math.min(Math.max(parseInt(val) || 0, 0), MAX_CODING_TASKS);
        let updated = [...codingChallenges];
        if (count > updated.length) {
            for (let i = updated.length; i < count; i++) {
                updated.push({ id: Date.now() + i, difficulty: '' });
            }
        } else {
            updated = updated.slice(0, count);
        }
        setCodingCount(count);
        setCodingChallenges(updated);
    };

    const updateCodingDiff = (id, diff) => {
        setCodingChallenges(prev => prev.map(c => c.id === id ? { ...c, difficulty: diff } : c));
    };

    const calculateTotalPoints = () => {
        const mcqPts = mcqCount * 1; // 1 pt per MCQ
        const codingPts = codingChallenges.reduce((sum, c) => {
            return sum + (c.difficulty === 'Easy' ? 100 : c.difficulty === 'Medium' ? 200 : c.difficulty === 'Hard' ? 300 : 0);
        }, 0);
        return mcqPts + codingPts;
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const incomingFiles = Array.from(e.target.files);
            setFiles(prevFiles => {
                const existingNames = new Set(prevFiles.map(f => f.name));
                const uniqueNewFiles = incomingFiles.filter(f => !existingNames.has(f.name));
                return [...prevFiles, ...uniqueNewFiles];
            });
            // Clear the input value so the same file can be uploaded again if removed
            e.target.value = '';
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setFiles(prevFiles => {
                const newFiles = Array.from(e.dataTransfer.files);
                const existingNames = new Set(prevFiles.map(f => f.name));
                const uniqueNewFiles = newFiles.filter(f => !existingNames.has(f.name));
                return [...prevFiles, ...uniqueNewFiles];
            });
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const removeFile = (index) => {
        const newFiles = [...files];
        newFiles.splice(index, 1);
        setFiles(newFiles);
    };

    const handleMatch = async () => {
        if (files.length === 0) {
            alert('Please upload at least one resume.');
            return;
        }
        if (!jobDescription.trim()) {
            alert('Please provide a job description.');
            return;
        }
        if (!experienceLevel) {
            alert('Please select an experience level.');
            return;
        }
        if (Number(threshold) <= 0) {
            alert('Sensitivity Threshold must be greater than 0%.');
            return;
        }

        if (matchMode === 'automatic') {
            if (Number(mcqCount) === 0 && Number(codingCount) === 0) {
                alert('Please provide at least one MCQ question or one Coding task for the assessment. They cannot both be 0.');
                return;
            }
            if (Number(codingCount) > 0 && codingChallenges.some(c => !c.difficulty)) {
                alert('Please select a Coding Level (Difficulty) for all coding tasks.');
                return;
            }
            if (Number(passThreshold) <= 0) {
                alert('Assessment Pass Threshold must be greater than 0%.');
                return;
            }
            if (Number(interviewPassThreshold) <= 0) {
                alert('Interview Pass Threshold must be greater than 0%.');
                return;
            }
            if (Number(codingCount) > 0 && (!codingDuration || Number(codingDuration) <= 0)) {
                alert('Coding Assessment Duration must be greater than 0 minutes.');
                return;
            }
            if (Number(mcqCount) > 0 && (!mcqDuration || Number(mcqDuration) <= 0)) {
                alert('MCQ Assessment Duration must be greater than 0 minutes.');
                return;
            }
            if (!assessmentStartDate || !assessmentStartTime || !assessmentEndDate || !assessmentEndTime) {
                alert('Please fill in ALL Assessment scheduling details (Start Date/Time and End Date/Time).');
                return;
            }
            if (!interviewStartDate || !interviewStartTime || !interviewEndDate || !interviewEndTime) {
                alert('Please fill in ALL Interview scheduling details (Start Date/Time and End Date/Time).');
                return;
            }

            const assessStartDt = new Date(`${assessmentStartDate}T${assessmentStartTime}`);
            const assessEndDt = new Date(`${assessmentEndDate}T${assessmentEndTime}`);
            const interStartDt = new Date(`${interviewStartDate}T${interviewStartTime}`);
            const interEndDt = new Date(`${interviewEndDate}T${interviewEndTime}`);

            const now = new Date();
            now.setSeconds(0, 0); // Ignore exact seconds for 'now' comparison

            if (assessStartDt < now) {
                alert('Assessment "Available From" timing cannot be in the past.');
                return;
            }
            if (assessStartDt >= assessEndDt) {
                alert('Assessment "Available Until" must be strictly after "Available From". Please select a different timing.');
                return;
            }
            if (interStartDt < now) {
                alert('Interview "Available From" timing cannot be in the past.');
                return;
            }
            if (interStartDt >= interEndDt) {
                alert('Interview "Available Until" must be strictly after "Available From". Please select a different timing.');
                return;
            }
        }

        setIsAnalyzing(true);
        setResults(null);
        setProgress({ processed: 0, total: files.length });

        const formData = new FormData();
        files.forEach(file => {
            formData.append('resume', file);
        });
        formData.append('job_description', jobDescription);

        if (selectedRoleId === 'custom') {
            formData.append('role_title', customRoleTitle);
        } else {
            const role = jobRoles.find(r => r.id.toString() === selectedRoleId);
            if (role) formData.append('role_title', role.title);
        }

        formData.append('threshold', threshold);
        formData.append('experience_level', experienceLevel);

        if (matchMode === 'automatic') {
            formData.append('mcq_duration', mcqDuration);
            formData.append('coding_duration', codingDuration);
            formData.append('mcq_count', mcqCount);
            formData.append('coding_count', codingCount);
            formData.append('coding_tasks', JSON.stringify(codingChallenges.map(c => c.difficulty)));
            formData.append('pass_threshold', passThreshold);
            formData.append('interview_pass_threshold', interviewPassThreshold);
            formData.append('mcq_weight', mcqWeight);
            formData.append('same_questions_for_all', sameQuestionsForAll);
            formData.append('is_fully_automatic', true);

            if (assessmentStartDate && assessmentStartTime) {
                formData.append('assessment_available_from', new Date(`${assessmentStartDate}T${assessmentStartTime}`).toISOString());
            }
            if (assessmentEndDate && assessmentEndTime) {
                formData.append('assessment_available_until', new Date(`${assessmentEndDate}T${assessmentEndTime}`).toISOString());
            }
            if (interviewStartDate && interviewStartTime) {
                formData.append('interview_available_from', new Date(`${interviewStartDate}T${interviewStartTime}`).toISOString());
            }
            if (interviewEndDate && interviewEndTime) {
                formData.append('interview_available_until', new Date(`${interviewEndDate}T${interviewEndTime}`).toISOString());
            }
        }

        try {
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/match/`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const data = response.data;
            if (data.batch_id) {
                setBatchId(data.batch_id);
                setProgress({ processed: 0, total: data.total });
                console.log(`🚀 Batch started: ${data.batch_id} (${data.total} candidates)`);
            } else {
                setResults(Array.isArray(data) ? data : [data]);
                setIsAnalyzing(false);
            }
        } catch (error) {
            const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message || 'Analysis failed';
            alert(`Failed to analyze: ${errorMsg}`);
            setIsAnalyzing(false);
        }
    };

    // --- Retry failed extractions only ---
    const handleRetryFailed = async () => {
        if (!results) return;

        const failedResults = results.filter(r =>
            r.extraction_failed ||
            r.candidate_name === 'Extraction Failed' ||
            (!r.candidate_name && r.error)
        );

        const failedIds = failedResults
            .map(r => r.candidate_id)
            .filter(id => id != null);

        if (failedIds.length === 0) {
            alert('No failed extractions to retry.');
            return;
        }

        setIsRetrying(true);
        try {
            console.log(`🔄 Retrying extraction for ${failedIds.length} candidates...`);
            const response = await axios.post(`${API_BASE_URL}/ai-candidates/retry-extraction/`, {
                candidate_ids: failedIds,
                job_description: jobDescription,
                threshold: threshold
            });

            const retryData = response.data;
            console.log("🔄 ======= RETRY RESULTS ======= 🔄");
            console.table(retryData, ["candidate_name", "candidate_email", "match_percentage", "extraction_failed", "file_name"]);

            // Merge: replace only the failed results, keep screened ones untouched
            setResults(prev => {
                const retryMap = {};
                retryData.forEach(r => {
                    if (r.candidate_id) retryMap[r.candidate_id] = r;
                });
                return prev.map(existing => {
                    if (existing.candidate_id && retryMap[existing.candidate_id]) {
                        return retryMap[existing.candidate_id];
                    }
                    return existing;
                });
            });
        } catch (error) {
            const errorMsg = error.response?.data?.error || error.message || 'Retry failed';
            alert(`Retry failed: ${errorMsg}`);
        } finally {
            setIsRetrying(false);
        }
    };

    const getProgressColor = (percentage, isEligible) => {
        if (isEligible) return '#10B981';
        if (percentage >= 40) return '#F59E0B';
        return '#EF4444';
    };

    // Helper: determine if a result is a failed extraction
    const checkExtractionFailed = (data) => {
        return data.extraction_failed ||
            data.candidate_name === 'Extraction Failed' ||
            (!data.candidate_name && data.error);
    };

    return (
        <div className="resume-matcher-page">
            <div className="matcher-container" style={{ paddingTop: '1rem', marginTop: 0 }}>
                <header className="page-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
                    <h1>Resume <span style={{ color: '#6366F1' }}>Matcher</span></h1>
                    <p>AI-powered side-by-side analysis of candidate fit against specific role requirements.</p>
                </header>

                <div className="form-stack">
                    <div className="section-container">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                <i className="fa-solid fa-file-contract"></i>
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Job Description</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Define the benchmark for comparison.</p>
                            </div>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <select
                                className="modern-input"
                                value={selectedRoleId}
                                onChange={(e) => {
                                    const roleId = e.target.value;
                                    setSelectedRoleId(roleId);
                                    const role = jobRoles.find(r => r.id.toString() === roleId);
                                    if (role) {
                                        setJobDescription(role.description);
                                    } else {
                                        setJobDescription('');
                                    }
                                }}
                                style={{ width: '100%', padding: '0.75rem', borderRadius: '10px', border: '1px solid #E2E8F0', outline: 'none', background: '#F8FAFC' }}
                            >
                                <option value="">-- Select a Saved Role --</option>
                                {jobRoles.map(r => (
                                    <option key={r.id} value={r.id}>{r.title}</option>
                                ))}
                                <option value="custom">Custom (Type Manually)</option>
                            </select>

                            {selectedRoleId === 'custom' && (
                                <input
                                    type="text"
                                    value={customRoleTitle}
                                    onChange={(e) => setCustomRoleTitle(e.target.value)}
                                    placeholder="Enter Role Title (e.g. Senior Frontend Developer)"
                                    className="modern-input"
                                    style={{ width: '100%', padding: '0.75rem', borderRadius: '10px', border: '1px solid #E2E8F0', outline: 'none' }}
                                />
                            )}

                            {selectedRoleId === 'custom' && (
                                <textarea
                                    value={jobDescription}
                                    onChange={(e) => setJobDescription(e.target.value)}
                                    placeholder="Paste the job requirements, responsibilities, and qualifications..."
                                    className="modern-textarea"
                                />
                            )}
                        </div>
                    </div>

                    <div className="section-container">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                <i className="fa-solid fa-file-pdf"></i>
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Candidate Resumes</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Match multiple candidates at once.</p>
                            </div>
                        </div>

                        <div
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onClick={() => document.getElementById('resumeFile').click()}
                            className="upload-zone"
                        >
                            <input type="file" id="resumeFile" accept=".pdf" multiple style={{ display: 'none' }} onChange={handleFileChange} />

                            {files.length === 0 ? (
                                <>
                                    <div style={{
                                        width: '56px', height: '56px', background: 'white', color: '#6366F1',
                                        borderRadius: '16px', display: 'flex', alignItems: 'center',
                                        justifyContent: 'center', marginBottom: '1.5rem', fontSize: '1.5rem',
                                        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.05)'
                                    }}>
                                        <i className="fa-solid fa-cloud-arrow-up"></i>
                                    </div>
                                    <p style={{ fontSize: '1rem', fontWeight: '500', color: '#1E293B', marginBottom: '0.5rem' }}>Select Resumes</p>
                                    <p style={{ fontSize: '0.85rem', color: '#94A3B8' }}>Click or drag PDF files here</p>
                                </>
                            ) : (
                                <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
                                    {files.map((file, idx) => (
                                        <div key={idx} style={{
                                            background: 'white', padding: '1rem', borderRadius: '16px', border: '1px solid #E2E8F0',
                                            display: 'flex', alignItems: 'center', gap: '0.75rem', position: 'relative'
                                        }}>
                                            <i className="fa-solid fa-file-pdf" style={{ color: '#EF4444' }}></i>
                                            <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1E293B', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {file.name}
                                            </span>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                                                style={{
                                                    position: 'absolute', top: '-10px', right: '-10px', background: '#EF4444', color: 'white',
                                                    border: 'none', borderRadius: '50%', width: '22px', height: '22px', fontSize: '12px', cursor: 'pointer',
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 2px 8px rgba(239, 68, 68, 0.3)'
                                                }}
                                            >
                                                <i className="fa-solid fa-xmark"></i>
                                            </button>
                                        </div>
                                    ))}
                                    <div style={{
                                        border: '2px dashed #6366F1', borderRadius: '16px', padding: '1rem',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366F1', fontSize: '0.8rem', fontWeight: '700',
                                        background: 'rgba(99, 102, 241, 0.05)'
                                    }}>
                                        <i className="fa-solid fa-plus" style={{ marginRight: '6px' }}></i> Add More
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="section-container">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                <i className="fa-solid fa-user-tie"></i>
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Experience Level</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Select the target seniority for AI assessment generation.</p>
                            </div>
                        </div>
                        <select
                            className="modern-input"
                            value={experienceLevel}
                            onChange={(e) => setExperienceLevel(e.target.value)}
                            style={{ width: '100%', padding: '0.75rem', borderRadius: '10px', border: '1px solid #E2E8F0', outline: 'none', background: '#F8FAFC', color: '#1B254B', fontWeight: '500' }}
                        >
                            <option value="" disabled>Select Experience Level</option>
                            <option value="fresher">Fresher (0 Years)</option>
                            <option value="entry">Entry Level (0-2 Years)</option>
                            <option value="mid">Mid Level (2-5 Years)</option>
                            <option value="senior">Senior Level (5-10 Years)</option>
                            <option value="expert">Expert / Architect (10+ Years)</option>
                        </select>
                    </div>

                    <div className="section-container">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                <i className="fa-solid fa-percent"></i>
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Sensitivity Settings</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Set the minimum match score for qualification.</p>
                            </div>
                        </div>
                        <div className="threshold-container">
                            <div style={{ flex: 1 }}>
                                <input
                                    type="range" min="10" max="100" value={threshold}
                                    onChange={(e) => setThreshold(e.target.value)}
                                    style={{ width: '100%', accentColor: '#6366F1', height: '6px', cursor: 'pointer' }}
                                />
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem', color: '#94A3B8', fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase' }}>
                                    <span>LENIENT</span>
                                    <span>STRICT</span>
                                </div>
                            </div>
                            <div className="threshold-display">
                                <div style={{ fontSize: '0.65rem', color: '#6366F1', fontWeight: '500', textTransform: 'uppercase', marginBottom: '2px' }}>THRESHOLD</div>
                                <div style={{ fontSize: '1.25rem', fontWeight: '500', color: '#1E293B' }}>{threshold}%</div>
                            </div>
                        </div>
                    </div>

                    <div className="section-container mode-toggle-card">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                            <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                <i className="fa-solid fa-sliders"></i>
                            </div>
                            <div>
                                <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Matching Mode</h3>
                                <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Choose between AI automation or manual review.</p>
                            </div>
                        </div>
                        <div className="toggle-container">
                            <button type="button" className={`toggle-option ${matchMode === 'automatic' ? 'active' : ''}`} onClick={() => setMatchMode('automatic')}>
                                <i className="fa-solid fa-bolt"></i>
                                <span>Fully-Automatic</span>
                            </button>
                            <button type="button" className={`toggle-option ${matchMode === 'manual' ? 'active' : ''}`} onClick={() => setMatchMode('manual')}>
                                <i className="fa-solid fa-hand"></i>
                                <span>Manual Review</span>
                            </button>
                        </div>
                    </div>

                    {matchMode === 'automatic' && (
                        <div className="section-container automation-settings-card">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                <div className="module-icon-wrapper indigo-glow" style={{ width: '40px', height: '40px', borderRadius: '10px' }}>
                                    <i className="fa-solid fa-gear"></i>
                                </div>
                                <div>
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: '500', color: '#111827', margin: 0 }}>Automation Settings</h3>
                                    <p style={{ color: '#6B7280', fontSize: '0.85rem' }}>Configure the assessment that will be sent to candidates.</p>
                                </div>
                            </div>

                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(3, 1fr)',
                                gap: '1.25rem',
                                marginBottom: '1.5rem'
                            }}>
                                <div className="setting-item">
                                    <label>MCQ Questions</label>
                                    <input
                                        type="number"
                                        value={mcqCount}
                                        onChange={(e) => {
                                            const val = e.target.value;
                                            if (val === '') {
                                                setMcqCount('');
                                                return;
                                            }
                                            const num = parseInt(val, 10);
                                            if (!isNaN(num)) {
                                                setMcqCount(Math.min(num, 999));
                                            }
                                        }}
                                        className="modern-input"
                                        min="0"
                                        max="999"
                                    />
                                </div>
                                <div className="setting-item">
                                    <label>Coding Tasks</label>
                                    <input type="number" value={codingCount} onChange={(e) => handleCodingCountChange(e.target.value)} className="modern-input" min="0" max={MAX_CODING_TASKS} />
                                </div>
                                <div className="setting-item">
                                    <label>Assessment Duration (Mins)</label>
                                    <div className="duration-split-box">
                                        <div className="duration-col" style={!mcqDurationManual ? { background: '#F0FDF4' } : {}}>
                                            <label>MCQ</label>
                                            <input type="number" value={mcqDuration} onChange={(e) => { setMcqDuration(e.target.value === '' ? '' : parseInt(e.target.value)); setMcqDurationManual(true); }} min="1" max="120" />
                                            {!mcqDurationManual && <span className="mini-marker" style={{ background: '#22c55e', color: 'white' }}>AUTO</span>}
                                        </div>
                                        <div className="duration-col">
                                            <label>Coding</label>
                                            <input type="number" value={codingDuration} onChange={(e) => setCodingDuration(e.target.value === '' ? '' : parseInt(e.target.value))} min="5" max="180" />
                                            <span className="mini-marker">MIN</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {codingCount > 0 && (
                                <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1.25rem', marginBottom: '1.5rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                                        <span style={{ fontWeight: '500', color: '#1B254B', fontSize: '0.95rem' }}>Customize Coding Complexity</span>
                                        <span style={{ fontSize: '0.85rem', color: '#4f46e5', fontWeight: '500' }}>Points: {calculateTotalPoints()}</span>
                                    </div>
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                                        {codingChallenges.map((c, idx) => (
                                            <div key={c.id} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', background: '#F8F9FF', padding: '0.6rem 1rem', borderRadius: '12px', border: '1px solid #e0e7ff' }}>
                                                <span style={{ color: '#4318FF', fontWeight: '500', fontSize: '0.85rem' }}>Q{idx + 1}</span>
                                                <select value={c.difficulty} onChange={(e) => updateCodingDiff(c.id, e.target.value)}
                                                    style={{ flex: 1, border: 'none', background: 'transparent', fontWeight: '500', color: '#1B254B', cursor: 'pointer' }}>
                                                    <option value="" disabled>Select Level</option>
                                                    <option value="Easy">Easy</option>
                                                    <option value="Medium">Medium</option>
                                                    <option value="Hard">Hard</option>
                                                </select>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="setting-item" style={{ marginBottom: '1.5rem' }}>
                                <label>Assessment Pass Threshold ({passThreshold}%)</label>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <input type="range" min="10" max="100" value={passThreshold} onChange={(e) => setPassThreshold(e.target.value)} style={{ flex: 1, accentColor: '#6366F1' }} />
                                    <span style={{ minWidth: '40px', fontWeight: '500', color: '#1E293B' }}>{passThreshold}%</span>
                                </div>
                                <p style={{ margin: 0, fontSize: '0.75rem', color: '#6B7280' }}>Candidates scoring below this will be automatically rejected.</p>
                            </div>

                            <div className="setting-item" style={{ marginBottom: '1.5rem' }}>
                                <label>AI Interview Pass Threshold ({interviewPassThreshold}%)</label>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                    <input type="range" min="10" max="100" value={interviewPassThreshold} onChange={(e) => setInterviewPassThreshold(e.target.value)} style={{ flex: 1, accentColor: '#6366F1' }} />
                                    <span style={{ minWidth: '40px', fontWeight: '500', color: '#1E293B' }}>{interviewPassThreshold}%</span>
                                </div>
                                <p style={{ margin: 0, fontSize: '0.75rem', color: '#6B7280' }}>Candidates scoring below this in the AI interview will be automatically rejected.</p>
                            </div>

                            {/* Same questions for all toggle */}
                            {files.length > 1 && (
                                <div style={{
                                    marginBottom: '1.5rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.75rem',
                                    background: 'rgba(99, 102, 241, 0.03)',
                                    padding: '1rem',
                                    borderRadius: '12px',
                                    border: '1px solid #E0E7FF'
                                }}>
                                    <div className="modern-toggle">
                                        <input
                                            type="checkbox"
                                            id="same_questions_for_all"
                                            checked={sameQuestionsForAll}
                                            onChange={(e) => setSameQuestionsForAll(e.target.checked)}
                                            style={{ cursor: 'pointer' }}
                                        />
                                        <label htmlFor="same_questions_for_all"></label>
                                    </div>
                                    <div>
                                        <label htmlFor="same_questions_for_all" style={{ margin: 0, fontWeight: '600', color: '#1E293B', fontSize: '0.85rem', cursor: 'pointer' }}>
                                            Same questions for all candidates
                                        </label>
                                        <p style={{ margin: 0, fontSize: '0.7rem', color: '#64748B' }}>
                                            All screened candidates will receive the exact same question set instead of unique randomized ones.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* Scoring Weight Slider */}
                            <div style={{ marginBottom: '1.5rem', background: 'rgba(99,102,241,0.04)', padding: '1rem 1.25rem', borderRadius: '12px', border: '1px solid #E0E7FF' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                                    <div>
                                        <label style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1E293B', display: 'block', marginBottom: '2px' }}>Scoring Weights</label>
                                        <span style={{ fontSize: '0.75rem', color: '#64748B' }}>How MCQ and Coding contribute to the final score</span>
                                    </div>
                                    <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                                        <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#6366F1', background: '#EEF2FF', padding: '2px 8px', borderRadius: '20px' }}>MCQ {mcqWeight}%</span>
                                        <span style={{ fontSize: '0.7rem', color: '#94A3B8' }}>+</span>
                                        <span style={{ fontSize: '0.75rem', fontWeight: '700', color: '#10B981', background: '#ECFDF5', padding: '2px 8px', borderRadius: '20px' }}>Coding {100 - mcqWeight}%</span>
                                    </div>
                                </div>
                                <div style={{ position: 'relative', height: '6px', marginBottom: '0.4rem', display: 'flex', alignItems: 'center' }}>
                                    <div style={{ flex: 1, position: 'relative', height: '6px' }}>
                                        <div style={{ position: 'absolute', inset: 0, height: '6px', borderRadius: '6px', background: `linear-gradient(to right, #6366F1 ${mcqWeight}%, #10B981 ${mcqWeight}%)` }} />
                                        {/* The "Ball" */}
                                        <div style={{
                                            position: 'absolute',
                                            top: '50%',
                                            left: `${mcqWeight}%`,
                                            transform: 'translate(-50%, -50%)',
                                            width: '14px',
                                            height: '14px',
                                            borderRadius: '50%',
                                            background: '#FFFFFF',
                                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                                            border: '2px solid #6366F1',
                                            zIndex: 1,
                                            pointerEvents: 'none',
                                            transition: 'left 0.1s ease-out'
                                        }} />
                                        <input
                                            type="range" min="0" max="100" step="5"
                                            value={mcqWeight}
                                            onChange={(e) => setMcqWeight(parseInt(e.target.value))}
                                            disabled={mcqCount === 0 || codingCount === 0}
                                            style={{ position: 'absolute', inset: 0, opacity: 0, width: '100%', cursor: (mcqCount === 0 || codingCount === 0) ? 'not-allowed' : 'pointer', height: '100%', zIndex: 2 }}
                                        />
                                    </div>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: '#94A3B8', fontWeight: '600' }}>
                                    <span>MCQ Only</span><span>Coding Only</span>
                                </div>
                            </div>

                            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1.5rem', marginBottom: '1.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                                    <div className="module-icon-wrapper teal-glow" style={{ width: '32px', height: '32px', borderRadius: '8px' }}>
                                        <i className="fa-solid fa-clock"></i>
                                    </div>
                                    <h4 style={{ margin: 0, color: '#1B254B', fontSize: '0.95rem', fontWeight: '500' }}>Schedule Delivery</h4>
                                </div>

                                <p style={{ margin: '0 0 1rem', fontSize: '0.85rem', color: '#64748B', fontWeight: '700' }}>ASSESSMENT WINDOW</p>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                                        <label style={{ fontSize: '0.8rem', fontWeight: '700', color: '#374151' }}>
                                            <i className="fa-regular fa-calendar-check" style={{ marginRight: '0.4rem', color: '#6366F1' }}></i>
                                            Available From
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <input type="date" min={new Date().toISOString().split('T')[0]} value={assessmentStartDate} onChange={(e) => setAssessmentStartDate(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1.5, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                            <input type="time" value={assessmentStartTime} onChange={(e) => setAssessmentStartTime(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                                        <label style={{ fontSize: '0.8rem', fontWeight: '700', color: '#374151' }}>
                                            <i className="fa-regular fa-calendar-xmark" style={{ marginRight: '0.4rem', color: '#EF4444' }}></i>
                                            Available Until
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <input type="date" min={new Date().toISOString().split('T')[0]} value={assessmentEndDate} onChange={(e) => setAssessmentEndDate(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1.5, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                            <input type="time" value={assessmentEndTime} onChange={(e) => setAssessmentEndTime(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                        </div>
                                    </div>
                                </div>

                                <p style={{ margin: '0 0 1rem', fontSize: '0.85rem', color: '#64748B', fontWeight: '700' }}>INTERVIEW WINDOW</p>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                                        <label style={{ fontSize: '0.8rem', fontWeight: '700', color: '#374151' }}>
                                            <i className="fa-regular fa-calendar-check" style={{ marginRight: '0.4rem', color: '#6366F1' }}></i>
                                            Available From
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <input type="date" min={assessmentEndDate ? new Date(new Date(assessmentEndDate).getTime() + 86400000).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]} value={interviewStartDate} onChange={(e) => setInterviewStartDate(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1.5, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                            <input type="time" value={interviewStartTime} onChange={(e) => setInterviewStartTime(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
                                        <label style={{ fontSize: '0.8rem', fontWeight: '700', color: '#374151' }}>
                                            <i className="fa-regular fa-calendar-xmark" style={{ marginRight: '0.4rem', color: '#EF4444' }}></i>
                                            Available Until
                                        </label>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <input type="date" min={assessmentEndDate ? new Date(new Date(assessmentEndDate).getTime() + 86400000).toISOString().split('T')[0] : new Date().toISOString().split('T')[0]} value={interviewEndDate} onChange={(e) => setInterviewEndDate(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1.5, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                            <input type="time" value={interviewEndTime} onChange={(e) => setInterviewEndTime(e.target.value)} onClick={(e) => e.target.showPicker && e.target.showPicker()} style={{ flex: 1, padding: '0.75rem', border: '1px solid #E2E8F0', borderRadius: '10px', outline: 'none', background: '#F8FAFC', fontSize: '0.85rem' }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {!results && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', alignItems: 'center' }}>
                            <button onClick={handleMatch} disabled={isAnalyzing} className="generate-btn">
                                {isAnalyzing ? (
                                    <><i className="fa-solid fa-atom fa-spin"></i> {matchMode === 'automatic' ? 'Analyzing & Generating Assessments...' : 'Analyzing Candidate Profiles...'}</>
                                ) : (
                                    <>
                                        <i className="fa-solid fa-wand-magic-sparkles"></i>
                                        {matchMode === 'automatic' ? ' Start' : ' Check Resume'}
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>

                {isAnalyzing && (
                    <div className="section-container" style={{ marginTop: '2rem', textAlign: 'center' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                            <span style={{ fontSize: '0.9rem', fontWeight: '600', color: '#4B5563' }}>
                                {progress.total > 0 ? 'Processing Resumes...' : 'Initializing Analysis...'}
                            </span>
                            <span style={{ fontSize: '0.9rem', fontWeight: '700', color: '#6366F1' }}>
                                {progress.total > 0 ? `${progress.processed} of ${progress.total}` : 'Please wait'}
                            </span>
                        </div>
                        <div style={{ width: '100%', height: '10px', background: '#E5E7EB', borderRadius: '5px', overflow: 'hidden' }}>
                            <div style={{
                                width: progress.total > 0 ? `${(progress.processed / progress.total) * 100}%` : '10%',
                                height: '100%',
                                background: 'linear-gradient(90deg, #6366F1, #A855F7)',
                                transition: 'width 0.5s ease-out'
                            }}></div>
                        </div>
                        <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: '#6B7280', fontStyle: 'italic' }}>
                            <i className="fa-solid fa-circle-info" style={{ marginRight: '5px' }}></i>
                            {progress.total > 0
                                ? "Sequential processing active to respect API limits. This may take a few minutes for large batches."
                                : "Connecting to server and preparing files. Do not close this tab."
                            }
                        </p>
                    </div>
                )}

                {results && (
                    <div className="results-wrapper" style={{ marginTop: '2.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                            <h2 style={{ fontSize: '1.5rem', fontWeight: '500', color: '#1e293b', letterSpacing: '-0.02em' }}>Match <span style={{ color: '#6366F1' }}>Insights</span></h2>

                            {/* Retry button — only visible if there are failed extractions */}
                            {results.some(r => checkExtractionFailed(r)) && (
                                <button
                                    onClick={handleRetryFailed}
                                    disabled={isRetrying}
                                    style={{
                                        background: isRetrying ? '#94A3B8' : 'linear-gradient(135deg, #F59E0B, #EF4444)',
                                        color: 'white',
                                        border: 'none',
                                        padding: '0.6rem 1.25rem',
                                        borderRadius: '12px',
                                        fontSize: '0.85rem',
                                        fontWeight: '600',
                                        cursor: isRetrying ? 'not-allowed' : 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        boxShadow: '0 4px 12px rgba(239, 68, 68, 0.2)',
                                        transition: 'all 0.2s ease'
                                    }}
                                >
                                    <i className={`fa-solid ${isRetrying ? 'fa-spinner fa-spin' : 'fa-rotate-right'}`}></i>
                                    {isRetrying ? 'Retrying...' : `Retry Failed (${results.filter(r => checkExtractionFailed(r)).length})`}
                                </button>
                            )}
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                            {results.map((data, index) => {
                                const failed = checkExtractionFailed(data);
                                const percentage = data.match_percentage || 0;
                                const progressColor = failed ? '#EF4444' : getProgressColor(percentage, data.is_eligible);
                                const fileName = data.file_name || 'Unknown PDF';

                                return (
                                    <div key={index} className="glass-card result-card" style={failed ? { borderLeft: '4px solid #EF4444' } : {}}>
                                        <div className="score-circle" style={{ background: `conic-gradient(${progressColor} ${percentage * 3.6}deg, #f1f5f9 0deg)` }}>
                                            <div className="score-inner">
                                                <span className="score-value" style={{ color: progressColor }}>{percentage}%</span>
                                                <span className="score-label">MATCH</span>
                                            </div>
                                        </div>

                                        <div style={{ flex: 1 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                                                {failed ? (
                                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                                        <h4 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '500', color: '#EF4444' }}>
                                                            <i className="fa-solid fa-triangle-exclamation" style={{ marginRight: '0.5rem' }}></i>
                                                            Extraction Failed
                                                        </h4>
                                                        <span style={{
                                                            fontSize: '0.8rem',
                                                            color: '#64748b',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            gap: '0.35rem'
                                                        }}>
                                                            <i className="fa-solid fa-file-pdf" style={{ color: '#EF4444', fontSize: '0.75rem' }}></i>
                                                            {fileName}
                                                        </span>
                                                    </div>
                                                ) : (
                                                    <h4 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '500', color: '#1e293b' }}>
                                                        {data.candidate_name}
                                                    </h4>
                                                )}
                                                <span className="status-tag" style={{
                                                    background: failed ? 'rgba(239, 68, 68, 0.1)' : data.is_eligible ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                                    color: failed ? '#dc2626' : data.is_eligible ? '#059669' : '#dc2626'
                                                }}>
                                                    {failed ? 'EXTRACTION FAILED' : data.is_eligible ? 'ELIGIBLE' : 'GAP DETECTED'}
                                                </span>
                                            </div>
                                            <p style={{ margin: 0, color: '#64748b', fontSize: '1rem', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
                                                {data.summary || 'AI has analyzed this profile against role expectations.'}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ResumeMatcher;
