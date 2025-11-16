from worksheet.models import Config
from worksheet.services.prompts import THEME_POOLS
import logging

logger = logging.getLogger(__name__)


def get_and_increment_topics():
    """
    Returns the theme list for this generation,
    and increments the index for next time.
    """
    cfg, created = Config.objects.get_or_create(
        key="topic_index", defaults={"value": "0"}
    )

    if created:
        logger.info("Created new topic_index config, starting at 0")
    else:
        logger.debug(f"Retrieved existing topic_index: {cfg.value}")

    index = int(cfg.value)
    themes = THEME_POOLS[index % len(THEME_POOLS)]

    logger.info(
        f"Selected theme pool at index {index} (pool {index % len(THEME_POOLS)}): {themes}"
    )

    cfg.value = str(index + 1)
    cfg.save()
    logger.debug(f"Incremented topic_index to {cfg.value}")

    return themes
