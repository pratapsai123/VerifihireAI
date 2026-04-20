import React, { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import '../styles/Contact.css';

const Contact = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    company: '',
    subject: '',
    message: ''
  });

  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setStatus({ type: '', message: '' });

    try {
      const response = await axios.post(`${API_BASE_URL}/contact/`, formData);
      if (response.data.success) {
        setStatus({
          type: 'success',
          message: 'Your message has been sent successfully! We will get back to you soon.'
        });
        setFormData({ full_name: '', email: '', company: '', subject: '', message: '' });
      } else {
        setStatus({
          type: 'error',
          message: response.data.error || 'Failed to send message. Please try again.'
        });
      }
    } catch (error) {
      console.error("Error sending contact message:", error);
      setStatus({
        type: 'error',
        message: error.response?.data?.error || 'An unexpected error occurred. Please try again later.'
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <MainHeader />
      <div className="contact-page-container">
        <div className="contact-card">
          <h1 className="contact-form-title">Details</h1>

          <form className="contact-form" onSubmit={handleSubmit}>
            {/* Row 1 */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="full_name">Full Name</label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  placeholder="john@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Row 2 */}
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="company">Company</label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  placeholder="Your Company"
                  value={formData.company}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="subject">Subject</label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  placeholder="How can we help?"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Row 3 - Message */}
            <div className="form-row">
              <div className="form-group" style={{ width: '100%' }}>
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  name="message"
                  placeholder="Tell us about your project..."
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows={4}
                ></textarea>
              </div>
            </div>

            <button
              type="submit"
              className="contact-submit-btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Sending...' : 'Book a Demo'}
              {!isSubmitting && <span>&rarr;</span>}
            </button>

            {status.message && (
              <div className={`contact-message-feedback ${status.type === 'success' ? 'contact-message-success' : 'contact-message-error'}`}>
                {status.message}
              </div>
            )}
          </form>
        </div>
      </div>
      <Footer />
    </>
  );
};

export default Contact;
