import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CreateAssessment.css';

const MAX_CODING_TASKS = 50;
const STORAGE_KEY = 'ai_assessment_create_form_data';

const CreateAssessment = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        job_description: '',
        skills: '',
        num_mcqs: 10,
        num_coding: 1,
        coding_challenges: [{ id: 1, difficulty: 'Medium' }],
        coding_time: 60,
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        pass_threshold: 60,
        customRoleTitle: '',
        num_applicants: 1
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

                return {
                    ...prev,
                    num_coding: limitedCount,
                    coding_challenges: newChallenges
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
        const mcqPoints = formData.num_mcqs * 20;
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
        if (!formData.num_mcqs && formData.num_mcqs !== 0) {
            alert('Please enter a valid number of MCQ questions.');
            return;
        }
        if (!formData.num_coding && formData.num_coding !== 0) {
            alert('Please enter a valid number of Coding tasks.');
            return;
        }
        if (!formData.coding_time) {
            alert('Please enter a valid Total Time (Duration).');
            return;
        }
        if (!formData.num_applicants) {
            alert('Please enter the number of applicants.');
            return;
        }

        // Mandatory Scheduling Validation
        if (!formData.start_date || !formData.start_time) {
            alert('Please provide a complete starting Date and Time for the assessment.');
            return;
        }
        if (!formData.end_date || !formData.end_time) {
            alert('Please provide a complete ending Date and Time for the assessment.');
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
            cancel_token: currentToken,

            // Include Job Title for persistence
            role_title: selectedRoleId === 'custom' ? formData.customRoleTitle : (jobRoles.find(r => r.id.toString() === selectedRoleId)?.title || formData.skills),

            mcq_easy: mcqMix.easy,
            mcq_medium: mcqMix.medium,
            mcq_hard: mcqMix.hard,
            coding_tasks: formData.coding_challenges.map(c => c.difficulty),
            duration: formData.coding_time,
            pass_threshold: formData.pass_threshold,
            total_possible_points: calculateTotalPoints(),
            num_applicants: formData.num_applicants,
            available_from: (formData.start_date && formData.start_time) ? new Date(`${formData.start_date}T${formData.start_time}`).toISOString() : null,
            available_until: (formData.end_date && formData.end_time) ? new Date(`${formData.end_date}T${formData.end_time}`).toISOString() : null
        };

        try {
            const response = await axios.post(`${API_BASE_URL}/ai/generate/`, payload, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.status === 200 || response.status === 201) {
                alert('Assessment Generated Successfully!');
                sessionStorage.removeItem(STORAGE_KEY); // Explicitly wipe data upon clean completion
                navigate('/ai-assessments');
            }
        } catch (error) {
            console.error('Error:', error);
            const errMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message || 'Generation failed. Please try again.';
            alert(`Generation failed: ${errMsg}`);
        } finally {
            setLoading(false);
            isGeneratingRef.current = false;
        }
    };

    return (
        <div className="create-assessment-page" style={{ paddingTop: 0 }}>
            <div className="assessment-container" style={{ paddingTop: '1rem', marginTop: 0 }}>
                <header className="assessment-header" style={{ marginBottom: '1.5rem', marginTop: 0 }}>
                    <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#111827', margin: 0, letterSpacing: '-0.025em' }}>Create <span style={{ color: '#6366F1', fontWeight: '400' }}>Smart</span> Assessment</h1>
                    <p style={{ color: '#6b7280', fontSize: '0.95rem', marginTop: '0.25rem' }}>Our intelligent AI transforms your requirements into a precision-engineered technical evaluation.</p>
                </header>

                <div>
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
                            />
                        </div>
                    )}
                </div>

                <div>
                    <SectionHeader title="Structure & Difficulty" />

                    {/* Reverted Parameter Row (from screenshot) */}
                    <div className="parameters-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2.5rem' }}>
                        <div className="form-group">
                            <label>MCQ Questions</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="0" max="50"
                                    value={formData.num_mcqs}
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        if (val === '') {
                                            handleChange('num_mcqs', '');
                                        } else {
                                            handleChange('num_mcqs', parseInt(val) || 0);
                                        }
                                    }}
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
                            <label>Total Time (Mins)</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="10" max="180"
                                    value={formData.coding_time}
                                    onChange={(e) => handleChange('coding_time', parseInt(e.target.value) || 0)}
                                />
                                <span className="marker">⌛</span>
                            </div>
                        </div>
                        <div className="form-group">
                            <label>No. of Applicants</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="1" max="1000"
                                    value={formData.num_applicants || ''}
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        if (val === '') {
                                            handleChange('num_applicants', '');
                                        } else {
                                            handleChange('num_applicants', parseInt(val) || 1);
                                        }
                                    }}
                                />
                                <span className="marker">👥</span>
                            </div>
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
                                    />
                                    <input
                                        type="time"
                                        value={formData.start_time}
                                        onChange={(e) => handleChange('start_time', e.target.value)}
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
                                    />
                                    <input
                                        type="time"
                                        value={formData.end_time}
                                        onChange={(e) => handleChange('end_time', e.target.value)}
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
                            Generating Assessment...
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