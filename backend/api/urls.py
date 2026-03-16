from django.urls import path # Reload trigger
from . import views
from . import coding_views
from .views.user_views import add_team_member_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('verify-login-otp/', views.verify_login_otp_view, name='verify_login_otp'),
    path('register/', views.register_view, name='register'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('extract-skills/', views.extract_skills_from_resume_view, name='extract_skills'),
    path('questions/', views.get_questions_view, name='get_questions'),
    path('questions/create/', views.create_question_view, name='create_question'),
    path('questions/bulk-create/', views.bulk_create_questions_view, name='bulk_create_questions'),
    path('questions/by-skills/', views.get_questions_by_skills_view, name='get_questions_by_skills'),
    path('questions/manual/', views.get_manual_questions_view, name='get_manual_questions'),
    path('questions/parse-document/', views.parse_questions_document_view, name='parse_questions_document'),
    path('custom-assessments/', views.create_custom_assessment_view, name='create_custom_assessment'),
    path('custom-assessments/<int:custom_assessment_id>/', views.get_custom_assessment_view, name='get_custom_assessment'),
    path('assessments/', views.create_assessment_view, name='create_assessment'),
    path('assessments/<int:assessment_id>/', views.get_assessment_detail_view, name='get_assessment_detail'),
    path('assessments/<int:assessment_id>/invite/', views.create_invitations_and_send_email_view, name='invite_candidates'),
    path('assessments/public/<uuid:token>/', views.get_assessment_public_view, name='get_assessment_public'),
    path('interviews/invite/', views.create_interview_invitations_and_send_email_view, name='invite_interview_candidates'),
    path('interviews/invitations/', views.interview_invitations_overview_view, name='interview_invitations_overview'),
    path('interviews/invitations/<uuid:token>/', views.get_interview_invitation_by_token_view, name='get_interview_invitation_by_token'),
    path('interviews/draft-invites/', views.draft_interview_invitations_view, name='draft_interview_invitations_list'),
    path('interviews/draft-invites/<int:draft_id>/', views.draft_interview_invitations_view, name='draft_interview_invitations_detail'),
    
    # Slot Booking
    path('interviews/slots/generate/', views.generate_all_interviewer_slots_view, name='generate_slots'),
    path('interviews/slots/<uuid:token>/', views.get_available_slots_view, name='get_available_slots'),
    path('interviews/slots/<uuid:token>/reserve/', views.reserve_interview_slot_view, name='reserve_slot'),
    path('interviews/slots/<uuid:token>/confirm/', views.confirm_interview_booking_view, name='confirm_booking'),
    path('interviews/availability/', views.get_interviewer_availability_view, name='interviewer_availability_list'),
    path('interviews/availability/manage/', views.manage_interviewer_availability_view, name='interviewer_availability_manage'),

    # Internal user invitations (HR Manager / HR)
    path('users/invite/', views.invite_user_view, name='invite_user'),
    path('users/invite/<uuid:token>/', views.get_invite_view, name='get_invite'),
    path('users/invite/<uuid:token>/cancel/', views.cancel_invite_view, name='cancel_invite'),
    path('users/invite/<uuid:token>/resend/', views.resend_invite_view, name='resend_invite'),
    path('users/accept-invite/', views.accept_invite_view, name='accept_invite'),
    path('users/team-members/', views.team_members_view, name='team_members'),
    path('users/team-members/add/', add_team_member_view, name='add_team_member'),
    path('profile/', views.profile_view, name='profile'),

    path('invitations/public/<uuid:token>/', views.get_invitation_public_view, name='get_invitation_public'),
    path('invitations/public/<uuid:token>/submit/', views.submit_invitation_answers_view, name='submit_invitation_answers'),
    path('invitations/public/<uuid:token>/submit-objective/', views.submit_objective_section, name='submit_objective_section'),
    path('invitations/public/<uuid:token>/result/', views.get_invitation_result_view, name='get_invitation_result'),
    path('invitations/public/<uuid:token>/rating/', views.submit_rating_view, name='submit_rating'),
    path('invitations/public/<uuid:token>/integrity/', views.update_standard_integrity_view, name='update_standard_integrity'),
    path('candidate-details/', views.save_candidate_details_view, name='save_candidate_details'),
    path('candidate-details/verify-pan/', views.verify_pan_backend_view, name='verify_pan_backend'),
    path('candidate-details/<str:token>/', views.get_candidate_details_view, name='get_candidate_details'),
    path('invitations/public/<uuid:token>/coding/run/', views.invitation_coding_run_view, name='invitation_coding_run'),
    path('invitations/public/<uuid:token>/coding/submit/', views.invitation_coding_submit_view, name='invitation_coding_submit'),
    path('invitations/public/<uuid:token>/coding/finalize/', views.invitation_coding_finalize_view, name='invitation_coding_finalize'),
    path('results/', views.results_overview_view, name='results_overview'),
    path('submissions/<int:pk>/', views.CandidateSubmissionDeleteView.as_view(), name='delete_submission'),
    path('results/<int:submission_id>/report/', views.download_candidate_report_view, name='download_candidate_report'),
    path('candidates/', views.candidates_overview_view, name='candidates_overview'),
    path('assessments/backfill-questions/', views.backfill_assessment_questions_view, name='backfill_assessment_questions'),

    # Coding Platform (isolated)
    path('coding/questions/', coding_views.coding_questions_view, name='coding_questions'),
    path('coding/questions/<int:question_id>/', coding_views.coding_question_detail_view, name='coding_question_detail'),
    path('coding/questions/<int:question_id>/testcases/', coding_views.coding_testcases_view, name='coding_testcases'),
    path('coding/testcases/<int:testcase_id>/', coding_views.coding_testcase_delete_view, name='coding_testcase_delete'),
    path('coding/questions/<int:question_id>/run/', coding_views.coding_run_view, name='coding_run'),
    path('coding/questions/<int:question_id>/submit/', coding_views.coding_submit_view, name='coding_submit'),
    path('coding/questions/<int:question_id>/submissions/', coding_views.coding_submissions_view, name='coding_submissions'),
    path('coding/invites/', coding_views.coding_invites_view, name='coding_invites_create'),
    path('coding/invites/<uuid:token>/', coding_views.coding_invite_detail_view, name='coding_invite_detail'),
    path('coding/invites/<uuid:token>/select-language/', coding_views.coding_invite_select_language_view, name='coding_invite_select_language'),
    path('coding/invites/<uuid:token>/run/', coding_views.coding_invite_run_view, name='coding_invite_run'),
    path('coding/invites/<uuid:token>/submit/', coding_views.coding_invite_submit_view, name='coding_invite_submit'),
    path('submit-interview-feedback/', views.submit_interview_feedback, name='submit_interview_feedback'),
    path('job-roles/', views.job_role_list_create_view, name='job_role_list_create'),
    path('job-roles/<int:pk>/', views.job_role_delete_view, name='job_role_delete'),

    # Superadmin (Platform ApplicationAdmin) endpoints
    path('superadmin/companies/', views.superadmin_companies_view, name='superadmin_companies'),
    path('superadmin/companies/<int:company_id>/approve/', views.superadmin_approve_company_view, name='superadmin_approve_company'),
    path('superadmin/companies/<int:company_id>/reject/', views.superadmin_reject_company_view, name='superadmin_reject_company'),
    path('superadmin/users/', views.superadmin_users_view, name='superadmin_users'),
    path('superadmin/users/<int:user_id>/approve/', views.superadmin_approve_user_view, name='superadmin_approve_user'),

    # Workflow / Settings
    path('settings/deletion/', views.company_deletion_settings_view, name='company_deletion_settings'),
    path('workflow/deletion-requests/', views.list_deletion_requests_view, name='list_deletion_requests'),
    path('workflow/deletion-requests/count/', views.pending_deletion_requests_count_view, name='pending_deletion_requests_count'),
    path('workflow/deletion-requests/<int:request_id>/action/', views.action_deletion_request_view, name='action_deletion_request'),
    path('workflow/deletion-requests/<int:request_id>/restore/', views.restore_deletion_request_view, name='restore_deletion_request'),
]

