import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import DetectionDemo from '../components/DetectionDemo';
import '../styles/Home.css';
import featuresBg from '../assets/features-neural-bg.png';
import { ShieldCheck, Activity, Users, MousePointer2, Zap, Cpu, BarChart3, ChevronRight } from 'lucide-react';

function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <MainHeader />
      <main className="classic-home">
        {/* --- Hero Section --- */}
        <section className={`hero-classic-section ${mounted ? 'fade-in' : ''}`}>
          <div className="hero-classic-content">
            <div className="hero-classic-text">
              <h1 className="hero-classic-title">
                AI Intelligence That <br />
                <span className="accent-blue">Transforms Hiring</span>
              </h1>
              <p className="hero-classic-subtitle">
                VerifiHireAI leverages advanced artificial intelligence to conduct structured, unbiased interviews while ensuring real-time fraud detection and candidate authenticity. Our platform enables organizations to make faster, data-driven hiring decisions with confidence, integrity, and precision.
              </p>
              <div className="hero-classic-buttons">
                <Link to="/signup" className="btn-primary-premium">
                  Get Started →
                </Link>
                <Link to="/contact" className="btn-secondary-premium">
                  Book a Demo
                </Link>
              </div>

            </div>
            <div className="hero-classic-visual">
              <DetectionDemo />
            </div>
          </div>
        </section>

        <hr className="section-divider" />

        {/* --- Key Features Section --- */}
        <section 
          className="features-classic" 
          style={{ 
            backgroundImage: `linear-gradient(rgba(11, 31, 58, 0.82), rgba(11, 31, 58, 0.94)), url(${featuresBg})` 
          }}
        >
          <div className="features-header">
            <h2>Enterprise-Grade AI Interviewing</h2>
            <p>Why VerifiHireAI</p>
          </div>
          <div className="features-grid-classic">
            <div className="feature-card-classic card-blue">
              <div className="feature-card-header">
                <div className="feature-icon-classic b-blue">
                  <ShieldCheck className="feature-icon" color="#2563EB" size={20} />
                </div>
                <h3 className="feature-card-title">Real-Time Fraud Detection</h3>
              </div>
              <p className="feature-card-text">
                Continuous identity verification, multi-face detection, and browser lockdown ensure complete integrity throughout the assessment.
              </p>
            </div>
            
            <div className="feature-card-classic card-green">
              <div className="feature-card-header">
                <div className="feature-icon-classic b-green">
                  <Activity className="feature-icon" color="#10B981" size={20} />
                </div>
                <h3 className="feature-card-title">Behavioral Analysis</h3>
              </div>
              <p className="feature-card-text">
                Advanced sentiment tracking and confidence analysis over the course of the candidate's interview responses.
              </p>
            </div>

            <div className="feature-card-classic card-purple">
              <div className="feature-card-header">
                <div className="feature-icon-classic b-purple">
                  <Users className="feature-icon" color="#8B5CF6" size={20} />
                </div>
                <h3 className="feature-card-title">Unbiased Scoring & Grading</h3>
              </div>
              <p className="feature-card-text">
                Standardized rubrics and completely objective AI evaluation eliminates human bias from preliminary screening rounds.
              </p>
            </div>

            <div className="feature-card-classic card-orange">
              <div className="feature-card-header">
                <div className="feature-icon-classic b-orange">
                  <MousePointer2 className="feature-icon" color="#F59E0B" size={20} />
                </div>
                <h3 className="feature-card-title">Seamless Dashboard Experience</h3>
              </div>
              <p className="feature-card-text">
                View detailed analytics, session integrity reports, and candidate progression in a premium, highly actionable unified dashboard.
              </p>
            </div>
          </div>
        </section>

      </main>
      <Footer />
    </>
  );
}

export default Home;
