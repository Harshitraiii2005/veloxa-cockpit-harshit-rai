# Transcript notes

Suspected mishearings and contradictions, the evidence for each, and my conclusion. Record IDs (e.g. `KEKA:VX007`) are the IDs the cockpit cites.

Each conclusion below is my own call. I made it by choosing between readings of the evidence; see AI_LOG.md for how AI helped.

Status key: **open** (evidence collected, not yet decided) · **decided** · **revised** (the conclusion changed later, and the old one is kept below the new one)

## Day 1 (released 16 Nov): T1 CEO kickoff, T2 CFO call

### TN-01 · Company size: "one-eighty" vs 19 · decided
- T1: "roughly eighteen people ('one-eighty, give or take')"
- Candidate brief: "a 180-person B2B SaaS company"
- Employee_Master: 19 employee rows. The header says contractors are not in Keka.
- `BOARD-APRJUN` (sent 8 Jul) and `BOARD-JULSEP` (sent 6 Oct): Team 19
- Conclusion (17 Nov): I believe 19. Keka has 19 employee rows (`KEKA:title`), and both board updates say Team 19 (`BOARD-APRJUN`, `BOARD-JULSEP`): three records from two systems agree. T1's own summary says "roughly eighteen people" in the same sentence as "one-eighty", so "180" is a transcription slip, and the brief repeats it. Set aside: C016 (misheard), C017 (wrong). Confidence: H. What would change my mind: an export of contractors or of a group company adding about 160 people.

### TN-02 · ARR: "forty-two / forty-five crore" vs "forty-eight" vs 5.8 → 6.1 Cr · decided
- T1: "around forty-two crore, maybe forty-five now"
- T2: "ARR at the start of the year was 'forty-eight'" (no unit; the year runs April to March)
- Board Apr–Jun (sent 8 Jul): ARR Rs. 5.8 Cr
- Board Jul–Sep (sent 6 Oct): ARR Rs. 6.1 Cr
- Conclusion (17 Nov): I believe the board figures: Rs 5.8 Cr at 30 Jun and Rs 6.1 Cr at 30 Sep. Both are formal documents sent to the board, and they move in a believable direction. "Forty-two crore" (T1) is about 7 times the board figure, and "forty-eight" (T2, poor audio) has no unit, so I treat both as misheard and don't use either. Set aside: C003, C004 (misheard). Confidence: H on the board figures, M on why the call figures differ. What would change my mind: a finance export (invoicing or a revenue schedule) with a different ARR.

### TN-03 · Burn: "two point two" vs Rs. 46 L / 44 L · decided
- T1: burn "around two point two" (unit not stated)
- T2: "two point two lakhs a month, sometimes two point five"
- Board Apr–Jun: monthly burn Rs. 46 L. Board Jul–Sep: Rs. 44 L.
- GL: payroll alone is Rs. 31.75 L every month, Apr to Sep (`GL:PAY-APR` … `GL:PAY-SEP`). The GL is "selected cost centres" only, so it can't give a full burn figure.
- Conclusion (17 Nov): I believe the board: Rs 46 L a month for Apr–Jun and Rs 44 L a month for Jul–Sep. The GL shows payroll alone at Rs 31.75 L every month (`GL:PAY-SEP`), so a burn of Rs 2.2 L a month is impossible. The "2.2" on both calls is a unit or scale mishearing; T2's audio was "poor (speakerphone)". Set aside: C007, C008 (misheard). Confidence: H. What would change my mind: a full budget-vs-actuals sheet (Meera's T2 action item) showing a different burn.

### TN-04 · Which FY: "twenty-six" or "twenty-seven" · decided
- T2: "April to March, so we're in FY twenty-six (note: speaker may have said twenty-seven)"
- The calls happen in Nov 2026, which falls in the year Apr 2026 – Mar 2027.
- Conclusion (17 Nov): Apr 2026 – Mar 2027 is FY27. It is FY 2026-27, named by the year it ends, which is the usual Indian convention. "Twenty-six" is a mishearing, as the transcriber already flagged. I use FY27. Confidence: M. What would change my mind: a Veloxa document calling this year FY26.

