"""Cockpit test set: every question in questions.json must come back with the expected
status, contain the expected words, and cite at least the expected records."""
import json
import unittest
from pathlib import Path

from cockpit.answer import ask
from cockpit.load import build
from cockpit.worry import worries

CASES = json.loads((Path(__file__).parent / "questions.json").read_text())


def setUpModule():
    build()


class Questions(unittest.TestCase):
    def test_questions(self):
        for case in CASES:
            with self.subTest(q=case["q"], as_of=case["as_of"]):
                a = ask(case["q"], case["as_of"])
                self.assertEqual(a.status, case["status"], a.text)
                for word in case["contains"]:
                    self.assertIn(word, a.text)
                for rid in case["cites"]:
                    self.assertIn(rid, a.cites)

    def test_enough_honesty_cases(self):
        self.assertGreaterEqual(sum(c["status"] in ("unknown", "disagree", "refused") for c in CASES), 5)


class Worries(unittest.TestCase):
    def test_nothing_before_release(self):
        self.assertEqual(worries("2026-11-15"), [])

    def test_day1_top_worry_is_atlas(self):
        top = worries("2026-11-16")[0]
        self.assertIn("Atlas", top.title)
        self.assertIn("BOARD-JULSEP", top.cites)

    def test_hotel_is_not_a_duplicate_vendor(self):
        titles = " ".join(w.title for w in worries("2026-11-16"))
        self.assertIn("Saphire Event Mgmt", titles)
        self.assertNotIn("Sapphire Residency Hotel", titles)

    def test_payroll_worry_shows_no_amounts(self):
        w = next(w for w in worries("2026-11-16") if "payroll" in w.title)
        self.assertNotIn("Rs.", w.title + w.why)


if __name__ == "__main__":
    unittest.main()
