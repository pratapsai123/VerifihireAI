import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import './PricingManagement.css';

function PricingManagement() {
    const [plans, setPlans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingPlan, setEditingPlan] = useState(null);

    const DEFAULT_FEATURES = [
        '5 AI Interviews / month',
        'Basic fraud detection',
        'Candidate score report',
        'Email support',
        '1 job role active',
        'Standard question bank',
        'Priority support',
        'Basic ATS export (CSV)',
        'White-label branding',
        'API access'
    ];

    // Form State
    const [formData, setFormData] = useState({
        name: '',
        base_price_monthly: 0,
        discount_6_months: 0,
        discount_12_months: 0,
        is_popular: false,
        color_theme: '#4F46E5',
        sort_order: 0,
        max_resume_screening: 0,
        max_ai_assessments: 0,
        max_ai_interviews: 0,
        max_fully_automatic: 0,
        max_custom_assessments: 0,
        max_coding_assessments: 0,
        max_live_interviews: 0,
        max_hr_managers: 0,
        max_hrs: 0,
        max_interviewers: 0,
        max_custom_questions: 0,
        features: DEFAULT_FEATURES,
        missing_features: ['']
    });

    useEffect(() => {
        fetchPlans(true);
    }, []);

    const fetchPlans = async (initial = false) => {
        try {
            if (initial) setLoading(true);
            const response = await axios.get(`${API_BASE_URL}/admin/plans/?t=${new Date().getTime()}`);
            setPlans(response.data.plans);
        } catch (error) {
            console.error('Failed to fetch plans', error);
        } finally {
            if (initial) setLoading(false);
        }
    };

    const handleOpenModal = (plan = null) => {
        if (plan) {
            setEditingPlan(plan);
            setFormData({
                ...plan,
                features: plan.features.length ? plan.features : [''],
                missing_features: plan.missing_features.length ? plan.missing_features : ['']
            });
        } else {
            setEditingPlan(null);
            setFormData({
                name: '',
                base_price_monthly: 0,
                discount_6_months: 0,
                discount_12_months: 0,
                is_popular: false,
                color_theme: '#4F46E5',
                sort_order: 0,
                max_resume_screening: 0,
                max_ai_assessments: 0,
                max_ai_interviews: 0,
                max_fully_automatic: 0,
                max_custom_assessments: 0,
                max_coding_assessments: 0,
                max_live_interviews: 0,
                max_hr_managers: 0,
                max_hrs: 0,
                max_interviewers: 0,
                max_custom_questions: 0,
                features: DEFAULT_FEATURES,
                missing_features: ['']
            });
        }
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setEditingPlan(null);
    };

    const handleFeatureChange = (index, value, type) => {
        const newFeatures = [...formData[type]];
        newFeatures[index] = value;
        setFormData({ ...formData, [type]: newFeatures });
    };

    const addFeatureField = (type) => {
        setFormData({ ...formData, [type]: [...formData[type], ''] });
    };

    const removeFeatureField = (index, type) => {
        const newFeatures = formData[type].filter((_, i) => i !== index);
        setFormData({ ...formData, [type]: newFeatures });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Cleanup empty features
        const cleanedData = {
            ...formData,
            features: formData.features.filter(f => f.trim() !== ''),
            missing_features: formData.missing_features.filter(f => f.trim() !== '')
        };

        try {
            if (editingPlan) {
                await axios.put(`${API_BASE_URL}/admin/plans/${editingPlan.id}/`, cleanedData);
            } else {
                await axios.post(`${API_BASE_URL}/admin/plans/`, cleanedData);
            }
            fetchPlans();
            handleCloseModal();
        } catch (error) {
            console.error('Error saving plan', error);
            alert('Failed to save plan. Check console for details.');
        }
    };

    const handleDelete = async (id) => {
        if(window.confirm('Are you sure you want to delete this plan?')) {
            try {
                await axios.delete(`${API_BASE_URL}/admin/plans/${id}/`);
                fetchPlans();
            } catch (error) {
                console.error('Error deleting plan', error);
            }
        }
    }

    if (loading) return <div className="pricing-admin-container">Loading...</div>;

    return (
        <div className="pricing-admin-container">
            <div className="pricing-admin-header">
                <h1>Pricing Management (INR)</h1>
                <button className="btn-primary" onClick={() => handleOpenModal()}>+ Add New Plan</button>
            </div>

            <div className="pricing-admin-list">
                {plans.map(plan => (
                    <div key={plan.id} className={`pricing-admin-card ${plan.is_popular ? 'popular' : ''}`} style={{ borderTop: `4px solid ${plan.color_theme}` }}>
                        {plan.is_popular && <div style={{position: 'absolute', top: -12, right: 20, background: 'var(--blue-accent)', color: '#fff', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem'}}>Most Popular</div>}
                        <h3 style={{color: plan.color_theme}}>{plan.name}</h3>
                        <div className="pricing-admin-price">₹{plan.base_price_monthly} <span style={{fontSize:'0.9rem', fontWeight:'normal', color:'#666'}}>/ month</span></div>
                        
                        <div className="pricing-admin-discounts">
                            <div><strong>6 Months:</strong> {plan.discount_6_months}% off</div>
                            <div><strong>12 Months:</strong> {plan.discount_12_months}% off</div>
                        </div>

                        <div className="pricing-admin-actions">
                            <button className="btn-secondary" onClick={() => handleOpenModal(plan)}>Edit</button>
                            {!(['trial', 'starter', 'pro', 'professional', 'enterprise', 'custom'].includes(plan.name.toLowerCase())) && (
                                <button className="btn-danger" onClick={() => handleDelete(plan.id)}>Delete</button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {isModalOpen && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                            <h2 style={{margin: 0}}>{editingPlan ? 'Edit Plan' : 'Add New Plan'}</h2>
                            <button onClick={handleCloseModal} type="button" style={{background: 'none', border: 'none', fontSize: '1.8rem', cursor: 'pointer', color: '#666', lineHeight: 1}}>&times;</button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                                <div className="form-group">
                                    <label>Plan Name</label>
                                    <input type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
                                </div>
                                <div className="form-group">
                                    <label>Base Price (Monthly) ₹</label>
                                    <input type="number" step="0.01" value={formData.base_price_monthly} onChange={e => setFormData({...formData, base_price_monthly: e.target.value})} required />
                                </div>
                                <div className="form-group">
                                    <label>6 Months Discount (%)</label>
                                    <input type="number" step="0.01" value={formData.discount_6_months} onChange={e => setFormData({...formData, discount_6_months: e.target.value})} required />
                                </div>
                                <div className="form-group">
                                    <label>12 Months Discount (%)</label>
                                    <input type="number" step="0.01" value={formData.discount_12_months} onChange={e => setFormData({...formData, discount_12_months: e.target.value})} required />
                                </div>
                                <div className="form-group">
                                    <label>Color Theme</label>
                                    <input type="color" value={formData.color_theme} onChange={e => setFormData({...formData, color_theme: e.target.value})} />
                                </div>
                                <div className="form-group">
                                    <label>Sort Order</label>
                                    <input type="number" value={formData.sort_order} onChange={e => setFormData({...formData, sort_order: e.target.value})} />
                                </div>
                                <div className="form-group" style={{gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: '8px'}}>
                                    <input type="checkbox" id="is_popular_check" checked={formData.is_popular} onChange={e => setFormData({...formData, is_popular: e.target.checked})} style={{width: 'auto', margin: 0}} />
                                    <label htmlFor="is_popular_check" style={{marginBottom: 0, cursor: 'pointer'}}>Mark as Most Popular</label>
                                </div>
                            </div>

                            <h3 style={{marginTop: '25px', marginBottom: '15px', borderBottom: '1px solid #eee', paddingBottom: '5px'}}>Quotas &amp; Limits (Invitations/Counts)</h3>
                            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', marginBottom: '20px', backgroundColor: '#f8fafc', padding: '15px', borderRadius: '8px'}}>
                                {[
                                    ['max_hr_managers', 'Max HR Managers'],
                                    ['max_hrs', 'Max HRs'],
                                    ['max_interviewers', 'Max Interviewers'],
                                    ['max_ai_assessments', 'Max AI Assessments'],
                                    ['max_ai_interviews', 'Max AI Interviews'],
                                    ['max_fully_automatic', 'Max Fully Automatic'],
                                    ['max_coding_assessments', 'Max Coding Assessments'],
                                    ['max_custom_assessments', 'Max Custom Assessments'],
                                    ['max_live_interviews', 'Max Live Interviews'],
                                    ['max_resume_screening', 'Max Resume Screening'],
                                    ['max_custom_questions', 'Max Custom Questions Bank'],
                                ].map(([field, label]) => (
                                    <div className="form-group" key={field}>
                                        <label>{label}</label>
                                        <input
                                            type="text"
                                            inputMode="numeric"
                                            pattern="[0-9]*"
                                            value={formData[field] === '' ? '' : (formData[field] ?? 0)}
                                            placeholder="0"
                                            onChange={e => {
                                                const raw = e.target.value.replace(/[^0-9]/g, '');
                                                setFormData(prev => ({
                                                    ...prev,
                                                    [field]: raw === '' ? '' : parseInt(raw, 10),
                                                }));
                                            }}
                                            onBlur={e => {
                                                // On blur, default empty to 0
                                                if (formData[field] === '' || formData[field] === undefined) {
                                                    setFormData(prev => ({ ...prev, [field]: 0 }));
                                                }
                                            }}
                                            style={{ appearance: 'textfield', MozAppearance: 'textfield' }}
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="form-group">
                                <label>Included Features</label>
                                {formData.features.map((feature, idx) => (
                                    <div key={idx} className="feature-item">
                                        <input type="text" value={feature} onChange={(e) => handleFeatureChange(idx, e.target.value, 'features')} placeholder="Feature description..." />
                                        <button type="button" onClick={() => removeFeatureField(idx, 'features')} className="btn-danger" style={{padding:'8px'}}>X</button>
                                    </div>
                                ))}
                                <button type="button" onClick={() => addFeatureField('features')} className="btn-secondary" style={{marginTop:'5px', fontSize:'0.8rem'}}>+ Add Feature</button>
                            </div>

                            <div className="form-group">
                                <label>Missing Features</label>
                                {formData.missing_features.map((feature, idx) => (
                                    <div key={idx} className="feature-item">
                                        <input type="text" value={feature} onChange={(e) => handleFeatureChange(idx, e.target.value, 'missing_features')} placeholder="Missing feature description..." />
                                        <button type="button" onClick={() => removeFeatureField(idx, 'missing_features')} className="btn-danger" style={{padding:'8px'}}>X</button>
                                    </div>
                                ))}
                                <button type="button" onClick={() => addFeatureField('missing_features')} className="btn-secondary" style={{marginTop:'5px', fontSize:'0.8rem'}}>+ Add Missing Feature</button>
                            </div>

                            <div className="modal-actions">
                                <button type="button" className="btn-secondary" onClick={handleCloseModal}>Cancel</button>
                                <button type="submit" className="btn-primary">Save Plan</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}

export default PricingManagement;
