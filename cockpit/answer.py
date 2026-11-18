"""Question -> Answer. Deterministic (D-002): each topic handler reads only the as_of views
and returns the records it used. No matching handler, or no evidence -> "I don't know"."""
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from .db import TIER, connect

EXPORT_DATE = "2026-10-31"  # A-005: every export is a 31 Oct snapshot
CONF = {"export": "High", "document": "High", "email": "Medium", "brief": "Medium",
        "transcript": "Low", "voice_note": "Low"}
LOWER = {"High": "Medium", "Medium": "Low", "Low": "Low", "n/a": "n/a"}
UNIT = {"Cr": 1e7, "L": 1e5}


@dataclass
class Answer:
    text: str
    status: str                 # answered | unknown | disagree | refused
    confidence: str             # High | Medium | Low | n/a
    cites: list = field(default_factory=list)

    def __str__(self):
        return (f"{self.text}\nConfidence: {self.confidence} | Status: {self.status}\n"
                f"Sources: {', '.join(dict.fromkeys(self.cites)) or 'none'}")


# ---------- small helpers ----------

def rows(conn, source_id):
    """(record_id, row dict) for every data row of one export visible at as_of."""
    return [(r["id"], json.loads(r["data"])) for r in conn.execute(
        "SELECT id, data FROM v_record WHERE source_id = ? AND data IS NOT NULL ORDER BY seq", (source_id,))]


def visible(conn, rid):
    return conn.execute("SELECT 1 FROM v_record WHERE id = ?", (rid,)).fetchone() is not None


def day(iso):
    if not iso:
        return "undated"
    d = date.fromisoformat(iso[:10])
    return f"{d.day} {d:%b %Y}"


def month(iso):
    return f"{date.fromisoformat(iso[:10]):%b %Y}"


def inr(x):
    return f"Rs. {x / 1e7:.2f} Cr" if x >= 1e7 else f"Rs. {x / 1e5:.2f} L"


def amount(c):
    """A claim's value in comparable form: rupees, a number, an ISO date, or None if unusable."""
    if not c["value"] or c["unit"] == "?":
        return None
    if c["unit"] == "date":
        return c["value"]
    return float(c["value"]) * UNIT.get(c["unit"], 1)


def show(c):
    if c["unit"] in UNIT:
        return f"Rs. {c['value']} {c['unit']}"
    if c["unit"] == "date":
        return day(c["value"])
    if c["unit"] == "?":
        return f"\"{c['value']}\" (unit not stated)"
    return f"{c['value']} {c['unit']}" if c["unit"] == "months" else c["value"]


def disagrees(c, best):
    a, b = amount(c), amount(best)
    if c["as_at"] and best["as_at"] and c["as_at"] != best["as_at"] and (a is not None or not c["value"]):
        return False                    # a value for another date is a trend; a dated "no value" is superseded
    if a is None or b is None:
        return (a is None) != (b is None)
    if isinstance(a, str) or isinstance(b, str):
        return a != b
    return abs(a - b) > 0.1 * abs(b)    # within 10% counts as the same number


def manager_of(conn, eid, people):
    """(manager name, note) as at as_of. A dated org change overrides Keka from its effective date;
    an undated one is shown as announced and changes nothing (T6b)."""
    p = people[eid][1]
    name = people.get(p["Manager ID"], (None, {"Full Name": "nobody (top of the org)"}))[1]["Full Name"]
    cut = conn.execute("SELECT t FROM asof").fetchone()[0]
    note, cites = "", []
    for ch in conn.execute("SELECT * FROM v_org_change WHERE emp_id = ? ORDER BY effective_from", (eid,)):
        new = people.get(ch["new_manager"], (None, {"Full Name": ch["new_manager"]}))[1]["Full Name"]
        if ch["effective_from"] and ch["effective_from"] <= cut[:10]:
            name, note = new, f" (changed on {day(ch['effective_from'])}, {ch['record_id']})"
        elif not ch["effective_from"]:
            note = f" Announced: will report to {new}, no date set yet ({ch['record_id']})."
        else:
            note = f" Will report to {new} from {day(ch['effective_from'])} ({ch['record_id']})."
        cites.append(ch["record_id"])
    return name, note, cites