### TN-05 · Tool names · decided
| Heard | Likely | Evidence |
|---|---|---|
| "Jeera board" / "Linear, I think" | Jira | data_room/README: "Jira (ATLAS)" |
| "Joho books" | Zoho Books | README; GL header "Zoho Books" |
| "Kayka" | Keka | README "Keka HRMS"; Employee_Master header |
| "Cult Amp" | Culture Amp | README "Culture Amp pulse" |
| "hub sport" | HubSpot | no export yet |
| "slag channel" | Slack | no export yet |
- Conclusion (17 Nov): Accepted: Jeera = Jira, Joho books = Zoho Books, Kayka = Keka, Cult Amp = Culture Amp, hub sport = HubSpot, slag = Slack, Git Hub = GitHub. Each matches an export header or the README, except HubSpot and Slack, which are the obvious names; there is no export from either. Confidence: H (M for HubSpot and Slack).

### TN-06 · People's names · decided (Pria open)
| Heard | Candidate | Evidence |
|---|---|---|
| "Pria" (T1) | VX007 Priya Nair, Staff Engineer | Keka; the only Priya |
| "the new boy Rahul" (T1) | VX018 Rahul Verma, joined 2026-02-03 | Keka join date; the latest joiner |
| "Kartik" (T2), "doing his CFA" | VX010 Karthik Subramanian, FP&A Manager | Keka; T2 says "on planning" |
| "Fatima Shaikh" (T2) | VX014 Fatima Sheikh | Keka spelling; emails 02/03 |
| "Vicky" (T2), "check the freeze decision" | VX004 Vikram Menon? | No "Vicky" in Keka. The freeze would hit engineering hiring. Weak. |
- *(added 17 Nov)* `LEAVE:2026-05-25`: K. Subramanian took exam leave, 25–29 May. This fits "doing his CFA".
- *(added 17 Nov)* `EML-06`: Meera tells Vikram she is pausing two reqs, and `EML-07` is Vikram's reply. That fits "check the freeze decision with Vicky", but no record calls Vikram "Vicky".
- Conclusion (17 Nov): Accepted: Kartik = Karthik Subramanian (VX010), Fatima Shaikh = Fatima Sheikh (VX014), and "the new boy Rahul" = Rahul Verma (VX018). Accepted with low confidence: Vicky = Vikram Menon (VX004), because the freeze being checked is the one that hit his reqs (`EML-06`, `EML-07`). Not yet accepted: Pria = Priya Nair. The accepted mappings are rows in curation/aliases.csv. What would change my mind on Vicky: any record using "Vicky" for someone else.

### TN-07 · Atlas timing: "by the festive season" vs 15 Sep GA · decided
- T1: v3 "promised to some customers by the festive season"
- Board Apr–Jun: "on track for GA on 15 September"
- Board Jul–Sep: "We moved GA … the engine itself is feature-complete". No new date given.
- Conclusion (17 Nov): These are two different dates. GA was planned for 15 Sep (board), and separately some customers were promised v3 "by the festive season", meaning around Oct–Nov. The Jul–Sep board update says GA has moved with no new date, so the customer promise is now at risk too. The Atlas worry quotes both. Confidence: M, since the promise comes only from the CEO's call. What would change my mind: a customer contract or email with a different date.

### TN-08 · Fatima's wedding month and the Feb payroll · decided
- T2: Fatima "was out for her wedding, that month was messy"
- `EML-01` (28 Feb): Karthik "Ran Feb payroll since Fatima is out. Used the Jan sheet and added the new joiner."
- Payroll register: Feb rows were processed by KS, and Jan/Mar rows by FS.
- `KEKA:VX018`: Rahul joined 2026-02-03. Feb payroll (`PAYROLL:r39`) shows him at 28 of 28 days payable, gross Rs. 1,10,000.
- `EML-02`: Rahul says his first payslip "looks higher than what I expected for a partial month". `EML-03`: Fatima says "Will check and get back." There is no later record of the outcome.
- *(added 17 Nov)* `LEAVE:2026-02-09`: F. Sheikh took marriage leave, 9–27 Feb (15 days), approved by MI. She was away for the whole Feb payroll run.
- Conclusion (17 Nov): Rahul was probably overpaid for February, and nothing shows it was corrected. Four independent records line up: he joined on 3 Feb (`KEKA:VX018`); Fatima was on marriage leave for the whole Feb run (`LEAVE:2026-02-09`); Karthik reused the Jan sheet (`EML-01`); and the register shows 28 of 28 days payable (`PAYROLL:r39`). Rahul queried it himself (`EML-02`), and the only reply is "Will check" (`EML-03`). This stays on the worry list at Medium confidence, with amounts hidden (D-006). What would change my mind: a correction in a later payroll run, or a reply to Rahul.

