from worksheet.models import Config
from worksheet.services.languages import SPANISH, LanguageConfig
import logging

logger = logging.getLogger(__name__)

POOLS_PER_WORKSHEET = 4


def get_and_increment_grammar_pools(language: LanguageConfig = SPANISH):
    """
    Returns POOLS_PER_WORKSHEET grammar pool names for this generation,
    and advances the index for next time. Each language rotates independently.
    """
    cfg, created = Config.objects.get_or_create(
        key=language.grammar_index_key, defaults={"value": "0"}
    )

    if created:
        logger.info("Created new %s config, starting at 0", language.grammar_index_key)
    else:
        logger.debug("Retrieved existing %s: %s", language.grammar_index_key, cfg.value)

    grammar_pools = language.grammar_pools
    index = int(cfg.value)
    pool_count = len(grammar_pools)
    pools = [
        grammar_pools[(index + i) % pool_count] for i in range(POOLS_PER_WORKSHEET)
    ]

    logger.info(
        "Selected %s grammar pools at index %s: %s", language.code, index, pools
    )

    cfg.value = str((index + POOLS_PER_WORKSHEET) % pool_count)
    cfg.save()
    logger.debug("Incremented %s to %s", language.grammar_index_key, cfg.value)

    return pools
