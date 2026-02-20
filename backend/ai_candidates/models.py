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
    job_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    submission_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when interview was completed")

    def __str__(self):
        return f"{self.full_name} - {self.job_title}"

class InterviewIntegrity(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='integrity')
    tab_switches = models.IntegerField(default=0)
    phone_detections = models.IntegerField(default=0)
    multiface_detections = models.IntegerField(default=0)
    no_face_detections = models.IntegerField(default=0)
    integrity_score = models.FloatField(default=100.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Integrity: {self.candidate.full_name} ({self.integrity_score}%)"
