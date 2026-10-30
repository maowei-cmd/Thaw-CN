#!/usr/bin/env python3
"""Unit tests for xcstrings_zh.py. Run: python3 -m unittest scripts/localization/test_xcstrings_zh.py"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import xcstrings_zh as tool


class SerializerTests(unittest.TestCase):
    def test_round_trip_matches_xcode_format(self):
        data = {
            "sourceLanguage": "en",
            "strings": {
                "Close": {
                    "comment": "A button",
                    "localizations": {"en": {"stringUnit": {"state": "translated", "value": "Close"}}},
                },
                "Empty": {},
            },
            "version": "1.1",
        }
        text = tool.dump_catalog(data)
        self.assertIn('"sourceLanguage" : "en"', text)
        self.assertIn('"Empty" : {\n\n    }', text)
        self.assertEqual(json.loads(text), data)

    def test_unicode_is_not_escaped(self):
        text = tool.dump_catalog({"strings": {"Close": {"localizations": {"zh-Hans": {"stringUnit": {"value": "关闭"}}}}}})
        self.assertIn("关闭", text)
        self.assertNotIn("\\u", text)


class PlaceholderTests(unittest.TestCase):
    def test_positional_placeholders_match_non_positional(self):
        self.assertEqual(tool.check_placeholders("%@ %@", "%1$@ %2$@"), [])

    def test_length_modifier_must_match(self):
        self.assertEqual(tool.check_placeholders("%lld items", "%lld 个项目"), [])
        self.assertNotEqual(tool.check_placeholders("%lld items", "%d items"), [])

    def test_literal_percent_is_ignored(self):
        self.assertEqual(tool.check_placeholders("Zoom: %lld%%", "缩放：%lld%%"), [])

    def test_positional_indices_must_be_contiguous(self):
        self.assertNotEqual(tool.check_placeholders("%@ %@", "%2$@ %3$@"), [])

    def test_missing_placeholder_is_reported(self):
        self.assertNotEqual(tool.check_placeholders("%@ and %lld more", "还有更多"), [])


class MarkdownTests(unittest.TestCase):
    def test_bold_and_link_urls_must_survive(self):
        key = "**Note:** see [the docs](https://example.com/a)."
        value = "**注意：** 参见[文档](https://example.com/a)。"
        self.assertEqual(tool.check_markdown(key, value), [])

    def test_changed_url_is_reported(self):
        self.assertNotEqual(
            tool.check_markdown("[docs](https://example.com/a)", "[文档](https://example.com/b)"),
            [],
        )


class InflectTests(unittest.TestCase):
    def test_translation_must_drop_inflect_annotation(self):
        key = "^[%lld items](inflect: true)"
        self.assertEqual(tool.check_inflect(key, "%lld 个项目"), [])
        self.assertNotEqual(tool.check_inflect(key, "^[%lld items](inflect: true)"), [])


class EntryTests(unittest.TestCase):
    def test_set_and_read_string_unit(self):
        entry = {}
        tool.set_zh_value(entry, "关闭", "translated")
        self.assertEqual(tool.zh_value(entry), ("关闭", "translated"))

    def test_set_and_read_plural(self):
        entry = {"localizations": {"en": {"variations": {"plural": {"one": {"stringUnit": {"value": "%lld item"}}}}}}}
        tool.set_zh_value(entry, "%lld 个项目", "translated")
        self.assertEqual(tool.zh_value(entry), ("%lld 个项目", "translated"))
        self.assertEqual(set(entry["localizations"]["zh-Hans"]["variations"]["plural"]), {"other"})


class CatalogValidationTests(unittest.TestCase):
    def test_clean_catalog_passes(self):
        data = {
            "sourceLanguage": "en",
            "strings": {
                "Close": {"localizations": {"zh-Hans": {"stringUnit": {"state": "translated", "value": "关闭"}}}},
            },
            "version": "1.1",
        }
        path = Path("/tmp/xcstrings-zh-test-catalog.json")
        path.write_text(tool.dump_catalog(data), encoding="utf-8")
        self.assertEqual(tool.main(["validate", "--catalog", str(path), "--strict"]), 0)

    def test_english_leftover_fails(self):
        data = {
            "sourceLanguage": "en",
            "strings": {
                "Close": {"localizations": {"zh-Hans": {"stringUnit": {"state": "new", "value": "Close"}}}},
            },
            "version": "1.1",
        }
        path = Path("/tmp/xcstrings-zh-test-catalog-bad.json")
        path.write_text(tool.dump_catalog(data), encoding="utf-8")
        self.assertEqual(tool.main(["validate", "--catalog", str(path), "--strict"]), 1)


if __name__ == "__main__":
    unittest.main()