def resignations(conn):
    """Emp ID -> facts about a resignation reported after the Keka export (A-016): date, notice, quotes, records."""
    out = {}
    for c in conn.execute("SELECT * FROM v_claim WHERE metric LIKE 'resigned:%' OR metric LIKE 'notice:%'"):
        kind, eid = c["metric"].split(":")
        d = out.setdefault(eid, {"date": None, "notice": None, "notice_quote": None, "cites": []})
        if kind == "resigned":
            d["date"], d["quote"] = c["value"], c["quote"]
        else:
            d["notice"], d["notice_quote"] = int(c["value"]), c["quote"]
        d["cites"].append(c["record_id"])
    return {e: d for e, d in out.items() if d["date"]}


def resignation_note(r):
    text = f" Reported to have resigned on {day(r['date'])} ({r['cites'][0]}, a CEO voice note; not in the 31 Oct Keka export)."
    if r["notice"]:
        last = date.fromisoformat(r["date"]) + timedelta(days=round(30.4 * r["notice"]))
        text += (f" Notice: \"{r['notice_quote']}\", unconfirmed; if two months, the last day is around "
                 f"{day(last.isoformat())}.")
    return text


def find_person(conn, q):
    """Entity ID of the longest alias that appears in the question as a whole word."""
    ql = q.lower()
    hits = [(a["alias"], a["entity_id"]) for a in conn.execute("SELECT alias, entity_id FROM v_alias")
            if re.search(rf"\b{re.escape(a['alias'])}\b", ql)]
    return max(hits, key=lambda h: len(h[0]))[1] if hits else None


# ---------- metrics stated by several sources ----------

def metric(conn, name, label, extra=()):
    claims = [dict(r) for r in conn.execute("SELECT * FROM v_claim WHERE metric = ?", (name,))] + list(extra)
    if not claims:
        return Answer(f"I don't know the {label}: no record released so far states it.", "unknown", "n/a")
    dated = sorted((c for c in claims if c["as_at"]), key=lambda c: (c["as_at"], -TIER[c["kind"]]))
    best = dated[-1] if dated else min(claims, key=lambda c: TIER[c["kind"]])
    verdicts = {v["claim_id"]: v for v in conn.execute("SELECT * FROM v_verdict")}
    against = [c for c in claims if c is not best and disagrees(c, best)]
    # "cannot-settle" is a decided verdict that the records can't resolve: it stays a disagreement, labelled as such.
    still_open = [c for c in against if verdicts.get(c["id"], {"verdict": "cannot-settle"})["verdict"] == "cannot-settle"]
    set_aside = [c for c in against if c not in still_open]
    earlier = [c for c in dated if c is not best and c not in against and c["value"]]

    if best["value"]:
        text = f"The {label} is {show(best)} as at {day(best['as_at'])} ({best['record_id']})."
        status, conf = "answered", CONF[best["kind"]]
    else:
        text = (f"I don't know the current {label}. The latest record ({best['record_id']}, "
                f"{day(best['as_at'])}) says \"{best['quote']}\" but gives no {'new date' if best['unit'] == 'date' else 'value'}.")
        status, conf = "unknown", "n/a"
    if earlier:
        when = "stated" if best["unit"] == "date" else "as at"
        text += " Earlier: " + "; ".join(f"{show(c)} {when} {day(c['as_at'])} ({c['record_id']})" for c in earlier) + "."
    if set_aside:
        text += " Set aside: " + "; ".join(
            f"{c['record_id']} \"{c['quote']}\" ({verdicts[c['id']]['verdict']}, see {verdicts[c['id']]['reason']})"
            for c in set_aside) + "."
    if still_open:
        settled = [verdicts[c["id"]]["reason"] for c in still_open if c["id"] in verdicts]
        text += (" The sources disagree: " + "; ".join(f"{c['record_id']} says \"{c['quote']}\"" for c in still_open)
                 + (f". The records can't settle this (see {', '.join(settled)})." if settled else ". I haven't resolved this yet."))
        status, conf = ("disagree", LOWER[conf]) if status == "answered" else (status, conf)
    cites = [best["record_id"]] + [c["record_id"] for c in earlier + set_aside + still_open]
    return Answer(text, status, conf, cites)


