import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock, Mock

from worksheet.services.generate import (
    extract_json_from_response,
    call_llm,
    generate_custom_exercises,
    generate_worksheet_for,
)
from worksheet.models import Worksheet

User = get_user_model()


def _section(prefix: str, *, conjugation: bool = True):
    return [
        {
            "prompt": (
                f"{prefix}-{i} ___ (hacer)"
                if conjugation
                else f"{prefix}-{i} English. (usar: infinitivo)"
            ),
            "answer": [f"sol-{prefix}-{i}"],
        }
        for i in range(8)
    ]


_MIN_WORKSHEET = {
    "past": _section("past"),
    "present": _section("present"),
    "future": _section("future"),
    "translation": _section("tr", conjugation=False),
}


def _custom_exercises(prefix: str = "custom"):
    return {
        "exercises": [
            {
                "prompt": f"Mi amiga ___ (venir) a la fiesta {i}.",
                "answer": [f"venga-{prefix}-{i}"],
            }
            for i in range(8)
        ]
    }


def _worksheet_with_past0(prompt: str, answer: str | list[str]):
    data = {
        "past": _section("past"),
        "present": _section("present"),
        "future": _section("future"),
        "translation": _section("tr", conjugation=False),
    }
    ans = [answer] if isinstance(answer, str) else answer
    data["past"][0] = {"prompt": prompt, "answer": ans}
    return data


class ExtractJsonFromResponseTest(TestCase):
    """Test JSON extraction from various LLM response formats"""

    def test_valid_json_without_markdown(self):
        """Test parsing clean JSON"""
        content = '{"key": "value"}'
        result = extract_json_from_response(content)
        self.assertEqual(result, content)

    def test_json_in_markdown_code_block(self):
        """Test extracting JSON from ```json block"""
        content = '```json\n{"key": "value"}\n```'
        result = extract_json_from_response(content)
        self.assertEqual(result, '{"key": "value"}')

    def test_json_in_plain_code_block(self):
        """Test extracting JSON from ``` block without json tag"""
        content = '```\n{"key": "value"}\n```'
        result = extract_json_from_response(content)
        self.assertEqual(result, '{"key": "value"}')

    def test_json_embedded_in_text(self):
        """Test extracting JSON object from surrounding text"""
        content = 'Here is your data: {"key": "value"} Please use it.'
        result = extract_json_from_response(content)
        self.assertEqual(result, '{"key": "value"}')

    def test_no_valid_json(self):
        """Test handling of content with no valid JSON"""
        content = "This is just plain text"
        result = extract_json_from_response(content)
        self.assertIsNone(result)

    def test_malformed_json_in_markdown(self):
        """Test handling of malformed JSON in markdown"""
        content = "```json\n{invalid json}\n```"
        result = extract_json_from_response(content)
        self.assertIsNone(result)


