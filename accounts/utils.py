from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_otp_email(user_email, otp_code):
    subject = 'Verify your TechTaskSoln account'
    message = f"""Hi there,

Your TechTaskSoln email verification code is:

    {otp_code}

This code expires in 10 minutes.
If you did not create an account, please ignore this email.

— The TechTaskSoln Team
"""
    # Always print OTP to console so development never gets blocked
    print(f"\n{'='*50}")
    print(f"OTP for {user_email}: {otp_code}")
    print(f"{'='*50}\n")

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    except Exception as e:
        # Log the error but don't let it crash registration
        logger.error(f"Failed to send OTP email to {user_email}: {e}")
        print(f"[EMAIL ERROR] Could not send email: {e}")
        print(f"[DEV] OTP code for {user_email}: {otp_code}")