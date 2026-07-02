from django.urls import path
from .interview_views import (
    StudentPracticeInterviewView,
    StudentInterviewHistoryView,
    StudentInterviewFeedbackView,
    StudentProgressView,
)

urlpatterns = [
    path('practice/', StudentPracticeInterviewView.as_view(), name='student-practice-interview'),
    path('my-interviews/', StudentInterviewHistoryView.as_view(), name='student-interview-history'),
    path('assessments/results/', StudentPracticeResultsView.as_view(), name='student-practice-results'),
    path('assessments/', StudentPracticeAssessmentView.as_view(), name='student-practice-assessment'),
    path('feedback/<str:public_token>/', StudentInterviewFeedbackView.as_view(), name='student-interview-feedback'),
    path('progress/', StudentProgressView.as_view(), name='student-progress'),
]
