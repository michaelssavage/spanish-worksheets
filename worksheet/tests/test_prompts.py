import json

from django.test import SimpleTestCase

from worksheet.services.prompts import (
    TRANSLATION_ITEMS,
    TRANSLATION_KEY,
    build_payload,
    build_user_prompt,
)

TEST_POOLS = ["past tenses", "present forms", "subjunctive", "connectors"]


class BuildUserPromptTest(SimpleTestCase):
    def test_includes_a_section_per_grammar_pool(self):
        prompt = build_user_prompt(["bugs"], TEST_POOLS)

        for pool in TEST_POOLS:
            self.assertIn(f'"{pool}"', prompt)

    def test_includes_translation_section(self):
        prompt = build_user_prompt(["bugs"], TEST_POOLS)

        self.assertIn(f'"{TRANSLATION_KEY}"', prompt)
        self.assertIn("English sentence", prompt)

    def test_schema_is_valid_json_once_filled_in(self):
        prompt = build_user_prompt(["bugs"], TEST_POOLS)
        schema_block = prompt[prompt.index("{") : prompt.rindex("}") + 1]  # noqa: E203

        parsed = json.loads(schema_block)

        self.assertEqual(set(parsed.keys()), set(TEST_POOLS) | {TRANSLATION_KEY})
        for pool in TEST_POOLS:
            self.assertEqual(len(parsed[pool]), 5)
        self.assertEqual(len(parsed[TRANSLATION_KEY]), TRANSLATION_ITEMS)

    def test_grammar_section_rules_are_scoped_away_from_translation(self):
        prompt = build_user_prompt(["bugs"], TEST_POOLS)

        self.assertIn(f'NOT "{TRANSLATION_KEY}"', prompt)


class BuildPayloadTest(SimpleTestCase):
    def test_returns_system_and_user_messages(self):
        payload = build_payload(["bugs"], TEST_POOLS)

        self.assertEqual([m["role"] for m in payload], ["system", "user"])
        self.assertIn(TRANSLATION_KEY, payload[1]["content"])
