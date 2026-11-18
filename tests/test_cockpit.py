"""Cockpit test set: every question in questions.json must come back with the expected
status, contain the expected words, cite at least the expected records, and not contain
any "absent" words (facts released after its as_of date)."""
import json
import unittest
from pathlib import Path

from cockpit.answer import ask
from cockpit.load import build
from cockpit.worry import Worry, top, worries

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
                for word in case.get("absent", []):      # later material must not leak into earlier answers
                    self.assertNotIn(word, a.text)

    def test_brief_minimums(self):
        self.assertGreaterEqual(len(CASES), 25)
        self.assertGreaterEqual(sum(c["status"] in ("unknown", "disagree", "refused") for c in CASES), 5)


class Worries(unittest.TestCase):
    def test_nothing_before_release(self):
        self.assertEqual(worries("2026-11-15"), [])

    def test_day1_top_worry_is_atlas(self):
        first = worries("2026-11-16")[0]
        self.assertIn("Atlas", first.title)
        self.assertIn("BOARD-JULSEP", first.cites)

    def test_hotel_is_not_a_duplicate_vendor(self):
        titles = " ".join(w.title for w in worries("2026-11-16"))
        self.assertIn("Saphire Event Mgmt", titles)
        self.assertNotIn("Sapphire Residency Hotel", titles)

    def test_t6a_opens_on_top_three(self):
        items = worries("2026-11-17")
        self.assertGreater(len(items), 3)
        self.assertEqual(top(items), items[:3])

    def test_t6a_never_cuts_a_five_or_pads(self):
        fives = [Worry(5, f"w{i}", "", "High", []) for i in range(4)]
        self.assertEqual(len(top(fives)), 4)
        self.assertEqual(len(top(fives[:1])), 1)

    def test_t6d_resignation_is_a_top_worry_on_19_nov_only(self):
        titles = [w.title for w in top(worries("2026-11-19"))]
        self.assertTrue(any("Priya Nair has resigned" in t for t in titles))
        self.assertFalse(any("resigned" in w.title for w in worries("2026-11-18")))

    def test_payroll_worry_shows_no_amounts(self):
        w = next(w for w in worries("2026-11-16") if "payroll" in w.title)
        self.assertNotIn("Rs.", w.title + w.why)


if __name__ == "__main__":
    unittest.main()
