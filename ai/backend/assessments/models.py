from django.db import models

class Assessment(models.Model):
    job_description = models.TextField()
    required_skills = models.CharField(max_length=500)
    mcq_count = models.IntegerField(default=10)
    coding_count = models.IntegerField(default=2)
    duration_minutes = models.IntegerField(default=60)
    generated_content = models.JSONField(blank=True, null=True)  # Store the AI response here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment for {self.required_skills} - {self.created_at.strftime('%Y-%m-%d')}"
