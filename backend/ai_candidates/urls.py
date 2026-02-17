from django.urls import path
from .views import CandidateListCreateView, CandidateDetailView, ResumeMatchView, CandidateStatusUpdateView, BulkInviteView, ProcessAnswerView

urlpatterns = [
    path('', CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('<int:pk>/status/', CandidateStatusUpdateView.as_view(), name='candidate-status-update'),
    path('match/', ResumeMatchView.as_view(), name='resume-match'),
    path('bulk-invite/', BulkInviteView.as_view(), name='bulk-invite'),
    path('process-answer/', ProcessAnswerView.as_view(), name='process-answer'),
]