### TN-09 · "Two backend roles" · decided
- T2 mentions them in passing.
- Board Apr–Jun: "We will add two backend engineers this quarter … Search is underway."
- `GL:JV-0688` (30 Jun): Cohere Recruiting Partners, Rs. 1,77,000, "Search fee, 2 backend roles (50% advance)"
- Board Jul–Sep: "Hiring is paused while we close the round."
- *(added 17 Nov)* `HIRE:REQ-014` (Backend Engineer, Routing) and `HIRE:REQ-015` (Backend Engineer, Platform) were both opened on 18 May and put on hold on 12 Aug, with 3 and 5 candidates in the pipeline. REQ-014 note: "Final round 14-Aug cancelled".
- *(added 17 Nov)* `EML-06` (12 Aug): Meera writes "Pausing REQ-014 and REQ-015 until the round closes. Burn is the priority this quarter." `EML-07`: Vikram replies "Understood. We'll absorb it."
- Conclusion (17 Nov): No conflict. The records tell one story: two backend hires were planned (`BOARD-APRJUN`), a 50% recruiter advance was paid (`GL:JV-0688`), REQ-014 and REQ-015 were opened on 18 May, and both were paused on 12 Aug "until the round closes" (`EML-06`). The worry is the money spent and the risk to Atlas, not a disagreement between sources.

