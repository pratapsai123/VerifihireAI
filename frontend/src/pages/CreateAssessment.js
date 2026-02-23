import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Dashboard.css';

const CreateAssessment = () => {
    const navigate = useNavigate();
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
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 200 || response.status === 201) {
                alert('Assessment Generated Successfully! Redirecting to assessments list...');
                navigate('/ai-assessments');
            } else {
                alert('Failed to generate assessment. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Is the backend running?');
        } finally {
            setIsGenerating(false);
        }
    };

    const SectionHeader = ({ iconClass, title, subtitle, colorClass }) => (
        <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.4rem' }}>
                <div className={`module-icon-wrapper ${colorClass}`} style={{ width: '32px', height: '32px', borderRadius: '8px' }}>
                    <i className={`${iconClass}`} style={{ fontSize: '0.9rem' }}></i>
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: '#111827', margin: 0, letterSpacing: '-0.01em' }}>{title}</h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#6B7280', margin: 0 }}>{subtitle}</p>
        </div>
    );

    return (
        <div className="dashboard-container">
            <div className="dashboard-main" style={{ maxWidth: '850px', paddingTop: '1.5rem' }}>

                {/* Header Section */}
                <header style={{
                    position: 'relative',
                    padding: '2.5rem 2rem',
                    background: 'white',
                    borderRadius: '24px',
                    marginBottom: '2rem',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
                    border: '1px solid #E5E7EB',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        position: 'absolute', top: '-40px', right: '-40px', width: '180px', height: '180px',
                        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)', borderRadius: '50%'
                    }}></div>

                    <div style={{ position: 'relative', zIndex: 1 }}>
                        <div style={{
                            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                            background: '#EEF2FF', color: '#4F46E5',
                            padding: '0.4rem 0.8rem', borderRadius: '10px', fontSize: '0.75rem',
                            fontWeight: '700', marginBottom: '1rem', border: '1px solid rgba(79, 70, 229, 0.1)'
                        }}>
                            <i className="fa-solid fa-wand-magic-sparkles"></i> AI GENERATOR
                        </div>
                        <h1 style={{ fontSize: '2.4rem', fontWeight: '900', color: '#111827', margin: '0 0 0.5rem', letterSpacing: '-0.03em' }}>
                            Create <span style={{ color: '#6366F1' }}>Smart</span> Assessment
                        </h1>
                        <p style={{ color: '#6B7280', fontSize: '1rem', maxWidth: '500px' }}>
                            Define the role and skills. Our AI will craft a comprehensive technical assessment.
                        </p>
                    </div>
                </header>

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    {/* Role & Requirements Card */}
                    <div className="module-card" style={{ padding: '2rem', background: 'white', borderRadius: '24px', border: '1px solid #E5E7EB' }}>
                        <SectionHeader
                            iconClass="fa-solid fa-briefcase"
                            title="Role Context"
                            subtitle="AI will analyze this to determine the appropriate depth of questions."
                            colorClass="indigo-glow"
                        />
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                            <div>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>Job Description</label>
                                <textarea
                                    id="jobDescription"
                                    value={formData.job_description}
                                    onChange={handleChange}
                                    placeholder="Paste the role requirements or mission statement..."
                                    style={{
                                        width: '100%', height: '150px', padding: '1rem', border: '1px solid #E2E8F0',
                                        borderRadius: '14px', resize: 'vertical', fontSize: '0.95rem', lineHeight: '1.6',
                                        color: '#1F2937', background: '#F8FAFC', outline: 'none'
                                    }}
                                    required
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>Core Skills</label>
                                <input
                                    type="text"
                                    id="requiredSkills"
                                    value={formData.required_skills}
                                    onChange={handleChange}
                                    placeholder="e.g. React, Node.js, System Design"
                                    style={{
                                        width: '100%', padding: '0.85rem 1rem', border: '1px solid #E2E8F0',
                                        borderRadius: '14px', fontSize: '0.95rem', color: '#1F2937', background: '#F8FAFC', outline: 'none'
                                    }}
                                    required
                                />
                            </div>
                            <div style={{ padding: '1rem', background: '#F0F9FF', borderRadius: '16px', border: '1px dashed #BAE6FD', marginTop: '1rem' }}>
                                <label style={{ fontSize: '0.82rem', fontWeight: '700', color: '#0369A1', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <i className="fa-solid fa-bullseye" style={{ fontSize: '0.8rem' }}></i> Pass Threshold (%)
                                </label>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <input
                                        type="number"
                                        id="passThreshold"
                                        value={formData.pass_threshold}
                                        onChange={handleChange}
                                        min="1" max="100"
                                        style={{
                                            width: '80px', padding: '0.6rem 0.8rem', border: '1px solid #BAE6FD',
                                            borderRadius: '10px', fontSize: '0.9rem', fontWeight: '700', color: '#0369A1', background: 'white', outline: 'none'
                                        }}
                                    />
                                    <span style={{ fontSize: '0.78rem', color: '#0EA5E9', fontWeight: '500' }}>Minimum percentage required to pass.</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Assessment Parameters Card */}
                    <div className="module-card" style={{ padding: '2rem', background: 'white', borderRadius: '24px', border: '1px solid #E5E7EB' }}>
                        <SectionHeader
                            iconClass="fa-solid fa-sliders"
                            title="Structure & Difficulty"
                            subtitle="Configure the scope and intensity of the generated test."
                            colorClass="blue-glow"
                        />

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1.25rem' }}>
                            <div>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>MCQ Questions</label>
                                <input
                                    type="number" id="mcqCount" min="1" max="50"
                                    value={formData.mcq_count} onChange={handleChange}
                                    style={{ width: '100%', padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC' }}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>Coding Tasks</label>
                                <input
                                    type="number" id="codingCount" min="0" max="10"
                                    value={formData.coding_count} onChange={handleChange}
                                    style={{ width: '100%', padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC' }}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>Duration (mins)</label>
                                <input
                                    type="number" id="duration" min="5" max="300"
                                    value={formData.duration} onChange={handleChange}
                                    style={{ width: '100%', padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC' }}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '0.5rem', display: 'block' }}>Complexity</label>
                                <select
                                    id="difficulty"
                                    value={formData.difficulty} onChange={handleChange}
                                    style={{
                                        width: '100%', padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px',
                                        outline: 'none', background: '#F8FAFC', appearance: 'none', cursor: 'pointer'
                                    }}
                                >
                                    <option value="Easy">Easy</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Hard">Hard</option>
                                </select>
                            </div>
                        </div>

                        <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1.25rem', paddingTop: '1.5rem', borderTop: '1px dashed #E2E8F0' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '-0.5rem', display: 'block' }}>
                                    <i className="fa-regular fa-calendar-check" style={{ marginRight: '0.4rem', color: '#6366F1' }}></i>
                                    Available From
                                </label>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <input
                                        type="date" id="fromDate"
                                        value={formData.from_date} onChange={handleChange}
                                        style={{ flex: 1.5, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                    />
                                    <input
                                        type="time" id="fromTime"
                                        value={formData.from_time} onChange={handleChange}
                                        style={{ flex: 1, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                    />
                                </div>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                                <label style={{ fontSize: '0.85rem', fontWeight: '700', color: '#374151', marginBottom: '-0.5rem', display: 'block' }}>
                                    <i className="fa-regular fa-calendar-xmark" style={{ marginRight: '0.4rem', color: '#EF4444' }}></i>
                                    Available Until
                                </label>
                                <div style={{ display: 'flex', gap: '0.5rem' }}>
                                    <input
                                        type="date" id="untilDate"
                                        value={formData.until_date} onChange={handleChange}
                                        style={{ flex: 1.5, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                    />
                                    <input
                                        type="time" id="untilTime"
                                        value={formData.until_time} onChange={handleChange}
                                        style={{ flex: 1, padding: '0.85rem', border: '1px solid #E2E8F0', borderRadius: '12px', outline: 'none', background: '#F8FAFC', fontSize: '0.9rem' }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Final Action Section */}
                    <div style={{ marginTop: '0.5rem', textAlign: 'center' }}>
                        <button
                            type="submit"
                            disabled={isGenerating}
                            style={{
                                width: '100%',
                                background: 'linear-gradient(135deg, #4F46E5 0%, #6366F1 100%)',
                                color: 'white',
                                border: 'none',
                                padding: '1.25rem',
                                borderRadius: '20px',
                                fontSize: '1.1rem',
                                fontWeight: '700',
                                cursor: isGenerating ? 'not-allowed' : 'pointer',
                                boxShadow: '0 10px 20px -5px rgba(79, 70, 229, 0.4)',
                                transition: 'all 0.2s',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '0.75rem'
                            }}
                        >
                            {isGenerating ? (
                                <>
                                    <i className="fa-solid fa-spinner fa-spin"></i>
                                    <span>AI Architecture in Progress...</span>
                                </>
                            ) : (
                                <>
                                    <i className="fa-solid fa-wand-sparkles"></i>
                                    <span>Generate Technical Assessment</span>
                                </>
                            )}
                        </button>

                        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'center', gap: '3rem' }}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ color: '#6366F1', fontSize: '1.2rem', marginBottom: '0.4rem' }}>
                                    <i className="fa-solid fa-microchip"></i>
                                </div>
                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#1E293B', textTransform: 'uppercase' }}>Gemini Pro</div>
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ color: '#6366F1', fontSize: '1.2rem', marginBottom: '0.4rem' }}>
                                    <i className="fa-solid fa-shield-halved"></i>
                                </div>
                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#1E293B', textTransform: 'uppercase' }}>Anti-Cheat</div>
                            </div>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ color: '#6366F1', fontSize: '1.2rem', marginBottom: '0.4rem' }}>
                                    <i className="fa-solid fa-code-merge"></i>
                                </div>
                                <div style={{ fontSize: '0.75rem', fontWeight: '800', color: '#1E293B', textTransform: 'uppercase' }}>Auto-Grade</div>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateAssessment;
