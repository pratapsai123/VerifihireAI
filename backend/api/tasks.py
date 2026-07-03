from celery import shared_task
from .pipeline import process_resume_passed, process_assessment_passed, process_batch_assessment
import logging

logger = logging.getLogger(__name__)

@shared_task
def trigger_batch_assessment_task(batch_id):
    from ai_candidates.models import Candidate
    from ai_candidates.utils import log_automation_event

    logger.info(f"=== trigger_batch_assessment_task started for batch {batch_id} ===")

    # Log a summary of who passed before entering the pipeline
    passed_qs = Candidate.objects.filter(batch_id=batch_id, status='Resume Passed')
    total_batch = Candidate.objects.filter(batch_id=batch_id).count()
    num_passed = passed_qs.count()

    logger.info(
        f"Batch {batch_id}: {total_batch} total candidates, "
        f"{num_passed} passed resume screening, "
        f"{total_batch - num_passed} did not pass."
    )

    if num_passed == 0:
        logger.info(f"Batch {batch_id}: No candidates passed. Assessment pool will NOT be generated.")
        return

    logger.info(f"Batch {batch_id}: Proceeding to generate shared assessment pool for {num_passed} candidate(s).")
    for c in passed_qs:
        log_automation_event(
            c, 'TASK_SCHEDULED', 'INFO',
            f"Batch assessment task triggered. {num_passed} candidate(s) passed in this batch. Generating shared pool.",
            details={'batch_id': batch_id, 'num_passed': num_passed, 'total_in_batch': total_batch},
            phase='ASSESSMENT'
        )

    process_batch_assessment(batch_id)
    logger.info(f"=== trigger_batch_assessment_task completed for batch {batch_id} ===")

@shared_task
def send_assessment_link_task(candidate_id):
    logger.info(f"Executing send_assessment_link_task for candidate {candidate_id}")
    process_resume_passed(candidate_id)

