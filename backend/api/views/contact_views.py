from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from api.models import ContactSubmission
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_us_view(request):
    try:
        data = request.data
        full_name = data.get('full_name')
        email = data.get('email')
        company = data.get('company', 'Not provided')
        subject = data.get('subject')
        message = data.get('message')

        if not full_name or not email or not subject or not message:
            return Response({'success': False, 'error': 'Please provide all required fields.'}, status=400)

        # Save to database
        submission = ContactSubmission.objects.create(
            full_name=full_name,
            email=email,
            company=company,
            subject=subject,
            message=message
        )

        # Construct email message
        email_subject = f"New Contact Request: {subject}"
        email_body = f"""
You have received a new contact submission.

Name: {full_name}
Email: {email}
Company: {company}
Subject: {subject}

Message:
{message}
"""
        
        # Determine from_email, fallback to a default if not set
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@verifihire.com')

        # Send an email to the required recipient
        send_mail(
            subject=email_subject,
            message=email_body,
            from_email=from_email,
            recipient_list=['sumanth.vishwanthula@iit.org.in'],
            fail_silently=False,
        )

        return Response({'success': True, 'message': 'Contact info submitted successfully.'})
    
    except Exception as e:
        logger.error(f"Error sending contact email: {e}")
        return Response({'success': False, 'error': 'An internal error occurred. Please try again later.'}, status=500)
