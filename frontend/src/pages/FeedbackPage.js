import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import './FeedbackPage.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

const FeedbackPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const candidateName = searchParams.get('candidate') || 'Candidate';
    const token = searchParams.get('token') || searchParams.get('session') || searchParams.get('sessionId');

    const [rating, setRating] = useState(0);
    const [feedback, setFeedback] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async () => {
        if (!token) {
            alert('Missing interview token.');
            return;
        }
        if (rating === 0) {
            alert('Please select a rating.');
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
                    rating: rating,
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

    return (
        <div className="feedback-page">
            <div className="feedback-container">
                <div className="feedback-header">
                    <h1 className="feedback-title">Interview Completed</h1>
                    <p className="feedback-subtitle">Please rate {candidateName}'s performance</p>
                </div>

                <div className="rating-section-simple">
                    <div className="stars-large">
                        {[1, 2, 3, 4, 5].map((star) => (
                            <i
                                key={star}
                                className={`fas fa-star star-large ${star <= rating ? 'active' : ''}`}
                                onClick={() => setRating(star)}
                            ></i>
                        ))}
                    </div>
                    <p className="rating-text">
                        {rating === 0 ? 'Select a rating' : `${rating} out of 5 stars`}
                    </p>
                </div>

                <div className="feedback-input-section">
                    <textarea
                        className="feedback-textarea"
                        placeholder="Write your detailed feedback here..."
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        rows="6"
                    />
                </div>

                <button
                    className="btn-submit"
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                >
                    {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
            </div>
        </div>
    );
};

export default FeedbackPage;
