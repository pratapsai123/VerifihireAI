import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import MainHeader from '../components/MainHeader';
import Footer from '../components/Footer';
import '../styles/Home.css';
import { CheckCircle2, XCircle } from 'lucide-react';

/* ─────────────────────────────────────────────
   Scroll Reveal Component
───────────────────────────────────────────── */
function ScrollReveal({ children, delay = 0 }) {
  const ref = useRef(null);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        } else {
          entry.target.classList.remove('visible');
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );
    const currentRef = ref.current;
    if (currentRef) observer.observe(currentRef);
    return () => {
      if (currentRef) observer.unobserve(currentRef);
    };
  }, []);

  return (
    <div ref={ref} className="home-scroll-reveal" style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  );
}

const PLAN_DESCRIPTIONS = {
  'Trial': 'Explore with no commitment — 7-day access.',
  'Starter': 'For growing teams ready to streamline hiring.',
  'Pro': 'Advanced AI & verification for serious hiring teams.',
  'Enterprise': 'Custom scale & deployment for large organisations.',
};

const DEFAULT_PLANS = [
  {
    name: 'Trial',
    base_price_monthly: '0.00',
    discount_6_months: '0',
    discount_12_months: '0',
    features: [
      "Resume Screening - Results",
      "AI Assessments + Coding - Results",
      "Coding Assessment",
      "Company Admin (1)",
      "HR (2)",
      "Interviewer (Unlimited)"
    ],
    missing_features: [
      "AI Interview + Coding - Results",
      "Custom Assessments",
      "Results (AI + Coding combined)",
      "PDF Report Generation",
      "Live Interview",
      "Secure Agent",
      "Deep-Face Verification",
      "HR Manager",
      "HR (10)",
      "Integrity Scoring",
      "Plagiarism Check",
      "Behavior Check",
      "Create Own MCQ, MSQ, True/False, PDF Upload"
    ],
    is_popular: false,
    color_theme: '#10B981',
  },
  {
    name: 'Starter',
    base_price_monthly: '6999.00',
    discount_6_months: '10',
    discount_12_months: '20',
    features: [
      "Resume Screening - Results",
      "AI Assessments + Coding - Results",
      "AI Interview + Coding - Results",
      "Coding Assessment",
      "Custom Assessments",
      "Results (AI + Coding combined)",
      "PDF Report Generation",
      "Company Admin (1)",
      "HR Manager (2)",
      "HR (10)",
      "Interviewer (Unlimited)",
      "Integrity Scoring",
      "Plagiarism Check",
      "Behavior Check",
      "Create Own MCQ, MSQ, True/False, PDF Upload"
    ],
    missing_features: [
      "Live Interview",
      "Secure Agent",
      "Deep-Face Verification"
    ],
    is_popular: false,
    color_theme: '#3B82F6',
  },
  {
    name: 'Pro',
    base_price_monthly: '14999.00',
    discount_6_months: '15',
    discount_12_months: '25',
    features: [
      "Resume Screening - Results (Limited)",
      "AI Assessments + Coding - Results (Limited)",
      "AI Interview + Coding - Results (Limited)",
      "Coding Assessment (Limited)",
      "Custom Assessments (Limited)",
      "Results (AI + Coding combined)",
      "PDF Report Generation",
      "Live Interview (Limited)",
      "Secure Agent",
      "Deep-Face Verification",
      "Company Admin (1)",
      "HR Manager (2)",
      "HR (10)",
      "Interviewer (Unlimited)",
      "Integrity Scoring",
      "Plagiarism Check",
      "Behavior Check",
      "Create Own MCQ, MSQ, True/False, PDF Upload"
    ],
    missing_features: [],
    is_popular: true,
    color_theme: '#6366F1',
  },
  {
    name: 'Enterprise',
    base_price_monthly: '-1.00',
    discount_6_months: '0',
    discount_12_months: '0',
    features: [
      "Resume Screening - Results (Unlimited)",
      "AI Assessments + Coding - Results (Unlimited)",
      "AI Interview + Coding - Results (Unlimited)",
      "Coding Assessment (Unlimited)",
      "Custom Assessments (Unlimited)",
      "Results (AI + Coding combined)",
      "PDF Report Generation",
      "Live Interview (Unlimited)",
      "Secure Agent",
      "Deep-Face Verification",
      "Company Admin (1)",
      "HR Manager (2)",
      "HR (10)",
      "Interviewer (Unlimited)",
      "Integrity Scoring",
      "Plagiarism Check",
      "Behavior Check",
      "Create Own MCQ, MSQ, True/False, PDF Upload",
      "Custom Scale & Deployment",
      "Volume Discounts Available",
      "Dedicated Account Manager"
    ],
    missing_features: [],
    is_popular: false,
    color_theme: '#F59E0B',
  }
];

