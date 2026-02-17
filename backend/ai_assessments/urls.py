from django.urls import path
from .views import GenerateAssessmentView, AssessmentListView, AssessmentDetailView, PublicAssessmentView, SubmitAssessmentView

urlpatterns = [
    path('generate/', GenerateAssessmentView.as_view(), name='generate-assessment'),
    path('', AssessmentListView.as_view(), name='list-assessments'),
    path('<int:pk>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('public/<str:token>/', PublicAssessmentView.as_view(), name='public-assessment'),
    path('submit/', SubmitAssessmentView.as_view(), name='submit-assessment'),
]
