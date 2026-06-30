import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Calendar as CalendarIcon, 
  Clock, 
  User, 
  CheckCircle, 
  AlertTriangle,
  ChevronRight,
  ChevronLeft,
  Info,
  RefreshCw,
  Building
} from 'lucide-react';
import { API_BASE_URL } from '../apiConfig';
import Lottie from 'lottie-react';
import '../styles/BookInterview.css';

// Public Lottie Animation URL for success
const SUCCESS_LOTTIE_URL = "https://lottie.host/5456f916-2495-48b4-933e-e64db8061eb0/rM6YclpB4U.json";

const API_BASE = API_BASE_URL;

const BookInterview = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    
    const [loading, setLoading] = useState(true);
    const [slots, setSlots] = useState([]);
    const [selectedSlot, setSelectedSlot] = useState(null);
    const [activeDate, setActiveDate] = useState(null);
    const [viewDate, setViewDate] = useState(new Date()); // For month navigation
    const [windowInfo, setWindowInfo] = useState(null); // { window_start, window_end }
    const [reservationExpiry, setReservationExpiry] = useState(null);
    const [countdown, setCountdown] = useState(0);
    const [error, setError] = useState(null);
    const [bookingSuccess, setBookingSuccess] = useState(false);
    const [bookingDetails, setBookingDetails] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [userTimezone, setUserTimezone] = useState('');
    const [successLottie, setSuccessLottie] = useState(null);

    useEffect(() => {
        // Detect User Timezone
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
        setUserTimezone(tz);

        // Fetch Lottie JSON gracefully
        fetch(SUCCESS_LOTTIE_URL)
            .then(res => {
                if (res.ok && res.headers.get('content-type')?.includes('application/json')) {
                    return res.json();
                }
                throw new Error('Not a valid JSON lottie');
            })
            .then(data => setSuccessLottie(data))
            .catch(err => {
                console.warn("Lottie failed to load, using SVG fallback.");
                setSuccessLottie(null);
            });
    }, []);

    const fetchSlots = useCallback(async () => {
        try {
            const res = await axios.get(`${API_BASE}/interviews/slots/${token}/`);
            if (res.data.success) {
                if (res.data.already_booked) {
                    setBookingDetails(res.data.booking_details);
                    setBookingSuccess(true);
                    setLoading(false);
                    return;
                }
                const fetchedSlots = res.data.slots;
                setSlots(fetchedSlots);

                // Capture the HR-defined booking window from the backend
                if (res.data.window_info) {
                    setWindowInfo(res.data.window_info);
                }
                
                // Set initial active date if none selected
                if (fetchedSlots.length > 0 && !activeDate) {
                    const firstDate = fetchedSlots[0].date;
                    setActiveDate(firstDate);
                    setViewDate(new Date(firstDate + 'T12:00:00')); // noon avoids timezone flip
                }
            }
        } catch (err) {
            console.error("Error fetching slots:", err);
            setError(err.response?.data?.error || "Failed to load slots.");
        } finally {
            setLoading(false);
        }
    }, [token, activeDate]);

    useEffect(() => {
        fetchSlots();
        const interval = setInterval(fetchSlots, 10000);
        return () => clearInterval(interval);
    }, [fetchSlots]);

    useEffect(() => {
        if (countdown > 0) {
            const timer = setInterval(() => {
                setCountdown(prev => prev - 1);
            }, 1000);
            return () => clearInterval(timer);
        } else if (countdown === 0 && selectedSlot && reservationExpiry) {
            setSelectedSlot(null);
            setReservationExpiry(null);
        }
    }, [countdown, selectedSlot, reservationExpiry]);

    const handleReserve = async (slotId) => {
        setError(null);
        setSubmitting(true);
        try {
            const res = await axios.post(`${API_BASE}/interviews/slots/${token}/reserve/`, { slot_id: slotId });
            if (res.data.success) {
                const realId = res.data.slot_id;
                const expiry = new Date(res.data.expiry);
                
                // Optimistically update the slot in our local list so the UI updates IMMEDIATELY
                setSlots(prevSlots => prevSlots.map(s => {
                    if (String(s.id) === String(slotId)) {
                        return { ...s, id: realId, status: 'reserved', is_mine: true };
                    }
                    return s;
                }));

                setSelectedSlot(realId);
                setReservationExpiry(expiry);
                setCountdown(Math.floor((expiry - new Date()) / 1000));
                fetchSlots(); // Still do a background refresh for total sync
            }
        } catch (err) {
            setError(err.response?.data?.error || "Failed to reserve slot.");
        } finally {
            setSubmitting(false);
        }
    };

    const handleConfirm = async () => {
        if (!selectedSlot) return;
        setSubmitting(true);
        setError(null);
        try {
            const res = await axios.post(`${API_BASE}/interviews/slots/${token}/confirm/`, { slot_id: selectedSlot });
            if (res.data.success) {
                setBookingSuccess(true);
                setBookingDetails(res.data.booking_details);
            }
        } catch (err) {
            setError(err.response?.data?.error || "Booking failed.");
        } finally {
            setSubmitting(false);
        }
    };

    const slotGroups = useMemo(() => {
        const groups = {};
        slots.forEach(slot => {
            if (!groups[slot.date]) groups[slot.date] = [];
            groups[slot.date].push(slot);
        });
        
        // Sort slots within each date chronologically
        Object.keys(groups).forEach(date => {
            groups[date].sort((a, b) => {
                const timeA = new Date(`1970-01-01 ${a.start_time}`);
                const timeB = new Date(`1970-01-01 ${b.start_time}`);
                return timeA - timeB;
            });
        });
        
        return groups;
    }, [slots]);

    const availableDates = useMemo(() => Object.keys(slotGroups), [slotGroups]);

    // Calendar Helper Functions
    const getDaysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
    const getFirstDayOfMonth = (year, month) => new Date(year, month, 1).getDay();

    const calendarDays = useMemo(() => {
        const year = viewDate.getFullYear();
        const month = viewDate.getMonth();
        const daysInMonth = getDaysInMonth(year, month);
        const firstDay = getFirstDayOfMonth(year, month);

        const days = [];
        // Fill previous month padding
        for (let i = 0; i < firstDay; i++) days.push(null);
        // Fill actual days
        for (let i = 1; i <= daysInMonth; i++) {
            const currentCellDate = new Date(year, month, i);
            const dateStr = `${year}-${(month + 1).toString().padStart(2, '0')}-${i.toString().padStart(2, '0')}`;

            // A date is valid only if the backend returned it as an available slot date.
            // All other dates (weekends, holidays, dates outside the 7-day window) are hidden.
            const isInWindow = availableDates.includes(dateStr);

            days.push({
                day: i,
                dateStr,
                hasSlots: isInWindow,
                isToday: new Date().toDateString() === currentCellDate.toDateString(),
                isOutsideWindow: !isInWindow,
            });
        }
        return days;
    }, [viewDate, availableDates]);

    // ── Window-aware month navigation ─────────────────────────────────────────
    // Derive the first and last months that contain valid booking dates.
    // This covers all three scenarios the user described:
    //   1) Window spans Jan→Feb  → backward from Feb and forward from Jan are allowed
    //   2) Window all in March   → both arrows disabled (no adjacent months)
    //   3) General case          → disable whichever boundary you've already reached
    const windowMonths = useMemo(() => {
        if (!windowInfo?.window_start || !windowInfo?.window_end) return null;
        // Parse dates at noon to avoid timezone shift to previous day
        const start = new Date(windowInfo.window_start + 'T12:00:00');
        const end   = new Date(windowInfo.window_end   + 'T12:00:00');
        return {
            firstYear:  start.getFullYear(),
            firstMonth: start.getMonth(), // 0-indexed
            lastYear:   end.getFullYear(),
            lastMonth:  end.getMonth(),
        };
    }, [windowInfo]);

    const canGoPrev = useMemo(() => {
        if (!windowMonths) return false;
        const curYear  = viewDate.getFullYear();
        const curMonth = viewDate.getMonth();
        // Can go back only if there is a month BEFORE this one that is still within the window
        return (
            curYear > windowMonths.firstYear ||
            (curYear === windowMonths.firstYear && curMonth > windowMonths.firstMonth)
        );
    }, [viewDate, windowMonths]);

    const canGoNext = useMemo(() => {
        if (!windowMonths) return false;
        const curYear  = viewDate.getFullYear();
        const curMonth = viewDate.getMonth();
        // Can go forward only if there is a month AFTER this one that is still within the window
        return (
            curYear < windowMonths.lastYear ||
            (curYear === windowMonths.lastYear && curMonth < windowMonths.lastMonth)
        );
    }, [viewDate, windowMonths]);

    const handleMonthChange = (offset) => {
        setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + offset, 1));
    };

    const formatDateFull = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
    };

    const getCalendarLinks = () => {
        if (!bookingDetails) return {};
        const dateStr = bookingDetails.date;
        const startTimeStr = bookingDetails.time.split(' - ')[0];
        const start = new Date(`${dateStr} ${startTimeStr}`);
        const end = new Date(start.getTime() + 50 * 60000);
        const formatISO = (date) => date.toISOString().replace(/-|:|\.\d\d\d/g, "");
        const subject = encodeURIComponent(`Interview @ VerifiHire`);
        const body = encodeURIComponent(`Your live interview has been scheduled. Please be on time.\n\nMeeting link will be shared via email.`);
        return {
            google: `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${subject}&dates=${formatISO(start)}/${formatISO(end)}&details=${body}`,
            outlook: `https://outlook.office.com/calendar/0/deeplink/compose?path=/calendar/action/compose&rru=addevent&subject=${subject}&body=${body}&startdt=${start.toISOString()}&enddt=${end.toISOString()}`
        };
    };

    if (loading) return (
        <div className="enterprise-booking-wrapper">
            <div className="booking-layout">
                <div className="booking-intro">
                    <div className="skeleton" style={{ width: '300px', height: '32px', marginBottom: '10px' }}></div>
                    <div className="skeleton" style={{ width: '450px', height: '18px' }}></div>
                </div>
                <div className="booking-main-grid-triple">
                    <div className="skeleton calendar-skeleton"></div>
                    <div className="skeleton times-skeleton"></div>
                    <div className="skeleton sidebar-skeleton"></div>
                </div>
            </div>
        </div>
    );

    if (bookingSuccess) return (
        <div className="booking-container success-mode">
            <div className="booking-card success-card animation-ready">
                <div className="lottie-success-container">
                    {successLottie ? (
                        <Lottie animationData={successLottie} loop={false} />
                    ) : (
                        <div className="success-icon-wrapper">
                            <CheckCircle className="success-icon-svg" size={60} />
                        </div>
                    )}
                </div>
                <h1 className="success-title">Confirmed!</h1>
                <p className="success-subtitle">We've reserved your spot. Preparation details have been sent to your inbox.</p>
                
                <div className="booking-summary-box">
                    <div className="summary-item">
                        <CalendarIcon size={18} className="summary-icon" />
                        <div className="summary-text">
                            <label>Scheduled Date</label>
                            <span>{formatDateFull(bookingDetails.date)}</span>
                        </div>
                    </div>
                    <div className="summary-item">
                        <Clock size={18} className="summary-icon" />
                        <div className="summary-text">
                            <label>Time Slot</label>
                            <span>{bookingDetails.time}</span>
                        </div>
                    </div>
                    <div className="summary-item">
                        <User size={18} className="summary-icon" />
                        <div className="summary-text">
                            <label>Host</label>
                            <span>{bookingDetails.interviewer}</span>
                        </div>
                    </div>
                    {bookingDetails.company && (
                        <div className="summary-item">
                            <Building size={18} className="summary-icon" />
                            <div className="summary-text">
                                <label>Organization</label>
                                <span>{bookingDetails.company}</span>
                            </div>
                        </div>
                    )}
                </div>

                <div className="success-info-banner">
                    <Info size={16} />
                    <span>A calendar invite has been dispatched.</span>
                </div>

                <div className="calendar-sync-block">
                    <div className="calendar-sync-actions">
                        <a href={getCalendarLinks().google} target="_blank" rel="noopener noreferrer" className="sync-btn google-sync">
                            Google Calendar
                        </a>
                        <a href={getCalendarLinks().outlook} target="_blank" rel="noopener noreferrer" className="sync-btn outlook-sync">
                            Outlook
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );

    const activeSlots = slotGroups[activeDate] || [];

    return (
        <div className="enterprise-booking-wrapper">
            <div className="booking-layout">
                <div className="booking-intro">
                    <h1 className="title">Select an Interview Slot</h1>
                    <div className="timezone-intelligence-badge">
                        <Clock size={16} className="globe-icon" />
                        <span>Times are shown in your local time: <span className="timezone-name">{userTimezone}</span></span>
                    </div>
                    <p className="description">Choose a time that fits your schedule for the 50-minute live session.</p>
                </div>

                <div className="booking-main-grid-triple">
                    {/* Column 1: Professional Month Calendar */}
                    <div className="calendar-card">
                        <div className="calendar-header">
                            <h3>{viewDate.toLocaleString('default', { month: 'long', year: 'numeric' })}</h3>
                            <div className="calendar-nav">
                                <button
                                    onClick={() => canGoPrev && handleMonthChange(-1)}
                                    disabled={!canGoPrev}
                                    className={!canGoPrev ? 'nav-btn-disabled' : ''}
                                    title={!canGoPrev ? 'No earlier dates in your booking window' : 'Previous month'}
                                >
                                    <ChevronLeft size={20} />
                                </button>
                                <button
                                    onClick={() => canGoNext && handleMonthChange(1)}
                                    disabled={!canGoNext}
                                    className={!canGoNext ? 'nav-btn-disabled' : ''}
                                    title={!canGoNext ? 'No later dates in your booking window' : 'Next month'}
                                >
                                    <ChevronRight size={20} />
                                </button>
                            </div>
                        </div>
                        
                        <div className="calendar-weekdays">
                            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => (
                                <div key={d} className="weekday-label">{d}</div>
                            ))}
                        </div>
                        
                        <div className="calendar-grid">
                            {calendarDays.map((dateObj, idx) => {
                                if (!dateObj) return <div key={`pad-${idx}`} className="calendar-cell empty"></div>;
                                
                                const isActive = activeDate === dateObj.dateStr;
                                return (
                                    <div 
                                        key={dateObj.dateStr} 
                                        className={`calendar-cell ${dateObj.hasSlots ? 'has-slots' : ''} ${isActive ? 'active' : ''} ${dateObj.isToday ? 'today' : ''} ${dateObj.isOutsideWindow ? 'outside-window' : ''}`}
                                        onClick={() => dateObj.hasSlots && setActiveDate(dateObj.dateStr)}
                                    >
                                        <span className="day-number">{dateObj.day}</span>
                                        {dateObj.hasSlots && <div className="slot-indicator"></div>}
                                    </div>
                                );
                            })}
                        </div>
                        
                        <div className="calendar-footer">
                            <div className="legend-item">
                                <span className="dot dot-available"></span> Available
                            </div>
                        </div>
                    </div>

                    {/* Column 2: Time selection */}
                    <div className="times-panel animated fadeIn">
                        <div className="panel-header">
                            <h3>{activeDate ? formatDateFull(activeDate) : 'Select a date'}</h3>
                            <div className="duration-badge">50 Min Session</div>
                        </div>
                        
                        <div className="slots-scroller">
                            {activeSlots.length > 0 ? (
                                <div className="slots-list-modern">
                                    {activeSlots.map(slot => {
                                        const isMine = slot.is_mine;
                                        const isBooked = slot.status === 'booked';
                                        const isOther = (slot.status === 'reserved' && !slot.is_mine) || isBooked;
                                        const isSelected = selectedSlot && (String(selectedSlot) === String(slot.id));

                                        return (
                                            <button 
                                                key={slot.id}
                                                className={`time-slot-btn ${isSelected ? 'selected' : ''} ${isOther ? 'disabled' : ''} ${isMine ? 'mine' : ''} ${isBooked ? 'booked' : ''}`}
                                                onClick={() => (slot.status === 'available' || isMine) && !isBooked && !submitting && handleReserve(slot.id)}
                                                disabled={isOther || submitting}
                                            >
                                                <Clock size={16} />
                                                <span>{slot.start_time} - {slot.end_time}</span>
                                                {isSelected && <CheckCircle size={16} className="check" />}
                                                {isBooked && <span className="booked-label">Full</span>}
                                            </button>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="empty-slots">
                                    <CalendarIcon size={32} />
                                    <p>No available times on this date.</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Column 3: Booking Action Area */}
                    <div className="action-sidebar-triple">
                        <div className={`booking-action-card ${selectedSlot || error ? 'visible' : ''}`}>
                            {error && <div className="booking-error-message" style={{ color: '#ef4444', backgroundColor: '#fee2e2', padding: '12px', borderRadius: '12px', marginBottom: '16px', fontSize: '0.85rem', fontWeight: 'bold', border: '1px solid #fecaca' }}>{error}</div>}
                            
                            {selectedSlot ? (
                                <>
                                    <div className="action-header">
                                        <h3>Review Your Slot</h3>
                                        {submitting && <RefreshCw className="spin" size={16} />}
                                    </div>
                                    
                                    <div className="action-details" style={{ opacity: submitting ? 0.6 : 1 }}>
                                        <div className="a-row"><CalendarIcon size={16} /> {formatDateFull(slots.find(s=>String(s.id)===String(selectedSlot))?.date || activeDate)}</div>
                                        <div className="a-row">
                                            <Clock size={16} /> 
                                            {slots.find(s=>String(s.id)===String(selectedSlot))?.start_time || '---'} - {slots.find(s=>String(s.id)===String(selectedSlot))?.end_time || '---'}
                                        </div>
                                    </div>

                                    <button 
                                        className="confirm-btn-extreme"
                                        disabled={submitting}
                                        onClick={handleConfirm}
                                    >
                                        {submitting ? <RefreshCw className="spin" /> : 'Confirm Interview'}
                                    </button>
                                </>
                            ) : submitting ? (
                                <div className="no-selection-placeholder">
                                    <RefreshCw size={32} className="p-icon spin" />
                                    <p>Reserving your slot...</p>
                                </div>
                            ) : (
                                <div className="no-selection-placeholder">
                                    <Clock size={32} className="p-icon" />
                                    <p>Select a time slot from the middle panel to proceed with your booking.</p>
                                </div>
                            )}
                        </div>

                        {/* Additional info to fill space */}
                        <div className="support-info-card">
                            <Info size={16} />
                            <p>Need help? Contact support if you face any booking issues.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default BookInterview;
