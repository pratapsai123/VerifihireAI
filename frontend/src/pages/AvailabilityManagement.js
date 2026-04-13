import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { useNavigate } from 'react-router-dom';
import { 
    Calendar, 
    Clock, 
    Info,
    CalendarCheck,
    Loader2,
    ChevronLeft,
    ChevronRight,
    CheckCircle
} from 'lucide-react';
import '../styles/AvailabilityManagement.css';

const AvailabilityManagement = () => {
    const navigate = useNavigate();
    const [windows, setWindows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null); // ID of slot being toggled
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [viewDate, setViewDate] = useState(new Date());
    const [toast, setToast] = useState(null);
    const [showClearDayModal, setShowClearDayModal] = useState(false);
    const [clearDayLoading, setClearDayLoading] = useState(false);

    useEffect(() => {
        fetchAvailability();
    }, []);

    const showToast = (message, type = 'info') => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 2600);
    };

    const fetchAvailability = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_BASE_URL}/interviews/availability/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.data.success) {
                setWindows(res.data.windows);
            }
        } catch (err) {
            console.error("Failed to fetch availability", err);
        } finally {
            setLoading(false);
        }
    };

    const toggleSlot = async (startTime) => {
        const slotId = `${selectedDate}_${startTime}`;
        setActionLoading(slotId);
        
        try {
            const token = localStorage.getItem('token');
            const existing = windows.find(w => w.date === selectedDate && w.start_time === startTime);
            
            if (existing) {
                // DELETE
                await axios.delete(`${API_BASE_URL}/interviews/availability/manage/`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                    data: { id: existing.id }
                });
            } else {
                // CREATE (50 min duration)
                const [h, m] = startTime.split(':');
                const end = new Date(new Date().setHours(parseInt(h), parseInt(m) + 50, 0));
                const endStr = `${end.getHours().toString().padStart(2, '0')}:${end.getMinutes().toString().padStart(2, '0')}`;
                
                await axios.post(`${API_BASE_URL}/interviews/availability/manage/`, {
                    date: selectedDate,
                    start_time: startTime,
                    end_time: endStr
                }, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            }
            await fetchAvailability();
        } catch (err) {
            const errorMsg = err.response?.data?.error || "Error updating slot.";
            showToast(errorMsg, 'error');
        } finally {
            setActionLoading(null);
        }
    };

    // Generate interview slots for the day (06:00 → 23:00)
    const dailySlots = useMemo(() => {
        const slots = [];
        for (let h = 6; h <= 23; h++) {
            slots.push(`${h.toString().padStart(2, '0')}:00`);
        }
        return slots;
    }, []);

    const groupedSlots = useMemo(() => {
        const groups = { morning: [], afternoon: [], evening: [] };
        dailySlots.forEach((slot) => {
            const hour = parseInt(slot.split(':')[0], 10);
            if (hour < 12) groups.morning.push(slot);
            else if (hour < 17) groups.afternoon.push(slot);
            else groups.evening.push(slot);
        });
        return groups;
    }, [dailySlots]);

    const formatTime = (timeStr) => {
        const [h, m] = timeStr.split(':');
        const hour = parseInt(h);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:${m} ${ampm}`;
    };

    // Calendar Helpers (reused logic)
    const getDaysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
    const getFirstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();

    const calendarDays = useMemo(() => {
        const year = viewDate.getFullYear();
        const month = viewDate.getMonth();
        const daysInMonth = getDaysInMonth(year, month);
        const firstDay = getFirstDayOfMonth(year, month);
        
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const days = [];
        for (let i = 0; i < firstDay; i++) days.push(null);
        for (let i = 1; i <= daysInMonth; i++) {
            const checkDate = new Date(year, month, i);
            const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${i.toString().padStart(2, '0')}`;
            const hasWindows = windows.some(w => w.date === dateStr);
            const isPast = checkDate < today;
            days.push({ 
                day: i, 
                dateStr, 
                hasWindows, 
                isPast,
                isToday: today.toDateString() === checkDate.toDateString() 
            });
        }
        return days;
    }, [viewDate, windows]);

    if (loading) return (
        <div className="availability-mgmt-container">
            <div className="skeleton-loading-center">
                <Loader2 className="animate-spin" size={48} color="#6366f1" />
                <p>Loading your schedule...</p>
            </div>
        </div>
    );

    const selectedDateCount = windows.filter(w => w.date === selectedDate).length;
    const selectedDateBookedCount = windows.filter(w => w.date === selectedDate && w.is_booked).length;
    const totalBookedCount = windows.filter(w => w.is_booked).length;

    const clearDaySlots = async () => {
        try {
            setClearDayLoading(true);
            const unbooked = windows.filter(w => w.date === selectedDate && !w.is_booked);
            if (unbooked.length === 0) {
                showToast('No unbooked slots available to clear on this date.', 'info');
                return;
            }
            const token = localStorage.getItem('token');
            for (const slot of unbooked) {
                await axios.delete(`${API_BASE_URL}/interviews/availability/manage/`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                    data: { id: slot.id }
                });
            }
            await fetchAvailability();
            showToast(`Cleared ${unbooked.length} slot(s) for selected day.`, 'success');
        } catch (err) {
            showToast(err.response?.data?.error || 'Failed to clear selected day slots.', 'error');
        } finally {
            setClearDayLoading(false);
            setShowClearDayModal(false);
        }
    };

    return (
        <div className="availability-mgmt-container">
            <div className="mgmt-shell">
                <div className="mgmt-header">
                    <div className="mgmt-header-left">
                        <div className="mgmt-header-icon">
                            <Calendar size={24} />
                        </div>
                        <div>
                            <h1>Manage Your Availability</h1>
                            <p>Pick interview slots for your upcoming live interviews</p>
                        </div>
                    </div>
                    <button className="mgmt-btn-back" type="button" onClick={() => navigate('/dashboard')}>
                        <ChevronLeft size={16} />
                        Back
                    </button>
                </div>

                <div className="mgmt-stats-row">
                    <div className="mgmt-stat">
                        <span className="mgmt-stat-value">{selectedDateCount}</span>
                        <span className="mgmt-stat-label">Slots on Selected Day</span>
                    </div>
                    <div className="mgmt-stat-divider" />
                    <div className="mgmt-stat">
                        <span className="mgmt-stat-value">{selectedDateBookedCount}</span>
                        <span className="mgmt-stat-label">Booked on Selected Day</span>
                    </div>
                    <div className="mgmt-stat-divider" />
                    <div className="mgmt-stat">
                        <span className="mgmt-stat-value">{windows.length}</span>
                        <span className="mgmt-stat-label">Total Active Slots</span>
                    </div>
                    <div className="mgmt-stat-divider" />
                    <div className="mgmt-stat">
                        <span className="mgmt-stat-value">{totalBookedCount}</span>
                        <span className="mgmt-stat-label">Total Booked Slots</span>
                    </div>
                </div>

                <div className="mgmt-upper-layout triple">
                {/* Column 1: Calendar */}
                <div className="mgmt-card calendar-side glass-card compact">
                    <div className="card-header">
                        <div className="header-info">
                            <Calendar size={18} className="text-indigo-600" />
                            <span className="text-sm">Select Date</span>
                        </div>
                        <div className="cal-nav">
                                <button
                                    onClick={() => setViewDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1))}
                                >
                                    <ChevronLeft size={16} />
                                </button>
                                <button
                                    onClick={() => setViewDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1))}
                                >
                                    <ChevronRight size={16} />
                                </button>
                        </div>
                    </div>
                    
                    <div className="mini-calendar">
                        <div className="calendar-month-name">{viewDate.toLocaleString('default', { month: 'long', year: 'numeric' })}</div>
                        <div className="mini-weekdays">
                            {['S','M','T','W','T','F','S'].map(d => <div key={d}>{d}</div>)}
                        </div>
                        <div className="mini-grid">
                            {calendarDays.map((d, i) => d ? (
                                <button 
                                    key={d.dateStr} 
                                    className={`cal-day ${selectedDate === d.dateStr ? 'selected' : ''} ${d.hasWindows ? 'active' : ''} ${d.isToday ? 'today' : ''} ${d.isPast ? 'past' : ''}`}
                                    onClick={() => !d.isPast && setSelectedDate(d.dateStr)}
                                    disabled={d.isPast}
                                >
                                    {d.day}
                                    {d.hasWindows && <div className="active-dot"></div>}
                                </button>
                            ) : <div key={`p-${i}`} className="cal-empty"></div>)}
                        </div>
                    </div>
                </div>

                {/* Column 2: Slot Grid */}
                <div className="mgmt-card slots-side glass-card compact">
                    <div className="card-header">
                        <div className="header-info">
                            <Clock size={18} className="text-indigo-600" />
                            <span className="text-sm">Available Slots</span>
                        </div>
                        <div className="slot-header-actions">
                            <div className="selected-date-label text-xs">
                                {new Date(selectedDate).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
                            </div>
                            <button 
                                className="clear-day-btn"
                                onClick={() => setShowClearDayModal(true)}
                            >
                                Clear Day
                            </button>
                        </div>
                    </div>

                    {[
                        { key: 'morning', title: 'Morning', slots: groupedSlots.morning },
                        { key: 'afternoon', title: 'Afternoon', slots: groupedSlots.afternoon },
                        { key: 'evening', title: 'Evening', slots: groupedSlots.evening },
                    ].map(group => (
                        <div className="slot-group" key={group.key}>
                            <div className="slot-group-title">{group.title}</div>
                            <div className="slots-picker-grid mini">
                                {group.slots.map(time => {
                            const window = windows.find(w => w.date === selectedDate && w.start_time === time);
                            const isSelected = !!window;
                            const isBooked = window?.is_booked;
                            const isLoading = actionLoading === `${selectedDate}_${time}`;
                            
                            // Check if slot is in the past (with a 60-minute prep buffer)
                            const [h, m] = time.split(':');
                            const slotDateTime = new Date(selectedDate);
                            slotDateTime.setHours(parseInt(h), parseInt(m), 0);
                            
                            const bufferTime = new Date();
                            bufferTime.setMinutes(bufferTime.getMinutes() + 60); // 1 hour buffer
                            const isPast = slotDateTime < bufferTime;

                            return (
                                <button
                                    key={time}
                                    className={`slot-toggle-btn sm ${isSelected ? 'active' : ''} ${isBooked ? 'booked' : ''} ${isLoading ? 'loading' : ''} ${isPast ? 'past' : ''}`}
                                    onClick={() => !isLoading && !isPast && !isBooked && toggleSlot(time)}
                                    disabled={isLoading || isPast || isBooked}
                                    title={isBooked ? "This slot is booked and cannot be removed" : ""}
                                >
                                    <div className="slot-inner text-xs">
                                        {isLoading ? <Loader2 className="animate-spin" size={14} /> : (isBooked ? <CalendarCheck size={14} /> : <Clock size={14} />)}
                                        <span>{formatTime(time)}</span>
                                    </div>
                                    {isBooked && <span className="booked-badge sm">Booked</span>}
                                </button>
                            );
                        })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Column 3: Rules & Highlights */}
                <div className="mgmt-card info-side glass-card compact">
                    <div className="section-title text-sm">
                        <Info size={18} className="text-indigo-600" />
                        <span>System Rules</span>
                    </div>
                    
                    <div className="rules-vertical-stack">
                        <div className="rule-item-mini">
                            <div className="rule-icon sm"><CheckCircle size={14} /></div>
                            <div className="rule-text">
                                <h4 className="text-xs">50 Min Slots</h4>
                                <p className="text-xxs">Each slot selected is 50 minutes long.</p>
                            </div>
                        </div>
                        <div className="rule-item-mini">
                            <div className="rule-icon sm"><CheckCircle size={14} /></div>
                            <div className="rule-text">
                                <h4 className="text-xs">10 Min Break</h4>
                                <p className="text-xxs">A 10-minute break is included.</p>
                            </div>
                        </div>
                        <div className="rule-item-mini">
                            <div className="rule-icon sm"><CheckCircle size={14} /></div>
                            <div className="rule-text">
                                <h4 className="text-xs">Live Sync</h4>
                                <p className="text-xxs">Syncs instantly with bookings.</p>
                            </div>
                        </div>
                    </div>

                    <div className="stats-spacer"></div>
                    <div className="stat-card mini">
                        <div className="mini-title text-xxs">Selected Date</div>
                        <div className="big-count sm">{new Date(selectedDate).toLocaleDateString(undefined, { day: '2-digit', month: 'short' })}</div>
                        <p>{selectedDateCount} active · {selectedDateBookedCount} booked</p>
                    </div>
                </div>
            </div>
            </div>

            {toast && (
                <div className={`mgmt-toast ${toast.type}`}>
                    {toast.message}
                </div>
            )}

            {showClearDayModal && (
                <div className="mgmt-confirm-overlay" onClick={() => !clearDayLoading && setShowClearDayModal(false)}>
                    <div className="mgmt-confirm-card" onClick={(e) => e.stopPropagation()}>
                        <h3>Clear Selected Day Slots?</h3>
                        <p>Only unbooked slots will be removed. Booked slots remain protected.</p>
                        <div className="mgmt-confirm-actions">
                            <button
                                className="mgmt-confirm-cancel"
                                type="button"
                                disabled={clearDayLoading}
                                onClick={() => setShowClearDayModal(false)}
                            >
                                Cancel
                            </button>
                            <button
                                className="mgmt-confirm-danger"
                                type="button"
                                disabled={clearDayLoading}
                                onClick={clearDaySlots}
                            >
                                {clearDayLoading ? 'Clearing...' : 'Clear Day'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AvailabilityManagement;
