"""T6b: reporting lines are effective-dated data, and moving people around doesn't break anything."""
import unittest

from cockpit.agents import interview, roster, work_facts
from cockpit.answer import ask, manager_of, rows
from cockpit.db import connect
from cockpit.load import build


def setUpModule():
    build()


def people(conn):
    return {r["Emp ID"]: (rid, r) for rid, r in rows(conn, "KEKA")}


class ReportingLines(unittest.TestCase):
    def test_announced_change_has_no_date_and_changes_nothing(self):
        a = ask("Who is Nikhil?", "2026-11-18")
        self.assertIn("reporting to Ananya Rao", a.text)
        self.assertIn("no date set yet", a.text)
        self.assertIn("T6b:#2", a.cites)
        self.assertNotIn("Announced", ask("Who is Nikhil?", "2026-11-17").text)   # T6b not released yet

    def test_a_dated_move_applies_from_its_date(self):
        for as_of, expected in (("2026-11-30", "Vikram Menon"), ("2026-12-01", "Priya Nair")):
            conn = connect(as_of)
            conn.execute("INSERT INTO org_change VALUES ('VX018', 'VX007', '2026-12-01', 'T6b:#2', 'test only')")
            self.assertEqual(manager_of(conn, "VX018", people(conn))[0], expected)
            conn.rollback()

    def test_moving_someone_updates_reports_and_keeps_all_fourteen(self):
        conn = connect("2026-12-01")
        conn.execute("INSERT INTO org_change VALUES ('VX018', 'VX007', '2026-11-20', 'T6b:#2', 'test only')")
        ppl = people(conn)
        priya = " ".join(s for s, _ in work_facts(conn, "VX007", ppl["VX007"][1], ppl))
        vikram = " ".join(s for s, _ in work_facts(conn, "VX004", ppl["VX004"][1], ppl))
        conn.rollback()
        self.assertIn("1 person reports to me: Rahul Verma", priya)
        self.assertNotIn("Rahul Verma", vikram)
        self.assertEqual(len(roster("2026-12-01")), 14)
        self.assertEqual(interview("Nikhil", "what do you do?", "2026-11-18").status, "answered")


if __name__ == "__main__":
    unittest.main()
