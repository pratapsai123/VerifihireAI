import React, { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/Coding.css';
import '../styles/CodingAttempt.css';
import { API_BASE_URL } from '../apiConfig';
import { Eye, EyeOff } from 'lucide-react';

const DEFAULT_LANGS = [
  'cpp',
  'java',
  'python3',
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
];

const MonacoEditor = React.lazy(() => import('@monaco-editor/react'));

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
  };
  return templates[lang] || '// Your code here';
}

// Extract template for a specific language from multi-language starter code
function extractLanguageTemplate(starterCode, lang) {
  if (!starterCode || !starterCode.trim()) {
    return getDefaultTemplate(lang);
  }

  // Check if starter code contains multiple language templates (has "// ===" markers)
  if (starterCode.includes('// ===')) {
    // Try to find the specific language's template
    const langLabels = {
      'cpp': 'C\\+\\+',
      'java': 'Java',
      'python3': 'Python3',
      'python': 'Python',
      'javascript': 'JavaScript',
      'typescript': 'TypeScript',
      'csharp': 'C#',
      'c': 'C',
      'go': 'Go',
      'kotlin': 'Kotlin',
      'swift': 'Swift',
      'rust': 'Rust',
      'ruby': 'Ruby',
      'php': 'PHP',
      'dart': 'Dart',
      'scala': 'Scala',
    };

    const langLabel = langLabels[lang] || lang;
    // Match: // === Language === followed by content until next // === or end
    const regex = new RegExp(`//\\s*===\\s*${langLabel}\\s*===\\s*\\n([\\s\\S]*?)(?=\\n\\n\\s*//\\s*===|$)`, 'i');
    const match = starterCode.match(regex);

    if (match && match[1]) {
      return match[1].trim();
    }

    // If not found in multi-language format, return default template
    return getDefaultTemplate(lang);
  }

  // If starter code doesn't have language markers, return it as-is (might be single language)
  return starterCode;
}

function monacoLanguage(lang) {
  switch ((lang || '').toLowerCase()) {
    case 'python':
      return 'python';
    case 'python3':
      return 'python';
    case 'javascript':
      return 'javascript';
    case 'typescript':
      return 'typescript';
    case 'java':
      return 'java';
    case 'c':
      return 'c';
    case 'cpp':
      return 'cpp';
    case 'csharp':
      return 'csharp';
    case 'go':
      return 'go';
    case 'kotlin':
      return 'kotlin';
    case 'swift':
      return 'swift';
    case 'rust':
      return 'rust';
    case 'ruby':
      return 'ruby';
    case 'php':
      return 'php';
    case 'dart':
      return 'dart';
    case 'scala':
      return 'scala';
    case 'sql':
      return 'sql';
    default:
      return 'plaintext';
  }
}

function normalizeRunResult(data) {
  const cleaned = { ...data };
  // Runs should not surface submission metadata
  if ('submission_id' in cleaned) delete cleaned.submission_id;
  return cleaned;
}