class CallLLMTest(TestCase):
    """Test LLM API calls with mocked external service"""

    @patch("worksheet.services.generate.OpenAI")
    def test_successful_api_call(self, mock_openai):
        """Test successful API call returns content"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"result": "success"}'
        mock_client.chat.completions.create.return_value = mock_response

        # Execute
        payload = [{"role": "user", "content": "test"}]
        result = call_llm(payload)

        # Assert
        self.assertEqual(result, '{"result": "success"}')
        mock_client.chat.completions.create.assert_called_once_with(
            model="deepseek-chat",
            messages=payload,
            temperature=0.7,
        )

    @patch("worksheet.services.generate.OpenAI")
    def test_api_call_with_markdown_response(self, mock_openai):
        """Test API call handles markdown-wrapped JSON"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '```json\n{"result": "success"}\n```'
        mock_client.chat.completions.create.return_value = mock_response

        payload = [{"role": "user", "content": "test"}]
        result = call_llm(payload)

        # call_llm returns the API message body unchanged
        self.assertEqual(result, '```json\n{"result": "success"}\n```')

    @patch("worksheet.services.generate.OpenAI")
    def test_api_call_exception_handling(self, mock_openai):
        """Test that API exceptions propagate correctly"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception(
            "API Error",
        )

        payload = [{"role": "user", "content": "test"}]

        with self.assertRaises(Exception) as context:
            call_llm(payload)

        self.assertIn("API Error", str(context.exception))


class GenerateWorksheetForTest(TestCase):
    """Test full worksheet generation workflow"""

    def setUp(self):
        """Create test user and clear any existing worksheets"""
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        Worksheet.objects.all().delete()

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_successful_worksheet_generation(self, mock_get_topics, mock_call_llm):
        """Test complete worksheet generation and saving"""
        # Setup mocks
        mock_get_topics.return_value = ["past", "present", "future"]
        payload = _worksheet_with_past0("test ___ (ver)", "sol-test")
        expected = json.dumps(payload, ensure_ascii=False)
        mock_call_llm.return_value = expected

        # Execute
        result = generate_worksheet_for(self.user)

        # Assert
        self.assertEqual(result, expected)
        self.assertEqual(Worksheet.objects.filter(user=self.user).count(), 1)

        worksheet = Worksheet.objects.get(user=self.user)
        self.assertEqual(worksheet.content, expected)
        self.assertEqual(
            worksheet.topics,
            ["past", "present", "future", "translation"],
        )

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_duplicate_content_returns_none(self, mock_get_topics, mock_call_llm):
        """Test that duplicate content hash returns None"""
        mock_get_topics.return_value = ["past", "present", "future"]
        mock_call_llm.return_value = json.dumps(_MIN_WORKSHEET, ensure_ascii=False)

        # Generate first worksheet
        result1 = generate_worksheet_for(self.user)
        self.assertIsNotNone(result1)

        # Try to generate duplicate
        result2 = generate_worksheet_for(self.user)
        self.assertIsNone(result2)

        # Should still only have one worksheet
        self.assertEqual(Worksheet.objects.filter(user=self.user).count(), 1)

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_replaces_existing_user_worksheet(self, mock_get_topics, mock_call_llm):
        """Test that new worksheet replaces old one for same user"""
        mock_get_topics.return_value = ["past", "present", "future"]

        # Create first worksheet
        first = json.dumps(
            _worksheet_with_past0("first ___ (ser)", "fa"), ensure_ascii=False
        )
        mock_call_llm.return_value = first
        generate_worksheet_for(self.user)

        # Create second worksheet with different content
        second = json.dumps(
            _worksheet_with_past0("second ___ (ir)", "sa"), ensure_ascii=False
        )
        mock_call_llm.return_value = second
        result = generate_worksheet_for(self.user)

        # Should only have one worksheet
        self.assertEqual(Worksheet.objects.filter(user=self.user).count(), 1)

        # Should be the new one
        worksheet = Worksheet.objects.get(user=self.user)
        self.assertEqual(worksheet.content, second)
        self.assertEqual(result, second)

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_different_users_can_have_same_content(
        self, mock_get_topics, mock_call_llm
    ):
        """Test that different users can have worksheets with same content"""
        user2 = User.objects.create_user(
            email="test2@example.com", password="testpass123"
        )

        mock_get_topics.return_value = ["past", "present", "future"]
        mock_call_llm.return_value = json.dumps(_MIN_WORKSHEET, ensure_ascii=False)

        # Generate for first user
        result1 = generate_worksheet_for(self.user)
        self.assertIsNotNone(result1)

        # Second user should get None (duplicate hash)
        result2 = generate_worksheet_for(user2)
        self.assertIsNone(result2)

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_llm_exception_propagates(self, mock_get_topics, mock_call_llm):
        """Test that LLM exceptions propagate correctly"""
        mock_get_topics.return_value = ["past", "present", "future"]
        mock_call_llm.side_effect = Exception("LLM API Error")

        with self.assertRaises(Exception) as context:
            generate_worksheet_for(self.user)

        self.assertIn("LLM API Error", str(context.exception))
        # No worksheet should be created
        self.assertEqual(Worksheet.objects.filter(user=self.user).count(), 0)

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_content_hash_calculation(self, mock_get_topics, mock_call_llm):
        """Test that content hash is calculated correctly"""
        import hashlib

        mock_get_topics.return_value = ["past", "present", "future"]
        test_content = json.dumps(_MIN_WORKSHEET, ensure_ascii=False)
        mock_call_llm.return_value = test_content

        generate_worksheet_for(self.user)

        worksheet = Worksheet.objects.get(user=self.user)
        expected_hash = hashlib.sha256(
            test_content.encode("utf-8"),
        ).hexdigest()
        self.assertEqual(worksheet.content_hash, expected_hash)

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_rejects_legacy_string_items(self, mock_get_topics, mock_call_llm):
        """Flat string lists (no prompt/answer) are no longer accepted."""
        mock_get_topics.return_value = ["past", "present", "future"]
        legacy = {
            "past": [str(i) for i in range(8)],
            "present": [str(i) for i in range(8)],
            "future": [str(i) for i in range(8)],
            "translation": [str(i) for i in range(8)],
        }
        mock_call_llm.return_value = json.dumps(legacy)

        result = generate_worksheet_for(self.user)

        self.assertIsNone(result)
        self.assertEqual(Worksheet.objects.filter(user=self.user).count(), 0)

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_explicit_themes_skip_topic_rotator(self, mock_get_topics, mock_call_llm):
        """When themes are passed in, the rotator is not used."""
        mock_call_llm.return_value = json.dumps(_MIN_WORKSHEET, ensure_ascii=False)

        generate_worksheet_for(self.user, themes=["bugs", "deploys"])

        mock_get_topics.assert_not_called()
        worksheet = Worksheet.objects.get(user=self.user)
        self.assertEqual(worksheet.themes, ["bugs", "deploys"])

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_retries_when_blank_validation_fails_once(
        self, mock_get_topics, mock_call_llm
    ):
        """Regenerates with a correction turn when ___ rules are violated."""
        bad = json.loads(json.dumps(_MIN_WORKSHEET))
        bad["past"][0] = {"prompt": "two ___ (a) ___ (b)", "answer": "x"}
        good = json.dumps(_MIN_WORKSHEET, ensure_ascii=False)
        mock_call_llm.side_effect = [
            json.dumps(bad, ensure_ascii=False),
            good,
        ]
        mock_get_topics.return_value = ["past", "present", "future"]

        result = generate_worksheet_for(self.user)

        self.assertIsNotNone(result)
        self.assertEqual(mock_call_llm.call_count, 2)
        self.assertEqual(
            Worksheet.objects.get(user=self.user).content,
            good,
        )

    @patch("worksheet.services.generate.call_llm")
    @patch("worksheet.services.generate.get_and_increment_topics")
    def test_normalizes_string_answers_from_llm(self, mock_get_topics, mock_call_llm):
        """String \"answer\" fields from the model are coerced to one-element lists."""
        mock_get_topics.return_value = ["past", "present", "future"]
        payload = json.loads(json.dumps(_MIN_WORKSHEET))
        for section in payload.values():
            for item in section:
                item["answer"] = item["answer"][0]
        mock_call_llm.return_value = json.dumps(payload, ensure_ascii=False)

        result = generate_worksheet_for(self.user)

        expected = json.dumps(_MIN_WORKSHEET, ensure_ascii=False)
        self.assertEqual(result, expected)
        stored = json.loads(Worksheet.objects.get(user=self.user).content)
        self.assertEqual(stored["past"][0]["answer"], ["sol-past-0"])