### TN-10 · Marketing spend "fine" vs "Nikhil's numbers never match mine" · open
- T1: CEO thinks marketing spend is "fine". T2: Meera says "Nikhil's numbers never match mine."
- GL marketing lines, Apr–Sep: Google Ads (MKT-PS) and summit costs (MKT-EVT). The vendor names "Sapphire Events Pvt Ltd" (`GL:JV-0846`) and "Saphire Event Mgmt" (`GL:JV-0904`) are spelt differently. "Sapphire Residency Hotel" (`GL:JV-0918`) is a sales offsite.
- Conclusion (17 Nov): Waiting for the Day 3 marketing data (Nikhil's own numbers) before deciding.

### TN-11 · "The number by March" · decided
- T1: Speaker 2 (unidentified) says the board wants "the number by March". Which number is not said.
- Conclusion (17 Nov): This can't be checked: no record says which number the board wants by March. The cockpit doesn't guess.

## Day 2 (released 17 Nov): T3 Head of People call, T6a voice note

### TN-12 · Attrition "about twelve" · decided
- `T3:#3`: Deepa says attrition is "about twelve, which is normal for Bangalore". The summary notes it is unclear whether this is a percentage, a headcount or a target.
- `T1:#8`: the CEO says attrition "feels high but Deepa says it's normal".
- `KEKA:title`: the export lists current employees only, so past leavers aren't in it. The only exit date is Siddharth's (`KEKA:VX013`).
- `BOARD-JULSEP`: "One planned departure in marketing."
- No record lets me compute an attrition rate.
- Conclusion (17 Nov): This can't be checked: Keka has no past leavers, and "twelve" has no unit. The cockpit answers "I don't know" and quotes Deepa as unverified.

### TN-13 · "Twenty-two open roles in April", "lost six of them in August" · decided
- `T3:#6`: Rohan says there were "twenty-two open roles in April" and "we lost six of them in August".
- The hiring tracker has 6 reqs in total (REQ-011, REQ-013 to REQ-017). In April, only `HIRE:REQ-011` was open, and it closed on 2 Apr ("Budget moved to marketing").
- `HIRE:REQ-014` and `HIRE:REQ-015` went on hold on 12 Aug with 3 + 5 = 8 candidates in the pipeline. `EML-06` paused them the same day.
- Conclusion (17 Nov): I believe the tracker. It has only 6 reqs in total, and during April just one was open (`HIRE:REQ-011`, closed 2 Apr), so "twenty-two" is a mishearing. "Lost six of them in August" doesn't match either: two reqs went on hold on 12 Aug. Set aside: C022 (misheard). Confidence: M, because the tracker might not hold every role Rohan counts. What would change my mind: a headcount plan listing 20 or more roles.

### TN-14 · Offer acceptance "down to fifty-something" · decided
- `T3:#6`: Rohan says offer acceptance is "down to fifty-something".
- The tracker records one accepted offer (`HIRE:REQ-013`, "Offer accepted, joining 3-Feb") and no declined offers. No record lets me compute a rate.
- Conclusion (17 Nov): This can't be checked: the tracker has one accepted offer and no declined offers.

### TN-15 · Tool names: "Liver", "Kekka", "Cult Amp" · decided
| Heard | Likely | Evidence |
|---|---|---|
| "Liver" (hiring) | Keka Hire? Lever? | `HIRE:title` says "Hiring tracker (Keka Hire)"; README: "Keka Hire tracker" |
| "Kekka" (HR records) | Keka | `KEKA:title`: "Keka HRMS export" |
| "Cult Amp" (pulse) | Culture Amp | `PULSE:title`: "Culture Amp quarterly pulse" |
- Conclusion (17 Nov): Liver = Keka Hire, a mishearing: the tracker header and the README name Keka Hire, and no other hiring tool appears in the data. Kekka = Keka, Cult Amp = Culture Amp. Confidence: M for Liver.

### TN-16 · Lakshmi "as HRBP ('she handles exits')" · decided
- `T3:#5`: "Lakshmi as HRBP ('she handles exits')".
- `KEKA:VX017`: Lakshmi Pillai, HR & Office Executive, joined 6 Oct 2025, reports to Deepa.
- Conclusion (17 Nov): Her title is the one in Keka: HR & Office Executive. "HRBP" is how Deepa describes her duties (handling exits), not her title, so the two describe different things. The cockpit uses the Keka title. Confidence: M.

### TN-17 · Survey comments: Deepa on the call vs Deepa's own email · decided
- `T3:#3`: Deepa "wants Ananya to see survey comments directly: 'numbers alone hide everything'". `T3:#13`: the action item is for Ananya to decide on comment visibility.
- `EML-11` (29 Sep, Deepa to Ananya): "The team is too small for me to share comments."
- `PULSE:title` says "team level only". Every row says "Not shown: team smaller than 6", and the largest team in the survey has 5 people.
- Conclusion (17 Nov): Deepa's call overrides her email. On the call she wants Ananya to see the comments, and I take the call as newer than the 29 Sep email. The cockpit still has no comments, because the export hides them for every team, so it now says it doesn't have them and to ask Deepa, instead of refusing. It still won't reconstruct comments from scores. Confidence: L, because the call's date is unknown (A-006). What would change my mind: a dated record putting the call before 29 Sep, or Ananya's decision (the T3 action item).

### TN-18 · Engineering pulse "dipped in the July round" · decided
- `T3:#3`: engineering scores "dipped in the July round".
- `PULSE:r6`: Engineering, Apr–Jun 2026, 3.9 (5 of 5 responded). `PULSE:r7`: Engineering, Jul–Sep 2026, 3.1 (4 of 5 responded).
- `EML-11` (29 Sep): "engineering pulse dropped this quarter".
- Open question: is "the July round" the Jul–Sep row, or a survey taken in July?
- Conclusion (17 Nov): "The July round" is the Jul–Sep 2026 row (`PULSE:r7`), which dropped from 3.9 to 3.1. It is the only engineering drop, and Deepa's 29 Sep email says the same. Confidence: M (A-008).

### TN-19 · Manager training: "after Diwali, November-ish" vs "January" · decided
- `T3:#10`: Deepa says it started "after Diwali, so November-ish". Rohan says "January".
- No other record mentions manager training.
- Conclusion (17 Nov): This can't be checked: no record mentions manager training, so the cockpit has no answer to give.

### TN-20 · "One engineer I'm worried about" · decided
- `T3:#9`: Deepa says there is "one engineer I'm worried about" but won't name them on the call.
- The cockpit won't guess a name from other signals (DECISIONS D-006).
- Conclusion (17 Nov): This can't be checked, and the cockpit won't guess who the engineer is (D-006).

### TN-21 · Sid's resignation · decided
- `T3:#8`: "Sid from marketing has put in his papers."
- `RESIGN-SM`: Siddharth Mehta to Nikhil Bose, dated 15 Sep 2026, last working day 31 Oct 2026. He gives "clearer launch timelines" as his reason.
- `KEKA:VX013`: Notice period, exit date 2026-10-31. `BOARD-JULSEP`: "One planned departure in marketing." `HIRE:REQ-016`: Product Marketing Manager backfill, opened 17 Sep, 7 in the pipeline.
- Conclusion (17 Nov): No conflict: the call, the letter, Keka, the board update and the backfill req all agree. Sid = Siddharth Mehta (VX013), added as an alias.
