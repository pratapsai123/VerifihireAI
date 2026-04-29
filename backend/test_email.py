#!/usr/bin/env python
"""
Test script to verify SMTP email configuration
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

def test_smtp_connection():
    """Test SMTP connection and send a test email"""
    
    print("=" * 60)
    print("SMTP Email Configuration Test")
    print("=" * 60)
    
    # Print current settings
    print(f"\n📧 Email Settings:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test recipient
    test_email = "python.nexnoratech@gmail.com"  # Send to same address for testing
    
    print(f"\n📝 Test Details:")
    print(f"   To: {test_email}")
    print(f"   Subject: SMTP Test Email")
    print(f"   Time: {timezone.now()}")
    
    try:
        print(f"\n🔄 Sending test email...")
        
        result = send_mail(
            subject='SMTP Test Email - VerifiHire AI',
            message='This is a test email to verify SMTP configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
            html_message='''
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #6366F1;">SMTP Test Email</h2>
                <p>This is a test email to verify SMTP configuration is working correctly.</p>
                <p><strong>Time:</strong> {}</p>
                <p>If you received this email, your SMTP configuration is working!</p>
            </body>
            </html>
            '''.format(timezone.now())
        )
        
        print(f"\n✅ SUCCESS! Email sent successfully!")
        print(f"   Messages sent: {result}")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED! Error sending email:")
        print(f"   Error: {str(e)}")
        
        import traceback
        print(f"\n📋 Detailed Traceback:")
        print(traceback.format_exc())
        
        return False

if __name__ == '__main__':
    success = test_smtp_connection()
    print("\n" + "=" * 60)
    if success:
        print("✅ SMTP Test PASSED")
    else:
        print("❌ SMTP Test FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
