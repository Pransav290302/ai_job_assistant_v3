import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def parse_json_response(response_text: str) -> Dict[str, Any]:
    if not response_text or not response_text.strip():
        raise ValueError("Empty response text")

    text = response_text.strip()

    code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if code_block:
        text = code_block.group(1).strip()


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
