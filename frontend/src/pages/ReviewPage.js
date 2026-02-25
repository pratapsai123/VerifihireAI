import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import '../styles/ReviewPage.css';
import CodingQuestionSelector from '../components/CodingQuestionSelector';
import { API_BASE_URL } from '../apiConfig';
const MANUAL_TOPIC_LABEL = 'Custom Questions';
const REVIEW_STATE_STORAGE_KEY = 'reviewAssessmentState';
const DRAFT_CUSTOM_ASSESSMENT_ID_KEY = 'draftCustomAssessmentId';
const CUSTOM_ASSESSMENT_STORAGE_KEY = 'customAssessmentFormData';

const DIFFICULTY_WEIGHTS = {
  easy: 1,
  medium: 2,
  hard: 3,
};

function ReviewPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [assessmentData, setAssessmentData] = useState(null);
  const [topics, setTopics] = useState([]);
  const [questions, setQuestions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [assessmentName, setAssessmentName] = useState('');
  const [minPassPercentage, setMinPassPercentage] = useState(60);
  const [timeLimit, setTimeLimit] = useState('00:00:00');
  const [isTimeEdited, setIsTimeEdited] = useState(false);
  const [showCodingModal, setShowCodingModal] = useState(false);

  // Split Assessment State
  const [objectiveTime, setObjectiveTime] = useState('00:00:00');
  const [codingTime, setCodingTime] = useState('00:00:00');
  const [hasObjectiveCutoff, setHasObjectiveCutoff] = useState(false);
  const [objPassPercentage, setObjPassPercentage] = useState(60);
  const [objWeight, setObjWeight] = useState(0);
  const [codingWeight, setCodingWeight] = useState(100);
  const [removedQuestionIds, setRemovedQuestionIds] = useState(new Set());

  const totalCodingPoints = useMemo(() => {
    const list = questions['Coding'] || [];
    return list.reduce((sum, q) => {
      const diff = String(q.difficulty || 'medium').toLowerCase();
      const w = DIFFICULTY_WEIGHTS[diff] || 2;
      return sum + (w * 100);
    }, 0);
  }, [questions]);

  // State Persistence Effect
  useEffect(() => {
    if (!loading && assessmentData) {
      const stateToSave = {
        ...assessmentData,
        questions,
        topics,
        assessmentName,
        minPassPercentage,
        timeLimit,
        objectiveTime,
        codingTime,
        hasObjectiveCutoff,
        objPassPercentage,
        removedQuestionIds: Array.from(removedQuestionIds),
        objWeight,
        codingWeight,
      };
      try {
        localStorage.setItem(REVIEW_STATE_STORAGE_KEY, JSON.stringify(stateToSave));
      } catch (e) {
        console.error('Failed to save state to localStorage:', e);
      }
    }
  }, [
    loading,
    assessmentData,
    questions,
    topics,
    assessmentName,
    minPassPercentage,
    timeLimit,
    objectiveTime,
    codingTime,
    hasObjectiveCutoff,
    objPassPercentage,
    objWeight,
    codingWeight,
    removedQuestionIds
  ]);

  // Initial Data Loading & Restoration
  useEffect(() => {
    let state = location.state || null;

    // Always try to restore from localStorage if navigation state is missing or partial
    // This handles page refreshes.
    try {
      const saved = localStorage.getItem(REVIEW_STATE_STORAGE_KEY);
      if (saved) {
        const parsedSaved = JSON.parse(saved);
        // If we have saved state and either no location state OR location state is from a fresh navigation
        // (like coming from CustomAssessment without questions yet populated),
        // we might want to prioritize location state's customAssessmentId but keep our local modifications.
        if (!state) {
          state = parsedSaved;
        } else if (state.customAssessmentId === parsedSaved.customAssessmentId) {
          // Merge: location state often has the source data, but parsedSaved has user edits (removed questions, settings)
          // Ensure we preserve incoming navigation flags like refreshManual
          const incomingRefresh = state.refreshManual;
          state = { ...state, ...parsedSaved };
          if (incomingRefresh) state.refreshManual = incomingRefresh;
        }
      }
    } catch {
      // ignore parse errors
    }

    // If state exists but customAssessmentId is missing, fall back to draft ID
    if (state && !state.customAssessmentId) {
      try {
        const draftId = localStorage.getItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
        const parsed = Number(draftId);
        if (draftId && !Number.isNaN(parsed) && parsed > 0) {
          state = { ...state, customAssessmentId: parsed };
        }
      } catch {
        // ignore
      }
    }

    if (state) {
      // Restore all state fields
      setAssessmentData(state);
      if (state.assessmentName) setAssessmentName(state.assessmentName);
      if (state.minPassPercentage !== undefined) setMinPassPercentage(state.minPassPercentage);
      if (state.timeLimit) setTimeLimit(state.timeLimit);
      if (state.objectiveTime) setObjectiveTime(state.objectiveTime);
      if (state.codingTime) setCodingTime(state.codingTime);
      if (state.hasObjectiveCutoff !== undefined) setHasObjectiveCutoff(state.hasObjectiveCutoff);
      if (state.objPassPercentage !== undefined) setObjPassPercentage(state.objPassPercentage);
      if (state.objWeight !== undefined) setObjWeight(state.objWeight);
      if (state.codingWeight !== undefined) setCodingWeight(state.codingWeight);
      if (state.removedQuestionIds) setRemovedQuestionIds(new Set(state.removedQuestionIds));

      // Restore questions if they exist in state
      if (state.questions && state.topics && !state.refreshManual) {
        setQuestions(state.questions);
        setTopics(state.topics);
        setLoading(false);
        return;
      }

      // If we need to refresh manual questions (e.g. just came back from ManualQuestions page)
      if (state.refreshManual) {
        console.log("ReviewPage: refreshManual is true, preparing to fetch latest manual questions.");
        const restoredQuestions = { ...(state.questions || {}) };
        const restoredTopics = [...(state.topics || [])];
        console.log("Initial questions groups:", Object.keys(restoredQuestions));

        const fetchLatestManual = async (forcedRemovedIds) => {
          const removedSet = forcedRemovedIds || removedQuestionIds;
          try {
            let cid = state.customAssessmentId;
            if (!cid) {
              const draft = localStorage.getItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
              if (draft) cid = Number(draft);
            }
            console.log("ReviewPage fetchLatestManual: cid =", cid);

            if (cid) {
              const manualResp = await axios.get(`${API_BASE_URL}/questions/manual/`, {
                params: { custom_assessment_id: cid }
              });
              let manualList = manualResp.data?.results || [];
              console.log(`ReviewPage fetchLatestManual: Fetched ${manualList.length} questions before filtering.`);

              // Filter out removed questions
              manualList = manualList.filter(q => !removedSet.has(q.id));
              console.log(`ReviewPage fetchLatestManual: ${manualList.length} questions after filtering.`);

              if (manualList.length > 0) {
                manualList.sort((a, b) => {
                  const ta = new Date(a.created_at || 0).getTime();
                  const tb = new Date(b.created_at || 0).getTime();
                  return ta - tb;
                });

                const codingQs = [];
                const standardQs = [];

                manualList.forEach(q => {
                  if (q.question_type === 'CODING' || q.topic === 'Coding') {
                    codingQs.push(q);
                  } else {
                    standardQs.push(q);
                  }
                });

                if (codingQs.length > 0) {
                  const existingCoding = restoredQuestions['Coding'] || [];
                  const existingIds = new Set(existingCoding.map(q => q.id));
                  const newCoding = [...existingCoding];
                  codingQs.forEach(q => {
                    if (!existingIds.has(q.id)) newCoding.push(q);
                  });
                  restoredQuestions['Coding'] = newCoding;
                  if (!restoredTopics.includes('Coding')) restoredTopics.push('Coding');
                }

                if (standardQs.length > 0) {
                  // Use a Set to avoid duplicates if standardQs contains questions already in restoredQuestions
                  const existingStandard = restoredQuestions[MANUAL_TOPIC_LABEL] || [];
                  const existingIds = new Set(existingStandard.map(q => q.id));
                  const newStandard = [...existingStandard];
                  standardQs.forEach(q => {
                    if (!existingIds.has(q.id)) newStandard.push(q);
                  });
                  restoredQuestions[MANUAL_TOPIC_LABEL] = newStandard;
                  if (!restoredTopics.includes(MANUAL_TOPIC_LABEL)) restoredTopics.push(MANUAL_TOPIC_LABEL);
                }
              }
            }
          } catch (e) {
            console.error('Failed to refresh manual questions:', e);
          } finally {
            setQuestions(restoredQuestions);
            setTopics(restoredTopics);
            setLoading(false);
          }
        };

        const initialRemovedSet = new Set(state.removedQuestionIds || []);
        fetchLatestManual(initialRemovedSet);
        return;
      }

      // If coding questions were passed directly
      if (Array.isArray(state.codingQuestions) && state.codingQuestions.length > 0) {
        const codingList = state.codingQuestions;
        setTopics(['Coding']);
        setQuestions({ Coding: codingList });
        const defaultName = state.assessmentName || state.role || (codingList.length === 1 ? codingList[0]?.title : 'Coding Assessment');
        setAssessmentName(defaultName || 'Coding Assessment');
        setLoading(false);
        return;
      }

      // Default: analyze and fetch from scratch
      analyzeAndFetchQuestions(state);
    } else {
      navigate('/custom-assessment');
    }
  }, [location, navigate]); // eslint-disable-line react-hooks/exhaustive-deps

  // Map experience level to difficulty
  const getDifficultyFromExperienceLevel = (experienceLevel) => {
    const difficultyMap = {
      'entry': 'easy',      // 0-2 years → Easy
      'mid': 'medium',      // 2-5 years → Medium
      'senior': 'hard',     // 5-10 years → Hard
      'expert': 'hard',     // 10+ years → Hard
    };


    return difficultyMap[experienceLevel] || null;
  };





  const formatInputTime = (value) => {
    // Remove non-digits
    let val = value.replace(/\D/g, '');
    // Limit to 6 digits (HHMMSS)
    if (val.length > 6) val = val.slice(0, 6);

    if (val.length >= 5) {
      // HH:MM:SS
      return `${val.slice(0, 2)}:${val.slice(2, 4)}:${val.slice(4)}`;
    } else if (val.length >= 3) {
      // HH:MM
      return `${val.slice(0, 2)}:${val.slice(2)}`;
    }
    return val;
  };

  // Analyze skills and fetch questions
  const analyzeAndFetchQuestions = async (data) => {
    setLoading(true);
    setError(null);

    try {
      // Get all unique skills from question distribution
      // If customAssessmentId is missing, fall back to draft ID (covers step-by-step navigation)
      let customAssessmentId = data.customAssessmentId;
      if (!customAssessmentId) {
        try {
          const draftId = localStorage.getItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
          const parsed = Number(draftId);
          if (draftId && !Number.isNaN(parsed) && parsed > 0) {
            customAssessmentId = parsed;
          }
        } catch {
          // ignore
        }
      }

      const allSkills = Object.keys(data.questionDistribution || {});

      if (allSkills.length === 0) {
        // Still try to load manual questions (user may only be using custom questions)
        const questionsByTopic = {};
        try {
          if (customAssessmentId) {
            const manualResp = await axios.get(`${API_BASE_URL}/questions/manual/`, {
              params: { custom_assessment_id: customAssessmentId }
            });
            let manualList = manualResp.data?.results || [];

            // Filter out removed questions
            const removedSet = new Set(data.removedQuestionIds || []);
            manualList = manualList.filter(q => !removedSet.has(q.id));

            if (manualList.length > 0) {
              manualList.sort((a, b) => {
                const ta = new Date(a.created_at || 0).getTime();
                const tb = new Date(b.created_at || 0).getTime();
                return ta - tb;
              });

              // Split coding vs standard
              const codingQs = [];
              const standardQs = [];
              manualList.forEach(q => {
                if (q.question_type === 'CODING' || q.topic === 'Coding') {
                  codingQs.push(q);
                } else {
                  standardQs.push(q);
                }
              });

              const newTopics = [];
              if (codingQs.length > 0) {
                questionsByTopic['Coding'] = codingQs;
                newTopics.push('Coding');
              }
              if (standardQs.length > 0) {
                questionsByTopic[MANUAL_TOPIC_LABEL] = standardQs;
                newTopics.push(MANUAL_TOPIC_LABEL);
              }
              setTopics(newTopics);
              setQuestions(questionsByTopic);
            } else {
              setTopics([]);
              setQuestions({});
            }
          } else {
            setTopics([]);
            setQuestions({});
          }
        } catch (manualErr) {
          console.error('Error fetching manual questions:', manualErr);
          setTopics([]);
          setQuestions({});
        } finally {
          setLoading(false);
        }
        return;
      }

      // Use skills directly as topics (since each skill is a topic in the database)
      setTopics(allSkills);

      // Get difficulty based on experience level
      const difficulty = getDifficultyFromExperienceLevel(data.experienceLevel);
      console.log('Experience Level:', data.experienceLevel, '→ Difficulty:', difficulty);

      // Fetch questions for all skills at once
      try {
        const skillsParam = allSkills.join(',');
        console.log('Fetching questions for skills:', skillsParam);
        console.log('Question distribution:', data.questionDistribution);

        // Get max required count to fetch enough questions
        const maxRequired = Math.max(...Object.values(data.questionDistribution || {}), 50);

        // Build API params
        const apiParams = {
          skills: skillsParam,
          limit_per_skill: maxRequired, // Fetch more than needed, we'll limit client-side
          visibility: 'GLOBAL'
        };



        // Add difficulty filter if experience level is set
        if (difficulty) {
          apiParams.difficulty = difficulty;
        }

        const response = await axios.get(`${API_BASE_URL}/questions/by-skills/`, {
          params: apiParams
        });

        console.log('API Response:', response.data);

        if (response.data && response.data.questions_by_topic) {
          const questionsByTopic = {};

          // Process the response and limit questions per skill based on distribution
          allSkills.forEach(skill => {
            let skillQuestions = response.data.questions_by_topic[skill];
            // Handle cases where backend returns {results: []} instead of a raw array.
            if (skillQuestions && typeof skillQuestions === 'object' && !Array.isArray(skillQuestions)) {
              skillQuestions = skillQuestions.results || [];
            } else if (!Array.isArray(skillQuestions)) {
              skillQuestions = [];
            }
            const requiredCount = data.questionDistribution[skill] || 0;

            console.log(`Skill: ${skill}, Required: ${requiredCount}, Found: ${skillQuestions.length}`);

            // Limit to required count
            if (requiredCount > 0) {
              questionsByTopic[skill] = skillQuestions.slice(0, requiredCount);
            } else {
              questionsByTopic[skill] = [];
            }
          });

          const totalQuestions = Object.values(questionsByTopic).reduce((sum, qs) => sum + qs.length, 0);
          console.log('Final questionsByTopic:', questionsByTopic);
          console.log(`Total questions loaded: ${totalQuestions}`);

          // Fetch manual questions (created from "Create Custom Questions") and show them LAST
          try {
            if (customAssessmentId) {
              const manualResp = await axios.get(`${API_BASE_URL}/questions/manual/`, {
                params: { custom_assessment_id: customAssessmentId }
              });
              let manualList = manualResp.data?.results || [];

              // Filter out removed questions
              const removedSet = new Set(data.removedQuestionIds || []);
              manualList = manualList.filter(q => !removedSet.has(q.id));

              if (manualList.length > 0) {
                // Sort so newest appears last
                manualList.sort((a, b) => {
                  const ta = new Date(a.created_at || 0).getTime();
                  const tb = new Date(b.created_at || 0).getTime();
                  return ta - tb;
                });

                // Split coding vs standard
                const codingQs = [];
                const standardQs = [];
                manualList.forEach(q => {
                  if (q.question_type === 'CODING' || q.topic === 'Coding') {
                    codingQs.push(q);
                  } else {
                    standardQs.push(q);
                  }
                });

                const updatedTopics = [...allSkills];
                if (codingQs.length > 0) {
                  // Merge with existing if any (unlikely here but safe)
                  const existingCoding = questionsByTopic['Coding'] || [];
                  const existingIds = new Set(existingCoding.map(q => q.id));
                  const mergedCoding = [...existingCoding];
                  codingQs.forEach(q => {
                    if (!existingIds.has(q.id)) mergedCoding.push(q);
                  });
                  questionsByTopic['Coding'] = mergedCoding;
                  if (!updatedTopics.includes('Coding')) updatedTopics.push('Coding');
                }

                if (standardQs.length > 0) {
                  questionsByTopic[MANUAL_TOPIC_LABEL] = standardQs;
                  if (!updatedTopics.includes(MANUAL_TOPIC_LABEL)) updatedTopics.push(MANUAL_TOPIC_LABEL);
                }

                setTopics(updatedTopics);
              } else {
                setTopics(allSkills);
              }
            } else {
              setTopics(allSkills);
            }
          } catch (manualErr) {
            console.error('Error fetching manual questions:', manualErr);
            setTopics(allSkills);
          }

          setQuestions(questionsByTopic);
        } else {
          console.warn('No questions_by_topic in response:', response.data);
          setError('No questions found in database. Please run: python manage.py generate_questions');
          setQuestions({});
        }
      } catch (apiError) {
        console.error('Error fetching questions:', apiError);
        console.error('Error details:', apiError.response?.data || apiError.message);
        setError(`Failed to load questions: ${apiError.response?.data?.error || apiError.message}. Please ensure questions are generated using: python manage.py generate_questions`);
        setQuestions({});
      }
    } catch (err) {
      console.error('Error analyzing and fetching questions:', err);
      setError('Failed to load questions. Please try again.');
      setQuestions({});
    } finally {
      setLoading(false);
    }
  };



  // Helper to get current state for navigation
  const getCurrentState = () => {
    return {
      ...assessmentData,
      customAssessmentId: assessmentData.id || assessmentData.customAssessmentId, // Explicitly pass the ID
      questions,
      topics,
      assessmentName,
      minPassPercentage,
      timeLimit,
      objectiveTime,
      codingTime,
      hasObjectiveCutoff,
      objPassPercentage,
      objWeight,
      codingWeight,
    };
  };

  const handleBack = () => {
    navigate('/custom-assessment', { state: getCurrentState() });
  };



  const handleCreateAssessment = async () => {
    if (!assessmentData) {
      return;
    }

    if (!assessmentData.customAssessmentId && !(Array.isArray(assessmentData.codingQuestions) && assessmentData.codingQuestions.length > 0)) {
      alert('Custom assessment ID not found. Please go back and recreate the assessment.');
      return;
    }

    try {
      // Check if we have coding questions from state (coding-only assessment)
      const codingQuestionsFromState = Array.isArray(assessmentData.codingQuestions) ? assessmentData.codingQuestions : [];

      if (codingQuestionsFromState.length > 0) {
        // This is a coding-only assessment
        const codingIds = codingQuestionsFromState
          .map((q) => Number(q.id))
          .filter((id) => Number.isFinite(id) && id > 0);

        if (codingIds.length === 0) {
          alert('No valid coding questions found. Please ensure coding questions are available.');
          return;
        }

        const payload = {
          custom_assessment_id: assessmentData.customAssessmentId,
          question_ids: [], // Empty for coding-only assessments
          coding_question_ids: codingIds,
        };



        // Extract allowed languages from coding questions if available
        const allLanguages = new Set();
        codingQuestionsFromState.forEach((q) => {
          if (Array.isArray(q.languages)) {
            q.languages.forEach((lang) => allLanguages.add(lang));
          } else if (q.language) {
            allLanguages.add(q.language);
          }
        });
        if (allLanguages.size > 0) {
          payload.coding_allowed_languages = Array.from(allLanguages);
        }

        if (assessmentName) {
          payload.name = assessmentName;
          payload.display_name = assessmentName;
        }
        if (assessmentData.role) payload.role = assessmentData.role;
        if (assessmentData.experienceLevel) payload.experience_level = assessmentData.experienceLevel;

        const response = await axios.post(`${API_BASE_URL}/assessments/`, payload);

        if (response.data && response.data.assessment_id) {
          const newId = response.data.assessment_id;
          alert('Assessment created successfully!');
          try {
            // localStorage.removeItem(REVIEW_STATE_STORAGE_KEY);
            // localStorage.removeItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
            // localStorage.removeItem(CUSTOM_ASSESSMENT_STORAGE_KEY);
          } catch {
            // ignore
          }
          navigate(`/invite-candidates/${newId}`, { state: { assessmentName: assessmentName || 'Assessment' } });
        } else {
          alert('Assessment created, but no ID was returned from the server.');
        }
        return;
      }

      // Regular assessment with objective questions (and possibly coding questions mixed in)
      // Flatten all questions from all topics into a single ordered list
      const allQuestions = [];
      const topicsOrder = [...topics];
      topicsOrder.forEach((topic) => {
        const topicQuestions = getQuestionsForTopic(topic);
        topicQuestions.forEach((q) => {
          const skillBadge = topic === MANUAL_TOPIC_LABEL ? (q.topic || MANUAL_TOPIC_LABEL) : topic;
          allQuestions.push({ ...q, skill: skillBadge });
        });
      });

      // Separate coding questions from regular questions
      // Coding questions typically have properties like: time_limit_ms, languages, mode, starter_code
      const regularQuestionIds = [];
      const codingQuestionIds = [];

      allQuestions.forEach((q) => {
        const id = q.id;
        if (id == null || id === undefined) return;

        // Check if it's a coding question (has coding-specific fields)
        const isCodingQuestion =
          q.time_limit_ms != null ||
          q.languages != null ||
          q.mode != null ||
          q.starter_code != null ||
          q.template_code != null;

        if (isCodingQuestion) {
          // Send object with overrides instead of just ID
          codingQuestionIds.push({
            id: Number(id),
            difficulty: q.difficulty,
            time_limit_ms: q.time_limit_ms
          });
        } else {
          regularQuestionIds.push(Number(id));
        }
      });

      if (regularQuestionIds.length === 0 && codingQuestionIds.length === 0) {
        alert('No questions loaded to create an assessment. Please ensure questions are available.');
        return;
      }

      const payload = {
        custom_assessment_id: assessmentData.customAssessmentId,
        question_ids: regularQuestionIds,
        coding_question_ids: codingQuestionIds,
      };


      if (assessmentName) {
        payload.name = assessmentName;
        payload.display_name = assessmentName;
      }
      if (assessmentData.role) payload.role = assessmentData.role;
      if (assessmentData.experienceLevel) payload.experience_level = assessmentData.experienceLevel;

      // New fields
      payload.min_pass_percentage = Number(minPassPercentage) || 60;
      payload.total_time = timeLimit || formatHHMMSS(getTotalTimeSeconds());

      // Split Assessment Fields
      payload.objective_time_limit = objectiveTime;
      payload.coding_time_limit = codingTime;
      payload.has_objective_cutoff = hasObjectiveCutoff;
      payload.min_objective_pass_percentage = Number(objPassPercentage) || 0;
      payload.weightage_objective = Number(objWeight);
      payload.weightage_coding = Number(codingWeight);

      const response = await axios.post(`${API_BASE_URL}/assessments/`, payload);

      if (response.data && response.data.assessment_id) {
        const newId = response.data.assessment_id;
        alert('Assessment created successfully!');
        // Once assessment is created, clear draft state so a new flow starts fresh
        try {
          // localStorage.removeItem(REVIEW_STATE_STORAGE_KEY);
          // localStorage.removeItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
          // localStorage.removeItem(CUSTOM_ASSESSMENT_STORAGE_KEY);
        } catch {
          // ignore
        }
        // Redirect to invite candidates for this assessment
        navigate(`/invite-candidates/${newId}`, { state: { assessmentName: assessmentName || 'Assessment' } });
      } else {
        alert('Assessment created, but no ID was returned from the server.');
      }
    } catch (error) {
      console.error('Error creating assessment:', error);
      const message =
        error.response?.data?.error ||
        error.message ||
        'An error occurred while creating the assessment.';
      alert(message);
    }
  };






  const getQuestionSeconds = (q) => {
    if (!q) return 0;
    if (q.time_limit_ms != null) return Math.floor(Number(q.time_limit_ms) / 1000);
    if (q.time_limit != null) return Number(q.time_limit) || 0;
    return 0;
  };



  const getTotalTimeSeconds = () => {
    return Object.values(questions).reduce((sum, qList) => {
      const listSeconds = (qList || []).reduce((s, q) => s + getQuestionSeconds(q), 0);
      return sum + listSeconds;
    }, 0);
  };



  const formatHHMMSS = (totalSeconds) => {
    const seconds = Math.max(0, Number(totalSeconds) || 0);
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  };

  const parseSeconds = (timeStr) => {
    if (!timeStr) return 0;
    const parts = timeStr.split(':').map(Number);
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    return Number(timeStr) || 0;
  };

  useEffect(() => {
    if (!isTimeEdited && !loading) {
      let objSec = 0;
      let codSec = 0;

      Object.values(questions).forEach(qList => {
        (qList || []).forEach(q => {
          const s = getQuestionSeconds(q);
          // Check if coding
          const isCoding =
            q.time_limit_ms != null ||
            q.languages != null ||
            q.mode != null ||
            q.starter_code != null;

          if (isCoding) codSec += s;
          else objSec += s;
        });
      });

      setObjectiveTime(formatHHMMSS(objSec));
      setCodingTime(formatHHMMSS(codSec));
      setTimeLimit(formatHHMMSS(objSec + codSec));
    }
  }, [questions, isTimeEdited, loading]);

  const handleRemoveQuestion = (topic, questionId) => {
    if (!window.confirm('Are you sure you want to remove this question?')) return;

    // Track removed IDs
    setRemovedQuestionIds(prev => new Set([...prev, questionId]));

    setQuestions(prev => {
      const list = prev[topic] || [];
      const newList = list.filter(q => q.id !== questionId);
      return { ...prev, [topic]: newList };
    });
  };



  const buildOptions = (q) => {
    if (!q) return [];

    if (Array.isArray(q.options) && q.options.length > 0) {
      return q.options
        .map((opt, idx) => {
          if (typeof opt === 'string') {
            return { key: String.fromCharCode(65 + idx), text: opt };
          }
          if (!opt || typeof opt !== 'object') return null;
          const key = opt.key || opt.label || opt.value || String.fromCharCode(65 + idx);
          const text = opt.text || opt.label || opt.value || opt.option || '';
          if (!text) return null;
          return { key, text };
        })
        .filter(Boolean);
    }

    const opts = [];
    if (q.option_a) opts.push({ key: 'A', text: q.option_a });
    if (q.option_b) opts.push({ key: 'B', text: q.option_b });
    if (q.option_c) opts.push({ key: 'C', text: q.option_c });
    if (q.option_d) opts.push({ key: 'D', text: q.option_d });

    if ((q.question_type || '').toUpperCase() === 'TF' && opts.length === 0) {
      return [
        { key: 'A', text: 'True' },
        { key: 'B', text: 'False' },
      ];
    }

    return opts;
  };



  const getQuestionsForTopic = (topic) => {
    return questions[topic] || [];
  };



  if (!assessmentData) {
    return (
      <div className="review-page-container">
        <div className="loading-container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="review-page-container">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <div className="page-container">
        <div className="review-wrapper">
          <h3 className="page-title-centered">Review Assessment</h3>

          {/* Assessment Summary & Configuration */}
          <div className="summary-section">
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">Role:</span>
                <span className="summary-value">
                  {assessmentData.role === 'other'
                    ? assessmentData.customRole
                    : assessmentData.role?.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Experience Level:</span>
                <span className="summary-value">
                  {assessmentData.experienceLevel?.replace(/\b\w/g, l => l.toUpperCase())}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Obj Questions:</span>
                <span className="summary-value">
                  {Object.entries(questions).reduce((sum, [topic, list]) => {
                    if (topic === 'Coding') return sum;
                    return sum + (list || []).length;
                  }, 0)}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Coding Questions:</span>
                <span className="summary-value">
                  {(questions['Coding'] || []).length}
                </span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Time Limit (HH:MM:SS):</span>

                <div
                  className="summary-value"
                  style={{
                    fontSize: '1.2rem',
                    color: '#16a34a',
                    fontWeight: '900',
                    display: 'flex',
                    alignItems: 'center',
                    height: '36px'
                  }}
                  title="Total time is calculated automatically based on questions"
                >
                  {loading ? assessmentData.time : timeLimit}
                </div>
              </div>
              <div className="summary-item">
                <span className="summary-label">Min Pass %:</span>

                <input
                  type="number"
                  className="summary-input"
                  value={minPassPercentage}
                  onChange={(e) => {
                    const val = e.target.value;
                    if (val === '') {
                      setMinPassPercentage('');
                      return;
                    }
                    const num = Number(val);
                    if (num > 100) setMinPassPercentage(100);
                    else if (num < 0) setMinPassPercentage(0);
                    else setMinPassPercentage(val);
                  }}
                  min="0" max="100"
                  style={{ padding: '6px 8px', fontSize: '0.9rem', width: '100%', height: '36px' }}
                />
              </div>

              <div className="summary-item">
                <span className="summary-label">Obj Time (HH:MM:SS):</span>
                <input
                  type="text"
                  className="summary-input"
                  value={objectiveTime}
                  onChange={(e) => {
                    const val = e.target.value;
                    const formatted = formatInputTime(val);
                    setObjectiveTime(formatted);
                    setIsTimeEdited(true);
                    // Update Total Time
                    const objS = parseSeconds(formatted);
                    const codS = parseSeconds(codingTime);
                    setTimeLimit(formatHHMMSS(objS + codS));
                  }}
                  placeholder="00:00:00"
                  maxLength={8}
                  style={{ padding: '6px 8px', fontSize: '0.9rem', width: '100%', height: '36px' }}
                />
              </div>

              <div className="summary-item">
                <span className="summary-label">Coding Time (HH:MM:SS):</span>
                <input
                  type="text"
                  className="summary-input"
                  value={codingTime}
                  onChange={(e) => {
                    const val = e.target.value;
                    const formatted = formatInputTime(val);
                    setCodingTime(formatted);
                    setIsTimeEdited(true);
                    // Update Total Time
                    const objS = parseSeconds(objectiveTime);
                    const codS = parseSeconds(formatted);
                    setTimeLimit(formatHHMMSS(objS + codS));
                  }}
                  placeholder="00:00:00"
                  maxLength={8}
                  style={{ padding: '6px 8px', fontSize: '0.9rem', width: '100%', height: '36px' }}
                />
              </div>

              <div className="summary-item config-row" style={{ gridColumn: '1 / -1', display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '10px', padding: '10px', background: '#f8f9fa', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={hasObjectiveCutoff}
                      onChange={(e) => setHasObjectiveCutoff(e.target.checked)}
                    />
                    <strong>Enforce Objective Cutoff?</strong>
                  </label>
                  {hasObjectiveCutoff && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>Min Obj Pass %:</span>
                      <input
                        type="number"
                        value={objPassPercentage}
                        onChange={(e) => {
                          const val = e.target.value;
                          const num = Number(val);
                          if (num > 100) setObjPassPercentage(100);
                          else if (num < 0) setObjPassPercentage(0);
                          else setObjPassPercentage(val);
                        }}
                        style={{ width: '60px', padding: '4px' }}
                      />
                    </div>
                  )}

                  <div style={{ marginLeft: '40px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.9rem', color: '#64748b', fontWeight: 'bold' }}>Coding Possible Points:</span>
                    <span style={{ fontSize: '1.1rem', fontWeight: '900', color: '#007bff' }}>{totalCodingPoints}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '15px', alignItems: 'center', width: '100%' }}>
                  <strong style={{ minWidth: '70px' }}>Weights:</strong>
                  <span style={{ fontSize: '0.9rem' }}>Objective: {objWeight}%</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={objWeight}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setObjWeight(val);
                      setCodingWeight(100 - val);
                    }}
                    style={{ flex: 1, cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.9rem' }}>Coding: {codingWeight}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* All Questions - Flat List (coding-only simplified) */}
          <div className="topics-section">
            {loading ? (
              <div className="loading-container">
                <div className="spinner"></div>
                <span>Loading questions...</span>
              </div>
            ) : error ? (
              <div className="error-container">
                <p className="error-message">{error}</p>
                <button onClick={() => analyzeAndFetchQuestions(assessmentData)} className="btn btn-primary">
                  Retry
                </button>
              </div>
            ) : (
              <div className="all-questions-list">
                {(() => {
                  // Separation Logic
                  const dbQuestions = [];
                  const manualQuestions = [];

                  topics.forEach((topic) => {
                    const topicQuestions = getQuestionsForTopic(topic);
                    topicQuestions.forEach((q) => {
                      const enrichedQ = { ...q, _topic: topic };
                      if (topic === MANUAL_TOPIC_LABEL) {
                        manualQuestions.push(enrichedQ);
                      } else if (topic !== 'Coding') {
                        dbQuestions.push({ ...enrichedQ, skill: topic }); // Skill is topic for DB items
                      }
                    });
                  });

                  // Group Manual Questions by "assessment" (PDF name or Manual set name)
                  const manualGroups = {};
                  manualQuestions.forEach((q) => {
                    const groupName = q.assessment || 'Unknown Source';
                    if (!manualGroups[groupName]) {
                      manualGroups[groupName] = [];
                    }
                    manualGroups[groupName].push(q);
                  });

                  const hasDbQuestions = dbQuestions.length > 0;
                  const hasManualQuestions = manualQuestions.length > 0;
                  // Check if we have any coding questions (from the 'Coding' topic)
                  const codingQs = questions['Coding'] || [];
                  const hasCodingQuestions = codingQs.length > 0;

                  if (!hasDbQuestions && !hasManualQuestions && !hasCodingQuestions) {
                    return (
                      <div className="no-questions">
                        <p>No questions available. Please ensure questions are generated in the database or add them manually.</p>
                      </div>
                    );
                  }

                  // Handler for Remove All
                  const handleRemoveAll = (groupType, groupKey) => {
                    if (!window.confirm(`Are you sure you want to remove all questions from ${groupKey}?`)) return;

                    setQuestions((prev) => {
                      const newQuestions = { ...prev };

                      if (groupType === 'database') {
                        // Remove all topics that are NOT MANUAL_TOPIC_LABEL AND NOT 'Coding'
                        Object.keys(newQuestions).forEach((t) => {
                          if (t !== MANUAL_TOPIC_LABEL && t !== 'Coding') {
                            delete newQuestions[t];
                          }
                        });
                        // Update topics list
                        setTopics((prevTopics) => prevTopics.filter((t) => t === MANUAL_TOPIC_LABEL || t === 'Coding'));
                      } else if (groupType === 'manual') {
                        // Remove questions from MANUAL_TOPIC_LABEL that match the assessment name
                        const currentManuals = newQuestions[MANUAL_TOPIC_LABEL] || [];
                        const keptManuals = currentManuals.filter((q) => (q.assessment || 'Unknown Source') !== groupKey);

                        if (keptManuals.length === 0) {
                          delete newQuestions[MANUAL_TOPIC_LABEL];
                          setTopics((prevTopics) => prevTopics.filter((t) => t !== MANUAL_TOPIC_LABEL));
                        } else {
                          newQuestions[MANUAL_TOPIC_LABEL] = keptManuals;
                        }

                        // Track removed IDs
                        const removedIds = currentManuals
                          .filter(q => (q.assessment || 'Unknown Source') === groupKey)
                          .map(q => q.id);
                        setRemovedQuestionIds(prev => new Set([...prev, ...removedIds]));
                      } else if (groupType === 'coding') {
                        const removedIds = (newQuestions['Coding'] || []).map(q => q.id);
                        setRemovedQuestionIds(prev => new Set([...prev, ...removedIds]));
                        delete newQuestions['Coding'];
                        setTopics((prevTopics) => prevTopics.filter((t) => t !== 'Coding'));
                      }
                      return newQuestions;
                    });
                  };

                  // Render Function for a list of questions
                  const renderQuestionList = (list, startIndex = 0, isCoding = false) => {
                    return (
                      <div className="questions-list">
                        {list.map((question, idx) => {
                          const globalIndex = startIndex + idx;
                          const isMultiSelect = (question.question_type || '').toUpperCase() === 'MSQ';
                          const controlType = isMultiSelect ? 'checkbox' : 'radio';

                          const isOptionCorrect = (label) => {
                            const normalized = String(label || '').toUpperCase();
                            const single = String(question.correct_answer || '').toUpperCase();
                            if (single && normalized === single) return true;
                            if (Array.isArray(question.correct_answers)) {
                              const multi = question.correct_answers.map((c) => String(c || '').toUpperCase());
                              if (multi.includes(normalized)) return true;
                            }
                            return false;
                          };

                          return (
                            <div key={question.id || globalIndex} className="question-card relative-card">
                              <div
                                className="question-header"
                                style={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  alignItems: 'flex-start',
                                }}
                              >
                                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'baseline', flex: 1 }}>
                                  <span className="question-number">Q{globalIndex + 1}</span>
                                  <div style={{ flex: 1 }}>
                                    <span className="question-title">{question.title || question.question}</span>
                                    {/* Difficulty Editor for Coding Questions */}
                                    {isCoding && (
                                      <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>Difficulty:</span>
                                        <select
                                          value={question.difficulty || 'medium'}
                                          onChange={(e) => {
                                            const newDifficulty = e.target.value;
                                            setQuestions(prev => {
                                              const codingList = prev['Coding'] || [];
                                              const updatedList = codingList.map(q =>
                                                q.id === question.id ? { ...q, difficulty: newDifficulty } : q
                                              );
                                              return { ...prev, 'Coding': updatedList };
                                            });
                                          }}
                                          style={{
                                            padding: '2px 6px',
                                            fontSize: '0.85rem',
                                            borderRadius: '4px',
                                            borderColor: '#d1d5db',
                                            cursor: 'pointer'
                                          }}
                                        >
                                          <option value="easy">Easy</option>
                                          <option value="medium">Medium</option>
                                          <option value="hard">Hard</option>
                                        </select>
                                      </div>
                                    )}
                                  </div>
                                </div>
                                <button
                                  className="btn-remove-question"
                                  onClick={() => handleRemoveQuestion(question._topic, question.id)}
                                  style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#dc3545',
                                    cursor: 'pointer',
                                    fontSize: '0.9rem',
                                    textDecoration: 'underline',
                                    padding: 0,
                                    whiteSpace: 'nowrap',
                                    marginLeft: '1rem',
                                    minWidth: 'fit-content',
                                  }}
                                >
                                  Remove
                                </button>
                              </div>
                              {(() => {
                                const optionList = buildOptions(question);
                                if (optionList.length === 0) {
                                  if (isCoding && question.description) {
                                    return (
                                      <div className="question-options" style={{ color: '#4b5563', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                                        {question.description.slice(0, 150)}{question.description.length > 150 ? '...' : ''}
                                      </div>
                                    );
                                  }
                                  return null;
                                }

                                return (
                                  <div className="question-options">
                                    {optionList.map((opt, optIdx) => {
                                      const label = opt.key || String.fromCharCode(65 + optIdx);
                                      const isCorrect = isOptionCorrect(label);
                                      return (
                                        <label
                                          key={`${question.id || globalIndex}-${label}-${optIdx}`}
                                          className={`option-item ${isCorrect ? 'option-correct' : ''}`}
                                        >
                                          <input type={controlType} className="option-input" disabled />
                                          <span className={`option-control ${controlType} ${isCorrect ? 'correct' : ''}`}>
                                            {label}
                                          </span>
                                          <span className="option-text">{opt.text}</span>
                                        </label>
                                      );
                                    })}
                                  </div>
                                );
                              })()}
                            </div>
                          );
                        })}
                      </div>
                    );
                  };

                  let runningIndex = 0;

                  return (
                    <>
                      {/* Coding Questions Section */}
                      {hasCodingQuestions && (
                        <div className="question-group-section" style={{ marginBottom: '2rem' }}>
                          <div
                            className="group-header"
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: '1rem',
                              borderBottom: '2px solid #e9ecef',
                              paddingBottom: '0.5rem',
                            }}
                          >
                            <h4 style={{ margin: 0, color: '#495057' }}>Coding Questions</h4>
                            <button
                              className="btn btn-outline-danger btn-sm"
                              onClick={() => handleRemoveAll('coding', 'Coding Questions')}
                            >
                              Remove All
                            </button>
                          </div>
                          {renderQuestionList(codingQs.map(q => ({ ...q, _topic: 'Coding' })), runningIndex, true)}
                        </div>
                      )}


                      {(() => {
                        // if (hasCodingQuestions) runningIndex += codingQs.length;
                        return null;
                      })()}


                      {/* Database Questions Section */}
                      {hasDbQuestions && (
                        <div className="question-group-section" style={{ marginBottom: '2rem' }}>
                          <div
                            className="group-header"
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: '1rem',
                              borderBottom: '2px solid #e9ecef',
                              paddingBottom: '0.5rem',
                            }}
                          >
                            <h4 style={{ margin: 0, color: '#495057' }}>Database Questions</h4>
                            <button
                              className="btn btn-outline-danger btn-sm"
                              onClick={() => handleRemoveAll('database', 'Database Questions')}
                            >
                              Remove All
                            </button>
                          </div>
                          {renderQuestionList(dbQuestions, runningIndex)}
                        </div>
                      )}

                      {/* Manual/PDF Groups */}

                      {(() => {
                        let currentIndex = runningIndex + (hasDbQuestions ? dbQuestions.length : 0);
                        return Object.entries(manualGroups).map(([groupName, groupList]) => {
                          const element = (
                            <div key={groupName} className="question-group-section" style={{ marginBottom: '2rem' }}>
                              <div
                                className="group-header"
                                style={{
                                  display: 'flex',
                                  justifyContent: 'space-between',
                                  alignItems: 'center',
                                  marginBottom: '1rem',
                                  borderBottom: '2px solid #e9ecef',
                                  paddingBottom: '0.5rem',
                                }}
                              >
                                <h4 style={{ margin: 0, color: '#495057' }}>
                                  Parsed from: <span style={{ color: '#2563eb' }}>{groupName}</span>
                                </h4>
                                <button
                                  className="btn btn-outline-danger btn-sm"
                                  onClick={() => handleRemoveAll('manual', groupName)}
                                >
                                  Remove All
                                </button>
                              </div>
                              {renderQuestionList(groupList, currentIndex)}
                            </div>
                          );
                          currentIndex += groupList.length;
                          return element;
                        });
                      })()}
                    </>
                  );
                })()}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="form-actions">
            <button type="button" onClick={handleBack} className="btn btn-secondary">
              Back
            </button>
            <button type="button" onClick={handleCreateAssessment} className="btn btn-primary">
              Create Assessment
            </button>
          </div>
        </div>
      </div>

      {/* Sticky Bottom Button - Create Custom Questions */}
      {/* Sticky Bottom Button Container */}
      <div className="sticky-bottom-button-container" style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
        <button
          type="button"
          className="btn-create-custom-questions"
          onClick={() => setShowCodingModal(true)}
          style={{ backgroundColor: '#4f46e5' }} // Distinct color
        >
          + Add Coding Question
        </button>
        <button
          type="button"
          className="btn-create-custom-questions"
          onClick={() => navigate('/manual-questions', { state: getCurrentState() })}
        >
          Create Custom Questions
        </button>
      </div>

      {/* Coding Question Modal */}
      {showCodingModal && (
        <CodingQuestionSelector
          onClose={() => setShowCodingModal(false)}
          onAdd={(selectedQuestions) => {
            setQuestions(prev => {
              const existing = prev['Coding'] || [];
              // Avoid duplicates
              const existingIds = new Set(existing.map(q => q.id));
              const newUnique = selectedQuestions.filter(q => !existingIds.has(q.id));
              return {
                ...prev,
                'Coding': [...existing, ...newUnique]
              };
            });
            setTopics(prev => {
              if (!prev.includes('Coding')) return [...prev, 'Coding'];
              return prev;
            });
            setShowCodingModal(false);
          }}
          alreadySelectedIds={(questions['Coding'] || []).map(q => q.id)}
        />
      )}
    </div>
  );
}

export default ReviewPage;


