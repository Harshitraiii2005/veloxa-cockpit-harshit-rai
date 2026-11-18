"""'What should I worry about': plain rules over the as_of views. Each rule returns zero or
more Worry items backed by record IDs; a rule with no evidence on that date returns nothing.
Severity (1-5) is my judgement of business impact; ranking is severity, then confidence."""
from collections import Counter
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from itertools import combinations

from .answer import (atlas, commits, day, display, duty_facts, inr, jira_points, marketing_spend, metric,
                     name_to_id, rows, visible)
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


def atlas_slipped(conn):
    a = atlas(conn, "")
    if a.status == "unknown" and a.cites:
        # TN-07: a claim I judged a different measure (the customer promise) is worth showing next to the GA plan.
        for c in conn.execute("""SELECT c.* FROM v_claim c JOIN v_verdict v ON v.claim_id = c.id
                                 WHERE c.metric = 'atlas_ga' AND v.verdict = 'different-measure'"""):
            a.text += f" Separately, {c['record_id']} says v3 was {c['quote']} (TN-07)."
            a.cites.append(c["record_id"])
        yield Worry(5, "Atlas (routing engine v3) has slipped and there is no new GA date on record", a.text, "High", a.cites)
        return
    planned = conn.execute("SELECT value FROM v_claim WHERE metric = 'atlas_ga' AND value != '' AND as_at != '' ORDER BY as_at").fetchall()
    if a.status != "unknown" and len(planned) > 1 and planned[-1]["value"] > planned[0]["value"]:
        yield Worry(5, f"Atlas GA has slipped from {day(planned[0]['value'])} to {day(planned[-1]['value'])}", a.text, "High", a.cites)


def key_person_load(conn):
    """One person holding 40% or more of the open Atlas work. Work patterns only; no guessing at intentions (D-006)."""
    pts = jira_points(conn)
    total = sum(d["open"] for d in pts.values())
    epic_names = {rid.split(":")[1]: r["Epic Name"] for rid, r in rows(conn, "JIRA") if "Epic Name" in r}
    for eid, d in pts.items():
        if not total or d["open"] / total < 0.4:
            continue
        name = display(conn, eid)
        why = (f"{d['open']} of {total} open story points, across {len(d['epics'])} epics: "
               + ", ".join(epic_names.get(e, e) for e in sorted(d["epics"])) + " (JIRA:title).")
        cites = ["JIRA:title"] + d["open_ids"][:3]
        n, late_after, late_before, ids, _ = commits(conn, eid)
        if late_after:
            why += f" Since June, {late_after} of {name}'s commits were made between 22:00 and 05:00 IST, against {late_before} before June."
            cites += [ids[0], ids[-1]]
        mail = conn.execute("SELECT alias FROM v_alias WHERE entity_id = ? AND alias LIKE '%@veloxa.in'", (eid,)).fetchone()
        for e in conn.execute("SELECT id, text, occurred_at FROM v_record WHERE kind = 'email' AND text LIKE ?",
                              (f"From: %{mail['alias'] if mail else '@@'}%",)):
            why += f" {e['id']} ({e['occurred_at'][11:16]} IST): \"{' '.join(e['text'].split(chr(10) * 2, 1)[-1].split())}\""
            cites.append(e["id"])
        if visible(conn, "T5:#3"):
            why += " Vikram says nobody is overloaded (T5:#3); I set that aside (TN-26)."
            cites.append("T5:#3")
        yield Worry(4, f"{name} holds {round(100 * d['open'] / total)}% of the open Atlas work", why, "Medium", cites)


def on_call_load(conn):
    """Someone on the on-call rota in 90% or more of weeks."""
    rota, alias = rows(conn, "ONCALL"), name_to_id(conn)
    counts = Counter(alias.get(n.lower(), n) for _, r in rota for n in {r["Primary"], r["Secondary"]})
    pts = jira_points(conn)
    for eid, n in counts.items():
        if n / len(rota) < 0.9:
            continue
        name, why, cites = display(conn, eid), [], []
        for sentence, refs in duty_facts(conn, eid):
            why.append(sentence)
            cites += refs
        if eid in pts:
            why.append(f"Their Atlas tickets: {pts[eid]['open']} points open, {pts[eid]['done']} done (JIRA:title).")
            cites.append("JIRA:title")
        for e in conn.execute("SELECT id FROM v_record WHERE kind = 'email' AND text LIKE '%SEV1%pausing%'"):
            why.append(f"{e['id']}: Atlas performance work paused to stabilise routing-api.")
            cites.append(e["id"])
        yield Worry(3, f"{name} has been on call in {n} of {len(rota)} weeks", " ".join(why), "High", cites)


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


