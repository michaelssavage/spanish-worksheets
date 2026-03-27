"""Worksheet exercise items: prompt (learner-facing) and answer (solution)."""

from __future__ import annotations

import json
from typing import Any

REQUIRED_SECTION_KEYS = frozenset({"past", "present", "future", "translation"})
ITEMS_PER_SECTION = 7


def exercise_prompt_for_display(item: Any) -> str:
    """Text shown to the learner (email, HTML). Supports legacy string-only items."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        p = item.get("prompt")
        if isinstance(p, str) and p.strip():
            return p
    return ""


def validate_worksheet_exercises(data: dict[str, Any]) -> bool:
    """True if each section has seven objects with non-empty prompt and answer strings."""
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
