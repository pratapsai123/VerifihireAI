import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CreateAssessment.css';

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
        pass_threshold: 60
    });

    const handleChange = (id, value) => {
        if (id === 'num_coding') {
            const count = parseInt(value) || 0;
            const limitedCount = Math.min(Math.max(count, 0), 5); // Limit to 5 tasks

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
        const { easy, medium, hard } = calculateMcqMix(formData.num_mcqs);
        const mcqPoints = (easy * 100) + (medium * 200) + (hard * 300);
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

        setLoading(true);

        const { easy, medium, hard } = calculateMcqMix(formData.num_mcqs);

        const combinedData = {
            job_description: formData.job_description,
            required_skills: formData.skills,
            mcq_easy: easy,
            mcq_medium: medium,
            mcq_hard: hard,
            coding_tasks: formData.coding_challenges.map(c => c.difficulty),
            duration: formData.coding_time,
            pass_threshold: formData.pass_threshold,
            total_possible_points: calculateTotalPoints(),
            available_from: (formData.start_date && formData.start_time) ? new Date(`${formData.start_date}T${formData.start_time}`).toISOString() : null,
            available_until: (formData.end_date && formData.end_time) ? new Date(`${formData.end_date}T${formData.end_time}`).toISOString() : null
        };

        try {
            const response = await axios.post(`${API_BASE_URL}/ai/generate/`, combinedData, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.status === 200 || response.status === 201) {
                alert('Assessment Generated Successfully!');
                navigate('/ai-assessments');
            }
        } catch (error) {
            console.error('Error:', error);
            const errMsg = error?.response?.data?.error || error?.response?.data?.message || error?.message || 'Generation failed. Please try again.';
            alert(`Generation failed: ${errMsg}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-assessment-page">
            <div className="bg-shape shape-1"></div>
            <div className="bg-shape shape-2"></div>
            <div className="bg-shape shape-3"></div>

            <div className="assessment-container">
                <header className="assessment-header">
                    <h1>Create <span>Smart</span> Assessment</h1>
                    <p>Our intelligent AI transforms your requirements into a precision-engineered technical evaluation.</p>
                </header>

                <div className="glass-card">
                    <SectionHeader icon="📝" title="Role Context" />
                    <div className="form-group">
                        <label>Job Requirements</label>
                        <textarea
                            placeholder="Describe the role, key responsibilities, and ideal candidate profile..."
                            value={formData.job_description}
                            onChange={(e) => handleChange('job_description', e.target.value)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Target Skills</label>
                        <input
                            type="text"
                            placeholder="e.g. React, Node.js, Python, System Design..."
                            value={formData.skills}
                            onChange={(e) => handleChange('skills', e.target.value)}
                        />
                    </div>
                </div>

                <div className="glass-card">
                    <SectionHeader icon="⚙️" title="Structure & Difficulty" />

                    {/* Reverted Parameter Row (from screenshot) */}
                    <div className="parameters-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '2rem', marginBottom: '2.5rem' }}>
                        <div className="form-group">
                            <label>MCQ Questions</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="0" max="50"
                                    value={formData.num_mcqs}
                                    onChange={(e) => handleChange('num_mcqs', parseInt(e.target.value) || 0)}
                                />
                                <span className="marker">{formData.num_mcqs}</span>
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Coding Tasks</label>
                            <div className="input-with-marker">
                                <input
                                    type="number" min="0" max="5"
                                    value={formData.num_coding}
                                    onChange={(e) => handleChange('num_coding', e.target.value)}
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
                                <label><span>📅</span> Available From</label>
                                <div className="datetime-row">
                                    <input
                                        type="date"
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
                                <label><span>⌛</span> Available Until</label>
                                <div className="datetime-row">
                                    <input
                                        type="date"
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

const SectionHeader = ({ icon, title }) => (
    <div className="section-header">
        <span className="icon-box">{icon}</span>
        <h2>{title}</h2>
    </div>
);

export default CreateAssessment;