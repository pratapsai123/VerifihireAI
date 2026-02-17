document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const resumeInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('fileName');
    const jobDescInput = document.getElementById('jobDesc');
    const matchBtn = document.getElementById('matchBtn');

<<<<<<< HEAD
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

=======
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
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
<<<<<<< HEAD
        if (resumeInput.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${resumeInput.files[0].name}`;
            selectedCandidateId = null; // Reset if new file selected
            fileNameDisplay.style.color = '';
            dropZone.style.borderColor = '';
            dropZone.style.backgroundColor = '';
        }
=======
        handleFiles(resumeInput.files);
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
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
<<<<<<< HEAD
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
=======
            handleFiles(resumeInput.files);
        }
    });

    function handleFiles(files) {
        if (files.length > 0) {
            if (files.length === 1) {
                fileNameDisplay.textContent = `Selected: ${files[0].name}`;
            } else {
                fileNameDisplay.textContent = `Selected: ${files.length} resumes`;
            }
            fileNameDisplay.style.display = 'block';
        }
    }

    // Match Analysis
    matchBtn.addEventListener('click', async () => {
        const files = resumeInput.files;
        const jobDescription = jobDescInput.value.trim();

        if (files.length === 0 || !jobDescription) {
            alert('Please provide at least one resume and a job description.');
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
            return;
        }

        // UI Feedback: Loading
        matchBtn.disabled = true;
<<<<<<< HEAD
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
=======
        matchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing ' + files.length + ' resume(s)...';

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('resume', files[i]);
        }
        formData.append('job_description', jobDescription);

        try {
            const response = await fetch('http://localhost:8000/api/candidates/match/', {
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Analysis failed. Please check the backend.');
            }

            const data = await response.json();
<<<<<<< HEAD
=======
            // Expecting data to be an array of results
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
            showResults(data);

        } catch (error) {
            console.error('Error:', error);
<<<<<<< HEAD
            alert('Failed to analyze resume. Ensure the backend is running with a valid Gemini API key.');
            matchBtn.disabled = false;
            matchBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze Match';
        }
    });

    function showResults(data) {
=======
            alert('Failed to analyze resumes. Ensure the backend is running with a valid Gemini API key.');
        } finally {
            matchBtn.disabled = false;
            matchBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Let\'s Analyze';
        }
    });

    function showResults(results) {
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
        // Hide inputs, show results
        inputSection.style.display = 'none';
        actionSection.style.display = 'none';
        resultSection.style.display = 'block';

<<<<<<< HEAD
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
=======
        // Clear previous results if any (though currently we hide/show sections)
        resultSection.innerHTML = `
            <div class="results-header" style="text-align: center; margin-bottom: 2rem;">
                <h2>Analysis Results</h2>
                <button class="auth-primary-btn" onclick="location.reload()" style="margin: 1rem auto; padding: 0.5rem 1.5rem; font-size: 1rem;">Analyze More</button>
            </div>
            <div class="results-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;">
                <!-- Results will be injected here -->
            </div>
        `;

        const grid = resultSection.querySelector('.results-grid');

        // Handle single object response (backward compatibility) or array
        const resultsArray = Array.isArray(results) ? results : [results];

        resultsArray.forEach(data => {
            const card = document.createElement('div');
            card.className = 'matcher-card result-card-item';

            const isEligible = data.is_eligible;
            const badgeClass = isEligible ? 'status-badge status-new' : 'status-badge status-review';
            const badgeText = isEligible ? 'Eligible' : 'Not Eligible';
            const percentage = data.match_percentage;

            // Generate distinct color for progress based on score
            const progressColor = percentage >= 70 ? '#05CD99' : (percentage >= 40 ? '#FFB547' : '#E31A1A');

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0; font-size: 1.1rem; color: var(--navy-secondary); text-overflow: ellipsis; white-space: nowrap; overflow: hidden; max-width: 200px;">
                        <i class="fa-solid fa-file-pdf"></i> ${data.filename || 'Resume'}
                    </h4>
                    <span class="${badgeClass}" style="padding: 0.25rem 0.75rem; border-radius: 100px; font-size: 0.8rem; font-weight: 600;">${badgeText}</span>
                </div>
                
                <div style="display: flex; flex-direction: column; align-items: center; margin: 1.5rem 0;">
                    <div style="position: relative; width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(${progressColor} ${percentage}%, #F0F2F9 ${percentage}%); display: flex; align-items: center; justify-content: center; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
                        <div style="position: absolute; width: 100px; height: 100px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                            <span style="font-size: 1.8rem; font-weight: 800; color: var(--navy-secondary);">${percentage}%</span>
                        </div>
                    </div>
                </div>

                <div style="background: #F8F9FF; padding: 1rem; border-radius: 12px; height: 100%;">
                    <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; margin: 0;">${data.summary}</p>
                </div>
            `;
            grid.appendChild(card);
        });
>>>>>>> 6565ae77c42e03d54aa085e6b6b788d64083a4bc
    }
});
