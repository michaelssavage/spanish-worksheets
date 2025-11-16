from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


def send_worksheet_email(user, content):
    logger.info(f"Sending worksheet email to {user.email}")
    subject = "Your Spanish Worksheet"
    send_mail(
        subject,
        content,
        "noreply@example.com",
        [user.email],
    )
    logger.info(f"Email sent successfully to {user.email}")
