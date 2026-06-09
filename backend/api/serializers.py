from rest_framework import serializers
from .models import InterviewViolation

class InterviewViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewViolation
        fields = '__all__'
