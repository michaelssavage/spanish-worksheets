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


def extract_json_from_response(content):
    """
    Extract JSON from LLM response that might be wrapped in markdown code blocks.
    """
    # First, try to parse as-is
    try:
        json.loads(content)
        return content
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    # Match ```json ... ``` or ``` ... ```
    json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(json_pattern, content, re.DOTALL)

    if match:
        extracted = match.group(1)
        logger.info("Extracted JSON from markdown code block")
        return extracted

    json_obj_pattern = r"\{.*?\}"
    match = re.search(json_obj_pattern, content, re.DOTALL)

    if match:
        extracted = match.group(0)
        try:
            json.loads(extracted)
            logger.info("Extracted JSON object from response")
            return extracted
        except json.JSONDecodeError:
            pass

    logger.warning("Could not extract valid JSON from LLM response")
    return content


def call_llm(predictions_payload):
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
    )

    logger.info("Sending request to DeepSeek API")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=predictions_payload,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    logger.info(f"Received response from LLM (length: {len(content)} chars)")

    content = extract_json_from_response(content)

    return content


def generate_worksheet_for(user):
    logger.info(f"Starting worksheet generation for user: {user.email} (ID: {user.id})")

    themes = get_and_increment_topics()
    logger.info(f"Selected themes: {themes}")

    payload = build_payload(themes)

    logger.info("Calling LLM to generate worksheet content")
    content = call_llm(payload)

    h = hashlib.sha256(content.encode("utf-8")).hexdigest()
    logger.debug(f"Content hash: {h[:16]}...")

    if Worksheet.objects.filter(content_hash=h).exists():
        logger.warning(
            f"Duplicate worksheet detected (hash: {h[:16]}...), returning None"
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
    logger.info(f"Worksheet saved successfully for user: {user.email}")

    return content
