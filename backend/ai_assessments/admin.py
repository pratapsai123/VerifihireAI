from django.contrib import admin

# Register your models here.
from .models import Assessment, AIAssessmentIntegrityScreenshot

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'required_skills', 'creation_type', 'status', 'batch_name', 'created_at', 'num_applicants']
    list_filter = ['creation_type', 'status', 'created_at']
    search_fields = ['required_skills', 'job_description', 'batch_name']
    readonly_fields = ['share_token', 'batch_id', 'created_at']

@admin.register(AIAssessmentIntegrityScreenshot)
class AIAssessmentIntegrityScreenshotAdmin(admin.ModelAdmin):
    list_display = ['submission', 'event_type', 'timestamp', 'screenshot']
