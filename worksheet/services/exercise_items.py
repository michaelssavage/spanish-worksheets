"""Worksheet exercise items: prompt (learner-facing) and answer (list of solutions)."""

from __future__ import annotations

import json
from typing import Any

REQUIRED_SECTION_KEYS = frozenset({"past", "present", "future", "subjunctive"})
CONJUGATION_SECTION_KEYS = REQUIRED_SECTION_KEYS
CUSTOM_EXERCISES_KEY = "exercises"
ITEMS_PER_SECTION = 8
BLANK_MARKER = "___"


def has_exactly_one_blank(prompt: str) -> bool:
    """True if the prompt has exactly one triple-underscore blank (___)."""
    if not isinstance(prompt, str):
        return False
    return prompt.count(BLANK_MARKER) == 1


def exercise_prompt_for_display(item: Any) -> str:
    """Learner-facing text (email, HTML). Supports legacy string-only items."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        p = item.get("prompt")
        if isinstance(p, str) and p.strip():
            return p
    return ""


def normalize_worksheet_answers(data: dict[str, Any]) -> None:
    """Coerce string answer fields to single-element lists (LLM slip tolerance)."""
    for key in REQUIRED_SECTION_KEYS:
        section = data.get(key)
        if not isinstance(section, list):
            continue
        for item in section:
            if not isinstance(item, dict):
                continue
            ans = item.get("answer")
            if isinstance(ans, str) and ans.strip():
                item["answer"] = [ans.strip()]


def normalize_custom_exercise_answers(data: dict[str, Any]) -> None:
    """Coerce custom string answer fields to single-element lists."""
    exercises = data.get(CUSTOM_EXERCISES_KEY)
    if not isinstance(exercises, list):
        return
    for item in exercises:
        if not isinstance(item, dict):
            continue
        ans = item.get("answer")
        if isinstance(ans, str) and ans.strip():
            item["answer"] = [ans.strip()]


def validate_custom_exercises(data: dict[str, Any]) -> bool:
    """True if custom output has exactly eight prompt/list-answer exercises."""
    if set(data.keys()) != {CUSTOM_EXERCISES_KEY}:
        return False
    exercises = data[CUSTOM_EXERCISES_KEY]
    if not isinstance(exercises, list) or len(exercises) != ITEMS_PER_SECTION:
        return False
    for item in exercises:
        if not isinstance(item, dict):
            return False
        prompt = item.get("prompt")
        answer = item.get("answer")
        if not isinstance(prompt, str) or not prompt.strip():
            return False
        if not isinstance(answer, list) or len(answer) < 1:
            return False
        if not all(isinstance(s, str) and s.strip() for s in answer):
            return False
    return True


def validate_custom_blank_prompts(data: dict[str, Any]) -> bool:
    """
    True if every custom exercise has exactly one ___. Call only after
    validate_custom_exercises passes.
    """
    exercises = data.get(CUSTOM_EXERCISES_KEY)
    if not isinstance(exercises, list):
        return False
    for item in exercises:
        if not isinstance(item, dict):
            return False
        if not has_exactly_one_blank(item.get("prompt")):
            return False
    return True


def validate_worksheet_exercises(data: dict[str, Any]) -> bool:
    """True if each section has eight objects with prompt and list-of-string answers."""
    if set(data.keys()) != REQUIRED_SECTION_KEYS:
        return False
    for key in REQUIRED_SECTION_KEYS:
        section = data[key]
        if not isinstance(section, list) or len(section) != ITEMS_PER_SECTION:
            return False
        for item in section:
            if not isinstance(item, dict):
                return False
            prompt = item.get("prompt")
            answer = item.get("answer")
            if not isinstance(prompt, str) or not prompt.strip():
                return False
            if not isinstance(answer, list) or len(answer) < 1:
                return False
            if not all(isinstance(s, str) and s.strip() for s in answer):
                return False
    return True


def validate_worksheet_blank_prompts(data: dict[str, Any]) -> bool:
    """
    True if every worksheet section prompt has exactly one ___. Call only after
    validate_worksheet_exercises passes.
    """
    for key in CONJUGATION_SECTION_KEYS:
        section = data.get(key)
        if not isinstance(section, list):
            return False
        for item in section:
            if not isinstance(item, dict):
                return False
            prompt = item.get("prompt")
            if not has_exactly_one_blank(prompt):
                return False
    return True


def parse_worksheet_content(
    content: str | dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Parse stored worksheet JSON into a dict, or None if invalid."""
    if content is None:
        return None
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None
