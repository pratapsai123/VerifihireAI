content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\tasks.py', 'r', encoding='utf-8').read()

task_code = '''
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
'''

if 'send_qualification_action_email_task' not in content:
    with open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\tasks.py', 'a', encoding='utf-8') as f:
        f.write("\n" + task_code + "\n")
    print('Added task to tasks.py')
else:
    print('Task already exists in tasks.py')