@shared_task
def send_interview_link_task(submission_id):
    logger.info(f"Executing send_interview_link_task for submission {submission_id}")
    try:
        from ai_assessments.models import AIAssessmentSubmission
        submission = AIAssessmentSubmission.objects.get(id=submission_id)
        
        if submission.status == 'selected':
            logger.info(f"Celery: Candidate {submission.candidate_email} PASSED assessment with {submission.percentage}%. Sending interview invitation...")
            process_assessment_passed(submission_id)
            logger.info(f"Celery: ✅ Interview invitation email sent to {submission.candidate_email}")
        else:
            logger.info(f"Celery: Candidate {submission.candidate_email} status is '{submission.status}' (score: {submission.percentage}%). NOT sending interview invitation.")
        
        logger.info(f"Successfully completed send_interview_link_task for submission {submission_id}")
    except AIAssessmentSubmission.DoesNotExist:
        logger.error(f"Celery: Submission {submission_id} not found!")
    except Exception as e:
        logger.error(f"Error in send_interview_link_task for submission {submission_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())

@shared_task
def send_custom_assessment_result_task(invitation_id):
    """
    Task triggered after assessment completion to send results after 1 hour.
    Checks if candidate is qualified and sends the slot booking link.
    """
    from .models import CandidateInvitation
    from django.core.mail import send_mail
    from django.conf import settings
    
    logger.info(f"Executing send_custom_assessment_result_task for invitation {invitation_id}")
    try:
        inv = CandidateInvitation.objects.get(id=invitation_id)
        submission = getattr(inv, 'submission', None)
        
        if not submission:
            logger.warning(f"No submission found for invitation {invitation_id}")
            return

        if not inv.is_auto_schedule:
            logger.info(f"Auto Slot Schedule is OFF for invitation {invitation_id}. Skipping email and slot booking.")
            return

        if submission.is_qualified:
            # Update status to qualified
            inv.status = 'qualified'
            inv.save(update_fields=['status'])
            
            # Send 'Cleared' Email with slot booking link
            frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
            booking_link = f"{frontend_base}/book-interview/{inv.token}"
            
            subject = f"Congratulations! You've cleared the assessment for {inv.assessment.name}"
            message = (
                f"Dear {inv.name},\n\n"
                f"We are pleased to inform you that you have cleared the assessment for the {inv.assessment.name} role.\n\n"
                f"Your Score: {submission.percentage}%\n\n"
                f"Please proceed to book your live interview slot using the link below:\n"
                f"{booking_link}\n\n"
                f"Note: Slots are available on a first-come, first-served basis.\n\n"
                f"Best regards,\nVerifiHire Team"
            )
            
            # Simple HTML version
            html_message = f"""
            <div style="font-family: sans-serif; max-width: 600px;">
                <h2 style="color: #2e7d32;">Congratulations, {inv.name}!</h2>
                <p>You have successfully cleared the assessment for <strong>{inv.assessment.name}</strong>.</p>
                <p>The next step is a live interview. Please use the button below to book your preferred slot:</p>
                <div style="margin: 30px 0;">
                    <a href="{booking_link}" style="background-color: #4318FF; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Book Interview Slot</a>
                </div>
                <p style="font-size: 12px; color: #666;">If the button above doesn't work, copy and paste this link: {booking_link}</p>
            </div>
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inv.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # ── CRITICAL: stamp the exact moment the email was sent ──
            # This timestamp is the anchor for the dynamic booking window:
            #   - 3-day prep buffer starts from here (candidate cannot book sooner)
            #   - 7 actual available days are counted forward from the buffer end
            # Even if the candidate opens the link 5 days later, the window is
            # always calculated relative to THIS fixed timestamp.
            from django.utils import timezone as tz
            inv.slot_booking_email_sent_at = tz.now()
            inv.save(update_fields=['slot_booking_email_sent_at'])
            
            logger.info(f"Result email sent to {inv.email} for invitation {invitation_id}")
        else:
            # If not qualified, check if it's a rejection (not 'hold')
            if submission.result == 'rejected':
                # Regret email is now handled by a separate task with 24h delay
                # triggered from the view to ensure it always fires regardless of auto-schedule
                logger.info(f"Candidate {inv.email} not qualified ({submission.percentage}%). Regret task should be scheduled.")
            else:
                logger.info(f"Candidate {inv.email} status is '{submission.result}' (score: {submission.percentage}%). No automatic email.")
            
    except CandidateInvitation.DoesNotExist:
        logger.error(f"Invitation {invitation_id} not found")
    except Exception as e:
        logger.error(f"Error in send_custom_assessment_result_task: {str(e)}")

@shared_task
def send_regret_email_task(invitation_id):
    """
    Sends a formal regret email to a candidate who did not qualify.
    Triggered with a 24-hour delay.
    """
    from .models import CandidateInvitation
    from django.core.mail import send_mail
    from django.conf import settings
    
    logger.info(f"Executing send_regret_email_task for invitation {invitation_id}")
    try:
        inv = CandidateInvitation.objects.get(id=invitation_id)
        submission = getattr(inv, 'submission', None)
        
        if not submission:
            logger.warning(f"No submission found for invitation {invitation_id}")
            return

        # CRITICAL: Only send if status is STILL 'rejected'
        # If the recruiter changed it to 'hold' or 'selected' during the 24h delay, skip.
        if submission.result != 'rejected':
            logger.info(f"Skipping regret email for {inv.email}: Result is currently '{submission.result}'")
            return
            
        if submission.regret_email_sent:
            logger.info(f"Regret email already sent to {inv.email}. Skipping.")
            return

        subject = f"Update regarding your assessment for {inv.assessment.name}"
        
        # Formal message that avoids direct "rejection/failed" terminology
        message = (
            f"Dear {inv.name},\n\n"
            f"Thank you for the time and effort you invested in completing the assessment for the {inv.assessment.name} position.\n\n"
            f"We have carefully reviewed your submission along with our current requirements. While we appreciate your interest in joining our team, we have decided to move forward with other candidates at this stage.\n\n"
            f"We will keep your profile in our database for future opportunities that may be a better match for your skills. We wish you the very best in your professional journey.\n\n"
            f"Best regards,\nThe VerifiHire Team"
        )
        
        html_message = f"""
        <div style="font-family: sans-serif; max-width: 600px; color: #333; line-height: 1.6;">
            <p>Dear <strong>{inv.name}</strong>,</p>
            <p>Thank you for the time and effort you invested in completing the assessment for the <strong>{inv.assessment.name}</strong> position.</p>
            <p>We have carefully reviewed your submission along with our current requirements. While we appreciate your interest in joining our team, we have decided to move forward with other candidates at this stage.</p>
            <p>We will keep your profile in our database for future opportunities that may be a better match for your skills. We wish you the very best in your professional journey.</p>
            <br/>
            <p>Best regards,<br/><strong>The VerifiHire Team</strong></p>
        </div>
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inv.email],
            html_message=html_message,
            fail_silently=False
        )
        
        submission.regret_email_sent = True
        submission.save(update_fields=['regret_email_sent'])
        
        logger.info(f"Formal regret email sent to {inv.email} for invitation {invitation_id}")
            
    except CandidateInvitation.DoesNotExist:
        logger.error(f"Invitation {invitation_id} not found")
    except Exception as e:
        logger.error(f"Error in send_regret_email_task: {str(e)}")

