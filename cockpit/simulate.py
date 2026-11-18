"""Stretch: keep the company "living" after the 31 Oct export (D-010).

A seeded, repeatable projection of the activity we have a measured basis for, computed on the fly from the
records visible at as_of. It is never stored and never cited as evidence. Every event names its basis.
  - commits: each engineer's weekday rate in Oct 2026, late-night share as since June (GIT)
  - on-call: the weekly primary/secondary swap seen since 17 Aug continues (ONCALL)
  - Jira: each person closes their open tickets at their own pace since April (JIRA)
  - ledger: Fatima keeps entering the monthly recurring lines on their usual days (GL); payroll amount hidden
Nothing is projected for people or activities with no data stream (marketing, people ops), or for anyone
whose Keka exit date has passed."""
import math
import random
from collections import Counter
from datetime import date, timedelta

from .answer import SINCE_APRIL_WEEKS, commits, display, inr, jira_points, name_to_id, rows
from .db import connect

START = date(2026, 11, 1)          # the day after the export (A-005)


def poisson(rng, rate):
    k, p, limit = 0, 1.0, math.exp(-rate)
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def simulate(as_of=None, seed=7):
    """[(day, entity ID, what happened, basis)], one seeded run from 1 Nov up to as_of."""
    conn = connect(as_of)
    end = date.fromisoformat(conn.execute("SELECT t FROM asof").fetchone()[0][:10])
    days = [START + timedelta(n) for n in range((end - START).days + 1)]
    rng, events = random.Random(seed), []
    people = {p["Emp ID"]: p for _, p in rows(conn, "KEKA")}
    alias = name_to_id(conn)
    gone = {e for e, p in people.items() if p.get("Exit Date") and p["Exit Date"] < START.isoformat()}

    # Commits: October weekday rate per person, late-night share since June.
    oct_counts, june_counts = Counter(), Counter()
    for _, r in rows(conn, "GIT"):
        eid = alias.get(r["author_email"].lower())
        oct_counts[eid] += r["committed_at"].startswith("2026-10")
        june_counts[eid] += r["committed_at"] >= "2026-06-01"
    for eid, n in oct_counts.items():
        if eid is None or eid in gone or not n:
            continue
        rate = n / 22                                   # 22 weekdays in Oct 2026
        late_after = commits(conn, eid, since="2026-06-01")[1]
        late_share = late_after / june_counts[eid]
        for d in days:
            if d.weekday() < 5 and (k := poisson(rng, rate)):
                late = sum(rng.random() < late_share for _ in range(k))
                events.append((d, eid, f"{k} commit{'s' if k > 1 else ''}" + (f", {late} after 22:00 IST" if late else ""),
                               f"GIT: {rate:.1f} commits a weekday in Oct, {late_share:.0%} late since June"))

    # On-call: continue the weekly swap of the last rota week.
    rota = rows(conn, "ONCALL")
    if rota:
        last = rota[-1][1]
        primary, secondary = alias.get(last["Primary"].lower()), alias.get(last["Secondary"].lower())
        week = date.fromisoformat(last["Week of"]) + timedelta(7)
        while week <= end:
            primary, secondary = secondary, primary
            if week >= START:
                events.append((week, primary, "on call this week (primary)", "ONCALL: weekly swap since 17 Aug"))
                events.append((week, secondary, "on call this week (secondary)", "ONCALL: weekly swap since 17 Aug"))
            week += timedelta(7)

    # Jira: each person closes open tickets, oldest first, at their own pace since April.
    pts = jira_points(conn)
    tickets = {rid: r for rid, r in rows(conn, "JIRA") if "Story Points" in r}
    for eid, d in pts.items():
        pace, banked = d["done"] / SINCE_APRIL_WEEKS, 0.0
        queue = sorted(d["open_ids"], key=lambda rid: tickets[rid]["Created"])
        for day_ in (x for x in days if x.weekday() == 4):          # Fridays
            banked += pace
            while queue and banked >= tickets[queue[0]]["Story Points"]:
                t = tickets[queue.pop(0)]
                banked -= t["Story Points"]
                events.append((day_, eid, f"closed {t['Key']} {t['Summary']} ({t['Story Points']} pts)",
                               f"JIRA: {pace:.1f} pts a week, the pace since April"))

    # Ledger: the monthly recurring lines, entered by whoever entered them before (FS).
    gl = rows(conn, "GL")
    for vendor, cc in (("Google India Pvt Ltd", "MKT-PS"), ("Amazon Web Services", "ENG-INF"),
                       ("WeWork India", "G&A"), ("Salaries (payroll)", "PAYROLL")):
        hist = [r for _, r in gl if r["Vendor / Payee"] == vendor]
        if not hist:
            continue
        on_day = int(hist[-1]["Txn Date"][8:10])
        amounts = [r["Amount (Rs.)"] for r in hist]
        growth = (amounts[-1] - amounts[0]) / (len(amounts) - 1) if vendor == "Amazon Web Services" else 0
        who = next((e for e, p in people.items() if "".join(w[0] for w in p["Full Name"].split()) == hist[-1]["Entered By"]), None)
        for d in days:
            if d.day == min(on_day, 30):
                months_on = (d.year - 2026) * 12 + d.month - int(hist[-1]["Txn Date"][5:7])
                typical = (sum(amounts[-3:]) / 3 if cc == "MKT-PS" else amounts[-1] + growth * months_on)
                what = (f"entered {cc} {vendor}, amount hidden (individual pay could be inferred, D-006)" if cc == "PAYROLL"
                        else f"entered {cc} {vendor}, about {inr(typical)}")
                events.append((d, who, what, f"GL: {vendor} is booked around day {on_day} every month"))
    return sorted(events, key=lambda e: (e[0], e[1] or ""))


def diary(eid, as_of=None, days=7, seed=7):
    """The last `days` days of one person's simulated activity."""
    events = simulate(as_of, seed)
    if not events:
        return []
    last = events[-1][0]
    return [e for e in events if e[1] == eid and e[0] > last - timedelta(days)]


if __name__ == "__main__":
    for d, eid, what, basis in simulate():
        print(d, display(connect(), eid) if eid else "?", "|", what, "|", basis)
