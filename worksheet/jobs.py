import logging
from django_rq import job
from django.contrib.auth import get_user_model

from worksheet.services.email import send_worksheet_email
from worksheet.services.generate import generate_worksheet_for


logger = logging.getLogger(__name__)
User = get_user_model()


@job("default", timeout=600)
def generate_worksheet_job(user_id):
    user = User.objects.get(id=user_id)

    logger.info(f"RQ job started for user {user.email}")

    content = generate_worksheet_for(user)

    if content is None:
        logger.warning("Duplicate worksheet detected in job")
        return {"status": "duplicate"}

    try:
        send_worksheet_email(user, content)
    except Exception as e:
        logger.error(f"Email failed: {e}")

    return {"status": "success"}
