"""
Unit tests for parsers (parse_json_response).
"""

import unittest
from model.parsers import parse_json_response


class TestParseJsonResponse(unittest.TestCase):
    def test_plain_json(self):
        text = '{"score": 85, "suggestions": []}'
        out = parse_json_response(text)
        self.assertEqual(out["score"], 85)
        self.assertEqual(out["suggestions"], [])

    def test_json_with_leading_trailing_text(self):
        text = 'Here is the result:\n{"score": 70, "match_percentage": 0.7}\nDone.'
        out = parse_json_response(text)
        self.assertEqual(out["score"], 70)
        self.assertEqual(out["match_percentage"], 0.7)

    def test_markdown_code_block(self):
        text = '```json\n{"score": 90, "matched_keywords": ["Python"]}\n```'
        out = parse_json_response(text)
        self.assertEqual(out["score"], 90)
        self.assertEqual(out["matched_keywords"], ["Python"])

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            parse_json_response("")
        with self.assertRaises(ValueError):
            parse_json_response("   ")

    def test_no_json_object_raises(self):
        with self.assertRaises(ValueError):
            parse_json_response("No JSON here")

    def test_invalid_json_raises(self):
        with self.assertRaises(ValueError):
            parse_json_response("{score: 80}")  # unquoted key
