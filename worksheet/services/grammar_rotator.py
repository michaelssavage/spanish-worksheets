from worksheet.models import Config
from worksheet.services.grammar_pools import GRAMMAR_POOLS
import logging

logger = logging.getLogger(__name__)

POOLS_PER_WORKSHEET = 4


def get_and_increment_grammar_pools():
    """
    Returns POOLS_PER_WORKSHEET grammar pool names for this generation,
    and advances the index for next time.
    """
    cfg, created = Config.objects.get_or_create(
        key="grammar_pool_index", defaults={"value": "0"}
    )

    if created:
        logger.info("Created new grammar_pool_index config, starting at 0")
    else:
        logger.debug(f"Retrieved existing grammar_pool_index: {cfg.value}")

    index = int(cfg.value)
    pool_count = len(GRAMMAR_POOLS)
    pools = [
        GRAMMAR_POOLS[(index + i) % pool_count] for i in range(POOLS_PER_WORKSHEET)
    ]

    logger.info(f"Selected grammar pools at index {index}: {pools}")

    cfg.value = str((index + POOLS_PER_WORKSHEET) % pool_count)
    cfg.save()
    logger.debug(f"Incremented grammar_pool_index to {cfg.value}")

    return pools