class GenerateCustomExercisesTest(TestCase):
    @patch("worksheet.services.generate.call_llm")
    def test_successful_custom_generation(self, mock_call_llm):
        payload = _custom_exercises()
        mock_call_llm.return_value = json.dumps(payload, ensure_ascii=False)

        result = generate_custom_exercises("Subjunctive tense about birthdays")

        self.assertEqual(result, payload)
        self.assertEqual(len(result["exercises"]), 8)

    @patch("worksheet.services.generate.call_llm")
    def test_custom_generation_repairs_json(self, mock_call_llm):
        payload = _custom_exercises()
        mock_call_llm.side_effect = [
            "not json",
            json.dumps(payload, ensure_ascii=False),
        ]

        result = generate_custom_exercises("Subjunctive tense about birthdays")

        self.assertEqual(result, payload)
        self.assertEqual(mock_call_llm.call_count, 2)

    @patch("worksheet.services.generate.call_llm")
    def test_custom_generation_normalizes_string_answers(self, mock_call_llm):
        payload = _custom_exercises()
        payload["exercises"][0]["answer"] = "venga"
        mock_call_llm.return_value = json.dumps(payload, ensure_ascii=False)

        result = generate_custom_exercises("Subjunctive tense about birthdays")

        self.assertEqual(result["exercises"][0]["answer"], ["venga"])

    @patch("worksheet.services.generate.call_llm")
    def test_custom_generation_retries_when_blank_validation_fails_once(
        self, mock_call_llm
    ):
        bad = _custom_exercises()
        bad["exercises"][0]["prompt"] = "Mi amiga viene a la fiesta."
        good = _custom_exercises("good")
        mock_call_llm.side_effect = [
            json.dumps(bad, ensure_ascii=False),
            json.dumps(good, ensure_ascii=False),
        ]

        result = generate_custom_exercises("Subjunctive tense about birthdays")

        self.assertEqual(result, good)
        self.assertEqual(mock_call_llm.call_count, 2)

    @patch("worksheet.services.generate.call_llm")
    def test_custom_generation_returns_none_for_invalid_structure(self, mock_call_llm):
        mock_call_llm.return_value = json.dumps({"exercises": []})

        result = generate_custom_exercises("Subjunctive tense about birthdays")

        self.assertIsNone(result)
