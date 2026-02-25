import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';
import { API_BASE_URL } from '../apiConfig';
import '../styles/CustomAssessment.css';

// LocalStorage key for custom assessment form data
const CUSTOM_ASSESSMENT_STORAGE_KEY = 'customAssessmentFormData';
const DRAFT_CUSTOM_ASSESSMENT_ID_KEY = 'draftCustomAssessmentId';

function CustomAssessment() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [formData, setFormData] = useState({
    resume: null,
    role: '',
    subRoles: [],
    customRole: '',
    experienceLevel: '',
    numberOfQuestions: '',
    time: '',
  });
  const [errors, setErrors] = useState({});
  const [resumeFileName, setResumeFileName] = useState('');
  const [extractedSkills, setExtractedSkills] = useState([]);
  const [isExtractingSkills, setIsExtractingSkills] = useState(false);
  const [suggestedSkills, setSuggestedSkills] = useState([]);
  const [commonSkills, setCommonSkills] = useState([]);
  const [questionDistribution, setQuestionDistribution] = useState({});
  const [manualDistribution, setManualDistribution] = useState({});
  const [removedSkills, setRemovedSkills] = useState([]);
  const [autoTime, setAutoTime] = useState('');
  const [weights, setWeights] = useState({ common: 70, role: 15, resume: 15 });
  // NOTE: distribution validation is handled via `errors.distribution` in validateForm().
  const [showQuestionValidationModal, setShowQuestionValidationModal] = useState(false);
  const [missingQuestionsData, setMissingQuestionsData] = useState(null);
  const [isValidatingQuestions, setIsValidatingQuestions] = useState(false);
  const [showMandatoryFieldsModal, setShowMandatoryFieldsModal] = useState(false);
  const [missingMandatoryFields, setMissingMandatoryFields] = useState([]);

  // Sub-roles mapping for each main role
  const roleSubRoles = {
    'software-engineer': [
      'Java Developer',
      'Python Developer',
      'C++ Developer',
      'C# Developer',
      'Go Developer',
      'Ruby Developer',
      'PHP Developer',
      'General Software Engineer'
    ],
    'frontend-developer': [
      'React Developer',
      'Angular Developer',
      'Vue.js Developer',
      'JavaScript Developer',
      'TypeScript Developer',
      'UI Developer',
      'Frontend Architect'
    ],
    'backend-developer': [
      'Node.js Developer',
      'Java Backend Developer',
      'Python Backend Developer',
      'API Developer',
      'Microservices Developer',
      'Backend Architect'
    ],
    'full-stack-developer': [
      'MEAN Stack Developer',
      'MERN Stack Developer',
      'LAMP Stack Developer',
      'Django Full Stack',
      'Rails Full Stack',
      'General Full Stack'
    ],
    'mobile-developer': [
      'iOS Developer (Swift)',
      'iOS Developer (Objective-C)',
      'Android Developer (Java)',
      'Android Developer (Kotlin)',
      'React Native Developer',
      'Flutter Developer',
      'Xamarin Developer',
      'Cross-platform Developer'
    ],
    'devops-engineer': [
      'AWS DevOps Engineer',
      'Azure DevOps Engineer',
      'GCP DevOps Engineer',
      'Kubernetes Specialist',
      'Docker Specialist',
      'CI/CD Engineer',
      'Infrastructure Engineer'
    ],
    'cloud-engineer': [
      'AWS Cloud Engineer',
      'Azure Cloud Engineer',
      'GCP Cloud Engineer',
      'Multi-cloud Engineer',
      'Cloud Architect',
      'Cloud Security Engineer'
    ],
    'data-engineer': [
      'ETL Developer',
      'Big Data Engineer',
      'Data Pipeline Engineer',
      'Spark Developer',
      'Hadoop Developer',
      'Data Infrastructure Engineer'
    ],
    'data-scientist': [
      'Machine Learning Scientist',
      'Deep Learning Scientist',
      'NLP Scientist',
      'Computer Vision Scientist',
      'Statistical Analyst',
      'Research Scientist'
    ],
    'machine-learning-engineer': [
      'ML Engineer (NLP)',
      'ML Engineer (Computer Vision)',
      'ML Engineer (Recommendation Systems)',
      'MLOps Engineer',
      'Deep Learning Engineer',
      'AI Engineer'
    ],
    'data-analyst': [
      'Business Data Analyst',
      'Financial Data Analyst',
      'Marketing Data Analyst',
      'Operations Analyst',
      'SQL Analyst',
      'BI Analyst'
    ],
    'qa-engineer': [
      'Manual QA Engineer',
      'Automation QA Engineer',
      'Performance Test Engineer',
      'Security Test Engineer',
      'Mobile QA Engineer',
      'API Test Engineer'
    ],
    'test-automation-engineer': [
      'Selenium Automation Engineer',
      'Cypress Automation Engineer',
      'Playwright Automation Engineer',
      'API Automation Engineer',
      'Mobile Automation Engineer'
    ],
    'security-engineer': [
      'Application Security Engineer',
      'Network Security Engineer',
      'Cloud Security Engineer',
      'Penetration Tester',
      'Security Architect',
      'Compliance Engineer'
    ],
    'cybersecurity-engineer': [
      'SOC Analyst',
      'Threat Intelligence Analyst',
      'Incident Response Engineer',
      'Security Operations Engineer',
      'Vulnerability Assessment Engineer'
    ],
    'database-administrator': [
      'MySQL DBA',
      'PostgreSQL DBA',
      'Oracle DBA',
      'SQL Server DBA',
      'MongoDB DBA',
      'NoSQL DBA'
    ],
    'database-developer': [
      'SQL Developer',
      'PL/SQL Developer',
      'Database Designer',
      'ETL Developer',
      'Data Warehouse Developer'
    ],
    'ui-ux-designer': [
      'UI Designer',
      'UX Designer',
      'Interaction Designer',
      'Visual Designer',
      'Product Designer',
      'Design Systems Designer'
    ],
    'product-manager': [
      'Technical Product Manager',
      'Product Manager (B2B)',
      'Product Manager (B2C)',
      'Product Manager (Mobile)',
      'Product Manager (SaaS)',
      'Product Owner'
    ],
    'technical-lead': [
      'Frontend Tech Lead',
      'Backend Tech Lead',
      'Full Stack Tech Lead',
      'DevOps Tech Lead',
      'Mobile Tech Lead',
      'Data Tech Lead'
    ],
    'solution-architect': [
      'Enterprise Architect',
      'Cloud Solution Architect',
      'Integration Architect',
      'Security Architect',
      'Data Architect',
      'Application Architect'
    ],
    'software-architect': [
      'System Architect',
      'Application Architect',
      'Microservices Architect',
      'Cloud Architect',
      'Technical Architect'
    ],
    'engineering-manager': [
      'Engineering Manager (Backend)',
      'Engineering Manager (Frontend)',
      'Engineering Manager (Full Stack)',
      'Engineering Manager (DevOps)',
      'Engineering Manager (Mobile)',
      'VP of Engineering'
    ],
    'business-analyst': [
      'IT Business Analyst',
      'Technical Business Analyst',
      'Agile Business Analyst',
      'Data Business Analyst',
      'Process Analyst'
    ],
    'project-manager': [
      'IT Project Manager',
      'Agile Project Manager',
      'Scrum Master',
      'Program Manager',
      'Technical Project Manager'
    ]
  };

  // Check if a role has sub-roles
  const hasSubRoles = (role) => {
    return role && roleSubRoles[role] && roleSubRoles[role].length > 0;
  };

  // Save form data to localStorage
  const saveFormDataToLocalStorage = () => {
    try {
      const dataToSave = {
        formData: {
          // Save all formData except the File object (can't serialize)
          role: formData.role,
          subRoles: formData.subRoles,
          customRole: formData.customRole,
          experienceLevel: formData.experienceLevel,
          numberOfQuestions: formData.numberOfQuestions,
          time: formData.time,
          // Note: resume File object is not saved, only fileName is saved separately
        },
        resumeFileName,
        extractedSkills,
        suggestedSkills,
        commonSkills,
        questionDistribution,
        manualDistribution,
        removedSkills,
        weights,
        autoTime,
        timestamp: new Date().toISOString(), // Track when data was saved
      };
      localStorage.setItem(CUSTOM_ASSESSMENT_STORAGE_KEY, JSON.stringify(dataToSave));
    } catch (error) {
      console.error('Error saving form data to localStorage:', error);
    }
  };

  // Load form data from localStorage
  const loadFormDataFromLocalStorage = () => {
    try {
      const savedData = localStorage.getItem(CUSTOM_ASSESSMENT_STORAGE_KEY);
      if (savedData) {
        const parsed = JSON.parse(savedData);

        // Restore formData (without resume File object)
        if (parsed.formData) {
          setFormData((prev) => ({
            ...prev,
            ...parsed.formData,
            resume: null, // File object cannot be restored
          }));
        }

        // Restore other state
        if (parsed.resumeFileName) setResumeFileName(parsed.resumeFileName);
        if (parsed.extractedSkills) setExtractedSkills(parsed.extractedSkills);
        if (parsed.suggestedSkills) setSuggestedSkills(parsed.suggestedSkills);
        if (parsed.commonSkills) setCommonSkills(parsed.commonSkills);
        if (parsed.questionDistribution) setQuestionDistribution(parsed.questionDistribution);
        if (parsed.manualDistribution) setManualDistribution(parsed.manualDistribution);
        if (parsed.removedSkills) setRemovedSkills(parsed.removedSkills);
        if (parsed.weights) setWeights(parsed.weights);
        if (parsed.autoTime) setAutoTime(parsed.autoTime);

        return true; // Indicate data was loaded
      }
    } catch (error) {
      console.error('Error loading form data from localStorage:', error);
    }
    return false; // No data loaded
  };

  // Check if form has unsaved changes
  const hasUnsavedChanges = useCallback(() => {
    try {
      // Get current form state
      const currentState = {
        formData: {
          role: formData.role,
          subRoles: formData.subRoles,
          customRole: formData.customRole,
          experienceLevel: formData.experienceLevel,
          numberOfQuestions: formData.numberOfQuestions,
          time: formData.time,
        },
        resumeFileName,
        extractedSkills,
        suggestedSkills,
        commonSkills,
        questionDistribution,
        manualDistribution,
        removedSkills,
        weights,
        autoTime,
      };

      // Get saved state from localStorage
      const savedData = localStorage.getItem(CUSTOM_ASSESSMENT_STORAGE_KEY);
      if (!savedData) {
        // If no saved data, check if form has any data
        return (
          formData.role ||
          formData.subRoles.length > 0 ||
          formData.customRole ||
          formData.experienceLevel ||
          formData.numberOfQuestions ||
          formData.time ||
          resumeFileName ||
          extractedSkills.length > 0 ||
          suggestedSkills.length > 0 ||
          Object.keys(questionDistribution).length > 0
        );
      }

      const savedState = JSON.parse(savedData);

      // Compare current state with saved state
      const currentStateStr = JSON.stringify(currentState);
      const savedStateStr = JSON.stringify({
        formData: savedState.formData,
        resumeFileName: savedState.resumeFileName,
        extractedSkills: savedState.extractedSkills,
        suggestedSkills: savedState.suggestedSkills,
        commonSkills: savedState.commonSkills,
        questionDistribution: savedState.questionDistribution,
        manualDistribution: savedState.manualDistribution,
        removedSkills: savedState.removedSkills,
        weights: savedState.weights,
        autoTime: savedState.autoTime,
      });

      return currentStateStr !== savedStateStr;
    } catch (error) {
      console.error('Error checking unsaved changes:', error);
      // If error, assume there are unsaved changes to be safe
      return true;
    }
  }, [formData, resumeFileName, extractedSkills, suggestedSkills, commonSkills, questionDistribution, manualDistribution, removedSkills, weights, autoTime]);

  // Sub-role to skills mapping
  const subRoleSkills = useMemo(() => ({
    // Software Engineer sub-roles
    'Java Developer': ['Java', 'Spring', 'Spring Boot', 'Hibernate', 'Maven', 'Gradle', 'JUnit', 'REST API', 'Microservices', 'SQL', 'MySQL', 'PostgreSQL'],
    'Python Developer': ['Python', 'Django', 'Flask', 'FastAPI', 'SQLAlchemy', 'Pytest', 'REST API', 'Git', 'Docker', 'PostgreSQL', 'MongoDB'],
    'C++ Developer': ['C++', 'STL', 'Object-Oriented Programming', 'Data Structures', 'Algorithms', 'CMake', 'Git', 'Linux', 'Multithreading'],
    'C# Developer': ['C#', '.NET', 'ASP.NET', 'Entity Framework', 'SQL Server', 'REST API', 'Git', 'Visual Studio', 'Azure'],
    'Go Developer': ['Go', 'Goroutines', 'REST API', 'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB', 'Git', 'Microservices'],
    'Ruby Developer': ['Ruby', 'Ruby on Rails', 'RSpec', 'PostgreSQL', 'MySQL', 'REST API', 'Git', 'Docker'],
    'PHP Developer': ['PHP', 'Laravel', 'Symfony', 'MySQL', 'REST API', 'Composer', 'Git', 'JavaScript', 'HTML', 'CSS'],
    'General Software Engineer': ['Programming', 'Data Structures', 'Algorithms', 'Git', 'REST API', 'SQL', 'Agile', 'Scrum'],

    // Frontend Developer sub-roles
    'React Developer': ['React', 'JavaScript', 'TypeScript', 'Redux', 'HTML', 'CSS', 'REST API', 'Git', 'Webpack', 'Jest'],
    'Angular Developer': ['Angular', 'TypeScript', 'RxJS', 'HTML', 'CSS', 'REST API', 'Git', 'Node.js', 'Jasmine'],
    'Vue.js Developer': ['Vue.js', 'JavaScript', 'TypeScript', 'Vuex', 'HTML', 'CSS', 'REST API', 'Git', 'Webpack'],
    'JavaScript Developer': ['JavaScript', 'ES6+', 'HTML', 'CSS', 'DOM', 'REST API', 'Git', 'Node.js', 'jQuery'],
    'TypeScript Developer': ['TypeScript', 'JavaScript', 'HTML', 'CSS', 'REST API', 'Git', 'Node.js', 'Angular', 'React'],
    'UI Developer': ['HTML', 'CSS', 'JavaScript', 'Responsive Design', 'UI/UX', 'Figma', 'Adobe XD', 'Git'],
    'Frontend Architect': ['React', 'Angular', 'Vue.js', 'TypeScript', 'Architecture', 'Design Patterns', 'Performance Optimization', 'Webpack', 'Micro Frontends'],

    // Backend Developer sub-roles
    'Node.js Developer': ['Node.js', 'Express', 'JavaScript', 'TypeScript', 'REST API', 'MongoDB', 'PostgreSQL', 'Git', 'Docker'],
    'Java Backend Developer': ['Java', 'Spring Boot', 'REST API', 'Microservices', 'MySQL', 'PostgreSQL', 'Maven', 'Git', 'Docker'],
    'Python Backend Developer': ['Python', 'Django', 'Flask', 'FastAPI', 'REST API', 'PostgreSQL', 'MongoDB', 'Git', 'Docker'],
    'API Developer': ['REST API', 'GraphQL', 'Postman', 'Swagger', 'OpenAPI', 'JSON', 'XML', 'Authentication', 'OAuth'],
    'Microservices Developer': ['Microservices', 'Docker', 'Kubernetes', 'REST API', 'Message Queue', 'Service Mesh', 'API Gateway'],
    'Backend Architect': ['System Design', 'Architecture', 'Microservices', 'Scalability', 'Performance', 'Security', 'Cloud', 'Design Patterns'],

    // Full Stack Developer sub-roles
    'MEAN Stack Developer': ['MongoDB', 'Express', 'Angular', 'Node.js', 'JavaScript', 'TypeScript', 'REST API', 'Git'],
    'MERN Stack Developer': ['MongoDB', 'Express', 'React', 'Node.js', 'JavaScript', 'REST API', 'Redux', 'Git'],
    'LAMP Stack Developer': ['Linux', 'Apache', 'MySQL', 'PHP', 'JavaScript', 'HTML', 'CSS', 'Git'],
    'Django Full Stack': ['Python', 'Django', 'HTML', 'CSS', 'JavaScript', 'PostgreSQL', 'REST API', 'Git', 'Docker'],
    'Rails Full Stack': ['Ruby', 'Ruby on Rails', 'HTML', 'CSS', 'JavaScript', 'PostgreSQL', 'REST API', 'Git'],
    'General Full Stack': ['Frontend', 'Backend', 'Database', 'REST API', 'Git', 'Docker', 'JavaScript', 'SQL'],

    // Mobile Developer sub-roles
    'iOS Developer (Swift)': ['Swift', 'iOS', 'Xcode', 'UIKit', 'SwiftUI', 'Core Data', 'REST API', 'Git', 'CocoaPods'],
    'iOS Developer (Objective-C)': ['Objective-C', 'iOS', 'Xcode', 'UIKit', 'Core Data', 'REST API', 'Git'],
    'Android Developer (Java)': ['Java', 'Android', 'Android Studio', 'XML', 'REST API', 'SQLite', 'Git', 'Gradle'],
    'Android Developer (Kotlin)': ['Kotlin', 'Android', 'Android Studio', 'XML', 'REST API', 'SQLite', 'Git', 'Gradle'],
    'React Native Developer': ['React Native', 'JavaScript', 'TypeScript', 'Redux', 'REST API', 'Git', 'iOS', 'Android'],
    'Flutter Developer': ['Flutter', 'Dart', 'iOS', 'Android', 'REST API', 'Git', 'Firebase', 'State Management'],
    'Xamarin Developer': ['Xamarin', 'C#', '.NET', 'iOS', 'Android', 'REST API', 'Git', 'Visual Studio'],
    'Cross-platform Developer': ['React Native', 'Flutter', 'Xamarin', 'JavaScript', 'Dart', 'C#', 'REST API', 'Git'],

    // DevOps Engineer sub-roles
    'AWS DevOps Engineer': ['AWS', 'EC2', 'S3', 'Lambda', 'CloudFormation', 'Terraform', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins'],
    'Azure DevOps Engineer': ['Azure', 'Azure DevOps', 'ARM Templates', 'Docker', 'Kubernetes', 'CI/CD', 'PowerShell', 'Terraform'],
    'GCP DevOps Engineer': ['GCP', 'Google Cloud', 'Cloud Build', 'Docker', 'Kubernetes', 'CI/CD', 'Terraform', 'Python'],
    'Kubernetes Specialist': ['Kubernetes', 'Docker', 'Helm', 'YAML', 'CI/CD', 'Monitoring', 'Service Mesh', 'Cloud'],
    'Docker Specialist': ['Docker', 'Docker Compose', 'Containerization', 'CI/CD', 'Linux', 'Kubernetes', 'Git'],
    'CI/CD Engineer': ['Jenkins', 'GitLab CI', 'GitHub Actions', 'Docker', 'Kubernetes', 'Scripting', 'Automation', 'Git'],
    'Infrastructure Engineer': ['Infrastructure', 'Cloud', 'Terraform', 'Ansible', 'Docker', 'Kubernetes', 'Linux', 'Networking'],

    // Cloud Engineer sub-roles
    'AWS Cloud Engineer': ['AWS', 'EC2', 'S3', 'RDS', 'Lambda', 'CloudFormation', 'Terraform', 'IAM', 'VPC'],
    'Azure Cloud Engineer': ['Azure', 'Azure AD', 'ARM Templates', 'PowerShell', 'Azure DevOps', 'Terraform', 'Networking'],
    'GCP Cloud Engineer': ['GCP', 'Google Cloud', 'Compute Engine', 'Cloud Storage', 'Terraform', 'Python', 'Networking'],
    'Multi-cloud Engineer': ['AWS', 'Azure', 'GCP', 'Terraform', 'Cloud Architecture', 'Networking', 'Security'],
    'Cloud Architect': ['Cloud Architecture', 'AWS', 'Azure', 'GCP', 'Scalability', 'Security', 'Cost Optimization', 'Design Patterns'],
    'Cloud Security Engineer': ['Cloud Security', 'AWS Security', 'Azure Security', 'IAM', 'Encryption', 'Compliance', 'Security Best Practices'],

    // Data Engineer sub-roles
    'ETL Developer': ['ETL', 'Python', 'SQL', 'Data Pipeline', 'Apache Airflow', 'Data Warehouse', 'ETL Tools'],
    'Big Data Engineer': ['Hadoop', 'Spark', 'Kafka', 'Big Data', 'Scala', 'Python', 'Data Pipeline', 'Distributed Systems'],
    'Data Pipeline Engineer': ['Data Pipeline', 'Apache Airflow', 'Python', 'SQL', 'ETL', 'Data Processing', 'Automation'],
    'Spark Developer': ['Apache Spark', 'Scala', 'Python', 'Big Data', 'Data Processing', 'Hadoop', 'SQL'],
    'Hadoop Developer': ['Hadoop', 'HDFS', 'MapReduce', 'Hive', 'Pig', 'Java', 'Big Data', 'Data Processing'],
    'Data Infrastructure Engineer': ['Data Infrastructure', 'Big Data', 'Cloud', 'Data Pipeline', 'Scalability', 'Monitoring', 'Automation'],

    // Data Scientist sub-roles
    'Machine Learning Scientist': ['Machine Learning', 'Python', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'Statistics', 'Data Analysis'],
    'Deep Learning Scientist': ['Deep Learning', 'TensorFlow', 'PyTorch', 'Neural Networks', 'Python', 'GPU Computing', 'Keras'],
    'NLP Scientist': ['NLP', 'Natural Language Processing', 'Python', 'TensorFlow', 'PyTorch', 'Transformers', 'Text Analysis'],
    'Computer Vision Scientist': ['Computer Vision', 'OpenCV', 'TensorFlow', 'PyTorch', 'Image Processing', 'Deep Learning', 'Python'],
    'Statistical Analyst': ['Statistics', 'R', 'Python', 'Data Analysis', 'Hypothesis Testing', 'Regression', 'Statistical Modeling'],
    'Research Scientist': ['Research', 'Machine Learning', 'Deep Learning', 'Python', 'Statistics', 'Publications', 'Experimentation'],

    // Machine Learning Engineer sub-roles
    'ML Engineer (NLP)': ['NLP', 'Machine Learning', 'Python', 'TensorFlow', 'PyTorch', 'Transformers', 'MLOps', 'Deployment'],
    'ML Engineer (Computer Vision)': ['Computer Vision', 'Machine Learning', 'OpenCV', 'TensorFlow', 'PyTorch', 'MLOps', 'Deployment'],
    'ML Engineer (Recommendation Systems)': ['Recommendation Systems', 'Machine Learning', 'Python', 'Collaborative Filtering', 'MLOps'],
    'MLOps Engineer': ['MLOps', 'Machine Learning', 'Docker', 'Kubernetes', 'CI/CD', 'Model Deployment', 'Monitoring', 'Python'],
    'Deep Learning Engineer': ['Deep Learning', 'TensorFlow', 'PyTorch', 'Neural Networks', 'Python', 'GPU Computing', 'MLOps'],
    'AI Engineer': ['Artificial Intelligence', 'Machine Learning', 'Deep Learning', 'Python', 'TensorFlow', 'PyTorch', 'MLOps'],

    // Data Analyst sub-roles
    'Business Data Analyst': ['Data Analysis', 'SQL', 'Excel', 'Tableau', 'Power BI', 'Statistics', 'Business Intelligence'],
    'Financial Data Analyst': ['Financial Analysis', 'SQL', 'Excel', 'Python', 'Statistics', 'Financial Modeling', 'Data Visualization'],
    'Marketing Data Analyst': ['Marketing Analytics', 'SQL', 'Excel', 'Google Analytics', 'Data Analysis', 'A/B Testing', 'Statistics'],
    'Operations Analyst': ['Operations Analysis', 'SQL', 'Excel', 'Data Analysis', 'Process Improvement', 'Statistics'],
    'SQL Analyst': ['SQL', 'Database', 'Data Analysis', 'Query Optimization', 'ETL', 'Reporting', 'Excel'],
    'BI Analyst': ['Business Intelligence', 'Tableau', 'Power BI', 'SQL', 'Data Analysis', 'Data Visualization', 'Reporting'],

    // QA Engineer sub-roles
    'Manual QA Engineer': ['Manual Testing', 'Bug Tracking', 'Test Planning', 'JIRA', 'Agile', 'Scrum'],
    'Automation QA Engineer': ['Test Automation', 'Selenium', 'Python', 'Java', 'Test Framework', 'CI/CD', 'Git'],
    'Performance Test Engineer': ['Performance Testing', 'Load Testing', 'JMeter', 'Performance Analysis', 'Optimization'],
    'Security Test Engineer': ['Security Testing', 'Penetration Testing', 'OWASP', 'Vulnerability Assessment', 'Security Tools'],
    'Mobile QA Engineer': ['Mobile Testing', 'iOS', 'Android', 'Test Automation', 'Appium', 'Manual Testing'],
    'API Test Engineer': ['API Testing', 'Postman', 'REST API', 'Automation', 'Test Framework', 'JSON', 'XML'],

    // Test Automation Engineer sub-roles
    'Selenium Automation Engineer': ['Selenium', 'Test Automation', 'Java', 'Python', 'Test Framework', 'CI/CD', 'Git'],
    'Cypress Automation Engineer': ['Cypress', 'JavaScript', 'Test Automation', 'E2E Testing', 'CI/CD', 'Git'],
    'Playwright Automation Engineer': ['Playwright', 'Test Automation', 'JavaScript', 'TypeScript', 'E2E Testing', 'CI/CD'],
    'API Automation Engineer': ['API Testing', 'Postman', 'REST Assured', 'Test Automation', 'CI/CD', 'Git'],
    'Mobile Automation Engineer': ['Appium', 'Mobile Testing', 'Test Automation', 'iOS', 'Android', 'CI/CD'],

    // Security Engineer sub-roles
    'Application Security Engineer': ['Application Security', 'OWASP', 'Security Testing', 'Code Review', 'Vulnerability Assessment'],
    'Network Security Engineer': ['Network Security', 'Firewall', 'VPN', 'IDS/IPS', 'Network Monitoring', 'Security Protocols'],
    'Penetration Tester': ['Penetration Testing', 'Ethical Hacking', 'Security Tools', 'Vulnerability Assessment', 'OWASP'],
    'Compliance Engineer': ['Compliance', 'GDPR', 'HIPAA', 'SOC 2', 'Security Audits', 'Risk Management'],

    // Cybersecurity Engineer sub-roles
    'SOC Analyst': ['SOC', 'Security Operations', 'SIEM', 'Threat Detection', 'Incident Response', 'Security Monitoring'],
    'Threat Intelligence Analyst': ['Threat Intelligence', 'Security Analysis', 'Threat Hunting', 'Malware Analysis'],
    'Incident Response Engineer': ['Incident Response', 'Forensics', 'Security Tools', 'Threat Analysis', 'Crisis Management'],
    'Security Operations Engineer': ['Security Operations', 'SIEM', 'Automation', 'Security Tools', 'Monitoring', 'Incident Response'],
    'Vulnerability Assessment Engineer': ['Vulnerability Assessment', 'Security Scanning', 'Penetration Testing', 'Risk Analysis'],

    // Database Administrator sub-roles
    'MySQL DBA': ['MySQL', 'Database Administration', 'SQL', 'Performance Tuning', 'Backup & Recovery', 'Replication'],
    'PostgreSQL DBA': ['PostgreSQL', 'Database Administration', 'SQL', 'Performance Tuning', 'Backup & Recovery', 'Replication'],
    'Oracle DBA': ['Oracle', 'Database Administration', 'PL/SQL', 'Performance Tuning', 'Backup & Recovery', 'RAC'],
    'SQL Server DBA': ['SQL Server', 'Database Administration', 'T-SQL', 'Performance Tuning', 'Backup & Recovery', 'Always On'],
    'MongoDB DBA': ['MongoDB', 'NoSQL', 'Database Administration', 'Performance Tuning', 'Backup & Recovery', 'Sharding'],
    'NoSQL DBA': ['NoSQL', 'MongoDB', 'Cassandra', 'Database Administration', 'Performance Tuning', 'Scalability'],

    // Database Developer sub-roles
    'SQL Developer': ['SQL', 'Database Design', 'Stored Procedures', 'Query Optimization', 'ETL', 'Reporting'],
    'PL/SQL Developer': ['PL/SQL', 'Oracle', 'Stored Procedures', 'Triggers', 'Database Design', 'SQL'],
    'Database Designer': ['Database Design', 'ER Modeling', 'Normalization', 'SQL', 'Database Architecture'],
    'Data Warehouse Developer': ['Data Warehouse', 'ETL', 'SQL', 'Dimensional Modeling', 'BI', 'Data Integration'],

    // UI/UX Designer sub-roles
    'UI Designer': ['UI Design', 'Figma', 'Adobe XD', 'Sketch', 'Design Systems', 'Prototyping', 'Visual Design'],
    'UX Designer': ['UX Design', 'User Research', 'Wireframing', 'Prototyping', 'Usability Testing', 'Figma', 'Adobe XD'],
    'Interaction Designer': ['Interaction Design', 'UX Design', 'Prototyping', 'User Flows', 'Figma', 'Adobe XD'],
    'Visual Designer': ['Visual Design', 'Graphic Design', 'Adobe Creative Suite', 'Figma', 'Branding', 'Typography'],
    'Product Designer': ['Product Design', 'UX Design', 'UI Design', 'Figma', 'Prototyping', 'User Research'],
    'Design Systems Designer': ['Design Systems', 'Component Libraries', 'Figma', 'Design Tokens', 'UI Design'],

    // Product Manager sub-roles
    'Technical Product Manager': ['Product Management', 'Technical Skills', 'Agile', 'Scrum', 'Roadmap', 'Stakeholder Management'],
    'Product Manager (B2B)': ['Product Management', 'B2B', 'Enterprise Software', 'Agile', 'Scrum', 'Stakeholder Management'],
    'Product Manager (B2C)': ['Product Management', 'B2C', 'User Experience', 'Agile', 'Scrum', 'Analytics'],
    'Product Manager (Mobile)': ['Product Management', 'Mobile Apps', 'iOS', 'Android', 'Agile', 'Scrum', 'Analytics'],
    'Product Manager (SaaS)': ['Product Management', 'SaaS', 'Cloud', 'Agile', 'Scrum', 'Stakeholder Management'],
    'Product Owner': ['Product Owner', 'Agile', 'Scrum', 'Backlog Management', 'Stakeholder Management', 'Requirements'],

    // Technical Lead sub-roles
    'Frontend Tech Lead': ['Frontend', 'React', 'Angular', 'Vue.js', 'Leadership', 'Architecture', 'Code Review', 'Mentoring'],
    'Backend Tech Lead': ['Backend', 'System Design', 'Architecture', 'Leadership', 'Code Review', 'Mentoring', 'Microservices'],
    'Full Stack Tech Lead': ['Full Stack', 'Frontend', 'Backend', 'Leadership', 'Architecture', 'Code Review', 'Mentoring'],
    'DevOps Tech Lead': ['DevOps', 'Cloud', 'Infrastructure', 'Leadership', 'Architecture', 'Automation', 'Mentoring'],
    'Mobile Tech Lead': ['Mobile', 'iOS', 'Android', 'Leadership', 'Architecture', 'Code Review', 'Mentoring'],
    'Data Tech Lead': ['Data Engineering', 'Big Data', 'Leadership', 'Architecture', 'Data Pipeline', 'Mentoring'],

    // Solution Architect sub-roles
    'Enterprise Architect': ['Enterprise Architecture', 'System Design', 'TOGAF', 'Architecture Patterns', 'Integration'],
    'Cloud Solution Architect': ['Cloud Architecture', 'AWS', 'Azure', 'GCP', 'System Design', 'Scalability', 'Security'],
    'Integration Architect': ['Integration Architecture', 'API', 'Microservices', 'ESB', 'System Integration', 'Middleware'],
    'Data Architect': ['Data Architecture', 'Data Modeling', 'Data Warehouse', 'Big Data', 'Data Strategy'],
    'Application Architect': ['Application Architecture', 'System Design', 'Design Patterns', 'Scalability', 'Performance'],

    // Software Architect sub-roles
    'System Architect': ['System Architecture', 'System Design', 'Scalability', 'Performance', 'Design Patterns'],
    'Microservices Architect': ['Microservices', 'System Design', 'Distributed Systems', 'API Gateway', 'Service Mesh'],
    'Technical Architect': ['Technical Architecture', 'System Design', 'Design Patterns', 'Technology Stack', 'Scalability'],

    // Engineering Manager sub-roles
    'Engineering Manager (Backend)': ['Backend', 'Leadership', 'Team Management', 'Hiring', 'Performance Management', 'Agile'],
    'Engineering Manager (Frontend)': ['Frontend', 'Leadership', 'Team Management', 'Hiring', 'Performance Management', 'Agile'],
    'Engineering Manager (Full Stack)': ['Full Stack', 'Leadership', 'Team Management', 'Hiring', 'Performance Management', 'Agile'],
    'Engineering Manager (DevOps)': ['DevOps', 'Leadership', 'Team Management', 'Hiring', 'Performance Management', 'Infrastructure'],
    'Engineering Manager (Mobile)': ['Mobile', 'Leadership', 'Team Management', 'Hiring', 'Performance Management', 'iOS', 'Android'],
    'VP of Engineering': ['Engineering Leadership', 'Strategy', 'Team Management', 'Hiring', 'Budget Management', 'Technology Vision'],

    // Business Analyst sub-roles
    'IT Business Analyst': ['Business Analysis', 'Requirements Gathering', 'Documentation', 'Stakeholder Management', 'Agile'],
    'Technical Business Analyst': ['Business Analysis', 'Technical Requirements', 'System Analysis', 'Documentation', 'Agile'],
    'Agile Business Analyst': ['Business Analysis', 'Agile', 'Scrum', 'Requirements', 'User Stories', 'Backlog Management'],
    'Data Business Analyst': ['Business Analysis', 'Data Analysis', 'SQL', 'Requirements', 'Data Requirements'],
    'Process Analyst': ['Process Analysis', 'Business Process', 'Process Improvement', 'Documentation', 'Analysis'],

    // Project Manager sub-roles
    'IT Project Manager': ['Project Management', 'Agile', 'Scrum', 'Stakeholder Management', 'Risk Management', 'Budget Management'],
    'Agile Project Manager': ['Project Management', 'Agile', 'Scrum', 'Kanban', 'Team Management', 'Stakeholder Management'],
    'Scrum Master': ['Scrum', 'Agile', 'Scrum Master', 'Team Facilitation', 'Sprint Planning', 'Retrospectives'],
    'Program Manager': ['Program Management', 'Project Management', 'Stakeholder Management', 'Strategy', 'Risk Management'],
    'Technical Project Manager': ['Project Management', 'Technical Skills', 'Agile', 'Scrum', 'Stakeholder Management', 'Risk Management']
  }), []);

  useEffect(() => {
    // Load saved form data from localStorage
    loadFormDataFromLocalStorage();
  }, []);

  // Handle browser tab/window close with unsaved changes warning
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges()) {
        // Modern browsers ignore custom messages, but we still need to set returnValue
        e.preventDefault();
        e.returnValue = ''; // Chrome requires returnValue to be set
        return ''; // Some browsers require return value
      }
    };

    // Add event listener
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges]);

  // Note: React Router navigation (like Cancel button) is handled by handleCancel function
  // The beforeunload event handles browser tab/window close

  // Calculate common skills between extracted and suggested skills
  useEffect(() => {
    if (extractedSkills.length > 0 && suggestedSkills.length > 0) {
      // Normalize skills for comparison (case-insensitive, trim whitespace)
      const normalizeSkill = (skill) => skill.toLowerCase().trim();

      const normalizedSuggested = suggestedSkills.map(normalizeSkill);

      // Find common skills (case-insensitive matching)
      const common = extractedSkills.filter(skill =>
        normalizedSuggested.includes(normalizeSkill(skill))
      );

      setCommonSkills(common);
    } else {
      setCommonSkills([]);
    }
  }, [extractedSkills, suggestedSkills]);

  const aggregateSuggested = useCallback((selectedSubs) => {
    const aggregated = [];
    selectedSubs.forEach((sub) => {
      if (subRoleSkills[sub]) {
        aggregated.push(...subRoleSkills[sub]);
      }
    });
    setSuggestedSkills(Array.from(new Set(aggregated)));
  }, [subRoleSkills]);

  // Re-aggregate suggested skills when sub-roles change (safety if set elsewhere)
  useEffect(() => {
    aggregateSuggested(formData.subRoles || []);
  }, [formData.subRoles, aggregateSuggested]);

  // Auto-calculate time based on number of questions (2 minutes each)
  useEffect(() => {
    const totalQuestions = parseInt(formData.numberOfQuestions);
    if (!Number.isNaN(totalQuestions) && totalQuestions > 0) {
      const totalSeconds = totalQuestions * 120; // 2 minutes per question
      const auto = formatSecondsToHHMMSS(totalSeconds);
      setAutoTime(auto);
      setFormData((prev) => ({ ...prev, time: auto }));
      setErrors((prev) => ({ ...prev, time: '' }));
    } else {
      setAutoTime('');
    }
  }, [formData.numberOfQuestions]);

  // Calculate question distribution per skill
  useEffect(() => {
    const totalQuestions = parseInt(formData.numberOfQuestions);

    if (Number.isNaN(totalQuestions) || totalQuestions <= 0) {
      setQuestionDistribution({});
      return;
    }

    if (commonSkills.length === 0 && extractedSkills.length === 0 && suggestedSkills.length === 0) {
      setQuestionDistribution({});
      return;
    }

    const distribution = {};

    // Helpers to normalize for comparison
    const normalize = (skill) => skill.toLowerCase().trim();

    // Get resume-only skills (in extracted but not in common)
    const resumeOnlySkills = extractedSkills.filter(
      (skill) => !commonSkills.some((common) => normalize(common) === normalize(skill))
    );

    // Get role-only skills (in suggested but not in common)
    const roleOnlySkills = suggestedSkills.filter(
      (skill) => !commonSkills.some((common) => normalize(common) === normalize(skill))
    );

    // Percent allocations (customizable)
    let totalWeight = (weights.common || 0) + (weights.role || 0) + (weights.resume || 0);
    if (totalWeight === 0) {
      totalWeight = 100;
    }
    // Normalize to sum to 1 so allocation still works even if user sums to e.g. 98 or 105.
    const effectiveCommon = (weights.common || 0) / totalWeight;
    const effectiveRole = (weights.role || 0) / totalWeight;

    let commonQuestionsTotal = Math.round(totalQuestions * effectiveCommon);
    let roleQuestionsTotal = Math.round(totalQuestions * effectiveRole);
    let resumeQuestionsTotal = totalQuestions - commonQuestionsTotal - roleQuestionsTotal;

    // Adjust for rounding errors to ensure sum matches totalQuestions
    if (resumeQuestionsTotal < 0) {
      resumeQuestionsTotal = 0;
    }
    const adjustDelta = totalQuestions - (commonQuestionsTotal + roleQuestionsTotal + resumeQuestionsTotal);
    if (adjustDelta !== 0) {
      commonQuestionsTotal += adjustDelta;
    }

    // Allocation helper
    const allocateQuestions = (skills, total) => {
      if (!skills || skills.length === 0 || total <= 0) return;

      const perSkill = Math.floor(total / skills.length);
      const remainder = total % skills.length;

      skills.forEach((skill, index) => {
        const count = perSkill + (index < remainder ? 1 : 0);
        distribution[skill] = (distribution[skill] || 0) + count;
      });
    };

    allocateQuestions(commonSkills, commonQuestionsTotal);
    allocateQuestions(roleOnlySkills, roleQuestionsTotal);
    allocateQuestions(resumeOnlySkills, resumeQuestionsTotal);

    // Apply manual overrides and filter removed skills
    const finalDistribution = {};
    Object.entries(distribution).forEach(([skill, count]) => {
      if (!removedSkills.includes(skill)) {
        finalDistribution[skill] = manualDistribution[skill] !== undefined
          ? manualDistribution[skill]
          : count;
      }
    });

    setQuestionDistribution(finalDistribution);
  }, [formData.numberOfQuestions, commonSkills, extractedSkills, suggestedSkills, manualDistribution, removedSkills, weights]);


  // Extract skills from resume using API
  const extractSkillsFromResume = async (file) => {
    setIsExtractingSkills(true);
    setExtractedSkills([]);

    try {
      // Create FormData to send file
      const formData = new FormData();
      formData.append('resume', file);

      // Call API to extract skills
      const response = await axios.post(`${API_BASE_URL} /extract-skills/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Set extracted skills from API response
      if (response.data && response.data.skills) {
        setExtractedSkills(response.data.skills);
      } else {
        setExtractedSkills([]);
      }
    } catch (error) {
      console.error('Error extracting skills:', error);
      // On error, set empty skills array
      setExtractedSkills([]);

      // Optionally show error message to user
      if (error.response) {
        console.error('API Error:', error.response.data.error || 'Failed to extract skills from resume.');
      } else if (error.request) {
        console.error('Network Error: Unable to connect to server. Please check if Django backend is running.');
      }
    } finally {
      setIsExtractingSkills(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData({ ...formData, resume: file });
      setResumeFileName(file.name);
      setErrors({ ...errors, resume: '' });
      // Extract skills from resume
      await extractSkillsFromResume(file);
    }
  };

  const handleRemoveResume = () => {
    setFormData({ ...formData, resume: null });
    setResumeFileName('');
    setExtractedSkills([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleReuploadResume = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setExtractedSkills(extractedSkills.filter(skill => skill !== skillToRemove));
  };

  const handleRemoveSkillFromDistribution = (skillToRemove) => {
    setRemovedSkills([...removedSkills, skillToRemove]);
    // Clear manual distribution for removed skill
    const updatedManual = { ...manualDistribution };
    delete updatedManual[skillToRemove];
    setManualDistribution(updatedManual);
  };

  const handleUpdateSkillQuestions = (skill, newCount) => {
    const count = Math.max(0, parseInt(newCount) || 0);
    setManualDistribution({ ...manualDistribution, [skill]: count });
  };

  const handleRestoreSkill = (skillToRestore) => {
    setRemovedSkills(removedSkills.filter(skill => skill !== skillToRestore));
  };

  const handleRebalanceRemaining = () => {
    const total = parseInt(formData.numberOfQuestions) || 0;
    const allocated = Object.values(questionDistribution).reduce((sum, count) => sum + (count || 0), 0);
    const remaining = total - allocated;
    if (remaining <= 0) return;

    const availableCommon = commonSkills.filter(skill => !removedSkills.includes(skill));
    if (availableCommon.length === 0) return;

    const perSkill = Math.floor(remaining / availableCommon.length);
    const remainder = remaining % availableCommon.length;
    const updatedManual = { ...manualDistribution };

    availableCommon.forEach((skill, index) => {
      const existing = questionDistribution[skill] || 0;
      updatedManual[skill] = existing + perSkill + (index < remainder ? 1 : 0);
    });

    setManualDistribution(updatedManual);
  };

  const handleWeightChange = (name, value) => {
    const num = Math.max(0, Math.min(100, parseInt(value) || 0));
    setWeights((prev) => ({ ...prev, [name]: num }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // If role is changed, clear subRole and customRole
    if (name === 'role') {
      if (value !== 'other') {
        setFormData({ ...formData, [name]: value, subRoles: [], customRole: '' });
        setSuggestedSkills([]);
      } else {
        setFormData({ ...formData, [name]: value, subRoles: [], customRole: '' });
        setSuggestedSkills([]);
      }
    } else {
      setFormData({ ...formData, [name]: value });
    }

    setErrors({ ...errors, [name]: '' });
  };

  const handleToggleSubRole = (subRole) => {
    const selected = formData.subRoles.includes(subRole)
      ? formData.subRoles.filter((s) => s !== subRole)
      : [...formData.subRoles, subRole];
    setFormData({ ...formData, subRoles: selected });
    aggregateSuggested(selected);
    setErrors({ ...errors, subRoles: '' });
  };

  const handleSelectAllSubRoles = () => {
    const allSubs = roleSubRoles[formData.role] || [];
    setFormData({ ...formData, subRoles: allSubs });
    aggregateSuggested(allSubs);
    setErrors({ ...errors, subRoles: '' });
  };

  const handleClearSubRoles = () => {
    setFormData({ ...formData, subRoles: [] });
    setSuggestedSkills([]);
  };

  const handleTimeChange = (e) => {
    let value = e.target.value;

    // Remove any non-digit and non-colon characters
    value = value.replace(/[^\d:]/g, '');

    // Auto-format as user types (HH:MM:SS)
    // Split by colons to handle existing format
    const parts = value.split(':');

    if (parts.length === 1) {
      // No colons yet - user is typing digits
      if (value.length <= 2) {
        // Just hours (0-23)
        setFormData({ ...formData, time: value });
      } else if (value.length === 3) {
        // Add first colon: HH:M
        setFormData({ ...formData, time: value.slice(0, 2) + ':' + value.slice(2) });
      } else if (value.length === 4) {
        // HH:MM
        setFormData({ ...formData, time: value.slice(0, 2) + ':' + value.slice(2) });
      } else if (value.length === 5) {
        // Add second colon: HH:MM:S
        setFormData({ ...formData, time: value.slice(0, 2) + ':' + value.slice(2, 4) + ':' + value.slice(4) });
      } else {
        // HH:MM:SS
        setFormData({ ...formData, time: value.slice(0, 2) + ':' + value.slice(2, 4) + ':' + value.slice(4, 6) });
      }
    } else if (parts.length === 2) {
      // Has one colon (HH:MM)
      if (parts[1].length <= 2) {
        setFormData({ ...formData, time: value });
      } else if (parts[1].length === 3) {
        // Add second colon: HH:MM:S
        setFormData({ ...formData, time: parts[0] + ':' + parts[1].slice(0, 2) + ':' + parts[1].slice(2) });
      } else {
        // HH:MM:SS
        setFormData({ ...formData, time: parts[0] + ':' + parts[1].slice(0, 2) + ':' + parts[1].slice(2, 4) });
      }
    } else if (parts.length === 3) {
      // Already has both colons (HH:MM:SS)
      // Limit each part: HH (0-23), MM (0-59), SS (0-59)
      let hours = parts[0].slice(0, 2);
      let minutes = parts[1].slice(0, 2);
      let seconds = parts[2].slice(0, 2);

      // Validate hours (0-23)
      if (hours.length === 2 && parseInt(hours) > 23) {
        hours = '23';
      }

      setFormData({ ...formData, time: `${hours}:${minutes}:${seconds} ` });
    } else {
      // Too many colons, keep only first 3 parts
      setFormData({ ...formData, time: parts.slice(0, 3).join(':') });
    }

    setErrors({ ...errors, time: '' });
  };

  const formatSecondsToHHMMSS = (totalSeconds) => {
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    const pad = (n) => n.toString().padStart(2, '0');
    return `${pad(hrs)}:${pad(mins)}:${pad(secs)} `;
  };

  const validateTimeFormat = (timeString) => {
    // Validate HH:MM:SS format
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$/;
    return timeRegex.test(timeString);
  };

  const validateForm = () => {
    const newErrors = {};
    const missingFields = [];

    // Check if resume exists OR if resumeFileName exists (for restored data from localStorage)
    // If extractedSkills exist, it means resume was already processed
    if (!formData.resume && !resumeFileName && extractedSkills.length === 0) {
      newErrors.resume = 'Please upload a resume';
      missingFields.push('Resume');
    }

    if (!formData.role) {
      newErrors.role = 'Please select a role';
      missingFields.push('Role');
    } else if (formData.role === 'other' && !formData.customRole.trim()) {
      newErrors.customRole = 'Please enter the role name';
      missingFields.push('Role Name');
    } else if (hasSubRoles(formData.role) && (!formData.subRoles || formData.subRoles.length === 0)) {
      newErrors.subRoles = 'Please select at least one sub-role';
      missingFields.push('Sub-Roles');
    }

    if (!formData.experienceLevel) {
      newErrors.experienceLevel = 'Please select an experience level';
      missingFields.push('Experience Level');
    }

    if (!formData.numberOfQuestions) {
      newErrors.numberOfQuestions = 'Please enter the number of questions';
      missingFields.push('Number of Questions');
    } else if (isNaN(formData.numberOfQuestions) || parseInt(formData.numberOfQuestions) < 1) {
      newErrors.numberOfQuestions = 'Please enter a valid number of questions';
      missingFields.push('Number of Questions');
    }

    if (!formData.time) {
      newErrors.time = 'Please enter the time';
      missingFields.push('Time');
    } else if (!validateTimeFormat(formData.time)) {
      newErrors.time = 'Please enter time in HH:MM:SS format (e.g., 01:30:00)';
      missingFields.push('Time');
    }

    const weightSum = (weights.common || 0) + (weights.role || 0) + (weights.resume || 0);
    if (weightSum !== 100) {
      newErrors.weights = 'Percentages must add up to 100.';
      missingFields.push('Percentages (must add up to 100)');
    }

    const totalQuestions = parseInt(formData.numberOfQuestions) || 0;
    const allocated = Object.values(questionDistribution).reduce((sum, c) => sum + (c || 0), 0);
    if (totalQuestions > 0 && allocated !== totalQuestions) {
      newErrors.distribution = `Please allocate exactly ${totalQuestions} questions(currently ${allocated}).`;
      missingFields.push('Question Distribution');
    }

    setErrors(newErrors);
    return {
      isValid: Object.keys(newErrors).length === 0,
      missingFields: missingFields
    };
  };

  // Validate question availability before navigation
  const validateQuestionAvailability = async () => {
    setIsValidatingQuestions(true);
    try {
      const allSkills = Object.keys(questionDistribution || {});
      if (allSkills.length === 0) {
        return { valid: false, missing: [] };
      }

      // Get difficulty based on experience level
      const difficultyMap = {
        'entry': 'easy',
        'mid': 'medium',
        'senior': 'hard',
        'expert': 'hard',
      };
      const difficulty = difficultyMap[formData.experienceLevel] || null;

      // Check availability for each skill
      const skillsParam = allSkills.join(',');
      const apiParams = {
        skills: skillsParam,
        visibility: 'GLOBAL'
      };

      if (difficulty) {
        apiParams.difficulty = difficulty;
      }

      const response = await axios.get(`${API_BASE_URL} /questions/by - skills / `, {
        params: apiParams
      });

      const missingSkills = [];
      if (response.data && response.data.questions_by_topic) {
        allSkills.forEach(skill => {
          const availableCount = (response.data.questions_by_topic[skill] || []).length;
          const requiredCount = questionDistribution[skill] || 0;

          if (requiredCount > 0 && availableCount < requiredCount) {
            missingSkills.push({
              skill,
              required: requiredCount,
              available: availableCount,
              missing: requiredCount - availableCount
            });
          }
        });
      }

      return {
        valid: missingSkills.length === 0,
        missing: missingSkills
      };
    } catch (error) {
      console.error('Error validating questions:', error);
      return { valid: false, missing: [], error: error.message };
    } finally {
      setIsValidatingQuestions(false);
    }
  };

  // Handle cancel/navigation with unsaved changes check
  const handleCancel = (targetPath = '/dashboard') => {
    if (hasUnsavedChanges()) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave? Your data will be saved automatically, but you may need to re-upload the resume file if you return.'
      );
      if (confirmed) {
        // Save current data before leaving
        saveFormDataToLocalStorage();
        navigate(targetPath);
      }
      // If not confirmed, stay on the page
    } else {
      // No unsaved changes, navigate directly
      navigate(targetPath);
    }
  };

  /**
   * Resolve a server-backed CustomAssessment id to be used for:
   * - linking manual questions (MCQ/MSQ/TF/PDF uploads) via custom_assessment_id
   * - creating final Assessment from Review page
   *
   * We previously reused a localStorage "draft" id without verifying it exists in DB.
   * If the DB was reset (or running in a different environment), that stale id causes:
   * "Custom assessment ID X was not found" when saving manual questions.
   */
  const resolveCustomAssessmentId = useCallback(async (payload) => {
    const clearDraft = () => {
      try {
        localStorage.removeItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
      } catch {
        // ignore
      }
    };

    let draftId = null;
    try {
      const existingDraftId = localStorage.getItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY);
      const parsed = Number(existingDraftId);
      if (existingDraftId && !Number.isNaN(parsed) && parsed > 0) {
        draftId = parsed;
      }
    } catch {
      // ignore
    }

    // If we have a draft id, verify it actually exists in the backend DB before reusing it.
    if (draftId) {
      try {
        await axios.get(`${API_BASE_URL} /custom-assessments/${draftId}/`);
        return draftId;
      } catch (err) {
        // Stale/invalid draft id or backend unavailable — don't trust it.
        clearDraft();
      }
    }

    // Create a new CustomAssessment record
    try {
      const saveResponse = await axios.post(`${API_BASE_URL}/custom-assessments/`, payload);
      const newId = saveResponse?.data?.id;
      if (newId) {
        try {
          localStorage.setItem(DRAFT_CUSTOM_ASSESSMENT_ID_KEY, String(newId));
        } catch {
          // ignore
        }
        return newId;
      }
    } catch (error) {
      console.error('Error saving custom assessment:', error);
      clearDraft();
    }

    return null;
  }, []);

  const handleNext = async (e) => {
    e.preventDefault();
    const validation = validateForm();

    if (!validation.isValid) {
      // Show modal with missing mandatory fields
      setMissingMandatoryFields(validation.missingFields);
      setShowMandatoryFieldsModal(true);
      return;
    }

    // If validation passes, continue with question availability check
    // Validate question availability first
    const questionValidation = await validateQuestionAvailability();

    if (!questionValidation.valid && questionValidation.missing.length > 0) {
      // Show error modal with missing questions
      setMissingQuestionsData(questionValidation);
      setShowQuestionValidationModal(true);
      return;
    }

    // Get user from localStorage for payload
    let userData = {
      first_name: '',
      last_name: '',
      email: '',
      organization_name: '',
    };
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        userData = JSON.parse(storedUser);
      }
    } catch {
      // ignore parse errors
    }

    // Prepare payload for backend to store full custom assessment
    const payload = {
      user: {
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        email: userData.email || '',
        organization_name: userData.organization_name || '',
      },
      assessment: {
        role: formData.role,
        sub_roles: formData.subRoles || [],
        custom_role: formData.customRole || '',
        experience_level: formData.experienceLevel,
        number_of_questions: parseInt(formData.numberOfQuestions, 10),
        time: formData.time,
        auto_time: autoTime,
        weights: {
          common: weights.common,
          role: weights.role,
          resume: weights.resume,
        },
        question_distribution: questionDistribution,
        removed_skills: removedSkills,
        extracted_skills: extractedSkills,
        suggested_skills: suggestedSkills,
        common_skills: commonSkills,
        resume_file_name: resumeFileName,
      },
    };

    const savedAssessmentId = await resolveCustomAssessmentId(payload);

    // Prepare assessment data to pass to review page
    const assessmentData = {
      formData,
      extractedSkills,
      suggestedSkills,
      commonSkills,
      questionDistribution,
      removedSkills,
      weights,
      autoTime,
      resumeFileName,
      role: formData.role,
      subRoles: formData.subRoles,
      customRole: formData.customRole,
      experienceLevel: formData.experienceLevel,
      numberOfQuestions: formData.numberOfQuestions,
      time: formData.time,
      // Backend record id (if saved)
      customAssessmentId: savedAssessmentId,
    };

    // Save form data to localStorage before navigation
    saveFormDataToLocalStorage();

    // Navigate to review page with assessment data
    navigate('/review-assessment', { state: assessmentData });
  };

  const handleProceedAnyway = async () => {
    setShowQuestionValidationModal(false);

    // Get user from localStorage for payload
    let userData = {
      first_name: '',
      last_name: '',
      email: '',
      organization_name: '',
    };
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        userData = JSON.parse(storedUser);
      }
    } catch {
      // ignore parse errors
    }

    // Prepare payload for backend to store full custom assessment even if
    // some skills have fewer questions than requested.
    const payload = {
      user: {
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        email: userData.email || '',
        organization_name: userData.organization_name || '',
      },
      assessment: {
        role: formData.role,
        sub_roles: formData.subRoles || [],
        custom_role: formData.customRole || '',
        experience_level: formData.experienceLevel,
        number_of_questions: parseInt(formData.numberOfQuestions, 10),
        time: formData.time,
        auto_time: autoTime,
        weights: {
          common: weights.common,
          role: weights.role,
          resume: weights.resume,
        },
        question_distribution: questionDistribution,
        removed_skills: removedSkills,
        extracted_skills: extractedSkills,
        suggested_skills: suggestedSkills,
        common_skills: commonSkills,
        resume_file_name: resumeFileName,
      },
    };

    const savedAssessmentId = await resolveCustomAssessmentId(payload);

    // Prepare assessment data to pass to review page
    const assessmentData = {
      formData,
      extractedSkills,
      suggestedSkills,
      commonSkills,
      questionDistribution,
      removedSkills,
      weights,
      autoTime,
      resumeFileName,
      role: formData.role,
      subRoles: formData.subRoles,
      customRole: formData.customRole,
      experienceLevel: formData.experienceLevel,
      numberOfQuestions: formData.numberOfQuestions,
      time: formData.time,
      customAssessmentId: savedAssessmentId,
    };

    // Save form data to localStorage before navigation
    saveFormDataToLocalStorage();

    // Navigate to review page with assessment data
    navigate('/review-assessment', { state: assessmentData });
  };

  return (
    <div className="custom-assessment-container">

      {/* Main Content */}
      <div className="page-container">
        <div className="form-wrapper">
          <h1 className="page-title">Custom Assessment</h1>
          <p className="page-subtitle">Create a custom assessment by uploading a resume and configuring the assessment parameters.</p>

          <form className="assessment-form">
            {/* Upload Resume */}
            <div className="form-group">
              <label htmlFor="resume" className="form-label">
                Upload Resume <span className="required">*</span>
              </label>
              <div className="file-upload-container">
                <input
                  ref={fileInputRef}
                  type="file"
                  id="resume"
                  name="resume"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="file-input"
                />
                {!resumeFileName ? (
                  <label htmlFor="resume" className="file-upload-label">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                      <path d="M14 2v6h6" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                      <path d="M16 13H8" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                      <path d="M16 17H8" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                      <path d="M10 9H8" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    </svg>
                    <span>Choose file or drag it here</span>
                  </label>
                ) : (
                  <div className="file-uploaded-container">
                    <div className="file-uploaded-info">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                        <path d="M14 2v6h6" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                        <path d="M9 12l2 2 4-4" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                      </svg>
                      <span className="file-name-uploaded">{resumeFileName}</span>
                    </div>
                    <div className="file-actions">
                      <button
                        type="button"
                        onClick={handleReuploadResume}
                        className="btn-file-action btn-reupload"
                      >
                        Reupload
                      </button>
                      <button
                        type="button"
                        onClick={handleRemoveResume}
                        className="btn-file-action btn-remove"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
              {errors.resume && <span className="error-message">{errors.resume}</span>}
              <p className="form-hint">Accepted formats: PDF, DOC, DOCX (Max 10MB)</p>
            </div>

            {/* Skills Field - Only show when resume is uploaded */}
            {resumeFileName && (
              <div className="form-group">
                <label className="form-label">
                  Skills Found in Resume
                </label>
                {isExtractingSkills ? (
                  <div className="skills-loading">
                    <div className="spinner"></div>
                    <span>Extracting skills from resume...</span>
                  </div>
                ) : extractedSkills.length > 0 ? (
                  <div className="skills-container">
                    <div className="skills-tags">
                      {extractedSkills.map((skill, index) => (
                        <span key={index} className="skill-tag">
                          {skill}
                          <button
                            type="button"
                            onClick={() => handleRemoveSkill(skill)}
                            className="skill-remove-btn"
                            aria-label={`Remove ${skill}`}
                            title={`Remove ${skill}`}
                          >
                            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M10.5 3.5L3.5 10.5M3.5 3.5L10.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          </button>
                        </span>
                      ))}
                    </div>
                    {extractedSkills.length > 0 && (
                      <p className="form-hint" style={{ marginTop: '0.5rem', fontSize: '0.625rem' }}>
                        Click the × button on any skill to remove it
                      </p>
                    )}
                  </div>
                ) : null}
              </div>
            )}

            {/* Role */}
            <div className="form-group">
              <label htmlFor="role" className="form-label">
                Role <span className="required">*</span>
              </label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                className={`form-select ${errors.role ? 'error' : ''}`}
              >
                <option value="">Select role</option>
                <optgroup label="Development">
                  <option value="software-engineer">Software Engineer / Software Developer</option>
                  <option value="frontend-developer">Frontend Developer</option>
                  <option value="backend-developer">Backend Developer</option>
                  <option value="full-stack-developer">Full Stack Developer</option>
                  <option value="mobile-developer">Mobile Developer (iOS/Android)</option>
                </optgroup>
                <optgroup label="DevOps & Infrastructure">
                  <option value="devops-engineer">DevOps Engineer</option>
                  <option value="cloud-engineer">Cloud Engineer</option>
                  <option value="system-administrator">System Administrator</option>
                  <option value="site-reliability-engineer">Site Reliability Engineer (SRE)</option>
                </optgroup>
                <optgroup label="Data & Analytics">
                  <option value="data-engineer">Data Engineer</option>
                  <option value="data-scientist">Data Scientist</option>
                  <option value="machine-learning-engineer">Machine Learning Engineer</option>
                  <option value="data-analyst">Data Analyst</option>
                  <option value="business-intelligence-analyst">Business Intelligence Analyst</option>
                </optgroup>
                <optgroup label="Quality & Testing">
                  <option value="qa-engineer">QA Engineer / Test Engineer</option>
                  <option value="test-automation-engineer">Test Automation Engineer</option>
                  <option value="quality-assurance-lead">Quality Assurance Lead</option>
                </optgroup>
                <optgroup label="Security">
                  <option value="security-engineer">Security Engineer</option>
                  <option value="cybersecurity-engineer">Cybersecurity Engineer</option>
                  <option value="information-security-analyst">Information Security Analyst</option>
                </optgroup>
                <optgroup label="Database & Systems">
                  <option value="database-administrator">Database Administrator (DBA)</option>
                  <option value="database-developer">Database Developer</option>
                  <option value="network-engineer">Network Engineer</option>
                </optgroup>
                <optgroup label="Design & Product">
                  <option value="ui-ux-designer">UI/UX Designer</option>
                  <option value="product-manager">Product Manager</option>
                  <option value="product-owner">Product Owner</option>
                </optgroup>
                <optgroup label="Leadership & Architecture">
                  <option value="technical-lead">Technical Lead</option>
                  <option value="solution-architect">Solution Architect</option>
                  <option value="software-architect">Software Architect</option>
                  <option value="engineering-manager">Engineering Manager</option>
                </optgroup>
                <optgroup label="Business & Project Management">
                  <option value="business-analyst">Business Analyst</option>
                  <option value="scrum-master">Scrum Master</option>
                  <option value="project-manager">Project Manager</option>
                  <option value="technical-project-manager">Technical Project Manager</option>
                </optgroup>
                <optgroup label="Other">
                  <option value="support-engineer">Support Engineer</option>
                  <option value="technical-writer">Technical Writer</option>
                  <option value="other">Other</option>
                </optgroup>
              </select>
              {errors.role && <span className="error-message">{errors.role}</span>}

              {/* Sub-Role Selection - Show when role has sub-roles */}
              {hasSubRoles(formData.role) && (
                <div style={{ marginTop: '0.75rem' }}>
                  <label className="form-label">
                    Sub-Roles <span className="required">*</span>
                  </label>
                  <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                    <button
                      type="button"
                      onClick={handleSelectAllSubRoles}
                      className="btn btn-secondary"
                      style={{ padding: '0.35rem 0.75rem' }}
                    >
                      Select all
                    </button>
                    <button
                      type="button"
                      onClick={handleClearSubRoles}
                      className="btn btn-secondary"
                      style={{ padding: '0.35rem 0.75rem' }}
                    >
                      Clear
                    </button>
                  </div>
                  <div className={`subrole-checkbox-list ${errors.subRoles ? 'error' : ''}`}>
                    {roleSubRoles[formData.role].map((subRole, index) => (
                      <label key={index} className="subrole-checkbox-item">
                        <input
                          type="checkbox"
                          checked={formData.subRoles.includes(subRole)}
                          onChange={() => handleToggleSubRole(subRole)}
                        />
                        <span>{subRole}</span>
                      </label>
                    ))}
                  </div>
                  {errors.subRoles && <span className="error-message">{errors.subRoles}</span>}

                  {/* Suggested Skills based on Sub-Roles */}
                  {suggestedSkills.length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block' }}>
                        Suggested Skills for {formData.subRoles && formData.subRoles.length > 0 ? formData.subRoles.join(', ') : 'selected sub-roles'}
                      </label>
                      <div className="skills-container">
                        <div className="skills-tags">
                          {suggestedSkills.map((skill, index) => (
                            <span key={index} className="skill-tag suggested-skill">
                              {skill}
                            </span>
                          ))}
                        </div>
                        <p className="form-hint" style={{ marginTop: '0.5rem', fontSize: '0.625rem' }}>
                          These are suggested skills for the selected sub-roles. Skills extracted from resume are shown above.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Common Skills - Skills that match between resume and suggested */}
                  {commonSkills.length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', color: '#059669', fontWeight: '600' }}>
                        ✓ Common Skills ({commonSkills.length})
                      </label>
                      <div className="skills-container">
                        <div className="skills-tags">
                          {commonSkills.map((skill, index) => (
                            <span key={index} className="skill-tag common-skill">
                              {skill}
                            </span>
                          ))}
                        </div>
                        <p className="form-hint" style={{ marginTop: '0.5rem', fontSize: '0.625rem' }}>
                          These skills are found in both the resume and the suggested skills for the selected sub-roles.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Custom Role Input - Show when "Other" is selected */}
              {formData.role === 'other' && (
                <div style={{ marginTop: '0.75rem' }}>
                  <label htmlFor="customRole" className="form-label">
                    Enter Role Name <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="customRole"
                    name="customRole"
                    value={formData.customRole}
                    onChange={handleInputChange}
                    placeholder="Enter custom role name"
                    className={`form-input ${errors.customRole ? 'error' : ''}`}
                  />
                  {errors.customRole && <span className="error-message">{errors.customRole}</span>}
                </div>
              )}
            </div>

            {/* Experience Level */}
            <div className="form-group">
              <label htmlFor="experienceLevel" className="form-label">
                Experience Level <span className="required">*</span>
              </label>
              <select
                id="experienceLevel"
                name="experienceLevel"
                value={formData.experienceLevel}
                onChange={handleInputChange}
                className={`form-select ${errors.experienceLevel ? 'error' : ''}`}
              >
                <option value="">Select experience level</option>
                <option value="entry">Entry Level (0-2 years)</option>
                <option value="mid">Mid Level (2-5 years)</option>
                <option value="senior">Senior Level (5-10 years)</option>
                <option value="expert">Expert Level (10+ years)</option>
              </select>
              {errors.experienceLevel && <span className="error-message">{errors.experienceLevel}</span>}
            </div>

            {/* Adjust Percentages */}
            <div className="form-group">
              <label className="form-label">Adjust Percentages (must add up to 100)</label>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <div style={{ flex: '1 1 150px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#374151' }}>Common (%)</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={weights.common}
                    onChange={(e) => handleWeightChange('common', e.target.value)}
                    className="form-input"
                  />
                </div>
                <div style={{ flex: '1 1 150px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#374151' }}>Role (%)</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={weights.role}
                    onChange={(e) => handleWeightChange('role', e.target.value)}
                    className="form-input"
                  />
                </div>
                <div style={{ flex: '1 1 150px' }}>
                  <span style={{ fontSize: '0.75rem', color: '#374151' }}>Resume (%)</span>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={weights.resume}
                    onChange={(e) => handleWeightChange('resume', e.target.value)}
                    className="form-input"
                  />
                </div>
              </div>
              <p className="form-hint" style={{ marginTop: '0.5rem' }}>
                Default: 70 / 15 / 15. If sum is 0, the default 70 / 15 / 15 is used automatically.
              </p>
              {((weights.common || 0) + (weights.role || 0) + (weights.resume || 0)) !== 100 && (
                <p className="error-message" style={{ marginTop: '0.25rem' }}>
                  Current sum is {(weights.common || 0) + (weights.role || 0) + (weights.resume || 0)}. We’ll normalize automatically, but please adjust to 100 for clarity.
                </p>
              )}
              {errors.weights && <span className="error-message">{errors.weights}</span>}
            </div>

            {/* Number of Questions */}
            <div className="form-group">
              <label htmlFor="numberOfQuestions" className="form-label">
                Number of Questions to Conduct <span className="required">*</span>
              </label>
              <input
                type="number"
                id="numberOfQuestions"
                name="numberOfQuestions"
                value={formData.numberOfQuestions}
                onChange={handleInputChange}
                min="1"
                placeholder="Enter number of questions"
                className={`form-input ${errors.numberOfQuestions ? 'error' : ''}`}
              />
              {errors.numberOfQuestions && <span className="error-message">{errors.numberOfQuestions}</span>}

              {/* Question Distribution Breakdown */}
              {formData.numberOfQuestions && parseInt(formData.numberOfQuestions) > 0 && Object.keys(questionDistribution).length > 0 && (
                <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem' }}>
                  <label className="form-label" style={{ marginBottom: '0.75rem', display: 'block', fontWeight: '600' }}>
                    Question Distribution Breakdown
                  </label>

                  {/* Summary */}
                  <div style={{ marginBottom: '1rem', padding: '0.75rem', backgroundColor: '#fff', borderRadius: '0.375rem', border: '1px solid #e5e7eb' }}>
                    {(() => {
                      const total = parseInt(formData.numberOfQuestions) || 0;
                      const allocatedTotal = Object.values(questionDistribution).reduce((sum, count) => sum + (count || 0), 0);
                      const remainingTotal = Math.max(total - allocatedTotal, 0);
                      const overTotal = Math.max(allocatedTotal - total, 0);
                      const commonTotal = Object.entries(questionDistribution)
                        .filter(([skill]) => commonSkills.some(cs => cs.toLowerCase().trim() === skill.toLowerCase().trim()))
                        .reduce((sum, [, count]) => sum + (count || 0), 0);
                      const roleTotal = Object.entries(questionDistribution)
                        .filter(([skill]) => suggestedSkills.some(rs => rs.toLowerCase().trim() === skill.toLowerCase().trim()) &&
                          !commonSkills.some(cs => cs.toLowerCase().trim() === skill.toLowerCase().trim()))
                        .reduce((sum, [, count]) => sum + (count || 0), 0);
                      const resumeTotal = Object.entries(questionDistribution)
                        .filter(([skill]) => !commonSkills.some(cs => cs.toLowerCase().trim() === skill.toLowerCase().trim()) &&
                          !suggestedSkills.some(rs => rs.toLowerCase().trim() === skill.toLowerCase().trim()))
                        .reduce((sum, [, count]) => sum + (count || 0), 0);

                      return (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', paddingBottom: '0.5rem', borderBottom: '1px solid #e5e7eb' }}>
                            <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#374151' }}>Total Allocated:</span>
                            <span style={{ fontSize: '0.75rem', fontWeight: '700', color: allocatedTotal === total ? '#059669' : '#dc2626' }}>
                              {allocatedTotal} / {total} questions
                            </span>
                          </div>
                          {remainingTotal > 0 && (
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', alignItems: 'center' }}>
                              <span style={{ fontSize: '0.75rem', color: '#dc2626' }}>
                                Remaining to allocate: {remainingTotal} {remainingTotal === 1 ? 'question' : 'questions'}
                              </span>
                              {commonSkills.length > 0 && (
                                <button
                                  type="button"
                                  onClick={handleRebalanceRemaining}
                                  style={{
                                    padding: '0.4rem 0.75rem',
                                    backgroundColor: '#2563eb',
                                    color: '#fff',
                                    border: 'none',
                                    borderRadius: '0.375rem',
                                    cursor: 'pointer',
                                    fontSize: '0.625rem',
                                    fontWeight: '600',
                                  }}
                                  onMouseEnter={(e) => { e.target.style.backgroundColor = '#1d4ed8'; }}
                                  onMouseLeave={(e) => { e.target.style.backgroundColor = '#2563eb'; }}
                                >
                                  Rebalance to common skills
                                </button>
                              )}
                            </div>
                          )}
                          {overTotal > 0 && (
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem', alignItems: 'center' }}>
                              <span style={{ fontSize: '0.75rem', color: '#dc2626' }}>
                                Over-allocated by {overTotal} {overTotal === 1 ? 'question' : 'questions'} — reduce some counts.
                              </span>
                            </div>
                          )}
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', marginTop: '0.5rem' }}>
                            <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Common Skills ({weights.common}%):</span>
                            <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#059669' }}>
                              {commonTotal} {commonTotal === 1 ? 'question' : 'questions'}
                            </span>
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Role Skills ({weights.role}%):</span>
                            <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#16a34a' }}>
                              {roleTotal} {roleTotal === 1 ? 'question' : 'questions'}
                            </span>
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Resume Skills ({weights.resume}%):</span>
                            <span style={{ fontSize: '0.75rem', fontWeight: '600', color: '#2563eb' }}>
                              {resumeTotal} {resumeTotal === 1 ? 'question' : 'questions'}
                            </span>
                          </div>
                        </>
                      );
                    })()}
                  </div>

                  {/* Skills with question counts */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {Object.entries(questionDistribution)
                      .sort((a, b) => b[1] - a[1]) // Sort by question count descending
                      .map(([skill, count]) => {
                        const normalizedSkill = skill.toLowerCase().trim();
                        const isCommonSkill = commonSkills.some(cs => cs.toLowerCase().trim() === normalizedSkill);
                        const isRoleSkill = suggestedSkills.some(rs => rs.toLowerCase().trim() === normalizedSkill);
                        const borderColor = isCommonSkill ? '#fcd34d' : isRoleSkill ? '#86efac' : '#bfdbfe';
                        const bgColor = isCommonSkill ? '#fef3c7' : isRoleSkill ? '#f0fdf4' : '#eff6ff';
                        const textColor = isCommonSkill ? '#92400e' : isRoleSkill ? '#166534' : '#1e40af';
                        return (
                          <div
                            key={skill}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '0.5rem 0.75rem',
                              backgroundColor: '#fff',
                              borderRadius: '0.375rem',
                              border: `1px solid ${borderColor}`,
                            }}
                          >
                            <span style={{ fontSize: '0.75rem', fontWeight: '500', flex: 1 }}>{skill}</span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <input
                                type="number"
                                min="0"
                                value={count || 0}
                                onChange={(e) => handleUpdateSkillQuestions(skill, e.target.value)}
                                style={{
                                  width: '60px',
                                  padding: '0.25rem 0.5rem',
                                  fontSize: '0.625rem',
                                  fontWeight: '600',
                                  textAlign: 'center',
                                  border: `1px solid ${borderColor}`,
                                  borderRadius: '0.25rem',
                                  backgroundColor: bgColor,
                                  color: textColor,
                                }}
                              />
                              <button
                                type="button"
                                onClick={() => handleRemoveSkillFromDistribution(skill)}
                                style={{
                                  padding: '0.25rem 0.5rem',
                                  backgroundColor: '#fee2e2',
                                  color: '#dc2626',
                                  border: '1px solid #fca5a5',
                                  borderRadius: '0.25rem',
                                  cursor: 'pointer',
                                  fontSize: '0.625rem',
                                  fontWeight: '600',
                                  transition: 'all 0.2s'
                                }}
                                onMouseEnter={(e) => {
                                  e.target.style.backgroundColor = '#fecaca';
                                  e.target.style.borderColor = '#f87171';
                                }}
                                onMouseLeave={(e) => {
                                  e.target.style.backgroundColor = '#fee2e2';
                                  e.target.style.borderColor = '#fca5a5';
                                }}
                                title="Remove this skill"
                              >
                                ×
                              </button>
                            </div>
                          </div>
                        );
                      })}
                  </div>

                  <p className="form-hint" style={{ marginTop: '0.75rem', fontSize: '0.75rem' }}>
                    Questions are distributed based on the selected percentages: Common (yellow), Role (green), Resume (blue).
                    You can edit question counts for each skill or remove skills. Questions from removed/zero-count skills are automatically redistributed to common skills.
                  </p>

                  {/* Removed skills with restore option */}
                  {removedSkills.length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <label className="form-label" style={{ marginBottom: '0.5rem', display: 'block', color: '#dc2626', fontWeight: '600' }}>
                        Removed Skills (click restore to add back)
                      </label>
                      <div className="skills-tags">
                        {removedSkills.map((skill, index) => (
                          <span key={index} className="skill-tag removed-skill">
                            {skill}
                            <button
                              type="button"
                              onClick={() => handleRestoreSkill(skill)}
                              className="skill-restore-btn"
                              aria-label={`Restore ${skill}`}
                              title={`Restore ${skill}`}
                            >
                              Restore
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Time */}
            <div className="form-group">
              <label htmlFor="time" className="form-label">
                Time (HH:MM:SS) <span className="required">*</span>
              </label>
              <input
                type="text"
                id="time"
                name="time"
                value={formData.time}
                onChange={handleTimeChange}
                placeholder="HH:MM:SS (e.g., 01:30:00)"
                maxLength="8"
                className={`form-input ${errors.time ? 'error' : ''}`}
              />
              {errors.time && <span className="error-message">{errors.time}</span>}
              <p className="form-hint">
                Format: Hours:Minutes:Seconds (e.g., 01:30:00). Auto-calculated at 2 minutes per question: {autoTime || '00:00:00'}.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="form-actions">
              <button type="button" onClick={() => handleCancel('/dashboard')} className="btn btn-secondary">
                Cancel
              </button>
              <button
                type="button"
                onClick={handleNext}
                className="btn btn-primary"
                disabled={isValidatingQuestions}
              >
                {isValidatingQuestions ? 'Validating...' : 'Next'}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Question Validation Error Modal */}
      {showQuestionValidationModal && missingQuestionsData && (
        <div className="modal-container">
          <div className="modal-backdrop" onClick={() => setShowQuestionValidationModal(false)} />
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">Insufficient Questions Available</h2>
              <button
                onClick={() => setShowQuestionValidationModal(false)}
                className="modal-close-btn"
                aria-label="Close"
                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.125rem', color: '#6b7280' }}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
                The following skills do not have enough questions in the database to meet your requirements:
              </p>
              <div style={{ marginBottom: '1.5rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                      <th style={{ padding: '0.75rem', textAlign: 'left', fontWeight: '600', color: '#374151' }}>Skill</th>
                      <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Required</th>
                      <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Available</th>
                      <th style={{ padding: '0.75rem', textAlign: 'center', fontWeight: '600', color: '#374151' }}>Missing</th>
                    </tr>
                  </thead>
                  <tbody>
                    {missingQuestionsData.missing.map((item, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                        <td style={{ padding: '0.75rem', fontWeight: '500', color: '#1f2937' }}>{item.skill}</td>
                        <td style={{ padding: '0.75rem', textAlign: 'center', color: '#1f2937' }}>{item.required}</td>
                        <td style={{ padding: '0.75rem', textAlign: 'center', color: '#059669' }}>{item.available}</td>
                        <td style={{ padding: '0.75rem', textAlign: 'center', color: '#dc2626', fontWeight: '600' }}>{item.missing}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div style={{ padding: '1rem', backgroundColor: '#fef3c7', border: '1px solid #fcd34d', borderRadius: '0.5rem', marginBottom: '1.5rem' }}>
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#92400e' }}>
                  <strong>Options:</strong>
                </p>
                <ul style={{ margin: '0.5rem 0 0 1.5rem', padding: 0, fontSize: '0.75rem', color: '#92400e' }}>
                  <li>Remove or reduce questions for skills with insufficient questions</li>
                  <li>Add other skills that have questions available in the database</li>
                  <li>Proceed anyway (only available questions will be shown)</li>
                </ul>
              </div>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setShowQuestionValidationModal(false)}
                  className="btn btn-secondary"
                  style={{ padding: '0.75rem 1.5rem' }}
                >
                  Stay & Adjust
                </button>
                <button
                  onClick={handleProceedAnyway}
                  className="btn btn-primary"
                  style={{ padding: '0.75rem 1.5rem' }}
                >
                  Proceed Anyway
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mandatory Fields Validation Modal */}
      {showMandatoryFieldsModal && (
        <div className="modal-container">
          <div className="modal-backdrop" onClick={() => setShowMandatoryFieldsModal(false)} />
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">Required Fields Missing</h2>
              <button
                onClick={() => setShowMandatoryFieldsModal(false)}
                className="modal-close-btn"
                aria-label="Close"
                style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.125rem', color: '#6b7280' }}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
                Please fill all mandatory fields before proceeding:
              </p>
              <div style={{ marginBottom: '1.5rem' }}>
                <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#374151' }}>
                  {missingMandatoryFields.map((field, index) => (
                    <li key={index} style={{ marginBottom: '0.5rem', fontSize: '0.75rem' }}>
                      {field}
                    </li>
                  ))}
                </ul>
              </div>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => setShowMandatoryFieldsModal(false)}
                  className="btn btn-primary"
                  style={{ padding: '0.75rem 1.5rem' }}
                >
                  OK, I'll Fill Them
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomAssessment;


