import json
import logging
import requests
from django.conf import settings
from django.utils.html import escape

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
    """Send worksheet email to user and their additional recipients."""
    logger.info(f"Sending worksheet email to {user.email}")

    # Fetch all recipients for this user
    all_recipients = list(user.email_recipients.values_list("email", flat=True))

    subject = "Your Spanish Worksheet"
    html_message = format_worksheet_html(content)

    try:
        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content
        plain_text = "Your Spanish Worksheet\n\n"
        plain_text += "1. El pasado:\n"
        for i, sentence in enumerate(data.get("past", []), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n2. El presente o futuro:\n"
        for i, sentence in enumerate(data.get("present_future", []), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n3. Ampliación de vocabulario:\n"
        for i, sentence in enumerate(data.get("vocab", []), 1):
            plain_text += f"   {i}. {sentence}\n"
    except (json.JSONDecodeError, KeyError, AttributeError):
        plain_text = str(content)

    if not settings.MAILGUN_API_KEY or not settings.MAILGUN_DOMAIN:
        raise ValueError(
            "Mailgun settings MAILGUN_API_KEY and MAILGUN_DOMAIN are required."
        )

    url = (
        f"{settings.MAILGUN_BASE_URL.rstrip('/')}/v3/{settings.MAILGUN_DOMAIN}/messages"
    )
    data = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": all_recipients,
        "subject": subject,
        "text": plain_text,
        "html": html_message,
    }

    try:
        response = requests.post(
            url,
            auth=("api", settings.MAILGUN_API_KEY),
            data=data,
            timeout=10,
        )

        if response.ok:
            logger.info(
                f"Email sent successfully to {len(all_recipients)} recipients via Mailgun"
            )
            return

        logger.error(
            f"Mailgun send failed (status {response.status_code}): {response.text}"
        )
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send email: {type(e).__name__}: {e}")
        raise
