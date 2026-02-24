import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/CreateAssessment.css';

const CreateAssessment = () => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({
        job_description: '',
        required_skills: '',
        mcq_count: 10,
        coding_count: 2,
        duration: 60,
        difficulty: 'Medium',
        from_date: '',
        from_time: '',
        until_date: '',
        until_time: '',
        pass_threshold: 60
    });
    const [isGenerating, setIsGenerating] = useState(false);

    const handleChange = (e) => {
        const { id, value } = e.target;
        const fieldMapping = {
            jobDescription: 'job_description',
            requiredSkills: 'required_skills',
            mcqCount: 'mcq_count',
            codingCount: 'coding_count',
            duration: 'duration',
            difficulty: 'difficulty',
            fromDate: 'from_date',
            fromTime: 'from_time',
            untilDate: 'until_date',
            untilTime: 'until_time',
            passThreshold: 'pass_threshold'
        };
        setFormData(prev => ({
            ...prev,
            [fieldMapping[id] || id]: value
        }));
    };

    const nextStep = (e) => {
        if (e) e.preventDefault();
        setCurrentStep(prev => Math.min(prev + 1, 3));
    };

    const prevStep = (e) => {
        if (e) e.preventDefault();
        setCurrentStep(prev => Math.max(prev - 1, 1));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsGenerating(true);

        const combinedData = {
            ...formData,
            available_from: (formData.from_date && formData.from_time) ? new Date(`${formData.from_date}T${formData.from_time}`).toISOString() : '',
            available_until: (formData.until_date && formData.until_time) ? new Date(`${formData.until_date}T${formData.until_time}`).toISOString() : ''
        };

        try {
            const response = await axios.post('http://localhost:8001/api/ai/generate/', combinedData, {
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.status === 200 || response.status === 201) {
                alert('Assessment Generated Successfully!');
                navigate('/ai-assessments');
            } else {
                alert('Failed to generate assessment.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Check if the backend is running.');
        } finally {
            setIsGenerating(false);
        }
    };

    const renderStepIndicators = () => (
        <div className="stepper-ui">
            <div className={`step-item ${currentStep === 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
                <div className="step-circle">{currentStep > 1 ? <i className="fa-solid fa-check"></i> : '1'}</div>
                <div className="step-label">Role</div>
            </div>
            <div className="step-line"></div>
            <div className={`step-item ${currentStep === 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
                <div className="step-circle">{currentStep > 2 ? <i className="fa-solid fa-check"></i> : '2'}</div>
                <div className="step-label">Config</div>
            </div>
            <div className="step-line"></div>
            <div className={`step-item ${currentStep === 3 ? 'active' : ''}`}>
                <div className="step-circle">3</div>
                <div className="step-label">Finalize</div>
            </div>
        </div>
    );

    return (
        <div className="assessment-page">
            <div className="assessment-container">
                <header className="assessment-header">
                    <div className="header-title-group">
                        <div className="ai-badge">
                            <i className="fa-solid fa-wand-magic-sparkles"></i>
                            Powered by NeuralAI
                        </div>
                        <h1>Create <span>Smart</span> Assessment</h1>
                    </div>
                </header>

                {renderStepIndicators()}

                <form onSubmit={handleSubmit} className="step-form">
                    {currentStep === 1 && (
                        <div className="glass-panel">
                            <div className="section-title-group">
                                <div className="icon-box"><i className="fa-solid fa-briefcase"></i></div>
                                <h2>Professional Context</h2>
                            </div>
                            <div className="form-group">
                                <label>Job Description</label>
                                <textarea
                                    id="jobDescription"
                                    value={formData.job_description}
                                    onChange={handleChange}
                                    placeholder="Paste technical requirements here..."
                                    className="glass-textarea"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Core Skills</label>
                                <input
                                    type="text"
                                    id="requiredSkills"
                                    value={formData.required_skills}
                                    onChange={handleChange}
                                    placeholder="React, Node.js, AWS..."
                                    className="glass-input"
                                    required
                                />
                            </div>
                            <div className="step-actions">
                                <div style={{ flex: 1 }}></div>
                                <button className="btn-primary" onClick={nextStep}>
                                    Next Configuration <i className="fa-solid fa-arrow-right"></i>
                                </button>
                            </div>
                        </div>
                    )}

                    {currentStep === 2 && (
                        <div className="glass-panel">
                            <div className="section-title-group">
                                <div className="icon-box" style={{ background: 'linear-gradient(135deg, #3b82f6, #2dd4bf)' }}>
                                    <i className="fa-solid fa-sliders"></i>
                                </div>
                                <h2>Assessment Config</h2>
                            </div>
                            <div className="param-grid">
                                <div className="form-group">
                                    <label>MCQ Count</label>
                                    <input type="number" id="mcqCount" value={formData.mcq_count} onChange={handleChange} className="glass-input" min="1" />
                                </div>
                                <div className="form-group">
                                    <label>Coding tasks</label>
                                    <input type="number" id="codingCount" value={formData.coding_count} onChange={handleChange} className="glass-input" min="0" />
                                </div>
                            </div>
                            <div className="form-group">
                                <label>Duration (Minutes)</label>
                                <input type="number" id="duration" value={formData.duration} onChange={handleChange} className="glass-input" min="1" />
                            </div>
                            <div className="form-group">
                                <label>Complexity</label>
                                <select id="difficulty" value={formData.difficulty} onChange={handleChange} className="glass-select">
                                    <option value="Easy">Standard</option>
                                    <option value="Medium">Advanced</option>
                                    <option value="Hard">Expert</option>
                                </select>
                            </div>
                            <div className="step-actions">
                                <button className="btn-secondary" onClick={prevStep}>Back</button>
                                <button className="btn-primary" onClick={nextStep}>
                                    Next Schedule <i className="fa-solid fa-arrow-right"></i>
                                </button>
                            </div>
                        </div>
                    )}

                    {currentStep === 3 && (
                        <div className="glass-panel">
                            <div className="section-title-group">
                                <div className="icon-box" style={{ background: 'linear-gradient(135deg, #10b981, #3b82f6)' }}>
                                    <i className="fa-solid fa-calendar-check"></i>
                                </div>
                                <h2>Threshold & Schedule</h2>
                            </div>

                            <div className="threshold-card">
                                <div className="threshold-header">Minimum Pass Threshold (%)</div>
                                <input type="number" id="passThreshold" value={formData.pass_threshold} onChange={handleChange} min="1" max="100" className="glass-input" />
                            </div>

                            <div className="form-group" style={{ marginTop: '1.5rem' }}>
                                <label>Available From</label>
                                <div className="date-time-group">
                                    <input type="date" id="fromDate" value={formData.from_date} onChange={handleChange} className="glass-input" />
                                    <input type="time" id="fromTime" value={formData.from_time} onChange={handleChange} className="glass-input" />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Expiry Date</label>
                                <div className="date-time-group">
                                    <input type="date" id="untilDate" value={formData.until_date} onChange={handleChange} className="glass-input" />
                                    <input type="time" id="untilTime" value={formData.until_time} onChange={handleChange} className="glass-input" />
                                </div>
                            </div>

                            <div className="step-actions">
                                <button className="btn-secondary" onClick={prevStep}>Back</button>
                                <button type="submit" disabled={isGenerating} className="generate-btn">
                                    {isGenerating ? (
                                        <><i className="fa-solid fa-atom fa-spin"></i> Architecting...</>
                                    ) : (
                                        <><i className="fa-solid fa-wand-magic-sparkles"></i> Generate Assessment</>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
};

export default CreateAssessment;
