import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CreateAssessment.css';

const MAX_CODING_TASKS = 99;
const STORAGE_KEY = 'ai_assessment_create_form_data';

const CreateAssessment = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [progressMsg, setProgressMsg] = useState('');
    const [formData, setFormData] = useState({
        job_description: '',
        skills: '',
        experience_level: '',  // NEW: Add experience level to form data
        num_mcqs: 10,
        num_coding: 1,
        coding_challenges: [{ id: 1, difficulty: 'Medium' }],
        mcq_time: 10,       // Auto-calculated: 1 min per MCQ, overridable
        coding_time: 30,    // Manually entered by recruiter
        mcqTimeManual: false, // Track if recruiter manually overrode MCQ time
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        pass_threshold: 60,
        customRoleTitle: '',
        num_applicants: 1,
        same_questions_for_all: false,
        mcq_weight: 40
    });


    // Job Roles State
    const [jobRoles, setJobRoles] = useState([]);
    const [selectedRoleId, setSelectedRoleId] = useState('');

    // --- Persistence Logic ---
    const isDirty = React.useRef(false);
    const isInitialRender = React.useRef(true);

    // --- Ghost Generation Abort Logic ---
    const cancelTokenRef = React.useRef(null);
    const isGeneratingRef = React.useRef(false);

    React.useEffect(() => {
        const handleBeforeUnload = (e) => {
            if (isGeneratingRef.current && cancelTokenRef.current) {
                // Send synchronous beacon to abort
                const url = `${API_BASE_URL}/ai/cancel-generation/`;
                const payload = JSON.stringify({ cancel_token: cancelTokenRef.current });
                navigator.sendBeacon(url, payload);
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);

        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            // Also handle SPA unmount
            if (isGeneratingRef.current && cancelTokenRef.current) {
                const url = `${API_BASE_URL}/ai/cancel-generation/`;
                const payload = JSON.stringify({ cancel_token: cancelTokenRef.current });
                navigator.sendBeacon(url, payload);
            }
        };
    }, []);

    React.useEffect(() => {
        // Never restore data on refresh per user request
        sessionStorage.removeItem(STORAGE_KEY);
        isDirty.current = false;
        window._assessment_init = true;

    }, []);

    const initialDataHash = React.useRef(null);
    if (!initialDataHash.current) {
        initialDataHash.current = JSON.stringify({
            formData, selectedRoleId
        });
    }

    React.useEffect(() => {
        const dataToSave = {
            formData: { ...formData },
            selectedRoleId
        };
        const currentDataStr = JSON.stringify(dataToSave);

        if (!isDirty.current && currentDataStr === initialDataHash.current) {
            return;
        }

        isDirty.current = true;
        sessionStorage.setItem(STORAGE_KEY, currentDataStr);
    }, [formData, selectedRoleId]);

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

    const handleChange = (id, value) => {
        if (id === 'num_coding') {
            if (value === '' || value === null || value === undefined) {
                setFormData(prev => ({ ...prev, num_coding: '' }));
                return;
            }
            const count = parseInt(value);
            if (isNaN(count)) return;
            const limitedCount = Math.min(Math.max(count, 0), MAX_CODING_TASKS);

            setFormData(prev => {
                let newChallenges = [...prev.coding_challenges];
                if (limitedCount > newChallenges.length) {
                    // Add new challenges
                    for (let i = newChallenges.length; i < limitedCount; i++) {
                        newChallenges.push({ id: Date.now() + i, difficulty: 'Medium' });
                    }
                } else if (limitedCount < newChallenges.length) {
                    // Remove excess challenges
                    newChallenges = newChallenges.slice(0, limitedCount);
                }

                // Auto-adjust weight: if coding is 0, MCQ gets 100%
                let newWeight = prev.mcq_weight;
                if (limitedCount === 0) {
                    newWeight = 100;
                } else if (prev.num_mcqs === 0 && prev.mcq_weight === 100) {
                    // Coding was just re-added while MCQ is still 0, keep at 0% MCQ
                    newWeight = 0;
                }

                return {
                    ...prev,
                    num_coding: limitedCount,
                    coding_challenges: newChallenges,
                    mcq_weight: newWeight
                };
            });
            return;
        }

        if (id === 'num_mcqs') {
            if (value === '' || value === null || value === undefined) {
                setFormData(prev => ({
                    ...prev,
                    num_mcqs: ''
                }));
                return;
            }
            const count = parseInt(value, 10);
            if (isNaN(count)) return;
            const numVal = Math.min(Math.max(count, 0), 999);

            setFormData(prev => {
                // Auto-adjust weight: if MCQs is 0, Coding gets 100%
                let newWeight = prev.mcq_weight;
                if (numVal === 0) {
                    newWeight = 0;
                } else if (prev.num_coding === 0 && prev.mcq_weight === 0) {
                    // MCQ was just re-added while coding is still 0, keep at 100% MCQ
                    newWeight = 100;
                }
                // Auto-calculate MCQ time (1 min per question) unless manually overridden
                const autoMcqTime = prev.mcqTimeManual ? prev.mcq_time : (numVal || 0);
                return {
                    ...prev,
                    num_mcqs: numVal,
                    mcq_weight: newWeight,
                    mcq_time: autoMcqTime,
                    mcqTimeManual: prev.mcqTimeManual
                };
            });
            return;
        }

        setFormData(prev => ({
            ...prev,
            [id]: value
        }));
    };

    const updateCodingDifficulty = (id, diff) => {
        setFormData(prev => ({
            ...prev,
            coding_challenges: prev.coding_challenges.map(c =>
                c.id === id ? { ...c, difficulty: diff } : c
            )
        }));
    };

    const calculateMcqMix = (total) => {
        const hard = Math.floor(total * 0.2);
        const medium = Math.floor(total * 0.3);
        const easy = total - hard - medium;
        return { easy, medium, hard };
    };

    const calculateTotalPoints = () => {
        const mcqPoints = formData.num_mcqs * 1; // 1 pt per MCQ
        const codingPoints = formData.coding_challenges.reduce((sum, c) => {
            const weight = c.difficulty === 'Easy' ? 100 : c.difficulty === 'Medium' ? 200 : 300;
            return sum + weight;
        }, 0);
        return mcqPoints + codingPoints;
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();

        if (!formData.job_description.trim()) {
            alert('Please enter a Job Description before generating.');
            return;
        }
        if (!formData.skills.trim()) {
            alert('Please enter Target Skills before generating.');
            return;
        }
        if (!formData.experience_level) {
            alert('Please select an Experience Level before generating.');
            return;
        }
        if (!formData.num_mcqs && formData.num_mcqs !== 0) {
            alert('Please enter a valid number of MCQ questions.');
            return;
        }
        if (!formData.num_coding && formData.num_coding !== 0) {
            alert('Please enter a valid number of Coding tasks.');
            return;
        }
        if (formData.num_mcqs === 0 && formData.num_coding === 0) {
            alert('Cannot generate an empty assessment! Please add at least one MCQ or Coding task.');
            return;
        }
        if (!formData.mcq_time && formData.num_mcqs > 0) {
            alert('Please enter a valid MCQ Time.');
            return;
        }
        if (!formData.coding_time && formData.num_coding > 0) {
            alert('Please enter a valid Coding Time.');
            return;
        }
        if (!formData.num_applicants) {
            alert('Please enter the number of applicants.');
            return;
        }

        // Mandatory Scheduling Validation
        const now = new Date();
        if (!formData.start_date || !formData.start_time) {
            alert('Please provide a complete starting Date and Time for the assessment.');
            return;
        }
        const startDateTime = new Date(`${formData.start_date}T${formData.start_time}`);
        if (startDateTime < now) {
            alert('The assessment start date and time cannot be in the past.');
            return;
        }

        if (!formData.end_date || !formData.end_time) {
            alert('Please provide a complete ending Date and Time for the assessment.');
            return;
        }
        const endDateTime = new Date(`${formData.end_date}T${formData.end_time}`);
        if (endDateTime < now) {
            alert('The assessment end date and time cannot be in the past.');
            return;
        }
        if (endDateTime <= startDateTime) {
            alert('The end date and time must be after the start date and time.');
            return;
        }

        setLoading(true);
        const currentToken = Date.now().toString() + Math.random().toString(36).substring(2, 11);
        cancelTokenRef.current = currentToken;
        isGeneratingRef.current = true;

        const mcqMix = calculateMcqMix(formData.num_mcqs);
        const payload = {
            job_description: formData.job_description,
            required_skills: formData.skills,
            experience_level: formData.experience_level,  // NEW: Include experience level in API payload
            cancel_token: currentToken,

            // Include Job Title for persistence
            role_title: selectedRoleId === 'custom' ? formData.customRoleTitle : (jobRoles.find(r => r.id.toString() === selectedRoleId)?.title || formData.skills),

            mcq_easy: mcqMix.easy,
            mcq_medium: mcqMix.medium,
            mcq_hard: mcqMix.hard,
            coding_tasks: formData.coding_challenges.map(c => c.difficulty),
            mcq_duration: formData.mcq_time,
            coding_duration: formData.coding_time,
            pass_threshold: formData.pass_threshold,
            total_possible_points: calculateTotalPoints(),
            num_applicants: formData.num_applicants,
            same_questions_for_all: formData.same_questions_for_all,
            mcq_weight: formData.mcq_weight,
            available_from: (formData.start_date && formData.start_time) ? new Date(`${formData.start_date}T${formData.start_time}`).toISOString() : null,
            available_until: (formData.end_date && formData.end_time) ? new Date(`${formData.end_date}T${formData.end_time}`).toISOString() : null
        };


        try {
            const response = await axios.post(`${API_BASE_URL}/ai/generate/`, payload, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.status === 200 || response.status === 201 || response.status === 202) {
                const taskId = response.data.task_id;
                
                if (taskId) {
                    setProgressMsg('Initializing generation task...');
                    
                    const pollInterval = setInterval(async () => {
                        try {
                            const statusRes = await axios.get(`${API_BASE_URL}/ai/generation-status/${taskId}/`);
                            const statusData = statusRes.data;
                            
                            if (statusData.status === 'completed') {
                                clearInterval(pollInterval);
                                alert('Assessment Generated Successfully!');
                                sessionStorage.removeItem(STORAGE_KEY);
                                setLoading(false);
                                isGeneratingRef.current = false;
                                navigate('/ai-assessments');
                            } else if (statusData.status === 'failed') {
                                clearInterval(pollInterval);
                                alert(`Generation failed: ${statusData.message || statusData.error}`);
                                setLoading(false);
                                isGeneratingRef.current = false;
                                setProgressMsg('');
                            } else {
                                setProgressMsg(statusData.progress || 'Processing...');
                            }
                        } catch (err) {
                            console.error('Error polling status:', err);
                        }
                    }, 3000);
                    
                    // Keep loading true, handled by polling
                    return;
                } else {
                    alert('Assessment Generated Successfully!');
                    sessionStorage.removeItem(STORAGE_KEY);
                    setLoading(false);
                    isGeneratingRef.current = false;
                    navigate('/ai-assessments');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            const errMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message || 'Generation failed. Please try again.';
            alert(`Generation failed: ${errMsg}`);
            setLoading(false);
            isGeneratingRef.current = false;
            setProgressMsg('');
        }
    };

    return (
        <div className="create-assessment-page" style={{ paddingTop: 0 }}>
            <div className="assessment-container" style={{ paddingTop: '1rem', marginTop: 0 }}>
                <header className="assessment-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
                    <h1 style={{ fontSize: '1.625rem', fontWeight: '700', color: '#111827', margin: 0, letterSpacing: '-0.025em' }}>Create <span style={{ color: '#6366F1', fontWeight: '400' }}>Smart</span> Assessment</h1>
                    <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem' }}>Our intelligent AI transforms your requirements into a precision-engineered technical evaluation.</p>
                </header>

                <div className="section-container">
                    <SectionHeader title="Role Context" />
                    <div className="form-group">
                        <label>Job Requirements</label>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <select
                                className="modern-input"
                                style={{ width: '100%', padding: '0.85rem', borderRadius: '10px', border: '1px solid #E2E8F0', outline: 'none', background: 'white' }}
                                value={selectedRoleId}
                                onChange={(e) => {
                                    const roleId = e.target.value;
                                    setSelectedRoleId(roleId);
                                    const role = jobRoles.find(r => r.id.toString() === roleId);
                                    if (role) {
                                        handleChange('job_description', role.description);
                                        handleChange('skills', role.title); // Populate skills with title to satisfy validation
                                        handleChange('customRoleTitle', ''); // Clear custom title if switching from custom
                                    } else {
                                        handleChange('job_description', '');
                                        handleChange('skills', '');
                                        handleChange('customRoleTitle', '');
                                    }
                                }}
                            >
                                <option value="">-- Select a Saved Role --</option>
                                {jobRoles.map(r => (
                                    <option key={r.id} value={r.id}>{r.title}</option>
                                ))}
                                <option value="custom">Custom (Type Manually)</option>
                            </select>

                            {selectedRoleId === 'custom' && (
                                <div className="input-group" style={{ marginTop: '1rem' }}>
                                    <label>Role Title</label>
                                    <input
                                        type="text"
                                        value={formData.customRoleTitle}
                                        onChange={(e) => handleChange('customRoleTitle', e.target.value)}
                                        placeholder="e.g. Senior Frontend Developer"
                                        className="modern-input"
                                    />
                                </div>
                            )}
                        </div>
                    </div>
                    {selectedRoleId === 'custom' && (
                        <div className="form-group">
                            <label>Target Skills</label>
                            <input
                                type="text"
                                placeholder="e.g. React, Node.js, Python, System Design..."
                                value={formData.skills}
                                onChange={(e) => handleChange('skills', e.target.value)}
                                className="modern-input"
                            />
                        </div>
                    )}

                    {/* NEW: Experience Level Section */}
                    {selectedRoleId && (
                        <div className="form-group" style={{ marginTop: '1.5rem' }}>
                            <label style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontSize: '0.95rem',
                                fontWeight: '600',
                                color: '#374151',
                                marginBottom: '0.75rem'
                            }}>
                                <i className="fa-solid fa-user-graduate" style={{ color: '#6366F1', fontSize: '0.9rem' }}></i>
                                Experience Level
                            </label>
                            <select
                                value={formData.experience_level}
                                onChange={(e) => handleChange('experience_level', e.target.value)}
                                className="modern-input"
                                style={{
                                    width: '100%',
                                    padding: '0.85rem 1rem',
                                    borderRadius: '10px',
                                    border: '1px solid #E2E8F0',
                                    outline: 'none',
                                    background: 'white',
                                    fontSize: '0.9rem',
                                    color: '#374151',
                                    cursor: 'pointer',
                                    transition: 'border-color 0.2s, box-shadow 0.2s'
                                }}
                            >
                                <option value="">Select candidate experience level...</option>
                                <option value="fresher">Fresher (0 Years)</option>
                                <option value="entry">Entry (0-2 years)</option>
                                <option value="mid">Mid (2-5 years)</option>
                                <option value="senior">Senior (5-10 years)</option>
                                <option value="expert">Expert (10+ years)</option>
                            </select>
                            <p style={{
                                fontSize: '0.8rem',
                                color: '#6B7280',
                                marginTop: '0.5rem',
                                marginBottom: 0,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.4rem'
                            }}>
                                <i className="fa-solid fa-lightbulb" style={{ color: '#F59E0B', fontSize: '0.75rem' }}></i>
                                AI will generate questions appropriate for this experience level
                            </p>
                        </div>
                    )}

                    {selectedRoleId && (
                        <div className="form-group" style={{ marginTop: '1.5rem' }}>
                            <label>Detailed Job Description</label>
                            <textarea
                                placeholder="Paste the full job description here. The AI will use this to generate precise questions."
                                value={formData.job_description}
                                onChange={(e) => handleChange('job_description', e.target.value)}
                                style={{
                                    width: '100%',
                                    minHeight: '150px',
                                    padding: '1rem',
                                    borderRadius: '12px',
                                    border: '1px solid #E2E8F0',
                                    fontSize: '0.9rem',
                                    lineHeight: '1.5',
                                    outline: 'none',
                                    transition: 'border-color 0.2s',
                                    fontFamily: 'inherit',
                                    resize: 'vertical',
                                    background: 'white'
                                }}
                            />
                        </div>
                    )}
                </div>

                <div className="section-container">
                    <SectionHeader title="Structure & Difficulty" />

                    {/* Reverted Parameter Row (from screenshot) */}
                    <div className="parameters-grid">
                        <div className="form-group">
                            <label>MCQ Questions</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="0" max="999"
                                    value={formData.num_mcqs}
                                    onChange={(e) => handleChange('num_mcqs', e.target.value)}
                                    onBlur={() => { if (formData.num_mcqs === '') handleChange('num_mcqs', 10); }}
                                />
                                <span className="marker">{formData.num_mcqs}</span>
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Coding Tasks</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="0" max={MAX_CODING_TASKS}
                                    value={formData.num_coding}
                                    onChange={(e) => handleChange('num_coding', e.target.value)}
                                    onBlur={() => { if (formData.num_coding === '') handleChange('num_coding', 1); }}
                                />
                                <span className="marker">{formData.num_coding}</span>
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Assessment Duration (Mins)</label>
                            <div className="duration-split-box">
                                <div className="duration-col" style={!formData.mcqTimeManual ? { background: '#F0FDF4' } : {}}>
                                    <label>MCQ</label>
                                    <input
                                        type="number" min="1" max="120"
                                        value={formData.mcq_time}
                                        onChange={(e) => {
                                            const val = parseInt(e.target.value) || 0;
                                            setFormData(prev => ({ ...prev, mcq_time: val, mcqTimeManual: true }));
                                        }}
                                    />
                                    <span className="mini-marker" style={!formData.mcqTimeManual ? { background: '#22c55e', color: 'white' } : {}}>
                                        {!formData.mcqTimeManual ? 'AUTO' : 'MIN'}
                                    </span>
                                </div>
                                <div className="duration-col">
                                    <label>Coding</label>
                                    <input
                                        type="number" min="5" max="180"
                                        value={formData.coding_time}
                                        onChange={(e) => handleChange('coding_time', parseInt(e.target.value) || 0)}
                                    />
                                    <span className="mini-marker">MIN</span>
                                </div>
                            </div>
                        </div>
                        <div className="form-group">
                            <label>No. of Applicants</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="1" max="999"
                                    value={formData.num_applicants || ''}
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        if (val === '') {
                                            handleChange('num_applicants', '');
                                        } else {
                                            const n = Math.min(parseInt(val) || 1, 999);
                                            handleChange('num_applicants', n);
                                            if (n <= 1) handleChange('same_questions_for_all', false);
                                        }
                                    }}
                                />
                                <span className="marker">👥</span>
                            </div>
                        </div>
                    </div>

                    {/* Case 3 Toggle: Same questions for all */}
                    {formData.num_applicants > 1 && (
                        <div style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem', background: '#F8FAFC', padding: '1rem', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
                            <div className="modern-toggle">
                                <input
                                    type="checkbox"
                                    id="same_questions_for_all"
                                    checked={formData.same_questions_for_all}
                                    onChange={(e) => handleChange('same_questions_for_all', e.target.checked)}
                                    style={{ display: 'none' }}
                                />
                                <label
                                    htmlFor="same_questions_for_all"
                                    style={{
                                        position: 'relative',
                                        display: 'inline-block',
                                        width: '44px',
                                        height: '24px',
                                        background: formData.same_questions_for_all ? '#6366F1' : '#CBD5E1',
                                        borderRadius: '20px',
                                        cursor: 'pointer',
                                        transition: 'background 0.3s'
                                    }}
                                >
                                    <span style={{
                                        position: 'absolute',
                                        top: '2px',
                                        left: formData.same_questions_for_all ? '22px' : '2px',
                                        width: '20px',
                                        height: '20px',
                                        background: 'white',
                                        borderRadius: '50%',
                                        transition: 'left 0.3s'
                                    }} />
                                </label>
                            </div>
                            <div>
                                <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: '600', color: '#1E293B' }}>Same questions for all candidates</h4>
                                <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748B' }}>Every candidate will receive the exact same assessment pool instead of unique randomized sets.</p>
                            </div>
                        </div>
                    )}


                    {/* Scoring Weight Slider */}
                    <div style={{ marginBottom: '2rem', background: '#F8FAFC', padding: '1.25rem 1.5rem', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <div>
                                <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: '600', color: '#1E293B' }}>Scoring Weights</h4>
                                <p style={{ margin: 0, fontSize: '0.8rem', color: '#64748B' }}>Adjust how MCQ and Coding scores contribute to the final result.</p>
                            </div>
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#6366F1', background: '#EEF2FF', padding: '3px 10px', borderRadius: '20px' }}>MCQ {formData.mcq_weight}%</span>
                                <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>+</span>
                                <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#8B5CF6', background: '#F5F3FF', padding: '3px 10px', borderRadius: '20px' }}>Coding {100 - formData.mcq_weight}%</span>
                            </div>
                        </div>
                        <div style={{ position: 'relative', marginBottom: '0.5rem', display: 'flex', alignItems: 'center' }}>
                            <div style={{ flex: 1, position: 'relative', height: '8px' }}>
                                <div style={{ position: 'absolute', inset: 0, height: '8px', borderRadius: '8px', background: `linear-gradient(to right, #6366F1 ${formData.mcq_weight}%, #8B5CF6 ${formData.mcq_weight}%)` }} />
                                {/* The "Ball" */}
                                <div style={{
                                    position: 'absolute',
                                    top: '50%',
                                    left: `${formData.mcq_weight}%`,
                                    transform: 'translate(-50%, -50%)',
                                    width: '16px',
                                    height: '16px',
                                    borderRadius: '50%',
                                    background: '#FFFFFF',
                                    boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
                                    border: '3px solid #6366F1',
                                    zIndex: 1,
                                    pointerEvents: 'none',
                                    transition: 'left 0.1s ease-out'
                                }} />
                                <input
                                    type="range" min="0" max="100" step="5"
                                    value={formData.mcq_weight}
                                    onChange={(e) => handleChange('mcq_weight', parseInt(e.target.value))}
                                    disabled={formData.num_mcqs === 0 || formData.num_coding === 0}
                                    style={{ position: 'absolute', inset: 0, opacity: 0, width: '100%', cursor: (formData.num_mcqs === 0 || formData.num_coding === 0) ? 'not-allowed' : 'pointer', height: '100%', margin: 0, zIndex: 2 }}
                                />
                            </div>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94A3B8', fontWeight: '600' }}>
                            <span>MCQ Only (100%)</span>
                            <span>Coding Only (100%)</span>
                        </div>
                    </div>

                    {/* Dynamic Complexity Detail (only if tasks > 0) */}
                    {formData.num_coding > 0 && (
                        <div className="coding-detail-section" style={{ borderTop: '1px solid #e2e8f0', paddingTop: '2rem', marginBottom: '2rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                                <h3 style={{ margin: 0, color: '#1B254B', fontSize: '1.1rem', fontWeight: '700' }}>Customize Coding Complexity</h3>
                                <div style={{ background: '#f0f2f5', padding: '0.4rem 1rem', borderRadius: '12px', fontSize: '0.9rem', color: '#64748b', fontWeight: '600' }}>
                                    Points: <span style={{ color: '#4f46e5' }}>{calculateTotalPoints()}</span>
                                </div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                                {formData.coding_challenges.map((challenge, index) => (
                                    <div key={challenge.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: '#F8F9FF', padding: '0.8rem 1.2rem', borderRadius: '15px', border: '1px solid #e0e7ff' }}>
                                        <span style={{ color: '#4318FF', fontWeight: '800', fontSize: '0.9rem', opacity: 0.7 }}>Q{index + 1}</span>
                                        <select
                                            value={challenge.difficulty}
                                            onChange={(e) => updateCodingDifficulty(challenge.id, e.target.value)}
                                            style={{ flex: 1, border: 'none', background: 'transparent', fontWeight: '600', color: '#1B254B', cursor: 'pointer' }}
                                        >
                                            <option value="Easy">Easy</option>
                                            <option value="Medium">Medium</option>
                                            <option value="Hard">Hard</option>
                                        </select>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="threshold-section">
                        <div className="threshold-info">
                            <h3>Pass Threshold (%)</h3>
                            <div className="circle-progress">
                                <svg viewBox="0 0 100 100">
                                    <defs>
                                        <linearGradient id="threshold-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                            <stop offset="0%" stopColor="#4f46e5" />
                                            <stop offset="100%" stopColor="#9333ea" />
                                        </linearGradient>
                                    </defs>
                                    <circle className="bg" cx="50" cy="50" r="45" />
                                    <circle
                                        className="progress"
                                        cx="50" cy="50" r="45"
                                        style={{ strokeDashoffset: 283 - (283 * formData.pass_threshold) / 100 }}
                                    />
                                </svg>
                                <span className="percentage">{formData.pass_threshold}%</span>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={formData.pass_threshold}
                                onChange={(e) => handleChange('pass_threshold', parseInt(e.target.value))}
                            />
                            <p className="hint">Minimum score required for candidate success</p>
                        </div>

                        <div className="availability-grid">
                            <div className="form-group">
                                <label>Available From</label>
                                <div className="datetime-row">
                                    <input
                                        type="date"
                                        min={new Date().toISOString().split('T')[0]}
                                        value={formData.start_date}
                                        onChange={(e) => handleChange('start_date', e.target.value)}
                                        onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                    />
                                    <input
                                        type="time"
                                        value={formData.start_time}
                                        onChange={(e) => handleChange('start_time', e.target.value)}
                                        onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                    />
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Available Until</label>
                                <div className="datetime-row">
                                    <input
                                        type="date"
                                        min={new Date().toISOString().split('T')[0]}
                                        value={formData.end_date}
                                        onChange={(e) => handleChange('end_date', e.target.value)}
                                        onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                    />
                                    <input
                                        type="time"
                                        value={formData.end_time}
                                        onChange={(e) => handleChange('end_time', e.target.value)}
                                        onClick={(e) => e.target.showPicker && e.target.showPicker()}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <button
                    className={`generate-btn ${loading ? 'loading' : ''}`}
                    onClick={handleSubmit}
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <span className="spinner"></span>
                            {progressMsg || 'Generating Assessment...'}
                        </>
                    ) : (
                        <>
                            🚀 Generate Assessment
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

const SectionHeader = ({ title }) => (
    <div className="section-header" style={{ marginBottom: '1.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#111827', margin: 0 }}>{title}</h2>
    </div>
);

export default CreateAssessment;