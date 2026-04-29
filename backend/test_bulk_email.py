#!/usr/bin/env python
"""
Test bulk invite email sending directly
"""
import os
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from django.core.mail import send_mail, get_connection
from django.conf import settings
from django.utils import timezone
import django

def test_smtp_connection_detailed():
    """Test SMTP with detailed diagnostics"""
    
    print("=" * 70)
    print("DETAILED SMTP DIAGNOSTICS")
    print("=" * 70)
    
    # Test 1: Connection test
    print("\n1️⃣ Testing SMTP Connection...")
    try:
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            fail_silently=False,
        )
        connection.open()
        print("   ✅ SMTP Connection OPENED successfully")
        connection.close()
        print("   ✅ SMTP Connection CLOSED successfully")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    # Test 2: Send to same domain (gmail)
    print("\n2️⃣ Testing email to Gmail (same domain)...")
    try:
        send_mail(
            subject='Test 2 - Gmail to Gmail',
            message='Test email to same domain',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['python.nexnoratech@gmail.com'],
            fail_silently=False,
        )
        print("   ✅ Email to Gmail SENT")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Send to external domain (mlrit.ac.in)
    print("\n3️⃣ Testing email to external domain (mlrit.ac.in)...")
    try:
        send_mail(
            subject='Test 3 - To External Domain',
            message='Test email to external domain',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['22r21a67d5@mlrit.ac.in'],
            fail_silently=False,
        )
        print("   ✅ Email to mlrit.ac.in SENT")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        print(traceback.format_exc())
    
    # Test 4: Simulate bulk invite parameters
    print("\n4️⃣ Simulating bulk invite email...")
    try:
        name = "Test Candidate"
        email = "22r21a67d5@mlrit.ac.in"
        link = "http://localhost:3000/interview-start/test-token"
        from_str = "Immediately"
        until_str = "No fixed deadline"
        batch_interview_time = "5:00 PM"
        
        message = f"Dear {name},\n\nYou have been invited to complete an AI-powered video interview.\n\nTiming Details:\n- Available From: {from_str}\n- Available Until: {until_str}\n\nPlease click the link below to verify your details and start your session:\n{link}"
        
        html_message = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background-color: #6366F1; padding: 24px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Interview Invitation</h1>
            </div>
            <div style="padding: 32px; background-color: white;">
                <p style="font-size: 16px; margin-bottom: 24px;">Dear <strong>{name}</strong>,</p>
                <p style="line-height: 1.6; margin-bottom: 24px;">You have been invited to attempt an AI-powered video interview session.</p>
                <a href="{link}">Start Interview</a>
            </div>
        </div>
        """
        
        send_mail(
            subject="Invite to VerifiHireAI Interview Session",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message
        )
        print("   ✅ Bulk invite style email SENT")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n" + "=" * 70)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 70)

if __name__ == '__main__':
    test_smtp_connection_detailed()
