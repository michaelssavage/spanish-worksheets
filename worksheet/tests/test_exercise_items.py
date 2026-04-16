from django.test import TestCase

from worksheet.services.exercise_items import (
    exercise_prompt_for_display,
    has_exactly_one_blank,
    parse_worksheet_content,
    validate_worksheet_blank_prompts,
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

    def test_has_exactly_one_blank(self):
        self.assertTrue(has_exactly_one_blank("Foo ___ (hacer) bar"))
        self.assertFalse(has_exactly_one_blank("No blank here"))
        self.assertFalse(has_exactly_one_blank("Two ___ (a) ___ (b)"))

    def test_validate_worksheet_blank_prompts(self):
        d = _valid_data()
        self.assertFalse(validate_worksheet_blank_prompts(d))
        d["past"] = [
            {"prompt": f"p{i} ___ (ver)", "answer": f"a{i}"} for i in range(7)
        ]
        d["present"] = [
            {"prompt": f"p{i} ___ (ver)", "answer": f"a{i}"} for i in range(7)
        ]
        d["future"] = [
            {"prompt": f"p{i} ___ (ver)", "answer": f"a{i}"} for i in range(7)
        ]
        d["translation"] = [
            {"prompt": f"En {i}. (usar: infinitivo)", "answer": f"a{i}"}
            for i in range(7)
        ]
        self.assertTrue(validate_worksheet_blank_prompts(d))
        d["past"][0]["prompt"] = "a ___ b ___"
        self.assertFalse(validate_worksheet_blank_prompts(d))
