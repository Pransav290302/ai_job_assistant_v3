"""
Data validation for the AI Job Assistant (Senior Data Scientist todo).
Validate and normalize ResumeScoreOutput from LLM.
"""

import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {"skills", "experience", "keywords"}
VALID_PRIORITIES = {"high", "medium", "low"}


def _normalize_suggestion(item: Union[Dict[str, str], str]) -> Dict[str, str]:
    """Convert a suggestion to {category, suggestion, priority}."""
    if isinstance(item, str):
        return {
            "category": "keywords",
            "suggestion": item,
            "priority": "medium",
        }
    return {
        "category": str(item.get("category", "keywords")).lower()
        if str(item.get("category", "keywords")).lower() in VALID_CATEGORIES
        else "keywords",
        "suggestion": str(item.get("suggestion", "")),
        "priority": str(item.get("priority", "medium")).lower()
        if str(item.get("priority", "medium")).lower() in VALID_PRIORITIES
        else "medium",
    }


def validate_resume_score(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize LLM output to ResumeScoreOutput schema.
    Accepts legacy format (suggestions as list of strings) and converts to
    {category, suggestion, priority} format.

    Args:
        raw: Parsed JSON from LLM (may have score, suggestions, strengths, etc.).

    Returns:
        Normalized dict with score, match_percentage, suggestions (structured),
        matched_keywords, missing_keywords; optional strengths, missing_skills.
    """
    score = raw.get("score")
    if score is None:
        score = int(float(raw.get("match_percentage", 0) * 100)
                   if isinstance(raw.get("match_percentage"), (int, float))
                   else 0)
    else:
        score = int(score) if isinstance(score, (int, float)) else 0
    score = max(0, min(100, score))

    match_percentage = raw.get("match_percentage")
    if match_percentage is None:
        match_percentage = score / 100.0
    else:
        match_percentage = float(match_percentage)
    match_percentage = max(0.0, min(1.0, match_percentage))

    suggestions_raw = raw.get("suggestions", [])
    if not isinstance(suggestions_raw, list):
        suggestions_raw = [str(suggestions_raw)] if suggestions_raw else []
    suggestions = [_normalize_suggestion(s) for s in suggestions_raw]

    matched_keywords = raw.get("matched_keywords", [])
    if not isinstance(matched_keywords, list):
        matched_keywords = [str(matched_keywords)] if matched_keywords else []
    matched_keywords = [str(k) for k in matched_keywords]

    missing_keywords = raw.get("missing_keywords", raw.get("missing_skills", []))
    if not isinstance(missing_keywords, list):
        missing_keywords = [str(missing_keywords)] if missing_keywords else []
    missing_keywords = [str(k) for k in missing_keywords]

    result: Dict[str, Any] = {
        "score": score,
        "match_percentage": match_percentage,
        "suggestions": suggestions,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }

    # Backward compatibility: keep strengths and missing_skills if present
    if "strengths" in raw and isinstance(raw["strengths"], list):
        result["strengths"] = [str(s) for s in raw["strengths"]]
    if "missing_skills" in raw and isinstance(raw["missing_skills"], list):
        result["missing_skills"] = [str(s) for s in raw["missing_skills"]]

    return result
