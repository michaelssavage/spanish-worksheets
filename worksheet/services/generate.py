from worksheet.models import Worksheet
from worksheet.services.prompts import build_payload
from django.conf import settings
import hashlib
from openai import OpenAI
import logging
import json
import re

from worksheet.services.topic_rotator import get_and_increment_topics
from worksheet.services.exercise_items import (
    validate_worksheet_blank_prompts,
    validate_worksheet_exercises,
)

logger = logging.getLogger(__name__)

MAX_BLANK_REGENERATION_ATTEMPTS = 3

BLANK_PROMPT_CORRECTION_USER = (
    "Some prompts had wrong blanks (missing ___, multiple ___, or ___ in "
    "translation). Fix strictly: each past/present/future prompt must "
    "contain exactly one '___'; translation prompts must contain none. "
    "Return the full worksheet JSON again with the same keys and shape."
)


def extract_json_from_response(content: str) -> str | None:
    """
    Attempt to extract a valid JSON object from an LLM response.
    Returns a JSON string if successful, otherwise None.
    """
    # 1. Try as-is
    try:
        json.loads(content)
        return content
    except json.JSONDecodeError:
        pass

    # 2. Markdown code block
    code_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(code_block_pattern, content, re.DOTALL)

    if match:
        extracted = match.group(1)
        try:
            json.loads(extracted)
            logger.info("Extracted valid JSON from markdown code block")
            return extracted
        except json.JSONDecodeError:
            pass

    # 3. Raw object fallback
    object_pattern = r"\{.*\}"
    match = re.search(object_pattern, content, re.DOTALL)

    if match:
        extracted = match.group(0)
        try:
            json.loads(extracted)
            logger.info("Extracted valid JSON object from raw response")
            return extracted
        except json.JSONDecodeError:
            pass

    logger.error("Failed to extract valid JSON from LLM response")
    return None


def call_llm(messages: list[dict]) -> str:
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content


def fix_json_structure_once(broken_content: str) -> str | None:
    """
    Ask the LLM once to fix JSON structure only.
    """
    logger.warning("Attempting one JSON structure repair")

    repair_prompt = [
        {
            "role": "system",
            "content": "You fix malformed JSON. You never change content.",
        },
        {
            "role": "user",
            "content": (
                "Fix the JSON structure only.\n"
                "Do not change, add, remove, or reorder any sentences.\n"
                "Return valid JSON only.\n\n"
                f"{broken_content}"
            ),
        },
    ]

    repaired = call_llm(repair_prompt)
    return extract_json_from_response(repaired)


def generate_worksheet_for(user, themes=None):
    logger.info(
        "Starting worksheet generation for user: %s (ID: %s)",
        user.email,
        user.id,
    )

    if themes is None:
        themes = get_and_increment_topics()
    messages = build_payload(themes)

    content: str | None = None

    for attempt in range(MAX_BLANK_REGENERATION_ATTEMPTS):
        logger.info(
            "Calling LLM to generate worksheet content (attempt %s)",
            attempt + 1,
        )
        raw_content = call_llm(messages)

        candidate = extract_json_from_response(raw_content)

        if candidate is None:
            candidate = fix_json_structure_once(raw_content)

        if candidate is None:
            logger.error(
                "Worksheet generation failed: JSON could not be repaired",
            )
            return None

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            logger.error("JSON invalid after repair attempt")
            return None

        if not validate_worksheet_exercises(parsed):
            logger.error(
                "Invalid worksheet structure. Expected four sections "
                "(past, present, future, translation), each with exactly 7 "
                'objects {"prompt": "...", "answer": "..."}.',
            )
            return None

        if validate_worksheet_blank_prompts(parsed):
            content = candidate
            break

        logger.warning(
            "Worksheet blank validation failed (attempt %s/%s)",
            attempt + 1,
            MAX_BLANK_REGENERATION_ATTEMPTS,
        )
        if attempt + 1 >= MAX_BLANK_REGENERATION_ATTEMPTS:
            logger.error(
                "Worksheet blank validation failed after all attempts",
            )
            return None

        messages = messages + [
            {"role": "assistant", "content": candidate},
            {"role": "user", "content": BLANK_PROMPT_CORRECTION_USER},
        ]

    if content is None:
        return None

    h = hashlib.sha256(content.encode("utf-8")).hexdigest()

    if Worksheet.objects.filter(content_hash=h).exists():
        logger.warning("Duplicate worksheet detected, aborting save")
        return None

    Worksheet.objects.filter(user=user).delete()
    Worksheet.objects.create(
        user=user,
        content_hash=h,
        content=content,
        topics=["past", "present", "future", "translation"],
        themes=themes,
    )

    logger.info("Worksheet saved successfully for user: %s", user.email)
    return content
