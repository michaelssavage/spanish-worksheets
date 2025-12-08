from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import escape
import json
import logging

logger = logging.getLogger(__name__)


def format_worksheet_html(content_json):
    """Parse JSON content and format it as HTML with 3 numbered lists."""
    try:
        # Parse the JSON content
        if isinstance(content_json, str):
            data = json.loads(content_json)
        else:
            data = content_json

        # Extract the three sections
        past = data.get("past", [])
        present_future = data.get("present_future", [])
        vocab = data.get("vocab", [])

        # Build HTML with numbered lists
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">Your Spanish Worksheet</h2>

            <h3 style="color: #34495e; margin-top: 30px;">1. Past Tense</h3>
            <ol style="margin-left: 20px;">
        """

        for sentence in past:
            # Escape HTML special characters to prevent XSS
            escaped_sentence = escape(str(sentence))
            html_content += f'                <li style="margin-bottom: 10px;">{escaped_sentence}</li>\n'

        html_content += """            </ol>

            <h3 style="color: #34495e; margin-top: 30px;">2. Present or Future Tense</h3>
            <ol style="margin-left: 20px;">
        """

        for sentence in present_future:
            escaped_sentence = escape(str(sentence))
            html_content += f'                <li style="margin-bottom: 10px;">{escaped_sentence}</li>\n'

        html_content += """            </ol>

            <h3 style="color: #34495e; margin-top: 30px;">3. Vocabulary Expansion</h3>
            <ol style="margin-left: 20px;">
        """

        for sentence in vocab:
            escaped_sentence = escape(str(sentence))
            html_content += f'                <li style="margin-bottom: 10px;">{escaped_sentence}</li>\n'

        html_content += """            </ol>
        </body>
        </html>
        """

        return html_content
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        logger.error(f"Error parsing worksheet content: {e}")
        # Fallback to plain text if JSON parsing fails
        return f"<html><body><pre>{content_json}</pre></body></html>"


def send_worksheet_email(user, content):
    """Send worksheet email to user with formatted HTML content."""
    logger.info(f"Sending worksheet email to {user.email}")
    subject = "Your Spanish Worksheet"

    html_message = format_worksheet_html(content)

    try:
        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content
        plain_text = "Your Spanish Worksheet\n\n"
        plain_text += "1. Past Tense:\n"
        for i, sentence in enumerate(data.get("past", []), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n2. Present or Future Tense:\n"
        for i, sentence in enumerate(data.get("present_future", []), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n3. Vocabulary Expansion:\n"
        for i, sentence in enumerate(data.get("vocab", []), 1):
            plain_text += f"   {i}. {sentence}\n"
    except (json.JSONDecodeError, KeyError, AttributeError):
        plain_text = str(content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_message, "text/html")

    try:
        email.send()
        logger.info(f"Email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {type(e).__name__}: {e}")
        logger.error(
            f"Email config - Host: {settings.EMAIL_HOST}, "
            f"Port: {settings.EMAIL_PORT}, TLS: {settings.EMAIL_USE_TLS}"
        )
        logger.error(f"Email user: {settings.EMAIL_HOST_USER[:10]}... (truncated)")
        raise
