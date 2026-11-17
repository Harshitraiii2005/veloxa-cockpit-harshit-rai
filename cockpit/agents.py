"""The 14 people as agents you can interview (D-005). Each answer is built fresh from:
  (a) facts computed from records visible at as_of, cited by record ID, and
  (b) an invented persona in curation/people.json, cited by its assumption ID (ASSUMPTIONS.md).
There is no free-running memory, so an agent can't drift away from the records."""
import json
import re
from collections import Counter

from .answer import Answer, day, find_person, rows
from .db import ROOT, connect

PERSONAS = json.loads((ROOT / "curation" / "people.json").read_text())
FOURTEEN = ("Engineering", "Finance", "People & Ops", "Marketing")   # A-002

TOPICS = [  # first match wins
    ("pay", r"salar|\bctc\b|\bearn|payslip amount|how much .*paid|\bpay\b"),
    ("quit", r"\bquit|resign|leav(e|ing) (veloxa|the company)|job.?hunt|looking (for|around)|interview(ing)? elsewhere"),
    ("leave", r"\bleave\b|time off|holiday|vacation|days off"),
    ("life", r"\blife\b|family|home|weekend|outside work|hobb|personal|married|kids|where do you live"),
    ("mood", r"how are you|feel|worr|stress|happy|enjoy|morale|tired"),
    ("work", r"work|busy|week|doing|project|focus|atlas|\bjob\b|\brole\b|who are you|what do you do"),
]


def interview(who, question, as_of=None):
    conn = connect(as_of)
    people = {r["Emp ID"]: (rid, r) for rid, r in rows(conn, "KEKA")}
    eid = find_person(conn, who)
    if eid not in people or people[eid][1]["Department"] not in FOURTEEN:
        return Answer(f"I don't have an agent for \"{who}\" in the records released so far. The 14 are the "
                      f"Engineering, Finance, People & Ops and Marketing staff in Keka.", "unknown", "n/a")
    rid, p = people[eid]
    persona = PERSONAS[eid]
    topic = next((t for t, pattern in TOPICS if re.search(pattern, question, re.I)), None)

    if topic == "pay":
        return Answer("I'm not going to talk about anyone's pay, mine included. Finance shares totals only (T2:#6).",
                      "refused", "n/a", ["T2:#6"])
    if topic == "quit":
        if p.get("Exit Date"):
            letters = [r["id"] for r in conn.execute(
                "SELECT id FROM v_record WHERE kind = 'document' AND text LIKE ?", (f"%{p['Full Name']}%resignation%",))]
            return Answer(f"Yes. I resigned, and my last day is {day(p['Exit Date'])}.", "answered", "High", [rid] + letters)
        return Answer("That's not something I'd discuss here. If something were wrong, I'd raise it with my manager first.",
                      "refused", "n/a")
    if topic == "leave":
        return leave_answer(conn, eid, persona)
    if topic in ("life", "mood"):
        return Answer(persona[topic], "answered", "Low", [persona["assumption"]])
    if topic == "work":
        boss = people.get(p["Manager ID"], (None, {"Full Name": "nobody"}))[1]["Full Name"]
        text = (f"I'm {p['Full Name']}, {p['Title']}, here since {day(p['Join Date'])}, reporting to {boss}. "
                f"{persona['work']}")
        cites = [rid, persona["assumption"]]
        for sentence, refs in work_facts(conn, eid, p, people):
            text += " " + sentence
            cites += refs
        return Answer(text, "answered", "Medium", cites)
    return Answer("I'd rather not guess at that. Ask me about my work, my week, my leave, or how things are.",
                  "unknown", "n/a")


def leave_answer(conn, eid, persona):
    alias = dict(conn.execute("SELECT alias, entity_id FROM v_alias").fetchall())
    leave = [(lid, r) for lid, r in rows(conn, "LEAVE") if alias.get(r["Employee"].lower()) == eid]
    if not leave:
        return Answer("There's no leave on record for me in what's been released so far.", "unknown", "n/a")
    text = "From the leave register: " + "; ".join(
        f"{r['Leave Type'].lower()}, {day(r['From'])}" + (f" to {day(r['To'])}" if r["To"] != r["From"] else "")
        + f" ({r['Days']:g} day{'s' if r['Days'] != 1 else ''})" for _, r in leave) + ". " + persona["leave_note"]
    return Answer(text, "answered", "Medium", [lid for lid, _ in leave] + [persona["assumption"]])


def work_facts(conn, eid, p, people):
    """Grounded sentences about this person's work, each with the records behind it."""
    reports = [(r_id, q) for r_id, q in people.values() if q["Manager ID"] == eid]
    if reports:
        yield f"{len(reports)} people report to me: {', '.join(q['Full Name'] for _, q in reports)}.", [r for r, _ in reports]
    reqs = [(hid, h) for hid, h in rows(conn, "HIRE") if h["Hiring Manager"] == eid]
    if reqs:
        yield ("I'm the hiring manager on " + "; ".join(f"{h['Req ID']} {h['Role']} ({h['Status'].lower()})" for _, h in reqs)
               + "."), [hid for hid, _ in reqs]
    mail = p["Work Email"]
    for e in conn.execute("SELECT id, data, occurred_at FROM v_record WHERE kind = 'email' ORDER BY occurred_at"):
        d = json.loads(e["data"])
        if mail in d["From"]:
            to = d["To"].split("<")[0].strip()
            yield f"On {day(e['occurred_at'])} I emailed {to}: \"{d['Subject']}\".", [e["id"]]
    # Who processed payroll / entered the GL is recorded by initials (FS, KS); use them only if unique.
    initials = Counter("".join(w[0] for w in q["Full Name"].split()) for _, q in people.values())
    mine = "".join(w[0] for w in p["Full Name"].split())
    if initials[mine] == 1:
        processed = [r_id for r_id, r in rows(conn, "PAYROLL") if r.get("Processed By") == mine]
        months = sorted({r["Month"] for _, r in rows(conn, "PAYROLL") if r.get("Processed By") == mine})
        if processed:
            yield f"I processed payroll for {', '.join(months)}.", ["PAYROLL:title", processed[0]]
        entered = [r_id for r_id, r in rows(conn, "GL") if r.get("Entered By") == mine]
        if entered:
            yield f"I entered all {len(entered)} lines in the Apr-Sep ledger export.", ["GL:title"]


def roster(as_of=None):
    conn = connect(as_of)
    return [(p["Emp ID"], p["Full Name"], p["Title"]) for _, p in rows(conn, "KEKA") if p["Department"] in FOURTEEN]
