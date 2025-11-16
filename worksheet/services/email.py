from django.core.mail import send_mail


def send_worksheet_email(user, content):
    subject = "Your Spanish Worksheet"
    send_mail(
        subject,
        content,
        "noreply@example.com",
        [user.email],
    )
