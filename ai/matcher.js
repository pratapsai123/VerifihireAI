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

        if (selectedCandidateId) {
            formData.append('candidate_id', selectedCandidateId);
        } else {
            formData.append('resume', resumeFile);
        }

        try {
            const response = await fetch('http://localhost:8001/api/candidates/match/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Analysis failed. Please check the backend.');
            }

            const data = await response.json();
            showResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to analyze resume. Ensure the backend is running with a valid Gemini API key.');
            matchBtn.disabled = false;
            matchBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze Match';
        }
    });

    function showResults(data) {
        // Hide inputs, show results
        inputSection.style.display = 'none';
        actionSection.style.display = 'none';
        resultSection.style.display = 'block';

        // Set score and circle
        const percentage = data.match_percentage;
        scoreValue.textContent = `${percentage}%`;
        progressCircle.style.background = `conic-gradient(var(--blue-primary, #4318FF) ${percentage}%, #eef2ff ${percentage}%)`;

        // Set badge
        if (data.is_eligible) {
            eligibilityBadge.textContent = 'Eligible';
            eligibilityBadge.className = 'status-badge status-new'; // Reusing green style
        } else {
            eligibilityBadge.textContent = 'Not Eligible';
            eligibilityBadge.className = 'status-badge status-review'; // Reusing orange style
        }

        // Set summary
        matchSummary.textContent = data.summary;
    }
});
