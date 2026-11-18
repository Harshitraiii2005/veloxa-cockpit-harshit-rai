"""The 14 agents: complete, logged, grounded in records, time-gated, and holding their boundaries."""
import re
import unittest

from cockpit.agents import PERSONAS, interview, roster
from cockpit.db import ROOT
from cockpit.load import build


def setUpModule():
    build()


class Agents(unittest.TestCase):
    def test_fourteen_agents_match_keka(self):
        ids = {eid for eid, _, _ in roster("2026-11-17")}
        self.assertEqual(len(ids), 14)
        self.assertEqual(ids, set(PERSONAS))

    def test_every_persona_is_logged_as_an_assumption(self):
        logged = set(re.findall(r"\| (A-\d+) \|", (ROOT / "ASSUMPTIONS.md").read_text()))
        for eid, persona in PERSONAS.items():
            self.assertIn(persona["assumption"], logged, eid)

    def test_facts_are_cited_and_time_gated(self):
        a = interview("Fatima", "Tell me about your leave", "2026-11-17")
        self.assertIn("LEAVE:2026-02-09", a.cites)
        self.assertIn("wedding", a.text)
        before = interview("Fatima", "Tell me about your leave", "2026-11-16")   # leave register is Day 2
        self.assertEqual(before.status, "unknown")
        self.assertNotIn("15 days", before.text)

    def test_work_answer_uses_records(self):
        a = interview("Vikram", "What's your week like?", "2026-11-17")
        self.assertIn("HIRE:REQ-014", a.cites)
        self.assertIn("A-104", a.cites)

    def test_boundaries(self):
        self.assertEqual(interview("Meera", "What's your salary?", "2026-11-17").status, "refused")
        self.assertEqual(interview("Priya", "Are you planning to quit?", "2026-11-17").status, "refused")
        sid = interview("Siddharth", "Are you leaving the company?", "2026-11-17")
        self.assertEqual(sid.status, "answered")
        self.assertIn("KEKA:VX013", sid.cites)

    def test_a_reported_resignation_changes_the_answer_from_its_release(self):
        before = interview("Priya", "Are you planning to quit?", "2026-11-18")
        after = interview("Priya", "Are you planning to quit?", "2026-11-19")
        self.assertEqual(before.status, "refused")
        self.assertEqual(after.status, "answered")
        self.assertIn("T6d:#2", after.cites)

    def test_only_the_fourteen_and_only_after_release(self):
        self.assertEqual(interview("Manoj", "How is sales?", "2026-11-17").status, "unknown")
        self.assertEqual(interview("Priya", "What are you working on?", "2026-11-15").status, "unknown")


if __name__ == "__main__":
    unittest.main()
