import uuid
from django.db import models

class Candidate(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Invited', 'Invited'),
        ('Review', 'In Review'),
        ('Interview', 'Interview'),
        ('Rejected', 'Rejected'),
        ('Hired', 'Hired'),
        ('Resume Passed', 'Resume Passed'),
        ('Resume Failed', 'Resume Failed'),
        ('Completed', 'Completed'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_text = models.TextField(blank=True, null=True, help_text="Cached text content of the resume to avoid re-parsing")
    cover_letter = models.TextField(blank=True, null=True)
    interview_time = models.CharField(max_length=100, blank=True, null=True, help_text="Scheduled time for the interview (e.g., 10 am - 11 am)")
    available_from = models.DateTimeField(blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('fresher', 'Fresher'),
            ('1-2', '1-2 Years'),
            ('3-5', '3-5 Years'),
            ('5+', '5+ Years'),
        ],
        blank=True, null=True,
        help_text="Experience level for difficulty-adjusted interview questions"
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    company = models.ForeignKey(
        'api.Company', 
        on_delete=models.CASCADE, 
        related_name='ai_candidates', 
        null=True, 
        blank=True
    )
    score = models.IntegerField(default=0)
    resume_score = models.IntegerField(default=0, help_text="Resume match percentage from AI screening")
    interview_pass_threshold = models.IntegerField(default=50, help_text="Minimum score percentage to pass the interview")
    total_questions = models.IntegerField(default=0)
    submission_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Ownership Tracking for RBAC (current owner)
    user_profile = models.ForeignKey(
        'api.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ai_candidates',
        help_text="The user who currently owns this candidate record",
    )
    # Immutable audit field: original creator
    created_by = models.ForeignKey(
        'api.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='originally_created_ai_candidates',
        help_text="Original creator — immutable audit field, not changed on ownership transfer",
    )

    is_deleted = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when interview was completed")
    link_opened_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when interview link was first opened")
    interview_summary = models.JSONField(default=list, blank=True, help_text="Stores per-question AI feedback and scores")
    interview_questions = models.JSONField(default=list, blank=True, help_text="The set of questions generated for this candidate")
    automation_settings = models.JSONField(default=dict, blank=True, help_text="Stores difficulty, duration, and question counts for the automated pipeline")
    batch_id = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="Internal UUID for the bulk session")
    batch_name = models.CharField(max_length=255, blank=True, null=True, db_index=True, help_text="Descriptive name (JD_date_time)")
    public_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)

    def __str__(self):
        return f"{self.full_name} - {self.job_title}"

class InterviewIntegrity(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='integrity')
    tab_switches = models.IntegerField(default=0)
    phone_detections = models.IntegerField(default=0)
    multiface_detections = models.IntegerField(default=0)
    no_face_detections = models.IntegerField(default=0)
    integrity_score = models.FloatField(default=100.0)
    warning_logs = models.JSONField(default=list, blank=True, help_text="Stores the first 3 violations as grace warnings")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Integrity: {self.candidate.full_name} ({self.integrity_score}%)"

class InterviewIntegrityLog(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='integrity_logs')
    event_type = models.CharField(max_length=100)
    screenshot_base64 = models.TextField(blank=True, null=True, help_text="Desktop/Full screen snapshot")
    webcam_screenshot_base64 = models.TextField(blank=True, null=True, help_text="Candidate webcam snapshot")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Violation: {self.event_type} - {self.candidate.full_name}"

class PipelineLog(models.Model):
    EVENT_CHOICES = [
        ('TASK_SCHEDULED', 'Task Scheduled'),
        ('AI_GENERATION', 'AI Generation'),
        ('EMAIL_SENT', 'Email Sent'),
        ('STATUS_CHANGE', 'Status Change'),
        ('ERROR', 'Error'),
    ]
    STATUS_CHOICES = [
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('FAILURE', 'Failure'),
    ]
    PHASE_CHOICES = [
        ('RESUME', 'Resume Screening'),
        ('ASSESSMENT', 'AI Assessment'),
        ('INTERVIEW', 'AI Interview'),
        ('GENERAL', 'General'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='pipeline_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INFO')
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='GENERAL')
    batch_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.candidate.full_name} - {self.event_type} ({self.status})"
