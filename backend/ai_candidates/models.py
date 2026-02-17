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
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    submission_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job_title}"
