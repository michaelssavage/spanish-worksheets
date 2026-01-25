import json
import logging
import random
import requests
from django.conf import settings
from django.utils.html import escape

logger = logging.getLogger(__name__)


def normalize_to_list(value):
    """Convert string values to list by splitting on sentence patterns.

    Handles cases where LLM returns a string instead of an array.
    Supports multiple patterns:
    - Pattern 1: '", "' for quoted list strings
    - Pattern 2: '., ' for period-comma-space sentence boundaries
    """
    if isinstance(value, list):
        return value
    elif isinstance(value, str):
        # Pattern 1: Split by '", "' (for quoted list strings)
        if '", "' in value:
            return [s.strip().strip('"').strip("'") for s in value.split('", "')]

        # Pattern 2: Split by '., ' (period, comma, space - sentence boundaries)
        if "., " in value:
            parts = value.split("., ")
            return [
                s.strip() + ("." if i < len(parts) - 1 else "")
                for i, s in enumerate(parts)
            ]

        return [value]
    else:
        return []


def format_worksheet_html(content_json, theme=None):
    """Parse JSON content and format it as HTML with 4 numbered lists."""
    try:
        # Parse the JSON content
        if isinstance(content_json, str):
            data = json.loads(content_json)
        else:
            data = content_json

        # Extract the four sections and normalize to lists
        sections = [
            ("Past Tense", normalize_to_list(data.get("past", []))),
            ("Present Tense", normalize_to_list(data.get("present", []))),
            ("Future Tense", normalize_to_list(data.get("future", []))),
            ("Error Correction", normalize_to_list(data.get("vocab", []))),
        ]

        # Randomize the order of sections
        random.shuffle(sections)

        # Format theme for display
        if theme:
            if isinstance(theme, list):
                theme_display = ", ".join(theme)
            else:
                theme_display = str(theme)
        else:
            theme_display = "Your Spanish Worksheet"

        # Build HTML with numbered lists
        # Use explicit numbering in text for better Notion compatibility when copying
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #2c3e50;">{escape(theme_display)}</h2>
        """

        # Build each section dynamically in randomized order
        for section_title, sentences in sections:
            html_content += f"""
            <h3 style="color: #34495e; margin-top: 30px;">{escape(section_title)}</h3>
            <ol style="margin-left: 20px; list-style-type: decimal;">
        """

            for i, sentence in enumerate(sentences, 1):
                # Escape HTML special characters to prevent XSS
                escaped_sentence = escape(str(sentence))
                # Include explicit number in text for Notion compatibility
                html_content += (
                    f'                <li style="margin-bottom: 10px;">'
                    f"<span>{i}. </span>{escaped_sentence}</li>\n"
                )

            html_content += """            </ol>
        """

        html_content += """        </body>
        </html>
        """

        return html_content
    except (json.JSONDecodeError, KeyError, AttributeError) as e:
        logger.error(f"Error parsing worksheet content: {e}")
        # Fallback to plain text if JSON parsing fails
        return f"<html><body><pre>{content_json}</pre></body></html>"


def send_worksheet_email(user, content, theme=None):
    """Send worksheet email to user and their additional recipients."""
    logger.info(f"Sending worksheet email to {user.email}")

    # Fetch all recipients for this user
    all_recipients = list(user.email_recipients.values_list("email", flat=True))

    subject = "Your Spanish Worksheet"
    html_message = format_worksheet_html(content, theme=theme)

    try:
        if isinstance(content, str):
            data = json.loads(content)
        else:
            data = content

        plain_text = "Your Spanish Worksheet\n\n"
        plain_text += "1. El pasado:\n"
        for i, sentence in enumerate(normalize_to_list(data.get("past", [])), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n2. El presente:\n"
        for i, sentence in enumerate(normalize_to_list(data.get("present", [])), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n3. El futuro:\n"
        for i, sentence in enumerate(normalize_to_list(data.get("future", [])), 1):
            plain_text += f"   {i}. {sentence}\n"
        plain_text += "\n4. Ampliación de vocabulario:\n"
        for i, sentence in enumerate(normalize_to_list(data.get("vocab", [])), 1):
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
