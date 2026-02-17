from django.urls import path
from .views import GenerateAssessmentView, AssessmentListView

urlpatterns = [
    path('generate/', GenerateAssessmentView.as_view(), name='generate-assessment'),
    path('', AssessmentListView.as_view(), name='list-assessments'),
]
