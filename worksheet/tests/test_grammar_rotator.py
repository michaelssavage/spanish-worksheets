from django.test import TestCase

from worksheet.models import Config
from worksheet.services.grammar_pools import GRAMMAR_POOLS
from worksheet.services.grammar_rotator import (
    POOLS_PER_WORKSHEET,
    get_and_increment_grammar_pools,
)


class GrammarRotatorTest(TestCase):
    def test_creates_config_starting_at_zero(self):
        self.assertFalse(Config.objects.filter(key="grammar_pool_index").exists())

        pools = get_and_increment_grammar_pools()

        self.assertEqual(pools, GRAMMAR_POOLS[:POOLS_PER_WORKSHEET])
        cfg = Config.objects.get(key="grammar_pool_index")
        self.assertEqual(cfg.value, str(POOLS_PER_WORKSHEET))

    def test_returns_requested_number_of_distinct_pools(self):
        pools = get_and_increment_grammar_pools()

        self.assertEqual(len(pools), POOLS_PER_WORKSHEET)
        self.assertEqual(len(set(pools)), POOLS_PER_WORKSHEET)

    def test_advances_window_on_next_call(self):
        first = get_and_increment_grammar_pools()
        second = get_and_increment_grammar_pools()

        self.assertEqual(
            second, GRAMMAR_POOLS[POOLS_PER_WORKSHEET : POOLS_PER_WORKSHEET * 2]
        )
        self.assertNotEqual(first, second)

    def test_wraps_around_end_of_pool_list(self):
        cfg = Config.objects.create(
            key="grammar_pool_index",
            value=str(len(GRAMMAR_POOLS) - 1),
        )

        pools = get_and_increment_grammar_pools()

        expected = [
            GRAMMAR_POOLS[(len(GRAMMAR_POOLS) - 1 + i) % len(GRAMMAR_POOLS)]
            for i in range(POOLS_PER_WORKSHEET)
        ]
        self.assertEqual(pools, expected)

        cfg.refresh_from_db()
        self.assertEqual(
            cfg.value,
            str((len(GRAMMAR_POOLS) - 1 + POOLS_PER_WORKSHEET) % len(GRAMMAR_POOLS)),
        )
