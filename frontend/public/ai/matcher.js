document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const resumeInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('fileName');
    const jobDescInput = document.getElementById('jobDesc');
    const matchBtn = document.getElementById('matchBtn');

    // State
    let selectedCandidateId = null;

    // Check for Candidate ID in URL
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');

    if (id) {
        fetchCandidate(id);
    }

    async function fetchCandidate(id) {
        try {
            const response = await fetch(`http://localhost:8001/api/candidates/${id}/`);
            if (response.ok) {
                const candidate = await response.json();
                selectedCandidateId = candidate.id;

                // Update UI to show candidate selected
                fileNameDisplay.textContent = `Selected: ${candidate.full_name}'s Resume (On File)`;
                fileNameDisplay.style.color = '#4318FF';
                fileNameDisplay.style.fontWeight = '500';

                // Optional: Disable file input visual or just indicate preference
                dropZone.style.borderColor = '#4318FF';
                dropZone.style.backgroundColor = '#f5f3ff';
            }
        } catch (error) {
            console.error('Error fetching candidate:', error);
        }
    }

    // Result Elements
    const inputSection = document.getElementById('inputSection');
    const actionSection = document.getElementById('actionSection');
    const resultSection = document.getElementById('resultSection');
    const scoreValue = document.getElementById('scoreValue');
    const eligibilityBadge = document.getElementById('eligibilityBadge');
    const matchSummary = document.getElementById('matchSummary');
    const progressCircle = document.querySelector('.circular-progress');

    // Drag and Drop
    dropZone.addEventListener('click', () => resumeInput.click());

    resumeInput.addEventListener('change', () => {
        if (resumeInput.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${resumeInput.files[0].name}`;
            selectedCandidateId = null; // Reset if new file selected
            fileNameDisplay.style.color = '';
            dropZone.style.borderColor = '';
            dropZone.style.backgroundColor = '';
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            resumeInput.files = e.dataTransfer.files;
            fileNameDisplay.textContent = `Selected: ${resumeInput.files[0].name}`;
            selectedCandidateId = null; // Reset
        }
    });

    // Match Analysis
    matchBtn.addEventListener('click', async () => {
        const resumeFile = resumeInput.files[0];
        const jobDescription = jobDescInput.value.trim();
        const minScore = document.getElementById('minScore').value;

        // Validation: Need (File OR CandidateID) AND JobDescription
        if ((!resumeFile && !selectedCandidateId) || !jobDescription) {
            alert('Please provide a job description and either upload a resume or select a candidate.');
            return;
        }

        // UI Feedback: Loading
        matchBtn.disabled = true;
        matchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        const formData = new FormData();
        formData.append('job_description', jobDescription);
        // formData.append('min_score', minScore); // Send this to API if supported

        if (selectedCandidateId) {
            formData.append('candidate_id', selectedCandidateId);
        } else {
            formData.append('resume', resumeFile);
        }

        try {
            const response = await fetch('http://localhost:8001/api/ai-candidates/match/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Analysis failed. Please check the backend.');
            }

            const data = await response.json();

            // Store candidate ID for decision
            if (data.candidate_id) {
                selectedCandidateId = data.candidate_id;
            }

            // Mocking list update for demo since API returns single result
            // updateResultsList(data, resumeFile ? resumeFile.name : 'Candidate Resume', minScore);

            showResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to analyze resume. Ensure the backend is running with a valid Gemini API key.');
        } finally {
            matchBtn.disabled = false;
            matchBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze Match';
        }
    });

    // Decision Handlers
    document.getElementById('approveBtn').addEventListener('click', () => updateStatus('Resume Passed'));
    document.getElementById('rejectBtn').addEventListener('click', () => updateStatus('Resume Failed'));

    async function updateStatus(status) {
        if (!selectedCandidateId) return;

        const decisionMsg = document.getElementById('decisionMessage');
        const btns = document.querySelector('.decision-actions');

        try {
            const response = await fetch(`http://localhost:8001/api/ai-candidates/${selectedCandidateId}/status/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: status })
            });

            if (response.ok) {
                btns.style.display = 'none';
                decisionMsg.style.display = 'block';
                decisionMsg.innerHTML = `
                    <p style="color: ${status === 'Resume Passed' ? 'var(--status-success)' : 'var(--status-error)'}">
                        <i class="fa-solid ${status === 'Resume Passed' ? 'fa-circle-check' : 'fa-circle-xmark'}"></i> 
                        Candidate marked as <strong>${status}</strong>.
                    </p>
                    <a href="candidates.html" class="browse-link">View in Candidates List</a>
                `;
            } else {
                alert('Failed to update status.');
            }
        } catch (error) {
            console.error('Error updating status:', error);
            alert('Error updating status.');
        }
    }

    function showResults(data) {
        // Hide inputs, show results
        inputSection.style.display = 'none';
        actionSection.style.display = 'none';
        resultSection.style.display = 'block';

        // Set score and circle
        const percentage = data.match_percentage;
        scoreValue.textContent = `${percentage}%`;

        // Update circle gradient
        scoreValue.parentElement.style.background = `conic-gradient(#4318FF ${percentage * 3.6}deg, #eef2ff 0deg)`;

        // Set badge
        if (data.is_eligible) {
            eligibilityBadge.textContent = 'Eligible';
            eligibilityBadge.className = 'status-badge status-new'; // Reusing green style
        } else {
            eligibilityBadge.textContent = 'Not Eligible';
            eligibilityBadge.className = 'status-badge status-review'; // Reusing orange style
        }

        // Set summary
        document.getElementById('matchSummary').textContent = data.summary;
    }

    function updateResultsList(data, candidateName, minScore) {
        const score = data.match_percentage;
        const isPassed = score >= minScore;

        const listId = isPassed ? 'passedList' : 'failedList';
        const container = document.getElementById(listId);
        const badge = document.querySelector(`.tab-btn[data-tab="${isPassed ? 'passed' : 'failed'}"] .badge`);

        // Create result item
        const item = document.createElement('div');
        item.className = 'feature-card matcher-card';
        item.style.marginBottom = '1rem';
        item.style.minHeight = 'auto'; // Override default
        item.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <div>
                    <h4 style="margin: 0; color: var(--navy-secondary); font-size: 1.1rem;">${candidateName}</h4>
                    <p style="margin: 0.5rem 0 0; font-size: 0.9rem;">Match: <strong>${score}%</strong></p>
                </div>
                <div class="status-badge ${isPassed ? 'status-new' : 'status-review'}">
                    ${isPassed ? 'Passed' : 'Failed'}
                </div>
            </div>
        `;

        // Remove empty state if present
        const emptyState = container.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        container.appendChild(item);

        // Update badge count
        let count = parseInt(badge.textContent) || 0;
        badge.textContent = count + 1;

        // Auto-switch tab to relevant result
        document.querySelector(`.tab-btn[data-tab="${isPassed ? 'passed' : 'failed'}"]`).click();
    }
});
