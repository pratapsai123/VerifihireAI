import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/CreateAssessment.css';

const CreateAssessment = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        job_description: '',
        skills: '',
        num_mcqs: 10,
        num_coding: 2,
        difficulty: 'Medium',
        start_date: '',
        start_time: '',
        end_date: '',
        end_time: '',
        pass_threshold: 60
    });

    const handleChange = (id, value) => {
        setFormData(prev => ({
            ...prev,
            [id]: value
        }));
    };

    const handleSubmit = async (e) => {
        if (e) e.preventDefault();
        setLoading(true);

        const combinedData = {
            job_description: formData.job_description,
            required_skills: formData.skills,
            mcq_count: formData.num_mcqs,
            coding_count: formData.num_coding,
            difficulty: formData.difficulty,
            pass_threshold: formData.pass_threshold,
            available_from: (formData.start_date && formData.start_time) ? new Date(`${formData.start_date}T${formData.start_time}`).toISOString() : null,
            available_until: (formData.end_date && formData.end_time) ? new Date(`${formData.end_date}T${formData.end_time}`).toISOString() : null
        };

        try {
            const response = await axios.post('http://localhost:8001/api/ai/generate/', combinedData, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.status === 200 || response.status === 201) {
                alert('Assessment Generated Successfully!');
                navigate('/ai-assessments');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Generation failed. Ensure the backend is running at port 8001.');
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
                    <div className="parameters-grid">
                        <div className="form-group">
                            <label>MCQ Questions</label>
                            <div className="input-with-marker">
                                <input
                                    type="number"
                                    min="1"
                                    max="50"
                                    value={formData.num_mcqs}
                                    onChange={(e) => handleChange('num_mcqs', e.target.value === '' ? '' : parseInt(e.target.value))}
                                />
                                <span className="marker">{formData.num_mcqs}</span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Coding Tasks</label>
                            <div className="input-with-marker">
                                <input
                                    type="number"
                                    min="0"
                                    max="5"
                                    value={formData.num_coding}
                                    onChange={(e) => handleChange('num_coding', e.target.value === '' ? '' : parseInt(e.target.value))}
                                />
                                <span className="marker">{formData.num_coding}</span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Complexity</label>
                            <select
                                value={formData.difficulty}
                                onChange={(e) => handleChange('difficulty', e.target.value)}
                            >
                                <option value="Easy">Easy</option>
                                <option value="Medium">Medium</option>
                                <option value="Hard">Hard</option>
                            </select>
                        </div>
                    </div>

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
