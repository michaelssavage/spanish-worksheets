"""Worksheet exercise items: prompt (learner-facing) and answer (solution)."""

from __future__ import annotations

import json
from typing import Any

REQUIRED_SECTION_KEYS = frozenset({"past", "present", "future", "translation"})
CONJUGATION_SECTION_KEYS = frozenset({"past", "present", "future"})
ITEMS_PER_SECTION = 7
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


def validate_worksheet_exercises(data: dict[str, Any]) -> bool:
    """True if each section has seven objects with prompt and answer set."""
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
            if not isinstance(answer, str) or not answer.strip():
                return False
    return True


def validate_worksheet_blank_prompts(data: dict[str, Any]) -> bool:
    """
    True if past/present/future each have exactly one ___ and translation
    has none. Call only after validate_worksheet_exercises passes.
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
    trans = data.get("translation")
    if not isinstance(trans, list):
        return False
    for item in trans:
        if not isinstance(item, dict):
            return False
        prompt = item.get("prompt")
        if not isinstance(prompt, str) or BLANK_MARKER in prompt:
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