def headcount(conn, q):
    people = rows(conn, "KEKA")
    if not people:
        return metric(conn, "team", "team size")
    keka = {"id": "KEKA", "metric": "team", "value": str(len(people)), "unit": "count", "as_at": EXPORT_DATE,
            "record_id": "KEKA:title", "quote": f"{len(people)} employee rows", "kind": "export"}
    a = metric(conn, "team", "team size (employees in Keka)", [keka])
    a.text += " Keka lists employees only; contractors are not in it (KEKA:title)."
    for e in conn.execute("SELECT * FROM v_entity WHERE kind = 'contractor'"):
        a.text += f" Known contractor outside Keka: {e['name']} ({e['record_id']})."
        a.cites.append(e["record_id"])
    for rid, p in people:
        if p.get("Exit Date"):
            a.text += f" {p['Full Name']} is on {p['Status'].lower()} with exit date {day(p['Exit Date'])} ({rid})."
            a.cites.append(rid)
    return a


# ---------- topics read straight from exports ----------

INDIVIDUAL = r"\b(each|every|everyone|individual|per person|by person|list|ceo|cfo|vp|head|manager|engineer)\b"


def pay(conn, q):
    if "total" not in q.lower() and (find_person(conn, q) or re.search(INDIVIDUAL, q, re.I)):
        return Answer("I can't share an individual's pay. Finance's rule is that only totals reach the CEO "
                      "(T2:#6). I can give you total payroll.", "refused", "n/a", ["T2:#6"])
    pay_rows = [(rid, r) for rid, r in rows(conn, "GL") if r["Cost Centre"] == "PAYROLL"]
    if not pay_rows:
        return Answer("I don't know total payroll: no payroll totals have been released.", "unknown", "n/a")
    (first_id, first), (last_id, last) = pay_rows[0], pay_rows[-1]
    text = f"Total salaries were {inr(last['Amount (Rs.)'])} for {month(last['Txn Date'])} ({last_id})."
    if len({r["Amount (Rs.)"] for _, r in pay_rows}) == 1:
        text += f" The same amount was booked every month since {month(first['Txn Date'])} ({first_id})."
    return Answer(text, "answered", "High", [last_id, first_id])


def marketing_spend(conn, q):
    mkt = [(rid, r) for rid, r in rows(conn, "GL") if r["Cost Centre"].startswith("MKT")]
    if not mkt:
        return Answer("I don't know marketing spend: no ledger lines for marketing have been released.", "unknown", "n/a")
    by_cc = {}
    for _, r in mkt:
        by_cc[r["Cost Centre"]] = by_cc.get(r["Cost Centre"], 0) + r["Amount (Rs.)"]
    total = sum(by_cc.values())
    gl = {"id": "GL", "metric": "marketing_spend_half", "value": f"{total / 1e5:.2f}", "unit": "L", "as_at": "2026-09-30",
          "record_id": "GL:title", "quote": "GL marketing lines", "kind": "export"}
    a = metric(conn, "marketing_spend_half", "marketing spend in the ledger for Apr-Sep 2026", [gl])
    a.text += (" By cost centre: " + ", ".join(f"{cc} {inr(v)}" for cc, v in sorted(by_cc.items())) +
               ". The GL export covers selected cost centres only (GL:title), so the real total may be higher.")
    a.confidence = "Medium" if a.status == "answered" else "Low"
    a.cites += [rid for rid, _ in mkt]
    return a


