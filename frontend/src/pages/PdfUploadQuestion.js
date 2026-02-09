import React, { useMemo, useState } from 'react';
import { flushSync } from 'react-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/PdfUploadQuestion.css';

// Django API base URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';

function PdfUploadQuestion() {
  const navigate = useNavigate();
  const location = useLocation();
  const assessmentContext = location.state || null;

  const assessmentOptions = [
    'Python',
    'Java',
    'Java Full Stack',
    'Python Full Stack',
    'JavaScript',
    'TypeScript',
    'Frontend Development',
    'Backend Development',
    'Full Stack (MERN)',
    'Full Stack (MEAN)',
    'React',
    'Angular',
    'Vue.js',
    'Node.js',
    '.NET',
    'C#',
    'C++',
    'Go',
    'PHP',
    'Ruby on Rails',
    'Mobile Development',
    'Android',
    'iOS',
    'React Native',
    'Flutter',
    'DevOps',
    'AWS',
    'Azure',
    'GCP',
    'Kubernetes',
    'Data Engineering',
    'Data Science',
    'Machine Learning',
    'AI / GenAI',
    'Cyber Security',
    'QA Manual',
    'QA Automation',
    'Salesforce',
    'SAP',
    'Power BI',
    'Tableau',
    'UI/UX Design',
    'Product Management',
    'Business Analyst',
  ];

  const [assessmentName, setAssessmentName] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [topicSkill, setTopicSkill] = useState(''); // optional default topic if missing in PDF
  const [file, setFile] = useState(null);
  const [parsedQuestions, setParsedQuestions] = useState([]);
  const [parseErrors, setParseErrors] = useState([]);
  const [isParsing, setIsParsing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const canParse = Boolean(file) && Boolean(assessmentContext?.customAssessmentId);

  const stats = useMemo(() => {
    const counts = { MCQ: 0, MSQ: 0, TF: 0, UNKNOWN: 0 };
    parsedQuestions.forEach((q) => {
      if (q.question_type === 'MCQ') counts.MCQ += 1;
      else if (q.question_type === 'MSQ') counts.MSQ += 1;
      else if (q.question_type === 'TF') counts.TF += 1;
      else counts.UNKNOWN += 1;
    });
    return counts;
  }, [parsedQuestions]);

  const formatCorrectAnswer = (q) => {
    if (!q) return 'N/A';
    if (q.question_type === 'MSQ') {
      return (q.correct_answers || []).join(', ') || 'N/A';
    }
    if (q.question_type === 'TF') {
      const ca = (q.correct_answer || '').toString().trim().toUpperCase();
      if (ca === 'A') return q.option_a || 'True';
      if (ca === 'B') return q.option_b || 'False';
      if (ca === 'TRUE') return 'True';
      if (ca === 'FALSE') return 'False';
      return q.correct_answer || 'N/A';
    }
    return q.correct_answer || 'N/A';
  };

  const resetAll = () => {
    setAssessmentName('');
    setExperienceLevel('');
    setTopicSkill('');
    setFile(null);
    setParsedQuestions([]);
    setParseErrors([]);
  };

  const handleCancel = () => {
    // eslint-disable-next-line no-alert
    const confirmed = window.confirm('Are you sure you want to erase all entered data?');
    if (!confirmed) return;
    flushSync(() => {
      resetAll();
    });
  };

  const handleBack = () => {
    flushSync(() => {
      resetAll();
    });
    navigate('/manual-questions', { replace: true, state: assessmentContext });
  };

  const handleFileChange = (e) => {
    const f = e.target.files?.[0] || null;
    setFile(f);
    setParsedQuestions([]);
    setParseErrors([]);
  };

  const handleParse = async () => {
    if (!assessmentContext?.customAssessmentId) {
      // eslint-disable-next-line no-alert
      alert('Custom assessment ID not found. Please go back to Review page and try again.');
      return;
    }
    if (!file) {
      // eslint-disable-next-line no-alert
      alert('Please select a PDF file.');
      return;
    }
    if (!assessmentName) {
      // eslint-disable-next-line no-alert
      alert('Please select Assessment name.');
      return;
    }
    if (!experienceLevel) {
      // eslint-disable-next-line no-alert
      alert('Please select Experience Level.');
      return;
    }

    try {
      setIsParsing(true);
      setParseErrors([]);
      setParsedQuestions([]);

      const form = new FormData();
      form.append('file', file);
      form.append('assessment', assessmentName);
      form.append('experience_level', experienceLevel);
      if (topicSkill) form.append('topic', topicSkill);

      const resp = await axios.post(`${API_BASE_URL}/questions/parse-document/`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setParsedQuestions(resp.data?.questions || []);
      setParseErrors(resp.data?.errors || []);
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Parse error:', error);
      const message =
        error.response?.data?.error ||
        error.message ||
        'Failed to parse PDF. Please try again.';
      setParseErrors([message]);
    } finally {
      setIsParsing(false);
    }
  };

  const handleSave = async () => {
    if (!assessmentContext?.customAssessmentId) {
      // eslint-disable-next-line no-alert
      alert('Custom assessment ID not found. Please go back to Review page and try again.');
      return;
    }
    if (!parsedQuestions.length) {
      // eslint-disable-next-line no-alert
      alert('No parsed questions to save. Please parse the PDF first.');
      return;
    }

    let userEmail = null;
    let organizationName = null;
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userObj = JSON.parse(storedUser);
        userEmail = (userObj.email || '').toString().trim().toLowerCase() || null;
        organizationName = (userObj.organization_name || userObj.organizationName || '')
          .toString()
          .trim() || null;
      }
    } catch {
      // ignore
    }

    const payload = {
      custom_assessment_id: assessmentContext.customAssessmentId,
      user_email: userEmail,
      organization_name: organizationName,
      questions: parsedQuestions.map((q) => ({
        assessment: q.assessment || assessmentName,
        // Topic is required by backend for saving; if missing in the document, fallback safely.
        topic: q.topic || topicSkill || assessmentName || 'Custom Questions',
        question_type: q.question_type,
        experience_level: experienceLevel,
        question: q.question,
        option_a: q.option_a,
        option_b: q.option_b,
        option_c: q.option_c,
        option_d: q.option_d,
        correct_answer: q.correct_answer,
        correct_answers: q.correct_answers,
        time_to_answer: q.time_to_answer,
      })),
    };

    try {
      setIsSaving(true);
      const resp = await axios.post(`${API_BASE_URL}/questions/bulk-create/`, payload);
      const created = resp.data?.created_count ?? parsedQuestions.length;
      const errors = resp.data?.errors || [];
      // eslint-disable-next-line no-alert
      alert(
        errors.length
          ? `Saved ${created} questions. Some failed to save:\n\n${errors.slice(0, 20).join('\n')}${errors.length > 20 ? '\n...more' : ''}`
          : `Saved ${created} questions successfully.`
      );
      navigate('/review-assessment', { state: assessmentContext });
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Save error:', error);
      const message =
        error.response?.data?.error ||
        error.message ||
        'Failed to save questions. Please try again.';
      // eslint-disable-next-line no-alert
      alert(message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="pdfq-page">
      <Header />
      <div className="pdfq-container">
        <div className="pdfq-card">
          <div className="pdfq-header-row">
            <button
              type="button"
              className="pdfq-back-btn"
              onClick={handleBack}
              aria-label="Go back"
            >
              ← Back
            </button>
            <h1 className="pdfq-title">PDF Uploading</h1>
            <div className="pdfq-actions">
              <button
                type="button"
                className="pdfq-btn pdfq-btn-secondary"
                onClick={handleCancel}
              >
                Cancel
              </button>
              <button
                type="button"
                className="pdfq-btn pdfq-btn-primary"
                onClick={handleSave}
                disabled={isSaving || !parsedQuestions.length}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>

          <div className="pdfq-form">
            <div className="pdfq-inline-row">
              <div>
                <label className="pdfq-field-label" htmlFor="assessmentName">
                  Assessment name<span className="pdfq-required">*</span>
                </label>
                <select
                  id="assessmentName"
                  className="pdfq-select"
                  value={assessmentName}
                  onChange={(e) => setAssessmentName(e.target.value)}
                >
                  <option value="">Select assessment</option>
                  {assessmentOptions.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="pdfq-field-label" htmlFor="experienceLevel">
                  Experience Level<span className="pdfq-required">*</span>
                </label>
                <select
                  id="experienceLevel"
                  className="pdfq-select"
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                >
                  <option value="">Select experience level</option>
                  <option value="entry">Entry Level (0-2 years)</option>
                  <option value="mid">Mid Level (2-5 years)</option>
                  <option value="senior">Senior Level (5-10 years)</option>
                  <option value="expert">Expert Level (10+ years)</option>
                </select>
              </div>

              <div>
                <label className="pdfq-field-label" htmlFor="topicSkill">
                  Default Topic / Skill (optional)
                </label>
                <input
                  id="topicSkill"
                  type="text"
                  className="pdfq-input"
                  placeholder="If PDF doesn't include topic, we use this"
                  value={topicSkill}
                  onChange={(e) => setTopicSkill(e.target.value)}
                />
              </div>
            </div>

            <div className="pdfq-upload-row">
              <div>
                <label className="pdfq-field-label" htmlFor="pdfFile">
                  Upload PDF / Word (.docx)<span className="pdfq-required">*</span>
                </label>
                <input
                  id="pdfFile"
                  type="file"
                  accept="application/pdf,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                  onChange={handleFileChange}
                />
                <p className="pdfq-hint">
                  Format supported: MCQ / MSQ / TF. Use options like A), B), C), D) and a line like
                  “Answer: A” or “Answer: A,C”. For TF use “Answer: True/False” or “Answer: A/B”.
                </p>
              </div>

              <button
                type="button"
                className="pdfq-btn pdfq-btn-secondary"
                onClick={handleParse}
                disabled={isParsing || !canParse || !assessmentName || !experienceLevel}
              >
                {isParsing ? 'Parsing...' : 'Parse PDF'}
              </button>
            </div>

            {parseErrors.length > 0 && (
              <div className="pdfq-error-box">
                <strong>Parse issues:</strong>
                <ul>
                  {parseErrors.map((e, idx) => (
                    <li key={idx}>{e}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="pdfq-stats">
              <span>Parsed: {parsedQuestions.length}</span>
              <span>MCQ: {stats.MCQ}</span>
              <span>MSQ: {stats.MSQ}</span>
              <span>TF: {stats.TF}</span>
            </div>

            {parsedQuestions.length > 0 && (
              <div className="pdfq-preview">
                {parsedQuestions.map((q, idx) => (
                  <div key={idx} className="pdfq-preview-card">
                    <div className="pdfq-preview-header">
                      <span className="pdfq-badge">{q.question_type}</span>
                      <span className="pdfq-preview-index">Q{idx + 1}</span>
                    </div>
                    <div className="pdfq-preview-question">{q.question}</div>
                    <div className="pdfq-preview-options">
                      {q.option_a ? <div><strong>A.</strong> {q.option_a}</div> : null}
                      {q.option_b ? <div><strong>B.</strong> {q.option_b}</div> : null}
                      {q.option_c ? <div><strong>C.</strong> {q.option_c}</div> : null}
                      {q.option_d ? <div><strong>D.</strong> {q.option_d}</div> : null}
                    </div>
                    <div className="pdfq-preview-answer">
                      <strong>Answer:</strong>{' '}
                      {formatCorrectAnswer(q)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PdfUploadQuestion;