def backend_hiring_paused(conn):
    """Hiring the board said would de-risk Atlas is paused, after money was spent on it."""
    fees = [(rid, r) for rid, r in rows(conn, "GL") if r["Cost Centre"] == "PPL-HIR"]
    held = [(rid, r) for rid, r in rows(conn, "HIRE") if r["Status"] == "On hold"]
    paused = [r["id"] for r in conn.execute(
        "SELECT id FROM v_record WHERE kind IN ('document', 'email') AND (text LIKE '%hiring is paused%' OR text LIKE '%pausing req%')")]
    if not paused or not (fees or held):
        return
    why = []
    if held:
        why.append(", ".join(f"{r['Req ID']} {r['Role']}" for _, r in held) + f" on hold since {day(held[0][1]['Status Date'])} "
                   f"with {sum(r['In pipeline'] for _, r in held)} candidates in the pipeline")
    why += [f"{inr(r['Amount (Rs.)'])} paid to {r['Vendor / Payee']} on {day(r['Txn Date'])} ({r['Narration']})" for _, r in fees]
    why.append(f"paused per {', '.join(paused)}")
    board = [rid for rid in ("BOARD-APRJUN",) if visible(conn, rid)]   # "two backend engineers ... to de-risk Atlas"
    yield Worry(4, "Backend hiring meant to de-risk Atlas is on hold, after a recruiter advance was paid",
                "; ".join(why) + ".", "High" if held else "Medium", [rid for rid, _ in held + fees] + paused + board)


def engagement_drop(conn):
    """A team whose pulse score fell by 0.4 or more quarter on quarter."""
    by_team = {}
    for rid, r in rows(conn, "PULSE"):
        by_team.setdefault(r["Team"], []).append((rid, r))
    for team, hist in by_team.items():
        (prid, prev), (lrid, last) = hist[-2], hist[-1]
        drop = round(prev["Engagement (1-5)"] - last["Engagement (1-5)"], 2)   # round: 3.8 - 3.4 is 0.3999...
        if drop >= 0.4:
            yield Worry(4 if drop >= 0.6 else 3,
                        f"{team} engagement fell from {prev['Engagement (1-5)']:g} to {last['Engagement (1-5)']:g} in {last['Quarter']}",
                        f"{last['Responses']} of {last['Team size']} responded. Comments are hidden because the team is smaller "
                        f"than 6 (PULSE:title), so the score is all there is.", "Medium", [lrid, prid, "PULSE:title"])


def departures(conn):
    """Someone with an exit date, and whether a backfill exists."""
    for rid, p in rows(conn, "KEKA"):
        if not p.get("Exit Date"):
            continue
        backfill = [(hid, h) for hid, h in rows(conn, "HIRE")
                    if h["Team"] == p["Department"] and "backfill" in (h.get("Notes") or "").lower()]
        letters = [r["id"] for r in conn.execute(
            "SELECT id FROM v_record WHERE kind = 'document' AND text LIKE ?", (f"%{p['Full Name']}%resignation%",))]
        why = (f"{backfill[0][1]['Req ID']} backfill opened {day(backfill[0][1]['Opened'])}, {backfill[0][1]['In pipeline']} in the pipeline."
               if backfill else "No backfill req is on record.")
        # Documents that name them as owner ("Owner: Sid."), using every name they go by.
        names = [a["alias"] for a in conn.execute("SELECT alias FROM v_alias WHERE entity_id = ? AND alias NOT LIKE '%@%'", (p["Emp ID"],))]
        owned = [r["id"] for r in conn.execute("SELECT id, text FROM v_record WHERE kind = 'document'")
                 if any(f"owner: {n}" in r["text"].lower() for n in names)]
        if owned:
            why += f" They own {', '.join(owned)}, which is still waiting on an engineering date."
        yield Worry(3 if owned else 2, f"{p['Full Name']} ({p['Title']}, {p['Department']}) is leaving: exit date {day(p['Exit Date'])}",
                    why, "High", [rid] + letters + [hid for hid, _ in backfill] + owned)


def numbers_disagree(conn):
    hits = [(label, metric(conn, m, label)) for m, label in
            [("arr", "ARR"), ("burn_monthly", "monthly burn"), ("team", "team size")]]
    hits += [("marketing spend", marketing_spend(conn, ""))]
    hits = [(label, a) for label, a in hits if a.status == "disagree"]
    if hits:
        yield Worry(2, "Leaders' figures don't match the records: " + ", ".join(l for l, _ in hits),
                    "What leaders said on calls doesn't match the board updates or the ledger. Ask me about "
                    + ", ".join(l for l, _ in hits) + " to see the figures side by side.", "High", [c for _, a in hits for c in a.cites])


RULES = [atlas_slipped, key_person_load, backend_hiring_paused, engagement_drop, on_call_load, joiner_paid_full_month,
         lookalike_vendors, departures, numbers_disagree]


def top(items, n=3):
    """T6a: open on the top n. Any 5/5 still shows even past n, and the list is never padded."""
    return [w for i, w in enumerate(items) if i < n or w.severity == 5]


def worries(as_of=None):
    conn = connect(as_of)
    items = [w for rule in RULES for w in rule(conn)]
    return sorted(items, key=lambda w: (-w.severity, RANK[w.confidence]))
