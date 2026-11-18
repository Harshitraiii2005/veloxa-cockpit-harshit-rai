"""Stretch: the projection after 31 Oct is repeatable, consistent with the records, and never evidence."""
import unittest

from cockpit.answer import ask
from cockpit.load import build
from cockpit.simulate import simulate


def setUpModule():
    build()


class Simulation(unittest.TestCase):
    def setUp(self):
        self.events = simulate("2026-11-18")

    def test_repeatable_and_starts_after_the_export(self):
        self.assertEqual(self.events, simulate("2026-11-18"))
        self.assertTrue(all(d.isoformat() >= "2026-11-01" for d, *_ in self.events))
        self.assertTrue(all(d.isoformat() <= "2026-11-18" for d, *_ in self.events))

    def test_consistent_with_the_records(self):
        who = {eid for _, eid, _, _ in self.events}
        self.assertNotIn("VX013", who)                                    # Siddharth left on 31 Oct
        late = {eid for _, eid, what, _ in self.events if "after 22:00" in what}
        self.assertEqual(late, {"VX007"})                                 # only Priya has a late-night basis
        rota = [(d, eid, what) for d, eid, what, _ in self.events if "on call" in what]
        primaries = [eid for _, eid, what in rota if "primary" in what]
        self.assertEqual(set(primaries), {"VX012", "EXT-SPATIL"})         # the weekly swap continues
        self.assertNotEqual(primaries[0], primaries[1])

    def test_never_shows_payroll_amounts_or_leaks_into_answers(self):
        pay = [what for _, _, what, _ in simulate("2026-11-30") if "PAYROLL" in what]   # payroll lands on the 28th
        self.assertTrue(pay and all("Rs." not in w for w in pay))
        self.assertTrue(all("Simulated" not in c for c in ask("Is engineering overloaded?", "2026-11-18").cites))

    def test_nothing_to_project_before_the_engineering_data(self):
        self.assertFalse([e for e in simulate("2026-11-17") if "commit" in e[2]])


if __name__ == "__main__":
    unittest.main()
