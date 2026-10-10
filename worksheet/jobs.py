import logging
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django_rq import job

from worksheet.services.email import send_worksheet_email
from worksheet.services.generate import generate_worksheet_for
from worksheet.services.languages import get_language


logger = logging.getLogger(__name__)
User = get_user_model()


@job("default", timeout=600)
def generate_worksheet_job(user_id, language="es", themes=None):
    """
    Long-lived RQ workers must reset DB connections so queries survive Postgres
    restarts (common on Railway) instead of hanging on a dead socket.
    """
    close_old_connections()
    try:
        user = User.objects.get(id=user_id)
        lang = get_language(language)

        logger.info("RQ %s job started for user %s", lang.code, user.email)

        content = generate_worksheet_for(user, themes=themes, language=lang.code)

        if content is None:
            logger.warning("Duplicate %s worksheet detected in job", lang.code)
            return {"status": "duplicate"}

        if lang.sends_email:
            try:
                from worksheet.models import Worksheet

                worksheet = (
                    Worksheet.objects.filter(user=user, language=lang.code)
                    .order_by("-created_at")
                    .first()
                )
                themes = worksheet.themes if worksheet and worksheet.themes else None
                send_worksheet_email(user, content, theme=themes)
            except Exception as e:
                logger.error("Email failed: %s", e)

        logger.info("RQ %s job finished for user %s", lang.code, user.email)
        return {"status": "success"}
    finally:
        close_old_connections()
