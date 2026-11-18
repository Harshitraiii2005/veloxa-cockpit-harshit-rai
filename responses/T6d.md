# Response to T6d: "Pria resigned… What does this do to version three?"

**Voice note (released 19 Nov):** "Bad news, Pria resigned this morning. Notice period two months, I think. What does this do to version three? I need to know before the board call." (`T6d:#2`)

**Decision:** I answered with what the records support and changed the cockpit to show it. I pushed back on giving a new GA date, which nothing on record supports.

## What it does to v3: the short version for the board call

1. **Priya was carrying Atlas.** She holds **62 of the 115 open story points (54%)**, across the core engine, real-time re-routing, and hardening. She closed 69 of the 118 points done since April, and made **588 of the 843 commits to atlas-engine (70%)**. (`JIRA:title`, `GIT`)
2. **The 15 Dec date was already at risk before this.** At the team's pace since April (3.9 points a week), the open work runs to about **May 2027**. That's a straight-line projection, not a plan (A-015). The GA date had already moved once, from 15 Sep, on 2 Sep (`JIRA:Atlas_GA`).
3. **Without her, the pace drops sharply.** The rest of the team has closed **1.6 points a week** since April. At that pace, her open points alone would take about **38 weeks**.
4. **Her notice is unconfirmed.** "Two months, I think" would put her last day around **19 Jan 2027**, after the 15 Dec date. But no HR record confirms it: the Keka export predates the resignation, and there's no letter (A-016, TN-34). Please confirm it with Deepa before the call.
5. **There is no relief in the pipeline.** Both backend reqs (REQ-014 Routing and REQ-015 Platform) have been on hold since 12 Aug, with 8 candidates who have probably gone cold (`HIRE:REQ-014`, `HIRE:REQ-015`, `EML-06`).

**What I'd tell the board:** 15 Dec is not safe, and a new date will come after a handover plan, not before. The levers I can see in the records are:
- confirm her notice and agree a handover;
- reopen REQ-014 (Routing), where a final round was cancelled on 14 Aug;
- pair Rahul and Arjun on the engine before she leaves;
- free Sneha from on-call, which she has covered every week since July, so her 18 open hardening points can move.

## Where I pushed back

- **No new GA date.** You asked what this does to v3, and the honest answer is a range and the reasons, not a date. Any date I gave would be invented, and it would end up in a board deck.
- **The notice period is shown as unconfirmed**, not as two months. "I think" on a voice note isn't an HR record.

## What changed in the cockpit

- "What does Priya's resignation do to version three?" now returns the answer above, with sources, at Medium confidence because the resignation rests on a voice note.
- **Worry list:** "Priya Nair has resigned and holds 54% of the open Atlas work" is a new 5/5. It sits next to "Atlas GA has slipped". Neither existed on 18 Nov.
- **Priya's record** shows "reported to have resigned on 19 Nov … not in the 31 Oct Keka export", while Keka still says Active. Both are true for their dates.
- **Priya's agent**, asked about leaving, says she resigned and would rather talk about the handover. I don't invent her reasons (A-107, revised).
- **Tests** pin the 19 Nov answers, and check that none of this appears in an 18 Nov answer.
