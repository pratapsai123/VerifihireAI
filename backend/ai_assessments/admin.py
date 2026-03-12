from django.contrib import admin

# Register your models here.
from .models import AIAssessmentIntegrityScreenshot

@admin.register(AIAssessmentIntegrityScreenshot)
class AIAssessmentIntegrityScreenshotAdmin(admin.ModelAdmin):
    list_display = ['submission', 'event_type', 'timestamp', 'screenshot']
