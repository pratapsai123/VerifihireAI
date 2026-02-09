import { useEffect } from 'react';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';

function Home() {
  useEffect(() => {
    // Initialize AOS
    if (window.AOS) { 
      window.AOS.init({
        duration: 800,
        once: true,
        offset: 50,
      });
    }

    // Initialize Particle.js only if hero container exists
    if (window.particlesJS && document.getElementById('particles-js')) {
      window.particlesJS('particles-js', {
        particles: {
          number: { value: 80, density: { enable: true, value_area: 800 } },
          color: { value: '#ffffff' },
          shape: {
            type: 'circle',
            stroke: { width: 0, color: '#000000' },
            polygon: { nb_sides: 5 },
          },
          opacity: {
            value: 0.5,
            random: false,
            anim: { enable: false, speed: 1, opacity_min: 0.1, sync: false },
          },
          size: {
            value: 3,
            random: true,
            anim: {
              enable: false,
              speed: 40,
              size_min: 0.1,
              sync: false,
            },
          },
          line_linked: {
            enable: true,
            distance: 150,
            color: '#ffffff',
            opacity: 0.4,
            width: 1,
          },
          move: {
            enable: true,
            speed: 6,
            direction: 'none',
            random: false,
            straight: false,
            out_mode: 'out',
            bounce: false,
            attract: { enable: false, rotateX: 600, rotateY: 1200 },
          },
        },
        interactivity: {
          detect_on: 'canvas',
          events: {
            onhover: { enable: true, mode: 'repulse' },
            onclick: { enable: true, mode: 'push' },
            resize: true,
          },
          modes: {
            grab: { distance: 400, line_linked: { opacity: 1 } },
            bubble: {
              distance: 400,
              size: 40,
              duration: 2,
              opacity: 8,
              speed: 3,
            },
            repulse: { distance: 200, duration: 0.4 },
            push: { particles_nb: 4 },
            remove: { particles_nb: 2 },
          },
        },
        retina_detect: true,
      });
    }
  }, []);

  const scrollToSection = (e, sectionId) => {
    e.preventDefault();
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <>
      <MainHeader />
      <main>
        {/* Hero Section */}
        <section className="hero-section hero-gradient">
          <div id="particles-js"></div>
          <div className="container hero-container hero-content">
            <h1 className="hero-title" data-aos="fade-down">
              Authentic Talent, Verified.
            </h1>
            <p
              className="hero-subtitle"
              data-aos="fade-up"
              data-aos-delay="200"
            >
              Our platform ensures integrity in online assessments, helping
              you recruit genuine talent with confidence by eliminating
              proxy interviews and monitoring candidate activity.
            </p>
            <button
              type="button"
              className="hero-cta"
              data-aos="zoom-in"
              data-aos-delay="400"
              onClick={(e) => scrollToSection(e, 'features')}
            >
              Explore Platform
            </button>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="section">
          <div className="container">
            <div className="section-header" data-aos="fade-up">
              <h2 className="section-title">The Ultimate Recruitment Shield</h2>
              <p className="section-subtitle">
                Everything you need to conduct secure, fair, and insightful
                online examinations.
              </p>
            </div>
            <div className="features-grid">
              {/* Feature 1 */}
              <div
                className="feature-card"
                data-aos="fade-up"
                data-aos-delay="100"
              >
                <div className="feature-icon-wrapper">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="feature-icon"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <h3 className="feature-title">Anti-Proxy Proctoring</h3>
                <p className="feature-description">
                  Our core mission. We leverage advanced monitoring to detect
                  and prevent fraudulent activities, ensuring the candidate
                  taking the test is the one you invited.
                </p>
              </div>

              {/* Feature 2 */}
              <div
                className="feature-card"
                data-aos="fade-up"
                data-aos-delay="200"
              >
                <div className="feature-icon-wrapper">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="feature-icon"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                    />
                  </svg>
                </div>
                <h3 className="feature-title">Custom Exam Builder</h3>
                <p className="feature-description">
                  Organizations have full control to create tailored
                  assessments. Build your own question banks to evaluate the
                  specific skills you need for fast growth.
                </p>
              </div>

              {/* Feature 3 */}
              <div
                className="feature-card"
                data-aos="fade-up"
                data-aos-delay="300"
              >
                <div className="feature-icon-wrapper">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="feature-icon"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <h3 className="feature-title">End-to-End Session Records</h3>
                <p className="feature-description">
                  Gain unparalleled insight. Our portal securely stores a
                  complete record of the candidate&apos;s activity during the
                  exam, from first click to final submission.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="section how-it-works-section">
          <div className="container">
            <div className="section-header" data-aos="fade-up">
              <h2 className="section-title">A Simple Path to Quality Hires</h2>
              <p className="section-subtitle">
                Recruit talent in four easy steps.
              </p>
            </div>
            <div className="steps-container">
              <div className="steps-grid">
                <div
                  className="step"
                  data-aos="fade-right"
                  data-aos-delay="100"
                >
                  <div className="step-number">1</div>
                  <h3 className="step-title">Create Exam</h3>
                  <p className="step-description">
                    Use our intuitive builder to design your assessment and
                    add questions.
                  </p>
                </div>
                <div
                  className="step"
                  data-aos="fade-right"
                  data-aos-delay="200"
                >
                  <div className="step-number">2</div>
                  <h3 className="step-title">Invite Candidates</h3>
                  <p className="step-description">
                    Send secure, unique invitations to your list of potential
                    hires.
                  </p>
                </div>
                <div
                  className="step"
                  data-aos="fade-left"
                  data-aos-delay="300"
                >
                  <div className="step-number">3</div>
                  <h3 className="step-title">Monitor &amp; Record</h3>
                  <p className="step-description">
                    Let our system monitor the session while you focus on
                    other tasks.
                  </p>
                </div>
                <div
                  className="step"
                  data-aos="fade-left"
                  data-aos-delay="400"
                >
                  <div className="step-number">4</div>
                  <h3 className="step-title">Review &amp; Recruit</h3>
                  <p className="step-description">
                    Analyze the activity reports and hire the most talented
                    candidates with confidence.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section id="about" className="section">
          <div className="container about-container" data-aos="fade-up">
            <h2 className="section-title">Our Mission</h2>
            <p className="about-description">
              At VerifiHireAI, we believe true talent deserves a fair
              chance. In a world of remote work, ensuring candidate
              authenticity is the biggest challenge for growing organizations.
              Our mission is to bridge this gap, providing a secure, reliable
              platform that empowers companies to identify and recruit the
              best minds, fostering growth and innovation built on a
              foundation of trust.
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

export default Home;

