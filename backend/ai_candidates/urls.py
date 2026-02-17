from django.urls import path
from .views import CandidateListCreateView, CandidateDetailView, ResumeMatchView, CandidateStatusUpdateView

urlpatterns = [
    path('', CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('<int:pk>/status/', CandidateStatusUpdateView.as_view(), name='candidate-status-update'),
    path('match/', ResumeMatchView.as_view(), name='resume-match'),
]
