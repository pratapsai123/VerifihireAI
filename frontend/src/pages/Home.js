import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import DetectionDemo from '../components/DetectionDemo';
import '../styles/Home.css';
import { ShieldCheck, Activity, Users, MousePointer2 } from 'lucide-react';

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


      </main>
      <Footer />
    </>
  );
}

export default Home;
