import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL, WS_BASE_URL } from '../apiConfig';

function NotificationCenter() {
    const [notifications, setNotifications] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [unreadCount, setUnreadCount] = useState(0);
    const navigate = useNavigate();
    const dropdownRef = useRef(null);

    // Load from local storage on mount
    useEffect(() => {
        const saved = localStorage.getItem('admin_notifications');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                setNotifications(parsed);
                setUnreadCount(parsed.filter(n => !n.read).length);
            } catch (e) {}
        }
    }, []);

    // Save to local storage when changed
    useEffect(() => {
        localStorage.setItem('admin_notifications', JSON.stringify(notifications));
        setUnreadCount(notifications.filter(n => !n.read).length);
    }, [notifications]);

    // Close on click outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Simulate notifications via polling (comparing state) since we can't change backend
    useEffect(() => {
        let prevCompanies = [];
        let prevUsers = [];

        const fetchState = async () => {
            try {
                const [compRes, userRes] = await Promise.all([
                    axios.get(`${API_BASE_URL}/superadmin/companies/`),
                    axios.get(`${API_BASE_URL}/superadmin/users/`)
                ]);
                const companies = compRes.data.companies || [];
                const users = userRes.data.users || [];

                if (prevCompanies.length > 0) {
                    companies.forEach(c => {
                        const oldC = prevCompanies.find(p => p.id === c.id);
                        if (!oldC) {
                            addNotification(`New company '${c.name}' registered`, 'company', c.id);
                        } else if (oldC.approval_status !== c.approval_status) {
                            addNotification(`Company '${c.name}' status changed to ${c.approval_status}`, 'status', c.id);
                        }
                    });
                }

                if (prevUsers.length > 0) {
                    users.forEach(u => {
                        const oldU = prevUsers.find(p => p.id === u.id);
                        if (!oldU) {
                            addNotification(`New user '${u.first_name}' registered`, 'user', u.id);
                        } else if (oldU.is_approved !== u.is_approved) {
                            addNotification(`User '${u.first_name}' was ${u.is_approved ? 'approved' : 'unapproved'}`, 'status', u.id);
                        }
                    });
                }

                prevCompanies = companies;
                prevUsers = users;
            } catch (err) {
                console.error('Notification polling error', err);
            }
        };

        fetchState();
        const interval = setInterval(fetchState, 15000);
        
        // Also try WebSocket if available
        let ws;
        try {
            ws = new WebSocket(`${WS_BASE_URL}/admin_events/`);
            ws.onmessage = (e) => {
                try {
                    const data = JSON.parse(e.data);
                    if (data.message) addNotification(data.message, data.type, data.id);
                } catch(err) {}
            };
        } catch(e) {}

        return () => {
            clearInterval(interval);
            if(ws) ws.close();
        };
    }, []);

    const addNotification = (text, type, id) => {
        setNotifications(prev => {
            const newNotif = {
                id: Date.now() + Math.random().toString(36).substr(2, 5),
                text,
                type,
                targetId: id,
                timestamp: new Date().toISOString(),
                read: false
            };
            // Keep last 50
            return [newNotif, ...prev].slice(0, 50);
        });
    };

    const markAllRead = () => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        setIsOpen(false);
    };

    const handleNotifClick = (notif) => {
        setNotifications(prev => prev.map(n => n.id === notif.id ? { ...n, read: true } : n));
        setIsOpen(false);
        if (notif.type === 'company') {
            navigate('/companies');
        } else if (notif.type === 'user') {
            navigate('/', { state: { activeTab: 'all_users' } });
        } else {
            navigate('/activity');
        }
    };

    const formatTime = (ts) => {
        const diff = Date.now() - new Date(ts).getTime();
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'Just now';
        if (mins < 60) return `${mins}m ago`;
        const hrs = Math.floor(mins / 60);
        if (hrs < 24) return `${hrs}h ago`;
        return `${Math.floor(hrs/24)}d ago`;
    };

    return (
        <div style={{ position: 'relative' }} ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    fontSize: '1.4rem', position: 'relative',
                    width: 40, height: 40, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    transition: 'background 0.2s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = '#f0f3f8'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
                🔔
                {unreadCount > 0 && (
                    <span style={{
                        position: 'absolute', top: 4, right: 4,
                        background: '#EE5D50', color: '#fff',
                        fontSize: '0.6rem', fontWeight: 800,
                        width: 18, height: 18, borderRadius: '50%',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        border: '2px solid #fff',
                    }}>
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <div style={{
                    position: 'absolute', top: '120%', right: 0,
                    width: 340, background: '#fff', borderRadius: 16,
                    boxShadow: '0 10px 40px rgba(112, 144, 176, 0.2)',
                    border: '1px solid #f0f3f8', zIndex: 1000,
                    overflow: 'hidden', animation: 'slideIn 0.2s ease',
                }}>
                    <div style={{
                        padding: '16px 20px', borderBottom: '1px solid #f0f3f8',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                        background: '#F8FAFC'
                    }}>
                        <h3 style={{ margin: 0, fontSize: '1rem', color: '#2B3674', fontWeight: 800 }}>Notifications</h3>
                        {unreadCount > 0 && (
                            <button onClick={markAllRead} style={{
                                background: 'none', border: 'none', color: '#4318FF',
                                fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer',
                            }}>Mark all read</button>
                        )}
                    </div>
                    
                    <div style={{ maxHeight: 360, overflowY: 'auto' }}>
                        {notifications.length === 0 ? (
                            <div style={{ padding: '30px', textAlign: 'center', color: '#A3AED0', fontSize: '0.85rem', fontWeight: 500 }}>
                                No notifications yet
                            </div>
                        ) : (
                            notifications.map(notif => (
                                <div
                                    key={notif.id}
                                    onClick={() => handleNotifClick(notif)}
                                    style={{
                                        padding: '16px 20px', borderBottom: '1px solid #f0f3f8',
                                        background: notif.read ? '#fff' : '#F4F7FE',
                                        cursor: 'pointer', transition: 'background 0.2s',
                                        display: 'flex', gap: 12, alignItems: 'flex-start',
                                    }}
                                    onMouseEnter={e => e.currentTarget.style.background = notif.read ? '#F8FAFC' : '#EBF0FE'}
                                    onMouseLeave={e => e.currentTarget.style.background = notif.read ? '#fff' : '#F4F7FE'}
                                >
                                    <div style={{
                                        width: 8, height: 8, borderRadius: '50%', marginTop: 6,
                                        background: notif.read ? 'transparent' : '#4318FF', flexShrink: 0
                                    }} />
                                    <div>
                                        <p style={{ margin: '0 0 6px', fontSize: '0.85rem', color: '#2B3674', fontWeight: notif.read ? 500 : 700, lineHeight: 1.4 }}>
                                            {notif.text}
                                        </p>
                                        <span style={{ fontSize: '0.7rem', color: '#A3AED0', fontWeight: 600 }}>{formatTime(notif.timestamp)}</span>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                    
                    <div style={{ padding: '12px', borderTop: '1px solid #f0f3f8', textAlign: 'center', background: '#fff' }}>
                        <button onClick={() => { setIsOpen(false); navigate('/activity'); }} style={{
                            background: 'none', border: 'none', color: '#4318FF',
                            fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
                        }}>View Activity Feed →</button>
                    </div>
                </div>
            )}
            <style>{`@keyframes slideIn { from { transform: translateY(-10px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }`}</style>
        </div>
    );
}

export default NotificationCenter;