function formatDuration(ms) {
  const totalSeconds = Math.max(0, Math.floor((ms || 0) / 1000));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const pad = (n) => String(n).padStart(2, '0');
  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

export default function CodingAttempt() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [q, setQ] = useState(null);
  const [code, setCode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [lastAction, setLastAction] = useState('run'); // 'run' | 'submit'
  const [isLeftCollapsed, setIsLeftCollapsed] = useState(false);
  const [leftWidth, setLeftWidth] = useState(44);
  const [lastExpandedWidth, setLastExpandedWidth] = useState(44);
  const [isDragging, setIsDragging] = useState(false);
  const [showResultPanel, setShowResultPanel] = useState(true);
  const [resultHeightPct, setResultHeightPct] = useState(30); // percent of right pane
  const [isResultDragging, setIsResultDragging] = useState(false);
  const resultRef = useRef(null);
  const shellRef = useRef(null);
  const editorWrapRef = useRef(null);
  const languages = useMemo(() => {
    const arr = Array.isArray(q?.languages) ? q.languages : [];
    const uniq = arr.filter((v, idx) => arr.indexOf(v) === idx && v);
    return uniq.length > 0 ? uniq : DEFAULT_LANGS;
  }, [q?.languages]);
  const [selectedLanguage, setSelectedLanguage] = useState(() => languages[0]);
  useEffect(() => {
    setSelectedLanguage((prev) => {
      if (prev && languages.includes(prev)) return prev;
      return languages[0];
    });
  }, [languages]);
  const editorLanguage = useMemo(() => monacoLanguage(selectedLanguage), [selectedLanguage]);

  // Update code when language changes - show only that language's template
  useEffect(() => {
    if (!q || !selectedLanguage) return;

    const starterCode = q.starter_code || '';
    const langSpecificCode = extractLanguageTemplate(starterCode, selectedLanguage);

    // Check if current code is still a template (hasn't been significantly edited)
    const currentCode = code.trim();
    const isStillTemplate = currentCode === '' ||
      currentCode.includes('// Your code here') ||
      currentCode.includes('# Your code here') ||
      currentCode.includes('// ===') || // Multi-language template
      currentCode === starterCode || // Still showing all languages
      currentCode === langSpecificCode; // Already showing this language

    // Always update when language changes if code is still template-like
    if (isStillTemplate) {
      setCode(langSpecificCode);
    }
  }, [selectedLanguage, q]);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await axios.get(`${API_BASE_URL}/coding/questions/${id}/`);
      setQ(resp.data);

      // Get available languages
      const availableLangs = Array.isArray(resp.data?.languages) && resp.data.languages.length > 0
        ? resp.data.languages
        : DEFAULT_LANGS;

      // Initialize with first language
      const firstLang = availableLangs[0];
      const starterCode = resp.data?.starter_code || '';

      // Extract template for the first language only
      const initialCode = extractLanguageTemplate(starterCode, firstLang);
      setCode(initialCode);
      setSelectedLanguage(firstLang);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Failed to load question');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!isDragging) return undefined;

    const handleMove = (e) => {
      if (!shellRef.current) return;
      const rect = shellRef.current.getBoundingClientRect();
      const relativeX = e.clientX - rect.left;
      const pct = (relativeX / rect.width) * 100;
      const clamped = Math.max(18, Math.min(70, pct));
      setLeftWidth(clamped);
      setLastExpandedWidth(clamped);
    };

    const handleUp = () => setIsDragging(false);

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [isDragging]);

  useEffect(() => {
    if (!isResultDragging) return undefined;

    const handleMove = (e) => {
      if (!editorWrapRef.current) return;
      const rect = editorWrapRef.current.getBoundingClientRect();
      const relativeY = e.clientY - rect.top;
      const pctBottom = ((rect.height - relativeY) / rect.height) * 100;
      const clamped = Math.max(15, Math.min(70, pctBottom));
      setResultHeightPct(clamped);
    };

    const handleUp = () => setIsResultDragging(false);

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseup', handleUp);
    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseup', handleUp);
    };
  }, [isResultDragging]);

  const run = async () => {
    setIsRunning(true);
    setError('');
    setResult(null);
    setLastAction('run');
    setResultHeightPct(50); // Expand results area upon running
    try {
      const resp = await axios.post(`${API_BASE_URL}/coding/questions/${id}/run/?mode=visible`, {
        code,
        mode: 'visible',
        language: selectedLanguage,
      });
      setResult(normalizeRunResult(resp.data));
      setTimeout(() => {
        if (resultRef.current) {
          resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }, 0);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Run failed');
    } finally {
      setIsRunning(false);
    }
  };

  const submit = async () => {
    setIsSubmitting(true);
    setError('');
    setResult(null);
    setLastAction('submit');
    setResultHeightPct(50); // Expand results area upon submitting
    try {
      const resp = await axios.post(`${API_BASE_URL}/coding/questions/${id}/submit/`, { code, language: selectedLanguage });
      setResult(resp.data);
      setTimeout(() => {
        if (resultRef.current) {
          resultRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }, 0);
    } catch (e) {
      setError(e?.response?.data?.error || e?.message || 'Submit failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    if (result) {
      setShowResultPanel(true);
    }
  }, [result]);

  const toggleLeftPane = () => {
    if (isLeftCollapsed) {
      setIsLeftCollapsed(false);
      setLeftWidth(lastExpandedWidth || 40);
    } else {
      setLastExpandedWidth(leftWidth);
      setIsLeftCollapsed(true);
    }
  };

  const startDrag = (e) => {
    if (isLeftCollapsed) return;
    setIsDragging(true);
    e.preventDefault();
  };

  const leftPaneStyle = isLeftCollapsed
    ? { flex: '0 0 34px', minWidth: '34px' }
    : { flex: `0 0 ${leftWidth}%`, minWidth: '260px' };

  const toggleResultPanel = () => {
    setShowResultPanel((v) => !v);
  };

  const startResultDrag = (e) => {
    if (!showResultPanel || !result) return;
    setIsResultDragging(true);
    e.preventDefault();
  };

  const resultPaneStyle = showResultPanel && result
    ? { flex: '0 0 auto', display: 'block' }
    : { display: 'none' };

  return (
    <div className="coding-container">
      <Header />
      {loading ? (
        <div className="page-container">
          <div className="coding-card">Loading…</div>
        </div>
      ) : error ? (
        <div className="page-container">
          <div className="coding-card coding-error">{error}</div>
        </div>
      ) : (
        <div className="coding-attempt-shell" ref={shellRef}>
          {/* Left: Problem statement */}
          <div
            className={`coding-pane coding-pane-left ${isLeftCollapsed ? 'is-collapsed' : ''}`}
            style={leftPaneStyle}
          >
            <button
              type="button"
              className="coding-collapse-btn"
              onClick={toggleLeftPane}
              aria-label={isLeftCollapsed ? 'Expand question panel' : 'Collapse question panel'}
            >
              {isLeftCollapsed ? '▶' : '◀'}
            </button>
            {!isLeftCollapsed && (
              <div className="coding-pane-left-content">
                <div className="coding-pane-header">
                  <div>
                    <div className="coding-title">{q?.title || 'Untitled'}</div>
                    <div className="coding-meta">
                      {languages.length === 0 ? (
                        <span className="coding-pill coding-pill-muted">—</span>
                      ) : (
                        languages.map((lang) => (
                          <span key={lang} className="coding-pill coding-pill-muted">
                            {lang}
                          </span>
                        ))
                      )}
                      <span className="coding-pill coding-pill-muted">{q?.mode || '—'}</span>
                    </div>
                  </div>
                  <div className="coding-toolbar">
                    <button type="button" className="btn btn-secondary" onClick={() => navigate('/coding')}>
                      Back
                    </button>
                  </div>
                </div>
                <div className="coding-pane-body">
                  <div className="coding-problem">{q?.description || 'No description provided.'}</div>
                </div>
              </div>
            )}
          </div>

          <div
            className={`coding-resizer ${isDragging ? 'dragging' : ''} ${isLeftCollapsed ? 'disabled' : ''}`}
            onMouseDown={startDrag}
            role="separator"
            aria-label="Resize panels"
            aria-orientation="vertical"
          />

          {/* Right: Editor + actions + results */}
          <div className="coding-pane coding-pane-right">
            <div className="coding-pane-header">
              <div className="coding-title">Code Editor</div>
              <div className="coding-toolbar">
                {languages.length > 0 && (
                  <select
                    className="coding-input coding-language-select"
                    value={selectedLanguage || ''}
                    onChange={(e) => {
                      const newLang = e.target.value;
                      setSelectedLanguage(newLang);
                      // Immediately update code to show only selected language's template
                      if (q) {
                        const starterCode = q.starter_code || '';
                        const langSpecificCode = extractLanguageTemplate(starterCode, newLang);
                        setCode(langSpecificCode);
                      }
                    }}
                  >
                    {languages.map((lang) => (
                      <option key={lang} value={lang}>
                        {lang}
                      </option>
                    ))}
                  </select>
                )}
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={toggleResultPanel}
                  disabled={!result}
                >
                  Test Cases
                </button>
                <button type="button" className="btn btn-secondary" onClick={run} disabled={isRunning || isSubmitting || loading}>
                  {isRunning ? 'Running…' : 'Run'}
                </button>
                <button type="button" className="btn btn-primary" onClick={submit} disabled={isSubmitting || isRunning || loading}>
                  {isSubmitting ? 'Submitting…' : 'Submit'}
                </button>
              </div>
            </div>

            <div className="coding-editor-wrap" ref={editorWrapRef} onClick={() => setResultHeightPct(30)}>
              <div className="coding-monaco">
                <Suspense fallback={<div className="coding-monaco-loading">Loading editor…</div>}>
                  <MonacoEditor
                    height="100%"
                    defaultLanguage={editorLanguage}
                    language={editorLanguage}
                    value={code}
                    onChange={(v) => setCode(v ?? '')}
                    theme="vs-dark"
                    options={{
                      fontSize: 13,
                      minimap: { enabled: false },
                      automaticLayout: true,
                      scrollBeyondLastLine: false,
                      wordWrap: 'on',
                    }}
                  />
                </Suspense>
              </div>

              {result && (
                <div
                  className={`coding-horizontal-resizer ${isResultDragging ? 'dragging' : ''} ${!showResultPanel ? 'disabled' : ''}`}
                  onMouseDown={startResultDrag}
                  role="separator"
                  aria-label="Resize editor and test cases"
                  aria-orientation="horizontal"
                />
              )}

              {result && (
                <div className="coding-result" ref={resultRef} style={resultPaneStyle}>
                  {result.results ? (
                    <>
                      <div className="coding-result-summary">
                        Status: <b>{result.status}</b> • Passed: <b>{result.passed_count}</b> / {result.total_tests} • Time:{' '}
                        {formatDuration(result.execution_time_ms)}{' '}
                        {lastAction === 'submit' && result.submission_id ? `• Submission #${result.submission_id}` : ''}
                        {lastAction === 'run' ? ' • (visible tests only)' : ''}
                      </div>
                      <div className={`coding-table is-results ${!(result.results || []).some(r => (r.stderr || '').trim()) ? 'hide-stderr' : ''}`}>
                        <div className="coding-table-head">
                          <div>Test</div>
                          <div>Status</div>
                          <div>stdout</div>
                          {(result.results || []).some(r => (r.stderr || '').trim()) && <div>stderr</div>}
                        </div>
                        {result.results.map((r, idx) => {
                          const isHidden = r.is_hidden ?? r.hidden ?? false;
                          return (
                            <div key={r.testcase_id ?? idx} className="coding-table-row">
                            <div className="coding-test-label" title={isHidden ? 'Hidden Test' : 'Visible Test'}>
                              {isHidden ? <EyeOff size={16} color="#64748b" /> : <Eye size={16} color="#22c55e" />}
                              <span className="coding-test-name">{idx + 1}</span>
                            </div>
                              <div className={`coding-status coding-status-${String(r.status || '').toLowerCase()}`}>{r.status}</div>
                              {r.status === 'ERROR' && r.message ? (
                                <div className="coding-mono coding-error-message" style={{ gridColumn: (result.results || []).some(res => (res.stderr || '').trim()) ? 'span 2' : 'span 1', color: '#ff6b6b' }}>
                                  {r.message}
                                </div>
                              ) : (
                                <>
                                  <div className="coding-mono">{(r.stdout || '').trim() || '—'}</div>
                                  {(result.results || []).some(res => (res.stderr || '').trim()) && <div className="coding-mono">{(r.stderr || '').trim() || '—'}</div>}
                                </>
                              )}
                            </div>

                          );
                        })}
                      </div>
                    </>
                  ) : (
                    <pre className="coding-mono">{JSON.stringify(result, null, 2)}</pre>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}



