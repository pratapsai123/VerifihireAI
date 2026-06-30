from django.urls import path
from .views import StudentPracticeInterviewView

urlpatterns = [
    path('practice/', StudentPracticeInterviewView.as_view(), name='student-practice-interview'),
]
