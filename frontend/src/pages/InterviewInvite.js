import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import '../styles/InterviewInvite.css';

const DRAFT_KEY = 'interviewInviteDraft:schedule';
const DRAFT_PANEL_KEY = 'interviewInviteDraft:panelMap';

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((email || '').trim());
}

function isValidPAN(pan) {
  if (!pan) return true;
  return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test((pan || '').trim().toUpperCase());
}

function isValidPhone(phone) {
  if (!phone) return true;
  return /^[6-9][0-9]{9}$/.test((phone || '').trim());
}



function getInitials(name) {
  const parts = (name || '').trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (parts[0] || '?')[0].toUpperCase();
}

// Default interview duration: 1 hour
const INTERVIEW_DURATION_SEC = 3600;

export default function InterviewInvite() {
  const navigate = useNavigate();

  // Add-form fields
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [interviewerName, setInterviewerName] = useState('');
  const [interviewerEmail, setInterviewerEmail] = useState('');
  const [pan, setPan] = useState('');
  const [phone, setPhone] = useState('');

  // Schedule (exact_window only)
  const [scheduleDate, setScheduleDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');   // editable; auto-filled from startTime + 1hr
  const [scheduleError, setScheduleError] = useState('');

  const [candidates, setCandidates] = useState([]);
  const [sending, setSending] = useState(false);
  const [userProfile, setUserProfile] = useState(null);

  // Additional Panelists for the current form
  const [panelistName, setPanelistName] = useState('');
  const [panelistEmail, setPanelistEmail] = useState('');
  const [currentPanelMembers, setCurrentPanelMembers] = useState([]);
  
  // Mapping of draft candidate ID to their additional panel members
  const [draftPanelMap, setDraftPanelMap] = useState({});
  
  // To track successfully created sessions for post-send management
  const [sentSessions, setSentSessions] = useState([]);

  const userDomain = useMemo(() => {
    if (!userProfile?.email) return '';
    return userProfile.email.split('@')[1] || '';
  }, [userProfile]);

  const canAdd = useMemo(() => {
    if (!name.trim()) return false;
    if (!isValidEmail(email.trim())) return false;
    if (!interviewerName.trim()) return false;
    if (!isValidEmail(interviewerEmail.trim())) return false;
    if (!isValidPAN(pan.trim())) return false;
    if (phone && !isValidPhone(phone.trim())) return false;
    if (!scheduleDate || !startTime) return false;
    return true;
  }, [name, email, interviewerName, interviewerEmail, pan, phone, scheduleDate, startTime]);

  // Track whether the user has manually edited endTime
  const endTimeManualRef = useRef(false);

  // ── Auto-fill endTime when startTime changes ──
  // Only overrides if the user hasn't manually edited it yet
  useEffect(() => {
    if (!startTime || endTimeManualRef.current) return;
    const [h, m] = startTime.split(':').map(Number);
    if (isNaN(h) || isNaN(m)) return;
    const d = new Date(2000, 0, 1, h, m);
    d.setTime(d.getTime() + INTERVIEW_DURATION_SEC * 1000);
    setEndTime(`${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`);
  }, [startTime]);

  // ── Computed schedule display for table/stats bar ──
  const scheduleDisplay = (() => {
    if (!scheduleDate || !startTime) return null;
    const start = new Date(`${scheduleDate}T${startTime}:00`);
    if (Number.isNaN(start.getTime())) return null;
    // Use editable endTime if present, otherwise fall back to auto +1hr
    let endDisplay = endTime;
    if (!endDisplay) {
      const autoEnd = new Date(start.getTime() + INTERVIEW_DURATION_SEC * 1000);
      endDisplay = `${String(autoEnd.getHours()).padStart(2, '0')}:${String(autoEnd.getMinutes()).padStart(2, '0')}`;
    }
    const fmtDate = (d) => d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    const fmtTime12 = (hhmm) => {
      const [h, m] = hhmm.split(':').map(Number);
      const ampm = h >= 12 ? 'PM' : 'AM';
      return `${String(h % 12 || 12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${ampm}`;
    };
    return `${fmtDate(start)} · ${fmtTime12(startTime)} – ${fmtTime12(endDisplay)}`;
  })();

  // ── Start window label (30-min grace) ──
  const startWindowLabel = (() => {
    if (!scheduleDate || !startTime) return '';
    const start = new Date(`${scheduleDate}T${startTime}:00`);
    if (Number.isNaN(start.getTime())) return '';
    const fmtTime = (d) => {
      const h = d.getHours(), m = d.getMinutes(), ampm = h >= 12 ? 'PM' : 'AM';
      return `${String(h % 12 || 12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${ampm}`;
    };
    return `${fmtTime(start)} – ${fmtTime(new Date(start.getTime() + 30 * 60000))}`;
  })();

  // ── Persist schedule to localStorage ──
  useEffect(() => {
    try {
      localStorage.setItem(DRAFT_KEY, JSON.stringify({ scheduleDate, startTime, endTime, endTimeManual: endTimeManualRef.current, updated_at: Date.now() }));
    } catch { /* ignore */ }
  }, [scheduleDate, startTime, endTime]);

  useEffect(() => {
    try {
      localStorage.setItem(DRAFT_PANEL_KEY, JSON.stringify(draftPanelMap));
    } catch { /* ignore */ }
  }, [draftPanelMap]);

  // ── Restore schedule on mount ──
  useEffect(() => {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (raw) {
        const p = JSON.parse(raw);
        if (p?.scheduleDate) setScheduleDate(p.scheduleDate);
        if (p?.startTime) setStartTime(p.startTime);
        if (p?.endTime) {
          setEndTime(p.endTime);
          if (p?.endTimeManual) endTimeManualRef.current = true;
        }
      }
    } catch { /* ignore */ }

    try {
      const rawPanel = localStorage.getItem(DRAFT_PANEL_KEY);
      if (rawPanel) setDraftPanelMap(JSON.parse(rawPanel));
    } catch { /* ignore */ }

    // Fetch profile + existing draft candidates
    const init = async () => {
      try {
        const [profileRes, draftsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/profile/`),
          axios.get(`${API_BASE_URL}/interviews/draft-invites/`),
        ]);
        setUserProfile(profileRes.data);
        if (draftsRes.data?.results) setCandidates(draftsRes.data.results);
      } catch (err) {
        console.error('Failed to load profile or drafts', err);
      }
    };
    init();
  }, []);

  const handlePanChange = (e) => {
    let val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (val.length > 10) return;
    let out = '';
    for (let i = 0; i < val.length; i++) {
      const ch = val[i];
      if (i < 5 && /[A-Z]/.test(ch)) out += ch;
      else if (i >= 5 && i < 9 && /[0-9]/.test(ch)) out += ch;
      else if (i === 9 && /[A-Z]/.test(ch)) out += ch;
    }
    setPan(out);
  };

  const handlePhoneChange = (e) => {
    const val = e.target.value.replace(/\D/g, '');
    if (val.length <= 10) setPhone(val);
  };

  const addCandidate = async () => {
    const n = name.trim(), e = email.trim().toLowerCase();
    const intN = interviewerName.trim(), intE = interviewerEmail.trim().toLowerCase();
    const p = pan.trim().toUpperCase(), ph = phone.trim();
    if (!n || !isValidEmail(e) || !intN || !isValidEmail(intE) || !isValidPAN(p) || (ph && !isValidPhone(ph))) return;
    if (userDomain && !intE.endsWith(`@${userDomain}`)) {
      alert(`Interviewer email must belong to your company domain (@${userDomain}).`); return;
    }
    const dupe = candidates.some((c) => c.email.toLowerCase() === e || (p && c.pan_number && c.pan_number === p));
    if (dupe) { alert('This candidate email or PAN already exists in the list.'); return; }
    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/draft-invites/`, {
        name: n, email: e, interviewer_name: intN, interviewer_email: intE,
        pan_number: p || null, phone: ph || null,
      });
      
      if (resp.data?.results) {
        const newCandidates = resp.data.results;
        setCandidates((prev) => [...prev, ...newCandidates]);
        
        // Save panel members for these new candidates
        if (currentPanelMembers.length > 0) {
          const newMap = { ...draftPanelMap };
          newCandidates.forEach(cand => {
            newMap[cand.id] = [...currentPanelMembers];
          });
          setDraftPanelMap(newMap);
        }
      }
      
      setName(''); setEmail(''); setInterviewerName(''); setInterviewerEmail(''); setPan(''); setPhone('');
      setCurrentPanelMembers([]);
    } catch (err) {
      alert(err?.response?.data?.error || 'Failed to save draft candidate.');
    }
  };

  const removeCandidate = async (idx) => {
    const c = candidates[idx];
    const label = `${c?.name || 'Candidate'}${c?.email ? ` (${c.email})` : ''}`;
    if (!window.confirm(`Remove ${label}?`)) return;
    try {
      await axios.delete(`${API_BASE_URL}/interviews/draft-invites/${c.id}/`);
      setCandidates((prev) => prev.filter((_, i) => i !== idx));
    } catch { alert('Failed to remove draft candidate.'); }
  };







  const shareInvites = async () => {
    if (candidates.length === 0) { alert('Please add at least one candidate.'); return; }
    if (!scheduleDate || !startTime) { setScheduleError('Please select date and start time.'); alert('Please select date and start time.'); return; }
    const startIso = (() => { const d = new Date(`${scheduleDate}T${startTime}:00`); return Number.isNaN(d.getTime()) ? null : d.toISOString(); })();
    if (!startIso) { setScheduleError('Invalid start time.'); return; }
    if (new Date(startIso).getTime() < Date.now()) { setScheduleError('Start time cannot be in the past.'); alert('Start time cannot be in the past.'); return; }
    const tz = (() => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || null; } catch { return null; } })();
    // Use manually-edited endTime if available, otherwise auto-compute start + 1hr
    const resolvedEndTime = endTime || (() => {
      const d = new Date(new Date(startIso).getTime() + INTERVIEW_DURATION_SEC * 1000);
      return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    })();
    const endIso = (() => {
      const d = new Date(`${scheduleDate}T${resolvedEndTime}:00`);
      return Number.isNaN(d.getTime()) ? new Date(new Date(startIso).getTime() + INTERVIEW_DURATION_SEC * 1000).toISOString() : d.toISOString();
    })();
    setScheduleError('');
    setSending(true);
    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/invite/`, {
        draft_ids: candidates.map(c => c.id),
        interview_name: 'Interview Invitation',
        start_time: startIso,
        end_time: endIso,
        time_zone: tz,
        validity_mode: 'exact_window',
        start_grace_minutes: 30,
      });
      const { sent, failed, results } = resp.data || {};
      
      // Handle additional panelists for each created session
      if (results && results.length > 0) {
        for (const res of results) {
          // Find original draft ID (this might be tricky if not returned, 
          // but usually results match draft_ids order or have draft_id field)
          // We'll try to find by email if draft_id is missing
          const panelists = draftPanelMap[res.id] || []; // assuming res.id is what we need or mapped
          
          if (panelists.length > 0) {
            console.log(`Adding ${panelists.length} panelists to session ${res.token}`);
            for (const panelist of panelists) {
              try {
                await axios.post(`${API_BASE_URL}/interviews/add-participant/`, {
                  session_id: res.token,
                  email: panelist.email,
                  name: panelist.name,
                  role: 'interviewer'
                });
              } catch (pErr) {
                console.error(`Failed to invite panelist ${panelist.email}:`, pErr);
              }
            }
          }
        }
      }

      if (failed > 0) {
        const failedEmails = (results || []).filter(r => r.status === 'failed').map(r => r.email).join(', ');
        alert(`Sent ${sent} invite(s). Failed: ${failed} — ${failedEmails}`);
      } else {
        alert(`Successfully sent interview invites to ${sent} candidate(s).`);
      }
      try { localStorage.removeItem(DRAFT_KEY); } catch { /* ignore */ }
      setCandidates([]); setName(''); setEmail(''); setPan(''); setPhone('');
      setInterviewerName(''); setInterviewerEmail('');
      setScheduleDate(''); setStartTime(''); setEndTime(''); endTimeManualRef.current = false;
      setDraftPanelMap({});
      setSentSessions(results || []);
    } catch (e) {
      alert(e?.response?.data?.error || e?.message || 'Failed to send interview invites');
    } finally { setSending(false); }
  };

  const isShareDisabled = sending || candidates.length === 0;

  // ── Progress steps ──
  const scheduleReady = !!(scheduleDate && startTime);
  const candidatesReady = candidates.length > 0;

  return (
    <div className="ii-page">
      <Header />

      <div className="ii-shell">

        {/* ── Page Header ── */}
        <div className="ii-top">
          <div className="ii-top-left">
            <div className="ii-icon-wrap">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.85" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
              </svg>
            </div>
            <div>
              <div className="ii-title">Invite for Live Interview</div>
              <div className="ii-meta">
                <span className="ii-meta-chip">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
                  Default duration: 1 hour
                </span>
                <span className="ii-meta-sep">·</span>
                <span className="ii-meta-chip">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.8a19.79 19.79 0 01-3.07-8.68A2 2 0 012 1h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.09 8.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" /></svg>
                  Live Interview
                </span>
              </div>
            </div>
          </div>
          <div className="ii-actions">
            <button className="ii-btn-back" type="button" onClick={() => navigate('/dashboard')}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6" /></svg>
              Back
            </button>
          </div>
        </div>

        {/* ── Progress Stepper ── */}
        <div className="ii-stepper">
          {[
            {
              label: 'Set Schedule', desc: 'Choose date & time', done: scheduleReady,
              active: !scheduleReady,
              icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></svg>
            },
            {
              label: 'Add Candidates', desc: `${candidates.length} added`, done: candidatesReady,
              active: scheduleReady && !candidatesReady,
              icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" /><line x1="19" y1="8" x2="19" y2="14" /><line x1="22" y1="11" x2="16" y2="11" /></svg>
            },
            {
              label: 'Send Invites', desc: 'Email all candidates', done: false,
              active: scheduleReady && candidatesReady,
              icon: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>
            },
          ].map((step, i, arr) => (
            <React.Fragment key={step.label}>
              <div className={`ii-step${step.done ? ' done' : step.active ? ' active' : ''}`}>
                <div className="ii-step-circle">
                  {step.done
                    ? <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                    : step.icon}
                </div>
                <div className="ii-step-text">
                  <span className="ii-step-label">{step.label}</span>
                  <span className="ii-step-desc">{step.desc}</span>
                </div>
              </div>
              {i < arr.length - 1 && <div className={`ii-step-connector${step.done ? ' done' : ''}`} />}
            </React.Fragment>
          ))}
        </div>

        {/* ── Schedule Card ── */}
        <div className="ii-card">
          <div className="ii-card-header">
            <div className="ii-card-icon blue">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" />
                <line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
              </svg>
            </div>
            <span className="ii-card-title">Schedule / Link Validity</span>
            <span className="ii-card-subtitle">Particular date + time window only</span>
          </div>

          <div className="ii-grid ii-grid-4">
            <div className="ii-field">
              <label className="ii-label">Start Date <span className="ii-required">*</span></label>
              <input
                type="date"
                className="ii-input"
                value={scheduleDate}
                min={new Date().toISOString().split('T')[0]}
                onChange={(e) => { setScheduleDate(e.target.value); setScheduleError(''); }}
              />
            </div>
            <div className="ii-field">
              <label className="ii-label">Start Time <span className="ii-required">*</span></label>
              <input
                type="time"
                className="ii-input"
                value={startTime}
                onChange={(e) => { setStartTime(e.target.value); setScheduleError(''); }}
              />
            </div>
            <div className="ii-field">
              <label className="ii-label">End Time <span className="ii-hint-inline">(auto · editable)</span></label>
              <input
                type="time"
                className="ii-input"
                value={endTime}
                onChange={(e) => {
                  endTimeManualRef.current = true;
                  setEndTime(e.target.value);
                  setScheduleError('');
                }}
                placeholder="Auto-computed"
              />
              <span className="ii-hint">Auto-filled as Start + 1 hr · change if needed</span>
            </div>
            <div className="ii-field">
              <label className="ii-label">Start Window (auto)</label>
              <input
                type="text"
                className="ii-input"
                value={startWindowLabel}
                readOnly
                placeholder="Auto-computed"
              />
              <span className="ii-hint">30-minute entry window</span>
            </div>
          </div>

          {scheduleError && <p className="ii-error" style={{ marginTop: '0.75rem' }}>{scheduleError}</p>}

          <div className="ii-schedule-note">
            <span className="ii-note-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </span>
            If a candidate starts within the allowed start window, they can refresh or reconnect and continue until the interview end time.
          </div>
        </div>

        {/* ── Add Candidate Card ── */}
        <div className="ii-card">
          <div className="ii-card-header">
            <div className="ii-card-icon teal">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
                <line x1="19" y1="8" x2="19" y2="14" /><line x1="22" y1="11" x2="16" y2="11" />
              </svg>
            </div>
            <span className="ii-card-title">Add Candidates</span>
            <span className="ii-card-subtitle">Fill manually</span>
          </div>

          {/* Two-row form: Candidate fields + Interviewer fields */}
          <div className="ii-form-section-label">Candidate Details</div>
          <div className="ii-add-row">
            <div className="ii-field">
              <label className="ii-label">Name <span className="ii-required">*</span></label>
              <div className="ii-input-wrap">
                <input
                  className={`ii-input${name.trim() ? ' ii-valid' : ''}`}
                  value={name}
                  onChange={(e) => { if (/^[a-zA-Z\s]*$/.test(e.target.value)) setName(e.target.value); }}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  autoComplete="off"
                  placeholder="Candidate full name"
                  maxLength={100}
                />
                {name.trim() && <span className="ii-tick">✓</span>}
              </div>
            </div>
            <div className="ii-field">
              <label className="ii-label">Email <span className="ii-required">*</span></label>
              <div className="ii-input-wrap">
                <input
                  className={`ii-input${email ? (isValidEmail(email) ? ' ii-valid' : ' ii-invalid') : ''}`}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="candidate@email.com"
                  maxLength={100}
                />
                {email && <span className={isValidEmail(email) ? 'ii-tick' : 'ii-cross'}>{isValidEmail(email) ? '✓' : '✕'}</span>}
              </div>
            </div>
            <div className="ii-field">
              <label className="ii-label">PAN <span className="ii-label-opt">(optional)</span></label>
              <div className="ii-input-wrap">
                <input
                  className={`ii-input${pan ? (isValidPAN(pan) ? (pan.length === 10 ? ' ii-valid' : '') : ' ii-invalid') : ''}`}
                  value={pan}
                  onChange={handlePanChange}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="ABCDE1234F"
                  maxLength={10}
                />
                {pan.length === 10 && isValidPAN(pan) && <span className="ii-tick">✓</span>}
                {pan && !isValidPAN(pan) && <span className="ii-cross">✕</span>}
              </div>
            </div>
            <div className="ii-field" style={{ position: 'relative' }}>
              <label className="ii-label">Phone <span className="ii-label-opt">(optional)</span></label>
              <div className="ii-input-wrap">
                <input
                  className={`ii-input${phone ? (isValidPhone(phone) ? ' ii-valid' : ' ii-invalid') : ''}`}
                  value={phone}
                  onChange={handlePhoneChange}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="10-digit number"
                />
                {phone && isValidPhone(phone) && <span className="ii-tick">✓</span>}
                {phone && !isValidPhone(phone) && <span className="ii-cross">✕</span>}
              </div>
              {phone && !/^[6-9]/.test(phone) && (
                <div style={{ position: 'absolute', top: '100%', left: 0, color: '#ef4444', fontSize: '12px', marginTop: '2px', whiteSpace: 'nowrap' }}>Enter valid phone number (must start with 6, 7, 8 or 9)</div>
              )}
            </div>
          </div>

          <div className="ii-form-section-label" style={{ marginTop: '1rem' }}>Interviewer Details</div>
          <div className="ii-add-row">
            <div className="ii-field">
              <label className="ii-label">Interviewer Name <span className="ii-required">*</span></label>
              <div className="ii-input-wrap">
                <input
                  className={`ii-input${interviewerName.trim() ? ' ii-valid' : ''}`}
                  value={interviewerName}
                  onChange={(e) => setInterviewerName(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  autoComplete="off"
                  placeholder="Interviewer full name"
                  maxLength={100}
                />
                {interviewerName.trim() && <span className="ii-tick">✓</span>}
              </div>
            </div>
            <div className="ii-field" style={{ flex: '1.5' }}>
              <label className="ii-label">
                Interviewer Email <span className="ii-required">*</span>
                {userDomain && <span className="ii-label-opt"> (@{userDomain})</span>}
              </label>
              <div className="ii-input-wrap">
                <input
                  className={`ii-input${interviewerEmail ? (isValidEmail(interviewerEmail) ? ' ii-valid' : ' ii-invalid') : ''}`}
                  value={interviewerEmail}
                  onChange={(e) => setInterviewerEmail(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder={`e.g. interviewer@${userDomain || 'company.com'}`}
                  maxLength={100}
                />
                {interviewerEmail && <span className={isValidEmail(interviewerEmail) ? 'ii-tick' : 'ii-cross'}>{isValidEmail(interviewerEmail) ? '✓' : '✕'}</span>}
              </div>
            </div>
          </div>

          <div className="ii-form-section-label" style={{ marginTop: '1rem' }}>Additional Panelists (Optional)</div>
          <div className="ii-add-row" style={{ alignItems: 'flex-end' }}>
            <div className="ii-field">
              <label className="ii-label">Panelist Name</label>
              <input
                className="ii-input"
                value={panelistName}
                onChange={(e) => setPanelistName(e.target.value)}
                placeholder="Enter name"
              />
            </div>
            <div className="ii-field" style={{ flex: '1.5' }}>
              <label className="ii-label">Panelist Email</label>
              <input
                className="ii-input"
                value={panelistEmail}
                onChange={(e) => setPanelistEmail(e.target.value)}
                placeholder="Enter email"
              />
            </div>
            <div className="ii-add-actions">
              <button 
                className="ii-btn-tertiary" 
                type="button" 
                onClick={() => {
                  if (!panelistEmail || !isValidEmail(panelistEmail)) {
                    alert('Valid email is required to add a panelist.');
                    return;
                  }
                  if (currentPanelMembers.length >= 2) {
                    alert('Maximum of 4 members allowed in an interview (1 candidate + 3 interviewers). You can only add up to 2 additional panelists here.');
                    return;
                  }
                  if (currentPanelMembers.some(p => p.email.toLowerCase() === panelistEmail.toLowerCase())) {
                    alert('This panelist has already been added to the list.');
                    return;
                  }
                  if (panelistEmail.toLowerCase() === interviewerEmail.toLowerCase()) {
                    alert('This email is already assigned as the primary interviewer.');
                    return;
                  }
                  setCurrentPanelMembers(prev => [...prev, { name: panelistName, email: panelistEmail }]);
                  setPanelistName('');
                  setPanelistEmail('');
                }}
              >
                Add Panelist
              </button>
            </div>
          </div>

          {currentPanelMembers.length > 0 && (
            <div className="ii-panel-list">
              {currentPanelMembers.map((m, idx) => (
                <div key={idx} className="ii-panel-chip">
                  <span>{m.name || m.email} ({m.email})</span>
                  <button onClick={() => setCurrentPanelMembers(prev => prev.filter((_, i) => i !== idx))}>×</button>
                </div>
              ))}
            </div>
          )}

          <div className="ii-form-footer" style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button className="ii-btn-tertiary" type="button" onClick={addCandidate} disabled={!canAdd}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              Add Candidate to List
            </button>
            <button type="button" onClick={shareInvites} disabled={isShareDisabled} className="ii-btn-share">
              {sending ? (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'ii-spin 1s linear infinite' }}>
                    <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
                  </svg>
                  Sending…
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                  Send All Invites
                </>
              )}
            </button>
          </div>
        </div>

        {/* ── Candidates Table Card ── */}
        <div className="ii-card">
          <div className="ii-card-header">
            <div className="ii-card-icon violet">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
              </svg>
            </div>
            <span className="ii-card-title">Candidates</span>
            {candidates.length > 0 && (
              <span className="ii-card-subtitle">{candidates.length} {candidates.length === 1 ? 'candidate' : 'candidates'} added</span>
            )}
          </div>

          {/* Stats bar */}
          {candidates.length > 0 && (
            <div className="ii-stats-bar">
              <div className="ii-stat">
                <span className="ii-stat-val">{candidates.length}</span>
                <span className="ii-stat-label">Total</span>
              </div>
              <div className="ii-stat">
                <span className="ii-stat-val">{candidates.filter(c => c.pan_number).length}</span>
                <span className="ii-stat-label">With PAN</span>
              </div>
              <div className="ii-stat">
                <span className="ii-stat-val">{candidates.filter(c => c.phone).length}</span>
                <span className="ii-stat-label">With Phone</span>
              </div>
              {scheduleDisplay && (
                <div className="ii-stat ii-stat-schedule">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                  <span className="ii-stat-schedule-val">{scheduleDisplay}</span>
                </div>
              )}
              <div className="ii-stat-actions">
                <button
                  type="button"
                  className="ii-btn-clear"
                  onClick={async () => {
                    if (!window.confirm(`Remove all ${candidates.length} candidates?`)) return;
                    try {
                      await Promise.all(candidates.map(c => axios.delete(`${API_BASE_URL}/interviews/draft-invites/${c.id}/`)));
                      setCandidates([]);
                    } catch { alert('Failed to clear some candidates.'); }
                  }}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14H6L5 6" />
                    <path d="M10 11v6" /><path d="M14 11v6" /><path d="M9 6V4h6v2" />
                  </svg>
                  Clear All
                </button>
              </div>
            </div>
          )}

          {candidates.length === 0 ? (
            <div className="ii-empty">
              <div className="ii-empty-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
                </svg>
              </div>
              <div className="ii-empty-title">No candidates added yet</div>
              <div className="ii-empty-text">Fill in the form above to add candidates to this interview batch.</div>
            </div>
          ) : (
            <div className="ii-table-wrap">
              <table className="ii-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Candidate</th>
                    <th>Candidate Email</th>
                    <th>Interviewer</th>
                    <th>Interviewer Email</th>
                    <th>Panel</th>
                    <th>Scheduled</th>
                    <th>PAN</th>
                    <th>Phone</th>
                    <th style={{ textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map((c, idx) => (
                    <tr key={`${c.email}-${idx}`}>
                      <td className="ii-td-num">{idx + 1}</td>
                      <td>
                        <div className="ii-cand-cell">
                          <div className="ii-avatar ii-avatar-blue">{getInitials(c.name)}</div>
                          <span className="ii-cand-name">{c.name}</span>
                        </div>
                      </td>
                      <td><span className="ii-mono">{c.email}</span></td>
                      <td>
                        <div className="ii-cand-cell">
                          <div className="ii-avatar ii-avatar-violet">{getInitials(c.interviewer_name || c.interviewer_email)}</div>
                          <span className="ii-cand-name">{c.interviewer_name || '—'}</span>
                        </div>
                      </td>
                      <td><span className="ii-mono">{c.interviewer_email}</span></td>
                      <td>
                        {draftPanelMap[c.id] && draftPanelMap[c.id].length > 0 ? (
                          <span className="ii-badge-schedule" style={{ background: '#f5f3ff', borderColor: '#c4b5fd', color: '#5b21b6' }}>
                            +{draftPanelMap[c.id].length} Panelists
                          </span>
                        ) : (
                          <span className="ii-badge-dash">—</span>
                        )}
                      </td>
                      <td>
                        {scheduleDisplay
                          ? <span className="ii-badge-schedule">{scheduleDisplay}</span>
                          : <span className="ii-badge-warn">Not set</span>}
                      </td>
                      <td>
                        {c.pan_number
                          ? <span className="ii-badge-pan">{c.pan_number}</span>
                          : <span className="ii-badge-dash">—</span>}
                      </td>
                      <td>
                        {c.phone
                          ? <span className="ii-mono">{c.phone}</span>
                          : <span className="ii-badge-dash">—</span>}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button className="ii-btn-danger" type="button" onClick={() => removeCandidate(idx)}>Remove</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>

      <style>{`@keyframes ii-spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
