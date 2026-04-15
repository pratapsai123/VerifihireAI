import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { 
    Save, 
    ArrowLeft, 
    ExternalLink, 
    Plus, 
    Trash2, 
    Clock, 
    Cpu, 
    Globe, 
    Layout, 
    Code, 
    CheckCircle,
    BarChart,
    ChevronUp,
    ChevronDown,
    Search,
    Database,
    AlertCircle,
    FileText,
    Languages,
    TrendingUp,
    AlignLeft,
    Timer,
    ShieldCheck,
    Hash,
    Eye,
    EyeOff
} from 'lucide-react';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import '../styles/Coding.css';

const DEFAULT_LANGS = [
  'cpp',
  'java',
  // 'python3',
  'python',
  'javascript',
  'typescript',
  'csharp',
  'c',
  'go',
  'kotlin',
  'swift',
  'rust',
  'ruby',
  'php',
  'dart',
  'scala',
  'sql',
];

const LANG_OPTIONS = [
  { value: 'cpp', label: 'C++' },
  { value: 'java', label: 'Java' },
  // { value: 'python3', label: 'Python3' },
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'csharp', label: 'C#' },
  { value: 'c', label: 'C' },
  { value: 'go', label: 'Go' },
  { value: 'kotlin', label: 'Kotlin' },
  { value: 'swift', label: 'Swift' },
  { value: 'rust', label: 'Rust' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'php', label: 'PHP' },
  { value: 'dart', label: 'Dart' },
  { value: 'scala', label: 'Scala' },
  // { value: 'scala', label: 'Scala' },
  { value: 'sql', label: 'SQL' },
];

