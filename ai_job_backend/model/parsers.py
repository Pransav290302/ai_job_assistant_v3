"""
Output parsing utilities for the AI Job Assistant (Senior Data Scientist todo).
Extract and normalize JSON from LLM responses.
"""

import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Extract a JSON object from LLM response text.
    Handles markdown code blocks and trailing/leading text.

    Args:
        response_text: Raw LLM response (may contain ```json ... ``` or plain JSON).

    Returns:
        Parsed dict.

    Raises:
        ValueError: If no valid JSON object found.
    """
    if not response_text or not response_text.strip():
        raise ValueError("Empty response text")

    text = response_text.strip()

    # Try to extract from markdown code block
    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if code_block:
        text = code_block.group(1).strip()

    # Find first { ... } (greedy to last })
    json_match = re.search(r"\{[\s\S]*\}", text)
    if not json_match:
        raise ValueError("No JSON object found in response")

    raw = json_match.group(0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}. Attempting to fix common issues.")
        fixed = re.sub(r",\s*}", "}", raw)
        fixed = re.sub(r",\s*]", "]", fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON: {e}") from e
