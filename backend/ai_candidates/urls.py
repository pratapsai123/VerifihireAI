from django.urls import path
from django.urls import path
from .views import CandidateListCreateView, CandidateDetailView, CandidateTimelineView, ResumeMatchView, CandidateStatusUpdateView, BulkInviteView, ProcessAnswerView, UpdateIntegrityView, AssemblyAITokenView, RetryFailedExtractionsView, BatchProgressView, TTSView, LatestActiveBatchView, CandidatePublicDetailView, CandidatePublicStatusUpdateView, CandidatePublicIntegrityUpdateView, CandidateReportDownloadView, CandidateRegistrationUpdateView
from .pan_validation_enhanced import EnhancedPanValidationView

urlpatterns = [
    path('', CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('<int:pk>/status/', CandidateStatusUpdateView.as_view(), name='candidate-status-update'),
    path('<int:pk>/timeline/', CandidateTimelineView.as_view(), name='candidate-timeline'),
    path('<int:pk>/integrity/', UpdateIntegrityView.as_view(), name='candidate-integrity-update'),
    path('public/<str:public_token>/', CandidatePublicDetailView.as_view(), name='candidate-public-detail'),
    path('public/<str:public_token>/status/', CandidatePublicStatusUpdateView.as_view(), name='candidate-public-status-update'),
    path('public/<str:public_token>/integrity/', CandidatePublicIntegrityUpdateView.as_view(), name='candidate-public-integrity-update'),
    path('match/', ResumeMatchView.as_view(), name='resume-match'),
    path('latest-active-batch/', LatestActiveBatchView.as_view(), name='latest-active-batch'),
    path('batch-progress/<str:batch_id>/', BatchProgressView.as_view(), name='batch-progress'),
    path('retry-extraction/', RetryFailedExtractionsView.as_view(), name='retry-failed-extractions'),
    path('bulk-invite/', BulkInviteView.as_view(), name='bulk-invite'),
    path('process-answer/', ProcessAnswerView.as_view(), name='process-answer'),
    path('assemblyai-token/', AssemblyAITokenView.as_view(), name='assemblyai-token'),
    path('tts/', TTSView.as_view(), name='tts'),
    path('<int:pk>/download-report/', CandidateReportDownloadView.as_view(), name='candidate-report-download'),
    path('validate-pan/', EnhancedPanValidationView.as_view(), name='validate-pan'),
    path('public/<str:public_token>/register/', CandidateRegistrationUpdateView.as_view(), name='candidate-registration-update'),
]