const DIFFICULTY_OPTIONS = [
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

// Default main method templates for each language
function getDefaultTemplate(lang) {
  const templates = {
    'cpp': `#include <iostream>
#include <vector>
#include <string>
using namespace std;

int main() {
    // Your code here
    return 0;
}`,
    'java': `public class Main {
    public static void main(String[] args) {
        // Your code here
    }
}`,
    'python3': `def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()`,
    'python': `def main():
    # Your code here
    pass

if __name__ == "__main__":
    main()`,
    'javascript': `function main() {
    // Your code here
}

main();`,
    'typescript': `function main(): void {
    // Your code here
}

main();`,
    'csharp': `using System;

class Program {
    static void Main(string[] args) {
        // Your code here
    }
}`,
    'c': `#include <stdio.h>

int main() {
    // Your code here
    return 0;
}`,
    'go': `package main

import "fmt"

func main() {
    // Your code here
}`,
    'kotlin': `fun main() {
    // Your code here
}`,
    'swift': `import Foundation

// Your code here`,
    'rust': `fn main() {
    // Your code here
}`,
    'ruby': `def main
    # Your code here
end

main`,
    'php': `<?php
// Your code here
?>`,
    'dart': `void main() {
    // Your code here
}`,
    'scala': `object Main {
    def main(args: Array[String]): Unit = {
        // Your code here
    }
}`,
    'sql': `-- Write your SQL query here
-- Result should match expected output
`,
  };
  return templates[lang] || '// Your code here';
}

// Generate starter code for multiple languages
function generateStarterCodeForLanguages(languages) {
  if (!languages || languages.length === 0) {
    return '';
  }

  if (languages.length === 1) {
    return getDefaultTemplate(languages[0]);
  }

  // For multiple languages, show templates for all
  const langLabels = LANG_OPTIONS.reduce((acc, opt) => ({ ...acc, [opt.value]: opt.label }), {});
  return languages.map(lang => {
    const label = langLabels[lang] || lang;
    return `// === ${label} ===\n${getDefaultTemplate(lang)}`;
  }).join('\n\n');
}

const getEmptyForm = () => {
  // Start with no languages selected - user will select which ones they want
  return {
    title: '',
    description: '',
    language: '',
    languages: [],
    difficulty: 'easy',
    mode: 'full_program',
    starter_code: '',
    schema_sql: '',
    database_engine: 'postgres',
    time_limit_ms: null,
    memory_limit_mb: 256,
    created_by_email: '',
    organization_name_snapshot: '',
    custom_assessment_id: null,
    is_active: true,
  };
};

const emptyForm = getEmptyForm();

function getStoredUser() {
  try {
    const raw = localStorage.getItem('user');
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function getOrgFromUser(user) {
  if (!user) return '';
  return (user.organization_name || user.organizationName || '').trim();
}

function getEmailFromUser(user) {
  if (!user) return '';
  return (user.email || '').trim();
}


function msToHHMMSS(ms) {
  const totalSeconds = Math.max(0, Math.floor((Number(ms) || 0) / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds].map((v) => String(v).padStart(2, '0')).join(':');
}

function hhmmssToMs(str) {
  if (!str) return null;
  const parts = str.split(':');
  if (parts.length > 3) return null;
  const [h, m = '0', s = '0'] = parts;
  const hours = Number(h || 0);
  const minutes = Number(m || 0);
  const seconds = Number(s || 0);
  if ([hours, minutes, seconds].some((v) => Number.isNaN(v))) return null;
  if (hours > 23) return null;
  if (minutes > 59 || seconds > 59) return null;
  if (hours === 23 && (minutes > 59 || seconds > 59)) return null;
  return (hours * 3600 + minutes * 60 + seconds) * 1000;
}

export default function CodingQuestionForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const editing = Boolean(id);
  const location = useLocation();

  const [loading, setLoading] = useState(Boolean(editing));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);

  const [testcases, setTestcases] = useState([]);
  const [tcStdin, setTcStdin] = useState('');
  const [tcExpected, setTcExpected] = useState('');
  const [tcHidden, setTcHidden] = useState(false);
  const [tcSaving, setTcSaving] = useState(false);
  const [timeInput, setTimeInput] = useState('');
  const [timeError, setTimeError] = useState('');
  const [showLangs, setShowLangs] = useState(false);
  const langsRef = useRef(null);

  const navAssessment = useMemo(() => location.state || null, [location.state]);

  // Click outside to close language menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (langsRef.current && !langsRef.current.contains(event.target)) {
        setShowLangs(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const normalizeLanguages = useCallback((value, fallbackLanguage) => {
    const arr = Array.isArray(value) ? value : value ? [value] : [];
    const cleaned = arr
      .map((v) => (v || '').toString().trim().toLowerCase())
      .filter((v) => LANG_OPTIONS.some((opt) => opt.value === v));

    const normalized = cleaned.filter((v, idx) => cleaned.indexOf(v) === idx);
    // If we have a fallback and the result is empty, use it.
    // BUT only if fallback is valid.
    if (normalized.length === 0 && fallbackLanguage) {
      // Check if fallback is valid option to prevent phantom languages
      const isFallbackValid = LANG_OPTIONS.some(o => o.value === fallbackLanguage);
      if (isFallbackValid) return [fallbackLanguage];
    }
    return normalized;
  }, []);

  const load = useCallback(async () => {
    if (!editing) return;
    setLoading(true);
    setError('');
    try {
      const resp = await axios.get(`${API_BASE_URL}/coding/questions/${id}/`);
      const langs = normalizeLanguages(resp.data?.languages, resp.data?.language || DEFAULT_LANGS[0]);
      setForm({
        ...emptyForm,
        ...resp.data,
        languages: langs,
        language: langs[0] || resp.data?.language || DEFAULT_LANGS[0],
      });
      setTimeInput(resp.data?.time_limit_ms != null ? msToHHMMSS(resp.data.time_limit_ms) : '');
      setTimeInput(resp.data?.time_limit_ms != null ? msToHHMMSS(resp.data.time_limit_ms) : '');
      setTimeError('');
      const tcs = await axios.get(`${API_BASE_URL}/coding/questions/${id}/testcases/`);
      const results = tcs.data?.results || [];
      setTestcases(results);
      setTcHidden(results.length >= 2);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to load question');
    } finally {
      setLoading(false);
    }
  }, [editing, id, normalizeLanguages]);

  useEffect(() => {
    if (editing) {
      load();
    } else if (navAssessment?.customAssessmentId) {
      // snapshot only; no joins
      setForm((prev) => ({ ...prev, custom_assessment_id: navAssessment.customAssessmentId }));
    }
  }, [editing, load, navAssessment?.customAssessmentId]);

  // Prefill company/email snapshot for new questions based on stored user profile
  useEffect(() => {
    if (editing) return;
    const user = getStoredUser();
    const orgName = getOrgFromUser(user);
    const email = getEmailFromUser(user);
    if (!orgName && !email) return;
    setForm((prev) => ({
      ...prev,
      created_by_email: prev.created_by_email || email,
      organization_name_snapshot: prev.organization_name_snapshot || orgName,
    }));
  }, [editing]);


  const update = (k, v) => setForm((prev) => ({ ...prev, [k]: v }));

  const handleTimeChange = (e) => {
    let val = e.target.value.replace(/\D/g, '');
    if (val.length > 6) val = val.slice(0, 6);

    let formatted = val;
    if (val.length >= 5) {
      formatted = `${val.slice(0, 2)}:${val.slice(2, 4)}:${val.slice(4)}`;
    } else if (val.length >= 3) {
      formatted = `${val.slice(0, 2)}:${val.slice(2)}`;
    }

    setTimeInput(formatted);
    if (!formatted) {
      setTimeError('');
      update('time_limit_ms', null);
      return;
    }

    const ms = hhmmssToMs(formatted);
    if (ms == null) {
      setTimeError('Invalid time (max 23:59:59)');
      update('time_limit_ms', null);
    } else {
      setTimeError('');
      update('time_limit_ms', ms);
    }
  };

  const toggleLanguage = (lang) => {
    setForm((prev) => {
      let next;
      // SQL Exclusivity Logic
      if (lang === 'sql') {
        const wasSelected = (prev.languages || []).includes('sql');
        // If it was selected, deselect it (empty). If not, select ONLY sql.
        next = wasSelected ? [] : ['sql'];
      } else {
        // Toggle normal language
        const wasSelected = (prev.languages || []).includes(lang);
        if (wasSelected) {
          next = prev.languages.filter((l) => l !== lang);
        } else {
          // If selecting a non-sql language, make sure we remove 'sql' from the list if present
          next = [...(prev.languages || []).filter(l => l !== 'sql'), lang];
        }
      }

      // Only show templates for currently selected languages (no default fallback)
      const newStarterCode = next.length > 0 ? generateStarterCodeForLanguages(next) : '';
      return {
        ...prev,
        languages: next,
        language: next.length > 0 ? next[0] : prev.language || '',
        starter_code: newStarterCode,
      };
    });
  };



  // Auto-populate starter code when languages change (for new questions only)
  useEffect(() => {
    if (editing) return; // Don't auto-populate when editing existing question
    const langs = normalizeLanguages(form.languages, form.language);
    // Only update if languages are actually selected
    if (langs.length > 0) {
      const newStarterCode = generateStarterCodeForLanguages(langs);
      setForm((prev) => {
        // Update starter code to show only templates for currently selected languages
        return { ...prev, starter_code: newStarterCode };
      });
    } else {
      // If no languages selected, clear starter code
      setForm((prev) => {
        if (prev.starter_code && prev.starter_code.trim() !== '') {
          // Only clear if it was auto-generated (contains template markers)
          const hasTemplateMarkers = prev.starter_code.includes('// ===') || prev.starter_code.includes('// Your code here');
          if (hasTemplateMarkers) {
            return { ...prev, starter_code: '' };
          }
        }
        return prev;
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.languages, editing]);

  const save = async ({ redirectTo } = {}) => {
    setSaving(true);
    setError('');
    try {
      if (timeError) {
        setSaving(false);
        return;
      }
      if (!timeInput || form.time_limit_ms == null) {
        setTimeError('Enter time as HH:MM:SS');
        setSaving(false);
        return;
      }
      const langs = normalizeLanguages(form.languages, form.language || DEFAULT_LANGS[0]);
      if (!langs.length) {
        setError('Please select at least one language');
        setSaving(false);
        return;
      }

      const user = getStoredUser();
      const orgName = getOrgFromUser(user);
      const email = getEmailFromUser(user);

      const payload = {
        ...form,
        languages: langs,
        language: langs[0],
        created_by_email: form.created_by_email || email,
        organization_name_snapshot: form.organization_name_snapshot || orgName,
      };
      let targetId = id;
      let questionPayload = null;
      if (editing) {
        await axios.put(`${API_BASE_URL}/coding/questions/${id}/`, payload);
        targetId = id;
        if (redirectTo) {
          const detail = await axios.get(`${API_BASE_URL}/coding/questions/${targetId}/`);
          questionPayload = detail.data;
        }
      } else {
        const resp = await axios.post(`${API_BASE_URL}/coding/questions/`, payload);
        targetId = resp.data?.id;
        if (redirectTo) {
          const detail = await axios.get(`${API_BASE_URL}/coding/questions/${targetId}/`);
          questionPayload = detail.data;
        }
        if (!redirectTo) {
          navigate(`/coding/questions/${targetId}/edit`, { state: navAssessment });
          return;
        }
      }

      if (redirectTo === '/review-assessment') {
        navigate('/review-assessment', { state: { ...(navAssessment || {}), refreshManual: true, codingQuestions: questionPayload ? [questionPayload] : [] } });
      } else if (redirectTo) {
        navigate(redirectTo, { state: { codingQuestions: questionPayload ? [questionPayload] : [] } });
      } else if (editing) {
        await load();
      }
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to save question');
    } finally {
      setSaving(false);
    }
  };

  const addTestcase = async () => {
    if (!editing) {
      setError('Save the question first, then add testcases.');
      return;
    }
    setTcSaving(true);
    setError('');
    try {
      await axios.post(`${API_BASE_URL}/coding/questions/${id}/testcases/`, {
        stdin: tcStdin,
        expected_stdout: tcExpected,
        is_hidden: tcHidden,
      });
      setTcStdin('');
      setTcExpected('');
      const tcs = await axios.get(`${API_BASE_URL}/coding/questions/${id}/testcases/`);
      const newList = tcs.data?.results || [];
      setTestcases(newList);
      setTcHidden(newList.length >= 2);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to add testcase');
    } finally {
      setTcSaving(false);
    }
  };

  const deleteTestcase = async (testcaseId) => {
    if (!editing) return;
    setError('');
    try {
      await axios.delete(`${API_BASE_URL}/coding/testcases/${testcaseId}/`);
      setTestcases((prev) => {
        const after = prev.filter((t) => t.id !== testcaseId);
        setTcHidden(after.length >= 2);
        return after;
      });
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to delete testcase');
    }
  };

  return (
    <div className="coding-container">
      <Header />
      <div className="page-container coding-form-page">
        <div className="coding-header-row">
          <div>
            <h2 className="page-title">{editing ? `Edit Question` : 'New Coding Question'}</h2>
            <div className="coding-muted">
              {editing ? `Updating question #${id}` : 'Create a robust coding challenge with testcases.'}
            </div>
          </div>
          <div className="coding-header-actions">
            <button type="button" className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }} onClick={() => {
              if (location.pathname === '/coding-challenge-question' || navAssessment) {
                navigate('/manual-questions', { state: navAssessment });
              } else {
                navigate('/coding');
              }
            }}>
              <ArrowLeft size={18} />
              Back
            </button>
            {editing && (
              <button type="button" className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }} onClick={() => navigate(`/coding/questions/${id}/attempt`)}>
                <ExternalLink size={18} />
                Preview
              </button>
            )}
            <button type="button" className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }} onClick={() => save()} disabled={saving || loading}>
              <Save size={18} />
              {saving ? 'Saving…' : 'Save Question'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="coding-card">Loading…</div>
        ) : (
          <>
            {error && <div className="coding-card coding-error">{error}</div>}

            <div className="coding-card">
              <div className="coding-form-grid">
                <label className="coding-field coding-field-short">
                  <div className="coding-label"><FileText size={16} style={{marginRight: '6px'}}/> Title *</div>
                  <input value={form.title} onChange={(e) => update('title', e.target.value)} className="coding-input" style={{ height: '48px' }} placeholder="Question title" />
                </label>

                <label className="coding-field coding-field-short">
                  <div className="coding-label"><Languages size={16} style={{marginRight: '6px'}}/> Languages *</div>
                  <div className="coding-multiselect" ref={langsRef}>
                    <div
                      className="coding-multiselect-trigger"
                      style={{ height: '48px' }}
                      onClick={() => setShowLangs(!showLangs)}
                    >
                      {form.languages.length === 0 ? (
                        <span className="coding-muted">Select Languages...</span>
                      ) : (
                        <div className="coding-selected-tags">
                          {form.languages.map(lang => {
                            const opt = LANG_OPTIONS.find(o => o.value === lang);
                            return (
                              <span key={lang} className="coding-selected-tag">
                                {opt ? opt.label : lang}
                              </span>
                            );
                          })}
                        </div>
                      )}
                      <span className="coding-trigger-arrow">{showLangs ? '▴' : '▾'}</span>
                    </div>

                    {showLangs && (
                      <div className="coding-multiselect-menu">
                        {LANG_OPTIONS.map((opt) => {
                          const checked = (form.languages || []).includes(opt.value);
                          return (
                            <label key={opt.value} className="coding-checkbox-pill">
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => toggleLanguage(opt.value)}
                              />
                              <span>{opt.label}</span>
                            </label>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </label>

                <label className="coding-field coding-field-short">
                  <div className="coding-label"><TrendingUp size={16} style={{marginRight: '6px'}}/> Difficulty Level *</div>
                  <select
                    value={form.difficulty || 'easy'}
                    onChange={(e) => update('difficulty', e.target.value)}
                    className="coding-input"
                    style={{ height: '48px' }}
                    required
                  >
                    {DIFFICULTY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                  <div className="coding-help-text" style={{ fontSize: '0.8rem', color: '#666', marginTop: '4px' }}>
                    Weights: Easy=1x, Medium=2x, Hard=3x
                  </div>
                </label>

                <label className="coding-field coding-field-wide">
                  <div className="coding-label"><AlignLeft size={16} style={{marginRight: '6px'}}/> Description</div>
                  <textarea value={form.description || ''} onChange={(e) => update('description', e.target.value)} className="coding-textarea" rows={4} />
                </label>

                <label className="coding-field coding-field-wide">
                  <div className="coding-label"><Code size={16} style={{marginRight: '6px'}}/> Starter code (editor default)</div>
                  <textarea value={form.starter_code || ''} onChange={(e) => update('starter_code', e.target.value)} className="coding-textarea" rows={8} />
                </label>

                {/* SQL Specific Fields */}
                {(form.languages || []).includes('sql') && (
                  <>
                    <label className="coding-field coding-field-short">
                      <div className="coding-label"><Database size={16} style={{marginRight: '6px'}}/> Database Engine</div>
                      <select
                        value={form.database_engine || 'postgres'}
                        onChange={(e) => update('database_engine', e.target.value)}
                        className="coding-input"
                        style={{ height: '48px' }}
                      >
                        <option value="postgres">PostgreSQL</option>
                        <option value="mysql">MySQL</option>
                        <option value="sqlite">SQLite</option>
                      </select>
                    </label>

                    <label className="coding-field coding-field-wide">
                      <div className="coding-label"><Database size={16} style={{marginRight: '6px'}}/> Schema SQL (Setup command)</div>
                      <div className="coding-help-text" style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '8px' }}>
                        Define tables and insert initial data. Runs before each test case.
                      </div>
                      <textarea
                        value={form.schema_sql || ''}
                        onChange={(e) => update('schema_sql', e.target.value)}
                        className="coding-textarea"
                        rows={8}
                        placeholder={`CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);\nINSERT INTO users (name) VALUES ('Alice');\n\n\nNOTE:Please avoid writing comments in the SQL schema section.`}
                      />
                    </label>
                  </>
                )}

                <label className="coding-field coding-field-short">
                  <div className="coding-label"><Hash size={16} style={{marginRight: '6px'}}/> Custom Assessment ID</div>
                  <input
                    value={form.custom_assessment_id ?? ''}
                    onChange={(e) => update('custom_assessment_id', e.target.value ? Number(e.target.value) : null)}
                    className="coding-input"
                    style={{ height: '48px' }}
                    placeholder="optional snapshot id"
                  />
                </label>
              </div>
            </div>

            <div className="coding-card">
              <div className="coding-form-grid">
                <label className="coding-field coding-field-short">
                  <div className="coding-label"><Timer size={16} style={{marginRight: '6px'}}/> Time limit (HH:MM:SS) *</div>
                  <input
                    type="text"
                    value={timeInput}
                    onChange={handleTimeChange}
                    placeholder="00:00:00"
                    maxLength={8}
                    className="coding-input"
                    style={{ height: '48px' }}
                    required
                  />
                  {timeError && (
                    <div style={{ color: 'red', fontSize: '0.9rem', marginTop: '4px' }}>
                      {timeError}
                    </div>
                  )}
                </label>

                <label className="coding-field coding-field-short">
                  <div className="coding-label"><Cpu size={16} style={{marginRight: '6px'}}/> Memory (MB) *</div>
                  <input
                    type="number"
                    value={form.memory_limit_mb}
                    onChange={(e) => update('memory_limit_mb', Number(e.target.value))}
                    className="coding-input"
                    style={{ height: '48px' }}
                    min={32}
                    required
                  />
                </label>

                <label className="coding-field coding-field-short">
                  <div className="coding-label"><ShieldCheck size={16} style={{marginRight: '6px'}}/> Active Status *</div>
                  <select 
                    value={form.is_active ? 'yes' : 'no'} 
                    onChange={(e) => update('is_active', e.target.value === 'yes')} 
                    className="coding-input" 
                    style={{ height: '48px' }}
                    required
                  >
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                  </select>
                </label>
              </div>
            </div>

            <div className="coding-card">
              <div className="coding-section-title">Test Cases</div>

              {!editing ? (
                <div className="coding-muted">Save the question to add testcases.</div>
              ) : (
                <>
                  <div className="coding-form-grid">
                    {/* Hide stdin for SQL questions as requested */}
                    {form.language !== 'sql' && (
                      <label className="coding-field coding-field-wide">
                        <div className="coding-label">stdin</div>
                        <textarea value={tcStdin} onChange={(e) => setTcStdin(e.target.value)} className="coding-textarea" rows={4} />
                      </label>
                    )}
                    <label className="coding-field coding-field-wide">
                      <div className="coding-label">expected stdout</div>
                      <textarea value={tcExpected} onChange={(e) => setTcExpected(e.target.value)} className="coding-textarea" rows={4} />
                    </label>
                    <label className="coding-field coding-field-short">
                      <div className="coding-label"><Eye size={16} style={{marginRight: '6px'}}/> Test Case Visibility</div>
                      <select 
                        value={tcHidden ? 'yes' : 'no'} 
                        onChange={(e) => setTcHidden(e.target.value === 'yes')} 
                        className="coding-input"
                        style={{ height: '48px' }}
                      >
                        <option value="no">Visible(Sample)</option>
                        <option value="yes">Hidden</option>
                      </select>
                    </label>
                    <div className="coding-field">
                      <div className="coding-label">&nbsp;</div>
                      <button 
                        type="button" 
                        className="btn btn-primary" 
                        style={{ display: 'flex', alignItems: 'center', gap: '8px', height: '48px' }} 
                        onClick={addTestcase} 
                        disabled={tcSaving}
                      >
                        <Plus size={18} />
                        {tcSaving ? 'Adding…' : 'Add Testcase'}
                      </button>
                    </div>
                  </div>

                  {testcases.length === 0 ? (
                    <div className="coding-muted" style={{ marginTop: '20px' }}>No testcases yet.</div>
                  ) : (
                    <div className={`coding-table ${form.language === 'sql' ? 'is-sql' : ''}`} style={{ marginTop: '32px' }}>
                      <div className="coding-table-head">
                        <div>ID</div>
                        <div>Visibility</div>
                        {form.language !== 'sql' && <div>stdin</div>}
                        <div>expected</div>
                        <div style={{ textAlign: 'right' }}>Actions</div>
                      </div>
                      {testcases.map((tc) => (
                        <div key={tc.id} className="coding-table-row">
                          <div>{tc.id}</div>
                          <div>
                            <span className={tc.is_hidden ? 'coding-pill-hidden' : 'coding-pill-visible'}>
                              {tc.is_hidden ? 'Hidden' : 'Visible(Sample)'}
                            </span>
                          </div>
                          {form.language !== 'sql' && <div className="coding-mono">{tc.stdin || '—'}</div>}
                          <div className="coding-mono">{tc.expected_stdout || '—'}</div>
                          <div style={{ textAlign: 'right' }}>
                            <button type="button" className="btn btn-secondary" onClick={() => deleteTestcase(tc.id)}>
                              Delete
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