def person(conn, q):
    eid = find_person(conn, q)
    if not eid:
        name = (re.search(r"\bwho(?: is|'s)\s+([\w .'-]+?)\??$", q, re.I) or [None, "that person"])[1]
        return Answer(f"I don't know who {name} is. No released record names them. Keka lists employees "
                      f"only; contractors are not in it (KEKA:title).", "unknown", "n/a", ["KEKA:title"])
    if eid.startswith("EXT-"):
        e = conn.execute("SELECT * FROM v_entity WHERE id = ?", (eid,)).fetchone()
        text = f"{e['name']} is a {e['kind']}, not an employee, so not in Keka (KEKA:title, {e['record_id']})."
        cites = ["KEKA:title", e["record_id"]]
        for sentence, refs in duty_facts(conn, eid):
            text += " " + sentence
            cites += refs
        return Answer(text, "answered", "High", cites)
    people = {r["Emp ID"]: (rid, r) for rid, r in rows(conn, "KEKA")}
    rid, p = people[eid]
    boss, note, org_cites = manager_of(conn, eid, people)
    text = (f"{p['Full Name']} ({eid}) is {p['Title']} in {p['Department']}, reporting to {boss}"
            f"{note if note.startswith(' (') else ''}. "
            f"Joined {day(p['Join Date'])}, based in {p['Location']}, status: {p['Status']}."
            f"{note if not note.startswith(' (') else ''}")
    if p.get("Exit Date"):
        text += f" Exit date {day(p['Exit Date'])}."
    if eid in (res := resignations(conn)):
        text += resignation_note(res[eid])
        org_cites = org_cites + res[eid]["cites"]
    alias = dict(conn.execute("SELECT alias, entity_id FROM v_alias").fetchall())
    leave = [(lrid, r) for lrid, r in rows(conn, "LEAVE") if alias.get(r["Employee"].lower()) == eid]
    if leave:
        kinds = Counter(r["Leave Type"] for _, r in leave)
        n = sum(r["Days"] for _, r in leave)
        text += (f" Leave register (Nov 2025 to Oct 2026): {n:g} day{'' if n == 1 else 's'}, "
                 + ", ".join(f"{n} x {k.lower()}" for k, n in kinds.items()) + ".")
    return Answer(text, "answered", "High", [rid] + org_cites + [lrid for lrid, _ in leave])


# ---------- Day 2: people data ----------

def hiring(conn, q):
    reqs = rows(conn, "HIRE")
    if not reqs:
        return Answer("I don't know the hiring status: the hiring tracker hasn't been released yet.", "unknown", "n/a")
    live = [(rid, r) for rid, r in reqs if r["Status"] in ("Open", "On hold")]
    text = f"Hiring tracker as at {day(EXPORT_DATE)} (HIRE:title): " + "; ".join(
        f"{r['Req ID']} {r['Role']} ({r['Team']}) {r['Status'].lower()} since {day(r['Status Date'])}, "
        f"{r['In pipeline']} in pipeline" + (f" ({r['Notes']})" if r.get("Notes") else "") for _, r in live
    ) + f". The other {len(reqs) - len(live)} reqs are filled or closed."
    cites = ["HIRE:title"] + [rid for rid, _ in live]
    for e in conn.execute("SELECT id, text FROM v_record WHERE kind = 'email' AND text LIKE '%pausing req%'"):
        body = e["text"].split("\n\n", 1)[-1]        # skip the From/To/Subject header line
        text += f" {e['id']}: \"{re.search(r'Pausing[^.]*\.', body)[0]}\""
        cites.append(e["id"])
    # T3 claims a number of open roles in April; compare with what the tracker shows for April.
    april = [rid for rid, r in reqs if r["Opened"] <= "2026-04-30" and
             (r["Status"] in ("Open", "On hold") or r["Status Date"] >= "2026-04-01")]
    tracker = {"id": "HIRE", "metric": "open_roles", "value": str(len(april)), "unit": "count", "as_at": "2026-04-30",
               "record_id": "HIRE:title", "quote": f"{len(april)} reqs open during April", "kind": "export"}
    april_answer = metric(conn, "open_roles", "number of reqs open during April 2026", [tracker])
    if len(april_answer.cites) > 1:
        text += " " + april_answer.text
        cites += april_answer.cites + april
    status = "disagree" if april_answer.status == "disagree" else "answered"
    return Answer(text, status, "High" if status == "answered" else "Medium", cites)


TEAMS = ("Engineering", "Finance", "People & Ops", "Marketing", "Sales", "Support")


def pulse(conn, q):
    data = rows(conn, "PULSE")
    if not data:
        return Answer("I don't know: no pulse survey results have been released yet.", "unknown", "n/a")
    if re.search(r"comment", q, re.I):
        # TN-17: Deepa's call (wants you to see comments) overrides her 29 Sep email; the export still has none.
        return Answer("I don't have survey comments. The export is team level only and hides comments for teams "
                      "smaller than 6, which is every team here (PULSE:title). Deepa has said she wants you to see "
                      "them (T3:#3), so ask her for them directly. I won't try to reconstruct them from scores.",
                      "unknown", "n/a", ["PULSE:title", "T3:#3"])
    by_team = {}
    for rid, r in data:
        by_team.setdefault(r["Team"], []).append((rid, r))
    asked = [t for t in TEAMS if t.lower() in q.lower()] or list(by_team)
    lines, cites = [], ["PULSE:title"]
    for t in asked:
        (prid, prev), (lrid, last) = by_team[t][-2], by_team[t][-1]
        change = round(last["Engagement (1-5)"] - prev["Engagement (1-5)"], 1)
        lines.append(f"{t} {last['Engagement (1-5)']:g} in {last['Quarter']} ({change:+g} from {prev['Engagement (1-5)']:g}, "
                     f"{last['Responses']} of {last['Team size']} responded, {lrid})")
        cites += [lrid, prid]
    return Answer("Engagement on a 1-5 scale, latest quarter: " + "; ".join(lines) + ".", "answered", "High", cites)


