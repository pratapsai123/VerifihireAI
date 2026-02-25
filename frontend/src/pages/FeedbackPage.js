import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import './FeedbackPage.css';

const FeedbackPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const candidateName = searchParams.get('candidate') || 'Candidate';
    const token = searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId');

    const [techRating, setTechRating] = useState(0);
    const [commRating, setCommRating] = useState(0);
    const [fitRating, setFitRating] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const calculateAverage = () => {
        const ratings = [techRating, commRating, fitRating].filter(r => r > 0);
        if (ratings.length === 0) return 0;
        const sum = ratings.reduce((acc, curr) => acc + curr, 0);
        return (sum / ratings.length).toFixed(1);
    };

    const averageRating = calculateAverage();

    const handleSubmit = async () => {
        if (!token) {
            alert('Missing interview token.');
            return;
        }
        if (techRating === 0 || commRating === 0 || fitRating === 0) {
            alert('Please provide ratings for all categories.');
            return;
        }

        setIsSubmitting(true);

        try {
            const response = await fetch(`${API_BASE_URL}/submit-interview-feedback/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    token: token,
                    technical_rating: techRating,
                    communication_rating: commRating,
                    team_fit_rating: fitRating,
                    rating: Math.round(averageRating), // Map to legacy field as fallback
                    feedback: feedback,
                    role: 'interviewer'
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                alert('Feedback submitted successfully!');
                navigate('/dashboard');
            } else {
                console.error('Submission failed:', data);
                alert(data.error || 'Failed to submit feedback. Please try again.');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
            alert('An error occurred. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    const renderStars = (currentRating, setter, label) => (
        <div className="rating-category">
            <label className="category-label">{label}</label>
            <div className="stars-wrapper">
                {[1, 2, 3, 4, 5].map((star) => (
                    <i
                        key={star}
                        className={`fas fa-star star-item ${star <= currentRating ? 'active' : ''}`}
                        onClick={() => setter(star)}
                    ></i>
                ))}
            </div>
        </div>
    );

    return (
        <div className="feedback-page">
            <div className="feedback-container">
                <div className="feedback-header">
                    <h1 className="feedback-title">Interview Feedback</h1>
                    <p className="feedback-subtitle">Candidate: <span className="highlight">{candidateName}</span></p>
                </div>

                <div className="multi-rating-section">
                    {renderStars(techRating, setTechRating, 'Technical Performance')}
                    {renderStars(commRating, setCommRating, 'Communication Skills')}
                    {renderStars(fitRating, setFitRating, 'Team Fit & Cultural Match')}

                    <div className="average-rating-display">
                        <span className="avg-label">Average Rating:</span>
                        <span className="avg-value">{averageRating} / 5.0</span>
                    </div>
                </div>

                <div className="feedback-input-section">
                    <label className="textarea-label">Detailed Notes</label>
                    <textarea
                        className="feedback-textarea"
                        placeholder="Provide specific feedback about the candidate..."
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        rows="4"
                    />
                </div>

                <button
                    className="btn-submit"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                >
                    {isSubmitting ? 'Submitting...' : 'Complete Interview Feedback'}
                </button>
            </div>
        </div>
    );
};

export default FeedbackPage;
