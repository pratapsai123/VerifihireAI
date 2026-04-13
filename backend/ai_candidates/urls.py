from django.urls import path
from .views import CandidateListCreateView, CandidateDetailView, CandidateTimelineView, ResumeMatchView, CandidateStatusUpdateView, BulkInviteView, ProcessAnswerView, UpdateIntegrityView, AssemblyAITokenView, RetryFailedExtractionsView, BatchProgressView, TTSView, LatestActiveBatchView

urlpatterns = [
    path('', CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('<int:pk>/status/', CandidateStatusUpdateView.as_view(), name='candidate-status-update'),
    path('<int:pk>/timeline/', CandidateTimelineView.as_view(), name='candidate-timeline'),
    path('<int:pk>/integrity/', UpdateIntegrityView.as_view(), name='candidate-integrity-update'),
    path('match/', ResumeMatchView.as_view(), name='resume-match'),
    path('latest-active-batch/', LatestActiveBatchView.as_view(), name='latest-active-batch'),
    path('batch-progress/<str:batch_id>/', BatchProgressView.as_view(), name='batch-progress'),
    path('retry-extraction/', RetryFailedExtractionsView.as_view(), name='retry-failed-extractions'),
    path('bulk-invite/', BulkInviteView.as_view(), name='bulk-invite'),
    path('process-answer/', ProcessAnswerView.as_view(), name='process-answer'),
    path('assemblyai-token/', AssemblyAITokenView.as_view(), name='assemblyai-token'),
    path('tts/', TTSView.as_view(), name='tts'),
]