@shared_task
def cleanup_expired_reservations_task():
    """
    Background task to release expired slot reservations.
    Can be scheduled via Celery Beat to run every minute.
    """
    from .models import InterviewSlot
    from django.utils import timezone
    
    now = timezone.now()
    expired_slots = InterviewSlot.objects.filter(
        status=InterviewSlot.STATUS_RESERVED,
        reservation_expiry_time__lt=now
    )
    
    count = expired_slots.count()
    if count > 0:
        expired_slots.update(
            status=InterviewSlot.STATUS_AVAILABLE,
            reserved_by_token=None,
            reservation_expiry_time=None
        )
        logger.info(f"Released {count} expired interview slot reservations.")

@shared_task
def send_interview_confirmation_task(slot_id):
    """
    Sends confirmation emails to both candidate and interviewer after successful booking.
    """
    from .models import InterviewSlot
    from django.core.mail import send_mail
    from django.conf import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        slot = InterviewSlot.objects.select_related('interviewer', 'invitation', 'invitation__assessment').get(id=slot_id)
        inv = slot.invitation
        interviewer = slot.interviewer
        
        if not inv:
            logger.error(f"Slot {slot_id} has no invitation linked.")
            return

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:3000').rstrip('/')
        # Join links: /live-interview?token=<inv.token>
        candidate_link = f"{frontend_base}/live-interview?token={inv.token}"
        interviewer_link = f"{frontend_base}/live-interview-interviewer?token={inv.token}"
        
        display_date = slot.slot_date.strftime('%B %d, %Y')
        display_time = f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
        assessment_name = inv.assessment.name if inv.assessment else "Live Interview"
        
        # 1. Email to Candidate
        candidate_subject = f"Confirmed: Interview Scheduled for {assessment_name}"
        candidate_html = f"""
        <div style="font-family: sans-serif; max-width: 600px; color: #333; line-height: 1.6;">
            <div style="background-color: #4318FF; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">Interview Confirmed!</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
                <p>Dear <strong>{inv.name}</strong>,</p>
                <p>Your live interview for the <strong>{assessment_name}</strong> position has been successfully scheduled.</p>
                
                <div style="background: #f1f4ff; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #4318FF;">
                    <p style="margin: 5px 0;"><strong>📅 Date:</strong> {display_date}</p>
                    <p style="margin: 5px 0;"><strong>⏰ Time:</strong> {display_time}</p>
                </div>
                
                <p>Please use the button below to join the interview at the scheduled time:</p>
                <div style="margin: 35px 0; text-align: center;">
                    <a href="{candidate_link}" style="background-color: #4318FF; color: white; padding: 14px 35px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(67, 24, 255, 0.2);">Join Interview Session</a>
                </div>
                
                <div style="background-color: #fff8e1; padding: 15px; border-radius: 6px; border: 1px solid #ffe082; margin-top: 20px;">
                    <p style="margin: 0; font-size: 14px;"><strong>Important Notes:</strong></p>
                    <ul style="margin: 10px 0 0 0; font-size: 13px; color: #555;">
                        <li>Ensure you have a working camera and microphone.</li>
                        <li>Join from a quiet environment with a stable internet connection.</li>
                        <li>Recommend joining 5 minutes early to test your audio/video.</li>
                    </ul>
                </div>
                
                <p style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; font-size: 13px; color: #888;">
                    Best regards,<br/><strong>The VerifiHire Team</strong>
                </p>
            </div>
        </div>
        """
        
        send_mail(
            subject=candidate_subject,
            message=f"Dear {inv.name}, your interview is confirmed for {display_date} at {display_time}. Link: {candidate_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inv.email],
            html_message=candidate_html,
            fail_silently=False
        )
        
        # 2. Email to Interviewer
        interviewer_subject = f"Confirmed: Interview with {inv.name} ({assessment_name})"
        interviewer_html = f"""
        <div style="font-family: sans-serif; max-width: 600px; color: #333; line-height: 1.6;">
            <div style="background-color: #16a34a; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 24px;">New Interview Scheduled</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
                <p>Hello <strong>{interviewer.first_name or interviewer.email}</strong>,</p>
                <p>A new live interview session has been booked with <strong>{inv.name}</strong>.</p>
                
                <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #16a34a;">
                    <p style="margin: 5px 0;"><strong>👤 Candidate:</strong> {inv.name}</p>
                    <p style="margin: 5px 0;"><strong>📧 Email:</strong> {inv.email}</p>
                    <p style="margin: 5px 0;"><strong>📅 Date:</strong> {display_date}</p>
                    <p style="margin: 5px 0;"><strong>⏰ Time:</strong> {display_time}</p>
                </div>
                
                <p>You can start the interview session using the button below:</p>
                <div style="margin: 35px 0; text-align: center;">
                    <a href="{interviewer_link}" style="background-color: #16a34a; color: white; padding: 14px 35px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(22, 163, 74, 0.2);">Start Interview Session</a>
                </div>
                
                <p style="margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px; font-size: 13px; color: #888;">
                    Best regards,<br/><strong>The VerifiHire Team</strong>
                </p>
            </div>
        </div>
        """
        
        send_mail(
            subject=interviewer_subject,
            message=f"New interview with {inv.name} on {display_date} at {display_time}. Start link: {interviewer_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[interviewer.email],
            html_message=interviewer_html,
            fail_silently=False
        )
        
        logger.info(f"Confirmation emails sent for slot {slot_id} to candidate ({inv.email}) and interviewer ({interviewer.email})")
        
    except Exception as e:
        logger.error(f"Error in send_interview_confirmation_task: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


@shared_task
def send_qualification_request_email_task(request_id):
    from .models import QualificationRequest, UserProfile
    from django.core.mail import send_mail
    from django.conf import settings
    
    logger.info(f"Executing send_qualification_request_email_task for request {request_id}")
    try:
        qual_req = QualificationRequest.objects.select_related('requester').get(id=request_id)
        requester = qual_req.requester
        
        if not requester or not requester.company:
            return
            
        # Find company admins and app admins
        admins = UserProfile.objects.filter(
            company=requester.company,
            role=UserProfile.ROLE_COMPANY_ADMIN
        ).values_list('email', flat=True)
        
        app_admins = UserProfile.objects.filter(
            role=UserProfile.ROLE_APPLICATION_ADMIN
        ).values_list('email', flat=True)
        
        admin_emails = list(admins) + list(app_admins)
        if not admin_emails:
            logger.warning(f"No admins found for company {requester.company.name}")
            return
            
        subject = f"New Qualification Request Pending Approval: {qual_req.candidate_name}"
        message = f"""Hello Admin,

A new qualification request has been submitted by {requester.first_name or requester.email} for candidate {qual_req.candidate_name}.

Requested Status: {qual_req.requested_result}
Reason: {qual_req.reason}

Please log in to the dashboard and go to Settings to review and approve or reject this request.

Best regards,
VerifiHire Team"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=True
        )
        logger.info(f"Sent qualification request email to {len(admin_emails)} admins.")
    except Exception as e:
        logger.error(f"Error in send_qualification_request_email_task: {str(e)}")



@shared_task
def send_qualification_action_email_task(request_id, action, reason=None):
    from .models import QualificationRequest
    from django.core.mail import send_mail
    from django.conf import settings
    
    logger.info(f"Executing send_qualification_action_email_task for request {request_id}")
    try:
        qual_req = QualificationRequest.objects.select_related('requester', 'actioned_by').get(id=request_id)
        requester = qual_req.requester
        
        if not requester or not requester.email:
            logger.warning(f"No email found for requester of request {request_id}")
            return
            
        admin_name = qual_req.actioned_by.first_name or qual_req.actioned_by.email if qual_req.actioned_by else "an Admin"
        
        subject = f"Qualification Request {action.title()}: {qual_req.candidate_name}"
        
        if action == 'approved':
            message = f"""Hello {requester.first_name or 'HR'},

Your qualification request for candidate {qual_req.candidate_name} has been APPROVED by {admin_name}.
The candidate's status has been successfully updated to '{qual_req.requested_result}'.

Best regards,
VerifiHire Team"""
        else:
            message = f"""Hello {requester.first_name or 'HR'},

Your qualification request for candidate {qual_req.candidate_name} has been REJECTED by {admin_name}.

Reason for rejection: {reason or qual_req.rejection_reason or 'No reason provided.'}

Best regards,
VerifiHire Team"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[requester.email],
            fail_silently=True
        )
        logger.info(f"Sent qualification action email to {requester.email}")
    except Exception as e:
        logger.error(f"Error in send_qualification_action_email_task: {str(e)}")


