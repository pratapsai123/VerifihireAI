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

        // Handle file name for storage (since we can't store actual files easily in localStorage)
        data.resumeName = fileInput.files[0] ? fileInput.files[0].name : 'No file uploaded';
        data.submissionDate = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        data.status = 'New';
        data.id = Date.now().toString(); // Simple ID

        // Save to localStorage
        const candidates = JSON.parse(localStorage.getItem('verifihire_candidates') || '[]');
        candidates.unshift(data); // Add new candidate to the top
        localStorage.setItem('verifihire_candidates', JSON.stringify(candidates));

        // UI Feedback
        const btn = document.querySelector('.auth-primary-btn');
        const originalText = btn.textContent;

        btn.textContent = 'Submitting...';
        btn.disabled = true;

        setTimeout(() => {
            btn.textContent = 'Application Submitted!';
            btn.style.background = 'var(--status-success)';

            setTimeout(() => {
                // Redirect to candidates page
                window.location.href = 'candidates.html';
            }, 1000);
        }, 1500);
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
