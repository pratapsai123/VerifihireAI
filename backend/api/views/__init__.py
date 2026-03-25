# This package replaces the monolithic views.py by grouping views by feature domain.
# Importing from this __init__.py exposes all views to urls.py without breaking existing imports.

from .auth_views import (
    api_root,
    send_otp_view,
    verify_otp_view,
    reset_password_view,
    register_view,
    login_view,
    verify_login_otp_view,
)

from .user_views import (
    invite_user_view,
    cancel_invite_view,
    resend_invite_view,
    get_invite_view,
    accept_invite_view,
    team_members_view,
    profile_view,
    add_team_member_view,
)

from .resume_matcher_views import (
    extract_skills_from_resume_view,
)

from .assessment_views import (
    get_questions_view,
    create_question_view,
    get_manual_questions_view,
    parse_questions_document_view,
    bulk_create_questions_view,
    get_questions_by_skills_view,
    create_custom_assessment_view,
    get_custom_assessment_view,
    create_assessment_view,
    get_assessment_public_view,
    get_assessment_detail_view,
)

from .candidate_assessment_views import (
    create_invitations_and_send_email_view,
    get_invitation_public_view,
    submit_invitation_answers_view,
    invitation_coding_run_view,
    invitation_coding_submit_view,
    invitation_coding_finalize_view,
    get_invitation_result_view,
    results_overview_view,
    CandidateSubmissionDeleteView,
    submit_rating_view,
    backfill_assessment_questions_view,
    submit_objective_section,
    save_all_candidate_details_view,
    _acq_merge_code,
    update_standard_integrity_view,
    verify_pan_backend_view,
)

from .live_interview_views import (
    create_interview_invitations_and_send_email_view,
    interview_invitations_overview_view,
    get_interview_invitation_by_token_view,
    submit_interview_feedback,
    draft_interview_invitations_view,
    download_candidate_report_view,
    get_candidate_details_view,
    generate_all_interviewer_slots_view,
    get_available_slots_view,
    reserve_interview_slot_view,
    confirm_interview_booking_view,
    get_interviewer_availability_view,
    manage_interviewer_availability_view,
)
from .job_role_views import (
    job_role_list_create_view,
    job_role_delete_view,
    ensure_role_exists,
)

from .superadmin_views import (
    superadmin_companies_view,
    superadmin_approve_company_view,
    superadmin_reject_company_view,
    superadmin_users_view,
    superadmin_approve_user_view,
)

from .workflow_views import (
    company_deletion_settings_view,
    list_deletion_requests_view,
    action_deletion_request_view,
    pending_deletion_requests_count_view,
    restore_deletion_request_view,
)