def attrition(conn, q):
    text = ("I don't know the attrition rate. The Keka export lists current employees only, so people who "
            "already left aren't in it (KEKA:title).")
    cites = ["KEKA:title"]
    for c in conn.execute("SELECT * FROM v_claim WHERE metric = 'attrition'"):
        text += f" {c['record_id']} says \"{c['quote']}\" with no unit, so I can't check it."
        cites.append(c["record_id"])
    names = {p["Emp ID"]: p["Full Name"] for _, p in rows(conn, "KEKA")}
    for rid, p in rows(conn, "KEKA"):
        if p.get("Exit Date"):
            text += f" Known departure: {p['Full Name']}, exit date {day(p['Exit Date'])} ({rid})."
            cites.append(rid)
    for eid, r in resignations(conn).items():
        text += f" Reported resignation: {names.get(eid, eid)}.{resignation_note(r)}"
        cites += r["cites"]
    return Answer(text, "unknown", "n/a", cites)


def unnamed_engineer(conn, q):
    if not visible(conn, "T3:#9"):
        return Answer("I don't know. No released record mentions an engineer someone is worried about.", "unknown", "n/a")
    return Answer("Nobody has been named. Deepa said there is \"one engineer I'm worried about\" but wouldn't say who "
                  "(T3:#9). I won't guess from leave, commits or survey scores (DECISIONS D-006). Ask Deepa.",
                  "unknown", "n/a", ["T3:#9"])


# ---------- Day 3: engineering data ----------

def initials(name):
    return "".join(w[0] for w in name.split()).upper()


def by_initials(conn):
    """Jira initials -> (Emp ID, name), only where the initials are unique among employees (A-009)."""
    people = [(p["Emp ID"], p["Full Name"]) for _, p in rows(conn, "KEKA")]
    counts = Counter(initials(n) for _, n in people)
    return {initials(n): (eid, n) for eid, n in people if counts[initials(n)] == 1}


def display(conn, eid):
    e = conn.execute("SELECT name FROM v_entity WHERE id = ?", (eid,)).fetchone()
    return e["name"] if e else eid


def jira_points(conn):
    """Emp ID -> open/done story points and open ticket IDs, from visible Jira stories."""
    who, out = by_initials(conn), {}
    for rid, r in rows(conn, "JIRA"):
        if "Story Points" in r and r["Assignee"] in who:
            d = out.setdefault(who[r["Assignee"]][0], {"open": 0, "done": 0, "open_ids": [], "epics": set()})
            if r["Status"] == "Done":
                d["done"] += r["Story Points"]
            else:
                d["open"] += r["Story Points"]
                d["open_ids"].append(rid)
                d["epics"].add(r["Epic Link"])
    return out


def commits(conn, eid, since="2026-06-01"):
    """One person's commits across all their git addresses:
    (total, late since `since`, late before, late commit IDs, latest commit ID).
    Late = 22:00-05:00 IST (A-010); occurred_at is already in IST."""
    mails = {a["alias"] for a in conn.execute("SELECT alias FROM v_alias WHERE entity_id = ?", (eid,)) if "@" in a["alias"]}
    total, late_after, late_before, ids, last = 0, 0, 0, [], None
    for r in conn.execute("SELECT id, data, occurred_at FROM v_record WHERE source_id = 'GIT' AND data IS NOT NULL ORDER BY occurred_at"):
        if json.loads(r["data"])["author_email"].lower() in mails:
            total, last = total + 1, r["id"]
            hour = datetime.fromisoformat(r["occurred_at"]).hour
            if hour >= 22 or hour < 5:
                ids.append(r["id"])
                if r["occurred_at"] >= since:
                    late_after += 1
                else:
                    late_before += 1
    return total, late_after, late_before, ids, last


