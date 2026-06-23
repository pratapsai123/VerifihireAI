from rest_framework import serializers
from .models import InterviewViolation, SubscriptionPlan

class InterviewViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewViolation
        fields = '__all__'

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
