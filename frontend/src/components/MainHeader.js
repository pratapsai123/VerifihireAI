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
    <header className="header">
      <nav className="container nav-container">
        <button type="button" className="logo" onClick={goHome}>
          VerifiHireAI
        </button>

        {isHomePage && (
          <div className="nav-links">
            <a
              href="#features"
              className="nav-link"
              onClick={(e) => scrollToSection(e, 'features')}
            >
              Features
            </a>
            <a
              href="#how-it-works"
              className="nav-link"
              onClick={(e) => scrollToSection(e, 'how-it-works')}
            >
              How It Works
            </a>
            <a
              href="#about"
              className="nav-link"
              onClick={(e) => scrollToSection(e, 'about')}
            >
              About
            </a>
          </div>
        )}

        <div className="header-buttons">
          <a href="/support" className="support-btn">
            Support
          </a>
          <Link to="/login" className="login-btn" style={{ textDecoration: 'none' }}>
            Login
          </Link>
        </div>
      </nav>
    </header>
  );
}

export default MainHeader;