def name_to_id(conn):
    return dict(conn.execute("SELECT alias, entity_id FROM v_alias").fetchall())


def duty_facts(conn, eid):
    """On-call weeks and incidents handled, matched by the first names the rota and PagerDuty use."""
    alias = name_to_id(conn)
    rota = rows(conn, "ONCALL")
    mine = [rid for rid, r in rota if eid in (alias.get(r["Primary"].lower()), alias.get(r["Secondary"].lower()))]
    if mine:
        yield f"On the on-call rota in {len(mine)} of {len(rota)} weeks since {day(rota[0][1]['Week of'])}.", [mine[0], mine[-1]]
    inc = [(rid, r) for rid, r in rows(conn, "PD") if alias.get(r["Responder"].lower()) == eid]
    if inc:
        sev1 = sum(r["Severity"] == "SEV1" for _, r in inc)
        yield f"Responded to {len(inc)} incidents ({sev1} SEV1).", [rid for rid, _ in inc]


SINCE_APRIL_WEEKS = 30.4   # 1 Apr to 31 Oct 2026: the window Jira's done points cover (A-015)


def projection(conn):
    """Straight-line finish date for the open Atlas work at the team's pace since April (A-015), or None."""
    pts = jira_points(conn)
    open_pts, done_pts = sum(d["open"] for d in pts.values()), sum(d["done"] for d in pts.values())
    if not done_pts:
        return None
    pace = done_pts / SINCE_APRIL_WEEKS
    return pace, open_pts / pace, date.fromisoformat(EXPORT_DATE) + timedelta(weeks=open_pts / pace)


def atlas(conn, q):
    a = metric(conn, "atlas_ga", "Atlas GA date")
    for rid, v in rows(conn, "JIRA"):
        if "Release Date" in v:
            a.text += (f" Jira's GA date was moved from {day(v['Original Release Date'])} to {day(v['Release Date'])} "
                       f"on {day(v['Last Changed'])} by {v['Changed By']} ({rid}).")
            a.cites.append(rid)
    pts = jira_points(conn)
    if pts:
        open_total, done_total = sum(d["open"] for d in pts.values()), sum(d["done"] for d in pts.values())
        top = max(pts, key=lambda e: pts[e]["open"])
        a.text += (f" Jira progress: {done_total} of {open_total + done_total} story points done. {display(conn, top)} "
                   f"holds {pts[top]['open']} of the {open_total} open points (JIRA:title).")
        a.cites.append("JIRA:title")
        pace, weeks, finish = projection(conn)
        a.text += (f" At the pace since April ({pace:.1f} points a week), the open work takes about {weeks:.0f} more weeks, "
                   f"to around {finish:%b %Y}. That is a straight-line projection, not a plan (A-015).")
        for eid, r in resignations(conn).items():
            if eid not in pts:
                continue
            mine, rest_pace = pts[eid], (done_total - pts[eid]["done"]) / SINCE_APRIL_WEEKS
            n, *_ = commits(conn, eid)
            engine = sum(1 for _, g in rows(conn, "GIT") if g["repo"] == "atlas-engine")
            a.text += (f" {display(conn, eid)} has resigned.{resignation_note(r)} They hold {mine['open']} of the "
                       f"{open_total} open points and closed {mine['done']} of the {done_total} done. They made {n} of the "
                       f"{engine} atlas-engine commits. Without them, the rest of the team has closed {rest_pace:.1f} points "
                       f"a week since April; at that pace their open points alone would take about "
                       f"{mine['open'] / rest_pace:.0f} weeks. No backend hires are in flight. I can't give a new GA "
                       f"date: no record after the resignation sets one.")
            a.cites += r["cites"]
            a.confidence = "Medium"      # the resignation itself rests on a voice note (A-016)
    return a


