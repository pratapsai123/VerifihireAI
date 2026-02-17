document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('fileName');
    const form = document.getElementById('jobApplicationForm');

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = `Selected: ${fileInput.files[0].name}`;
        }
    });

    // Drag and Drop functionality
    dropZone.addEventListener('click', () => fileInput.click());

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
            fileInput.files = e.dataTransfer.files;
            fileNameDisplay.textContent = `Selected: ${fileInput.files[0].name}`;
        }
    });

    // Form Submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Construct FormData for file upload
        const apiData = new FormData();
        apiData.append('full_name', data.fullName);
        apiData.append('email', data.email);
        apiData.append('phone', data.phone);
        apiData.append('job_title', data.jobTitle);
        apiData.append('linkedin_url', data.linkedin || '');
        apiData.append('cover_letter', data.coverLetter || '');

        if (fileInput.files[0]) {
            apiData.append('resume', fileInput.files[0]);
        }

        // Create Candidate via API
        fetch('http://localhost:8001/api/candidates/', {
            method: 'POST',
            body: apiData // Send FormData directly
        })
            .then(response => {
                if (response.ok) {
                    // UI Feedback
                    const btn = document.querySelector('.auth-primary-btn');
                    btn.textContent = 'Application Submitted!';
                    btn.style.background = 'var(--status-success)';
                    btn.disabled = false;

                    setTimeout(() => {
                        // Reset form instead of redirecting
                        form.reset();
                        fileNameDisplay.textContent = '';
                        btn.textContent = 'Submit Another Application';
                        btn.style.background = ''; // Reset to default
                    }, 2000);
                } else {
                    console.error('Submission failed', response);
                    alert('Error submitting application. Please ensure the backend is running.');
                    // Reset button
                    const btn = document.querySelector('.auth-primary-btn');
                    btn.textContent = 'Submit Application';
                    btn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Network error. Is the backend running?');
                // Reset button
                const btn = document.querySelector('.auth-primary-btn');
                btn.textContent = 'Submit Application';
                btn.disabled = false;
            });
    });

    // Floating label interactions (extra polish for autofill/pre-filled)
    const inputs = document.querySelectorAll('.auth-input-with-icon');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            if (input.value) {
                input.classList.add('has-value');
            } else {
                input.classList.remove('has-value');
            }
        });
    });
});