function Pricing() {
  const [billing, setBilling] = useState('monthly');
  const [pricingPlans, setPricingPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSpecialOffers, setShowSpecialOffers] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/plans/?t=${new Date().getTime()}`);
      const plans = response.data.plans || [];
      if (plans.length > 0) {
        setPricingPlans(plans);
      } else {
        setPricingPlans(DEFAULT_PLANS);
      }

      const coreNames = ['Trial', 'Starter', 'Pro', 'Enterprise'];
      const special = plans.filter(p => !coreNames.includes(p.name));
      if (special.length > 0) {
        setShowSpecialOffers(true);
      }
    } catch (error) {
      console.error("Failed to fetch plans", error);
      setPricingPlans(DEFAULT_PLANS);
    } finally {
      setLoading(false);
    }
  };

  const coreNames = ['Trial', 'Starter', 'Pro', 'Enterprise'];
  const corePlans = pricingPlans.filter(p => coreNames.includes(p.name));
  const specialOffers = pricingPlans.filter(p => !coreNames.includes(p.name));
  const activeOffer = specialOffers.length > 0 ? specialOffers[0] : null;

  let offerMonthlyDiscount = 0;
  let offer6MoDiscount = 0;
  let offer12MoDiscount = 0;
  if (activeOffer) {
    offerMonthlyDiscount = parseFloat(activeOffer.base_price_monthly) <= 100 ? parseFloat(activeOffer.base_price_monthly) : 0;
    offer6MoDiscount = parseFloat(activeOffer.discount_6_months) || 0;
    offer12MoDiscount = parseFloat(activeOffer.discount_12_months) || 0;
  }

  const getPricingDetails = (plan) => {
    const basePrice = parseFloat(plan.base_price_monthly);
    if (basePrice < 0) return { priceStr: 'Custom', originalPriceStr: null, discountStr: null, isOverridden: false };
    if (basePrice === 0) return { priceStr: 'Free', originalPriceStr: null, discountStr: null, isOverridden: false };

    let finalPrice = basePrice;
    let originalPriceStr = null;
    let discountStr = null;

    // Check if this plan is being overridden by an active offer
    const isOverridden = activeOffer && (plan.name === 'Starter' || plan.name === 'Pro' || plan.name.toLowerCase() === 'professional');

    let currentDiscount = 0;
    if (billing === 'monthly') {
      currentDiscount = isOverridden ? offerMonthlyDiscount : 0;
    } else if (billing === 'biannual') {
      currentDiscount = isOverridden ? offer6MoDiscount : parseFloat(plan.discount_6_months || 0);
    } else if (billing === 'annual') {
      currentDiscount = isOverridden ? offer12MoDiscount : parseFloat(plan.discount_12_months || 0);
    }

    if (currentDiscount > 0) {
      finalPrice = basePrice * (1 - (currentDiscount / 100));
      originalPriceStr = `₹${Math.round(basePrice).toLocaleString('en-IN')}`;
      discountStr = `Save ${currentDiscount}%`;
    }

    return {
      priceStr: `₹${Math.round(finalPrice).toLocaleString('en-IN')}`,
      originalPriceStr,
      discountStr,
      isOverridden
    };
  };

  const getBillingPeriodLabel = () => {
    if (billing === 'monthly') return '/ month';
    if (billing === 'biannual') return '/ month (Billed every 6 months)';
    return '/ month (Billed annually)';
  };

  return (
    <>
      <MainHeader />
      <main className="classic-home" style={{ minHeight: '80vh', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <section className="pricing-section" style={{ padding: '60px 10px' }}>
          <div className="pricing-container">
            <div className="pricing-header">
              <span className="badge-dark">Simple Pricing</span>
              <h2>Transparent Plans. No Hidden Fees.</h2>
              <p>Start free, scale as you grow. All plans include our core AI interviewing engine.</p>
              <div className="pricing-toggle">
                <button className={`ptoggle ${billing === 'monthly' ? 'ptoggle-active' : ''}`} onClick={() => setBilling('monthly')}>Monthly</button>
                <button className={`ptoggle ${billing === 'biannual' ? 'ptoggle-active' : ''}`} onClick={() => setBilling('biannual')}>6 Months</button>
                <button className={`ptoggle ${billing === 'annual' ? 'ptoggle-active' : ''}`} onClick={() => setBilling('annual')}>Annual</button>
              </div>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '50px 0', color: '#fff' }}>Loading plans...</div>
            ) : (
              <ScrollReveal>
                <div className="pricing-grid">
                  {corePlans.map((plan, i) => {
                    const pricing = getPricingDetails(plan);
                    return (
                      <div key={i} className={`pricing-card ${plan.is_popular ? "pricing-popular" : ""}`} style={{ "--pc": plan.color_theme }}>
                        {pricing.isOverridden && (
                          <div className="pricing-popular-badge" style={{ background: '#EF4444', top: '-14px', zIndex: 10 }}>
                            🎉 {activeOffer.name} Applied!
                          </div>
                        )}
                        {!pricing.isOverridden && plan.is_popular && <div className="pricing-popular-badge">⭐ Most Popular</div>}
                        <div className="pricing-card-top">
                          <div className="pricing-plan-name" style={{ color: plan.color_theme }}>{plan.name}</div>
                          <div className="pricing-price" style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                              {pricing.originalPriceStr && (
                                <span style={{ textDecoration: 'line-through', color: '#94A3B8', fontSize: '1.1rem', marginRight: '4px' }}>
                                  {pricing.originalPriceStr}
                                </span>
                              )}
                              <span className="pricing-amount">{pricing.priceStr}</span>
                              {pricing.discountStr && (
                                <span style={{ background: 'rgba(5, 205, 153, 0.2)', color: '#05CD99', padding: '2px 8px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 'bold' }}>
                                  {pricing.discountStr}
                                </span>
                              )}
                            </div>
                            <span className="pricing-period" style={{ marginTop: '0' }}>
                              {parseFloat(plan.base_price_monthly) < 0 ? 'Contact us' : parseFloat(plan.base_price_monthly) > 0 ? getBillingPeriodLabel() : 'Forever'}
                            </span>
                          </div>
                          <p className="pricing-desc">{PLAN_DESCRIPTIONS[plan.name] || plan.desc || 'Premium AI Hiring Features included.'}</p>
                        </div>
                        <ul className="pricing-features">
                          {plan.features && plan.features.map((f, j) => (
                            <li key={j} className="pricing-feature">
                              <CheckCircle2 size={14} color={plan.color_theme} />
                              {f}
                            </li>
                          ))}
                          {plan.missing_features && plan.missing_features.map((f, j) => (
                            <li key={`m${j}`} className="pricing-feature pricing-feature-missing" style={{ textDecoration: 'line-through' }}>
                              <XCircle size={14} color="rgba(255,255,255,0.2)" />
                              {f}
                            </li>
                          ))}
                        </ul>
                        <Link to={parseFloat(plan.base_price_monthly) < 0 ? "/contact" : `/signup?plan_id=${plan.id}&billing_cycle=${billing}`}
                          className={plan.is_popular ? 'btn-primary-premium pricing-cta' : 'btn-secondary-premium pricing-cta'}
                          style={plan.is_popular ? {} : { borderColor: `${plan.color_theme}40`, color: plan.color_theme }}
                        >
                          {parseFloat(plan.base_price_monthly) < 0 ? 'Talk to Sales' : parseFloat(plan.base_price_monthly) === 0 ? 'Get Started Free' : 'Choose Plan'}
                        </Link>
                      </div>
                    )
                  })}
                </div>
              </ScrollReveal>
            )}

            <p className="pricing-note" style={{ marginTop: '40px' }}>
              All plans include: 🔒 GDPR compliance · 🛡 Fraud detection · 📊 Score reports · 🌐 Multi-device support
            </p>
          </div>
        </section>
      </main>

      {/* Special Offers Modal */}
      {specialOffers.length > 0 && showSpecialOffers && (
        <div className="special-offer-modal">
          <div className="special-offer-overlay"></div>
          <div className="special-offer-content">
            <button className="special-offer-close" onClick={() => setShowSpecialOffers(false)}>&times;</button>
            <div className="special-offer-header">
              <h2>🎉 Special Offers Just For You!</h2>
              <p>Take advantage of these limited time customized pricing plans.</p>
            </div>
            <div className="special-offer-grid">
              {specialOffers.map((plan, i) => (
                <div key={i} className="pricing-card special-offer-card" style={{ "--pc": plan.color_theme || '#F59E0B' }}>
                  <div className="pricing-card-top">
                    <div className="pricing-plan-name" style={{ color: plan.color_theme || '#F59E0B' }}>{plan.name}</div>
                    <div className="pricing-price" style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        {getPricingDetails(plan).originalPriceStr && (
                          <span style={{ textDecoration: 'line-through', color: '#94A3B8', fontSize: '1.1rem', marginRight: '4px' }}>
                            {getPricingDetails(plan).originalPriceStr}
                          </span>
                        )}
                        <span className="pricing-amount">{getPricingDetails(plan).priceStr}</span>
                        {getPricingDetails(plan).discountStr && (
                          <span style={{ background: 'rgba(5, 205, 153, 0.2)', color: '#05CD99', padding: '2px 8px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 'bold' }}>
                            {getPricingDetails(plan).discountStr}
                          </span>
                        )}
                      </div>
                      <span className="pricing-period" style={{ marginTop: '0' }}>
                        {parseFloat(plan.base_price_monthly) < 0 ? 'Contact us' : parseFloat(plan.base_price_monthly) > 0 ? getBillingPeriodLabel() : 'Forever'}
                      </span>
                    </div>
                    <p className="pricing-desc">{PLAN_DESCRIPTIONS[plan.name] || plan.desc || 'Premium AI Hiring Features included.'}</p>
                  </div>
                  <ul className="pricing-features">
                    {plan.features && plan.features.map((f, j) => (
                      <li key={j} className="pricing-feature">
                        <CheckCircle2 size={14} color={plan.color_theme || '#F59E0B'} />
                        {f}
                      </li>
                    ))}
                    {plan.missing_features && plan.missing_features.map((f, j) => (
                      <li key={`m${j}`} className="pricing-feature pricing-feature-missing" style={{ textDecoration: 'line-through' }}>
                        <XCircle size={14} color="rgba(255,255,255,0.2)" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <Link to={parseFloat(plan.base_price_monthly) < 0 ? "/contact" : `/signup?plan_id=${plan.id}&billing_cycle=${billing}`}
                    className="btn-primary-premium pricing-cta"
                    style={{ background: plan.color_theme || '#F59E0B' }}
                  >
                    {parseFloat(plan.base_price_monthly) < 0 ? 'Talk to Sales' : parseFloat(plan.base_price_monthly) === 0 ? 'Get Started Free' : 'Claim Offer'}
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Floating Toggle Button */}
      {specialOffers.length > 0 && !showSpecialOffers && (
        <button className="special-offer-floating-btn" onClick={() => setShowSpecialOffers(true)}>
          🎁 Latest Offers
        </button>
      )}

      <Footer />
    </>
  );
}

export default Pricing;