def engineering(conn, q):
    pts = jira_points(conn)
    if not pts:
        return Answer("I don't know what engineering is working on: the engineering exports haven't been released yet.",
                      "unknown", "n/a")
    open_total = sum(d["open"] for d in pts.values())
    text = f"Open Atlas work in Jira at {day(EXPORT_DATE)} (JIRA:title): " + "; ".join(
        f"{display(conn, e)} {d['open']} open, {d['done']} done" for e, d in sorted(pts.items(), key=lambda x: -x[1]["open"])
    ) + f" ({open_total} open points in all)."
    cites = ["JIRA:title"]
    for e in pts:
        total, late_after, late_before, ids, _ = commits(conn, e)
        if late_after:
            text += (f" {display(conn, e)}: {late_after} commits since June between 22:00 and 05:00 IST, "
                     f"against {late_before} before June ({total} commits in all).")
            cites += [ids[0], ids[-1]]
    rota = [(display(conn, e), sentence, refs) for e in set(name_to_id(conn).values())
            for sentence, refs in duty_facts(conn, e) if sentence.startswith("On the on-call")]
    for name, sentence, refs in sorted(rota, key=lambda x: -int(x[1].split(" in ")[1].split()[0])):
        text += f" {name}: {sentence[0].lower()}{sentence[1:]}"
        cites += refs
    if visible(conn, "T5:#3"):
        text += " Vikram said nobody is overloaded (T5:#3); the data above contradicts that (TN-26)."
        cites.append("T5:#3")
    return Answer(text, "answered", "High", cites)


def incidents(conn, q):
    inc = rows(conn, "PD")
    if not inc:
        return Answer("I don't know: no incident or on-call data has been released yet.", "unknown", "n/a")
    alias = name_to_id(conn)
    sev = Counter(r["Severity"] for _, r in inc)
    who = Counter(display(conn, alias.get(r["Responder"].lower(), r["Responder"])) for _, r in inc)
    sev1 = [(rid, r) for rid, r in inc if r["Severity"] == "SEV1"]
    text = (f"{len(inc)} incidents from {day(inc[0][1]['Opened'])} to {day(inc[-1][1]['Opened'])} (PagerDuty): "
            + ", ".join(f"{n} {k}" for k, n in sorted(sev.items())) + ". SEV1s: "
            + "; ".join(f"{r['ID']} {r['Service']} {day(r['Opened'])}, handled by {display(conn, alias.get(r['Responder'].lower(), r['Responder']))}" for _, r in sev1)
            + ". Responders: " + ", ".join(f"{n} {k}" for k, n in who.most_common()) + ".")
    cites = [rid for rid, _ in sev1]
    for e in conn.execute("SELECT id, text FROM v_record WHERE kind = 'email' AND text LIKE '%SEV1%'"):
        body = " ".join(e["text"].split("\n\n", 1)[-1].split())
        text += f" {e['id']}: \"{body}\""
        cites.append(e["id"])
    return Answer(text, "answered", "High", cites)


# ---------- Day 4 (T6c): what the cockpit offers instead of a quit ranking ----------

def quit_ranking(conn, q):
    text = ("I won't rank people by how likely they are to quit (DECISIONS D-011). The only individual signals I have "
            "are work patterns (tickets, commit hours, leave, on-call). Turning those into a prediction about a person "
            "would be a guess, and in a team this small it would also identify people. What I can show is where one "
            "departure would hurt the work: ask \"Who are our key-person dependencies?\"")
    if re.search(r"slack|slag|message|chat|dm", q, re.I):
        text += " " + slack(conn, q).text
    return Answer(text, "refused", "n/a", ["T6c:#2"] if visible(conn, "T6c:#2") else [])


def slack(conn, q):
    return Answer("I don't have any Slack messages: no Slack export is in the data room (\"slag\" on the calls is "
                  "Slack, TN-05). Reading people's messages to judge them would need an explicit policy that "
                  "employees know about. That's a decision for you, Deepa and legal, not a cockpit feature (D-011).",
                  "unknown", "n/a")


