import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/InterviewInvite.css';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';
const INTERVIEW_INVITE_DRAFT_KEY_PREFIX = 'interviewInviteDraft:';

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((email || '').trim());
}

function isValidPAN(pan) {
  if (!pan) return true;
  return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test((pan || '').trim().toUpperCase());
}

function normalizeHeader(h) {
  return (h || '').toString().trim().toLowerCase().replace(/\s+/g, '_');
}

function parseCSV(text) {
  const rows = [];
  let row = [];
  let cell = '';
  let inQuotes = false;

  const pushCell = () => {
    row.push(cell);
    cell = '';
  };

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
        if (next === '"') {
          cell += '"';
          i += 1;
        } else {
          inQuotes = false;
        }
      } else {
        cell += ch;
      }
    } else if (ch === '"') {
      inQuotes = true;
    } else if (ch === ',') {
      pushCell();
    } else if (ch === '\n') {
      pushCell();
      pushRow();
    } else if (ch === '\r') {
      // ignore
    } else {
      cell += ch;
    }
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

export default function InterviewInvite() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [pan, setPan] = useState('');
  const [phone, setPhone] = useState('');

  const [candidates, setCandidates] = useState([]);
  const [sending, setSending] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [importMsg, setImportMsg] = useState('');
  const fileRef = useRef(null);

  // Scheduling / validity controls
  const [validityMode, setValidityMode] = useState('exact_window');
  const [scheduleDate, setScheduleDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [scheduleError, setScheduleError] = useState('');

  const draftKey = INTERVIEW_INVITE_DRAFT_KEY_PREFIX;

  const canAdd = useMemo(() => {
    const n = name.trim();
    const e = email.trim();
    const p = pan.trim();
    if (!n) return false;
    if (!isValidEmail(e)) return false;
    if (!isValidPAN(p)) return false;
    return true;
  }, [name, email, pan]);

  // Restore draft candidates on refresh
  useEffect(() => {
    try {
      const raw = localStorage.getItem(draftKey);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && Array.isArray(parsed.candidates)) {
          setCandidates(parsed.candidates);
        }
        if (parsed && typeof parsed.name === 'string') setName(parsed.name);
        if (parsed && typeof parsed.email === 'string') setEmail(parsed.email);
        if (parsed && typeof parsed.pan === 'string') setPan(parsed.pan);
        if (parsed && typeof parsed.phone === 'string') setPhone(parsed.phone);
      }
    } catch {
      // ignore
    } finally {
      setHydrated(true);
    }
  }, [draftKey]);

  // Persist draft while user is adding/removing candidates
  useEffect(() => {
    if (!hydrated) return;
    try {
      localStorage.setItem(
        draftKey,
        JSON.stringify({
          candidates,
          name,
          email,
          pan,
          phone,
          updated_at: Date.now(),
        })
      );
    } catch {
      // ignore
    }
  }, [draftKey, hydrated, candidates, name, email, pan, phone]);

  const addCandidate = () => {
    const n = name.trim();
    const e = email.trim().toLowerCase();
    const p = pan.trim().toUpperCase();
    const ph = phone.trim();

    if (!n) return;
    if (!isValidEmail(e)) return;
    if (!isValidPAN(p)) return;

    const dupe = candidates.some((c) => c.email.toLowerCase() === e || (p && c.pan_number && c.pan_number === p));
    if (dupe) {
      alert('This candidate email or PAN already exists in the list.');
      return;
    }

    setCandidates((prev) => [
      ...prev,
      {
        name: n,
        email: e,
        pan_number: p || null,
        phone: ph || null,
      },
    ]);

    setName('');
    setEmail('');
    setPan('');
    setPhone('');
  };

  const removeCandidate = (idx) => {
    const c = candidates[idx];
    const label = `${c?.name || 'Candidate'}${c?.email ? ` (${c.email})` : ''}`;
    const ok = window.confirm(`Remove ${label}?`);
    if (!ok) return;
    setCandidates((prev) => prev.filter((_, i) => i !== idx));
  };

  const downloadTemplate = () => {
    const sample = [
      ['name', 'email', 'pan_number', 'phone'].join(','),
      ['John Doe', 'john@example.com', 'ABCDE1234F', '9999999999'].join(','),
    ].join('\n');
    downloadTextFile('interview_invite_template.csv', sample);
  };

  const importFromCSVText = (csvText) => {
    setImportMsg('');
    const rows = parseCSV(csvText || '');
    if (!rows.length) {
      setImportMsg('CSV is empty.');
      return;
    }

    const first = rows[0].map((c) => normalizeHeader(c));
    const hasHeader = first.includes('email') || first.includes('name');

    let header = null;
    let dataRows = rows;
    if (hasHeader) {
      header = first;
      dataRows = rows.slice(1);
    }

    const mapRow = (cells) => {
      const get = (key, idxFallback) => {
        if (header) {
          const idx = header.indexOf(key);
          if (idx >= 0) return (cells[idx] ?? '').toString().trim();
          return '';
        }
        return (cells[idxFallback] ?? '').toString().trim();
      };

      const n = get('name', 0);
      const e = get('email', 1).toLowerCase();
      const pRaw = get('pan_number', 2) || get('pan', 2);
      const phRaw = get('phone', 3) || get('phone_number', 3) || get('mobile', 3);
      const p = (pRaw || '').trim().toUpperCase();
      const ph = (phRaw || '').trim();

      return {
        name: n,
        email: e,
        pan_number: p || null,
        phone: ph || null,
      };
    };

    const existingEmails = new Set(candidates.map((c) => (c.email || '').toLowerCase()));
    const existingPANs = new Set(candidates.map((c) => (c.pan_number || '').toUpperCase()).filter(Boolean));

    let added = 0;
    let dupes = 0;
    let invalid = 0;

    const next = [...candidates];

    dataRows.forEach((cells) => {
      const r = mapRow(cells);
      const n = (r.name || '').trim();
      const e = (r.email || '').trim();
      const p = (r.pan_number || '').trim().toUpperCase();

      if (!n || !isValidEmail(e) || !isValidPAN(p)) {
        invalid += 1;
        return;
      }

      const emailKey = e.toLowerCase();
      if (existingEmails.has(emailKey) || (p && existingPANs.has(p))) {
        dupes += 1;
        return;
      }

      existingEmails.add(emailKey);
      if (p) existingPANs.add(p);
      next.push({
        name: n,
        email: emailKey,
        pan_number: p || null,
        phone: r.phone ? String(r.phone).trim() : null,
      });
      added += 1;
    });

    setCandidates(next);
    setImportMsg(`Imported ${added}. Skipped duplicates ${dupes}. Invalid rows ${invalid}.`);
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
    if (candidates.length === 0) {
      alert('Please add at least one candidate.');
      return;
    }

    const tz = (() => {
      try {
        return Intl.DateTimeFormat().resolvedOptions().timeZone || null;
      } catch {
        return null;
      }
    })();

    const toISOFromLocal = (dateStr, timeStr) => {
      const d = new Date(`${dateStr}T${timeStr}:00`);
      if (Number.isNaN(d.getTime())) return null;
      return d.toISOString();
    };

    const parseHHMMSSSeconds = (value) => {
      try {
        const parts = String(value || '').split(':').map((x) => Number(x));
        if (parts.length === 2) {
          const [m, s] = parts;
          return Math.max(0, (m || 0) * 60 + (s || 0));
        }
        if (parts.length === 3) {
          const [h, m, s] = parts;
          return Math.max(0, (h || 0) * 3600 + (m || 0) * 60 + (s || 0));
        }
        return 0;
      } catch {
        return 0;
      }
    };

    const buildSchedule = () => {
      setScheduleError('');
      if (validityMode === 'date_anytime') {
        if (!scheduleDate) return { ok: false, error: 'Please select a start date for "Whole day".' };
        const startIso = toISOFromLocal(scheduleDate, '00:00');
        const endD = endDate || scheduleDate;
        const endLocal = new Date(`${endD}T23:59:59`);
        if (!startIso || Number.isNaN(endLocal.getTime())) return { ok: false, error: 'Invalid date.' };
        if (endLocal.getTime() < new Date(startIso).getTime()) {
          return { ok: false, error: 'End date must be same or after start date.' };
        }
        return { ok: true, start_time: startIso, end_time: endLocal.toISOString() };
      }
      if (validityMode === 'one_week') {
        if (!scheduleDate) return { ok: false, error: 'Please select a start date for "1 week".' };
        const startIso = toISOFromLocal(scheduleDate, '00:00');
        if (!startIso) return { ok: false, error: 'Invalid start date.' };
        const start = new Date(startIso);
        const end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
        const endYMD = `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
        const endLocal = new Date(`${endYMD}T23:59:59`);
        return { ok: true, start_time: start.toISOString(), end_time: endLocal.toISOString() };
      }
      // exact_window
      if (!scheduleDate || !startTime) return { ok: false, error: 'Please select date and start time.' };
      const startIso = toISOFromLocal(scheduleDate, startTime);
      if (!startIso) return { ok: false, error: 'Invalid start time.' };

      // For interview invites, duration is optional - use a default if not provided
      const durationSeconds = 3600; // Default 1 hour for interviews

      const end = new Date(new Date(startIso).getTime() + durationSeconds * 1000);
      const endIso = end.toISOString();

      const DEFAULT_START_GRACE_MINUTES = 30;
      return { ok: true, start_time: startIso, end_time: endIso, start_grace_minutes: DEFAULT_START_GRACE_MINUTES };
    };

    const sched = buildSchedule();
    if (!sched.ok) {
      setScheduleError(sched.error);
      alert(sched.error);
      return;
    }

    const payloadCandidates = candidates.map((c) => ({
      ...c,
      start_time: sched.start_time,
      end_time: sched.end_time,
      time_zone: tz,
      start_grace_minutes: validityMode === 'exact_window' ? (sched.start_grace_minutes || 0) : 0,
    }));

    setSending(true);
    setError('');
    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/invite/`, {
        candidates: payloadCandidates,
        interview_name: 'Interview Invitation',
      });

      const { sent, failed, results } = resp.data || {};
      
      if (failed > 0) {
        const failedEmails = results.filter(r => r.status === 'failed').map(r => r.email).join(', ');
        alert(`Sent ${sent} invite(s). Failed to send ${failed} invite(s): ${failedEmails}`);
      } else {
        alert(`Successfully sent interview invites to ${sent} candidate(s).`);
      }

      // Clear draft ONLY after Share completes successfully
      try {
        localStorage.removeItem(draftKey);
      } catch {
        // ignore
      }
      setCandidates([]);
      setName('');
      setEmail('');
      setPan('');
      setPhone('');
      setImportMsg('');
      setScheduleDate('');
      setEndDate('');
      setStartTime('');
    } catch (e) {
      const errorMsg = e?.response?.data?.error || e?.message || 'Failed to send interview invites';
      setError(errorMsg);
      alert(errorMsg);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="interview-invite-page">
      <Header />

      <div className="interview-invite-shell">
        <div className="interview-invite-top">
          <div>
            <div className="interview-invite-title">Invite Candidates</div>
          </div>
          <div className="interview-invite-actions">
            <button className="btn-secondary" type="button" onClick={() => navigate('/dashboard')}>Back</button>
            <button className="btn-primary" type="button" onClick={shareInvites} disabled={sending || candidates.length === 0}>
              {sending ? 'Sharing…' : 'Share'}
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Schedule / Link Validity</div>
          <div className="form-grid" style={{ marginBottom: 8 }}>
            <div className="field">
              <label>Validity Type</label>
              <select
                className="select"
                value={validityMode}
                onChange={(e) => {
                  setValidityMode(e.target.value);
                  setScheduleError('');
                }}
              >
                <option value="exact_window">Particular date + time window</option>
                <option value="date_anytime">Particular date (whole day / date range)</option>
                <option value="one_week">1 week from start</option>
              </select>
            </div>
            <div className="field">
              <label>Start Date</label>
              <input type="date" value={scheduleDate} onChange={(e) => setScheduleDate(e.target.value)} />
            </div>
            {validityMode === 'date_anytime' ? (
              <div className="field">
                <label>End Date (optional)</label>
                <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                <div className="hint">Leave empty to allow only the start date.</div>
              </div>
            ) : validityMode === 'one_week' ? (
              <div className="field">
                <label>End Date (auto)</label>
                <input
                  type="date"
                  value={(() => {
                    if (!scheduleDate) return '';
                    const start = new Date(`${scheduleDate}T00:00:00`);
                    if (Number.isNaN(start.getTime())) return '';
                    const end = new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000);
                    return `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
                  })()}
                  readOnly
                />
              </div>
            ) : (
              <>
                <div className="field">
                  <label>Start Time</label>
                  <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
                  <div className="hint">Grace period is automatically applied.</div>
                </div>
                <div className="field">
                  <label>End Time (auto)</label>
                  <input
                    type="text"
                    value={(() => {
                      // Default interview duration: 1 hour (3600 seconds)
                      const durationSeconds = 3600;
                      if (!scheduleDate || !startTime || !durationSeconds) return '';
                      const start = new Date(`${scheduleDate}T${startTime}:00`);
                      if (Number.isNaN(start.getTime())) return '';
                      const end = new Date(start.getTime() + durationSeconds * 1000);
                      const hh = String(end.getHours()).padStart(2, '0');
                      const mm = String(end.getMinutes()).padStart(2, '0');
                      return `${hh}:${mm}`;
                    })()}
                    readOnly
                    placeholder="Auto"
                  />
                  <div className="hint">Calculated using default interview duration: <span className="mono">01:00:00</span></div>
                </div>
              </>
            )}
          </div>
          {scheduleError ? <div className="hint error-text">{scheduleError}</div> : null}
          <div className="hint">
            Note: If a candidate starts within the allowed start window, they can refresh/reconnect and continue until the interview end time.
          </div>
        </div>

        <div className="card">
          <div className="card-title">Add Candidate</div>
          <div className="bulk-row">
            <button className="btn-secondary" type="button" onClick={downloadTemplate}>
              Download CSV Template
            </button>
            <label className="file-pill" htmlFor="interviewInviteCsv">
              Upload CSV
              <input
                id="interviewInviteCsv"
                ref={fileRef}
                className="file-input"
                type="file"
                accept=".csv,text/csv"
                onChange={(e) => handleCSVUpload(e.target.files?.[0])}
              />
            </label>
            <div className="hint">
              Columns: <span className="mono">name,email,pan_number,phone</span> (PAN/Phone optional)
            </div>
          </div>
          {importMsg ? <div className="hint">{importMsg}</div> : null}
          <div className="form-grid add-inline">
            <div className="field">
              <label>Name *</label>
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Candidate name" />
            </div>
            <div className="field">
              <label>Email *</label>
              <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Candidate email" />
            </div>
            <div className="field">
              <label>PAN</label>
              <input value={pan} onChange={(e) => setPan(e.target.value.toUpperCase())} placeholder="ABCDE1234F" maxLength={10} />
              {pan && !isValidPAN(pan) ? <div className="hint error-text">Invalid PAN format.</div> : null}
            </div>
            <div className="field">
              <label>Phone</label>
              <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Optional" />
            </div>
            <div className="field add-btn-cell">
              <label>&nbsp;</label>
              <button className="btn-tertiary add-btn" type="button" onClick={addCandidate} disabled={!canAdd}>
                Add
              </button>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Candidates</div>
          {candidates.length === 0 ? (
            <div className="empty">No candidates added yet.</div>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>PAN</th>
                    <th>Phone</th>
                    <th style={{ textAlign: 'right' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {candidates.map((c, idx) => (
                    <tr key={`${c.email}-${idx}`}>
                      <td>{c.name}</td>
                      <td className="mono">{c.email}</td>
                      <td className="mono">{c.pan_number || '-'}</td>
                      <td className="mono">{c.phone || '-'}</td>
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
    </div>
  );
}
