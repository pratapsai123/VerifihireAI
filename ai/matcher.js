document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const resumeInput = document.getElementById('resumeFile');
    const fileNameDisplay = document.getElementById('fileName');
    const jobDescInput = document.getElementById('jobDesc');
    const matchBtn = document.getElementById('matchBtn');

    // New Threshold Slider
    const thresholdRange = document.getElementById('thresholdRange');
    const thresholdValue = document.getElementById('thresholdValue');

    if (thresholdRange && thresholdValue) {
        thresholdRange.addEventListener('input', (e) => {
            thresholdValue.textContent = `${e.target.value}%`;
        });
    }

    // Result Elements
    const inputSection = document.getElementById('inputSection');
    const actionSection = document.getElementById('actionSection');
    const resultSection = document.getElementById('resultSection');

    // Drag and Drop
    dropZone.addEventListener('click', () => resumeInput.click());

    resumeInput.addEventListener('change', () => {
        handleFiles(resumeInput.files);
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
            // Visual feedback
            dropZone.style.borderColor = '#4318FF';
            dropZone.style.background = '#F0F2F9';
        }
    }

    // Match Analysis
    matchBtn.addEventListener('click', async () => {
        const files = resumeInput.files;
        const jobDescription = jobDescInput.value.trim();
        const threshold = thresholdRange ? thresholdRange.value : 70;

        if (files.length === 0 || !jobDescription) {
            alert('Please provide at least one resume and a job description.');
            return;
        }

        // UI Feedback: Loading
        matchBtn.disabled = true;
        matchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing ' + files.length + ' resume(s)...';

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('resume', files[i]);
        }
        formData.append('job_description', jobDescription);
        formData.append('threshold', threshold); // Send threshold to backend if supported (or use for client-side filtering)

        try {
            // Using port 8001 (VerifiHireAI Backend)
            const response = await fetch('http://localhost:8001/api/ai-candidates/match/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || 'Analysis failed. Please check backend.');
            }

            const data = await response.json();
            // Expecting data to be an array of results or a single object if only 1
            // Adjust according to backend response structure.
            // If backend returns single object for single file, wrap it.

            // NOTE: The current backend might return a single result or list depending on implementation.
            // Let's handle both.

            showResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert(`Failed to analyze: ${error.message}`);
        } finally {
            matchBtn.disabled = false;
            matchBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Analyze Match';
        }
    });

    function showResults(results) {
        // Hide inputs, show results
        inputSection.style.display = 'none';
        actionSection.style.display = 'none';
        resultSection.style.display = 'block';

        // Clear previous results
        resultSection.innerHTML = `
            <div class="result-header" style="text-align: center; margin-bottom: 2rem;">
                <h2 style="font-size: 2rem; background: linear-gradient(135deg, var(--navy-secondary), var(--blue-secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Analysis Results</h2>
                <button class="auth-primary-btn" onclick="location.reload()" style="margin: 1.5rem auto; padding: 0.75rem 2rem; font-size: 1rem;">
                    <i class="fa-solid fa-rotate-right"></i> Analyze More
                </button>
            </div>
            <div class="results-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem;">
                <!-- Results injected here -->
            </div>
        `;

        const grid = resultSection.querySelector('.results-grid');

        // Handle single object response (backward compatibility) or array
        const resultsArray = Array.isArray(results) ? results : [results];

        resultsArray.forEach(data => {
            const card = document.createElement('div');
            card.className = 'matcher-card result-card-item';

            // Ensure we handle data structure safely
            const isEligible = data.is_eligible;
            const badgeClass = isEligible ? 'status-badge status-new' : 'status-badge status-review';
            const badgeText = isEligible ? 'Eligible' : 'Not Eligible';
            const percentage = data.match_percentage || 0;
            const filename = data.filename || 'Candidate Resume';
            const summary = data.summary || 'No summary provided.';

            // Generate distinct color for progress based on score
            const progressColor = percentage >= 70 ? '#05CD99' : (percentage >= 40 ? '#FFB547' : '#EE5D50');

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                    <h4 style="margin: 0; font-size: 1.1rem; color: var(--navy-secondary); display: flex; align-items: center; gap: 0.5rem; max-width: 65%;">
                        <i class="fa-solid fa-file-pdf" style="color: var(--blue-accent);"></i> 
                        <span style="text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">${filename}</span>
                    </h4>
                    <span class="${badgeClass}">${badgeText}</span>
                </div>
                
                <div style="display: flex; flex-direction: column; align-items: center; margin: 2rem 0;">
                    <div style="position: relative; width: 140px; height: 140px; border-radius: 50%; background: conic-gradient(${progressColor} ${percentage}%, #F0F2F9 ${percentage}%); display: flex; align-items: center; justify-content: center; box-shadow: inset 0 0 10px rgba(0,0,0,0.05);">
                        <div style="position: absolute; width: 115px; height: 115px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                            <span style="font-size: 2rem; font-weight: 800; color: var(--navy-secondary);">${percentage}%</span>
                        </div>
                    </div>
                    <p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.9rem;">Match Score</p>
                </div>

                <div style="background: #F8F9FF; padding: 1.5rem; border-radius: 16px; min-height: 120px;">
                    <h5 style="margin: 0 0 0.5rem 0; color: var(--navy-secondary); font-size: 0.95rem;">AI Summary</h5>
                    <p style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; margin: 0;">${summary}</p>
                </div>
                
                <button class="action-btn" style="width: 100%; margin-top: 1.5rem; justify-content: center; display: flex;" onclick="alert('Detailed report feature coming soon!')">
                    View Full Report
                </button>
            `;
            grid.appendChild(card);
        });
    }
});
