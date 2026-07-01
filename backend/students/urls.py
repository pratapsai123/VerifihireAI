from django.urls import path
from .interview_views import StudentPracticeInterviewView, StudentInterviewHistoryView
from .assessment_views import StudentPracticeAssessmentView, StudentPracticeResultsView

urlpatterns = [
    path('practice/', StudentPracticeInterviewView.as_view(), name='student-practice-interview'),
    path('my-interviews/', StudentInterviewHistoryView.as_view(), name='student-interview-history'),
    path('assessments/results/', StudentPracticeResultsView.as_view(), name='student-practice-results'),
    path('assessments/', StudentPracticeAssessmentView.as_view(), name='student-practice-assessment'),
]
