"""'What should I worry about': plain rules over the as_of views. Each rule returns zero or
more Worry items backed by record IDs; a rule with no evidence on that date returns nothing.
Severity (1-5) is my judgement of business impact; ranking is severity, then confidence."""
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from itertools import combinations

from .answer import day, inr, metric, rows
from .db import connect

RANK = {"High": 0, "Medium": 1, "Low": 2}


@dataclass
class Worry:
    severity: int
    title: str
    why: str
    confidence: str
    cites: list

    def __str__(self):
        return f"[{self.severity}/5, {self.confidence}] {self.title}\n    {self.why}\n    Sources: {', '.join(dict.fromkeys(self.cites))}"


def atlas_date_unknown(conn):
    a = metric(conn, "atlas_ga", "Atlas GA date")
    if a.status == "unknown" and a.cites:
        yield Worry(5, "Atlas (routing engine v3) has slipped and there is no new GA date on record", a.text, "High", a.cites)


def joiner_paid_full_month(conn):
    """A payroll row that pays every day of a month the person joined part-way through. Never shows amounts."""
    joined = {p["Emp ID"]: (rid, p) for rid, p in rows(conn, "KEKA")}
    for rid, r in rows(conn, "PAYROLL"):
        keka_id, p = joined.get(r["Emp ID"], (None, None))
        if not p:
            continue
        start = date.fromisoformat(p["Join Date"][:10])
        if f"{start:%b-%Y}" == r["Month"] and start.day > 1 and r["Days Payable"] == r["Days in Month"]:
            emails = [e["id"] for e in conn.execute(
                "SELECT id FROM v_record WHERE kind = 'email' AND (text LIKE '%payroll%' OR text LIKE '%payslip%')")]
            yield Worry(3, f"{r['Month']} payroll may have paid {r['Name']} for the whole month after joining on {day(p['Join Date'])}",
                        f"The register shows {r['Days Payable']} of {r['Days in Month']} days payable, but Keka has a join date of "
                        f"{day(p['Join Date'])}. Related emails: {', '.join(emails) or 'none'}. No record shows it was corrected.",
                        "Medium", [rid, keka_id] + emails)


def lookalike_vendors(conn):
    """Two different payee names in the same cost centre whose first words nearly match (Sapphire / Saphire).
    Different cost centres are skipped on purpose: a hotel and an events firm can share a word."""
    by_cc = {}
    for rid, r in rows(conn, "GL"):
        by_cc.setdefault(r["Cost Centre"], []).append((rid, r))
    for cc, lines in by_cc.items():
        for (ra, a), (rb, b) in combinations(lines, 2):
            na, nb = a["Vendor / Payee"], b["Vendor / Payee"]
            if na != nb and SequenceMatcher(None, na.split()[0].lower(), nb.split()[0].lower()).ratio() >= 0.85:
                yield Worry(3, f"Possible duplicate vendor in {cc}: \"{na}\" and \"{nb}\"",
                            f"{inr(a['Amount (Rs.)'])} on {day(a['Txn Date'])} ({a['Narration']}, ref {a['Ref']}) and "
                            f"{inr(b['Amount (Rs.)'])} on {day(b['Txn Date'])} ({b['Narration']}, ref {b['Ref']}). "
                            f"It may be one vendor under two names, or two separate bills for one event.",
                            "Medium", [ra, rb])


def paid_for_paused_hiring(conn):
    fees = [(rid, r) for rid, r in rows(conn, "GL") if r["Cost Centre"] == "PPL-HIR"]
    paused = [r["id"] for r in conn.execute(
        "SELECT id FROM v_record WHERE kind IN ('document', 'email') AND (text LIKE '%hiring is paused%' OR text LIKE '%pausing req%')")]
    for rid, r in fees if paused else []:
        yield Worry(3, "A recruiter advance was paid for hiring that is now paused",
                    f"{inr(r['Amount (Rs.)'])} paid to {r['Vendor / Payee']} on {day(r['Txn Date'])} ({r['Narration']}), "
                    f"but {', '.join(paused)} {'says' if len(paused) == 1 else 'say'} hiring is paused.", "Medium", [rid] + paused)


def numbers_disagree(conn):
    hits = [(label, metric(conn, m, label)) for m, label in
            [("arr", "ARR"), ("burn_monthly", "monthly burn"), ("team", "team size")]]
    hits = [(label, a) for label, a in hits if a.status == "disagree"]
    if hits:
        yield Worry(2, "Leadership quotes numbers that don't match the board updates: " + ", ".join(l for l, _ in hits),
                    "Board updates and what leaders said on calls give different figures. Ask me about "
                    + ", ".join(l for l, _ in hits) + " to see the quotes side by side.", "High", [c for _, a in hits for c in a.cites])


RULES = [atlas_date_unknown, joiner_paid_full_month, lookalike_vendors, paid_for_paused_hiring, numbers_disagree]


def worries(as_of=None):
    conn = connect(as_of)
    items = [w for rule in RULES for w in rule(conn)]
    return sorted(items, key=lambda w: (-w.severity, RANK[w.confidence]))
