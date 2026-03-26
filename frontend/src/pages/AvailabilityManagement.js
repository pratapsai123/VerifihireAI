import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../apiConfig';
import { 
    Calendar, 
    Clock, 
    Info,
    CalendarCheck,
    Loader2,
    ChevronLeft,
    ChevronRight,
    CheckCircle,
    AlertTriangle
} from 'lucide-react';
import './AvailabilityManagement.css';

const AvailabilityManagement = () => {
    const [windows, setWindows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null); // ID of slot being toggled
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [viewDate, setViewDate] = useState(new Date());

    useEffect(() => {
        fetchAvailability();
    }, []);

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
            alert("Error updating slot.");
        } finally {
            setActionLoading(null);
        }
    };

    // Generate Hourly Slots from 9 AM to 6 PM
    const dailySlots = useMemo(() => {
        const slots = [];
        for (let h = 9; h <= 18; h++) {
            slots.push(`${h.toString().padStart(2, '0')}:00`);
        }
        return slots;
    }, []);

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

    return (
        <div className="availability-mgmt-container">
            <div className="mgmt-header">
                <h1>Manage Your Availability</h1>
                <p>Select a date and click time slots to open them for candidates. Each slot is 50 minutes.</p>
            </div>

            <div className="mgmt-grid-triple">
                {/* Column 1: Calendar */}
                <div className="mgmt-card calendar-side">
                    <div className="card-header">
                        <div className="header-info">
                            <Calendar size={20} className="text-indigo-600" />
                            <span>Select Date</span>
                        </div>
                        <div className="cal-nav">
                            <button onClick={() => setViewDate(new Date(viewDate.setMonth(viewDate.getMonth() - 1)))}><ChevronLeft size={18} /></button>
                            <button onClick={() => setViewDate(new Date(viewDate.setMonth(viewDate.getMonth() + 1)))}><ChevronRight size={18} /></button>
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
                <div className="mgmt-card slots-side">
                    <div className="card-header">
                        <div className="header-info">
                            <Clock size={20} className="text-indigo-600" />
                            <span>Available Slots</span>
                        </div>
                        <div className="selected-date-label">
                            {new Date(selectedDate).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
                        </div>
                    </div>

                    <div className="slots-picker-grid">
                        {dailySlots.map(time => {
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
                                    className={`slot-toggle-btn ${isSelected ? 'active' : ''} ${isBooked ? 'booked' : ''} ${isLoading ? 'loading' : ''} ${isPast ? 'past' : ''}`}
                                    onClick={() => !isLoading && !isPast && !isBooked && toggleSlot(time)}
                                    disabled={isLoading || isPast || isBooked}
                                    title={isBooked ? "This slot is booked and cannot be removed" : ""}
                                >
                                    {isLoading ? <Loader2 className="animate-spin" size={16} /> : (isBooked ? <CalendarCheck size={16} /> : <Clock size={16} />)}
                                    <span>{formatTime(time)}</span>
                                    {isBooked && <span className="booked-badge">Booked</span>}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Column 3: Summary/Info */}
                <div className="mgmt-card info-side">
                    <div className="section-title">
                        <Info size={20} className="text-indigo-600" />
                        <span>System Rules</span>
                    </div>
                    
                    <div className="rules-list">
                        <div className="rule-item">
                            <div className="rule-icon"><CheckCircle size={16} /></div>
                            <p>Each slot selected is <strong>50 minutes</strong> long.</p>
                        </div>
                        <div className="rule-item">
                            <div className="rule-icon"><CheckCircle size={16} /></div>
                            <p>A <strong>10-minute break</strong> is automatically added after each slot.</p>
                        </div>
                        <div className="rule-item">
                            <div className="rule-icon"><CheckCircle size={16} /></div>
                            <p>Candidates see these in real-time as available bookings.</p>
                        </div>
                        <div className="rule-item">
                            <div className="rule-icon"><AlertTriangle size={16} /></div>
                            <p>Overlapping with existing calendar events is discouraged.</p>
                        </div>
                    </div>

                    <div className="future-openings-mini">
                         <div className="mini-title">Total Opened Slots</div>
                         <div className="big-count">{windows.length}</div>
                         <p>Active availability windows across all dates.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AvailabilityManagement;
