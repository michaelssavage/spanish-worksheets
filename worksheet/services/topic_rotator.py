from worksheet.models import Config
from worksheet.services.prompts import THEME_POOLS


def get_and_increment_topics():
    """
    Returns the theme list for this generation,
    and increments the index for next time.
    """
    cfg, _ = Config.objects.get_or_create(key="topic_index", defaults={"value": "0"})

    index = int(cfg.value)
    themes = THEME_POOLS[index % len(THEME_POOLS)]

    cfg.value = str(index + 1)
    cfg.save()

    return themes
