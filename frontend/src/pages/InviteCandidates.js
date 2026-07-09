import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/InviteCandidates.css';
import { API_BASE_URL } from '../apiConfig';

const INVITE_DRAFT_KEY_PREFIX = 'inviteCandidatesDraft:';

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

function normalizeHeader(h) {
  return (h || '').toString().trim().toLowerCase().replace(/\s+/g, '_');
}

function parseCSV(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let inQuotes = false;

  const pushCell = () => { row.push(cell); cell = ''; };
  const pushRow = () => {
    const isEmpty = row.every((c) => !String(c || '').trim());
    if (!isEmpty) rows.push(row);
    row = [];
  };

  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (inQuotes) {
      if (ch === '"') {
        const next = text[i + 1];
        if (next === '"') { cell += '"'; i += 1; } else { inQuotes = false; }
      } else { cell += ch; }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      pushCell();
    } else if (ch === '\n') {
      pushCell(); pushRow();
    } else if (ch === '\r') { // ignore
    } else { cell += ch; }
  }
  pushCell();
  pushRow();
  return rows;
}

function downloadTextFile(filename, text) {
  const blob = new Blob([text], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function getInitials(name) {
  const parts = (name || '').trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (parts[0] || '?')[0].toUpperCase();
}

export default function InviteCandidates() {
  const navigate = useNavigate();
  const { assessmentId } = useParams();

  const [loading, setLoading] = useState(true);
  const [assessment, setAssessment] = useState(null);
  const [error, setError] = useState('');

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [pan, setPan] = useState('');
  const [phone, setPhone] = useState('');

  const [candidates, setCandidates] = useState([]);
  const [sending, setSending] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [importMsg, setImportMsg] = useState('');
  const [teamMembers, setTeamMembers] = useState([]);
  const [selectedInterviewerIds, setSelectedInterviewerIds] = useState([]);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showCreditConfirm, setShowCreditConfirm] = useState(false);
  const [availableCredits, setAvailableCredits] = useState(0);
  const [isAutoSchedule, setIsAutoSchedule] = useState(false);
  const fileRef = useRef(null);

  const [validityMode, setValidityMode] = useState('exact_window');
  const [scheduleDate, setScheduleDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [scheduleError, setScheduleError] = useState('');

  const draftKey = `${INVITE_DRAFT_KEY_PREFIX}${assessmentId || 'unknown'}`;

  const canAdd = useMemo(() => {
    const n = name.trim();
    const e = email.trim();
    const p = pan.trim();
    if (!n) return false;
    if (!isValidEmail(e)) return false;
    if (!isValidPAN(p)) return false;

    if (validityMode === 'exact_window' && (!scheduleDate || !startTime)) return false;
    if ((validityMode === 'date_anytime' || validityMode === 'one_week') && !scheduleDate) return false;
    if (phone && !isValidPhone(phone)) return false;

    return true;
  }, [name, email, pan, validityMode, scheduleDate, startTime]);

  const isSingleLimitReached = useMemo(() => {
    return assessment?.assessment_mode === 'single' && (candidates.length >= 1 || assessment.invited > 0);
  }, [assessment, candidates.length]);

  const loadAssessment = async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await axios.get(`${API_BASE_URL}/assessments/${assessmentId}/`);
      setAssessment(resp.data);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeamMembers = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/users/team-members/`);
      if (res.data.members) {
        const interviewers = res.data.members
          .filter(m => m.role === 'interviewer')
          .sort((a, b) => (a.first_name || a.email || '').localeCompare(b.first_name || b.email || ''));
        setTeamMembers(interviewers);
      }
    } catch (err) {
      console.error('Error in fetchTeamMembers metadata:', err);
    }
  };

  const toggleInterviewer = (id) => {
    setSelectedInterviewerIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleGenerateSlots = async () => {
    if (selectedInterviewerIds.length === 0) {
      alert('Please select at least one interviewer.');
      return;
    }
    setGenerating(true);
    try {
      await axios.post(`${API_BASE_URL}/interviews/slots/generate/`, {
        assessment_id: assessmentId,
        interviewer_ids: selectedInterviewerIds,
      });
      alert('Interview slots generated successfully for the next 7 days.');
      setShowBookingModal(false);
    } catch (err) {
      console.error('Error generating slots:', err);
      alert(err.response?.data?.error || 'Failed to generate interview slots.');
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    if (!assessmentId) return;
    loadAssessment();
    fetchTeamMembers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId]);

  useEffect(() => {
    const fetchCredits = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get(`${API_BASE_URL}/students/wallet/`, { headers: { Authorization: `Bearer ${token}` } });
        setAvailableCredits(res.data.ai_credits || 0);
      } catch (e) {}
    };
    fetchCredits();
  }, []);

  // Calculate credit cost for assessment invites
  const numMcqs = assessment?.total_questions || 0;
  const numCoding = assessment?.coding_question_count || 0;
  const creditPerCandidate = Math.max(1, Math.round((numMcqs * 0.5) + (numCoding * 6)));
  const totalCreditCost = creditPerCandidate * candidates.length;

  useEffect(() => {
    if (!assessmentId) return;
    try {
      const raw = localStorage.getItem(draftKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        // Candidate list
        if (parsed && Array.isArray(parsed.candidates)) setCandidates(parsed.candidates);
        // Add-form fields (Name is excluded from restoration to ensure it remains empty by default)
        if (parsed && typeof parsed.email === 'string') setEmail(parsed.email);
        if (parsed && typeof parsed.pan === 'string') setPan(parsed.pan);
        if (parsed && typeof parsed.phone === 'string') setPhone(parsed.phone);
        // Schedule fields
        if (parsed?.validityMode) setValidityMode(parsed.validityMode);
        if (parsed?.scheduleDate) setScheduleDate(parsed.scheduleDate);
        if (parsed?.endDate) setEndDate(parsed.endDate);
        if (parsed?.startTime) setStartTime(parsed.startTime);
        if (typeof parsed?.isAutoSchedule === 'boolean') setIsAutoSchedule(parsed.isAutoSchedule);
      }
    } catch {
      // ignore
    } finally {
      setHydrated(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId]);


  useEffect(() => {
    if (!assessmentId || !hydrated) return;
    try {
      localStorage.setItem(draftKey, JSON.stringify({
        // Add-form fields
        candidates, name, email, pan, phone,
        // Schedule fields
        validityMode, scheduleDate, endDate, startTime, isAutoSchedule,
        updated_at: Date.now(),
      }));
    } catch {
      // ignore
    }
  }, [assessmentId, draftKey, hydrated, candidates, name, email, pan, phone,
    validityMode, scheduleDate, endDate, startTime, isAutoSchedule]);

  const handlePanChange = (e) => {
    const val = e.target.value.toUpperCase();
    if (val.length <= 5) { if (/^[A-Z]*$/.test(val)) setPan(val); return; }
    if (val.length <= 9) { if (/^[A-Z]{5}[0-9]*$/.test(val)) setPan(val); return; }
    if (val.length === 10) { if (/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(val)) setPan(val); return; }
  };

  const handlePhoneChange = (e) => {
    const val = e.target.value.replace(/\D/g, '');
    if (val.length <= 10) setPhone(val);
  };

  const addCandidate = () => {
    if (assessment?.assessment_mode === 'single') {
      if (candidates.length >= 1) {
        alert('Single Mode assessment: Only one candidate can be invited.');
        return;
      }
      if (assessment.invited > 0) {
        alert('Invitation already sent for this Single Mode assessment.');
        return;
      }
    }
    const n = name.trim();
    const e = email.trim().toLowerCase();
    const p = pan.trim().toUpperCase();
    const ph = phone.trim();
    if (!n || !isValidEmail(e) || !isValidPAN(p) || (ph && !isValidPhone(ph))) return;
    const dupe = candidates.some((c) => c.email.toLowerCase() === e || (p && c.pan_number && c.pan_number === p));
    if (dupe) { alert('This candidate email or PAN already exists in the list.'); return; }
    setCandidates((prev) => [...prev, { name: n, email: e, pan_number: p || null, phone: ph || null }]);
    setName(''); setEmail(''); setPan(''); setPhone('');
  };

  const removeCandidate = (idx) => {
    const c = candidates[idx];
    const label = `${c?.name || 'Candidate'}${c?.email ? ` (${c.email})` : ''}`;
    // eslint-disable-next-line no-alert
    if (!window.confirm(`Remove ${label}?`)) return;
    setCandidates((prev) => prev.filter((_, i) => i !== idx));
  };

  const downloadTemplate = () => {
    const sample = [
      ['name', 'email', 'pan_number', 'phone'].join(','),
      ['John Doe', 'john@example.com', 'ABCDE1234F', '9999999999'].join(','),
    ].join('\n');
    downloadTextFile('invite_candidates_template.csv', sample);
  };

  const importFromCSVText = (csvText) => {
    setImportMsg('');
    const rows = parseCSV(csvText || '');
    if (!rows.length) { setImportMsg('CSV is empty.'); return; }
    const first = rows[0].map((c) => normalizeHeader(c));
    const hasHeader = first.includes('email') || first.includes('name');
    let header = null;
    let dataRows = rows;
    if (hasHeader) { header = first; dataRows = rows.slice(1); }

    const mapRow = (cells) => {
      const get = (key, idxFallback) => {
        if (header) { const idx = header.indexOf(key); if (idx >= 0) return (cells[idx] ?? '').toString().trim(); return ''; }
        return (cells[idxFallback] ?? '').toString().trim();
      };
      const n = get('name', 0);
      const e = get('email', 1).toLowerCase();
      const pRaw = get('pan_number', 2) || get('pan', 2);
      const phRaw = get('phone', 3) || get('phone_number', 3) || get('mobile', 3);
      return { name: n, email: e, pan_number: (pRaw || '').trim().toUpperCase() || null, phone: (phRaw || '').trim() || null };
    };

    const existingEmails = new Set(candidates.map((c) => (c.email || '').toLowerCase()));
    const existingPANs = new Set(candidates.map((c) => (c.pan_number || '').toUpperCase()).filter(Boolean));
    let added = 0, dupes = 0, invalid = 0;
    const next = [...candidates];

    dataRows.forEach((cells) => {
      if (assessment?.assessment_mode === 'single') {
        if (next.length >= 1 || assessment.invited > 0) return;
      }
      const r = mapRow(cells);
      const n = (r.name || '').trim();
      const e = (r.email || '').trim();
      const p = (r.pan_number || '').trim().toUpperCase();
      const ph = (r.phone || '').trim();
      if (!n || !isValidEmail(e) || !isValidPAN(p) || (ph && !isValidPhone(ph))) { invalid += 1; return; }
      if (existingEmails.has(e.toLowerCase()) || (p && existingPANs.has(p))) { dupes += 1; return; }
      existingEmails.add(e.toLowerCase());
      if (p) existingPANs.add(p);
      next.push({ name: n, email: e.toLowerCase(), pan_number: p || null, phone: r.phone ? String(r.phone).trim() : null });
      added += 1;
    });

    setCandidates(next);
    setImportMsg(`Imported ${added}${dupes ? ` · ${dupes} duplicate${dupes > 1 ? 's' : ''} skipped` : ''}${invalid ? ` · ${invalid} invalid` : ''}`);
  };

  const handleCSVUpload = async (file) => {
    if (!file) return;
    setImportMsg('');
    try {
      const text = await file.text();
      importFromCSVText(text);
    } catch {
      setImportMsg('Could not read the CSV file.');
    } finally {
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const shareInvites = async () => {
    if (candidates.length === 0) { alert('Please add at least one candidate.'); return; }
    if (availableCredits < totalCreditCost) {
      alert(`Insufficient credits. You need ${totalCreditCost} credits (${candidates.length} candidates × ${creditPerCandidate}) but have ${availableCredits}. Please add credits from your wallet.`);
      return;
    }
    setShowCreditConfirm(true);
  };

  const proceedWithInvites = async () => {
    setShowCreditConfirm(false);

    const tz = (() => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || null; } catch { return null; } })();
    const toISOFromLocal = (dateStr, timeStr) => {
      const d = new Date(`${dateStr}T${timeStr}:00`);
      if (Number.isNaN(d.getTime())) return null;
      return d.toISOString();
    };
    const parseHHMMSSSeconds = (value) => {
      try {
        const parts = String(value || '').split(':').map((x) => Number(x));
        if (parts.length === 2) return Math.max(0, (parts[0] || 0) * 60 + (parts[1] || 0));
        if (parts.length === 3) return Math.max(0, (parts[0] || 0) * 3600 + (parts[1] || 0) * 60 + (parts[2] || 0));
        return 0;
      } catch { return 0; }
    };

    const buildSchedule = () => {
      setScheduleError('');
      if (validityMode === 'date_anytime') {
        if (!scheduleDate) return { ok: false, error: 'Please select a start date.' };
        const startIso = toISOFromLocal(scheduleDate, '00:00');
        const endD = endDate || scheduleDate;
        const endLocal = new Date(`${endD}T23:59:59`);
        if (!startIso || Number.isNaN(endLocal.getTime())) return { ok: false, error: 'Invalid date.' };
        if (endLocal.getTime() < new Date(startIso).getTime()) return { ok: false, error: 'End date must be same or after start date.' };
        return { ok: true, start_time: startIso, end_time: endLocal.toISOString() };
      }
      if (validityMode === 'one_week') {
        if (!scheduleDate) return { ok: false, error: 'Please select a start date.' };
        const startIso = toISOFromLocal(scheduleDate, '00:00');
        if (!startIso) return { ok: false, error: 'Invalid start date.' };
        const start = new Date(startIso);
        const end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
        const endYMD = `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
        return { ok: true, start_time: start.toISOString(), end_time: new Date(`${endYMD}T23:59:59`).toISOString() };
      }
      if (!scheduleDate || !startTime) return { ok: false, error: 'Please select date and start time.' };
      const startIso = toISOFromLocal(scheduleDate, startTime);
      if (!startIso) return { ok: false, error: 'Invalid start time.' };
      if (new Date(startIso).getTime() < Date.now()) return { ok: false, error: 'Start time cannot be in the past.' };
      const durationSeconds = parseHHMMSSSeconds(assessment?.total_time);
      if (!durationSeconds) return { ok: false, error: 'Assessment total time is missing. Please set exam duration first.' };
      const end = new Date(new Date(startIso).getTime() + durationSeconds * 1000);
      return { ok: true, start_time: startIso, end_time: end.toISOString(), start_grace_minutes: 30 };
    };

    const sched = buildSchedule();
    if (!sched.ok) { setScheduleError(sched.error); alert(sched.error); return; }

    const payloadCandidates = candidates.map((c) => ({
      ...c,
      start_time: sched.start_time,
      end_time: sched.end_time,
      time_zone: tz,
      validity_mode: validityMode,
      start_grace_minutes: validityMode === 'exact_window' ? (sched.start_grace_minutes || 0) : 0,
      is_auto_schedule: isAutoSchedule,
    }));

    setSending(true);
    try {
      const resp = await axios.post(`${API_BASE_URL}/assessments/${assessmentId}/invite/`, { candidates: payloadCandidates });
      const sent = resp.data?.sent ?? 0;
      const failed = resp.data?.failed ?? 0;
      alert(`Invites processed. Sent: ${sent}, Failed: ${failed}`);
      try { localStorage.removeItem(draftKey); } catch { /* ignore */ }
      // Reset all form state
      setCandidates([]); setName(''); setEmail(''); setPan(''); setPhone(''); setImportMsg('');
      setValidityMode('exact_window'); setScheduleDate(''); setEndDate(''); setStartTime('');
      setIsAutoSchedule(false); setSelectedInterviewerIds([]);
    } catch (e) {
      alert(e?.response?.data?.error || e?.message || 'Failed to send invites');
    } finally {
      setSending(false);
    }
  };

  // ── Computed auto-end date for one_week mode ──
  const oneWeekEndDate = (() => {
    if (validityMode !== 'one_week' || !scheduleDate) return '';
    const start = new Date(`${scheduleDate}T00:00:00`);
    if (Number.isNaN(start.getTime())) return '';
    const end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
    return `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
  })();

  // ── Computed schedule display label (for table + stats bar) ──
  const scheduleDisplay = (() => {
    if (!scheduleDate) return null;

    const fmtDate = (ymd) => {
      const d = new Date(`${ymd}T00:00:00`);
      if (Number.isNaN(d.getTime())) return ymd;
      return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    };

    const fmtTime = (d) => {
      const h = d.getHours(), m = d.getMinutes();
      const ampm = h >= 12 ? 'PM' : 'AM';
      return `${String(h % 12 || 12).padStart(2, '0')}:${String(m).padStart(2, '0')} ${ampm}`;
    };

    const parseDurationSeconds = (totalTime) => {
      try {
        const parts = String(totalTime || '').split(':').map(Number);
        if (parts.length === 3) return (parts[0] || 0) * 3600 + (parts[1] || 0) * 60 + (parts[2] || 0);
        if (parts.length === 2) return (parts[0] || 0) * 60 + (parts[1] || 0);
        return 0;
      } catch { return 0; }
    };

    if (validityMode === 'exact_window' && startTime) {
      const start = new Date(`${scheduleDate}T${startTime}:00`);
      if (Number.isNaN(start.getTime())) return `${fmtDate(scheduleDate)}`;
      const durationSec = parseDurationSeconds(assessment?.total_time);
      const end = durationSec > 0
        ? new Date(start.getTime() + durationSec * 1000)
        : null;
      return end
        ? `${fmtDate(scheduleDate)} · ${fmtTime(start)} – ${fmtTime(end)}`
        : `${fmtDate(scheduleDate)} · ${fmtTime(start)}`;
    }

    if (validityMode === 'date_anytime') {
      const endD = endDate && endDate !== scheduleDate ? endDate : null;
      const dateRange = endD
        ? `${fmtDate(scheduleDate)} – ${fmtDate(endD)}`
        : fmtDate(scheduleDate);
      return `${dateRange} · 12:00 AM – 11:59 PM`;
    }

    if (validityMode === 'one_week' && oneWeekEndDate) {
      return `${fmtDate(scheduleDate)} – ${fmtDate(oneWeekEndDate)} · 12:00 AM – 11:59 PM`;
    }

    return fmtDate(scheduleDate);
  })();

  // ── Computed start window for exact mode ──
  const startWindowLabel = (() => {
    if (validityMode !== 'exact_window' || !scheduleDate || !startTime) return '';
    const start = new Date(`${scheduleDate}T${startTime}:00`);
    if (Number.isNaN(start.getTime())) return '';
    const fmt = (d) => {
      const h = d.getHours(), m = String(d.getMinutes()).padStart(2, '0');
      const ampm = h >= 12 ? 'PM' : 'AM';
      return `${String(h % 12 || 12).padStart(2, '0')}:${m} ${ampm}`;
    };
    const end = new Date(start.getTime() + 30 * 60000);
    return `${fmt(start)} – ${fmt(end)}`;
  })();

  // ─────────────────────────────────────────────
  if (loading) {
    return (
      <div className="invite-page">
        <Header />
        <div className="invite-shell">
          <div className="state-card" style={{ marginTop: '2rem' }}>
            <div className="state-title">Loading assessment…</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="invite-page">
        <Header />
        <div className="invite-shell">
          <div className="state-card error" style={{ marginTop: '2rem' }}>
            <div className="state-title">Couldn't open Invite Candidates</div>
            <div className="state-text">{error}</div>
            <button className="btn-primary" type="button" onClick={() => navigate('/assessments')}>Go back</button>
          </div>
        </div>
      </div>
    );
  }

  const isShareDisabled =
    sending ||
    candidates.length === 0 ||
    (isAutoSchedule && selectedInterviewerIds.length === 0) ||
    (assessment?.assessment_mode === 'single' && assessment.invited > 0);

  return (
    <div className="invite-page">
      <Header />

      <div className="invite-shell">

        {/* ── Page Header ── */}
        <div className="invite-top">
          <div className="invite-top-left">
            <div className="invite-icon-wrap">
              {/* Invitation / Send envelope icon */}
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.85" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 2 11 13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </div>
            <div>
              <div className="invite-title">Invite Candidates</div>
              <div className="invite-meta">
                <span className="invite-meta-chip">
                  {assessment?.display_name || assessment?.name || 'Assessment'}
                </span>
                <span className="invite-meta-sep">·</span>
                <span className="invite-meta-chip">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
                  {assessment?.total_time ?? '—'}
                </span>
                <span className="invite-meta-sep">·</span>
                <span className="invite-meta-chip">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" /></svg>
                  {(assessment?.total_questions || 0) + (assessment?.coding_question_count || 0) || '—'} questions
                </span>
              </div>
            </div>
          </div>
          <div className="invite-actions">
            <button className="btn-back" type="button" onClick={() => navigate('/assessments')}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6" /></svg>
              Back
            </button>
          </div>
        </div>

        {/* ── Progress Stepper ── */}
        {assessment?.assessment_mode === 'single' && assessment.invited > 0 && (
          <div className="state-card info" style={{ marginBottom: '1.5rem', background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '1rem', borderRadius: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ background: '#4318FF', color: 'white', borderRadius: '50%', width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>!</div>
              <div>
                <div style={{ fontWeight: '700', color: '#1B254B', fontSize: '0.9rem' }}>Invitation Already Sent</div>
                <div style={{ color: '#64748b', fontSize: '0.8rem' }}>This is a single-candidate assessment. You cannot send more invitations.</div>
              </div>
            </div>
          </div>
        )}
        {(() => {
          const scheduleReady = scheduleDate && (validityMode !== 'exact_window' || startTime);
          const candidatesReady = candidates.length > 0;
          const steps = [
            {
              label: 'Set Schedule', desc: 'Choose date & validity', done: scheduleReady, icon: (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              )
            },
            {
              label: 'Add Candidates', desc: `${candidates.length} added`, done: candidatesReady, icon: (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" /><circle cx="9" cy="7" r="4" />
                  <line x1="19" y1="8" x2="19" y2="14" /><line x1="22" y1="11" x2="16" y2="11" />
                </svg>
              )
            },
            {
              label: 'Share Invites', desc: 'Send to all candidates', done: false, icon: (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              )
            },
          ];
          return (
            <div className="ic-stepper">
              {steps.map((step, i) => (
                <React.Fragment key={step.label}>
                  <div className={`ic-step${step.done ? ' done' : i === 0 && !scheduleReady ? ' active' : i === 1 && scheduleReady && !candidatesReady ? ' active' : i === 2 && scheduleReady && candidatesReady ? ' active' : ''}`}>
                    <div className="ic-step-circle">
                      {step.done
                        ? <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                        : step.icon}
                    </div>
                    <div className="ic-step-text">
                      <span className="ic-step-label">{step.label}</span>
                      <span className="ic-step-desc">{step.desc}</span>
                    </div>
                  </div>
                  {i < steps.length - 1 && <div className={`ic-step-connector${steps[i].done ? ' done' : ''}`} />}
                </React.Fragment>
              ))}
            </div>
          );
        })()}

        {/* ── Schedule / Link Validity Card ── */}
        <div className="ic-card">
          <div className="ic-card-header">
            <div className="ic-card-icon blue">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
            </div>
            <span className="ic-card-title">Schedule / Link Validity</span>
            <span className="ic-card-subtitle">Set when candidates can access this assessment</span>
          </div>

          {/* Mode selector tabs */}
          <div className="validity-toggle">
            <button
              type="button"
              className={`validity-tab${validityMode === 'exact_window' ? ' active' : ''}`}
              onClick={() => { setValidityMode('exact_window'); setScheduleError(''); }}
            >
              <span className="tab-label">Exact Time Window</span>
              <span className="tab-desc">Specific date + time</span>
            </button>
            <button
              type="button"
              className={`validity-tab${validityMode === 'date_anytime' ? ' active' : ''}`}
              onClick={() => { setValidityMode('date_anytime'); setScheduleError(''); }}
            >
              <span className="tab-label">Whole Day / Date Range</span>
              <span className="tab-desc">Anytime on chosen date(s)</span>
            </button>
            <button
              type="button"
              className={`validity-tab${validityMode === 'one_week' ? ' active' : ''}`}
              onClick={() => { setValidityMode('one_week'); setScheduleError(''); }}
            >
              <span className="tab-label">1 Week from Start</span>
              <span className="tab-desc">7-day rolling window</span>
            </button>
          </div>

          {/* Schedule inputs */}
          {validityMode === 'exact_window' && (
            <div className="ic-grid ic-grid-3">
              <div className="ic-field">
                <label className="ic-label">Start Date <span className="ic-required">*</span></label>
                <input
                  type="date"
                  className="ic-input"
                  value={scheduleDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setScheduleDate(e.target.value)}
                />
              </div>
              <div className="ic-field">
                <label className="ic-label">Start Time <span className="ic-required">*</span></label>
                <input
                  type="time"
                  className="ic-input"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                />
              </div>
              <div className="ic-field">
                <label className="ic-label">Start Window (auto)</label>
                <input
                  type="text"
                  className="ic-input"
                  value={startWindowLabel}
                  readOnly
                  placeholder="Auto-computed"
                />
                <span className="ic-hint">30-minute entry window starting at your chosen time</span>
              </div>
            </div>
          )}

          {validityMode === 'date_anytime' && (
            <div className="ic-grid ic-grid-2">
              <div className="ic-field">
                <label className="ic-label">Start Date <span className="ic-required">*</span></label>
                <input
                  type="date"
                  className="ic-input"
                  value={scheduleDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setScheduleDate(e.target.value)}
                />
              </div>
              <div className="ic-field">
                <label className="ic-label">End Date <span style={{ color: '#94a3b8', fontWeight: 400 }}>(optional)</span></label>
                <input
                  type="date"
                  className="ic-input"
                  value={endDate}
                  min={scheduleDate || new Date().toISOString().split('T')[0]}
                  onChange={(e) => setEndDate(e.target.value)}
                />
                <span className="ic-hint">Leave empty to allow only the start date</span>
              </div>
            </div>
          )}

          {validityMode === 'one_week' && (
            <div className="ic-grid ic-grid-2">
              <div className="ic-field">
                <label className="ic-label">Start Date <span className="ic-required">*</span></label>
                <input
                  type="date"
                  className="ic-input"
                  value={scheduleDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setScheduleDate(e.target.value)}
                />
              </div>
              <div className="ic-field">
                <label className="ic-label">End Date (auto)</label>
                <input type="date" className="ic-input" value={oneWeekEndDate} readOnly />
                <span className="ic-hint">Automatically set to 7 days from start</span>
              </div>
            </div>
          )}

          {scheduleError && <p className="ic-error" style={{ marginTop: '0.75rem' }}>{scheduleError}</p>}

          <div className="schedule-note">
            <span className="schedule-note-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </span>
            If a candidate starts within the allowed start window, they can refresh or reconnect and continue until the exam end time.
          </div>
        </div>

        {/* ── Add Candidate Card ── */}
        <div className="ic-card">
          <div className="ic-card-header">
            <div className="ic-card-icon teal">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <line x1="19" y1="8" x2="19" y2="14" /><line x1="22" y1="11" x2="16" y2="11" />
              </svg>
            </div>
            <span className="ic-card-title">Add Candidates</span>
            <span className="ic-card-subtitle">Fill manually or import from CSV</span>
          </div>

          {/* Toolbar */}
          <div className="ic-toolbar">
            <div className="ic-toolbar-left">
              <button className="btn-secondary" type="button" onClick={downloadTemplate}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Download CSV Template
              </button>

              <label
                className={`auto-schedule-toggle${isAutoSchedule ? ' active' : ''}`}
                htmlFor="autoScheduleCheck"
              >
                <input
                  type="checkbox"
                  id="autoScheduleCheck"
                  checked={isAutoSchedule}
                  onChange={(e) => setIsAutoSchedule(e.target.checked)}
                />
                Auto Slot Schedule
              </label>
            </div>

            <div className="ic-toolbar-right">
              {importMsg && (
                <span className="import-msg">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
                  {importMsg}
                </span>
              )}
              <label
                className={`file-pill${isSingleLimitReached ? ' disabled' : ''}`}
                htmlFor="inviteCsv"
                style={isSingleLimitReached ? { opacity: 0.48, cursor: 'not-allowed', pointerEvents: 'none' } : {}}
                title={isSingleLimitReached ? "Single Mode assessment: Only one candidate can be invited." : "Upload CSV"}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                Upload CSV
                <input
                  id="inviteCsv"
                  ref={fileRef}
                  className="file-input"
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(e) => handleCSVUpload(e.target.files?.[0])}
                  disabled={isSingleLimitReached}
                />
              </label>
            </div>
          </div>

          {/* Inline add form */}
          <div className="ic-add-row">
            <div className="ic-field">
              <label className="ic-label">Name <span className="ic-required">*</span></label>
              <div className="ic-input-wrap">
                <input
                  className={`ic-input${name.trim() ? ' ic-input-valid' : ''}`}
                  value={name}
                  onChange={(e) => { if (/^[a-zA-Z\s]*$/.test(e.target.value)) setName(e.target.value); }}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="Full name"
                  maxLength={100}
                  disabled={isSingleLimitReached}
                  title={isSingleLimitReached ? "Single Mode assessment: Only one candidate can be invited." : ""}
                />
                {name.trim() && <span className="ic-input-tick">✓</span>}
              </div>
            </div>
            <div className="ic-field">
              <label className="ic-label">Email <span className="ic-required">*</span></label>
              <div className="ic-input-wrap">
                <input
                  className={`ic-input${email ? (isValidEmail(email) ? ' ic-input-valid' : ' ic-input-invalid') : ''}`}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="candidate@email.com"
                  maxLength={100}
                  disabled={isSingleLimitReached}
                  title={isSingleLimitReached ? "Single Mode assessment: Only one candidate can be invited." : ""}
                />
                {email && (
                  <span className={isValidEmail(email) ? 'ic-input-tick' : 'ic-input-cross'}>
                    {isValidEmail(email) ? '✓' : '✕'}
                  </span>
                )}
              </div>
            </div>
            <div className="ic-field">
              <label className="ic-label">PAN <span className="ic-label-opt">(optional)</span></label>
              <div className="ic-input-wrap">
                <input
                  className={`ic-input${pan ? (isValidPAN(pan) ? (pan.length === 10 ? ' ic-input-valid' : '') : ' ic-input-invalid') : ''}`}
                  value={pan}
                  onChange={handlePanChange}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="ABCDE1234F"
                  maxLength={10}
                  disabled={isSingleLimitReached}
                  title={isSingleLimitReached ? "Single Mode assessment: Only one candidate can be invited." : ""}
                />
                {pan.length === 10 && isValidPAN(pan) && <span className="ic-input-tick">✓</span>}
                {pan && !isValidPAN(pan) && <span className="ic-input-cross">✕</span>}
              </div>
            </div>
            <div className="ic-field" style={{ position: 'relative' }}>
              <label className="ic-label">Phone <span className="ic-label-opt">(optional)</span></label>
              <div className="ic-input-wrap">
                <input
                  className={`ic-input${phone ? (isValidPhone(phone) ? ' ic-input-valid' : ' ic-input-invalid') : ''}`}
                  value={phone}
                  onChange={handlePhoneChange}
                  onKeyDown={(e) => { if (e.key === 'Enter' && canAdd) addCandidate(); }}
                  placeholder="10-digit number"
                  disabled={isSingleLimitReached}
                  title={isSingleLimitReached ? "Single Mode assessment: Only one candidate can be invited." : ""}
                />
                {phone && isValidPhone(phone) && <span className="ic-input-tick">✓</span>}
                {phone && !isValidPhone(phone) && <span className="ic-input-cross">✕</span>}
              </div>
              {phone && !/^[6-9]/.test(phone) && (
                <div style={{ position: 'absolute', top: '100%', left: 0, color: '#ef4444', fontSize: '12px', marginTop: '2px', whiteSpace: 'nowrap' }}>Enter valid phone number (must start with 6, 7, 8 or 9)</div>
              )}
            </div>

            <div className="ic-add-actions">
              <button
                className="btn-tertiary"
                type="button"
                onClick={addCandidate}
                disabled={!canAdd || isSingleLimitReached}
                title={isSingleLimitReached ? "Single Mode assessment: Only one candidate can be invited." : "Add Candidate"}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add
              </button>

              {isAutoSchedule && (
                <button
                  type="button"
                  onClick={() => setShowBookingModal(true)}
                  disabled={candidates.length === 0}
                  className={selectedInterviewerIds.length > 0 ? 'btn-schedule scheduled' : 'btn-schedule'}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" />
                  </svg>
                  {selectedInterviewerIds.length > 0 ? `Scheduled (${selectedInterviewerIds.length})` : 'Schedule Interview'}
                </button>
              )}

              <button
                type="button"
                onClick={shareInvites}
                disabled={isShareDisabled}
                className="btn-share"
              >
                {sending ? (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'spin 1s linear infinite' }}>
                      <polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10" />
                    </svg>
                    Sending…
                  </>
                ) : (
                  <>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                    Share Invites
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* ── Candidates Table Card ── */}
        <div className="ic-card">
          <div className="ic-card-header">
            <div className="ic-card-icon violet">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
              </svg>
            </div>
            <span className="ic-card-title">Candidates</span>
            {candidates.length > 0 && (
              <span className="ic-card-subtitle">{candidates.length} {candidates.length === 1 ? 'candidate' : 'candidates'} added</span>
            )}
          </div>

          {candidates.length > 0 && (
            <div className="ic-stats-bar">
              <div className="ic-stat">
                <span className="ic-stat-val">{candidates.length}</span>
                <span className="ic-stat-label">Total</span>
              </div>
              <div className="ic-stat">
                <span className="ic-stat-val">{candidates.filter(c => c.pan_number).length}</span>
                <span className="ic-stat-label">With PAN</span>
              </div>
              <div className="ic-stat">
                <span className="ic-stat-val">{candidates.filter(c => c.phone).length}</span>
                <span className="ic-stat-label">With Phone</span>
              </div>
              {scheduleDisplay && (
                <div className="ic-stat ic-stat-schedule">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                  <span className="ic-stat-schedule-val">{scheduleDisplay}</span>
                </div>
              )}
              <div className="ic-stat-actions">
                <button
                  type="button"
                  className="btn-clear-all"
                  onClick={() => { if (window.confirm(`Remove all ${candidates.length} candidates?`)) setCandidates([]); }}
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14H6L5 6" /><path d="M10 11v6" /><path d="M14 11v6" />
                    <path d="M9 6V4h6v2" />
                  </svg>
                  Clear All
                </button>
              </div>
            </div>
          )}

          {candidates.length === 0 ? (
            <div className="ic-empty">
              <div className="ic-empty-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
                </svg>
              </div>
              <div className="ic-empty-title">No candidates added yet</div>
              <div className="ic-empty-text">Fill in the form above or upload a CSV file to add candidates to this invite batch.</div>
            </div>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Candidate</th>
                    <th>Email</th>
                    <th>Scheduled</th>
                    <th>PAN</th>
                    <th>Phone</th>
                    <th style={{ textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map((c, idx) => (
                    <tr key={`${c.email}-${idx}`}>
                      <td style={{ color: '#94a3b8', fontSize: '0.78rem', fontWeight: 600, width: '2.5rem' }}>
                        {idx + 1}
                      </td>
                      <td>
                        <div className="cand-cell">
                          <div className="cand-avatar">{getInitials(c.name)}</div>
                          <span className="cand-name">{c.name}</span>
                        </div>
                      </td>
                      <td><span className="mono">{c.email}</span></td>
                      <td>
                        {scheduleDisplay
                          ? <span className="badge-schedule">{scheduleDisplay}</span>
                          : <span className="badge-schedule-none">Not set</span>}
                      </td>
                      <td>
                        {c.pan_number
                          ? <span className="badge-pan">{c.pan_number}</span>
                          : <span className="badge-dash">—</span>}
                      </td>
                      <td>
                        {c.phone
                          ? <span className="mono">{c.phone}</span>
                          : <span className="badge-dash">—</span>}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button className="btn-danger" type="button" onClick={() => removeCandidate(idx)}>Remove</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>

      {/* ── Interviewer Booking Modal ── */}
      {showBookingModal && (
        <div className="ic-modal-overlay" onClick={() => setShowBookingModal(false)}>
          <div className="ic-modal" onClick={(e) => e.stopPropagation()}>
            <div className="ic-modal-head">
              <div className="ic-modal-head-left">
                <div className="ic-modal-head-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 00-3-3.87" /><path d="M16 3.13a4 4 0 010 7.75" />
                  </svg>
                </div>
                <div>
                  <div className="ic-modal-title">Select Interviewers</div>
                  <div className="ic-modal-desc">Choose who will conduct the interviews</div>
                </div>
              </div>
              <button
                className="ic-modal-close"
                onClick={() => setShowBookingModal(false)}
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            <div className="ic-modal-body">
              <div className="ic-interviewer-list">
                {teamMembers.length > 0 ? (
                  teamMembers.map(member => {
                    const fullName = member.first_name
                      ? `${member.first_name} ${member.last_name || ''}`.trim()
                      : member.email;
                    const isSelected = selectedInterviewerIds.includes(member.id);
                    return (
                      <div
                        key={member.id}
                        className={`ic-interviewer-row${isSelected ? ' selected' : ''}`}
                        onClick={() => toggleInterviewer(member.id)}
                      >
                        <input type="checkbox" readOnly checked={isSelected} />
                        <div className="ic-interviewer-avatar">{getInitials(fullName)}</div>
                        <div className="ic-interviewer-info">
                          <div className="ic-interviewer-name">{fullName}</div>
                          {member.first_name && (
                            <div className="ic-interviewer-email">{member.email}</div>
                          )}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="ic-modal-no-interviewers">
                    <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>👥</div>
                    <div>No interviewers found in your team.</div>
                  </div>
                )}
              </div>
            </div>

            <div className="ic-modal-foot">
              <button
                onClick={() => setShowBookingModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateSlots}
                className="btn-primary"
                disabled={generating || selectedInterviewerIds.length === 0}
              >
                {generating ? 'Generating…' : `Generate Slots${selectedInterviewerIds.length > 0 ? ` for ${selectedInterviewerIds.length}` : ''}`}
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>

      {/* Credit cost indicator */}
      {candidates.length > 0 && (
        <div style={{ position: 'fixed', bottom: '1rem', left: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', gap: '6px', background: 'white', padding: '8px 16px', borderRadius: '12px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)', border: '1px solid #e2e8f0', zIndex: 50, color: '#6366f1', fontSize: '0.85rem', fontWeight: 600 }}>
          <span>⚡</span>
          <span>Invite cost: <strong>{totalCreditCost} credits</strong> ({candidates.length} × {creditPerCandidate})</span>
          <span style={{ color: '#94a3b8', fontWeight: 400 }}>({availableCredits} available)</span>
        </div>
      )}

      {/* Credit Confirmation Popup */}
      {showCreditConfirm && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
          <div style={{ background: 'white', borderRadius: '20px', padding: '2rem', maxWidth: '400px', width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.2)' }}>
            <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
              <div style={{ width: '56px', height: '56px', borderRadius: '16px', background: 'linear-gradient(135deg, #eef2ff, #e0e7ff)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                <span style={{ fontSize: '1.5rem' }}>⚡</span>
              </div>
              <h3 style={{ margin: '0 0 0.5rem', fontSize: '1.2rem', fontWeight: 700, color: '#1e293b' }}>Confirm Credit Usage</h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.9rem' }}>
                Sending invites will use <strong style={{ color: '#6366f1' }}>{totalCreditCost} credits</strong>.
              </p>
              <p style={{ margin: '0.5rem 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
                {candidates.length} candidates × {creditPerCandidate} credits each
              </p>
              <p style={{ margin: '0.25rem 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
                Remaining after: {availableCredits - totalCreditCost} credits
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button onClick={() => setShowCreditConfirm(false)} style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: '1px solid #e2e8f0', background: 'white', color: '#475569', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
              <button onClick={proceedWithInvites} style={{ flex: 1, padding: '0.85rem', borderRadius: '12px', border: 'none', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', fontSize: '0.9rem', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 14px rgba(99,102,241,0.3)' }}>Proceed</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
