"""Loader + point-in-time gate. Run: python -m unittest discover tests -v"""
import unittest

from cockpit.db import connect
from cockpit.load import build


def setUpModule():
    build()


def days_visible(as_of):
    return {r[0][:10] for r in connect(as_of).execute("SELECT DISTINCT released_at FROM v_record")}


class PointInTime(unittest.TestCase):
    def test_nothing_known_before_first_release(self):
        self.assertEqual(days_visible("2026-11-16T09:59"), set())

    def test_release_boundaries(self):
        self.assertEqual(days_visible("2026-11-16T10:00"), {"2026-11-16"})
        self.assertEqual(days_visible("2026-11-17"), {"2026-11-16", "2026-11-17"})  # date = end of day IST
        self.assertEqual(len(days_visible("2026-11-20")), 4)

    def test_entities_follow_their_evidence(self):
        self.assertEqual(connect("2026-11-15").execute("SELECT COUNT(*) FROM v_entity").fetchone()[0], 0)
        self.assertEqual(connect("2026-11-16").execute("SELECT COUNT(*) FROM v_entity WHERE kind='person'").fetchone()[0], 19)

    def test_payroll_is_restricted(self):
        rows = connect("2026-11-16").execute("SELECT DISTINCT source_id FROM v_record WHERE restricted = 1").fetchall()
        self.assertEqual([r[0] for r in rows], ["PAYROLL"])


if __name__ == "__main__":
    unittest.main()
