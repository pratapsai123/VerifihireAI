from celery import shared_task
from .pipeline import process_resume_passed, process_assessment_passed
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_assessment_link_task(candidate_id):
    logger.info(f"Executing send_assessment_link_task for candidate {candidate_id}")
    process_resume_passed(candidate_id)

@shared_task
def send_interview_link_task(submission_id):
    logger.info(f"Executing send_interview_link_task for submission {submission_id}")
    process_assessment_passed(submission_id)

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
                <p><strong>Your Final Score:</strong> {submission.percentage}%</p>
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
            # Optional: Send rejection email? 
            # User specifically asked for 'cleard message and slot booking'.
            logger.info(f"Candidate {inv.email} not qualified ({submission.percentage}%). No email sent.")
            
    except CandidateInvitation.DoesNotExist:
        logger.error(f"Invitation {invitation_id} not found")
    except Exception as e:
        logger.error(f"Error in send_custom_assessment_result_task: {str(e)}")

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

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', 'https://verifihireai.com').rstrip('/')
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
