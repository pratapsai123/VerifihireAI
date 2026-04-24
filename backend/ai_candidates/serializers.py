from rest_framework import serializers
from django.utils import timezone
from .models import Candidate, InterviewIntegrityLog, PipelineLog

class PipelineLogSerializer(serializers.ModelSerializer):
    timestamp_formatted = serializers.SerializerMethodField()

    class Meta:
        model = PipelineLog
        fields = ['id', 'event_type', 'status', 'phase', 'batch_id', 'message', 'details', 'timestamp', 'timestamp_formatted']

    def get_timestamp_formatted(self, obj):
        # Convert UTC to local time (configured in settings.TIME_ZONE)
        local_time = timezone.localtime(obj.timestamp)
        return local_time.strftime('%B %d, %Y at %I:%M %p')

class InterviewIntegrityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewIntegrityLog
        fields = ['id', 'event_type', 'screenshot_base64', 'webcam_screenshot_base64', 'timestamp']

class CandidateSerializer(serializers.ModelSerializer):
    integrity_logs = InterviewIntegrityLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Candidate
        fields = '__all__'
