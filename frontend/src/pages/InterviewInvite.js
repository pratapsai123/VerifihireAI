import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import '../styles/InterviewInvite.css';

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

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [interviewerName, setInterviewerName] = useState('');
  const [interviewerEmail, setInterviewerEmail] = useState('');
  const [pan, setPan] = useState('');
  const [phone, setPhone] = useState('');

  const [candidates, setCandidates] = useState([]);
  const [sending, setSending] = useState(false);
  const [importMsg, setImportMsg] = useState('');
  const fileRef = useRef(null);

  const [userProfile, setUserProfile] = useState(null);

  // Scheduling / validity controls
  const [validityMode, setValidityMode] = useState('exact_window');
  const [scheduleDate, setScheduleDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [startTime, setStartTime] = useState('');
  const [scheduleError, setScheduleError] = useState('');

  const handlePanChange = (e) => {
    let val = e.target.value.toUpperCase();
    // Enforce strict format: 5 letters, 4 numbers, 1 letter
    val = val.replace(/[^A-Z0-9]/g, '');
    if (val.length > 10) return; // Max 10 chars
    let newVal = '';
    for (let i = 0; i < val.length; i++) {
      const char = val[i];
      if (i < 5) {
        // First 5 must be letters
        if (/[A-Z]/.test(char)) newVal += char;
      } else if (i < 9) {
        // Next 4 must be numbers
        if (/[0-9]/.test(char)) newVal += char;
      } else if (i === 9) {
        // Last 1 must be letter
        if (/[A-Z]/.test(char)) newVal += char;
      }
    }
    setPan(newVal);
  };
  const handlePhoneChange = (e) => {
    const val = e.target.value.replace(/\D/g, ''); // Remove non-digits
    if (val.length <= 10) {
      setPhone(val);
    }
  };


  const draftKey = INTERVIEW_INVITE_DRAFT_KEY_PREFIX;

  const canAdd = useMemo(() => {
    const n = name.trim();
    const e = email.trim();
    const intN = interviewerName.trim();
    const intE = interviewerEmail.trim();
    const p = pan.trim();
    if (!n) return false;
    if (!isValidEmail(e)) return false;
    if (!isValidEmail(intE)) return false;
    if (!intN) return false;
    if (!isValidPAN(p)) return false;

    if (validityMode === 'exact_window') {
      if (!scheduleDate || !startTime) return false;
    } else {
      if (!scheduleDate) return false;
    }

    return true;
  }, [name, email, interviewerName, interviewerEmail, pan, validityMode, scheduleDate, startTime]);

  const userDomain = useMemo(() => {
    if (!userProfile?.email) return '';
    return userProfile.email.split('@')[1] || '';
  }, [userProfile]);

  // Fetch Profile and Existing Draft Candidates
  const fetchDraftsAndProfile = async () => {
    try {
      const profileUrl = `${API_BASE_URL}/profile/`;
      const [profileRes, draftsRes] = await Promise.all([
        axios.get(profileUrl),
        axios.get(`${API_BASE_URL}/interviews/draft-invites/`)
      ]);
      setUserProfile(profileRes.data);
      if (draftsRes.data?.results) {
        setCandidates(draftsRes.data.results);
      }
    } catch (err) {
      console.error('Failed to load profile or drafts', err);
    } finally {
      // hydration complete
    }
  };

  useEffect(() => {
    fetchDraftsAndProfile();
  }, []);

  const addCandidate = async () => {
    const n = name.trim();
    const e = email.trim().toLowerCase();
    const intN = interviewerName.trim();
    const intE = interviewerEmail.trim().toLowerCase();
    const p = pan.trim().toUpperCase();
    const ph = phone.trim();

    if (!n) return;
    if (!isValidEmail(e)) return;
    if (!isValidPAN(p)) return;

    if (!intN) return;
    if (!isValidEmail(intE)) return;

    if (userDomain && !intE.endsWith(`@${userDomain}`)) {
      alert(`Interviewer email must belong to your company domain (@${userDomain}).`);
      return;
    }

    const dupe = candidates.some((c) => c.email.toLowerCase() === e || (p && c.pan_number && c.pan_number === p));
    if (dupe) {
      alert('This candidate email or PAN already exists in the list.');
      return;
    }

    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/draft-invites/`, {
        name: n,
        email: e,
        interviewer_name: intN,
        interviewer_email: intE,
        pan_number: p || null,
        phone: ph || null,
      });

      if (resp.data?.results) {
        setCandidates((prev) => [...prev, ...resp.data.results]);
      }

      setName('');
      setEmail('');
      setInterviewerName('');
      setInterviewerEmail('');
      setPan('');
      setPhone('');
    } catch (err) {
      alert(err?.response?.data?.error || 'Failed to save draft candidate.');
    }
  };

  const removeCandidate = async (idx) => {
    const c = candidates[idx];
    const label = `${c?.name || 'Candidate'}${c?.email ? ` (${c.email})` : ''}`;
    const ok = window.confirm(`Remove ${label}?`);
    if (!ok) return;

    try {
      await axios.delete(`${API_BASE_URL}/interviews/draft-invites/${c.id}/`);
      setCandidates((prev) => prev.filter((_, i) => i !== idx));
    } catch (err) {
      alert('Failed to remove draft candidate.');
    }
  };

  const downloadTemplate = () => {
    const sample = [
      ['name', 'email', 'interviewer_name', 'interviewer_email', 'pan_number', 'phone'].join(','),
      ['John Doe', 'john@example.com', 'Jane Smith', 'jane@iit.org.in', 'ABCDE1234F', '9999999999'].join(','),
    ].join('\n');
    downloadTextFile('interview_invite_template.csv', sample);
  };

  const importFromCSVText = async (csvText) => {
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
      const intN = get('interviewer_name', 2);
      const intE = get('interviewer_email', 3).toLowerCase();
      const pRaw = get('pan_number', 4) || get('pan', 4);
      const phRaw = get('phone', 5) || get('phone_number', 5) || get('mobile', 5);
      const p = (pRaw || '').trim().toUpperCase();
      const ph = (phRaw || '').trim();

      return {
        name: n,
        email: e,
        interviewer_name: intN || n,
        interviewer_email: intE || '',
        pan_number: p || null,
        phone: ph || null,
      };
    };

    const existingEmails = new Set(candidates.map((c) => (c.email || '').toLowerCase()));
    const existingPANs = new Set(candidates.map((c) => (c.pan_number || '').toUpperCase()).filter(Boolean));

    let invalidDomain = 0;
    let dupes = 0;
    let invalid = 0;
    const toUpload = [];

    dataRows.forEach((cells) => {
      const r = mapRow(cells);
      const n = (r.name || '').trim();
      const e = (r.email || '').trim();
      const p = (r.pan_number || '').trim().toUpperCase();
      const intE = (r.interviewer_email || '').trim().toLowerCase();

      if (!n || !isValidEmail(e) || !isValidPAN(p) || !isValidEmail(intE)) {
        invalid += 1;
        return;
      }

      if (userDomain && !intE.endsWith(`@${userDomain}`)) {
        invalidDomain += 1;
        return;
      }

      const emailKey = e.toLowerCase();
      if (existingEmails.has(emailKey) || (p && existingPANs.has(p))) {
        dupes += 1;
        return;
      }

      existingEmails.add(emailKey);
      if (p) existingPANs.add(p);
      toUpload.push(r);
    });

    if (toUpload.length === 0) {
      setImportMsg(`No valid candidates imported. Skipped duplicates: ${dupes}. Invalid format: ${invalid}. Invalid Domain: ${invalidDomain}.`);
      return;
    }

    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/draft-invites/`, {
        candidates: toUpload
      });
      if (resp.data?.results) {
        setCandidates((prev) => [...prev, ...resp.data.results]);
        setImportMsg(`Imported ${resp.data.results.length}. Skipped duplicates: ${dupes}. Invalid format: ${invalid}. Invalid domain: ${invalidDomain}.`);
      }
    } catch (err) {
      setImportMsg('Failed to save imported drafts to server.');
    }
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

    setSending(true);
    try {
      const resp = await axios.post(`${API_BASE_URL}/interviews/invite/`, {
        draft_ids: candidates.map(c => c.id),
        interview_name: 'Interview Invitation',
        start_time: sched.start_time,
        end_time: sched.end_time,
        time_zone: tz,
        validity_mode: validityMode,
        start_grace_minutes: validityMode === 'exact_window' ? (sched.start_grace_minutes || 0) : 0,
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
          <div className="card-title">Add Candidate
            <button className="btn-primary" type="button" onClick={shareInvites} disabled={sending || candidates.length === 0}>
              {sending ? 'Sharing…' : 'Share'}
            </button>
          </div>

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
              <label>Candidate Name *</label>
              <input value={name} onChange={(e) => { if (/^[a-zA-Z\s]*$/.test(e.target.value)) setName(e.target.value); }} placeholder="Candidate name" maxLength={100} />
            </div>
            <div className="field">
              <label>Candidate Email *</label>
              <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Candidate email" maxLength={100} />
            </div>
            <div className="field">
              <label>Candidate Phone (Optional)</label>
              <input value={phone} onChange={handlePhoneChange} placeholder="1234567890" maxLength={10} />
            </div>
            <div className="field">
              <label>Interviewer Name *</label>
              <input value={interviewerName} onChange={(e) => setInterviewerName(e.target.value)} placeholder="Interviewer Name" maxLength={100} />
            </div>
            <div className="field">
              <label>Interviewer Email *</label>
              <input value={interviewerEmail} onChange={(e) => setInterviewerEmail(e.target.value)} placeholder={`e.g. user@${userDomain || 'company.com'}`} maxLength={100} />
            </div>
            <div className="field">
              <label>Candidate PAN (Optional)</label>
              <input value={pan} onChange={handlePanChange} placeholder="ABCDE1234F" maxLength={10} />
              {pan && !isValidPAN(pan) ? <div className="hint error-text">Invalid PAN format.</div> : null}
            </div>
          </div>
          <div className="add-action-row">
            <button className="btn-primary" type="button" onClick={addCandidate} disabled={!canAdd} style={{ padding: '0.75rem 2.5rem', fontSize: '1rem', marginTop: '1.5rem' }}>
              Add Candidate
            </button>
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
                    <th>Candidate Name</th>
                    <th>Candidate Email</th>
                    <th>Interviewer Name</th>
                    <th>Interviewer Email</th>
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
                      <td>{c.interviewer_name}</td>
                      <td className="mono">{c.interviewer_email}</td>
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
