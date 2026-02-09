import { useNavigate } from 'react-router-dom';

function Footer() {
  const navigate = useNavigate();

  const goHome = () => {
    navigate('/');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <button type="button" className="footer-logo" onClick={goHome}>
          VerifiHireAI
          </button>
          <p className="footer-tagline">
            Building the future of recruitment with integrity and
            technology.
          </p>
          <div className="footeropyright">
            &copy; 2025 VerifiHireAI. All Rights Reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

