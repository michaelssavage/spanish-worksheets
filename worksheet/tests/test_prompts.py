import json

from django.test import SimpleTestCase

from worksheet.services.grammar_pools import (
    CATALAN_GRAMMAR_POOL_GUIDANCE,
    CATALAN_GRAMMAR_POOLS,
    SPANISH_GRAMMAR_POOL_GUIDANCE,
    SPANISH_GRAMMAR_POOLS,
)
from worksheet.services.languages import CATALAN, SPANISH
from worksheet.services.prompts import (
    CATALAN_SYSTEM_PROMPT,
    SPANISH_SYSTEM_PROMPT,
    TRANSLATION_ITEMS,
    TRANSLATION_KEY,
    build_custom_payload,
    build_payload,
    build_user_prompt,
)
from worksheet.services.themes import CATALAN_THEME_POOLS, SPANISH_THEME_POOLS

TEST_POOLS = ["past tenses", "present forms", "subjunctive", "por vs para"]
CATALAN_TEST_POOLS = ["past tenses", "pronoms febles", "subjunctive", "per vs per a"]


class BuildUserPromptTest(SimpleTestCase):
    def test_includes_a_section_per_grammar_pool(self):
        prompt = build_user_prompt(SPANISH, ["bugs"], TEST_POOLS)

        for pool in TEST_POOLS:
            self.assertIn(f'"{pool}"', prompt)

    def test_includes_translation_section(self):
        prompt = build_user_prompt(SPANISH, ["bugs"], TEST_POOLS)

        self.assertIn(f'"{TRANSLATION_KEY}"', prompt)
        self.assertIn("English clause", prompt)

    def test_schema_is_valid_json_once_filled_in(self):
        prompt = build_user_prompt(SPANISH, ["bugs"], TEST_POOLS)
        schema_block = prompt[prompt.index("{") : prompt.rindex("}") + 1]  # noqa: E203

        parsed = json.loads(schema_block)

        self.assertEqual(set(parsed.keys()), set(TEST_POOLS) | {TRANSLATION_KEY})
        for pool in TEST_POOLS:
            self.assertEqual(len(parsed[pool]), 5)
        self.assertEqual(len(parsed[TRANSLATION_KEY]), TRANSLATION_ITEMS)

    def test_grammar_section_rules_are_scoped_away_from_translation(self):
        prompt = build_user_prompt(SPANISH, ["bugs"], TEST_POOLS)

        self.assertIn(f'NOT "{TRANSLATION_KEY}"', prompt)

    def test_catalan_prompt_uses_catalan_guidance_and_language(self):
        prompt = build_user_prompt(CATALAN, ["bugs"], CATALAN_TEST_POOLS)

        self.assertIn(CATALAN_GRAMMAR_POOL_GUIDANCE["pronoms febles"], prompt)
        self.assertIn("Catalan only in prompts and answers", prompt)
        self.assertIn("Va arribar", prompt)
        self.assertNotIn("Spanish", prompt)


class BuildPayloadTest(SimpleTestCase):
    def test_returns_system_and_user_messages(self):
        payload = build_payload(SPANISH, ["bugs"], TEST_POOLS)

        self.assertEqual([m["role"] for m in payload], ["system", "user"])
        self.assertEqual(payload[0]["content"], SPANISH_SYSTEM_PROMPT)
        self.assertIn(TRANSLATION_KEY, payload[1]["content"])

    def test_catalan_payload_uses_catalan_system_prompt(self):
        payload = build_payload(CATALAN, ["bugs"], CATALAN_TEST_POOLS)

        self.assertEqual(payload[0]["content"], CATALAN_SYSTEM_PROMPT)

    def test_system_prompt_excludes_future_subjunctive(self):
        self.assertIn(
            "Never use the obsolete future subjunctive", SPANISH_SYSTEM_PROMPT
        )
        self.assertIn("hubiere cantado", SPANISH_SYSTEM_PROMPT)
        self.assertIn("future perfect indicative", SPANISH_SYSTEM_PROMPT)

    def test_catalan_system_prompt_bans_castilianisms_and_anar_a_future(self):
        self.assertIn("Castilianisms", CATALAN_SYSTEM_PROMPT)
        self.assertIn("anar a + infinitive", CATALAN_SYSTEM_PROMPT)
        self.assertNotIn("Spanish", CATALAN_SYSTEM_PROMPT)


class BuildCustomPayloadTest(SimpleTestCase):
    def test_spanish_custom_prompt(self):
        payload = build_custom_payload(SPANISH, "Subjunctive about movies")

        self.assertEqual(payload[0]["content"], SPANISH_SYSTEM_PROMPT)
        self.assertIn("8 Spanish conjugation exercises", payload[1]["content"])
        self.assertIn("ir a + infinitive", payload[1]["content"])

    def test_catalan_custom_prompt(self):
        payload = build_custom_payload(CATALAN, "Subjunctive about movies")

        self.assertEqual(payload[0]["content"], CATALAN_SYSTEM_PROMPT)
        self.assertIn("8 Catalan conjugation exercises", payload[1]["content"])
        self.assertIn("anar a + infinitive", payload[1]["content"])
        self.assertNotIn("Spanish", payload[1]["content"])


class LanguageDataTest(SimpleTestCase):
    def test_theme_pools_are_index_aligned(self):
        self.assertEqual(len(SPANISH_THEME_POOLS), len(CATALAN_THEME_POOLS))

    def test_every_pool_has_guidance(self):
        self.assertEqual(set(SPANISH_GRAMMAR_POOLS), set(SPANISH_GRAMMAR_POOL_GUIDANCE))
        self.assertEqual(set(CATALAN_GRAMMAR_POOLS), set(CATALAN_GRAMMAR_POOL_GUIDANCE))
