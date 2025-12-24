from worksheet.models import Worksheet
from worksheet.services.prompts import build_payload
from django.conf import settings
import hashlib
from openai import OpenAI
import logging
import json
import re

from worksheet.services.topic_rotator import get_and_increment_topics

logger = logging.getLogger(__name__)


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

    # 2. Try fenced code blocks ```json ... ``` or ``` ... ```
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

    # 3. Last resort: first JSON-looking object
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


def call_llm(predictions_payload: list[dict]) -> str | None:
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )

    logger.info("Sending request to DeepSeek API")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=predictions_payload,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    logger.info("Received response from LLM (%d chars)", len(content))

    return extract_json_from_response(content)


def generate_worksheet_for(user):
    logger.info(
        "Starting worksheet generation for user: %s (ID: %s)",
        user.email,
        user.id,
    )

    themes = get_and_increment_topics()
    logger.info("Selected themes: %s", themes)

    payload = build_payload(themes)

    logger.info("Calling LLM to generate worksheet content")
    content = call_llm(payload)

    if content is None:
        logger.error("Worksheet generation failed: no valid JSON returned")
        return None

    # Hard validation gate
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        logger.error("Extracted content is not valid JSON after extraction")
        return None

    required_keys = {"past", "present", "future", "vocab"}
    if set(parsed.keys()) != required_keys:
        logger.error(
            "Invalid worksheet structure. Expected keys %s, got %s",
            required_keys,
            set(parsed.keys()),
        )
        return None

    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    logger.debug("Content hash: %s...", h[:16])

    if Worksheet.objects.filter(content_hash=h).exists():
        logger.warning(
            "Duplicate worksheet detected (hash: %s...), aborting save",
            h[:16],
        )
        return None

    logger.info("Saving new worksheet to database (replacing prior user worksheet)")
    Worksheet.objects.filter(user=user).delete()
    Worksheet.objects.create(
        user=user,
        content_hash=h,
        content=content,
        topics=["past", "present", "future", "vocab"],
    )

    logger.info("Worksheet saved successfully for user: %s", user.email)
    return content