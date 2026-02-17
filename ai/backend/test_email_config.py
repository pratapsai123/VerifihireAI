import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

def test_email_config():
    print("📧 Testing Email Configuration...")
    
    host = os.environ.get('EMAIL_HOST')
    port = int(os.environ.get('EMAIL_PORT', 587))
    user = os.environ.get('EMAIL_HOST_USER')
    password = os.environ.get('EMAIL_HOST_PASSWORD')
    
    print(f"Server: {host}:{port}")
    print(f"User: {user}")
    
    if user == 'your-email@gmail.com':
        print("\n❌ CRITICAL: Default credentials detected in .env!")
        print("   You MUST update the EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in ai/backend/.env")
        return

    try:
        msg = EmailMessage()
        msg.set_content("This is a test email from VerifiHireAI backend to verify SMTP configuration.")
        msg['Subject'] = "VerifiHireAI SMTP Test"
        msg['From'] = user
        msg['To'] = user # Send to self
        
        print("\nAttempting connection...")
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(user, password)
        print("✅ Login successful!")
        
        server.send_message(msg)
        print(f"✅ Test email sent to {user}")
        server.quit()
        
    except Exception as e:
        print(f"\n❌ FAILED TO SEND EMAIL: {e}")
        print("\nTroubleshooting Tips:")
        print("1. If using Gmail, ensure 'App Password' is used, NOT your login password.")
        print("2. Check if 'Less secure app access' is enabled (deprecated, use App Passwords).")
        print("3. Verify firewall/antivirus isn't blocking port 587.")

if __name__ == "__main__":
    test_email_config()
