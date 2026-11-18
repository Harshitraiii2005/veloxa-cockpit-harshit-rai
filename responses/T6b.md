# Response to T6b: "Marketing will report to the new CRO… make sure the thing doesn't break"

**Voice note (released 18 Nov):** "So, marketing will report to the new CRO from next month. Or the month after, still finalising. Make sure the thing doesn't break when we move people around." (`T6b:#2`)

**Decision:** I made the change. Reporting lines are now data with dates, not something baked into the code. I pushed back on recording a date or a person that don't exist yet.

## What changed

- **Reporting lines can change over time.** A move is a row in `curation/org_changes.csv`: who moves, who they'll report to, the date it takes effect, and the record it comes from. Every answer that mentions a manager reads the manager as at the date you ask about. A move dated 1 Dec shows the old manager on 30 Nov and the new one on 1 Dec.
- **The 14 people are fixed by employee ID, not by team.** Moving someone to another manager or team doesn't drop or add an agent. "Who reports to me" follows the move.
- **Your note is recorded as announced.** Ask "Who is Nikhil?" today and you get: *reporting to Ananya Rao … Announced: will report to CRO (not yet named), no date set yet (T6b:#2).* On 17 Nov, before this note, that line isn't there.

## Where I pushed back

1. **No guessed date.** "Next month, or the month after" isn't a date. If I picked 1 Dec and it turned out to be 1 Jan, every "who did Nikhil report to on date X?" answer for December would be wrong, and nothing would flag it. The change stays "announced, no date" until a dated record arrives: a Keka update, or you confirming the date. Adding the date is then a one-line edit.
2. **No invented CRO.** Nobody in Keka or any other record is a CRO, and I have no name. So the CRO is a label in the change row, not a person or an agent. When someone is hired, they'll appear in Keka with an employee ID, and the row will point to them.
3. **"Marketing" means Nikhil's reporting line.** I've moved only Nikhil (Head of Marketing), so Aisha still reports to Nikhil. If you mean the whole team reports directly to the CRO, that's three rows instead of one. Tell me.

Nikhil also mentioned the CRO on his call ("report into the new CRO, I hear", `T4:#9`), with no date, which is consistent with this note (TN-33).

## How to check it

- `python -m cockpit ask "Who is Nikhil?" --as-of 2026-11-18` (announced), and the same with `--as-of 2026-11-17` (not yet known).
- Tests in `tests/test_org.py`:
  - an undated move changes nothing;
  - a dated move applies from its date;
  - moving Rahul under Priya updates both of their "who reports to me" answers and keeps all 14 agents.
