from django.test import TestCase

from worksheet.services.exercise_items import (
    exercise_prompt_for_display,
    has_exactly_one_blank,
    normalize_custom_exercise_answers,
    normalize_worksheet_answers,
    parse_worksheet_content,
    validate_custom_blank_prompts,
    validate_custom_exercises,
    validate_worksheet_blank_prompts,
    validate_worksheet_exercises,
)


def _valid_data():
    sec = [{"prompt": f"p{i}", "answer": [f"a{i}"]} for i in range(8)]
    return {
        "past": sec,
        "present": sec,
        "future": sec,
        "translation": sec,
    }


def _valid_custom_data():
    return {
        "exercises": [
            {"prompt": f"Yo ___ (hacer) algo {i}.", "answer": [f"hago{i}"]}
            for i in range(8)
        ]
    }


class ExerciseItemsTest(TestCase):
    def test_prompt_for_display_dict(self):
        self.assertEqual(
            exercise_prompt_for_display({"prompt": "  hi  ", "answer": "x"}),
            "  hi  ",
        )

    def test_prompt_for_display_legacy_string(self):
        self.assertEqual(exercise_prompt_for_display("legacy"), "legacy")

    def test_prompt_for_display_bad(self):
        self.assertEqual(exercise_prompt_for_display({"answer": "only"}), "")
        self.assertEqual(exercise_prompt_for_display(3), "")

    def test_validate_full(self):
        self.assertTrue(validate_worksheet_exercises(_valid_data()))

    def test_validate_wrong_key_set(self):
        d = _valid_data()
        del d["translation"]
        self.assertFalse(validate_worksheet_exercises(d))

    def test_validate_wrong_count(self):
        d = _valid_data()
        d["past"] = d["past"][:6]
        self.assertFalse(validate_worksheet_exercises(d))

    def test_validate_string_item(self):
        d = _valid_data()
        d["past"][0] = "nope"
        self.assertFalse(validate_worksheet_exercises(d))

    def test_validate_string_answer(self):
        d = _valid_data()
        d["past"][0]["answer"] = "string-not-allowed"
        self.assertFalse(validate_worksheet_exercises(d))

    def test_validate_empty_answer_list(self):
        d = _valid_data()
        d["past"][0]["answer"] = []
        self.assertFalse(validate_worksheet_exercises(d))

    def test_validate_answer_list_with_blank_string(self):
        d = _valid_data()
        d["past"][0]["answer"] = ["ok", "  "]
        self.assertFalse(validate_worksheet_exercises(d))

    def test_normalize_coerces_string_answer(self):
        d = _valid_data()
        d["past"][0]["answer"] = "  solo  "
        normalize_worksheet_answers(d)
        self.assertEqual(d["past"][0]["answer"], ["solo"])

    def test_parse_content(self):
        import json

        data = _valid_data()
        raw = json.dumps(data)
        self.assertEqual(parse_worksheet_content(raw), data)
        self.assertEqual(parse_worksheet_content(data), data)

    def test_has_exactly_one_blank(self):
        self.assertTrue(has_exactly_one_blank("Foo ___ (hacer) bar"))
        self.assertFalse(has_exactly_one_blank("No blank here"))
        self.assertFalse(has_exactly_one_blank("Two ___ (a) ___ (b)"))

    def test_validate_worksheet_blank_prompts(self):
        d = _valid_data()
        self.assertFalse(validate_worksheet_blank_prompts(d))
        d["past"] = [
            {"prompt": f"p{i} ___ (ver)", "answer": [f"a{i}"]} for i in range(8)
        ]
        d["present"] = [
            {"prompt": f"p{i} ___ (ver)", "answer": [f"a{i}"]} for i in range(8)
        ]
        d["future"] = [
            {"prompt": f"p{i} ___ (ver)", "answer": [f"a{i}"]} for i in range(8)
        ]
        d["translation"] = [
            {"prompt": f"En {i}. (usar: infinitivo)", "answer": [f"a{i}"]}
            for i in range(8)
        ]
        self.assertTrue(validate_worksheet_blank_prompts(d))
        d["past"][0]["prompt"] = "a ___ b ___"
        self.assertFalse(validate_worksheet_blank_prompts(d))

    def test_validate_custom_exercises(self):
        self.assertTrue(validate_custom_exercises(_valid_custom_data()))

    def test_validate_custom_rejects_wrong_key_set(self):
        d = _valid_custom_data()
        d["past"] = []
        self.assertFalse(validate_custom_exercises(d))

    def test_validate_custom_rejects_wrong_count(self):
        d = _valid_custom_data()
        d["exercises"] = d["exercises"][:7]
        self.assertFalse(validate_custom_exercises(d))

    def test_validate_custom_rejects_string_answer_before_normalization(self):
        d = _valid_custom_data()
        d["exercises"][0]["answer"] = "hago"
        self.assertFalse(validate_custom_exercises(d))
        normalize_custom_exercise_answers(d)
        self.assertTrue(validate_custom_exercises(d))
        self.assertEqual(d["exercises"][0]["answer"], ["hago"])

    def test_validate_custom_blank_prompts(self):
        d = _valid_custom_data()
        self.assertTrue(validate_custom_blank_prompts(d))
        d["exercises"][0]["prompt"] = "Yo hago algo."
        self.assertFalse(validate_custom_blank_prompts(d))
        d["exercises"][0]["prompt"] = "Yo ___ (hacer) y ___ (decir)."
        self.assertFalse(validate_custom_blank_prompts(d))
