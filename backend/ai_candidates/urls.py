from django.urls import path
from .views import CandidateListCreateView, CandidateDetailView, CandidateTimelineView, StandaloneTimelineView, ResumeMatchView, CandidateStatusUpdateView, BulkInviteView, ProcessAnswerView, UpdateIntegrityView, AssemblyAITokenView, RetryFailedExtractionsView, BatchProgressView, TTSView, LatestActiveBatchView, CandidatePublicDetailView, CandidatePublicStatusUpdateView, CandidatePublicIntegrityUpdateView, CandidateReportDownloadView, PanValidationView, CandidateRegistrationUpdateView, HealthCheckView, LogCandidateActivityView, ApprovePendingIdentityPhotoView, InterviewsOverviewView, ResendInviteView, IntegrityScreenshotView, StandaloneResumeScreeningListCreateView, StandaloneResumeScreeningDetailView
from .pan_validation_enhanced import EnhancedPanValidationView
from .async_views import AsyncProcessAnswerView, TaskStatusView, InterviewQueueStatusView

urlpatterns = [
    path('', CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<int:pk>/', CandidateDetailView.as_view(), name='candidate-detail'),
    path('<int:pk>/status/', CandidateStatusUpdateView.as_view(), name='candidate-status-update'),
    path('<int:pk>/timeline/', CandidateTimelineView.as_view(), name='candidate-timeline'),
    path('standalone-resume/<int:pk>/timeline/', StandaloneTimelineView.as_view(), name='standalone-resume-timeline'),
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
    path('process-answer-async/', AsyncProcessAnswerView.as_view(), name='process-answer-async'),
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
    path('queue-status/', InterviewQueueStatusView.as_view(), name='queue-status'),
    path('assemblyai-token/', AssemblyAITokenView.as_view(), name='assemblyai-token'),
    path('tts/', TTSView.as_view(), name='tts'),
    path('<int:pk>/download-report/', CandidateReportDownloadView.as_view(), name='candidate-report-download'),
    path('validate-pan/', EnhancedPanValidationView.as_view(), name='validate-pan'),
    path('public/<str:public_token>/register/', CandidateRegistrationUpdateView.as_view(), name='candidate-registration-update'),
    path('public/<str:public_token>/log/', LogCandidateActivityView.as_view(), name='candidate-public-log'),
    path('<int:pk>/approve-photo/', ApprovePendingIdentityPhotoView.as_view(), name='candidate-approve-photo'),
    path('interviews-overview/', InterviewsOverviewView.as_view(), name='interviews-overview'),
    path('<int:pk>/resend-invite/', ResendInviteView.as_view(), name='resend-invite'),
    path('integrity-screenshot/<int:log_id>/', IntegrityScreenshotView.as_view(), name='integrity-screenshot'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('standalone-screening/', StandaloneResumeScreeningListCreateView.as_view(), name='standalone-screening-list-create'),
    path('standalone-screening/<int:pk>/', StandaloneResumeScreeningDetailView.as_view(), name='standalone-screening-detail'),
]

