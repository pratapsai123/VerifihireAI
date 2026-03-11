import uuid
from django.db import models
from django.utils import timezone

class Assessment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    job_description = models.TextField()
    required_skills = models.CharField(max_length=500)
    mcq_count = models.IntegerField(default=10)
    mcq_easy = models.IntegerField(default=5)
    mcq_medium = models.IntegerField(default=3)
    mcq_hard = models.IntegerField(default=2)
    coding_count = models.IntegerField(default=2)
    coding_difficulty_list = models.JSONField(default=list, blank=True) # e.g. ['Easy', 'Medium']
    duration_minutes = models.IntegerField(default=60)
    difficulty_level = models.CharField(max_length=20, default='Medium', choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])
    generated_content = models.JSONField(blank=True, null=True)  # Store the AI response here
    created_at = models.DateTimeField(auto_now_add=True)
    pass_threshold = models.IntegerField(default=60)
    total_points = models.IntegerField(default=0)  # Dynamic based on difficulty weights

    # New Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    available_from = models.DateTimeField(blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    invited_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Assessment for {self.required_skills} - {self.total_points} pts"

    class Meta:
        db_table = 'ai_assessment'

class AIAssessmentSubmission(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    candidate_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    answers = models.JSONField(default=dict)
    score = models.IntegerField(default=0)
    mcq_score = models.IntegerField(default=0)
    coding_score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, default='rejected')  # 'selected' or 'rejected'
    
    # Monitoring Data
    integrity_score = models.FloatField(default=100.0)
    tab_switches = models.IntegerField(default=0)
    face_warnings = models.IntegerField(default=0)
    phone_warnings = models.IntegerField(default=0)
    warning_logs = models.JSONField(default=list, blank=True, help_text="Stores the first 3 violations as grace warnings")
    monitoring_logs = models.JSONField(default=list, blank=True)
    results_breakdown = models.JSONField(default=dict, blank=True) # Detailed scoring info
    candidate_questions = models.JSONField(default=dict, blank=True) # Locked-in randomized subset

    started_at = models.DateTimeField(default=timezone.now)
    submitted_at = models.DateTimeField(blank=True, null=True)
    current_question_index = models.IntegerField(default=0)

    def __str__(self):
        return f"AI Submission - {self.candidate_name} ({self.candidate_email})"

    class Meta:
        db_table = 'ai_assessment_submission'
