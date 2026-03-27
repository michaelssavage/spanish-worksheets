from django.test import TestCase

from worksheet.services.exercise_items import (
    exercise_prompt_for_display,
    parse_worksheet_content,
    validate_worksheet_exercises,
)


def _valid_data():
    sec = [{"prompt": f"p{i}", "answer": f"a{i}"} for i in range(7)]
    return {
        "past": sec,
        "present": sec,
        "future": sec,
        "translation": sec,
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

    def test_parse_content(self):
        import json

        data = _valid_data()
        raw = json.dumps(data)
        self.assertEqual(parse_worksheet_content(raw), data)
        self.assertEqual(parse_worksheet_content(data), data)
