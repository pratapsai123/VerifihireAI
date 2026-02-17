document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const resumeInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('fileName');
    const jobDescInput = document.getElementById('jobDesc');
    const matchBtn = document.getElementById('matchBtn');
    
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
        }
    });

    // Match Analysis
    matchBtn.addEventListener('click', async () => {
        const resumeFile = resumeInput.files[0];
        const jobDescription = jobDescInput.value.trim();

        if (!resumeFile || !jobDescription) {
            alert('Please provide both a resume and a job description.');
            return;
        }

        // UI Feedback: Loading
        matchBtn.disabled = true;
        matchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        const formData = new FormData();
        formData.append('resume', resumeFile);
        formData.append('job_description', jobDescription);

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
