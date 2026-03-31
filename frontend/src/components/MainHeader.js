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
  const navLinkStyle = {
    color: '#CCD6F6',
    fontWeight: 600,
    textDecoration: 'none',
    fontSize: '0.9rem',
    transition: 'all 0.3s ease',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
  };

  return (
    <header style={{
      background: 'rgba(10, 25, 47, 0.85)',
      backdropFilter: 'blur(15px)',
      WebkitBackdropFilter: 'blur(15px)',
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      width: '100%',
    }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0.8rem 3%',
        width: '100%',
        margin: '0 auto',
        boxSizing: 'border-box',
      }}>
        {/* Left: Logo */}
        <button
          type="button"
          onClick={goHome}
          style={{
            fontSize: '1.5rem',
            fontWeight: 800,
            color: '#FFFFFF',
            letterSpacing: '-0.03em',
            background: 'none',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            fontFamily: "'Poppins', sans-serif",
          }}
        >
          Verifi<span style={{ color: '#3B82F6' }}>HireAI</span>
        </button>

        {/* Center: Navigation Links removed */}

        {/* Right: Login Button */}
        <Link
          to="/login"
          style={{
            background: 'linear-gradient(135deg, #2563EB 0%, #1E40AF 100%)',
            color: '#ffffff',
            fontWeight: 600,
            padding: '12px 32px',
            borderRadius: '100px',
            boxShadow: '0 8px 20px rgba(37, 99, 235, 0.2)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            display: 'inline-block',
            cursor: 'pointer',
            border: 'none',
            textDecoration: 'none',
            fontSize: '0.95rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 12px 25px rgba(37, 99, 235, 0.35)';
            e.currentTarget.style.filter = 'brightness(1.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 8px 20px rgba(37, 99, 235, 0.2)';
            e.currentTarget.style.filter = 'brightness(1)';
          }}
        >
          Login
        </Link>
      </nav>
    </header>
  );
}

export default MainHeader;

