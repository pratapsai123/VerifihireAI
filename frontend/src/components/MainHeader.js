import { Link, useLocation, useNavigate } from 'react-router-dom';

function MainHeader() {
  const location = useLocation();
  const navigate = useNavigate();
  const isHomePage = location.pathname === '/';

  const scrollToSection = (e, sectionId) => {
    e.preventDefault();
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const goHome = () => {
    navigate('/');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header style={{
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(4px)',
      WebkitBackdropFilter: 'blur(4px)',
      boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
      position: 'sticky',
      top: 0,
      zIndex: 40,
      width: '100%'
    }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 2rem',
        width: '100%',
        maxWidth: '100%',
        margin: 0
      }}>
        {/* Left: Logo */}
        <button
          type="button"
          onClick={goHome}
          style={{
            fontSize: '1.875rem',
            fontWeight: 700,
            color: '#4f46e5',
            background: 'none',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            fontFamily: 'inherit'
          }}
        >
          VerifiHireAI
        </button>

        {/* Center: Navigation Links (only on home page) */}
        {isHomePage && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '2rem',
            position: 'absolute',
            left: '50%',
            transform: 'translateX(-50%)'
          }}>
            <a
              href="#features"
              onClick={(e) => scrollToSection(e, 'features')}
              style={{
                color: '#4b5563',
                fontWeight: 500,
                textDecoration: 'none',
                transition: 'color 300ms'
              }}
              onMouseEnter={(e) => e.target.style.color = '#4f46e5'}
              onMouseLeave={(e) => e.target.style.color = '#4b5563'}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              onClick={(e) => scrollToSection(e, 'how-it-works')}
              style={{
                color: '#4b5563',
                fontWeight: 500,
                textDecoration: 'none',
                transition: 'color 300ms'
              }}
              onMouseEnter={(e) => e.target.style.color = '#4f46e5'}
              onMouseLeave={(e) => e.target.style.color = '#4b5563'}
            >
              How It Works
            </a>
            <a
              href="#about"
              onClick={(e) => scrollToSection(e, 'about')}
              style={{
                color: '#4b5563',
                fontWeight: 500,
                textDecoration: 'none',
                transition: 'color 300ms'
              }}
              onMouseEnter={(e) => e.target.style.color = '#4f46e5'}
              onMouseLeave={(e) => e.target.style.color = '#4b5563'}
            >
              About
            </a>
          </div>
        )}

        {/* Right: Login Button */}
        <Link
          to="/login"
          style={{
            backgroundColor: '#4f46e5',
            color: '#ffffff',
            fontWeight: 600,
            padding: '0.625rem 1.5rem',
            borderRadius: '0.5rem',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
            transition: 'all 300ms',
            display: 'inline-block',
            cursor: 'pointer',
            border: 'none',
            textDecoration: 'none'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#4338ca';
            e.target.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = '#4f46e5';
            e.target.style.transform = 'translateY(0)';
          }}
        >
          Login
        </Link>
      </nav>
    </header>
  );
}

export default MainHeader;

