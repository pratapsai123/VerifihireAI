from rest_framework import serializers
from .models import Candidate, InterviewIntegrityLog

class InterviewIntegrityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewIntegrityLog
        fields = ['id', 'event_type', 'screenshot_base64', 'webcam_screenshot_base64', 'timestamp']

class CandidateSerializer(serializers.ModelSerializer):
    integrity_logs = InterviewIntegrityLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = Candidate
        fields = '__all__'
