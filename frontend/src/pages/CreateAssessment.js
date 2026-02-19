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
        difficulty: 'Medium'
    });
    const [isGenerating, setIsGenerating] = useState(false);

    const handleChange = (e) => {
        const { id, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [id === 'jobDescription' ? 'job_description' :
                id === 'requiredSkills' ? 'required_skills' :
                    id === 'mcqCount' ? 'mcq_count' :
                        id === 'codingCount' ? 'coding_count' :
                            id === 'duration' ? 'duration' : 'difficulty']: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsGenerating(true);

        try {
            // Using localhost:8001 as per original html
            const response = await axios.post('http://localhost:8001/api/ai/generate/', formData, {
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

    return (
        <div className="dashboard-container" style={{ paddingTop: '2rem', display: 'flex', justifyContent: 'center' }}>
            <div className="card" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                backdropFilter: 'blur(10px)',
                borderRadius: '30px',
                padding: '3.5rem',
                boxShadow: '0 20px 50px rgba(0, 0, 0, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                width: '100%',
                maxWidth: '700px'
            }}>
                <div className="header" style={{ marginBottom: '3rem' }}>
                    <h1 style={{ fontFamily: "'Poppins', sans-serif", fontSize: '2.2rem', fontWeight: '700', margin: '0 0 0.5rem', color: '#1B254B' }}>Create Smart Assessment</h1>
                    <p style={{ color: '#A3AED0', fontSize: '1.1rem', margin: '0' }}>Define the role and let AI craft the perfect test.</p>
                </div>

                <form onSubmit={handleSubmit}>
                    {/* Job Description */}
                    <div className="form-group" style={{ position: 'relative', marginBottom: '2rem' }}>
                        <textarea
                            id="jobDescription"
                            className="form-control"
                            required
                            placeholder=" "
                            value={formData.job_description}
                            onChange={handleChange}
                            style={{
                                width: '100%', padding: '1.1rem 1rem 1.1rem 3.5rem', border: '2px solid #E0E5F2',
                                borderRadius: '18px', fontSize: '1rem', fontWeight: '500', background: '#F4F7FE',
                                color: '#1B254B', transition: 'all 0.3s', fontFamily: 'inherit', minHeight: '120px', resize: 'vertical'
                            }}
                        ></textarea>
                        <i className="fa-solid fa-file-lines" style={{
                            position: 'absolute', left: '1.2rem', top: '1.4rem', color: '#A3AED0', fontSize: '1.1rem', pointerEvents: 'none'
                        }}></i>
                        <label htmlFor="jobDescription" className="form-label" style={{
                            position: 'absolute', left: formData.job_description ? '1.2rem' : '3.5rem',
                            top: formData.job_description ? '-0.8rem' : '1.1rem',
                            color: formData.job_description ? '#4318FF' : '#A3AED0',
                            fontSize: formData.job_description ? '0.85rem' : '1rem',
                            fontWeight: formData.job_description ? '700' : 'normal',
                            background: formData.job_description ? 'white' : 'transparent',
                            padding: formData.job_description ? '0 0.5rem' : '0',
                            borderRadius: '4px', pointerEvents: 'none', transition: 'all 0.3s'
                        }}>Job Description / Role Requirements</label>
                    </div>

                    {/* Skills */}
                    <div className="form-group" style={{ position: 'relative', marginBottom: '2rem' }}>
                        <input
                            type="text"
                            id="requiredSkills"
                            className="form-control"
                            required
                            placeholder=" "
                            value={formData.required_skills}
                            onChange={handleChange}
                            style={{
                                width: '100%', padding: '1.1rem 1rem 1.1rem 3.5rem', border: '2px solid #E0E5F2',
                                borderRadius: '18px', fontSize: '1rem', fontWeight: '500', background: '#F4F7FE',
                                color: '#1B254B', transition: 'all 0.3s', fontFamily: 'inherit'
                            }}
                        />
                        <i className="fa-solid fa-tags" style={{
                            position: 'absolute', left: '1.2rem', top: '1.1rem', color: '#A3AED0', fontSize: '1.1rem', pointerEvents: 'none'
                        }}></i>
                        <label htmlFor="requiredSkills" className="form-label" style={{
                            position: 'absolute', left: formData.required_skills ? '1.2rem' : '3.5rem',
                            top: formData.required_skills ? '-0.8rem' : '1.1rem',
                            color: formData.required_skills ? '#4318FF' : '#A3AED0',
                            fontSize: formData.required_skills ? '0.85rem' : '1rem',
                            fontWeight: formData.required_skills ? '700' : 'normal',
                            background: formData.required_skills ? 'white' : 'transparent',
                            padding: formData.required_skills ? '0 0.5rem' : '0',
                            borderRadius: '4px', pointerEvents: 'none', transition: 'all 0.3s'
                        }}>Required Skills (e.g., Python, React, AWS)</label>
                    </div>

                    {/* Configuration Grid */}
                    <div className="config-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                        {/* MCQ Count */}
                        <div className="form-group" style={{ position: 'relative' }}>
                            <input
                                type="number" id="mcqCount" className="form-control" min="1" max="20" required placeholder=" "
                                value={formData.mcq_count} onChange={handleChange}
                                style={{
                                    width: '100%', padding: '1.1rem 1rem 1.1rem 3.5rem', border: '2px solid #E0E5F2',
                                    borderRadius: '18px', fontSize: '1rem', fontWeight: '500', background: '#F4F7FE',
                                    color: '#1B254B', transition: 'all 0.3s', fontFamily: 'inherit'
                                }}
                            />
                            <i className="fa-solid fa-list-check" style={{ position: 'absolute', left: '1.2rem', top: '1.1rem', color: '#A3AED0', fontSize: '1.1rem', pointerEvents: 'none' }}></i>
                            <label htmlFor="mcqCount" className="form-label" style={{
                                position: 'absolute', left: '1.2rem', top: '-0.8rem', color: '#4318FF', fontSize: '0.85rem', fontWeight: '700', background: 'white', padding: '0 0.5rem', borderRadius: '4px'
                            }}>MCQs</label>
                        </div>

                        {/* Coding Count */}
                        <div className="form-group" style={{ position: 'relative' }}>
                            <input
                                type="number" id="codingCount" className="form-control" min="0" max="5" required placeholder=" "
                                value={formData.coding_count} onChange={handleChange}
                                style={{
                                    width: '100%', padding: '1.1rem 1rem 1.1rem 3.5rem', border: '2px solid #E0E5F2',
                                    borderRadius: '18px', fontSize: '1rem', fontWeight: '500', background: '#F4F7FE',
                                    color: '#1B254B', transition: 'all 0.3s', fontFamily: 'inherit'
                                }}
                            />
                            <i className="fa-solid fa-code" style={{ position: 'absolute', left: '1.2rem', top: '1.1rem', color: '#A3AED0', fontSize: '1.1rem', pointerEvents: 'none' }}></i>
                            <label htmlFor="codingCount" className="form-label" style={{
                                position: 'absolute', left: '1.2rem', top: '-0.8rem', color: '#4318FF', fontSize: '0.85rem', fontWeight: '700', background: 'white', padding: '0 0.5rem', borderRadius: '4px'
                            }}>Coding</label>
                        </div>

                        {/* Duration */}
                        <div className="form-group" style={{ position: 'relative' }}>
                            <input
                                type="number" id="duration" className="form-control" min="15" max="180" required placeholder=" "
                                value={formData.duration} onChange={handleChange}
                                style={{
                                    width: '100%', padding: '1.1rem 1rem 1.1rem 3.5rem', border: '2px solid #E0E5F2',
                                    borderRadius: '18px', fontSize: '1rem', fontWeight: '500', background: '#F4F7FE',
                                    color: '#1B254B', transition: 'all 0.3s', fontFamily: 'inherit'
                                }}
                            />
                            <i className="fa-regular fa-clock" style={{ position: 'absolute', left: '1.2rem', top: '1.1rem', color: '#A3AED0', fontSize: '1.1rem', pointerEvents: 'none' }}></i>
                            <label htmlFor="duration" className="form-label" style={{
                                position: 'absolute', left: '1.2rem', top: '-0.8rem', color: '#4318FF', fontSize: '0.85rem', fontWeight: '700', background: 'white', padding: '0 0.5rem', borderRadius: '4px'
                            }}>Duration</label>
                        </div>

                        {/* Difficulty Level */}
                        <div className="form-group" style={{ position: 'relative' }}>
                            <select
                                id="difficulty" className="form-control" required
                                value={formData.difficulty} onChange={handleChange}
                                style={{
                                    width: '100%', padding: '1.1rem 1rem 1.1rem 3.5rem', border: '2px solid #E0E5F2',
                                    borderRadius: '18px', fontSize: '1rem', fontWeight: '500', background: '#F4F7FE',
                                    color: '#1B254B', transition: 'all 0.3s', fontFamily: 'inherit', appearance: 'none'
                                }}
                            >
                                <option value="Easy">Easy</option>
                                <option value="Medium">Medium</option>
                                <option value="Hard">Hard</option>
                            </select>
                            <i className="fa-solid fa-gauge-high" style={{ position: 'absolute', left: '1.2rem', top: '1.1rem', color: '#A3AED0', fontSize: '1.1rem', pointerEvents: 'none' }}></i>
                            <label htmlFor="difficulty" className="form-label" style={{
                                position: 'absolute', left: '1.2rem', top: '-0.8rem', color: '#4318FF', fontSize: '0.85rem', fontWeight: '700', background: 'white', padding: '0 0.5rem', borderRadius: '4px'
                            }}>Difficulty</label>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button type="submit" className="btn-generate" disabled={isGenerating} style={{
                        width: '100%', background: 'linear-gradient(135deg, #4318FF 0%, #7551FF 100%)', color: 'white',
                        border: 'none', padding: '1.2rem', borderRadius: '18px', fontSize: '1.1rem', fontWeight: '700',
                        cursor: isGenerating ? 'not-allowed' : 'pointer', boxShadow: '0 15px 30px rgba(67, 24, 255, 0.2)',
                        transition: 'all 0.3s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.8rem',
                        opacity: isGenerating ? 0.7 : 1
                    }}>
                        {isGenerating ? (
                            <>
                                <i className="fa-solid fa-circle-notch fa-spin"></i>
                                <span>Generating...</span>
                            </>
                        ) : (
                            <>
                                <i className="fa-solid fa-wand-magic-sparkles"></i>
                                <span>Generate Assessment</span>
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default CreateAssessment;
