"""
Unit tests for validators (validate_resume_score).
"""

import unittest
from model.validators import validate_resume_score


class TestValidateResumeScore(unittest.TestCase):
    def test_full_structure(self):
        raw = {
            "score": 85,
            "match_percentage": 0.85,
            "suggestions": [
                {"category": "skills", "suggestion": "Add React", "priority": "high"},
                {"category": "experience", "suggestion": "Quantify impact", "priority": "medium"},
            ],
            "matched_keywords": ["Python", "SQL"],
            "missing_keywords": ["Docker"],
        }
        out = validate_resume_score(raw)
        self.assertEqual(out["score"], 85)
        self.assertEqual(out["match_percentage"], 0.85)
        self.assertEqual(len(out["suggestions"]), 2)
        self.assertEqual(out["suggestions"][0]["category"], "skills")
        self.assertEqual(out["suggestions"][0]["priority"], "high")
        self.assertEqual(out["matched_keywords"], ["Python", "SQL"])
        self.assertEqual(out["missing_keywords"], ["Docker"])

    def test_legacy_string_suggestions(self):
        raw = {
            "score": 70,
            "suggestions": ["Add more keywords", "Quantify achievements"],
            "matched_keywords": [],
            "missing_keywords": [],
        }
        out = validate_resume_score(raw)
        self.assertEqual(out["score"], 70)
        self.assertEqual(len(out["suggestions"]), 2)
        self.assertEqual(out["suggestions"][0]["category"], "keywords")
        self.assertEqual(out["suggestions"][0]["suggestion"], "Add more keywords")
        self.assertEqual(out["suggestions"][0]["priority"], "medium")

    def test_missing_fields_defaulted(self):
        raw = {}
        out = validate_resume_score(raw)
        self.assertEqual(out["score"], 0)
        self.assertEqual(out["match_percentage"], 0.0)
        self.assertEqual(out["suggestions"], [])
        self.assertEqual(out["matched_keywords"], [])
        self.assertEqual(out["missing_keywords"], [])

    def test_score_clamped(self):
        out = validate_resume_score({"score": 150, "match_percentage": 2.0})
        self.assertEqual(out["score"], 100)
        self.assertEqual(out["match_percentage"], 1.0)

    def test_strengths_and_missing_skills_preserved(self):
        raw = {
            "score": 80,
            "suggestions": [],
            "matched_keywords": [],
            "missing_keywords": [],
            "strengths": ["Strong Python"],
            "missing_skills": ["Kubernetes"],
        }
        out = validate_resume_score(raw)
        self.assertEqual(out["strengths"], ["Strong Python"])
        self.assertEqual(out["missing_skills"], ["Kubernetes"])
