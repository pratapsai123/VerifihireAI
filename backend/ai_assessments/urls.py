from django.urls import path
from .views import (
    GenerateAssessmentView, AssessmentListView, AssessmentDetailView, 
    PublicAssessmentView, SubmitAssessmentView, CreateSubmissionView, 
    UpdateAssessmentIntegrityView, InviteAssessmentCandidatesView, GetInvitedCandidatesView,
    ProxyCodeExecuteView, AIAssessmentSubmissionDetailView, AIAssessmentSubmissionListView,
    SaveAssessmentProgressView, AIAssessmentAssignmentView, AIAssessmentAvailableInterviewersView,
    CancelGenerationView, GenerationStatusView, AIAssessmentReportDownloadView, AIAssessmentResultsView,
    ServeDeepFaceFaceView, OverrideSubmissionStatusView, ApproveAssessmentIdentityPhotoView,
    ResendAssessmentInviteView, AIAssessmentTimelineView
)

urlpatterns = [
    path('registration/face/<path:person_id>/', ServeDeepFaceFaceView.as_view(), name='serve-deepface-face'),
    path('generate/', GenerateAssessmentView.as_view(), name='generate-assessment'),
    path('generation-status/<str:task_id>/', GenerationStatusView.as_view(), name='generation-status'),
    path('cancel-generation/', CancelGenerationView.as_view(), name='cancel-generation'),
    path('', AssessmentListView.as_view(), name='list-assessments'),
    path('<int:pk>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:pk>/assign-interviewers/', AIAssessmentAssignmentView.as_view(), name='assign-interviewers'),
    path('<int:pk>/available-interviewers/', AIAssessmentAvailableInterviewersView.as_view(), name='available-interviewers'),
    path('<int:assessment_id>/invited-candidates/', GetInvitedCandidatesView.as_view(), name='get-invited-candidates'),
    path('public/<str:token>/', PublicAssessmentView.as_view(), name='public-assessment'),
    path('invite/', InviteAssessmentCandidatesView.as_view(), name='invite-candidates'),
    path('invite/resend/', ResendAssessmentInviteView.as_view(), name='resend-invite'),
    path('submit/', SubmitAssessmentView.as_view(), name='submit-assessment'),
    path('submit/create/', CreateSubmissionView.as_view(), name='create-submission'),
    path('submission/<int:pk>/integrity/', UpdateAssessmentIntegrityView.as_view(), name='update-integrity'),
    path('submission/<int:pk>/progress/', SaveAssessmentProgressView.as_view(), name='save-progress'),
    path('submission/<int:pk>/override-status/', OverrideSubmissionStatusView.as_view(), name='override-submission-status'),
    path('submission/<int:pk>/approve-photo/', ApproveAssessmentIdentityPhotoView.as_view(), name='submission-approve-photo'),
    path('submission/<int:pk>/download-report/', AIAssessmentReportDownloadView.as_view(), name='ai-submission-report-download'),
    path('submission/<int:pk>/', AIAssessmentSubmissionDetailView.as_view(), name='submission-detail'),
    path('submission/<int:pk>/timeline/', AIAssessmentTimelineView.as_view(), name='submission-timeline'),
    path('submissions/', AIAssessmentSubmissionListView.as_view(), name='submissions-list'),
    path('results/', AIAssessmentResultsView.as_view(), name='ai-results'),
    path('execute/', ProxyCodeExecuteView.as_view(), name='proxy-execute'),
]

