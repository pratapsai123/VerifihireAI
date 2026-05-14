content = open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\tasks.py', 'r', encoding='utf-8').read()

task_code = '''
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
            
        # Find company admins
        admins = UserProfile.objects.filter(
            company=requester.company,
            role=UserProfile.ROLE_COMPANY_ADMIN
        ).values_list('email', flat=True)
        
        admin_emails = list(admins)
        if not admin_emails:
            logger.warning(f"No admins found for company {requester.company.name}")
            return
            
        subject = f"New Qualification Request Pending Approval: {qual_req.candidate_name}"
        message = (
            f"Hello Admin,\n\n"
            f"A new qualification request has been submitted by {requester.first_name or requester.email} "
            f"for candidate {qual_req.candidate_name}.\n\n"
            f"Requested Status: {qual_req.requested_result}\n"
            f"Reason: {qual_req.reason}\n\n"
            f"Please log in to the dashboard and go to Settings to review and approve or reject this request.\n\n"
            f"Best regards,\nVerifiHire Team"
        )
        
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
'''

if 'send_qualification_request_email_task' not in content:
    with open('C:\\Users\\eduma\\Desktop\\VerifiHireAI\\backend\\api\\tasks.py', 'a', encoding='utf-8') as f:
        f.write("\n" + task_code + "\n")
    print('Added task to tasks.py')
else:
    print('Task already exists in tasks.py')
