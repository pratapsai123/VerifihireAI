from django.urls import path
from .interview_views import StudentPracticeInterviewView, StudentInterviewHistoryView

urlpatterns = [
    path('practice/', StudentPracticeInterviewView.as_view(), name='student-practice-interview'),
    path('my-interviews/', StudentInterviewHistoryView.as_view(), name='student-interview-history'),
]
