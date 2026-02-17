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

        // Construct API payload matching Django model fields
        const apiData = {
            full_name: data.fullName,
            email: data.email,
            phone: data.phone,
            job_title: data.jobTitle,
            linkedin_url: data.linkedin || '',
            resume_name: fileInput.files[0] ? fileInput.files[0].name : 'No file uploaded',
            cover_letter: data.coverLetter || ''
        };

        // Create Candidate via API
        fetch('http://localhost:8001/api/candidates/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiData)
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
