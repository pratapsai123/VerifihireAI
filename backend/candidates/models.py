from django.db import models

class Candidate(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Review', 'In Review'),
        ('Interview', 'Interview'),
        ('Rejected', 'Rejected'),
        ('Hired', 'Hired'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    job_title = models.CharField(max_length=255)
    linkedin_url = models.URLField(blank=True, null=True)
    resume_name = models.CharField(max_length=255)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='New')
    submission_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.job_title}"