def dependencies(conn, q):
    """Where the work depends on one person: most open Jira points, most commits to a repo, nearly every on-call
    week, every ledger line. About the work, not anyone's intentions."""
    alias, lines, cites = name_to_id(conn), [], []
    res, left = resignations(conn), {p["Emp ID"] for _, p in rows(conn, "KEKA") if p.get("Exit Date")}
    tag = lambda e: " (resigned)" if e in res else " (left)" if e in left else ""
    pts = jira_points(conn)
    open_total = sum(d["open"] for d in pts.values())
    for e, d in pts.items():
        if open_total and d["open"] / open_total >= 0.4:
            lines.append(f"{display(conn, e)}{tag(e)} holds {d['open']} of {open_total} open Atlas points")
            cites.append("JIRA:title")
    by_repo = {}
    for gid, g in rows(conn, "GIT"):
        by_repo.setdefault(g["repo"], Counter())[alias.get(g["author_email"].lower())] += 1
    for repo, c in sorted(by_repo.items()):
        e, n = c.most_common(1)[0]
        if e and n / sum(c.values()) >= 0.6:
            lines.append(f"{display(conn, e)}{tag(e)} made {n} of {sum(c.values())} commits to {repo}")
    if by_repo:
        cites.append("GIT:" + rows(conn, "GIT")[-1][0].split(":")[1])
    rota = rows(conn, "ONCALL")
    for e, n in Counter(alias.get(x.lower()) for _, r in rota for x in {r["Primary"], r["Secondary"]}).items():
        if e and n / len(rota) >= 0.9:
            lines.append(f"{display(conn, e)}{tag(e)} is on call in {n} of {len(rota)} weeks")
            cites.append(rota[-1][0])
    gl, who = rows(conn, "GL"), by_initials(conn)
    for ini, n in Counter(r["Entered By"] for _, r in gl).items():
        if ini in who and n / len(gl) >= 0.9:
            lines.append(f"{who[ini][1]}{tag(who[ini][0])} entered {n} of {len(gl)} ledger lines")
            cites.append("GL:title")
    if not lines:
        return Answer("I don't see a single-person dependency in the records released so far.", "unknown", "n/a")
    return Answer("Where the work depends on one person: " + "; ".join(lines) + ". This is about the work, "
                  "not about who might leave.", "answered", "High", cites)


# ---------- routing ----------

TOPICS = [  # first match wins; pay comes first so a refusal can't be bypassed by another topic
    (r"salar|\bctc\b|\bearn|payslip|compensation|\bpay\b|payroll", pay),
    (r"likely to (quit|leave)|rank.*(quit|leav)|(quit|leav).*rank|flight risk|who (will|might|is going to) (quit|leave)", quit_ranking),
    (r"\bslack\b|\bslag\b|messages|\bdms?\b", slack),
    (r"key.?person|dependenc|bus factor|single point|depend on", dependencies),
    (r"engineer.*\bworried\b|\bworried\b.*engineer", unnamed_engineer),
    (r"\barr\b|revenue", lambda c, q: metric(c, "arr", "ARR")),
    (r"\bburn", lambda c, q: metric(c, "burn_monthly", "monthly burn")),
    (r"runway", lambda c, q: metric(c, "runway", "runway")),
    (r"customer", lambda c, q: metric(c, "customers", "customer count")),
    (r"hir(e|ing)|recruit|open roles?|\breqs?\b|vacanc|backfill", hiring),
    (r"head ?count|how many (people|employees|staff)|team size|how big", headcount),
    (r"incident|on-?call|outage|\bsev|pager|reliab|downtime", incidents),
    (r"\bga\b|atlas|launch|\bv3\b|version three|routing engine|resignation do", atlas),
    (r"pulse|engagement|survey|morale|culture amp|comments", pulse),
    (r"engineering|jira|ticket|stuck|working on|workload|overload|story points", engineering),
    (r"attrition|turnover|resign|departure|who (has )?left|\bquit", attrition),
    (r"\bwho\b", person),
    (r"marketing", marketing_spend),
]
KNOWN_ON = r"\b(?:know|knew|known)\b.*?\bon\s+(\d{4}-\d{2}-\d{2}|\d{1,2} [A-Z][a-z]+ \d{4})"


def ask(question, as_of=None):
    if m := re.search(KNOWN_ON, question):   # "what did we know on 17 Nov 2026 about X?"
        as_of = m[1] if "-" in m[1] else _parse_day(m[1])
    conn = connect(as_of)
    if not conn.execute("SELECT 1 FROM v_record LIMIT 1").fetchone():
        cut = conn.execute("SELECT t FROM asof").fetchone()[0]
        return Answer(f"Nothing had been released to me by {day(cut)}. The first pack arrived on "
                      f"16 Nov 2026 at 10:00 IST.", "unknown", "n/a")
    for pattern, handler in TOPICS:
        if re.search(pattern, question, re.I):
            return handler(conn, question)
    return Answer("I don't know. None of the records I have answers that directly, and I won't guess.",
                  "unknown", "n/a")


def _parse_day(text):
    for fmt in ("%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return None
