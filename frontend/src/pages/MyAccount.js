import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Camera, Check, AlertCircle, Loader2, X, Eye, EyeOff, Plus } from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import '../styles/MyAccount.css';

const MyAccount = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [formData, setFormData] = useState({
        full_name: '',
        organization_name: '',
        role: '',
    });
    const [avatarFile, setAvatarFile] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState(null);
    const fileInputRef = useRef(null);
    const photoOptionsRef = useRef(null);

    // Password Change Modal State
    const [showPwdModal, setShowPwdModal] = useState(false);
    const [pwdStep, setPwdStep] = useState('current'); // current -> new
    const [pwdLoading, setPwdLoading] = useState(false);
    const [pwdError, setPwdError] = useState('');
    const [pwdSuccess, setPwdSuccess] = useState('');
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showCurrentPassword, setShowCurrentPassword] = useState(false);
    const [showNewPassword, setShowNewPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    // Photo Edit State
    const [showPhotoOptions, setShowPhotoOptions] = useState(false);
    const [isAvatarDeleted, setIsAvatarDeleted] = useState(false);

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,12}$/;
    const passwordRequirements = [
        { id: 'length', label: '6-12 characters', test: (pwd) => pwd.length >= 6 && pwd.length <= 12 },
        { id: 'uppercase', label: 'At least one uppercase letter', test: (pwd) => /[A-Z]/.test(pwd) },
        { id: 'lowercase', label: 'At least one lowercase letter', test: (pwd) => /[a-z]/.test(pwd) },
        { id: 'number', label: 'At least one number', test: (pwd) => /\d/.test(pwd) },
        { id: 'special', label: 'At least one special character', test: (pwd) => /[^A-Za-z0-9]/.test(pwd) },
    ];
    const passwordRequirementStatuses = passwordRequirements.map(req => ({
        ...req,
        met: req.test(newPassword),
    }));
    const unmetPasswordRequirements = passwordRequirementStatuses.filter(req => !req.met);

    useEffect(() => {
        fetchProfile();
    }, []);

    useEffect(() => {
        if (message.text) {
            const timer = setTimeout(() => {
                setMessage({ type: '', text: '' });
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [message]);

    const fetchProfile = async () => {
        try {
            const storedUser = localStorage.getItem('user');
            if (!storedUser) return;
            const userData = JSON.parse(storedUser);

            const response = await axios.get(`${API_BASE_URL}/profile/`, {
                params: { email: userData.email }
            });

            const profile = response.data;
            setUser(profile);
            setFormData({
                full_name: `${profile.first_name || ''} ${profile.last_name || ''}`.trim(),
                organization_name: profile.organization_name || '',
                role: profile.role || '',
            });
            if (profile.avatar) {
                const avatarUrl = profile.avatar.startsWith('http')
                    ? profile.avatar
                    : `${API_BASE_URL.replace('/api', '')}${profile.avatar}`;
                setAvatarPreview(avatarUrl);
            }
            setLoading(false);
        } catch (err) {
            console.error("Error fetching profile:", err);
            setMessage({ type: 'error', text: 'Failed to load profile data.' });
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setAvatarFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setAvatarPreview(reader.result);
            };
            reader.readAsDataURL(file);
            setIsAvatarDeleted(false);
            setShowPhotoOptions(false);
        }
    };

    const handleDeletePhoto = () => {
        setAvatarFile(null);
        setAvatarPreview(null);
        setIsAvatarDeleted(true);
        setShowPhotoOptions(false);
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (photoOptionsRef.current && !photoOptionsRef.current.contains(event.target)) {
                setShowPhotoOptions(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleInitiatePasswordChange = (e) => {
        e.preventDefault();
        setShowPwdModal(true);
        setPwdError('');
        setPwdSuccess('');
        setPwdStep('current');
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setShowCurrentPassword(false);
        setShowNewPassword(false);
        setShowConfirmPassword(false);
    };

    const handleVerifyCurrentPassword = async (e) => {
        e.preventDefault();
        setPwdError('');
        setPwdSuccess('');

        if (!currentPassword) {
            setPwdError('Current password is required.');
            return;
        }

        setPwdLoading(true);
        try {
            await axios.post(`${API_BASE_URL}/verify-current-password/`, {
                email: user.email,
                password: currentPassword,
            });
            setPwdStep('new');
        } catch (err) {
            setPwdError(err.response?.data?.error || 'Incorrect current password.');
        } finally {
            setPwdLoading(false);
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        setPwdError('');
        setPwdSuccess('');

        if (!passwordRegex.test(newPassword)) {
            setPwdError('New password must meet all requirements.');
            return;
        }
        if (newPassword !== confirmPassword) {
            setPwdError('Passwords do not match.');
            return;
        }

        setPwdLoading(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/change-password/`, {
                email: user.email,
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword,
            });
            setPwdSuccess(res.data.message || 'Password updated successfully!');
            
            // Clear session and redirect to login
            setTimeout(() => {
                localStorage.removeItem('user');
                localStorage.removeItem('token');
                navigate('/login');
            }, 2000);
        } catch (err) {
            const errorMsg = err.response?.data?.error || 'Failed to update password.';
            setPwdError(errorMsg);
        } finally {
            setPwdLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage({ type: '', text: '' });

        try {
            const data = new FormData();
            data.append('email', user.email);
            data.append('full_name', formData.full_name);
            data.append('organization_name', formData.organization_name);
            data.append('role', formData.role);
            if (avatarFile) {
                data.append('avatar', avatarFile);
            } else if (isAvatarDeleted) {
                data.append('delete_avatar', 'true');
            }

            const response = await axios.post(`${API_BASE_URL}/profile/`, data, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setMessage({ type: 'success', text: 'Profile updated successfully!' });

            const updatedUser = {
                ...user,
                first_name: response.data.full_name.split(' ')[0],
                last_name: response.data.full_name.split(' ').slice(1).join(' '),
                role: formData.role,
                organization_name: formData.organization_name,
                avatar: response.data.avatar
            };
            setUser(updatedUser);
            localStorage.setItem('user', JSON.stringify(updatedUser));
            setIsAvatarDeleted(false);
            setAvatarFile(null);

            setTimeout(() => {
                window.location.reload();
            }, 1000);

        } catch (err) {
            console.error("Error updating profile:", err);
            setMessage({ type: 'error', text: err.response?.data?.error || 'Failed to update profile.' });
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="my-account-loading">
                <Loader2 className="spinner" />
                <p>Loading your account...</p>
            </div>
        );
    }

    const initials = formData.full_name
        ? formData.full_name.split(' ').map(n => n[0]).join('').toUpperCase()
        : (user?.email ? user.email[0].toUpperCase() : 'U');

    return (
        <div className="my-account-page">
            {message.text && (
                <div className={`toast-alert ${message.type === 'success' ? 'toast-success' : 'toast-error'}`}>
                    {message.type === 'success' ? <Check size={18} /> : <AlertCircle size={18} />}
                    <span>{message.text}</span>
                    <button className="toast-close" onClick={() => setMessage({ type: '', text: '' })}>
                        <X size={14} />
                    </button>
                </div>
            )}
            <main className="my-account-container">
                <div className="my-account-card">
                    <div className="account-top-header">
                        <h1>My Account</h1>
                    </div>
                    <hr className="header-divider" />

                    <div className="account-content-split">
                        <div className="account-sidebar">
                            <div className="profile-image-container" ref={photoOptionsRef}>
                                <div 
                                    className="profile-circle" 
                                    onClick={() => {
                                        if (avatarPreview) {
                                            setShowPhotoOptions(!showPhotoOptions);
                                        } else {
                                            fileInputRef.current.click();
                                        }
                                    }}
                                >
                                    {avatarPreview ? (
                                        <>
                                            <img src={avatarPreview} alt="Profile" className="profile-img" />
                                            <div className="profile-overlay">
                                                <div className="overlay-content">
                                                    <Camera size={24} />
                                                    <span>Edit Photo</span>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="profile-initials">
                                            {initials}
                                            <div className="add-photo-badge">
                                                <Plus size={14} strokeWidth={3} />
                                            </div>
                                        </div>
                                    )}
                                </div>
                                
                                {showPhotoOptions && avatarPreview && (
                                    <div className="photo-options-dropdown">
                                        <button className="photo-opt-item" onClick={() => { fileInputRef.current.click(); }}>
                                            Change Photo
                                        </button>
                                        <button className="photo-opt-item delete" onClick={handleDeletePhoto}>
                                            Delete Photo
                                        </button>
                                    </div>
                                )}
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    accept="image/*"
                                    style={{ display: 'none' }}
                                />
                            </div>
                        </div>

                        <div className="account-form-area">
                            <form onSubmit={handleSubmit} className="account-form">
                                <div className="form-grid">
                                    <div className="form-group disabled">
                                        <label>Full Name <span className="mandatory-mark">*</span></label>
                                        <input
                                            type="text"
                                            value={formData.full_name}
                                            disabled
                                            className="readonly-input"
                                        />
                                    </div>

                                    <div className="form-group disabled">
                                        <label>Organization <span className="mandatory-mark">*</span></label>
                                        <input
                                            type="text"
                                            value={formData.organization_name}
                                            disabled
                                            className="readonly-input"
                                        />
                                    </div>

                                    <div className="form-group disabled">
                                        <label>Organization Mail <span className="mandatory-mark">*</span></label>
                                        <input
                                            type="email"
                                            value={user?.email || ''}
                                            disabled
                                            className="readonly-input"
                                        />
                                    </div>

                                    <div className="form-group disabled">
                                        <label>Role <span className="mandatory-mark">*</span></label>
                                        <input
                                            type="text"
                                            value={formData.role.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                                            disabled
                                            className="readonly-input"
                                        />
                                    </div>

                                    <div className="form-group disabled">
                                        <label>Password <span className="mandatory-mark">*</span></label>
                                        <input
                                            type="password"
                                            value="********"
                                            disabled
                                            className="readonly-input"
                                        />
                                    </div>

                                    <div className="form-group disabled">
                                        <label>Updated Password Date <span className="mandatory-mark">*</span></label>
                                        <input
                                            type="text"
                                            value={user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : 'N/A'}
                                            disabled
                                            className="readonly-input"
                                        />
                                    </div>
                                </div>

                                <div className="form-actions">
                                    <a href="#" onClick={handleInitiatePasswordChange} className="change-password-link">
                                        Change Password?
                                    </a>
                                    <button type="submit" className="save-btn" disabled={saving}>
                                        {saving ? <Loader2 className="spinner" size={18} /> : null}
                                        {saving ? 'Saving...' : 'Save Changes'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </main>

            {showPwdModal && (
                <div className="pwd-modal-overlay">
                    <div className="pwd-modal-content">
                        <button className="pwd-modal-close" onClick={() => setShowPwdModal(false)}>
                            <X size={20} />
                        </button>
                        <h2 className="pwd-modal-title">Change Password</h2>

                        {pwdSuccess && <div className="inline-alert success"><Check size={16} /> {pwdSuccess}</div>}
                        {pwdError && <div className="inline-alert error"><AlertCircle size={16} /> {pwdError}</div>}

                        {pwdStep === 'current' ? (
                            <form onSubmit={handleVerifyCurrentPassword} className="pwd-modal-form">
                                <p className="pwd-modal-subtitle">Verify your current password to proceed.</p>
                                
                                <div className="form-group">
                                    <label>Current Password</label>
                                    <div style={{ position: 'relative' }}>
                                        <input
                                            type={showCurrentPassword ? "text" : "password"}
                                            placeholder="Enter current password"
                                            value={currentPassword}
                                            onChange={(e) => setCurrentPassword(e.target.value)}
                                            disabled={pwdLoading}
                                            style={{ paddingRight: '2.5rem', width: '100%' }}
                                        />
                                        <button type="button" onClick={() => setShowCurrentPassword(!showCurrentPassword)} className="pwd-eye-btn">
                                            {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </button>
                                    </div>
                                </div>

                                <button type="submit" className="save-btn" style={{ width: '100%', justifyContent: 'center', marginTop: '1.5rem' }} disabled={pwdLoading || !currentPassword}>
                                    {pwdLoading ? <Loader2 className="spinner" size={18} /> : null}
                                    {pwdLoading ? 'Verifying...' : 'Continue'}
                                </button>
                            </form>
                        ) : (
                            <form onSubmit={handleChangePassword} className="pwd-modal-form">
                                <p className="pwd-modal-subtitle">Set your new strong password.</p>
                                
                                <div className="form-group">
                                    <label>New Password</label>
                                    <div style={{ position: 'relative' }}>
                                        <input
                                            type={showNewPassword ? "text" : "password"}
                                            placeholder="Enter new password"
                                            value={newPassword}
                                            onChange={(e) => setNewPassword(e.target.value)}
                                            disabled={pwdLoading}
                                            style={{ paddingRight: '2.5rem', width: '100%' }}
                                        />
                                        <button type="button" onClick={() => setShowNewPassword(!showNewPassword)} className="pwd-eye-btn">
                                            {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </button>
                                    </div>
                                </div>

                                {newPassword.length > 0 && unmetPasswordRequirements.length > 0 && (
                                    <div className="pwd-requirements">
                                        <div className="pwd-req-title">Password must include:</div>
                                        {unmetPasswordRequirements.map(req => (
                                            <div key={req.id} className="pwd-req-item">• {req.label}</div>
                                        ))}
                                    </div>
                                )}

                                <div className="form-group" style={{ marginTop: '1rem' }}>
                                    <label>Confirm Password</label>
                                    <div style={{ position: 'relative' }}>
                                        <input
                                            type={showConfirmPassword ? "text" : "password"}
                                            placeholder="Confirm new password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            onPaste={(e) => e.preventDefault()}
                                            onCopy={(e) => e.preventDefault()}
                                            disabled={pwdLoading}
                                            style={{ paddingRight: '2.5rem', width: '100%' }}
                                        />
                                        <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="pwd-eye-btn">
                                            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                        </button>
                                    </div>
                                </div>
                                
                                {confirmPassword.length > 0 && newPassword !== confirmPassword && (
                                    <div style={{ color: '#ef4444', fontSize: '0.8rem', marginTop: '0.5rem', fontWeight: '500' }}>
                                        Passwords do not match
                                    </div>
                                )}

                                <div style={{ marginTop: '1.5rem' }}>
                                    <button type="submit" className="save-btn" style={{ width: '100%', justifyContent: 'center' }} disabled={pwdLoading || !newPassword || newPassword !== confirmPassword || unmetPasswordRequirements.length > 0}>
                                        {pwdLoading ? <Loader2 className="spinner" size={18} /> : null}
                                        {pwdLoading ? 'Updating...' : 'Change Password'}
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MyAccount;