# ─── Plagiarism Detection Task ────────────────────────────────────────────────

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def run_plagiarism_check_task(self, submission_id: int, question_id: int):
    """
    Background Celery task: run Winnowing-based plagiarism check for a
    newly saved CodingSubmission and store the result back into the
    submission's `results` JSONField.

    Triggered automatically after every coding submission.
    Runs asynchronously — zero impact on candidate submission speed.

    Parameters
    ----------
    submission_id : int   — ID of the newly created CodingSubmission
    question_id   : int   — ID of the coding question (used to scope comparison)
    """
    from api.models import CodingSubmission
    from api.utils.plagiarism_checker import check_plagiarism

    logger.info(
        f"[PLAGIARISM TASK] Starting check | submission_id={submission_id} | question_id={question_id}"
    )

    try:
        # Run the plagiarism check engine
        plagiarism_result = check_plagiarism(
            new_submission_id=submission_id,
            question_id=question_id,
        )

        # Merge result into the submission's existing results JSONField
        try:
            sub = CodingSubmission.objects.get(id=submission_id)
            existing_results = sub.results or {}
            existing_results['plagiarism'] = plagiarism_result
            sub.results = existing_results
            sub.save(update_fields=['results'])

            # Automatically update parent CandidateSubmission result to 'hold' if flagged/high_risk
            is_plagiarism_flagged = plagiarism_result.get('flagged', False)
            risk_level = plagiarism_result.get('risk', {}).get('level', 'clean')
            if is_plagiarism_flagged or risk_level in ['flagged', 'high_risk']:
                try:
                    from api.models import CandidateSubmission
                    parent_sub = CandidateSubmission.objects.filter(
                        invitation__email__iexact=sub.user_email
                    ).first()
                    if parent_sub:
                        parent_sub.result = 'hold'
                        parent_sub.save(update_fields=['result'])
                        logger.info(
                            f"[PLAGIARISM TASK] Auto-held CandidateSubmission {parent_sub.id} "
                            f"due to plagiarism check (level={risk_level})"
                        )
                except Exception as _hold_err:
                    logger.error(f"[PLAGIARISM TASK] Failed to auto-hold candidate: {_hold_err}")

            logger.info(
                f"[PLAGIARISM TASK] Done | submission_id={submission_id} | "
                f"score={plagiarism_result.get('similarity_score', 0)}% | "
                f"flagged={plagiarism_result.get('flagged', False)}"
            )
        except CodingSubmission.DoesNotExist:
            logger.error(f"[PLAGIARISM TASK] Submission {submission_id} not found when saving result.")

    except Exception as exc:
        logger.error(
            f"[PLAGIARISM TASK] Failed for submission_id={submission_id}: {exc}",
            exc_info=True
        )
        # Retry up to max_retries times with a 30-second delay
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"[PLAGIARISM TASK] Max retries exceeded for submission_id={submission_id}")
