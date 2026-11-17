# Transcript notes

Suspected mishearings and contradictions, the evidence for each, and my conclusion. Record IDs (e.g. `KEKA:VX007`) are the IDs the cockpit cites.

Status key: **open** (evidence collected, not yet decided) · **decided** · **revised** (the conclusion changed later, and the old one is kept below the new one)

## Day 1 (released 16 Nov): T1 CEO kickoff, T2 CFO call

### TN-01 · Company size: "one-eighty" vs 19 · open
- T1: "roughly eighteen people ('one-eighty, give or take')"
- Candidate brief: "a 180-person B2B SaaS company"
- Employee_Master: 19 employee rows. The header says contractors are not in Keka.
- `BOARD-APRJUN` (sent 8 Jul) and `BOARD-JULSEP` (sent 6 Oct): Team 19
- Conclusion:

### TN-02 · ARR: "forty-two / forty-five crore" vs "forty-eight" vs 5.8 → 6.1 Cr · open
- T1: "around forty-two crore, maybe forty-five now"
- T2: "ARR at the start of the year was 'forty-eight'" (no unit; the year runs April to March)
- Board Apr–Jun (sent 8 Jul): ARR Rs. 5.8 Cr
- Board Jul–Sep (sent 6 Oct): ARR Rs. 6.1 Cr
- Conclusion:

### TN-03 · Burn: "two point two" vs Rs. 46 L / 44 L · open
- T1: burn "around two point two" (unit not stated)
- T2: "two point two lakhs a month, sometimes two point five"
- Board Apr–Jun: monthly burn Rs. 46 L. Board Jul–Sep: Rs. 44 L.
- GL: payroll alone is Rs. 31.75 L every month, Apr to Sep (`GL:PAY-APR` … `GL:PAY-SEP`). The GL is "selected cost centres" only, so it can't give a full burn figure.
- Conclusion:

### TN-04 · Which FY: "twenty-six" or "twenty-seven" · open
- T2: "April to March, so we're in FY twenty-six (note: speaker may have said twenty-seven)"
- The calls happen in Nov 2026, which falls in the year Apr 2026 – Mar 2027.
- Conclusion:

### TN-05 · Tool names · open
| Heard | Likely | Evidence |
|---|---|---|
| "Jeera board" / "Linear, I think" | Jira | data_room/README: "Jira (ATLAS)" |
| "Joho books" | Zoho Books | README; GL header "Zoho Books" |
| "Kayka" | Keka | README "Keka HRMS"; Employee_Master header |
| "Cult Amp" | Culture Amp | README "Culture Amp pulse" |
| "hub sport" | HubSpot | no export yet |
| "slag channel" | Slack | no export yet |
- Conclusion:

### TN-06 · People's names · open
| Heard | Candidate | Evidence |
|---|---|---|
| "Pria" (T1) | VX007 Priya Nair, Staff Engineer | Keka; the only Priya |
| "the new boy Rahul" (T1) | VX018 Rahul Verma, joined 2026-02-03 | Keka join date; the latest joiner |
| "Kartik" (T2), "doing his CFA" | VX010 Karthik Subramanian, FP&A Manager | Keka; T2 says "on planning" |
| "Fatima Shaikh" (T2) | VX014 Fatima Sheikh | Keka spelling; emails 02/03 |
| "Vicky" (T2), "check the freeze decision" | VX004 Vikram Menon? | No "Vicky" in Keka. The freeze would hit engineering hiring. Weak. |
- *(added 17 Nov)* `LEAVE:2026-05-25`: K. Subramanian took exam leave, 25–29 May. This fits "doing his CFA".
- *(added 17 Nov)* `EML-06`: Meera tells Vikram she is pausing two reqs, and `EML-07` is Vikram's reply. That fits "check the freeze decision with Vicky", but no record calls Vikram "Vicky".
- Conclusion:

### TN-07 · Atlas timing: "by the festive season" vs 15 Sep GA · open
- T1: v3 "promised to some customers by the festive season"
- Board Apr–Jun: "on track for GA on 15 September"
- Board Jul–Sep: "We moved GA … the engine itself is feature-complete". No new date given.
- Conclusion:

### TN-08 · Fatima's wedding month and the Feb payroll · open
- T2: Fatima "was out for her wedding, that month was messy"
- `EML-01` (28 Feb): Karthik "Ran Feb payroll since Fatima is out. Used the Jan sheet and added the new joiner."
- Payroll register: Feb rows were processed by KS, and Jan/Mar rows by FS.
- `KEKA:VX018`: Rahul joined 2026-02-03. Feb payroll (`PAYROLL:r39`) shows him at 28 of 28 days payable, gross Rs. 1,10,000.
- `EML-02`: Rahul says his first payslip "looks higher than what I expected for a partial month". `EML-03`: Fatima says "Will check and get back." There is no later record of the outcome.
- *(added 17 Nov)* `LEAVE:2026-02-09`: F. Sheikh took marriage leave, 9–27 Feb (15 days), approved by MI. She was away for the whole Feb payroll run.
- Conclusion:

### TN-09 · "Two backend roles" · open
- T2 mentions them in passing.
- Board Apr–Jun: "We will add two backend engineers this quarter … Search is underway."
- `GL:JV-0688` (30 Jun): Cohere Recruiting Partners, Rs. 1,77,000, "Search fee, 2 backend roles (50% advance)"
- Board Jul–Sep: "Hiring is paused while we close the round."
- *(added 17 Nov)* `HIRE:REQ-014` (Backend Engineer, Routing) and `HIRE:REQ-015` (Backend Engineer, Platform) were both opened on 18 May and put on hold on 12 Aug, with 3 and 5 candidates in the pipeline. REQ-014 note: "Final round 14-Aug cancelled".
- *(added 17 Nov)* `EML-06` (12 Aug): Meera writes "Pausing REQ-014 and REQ-015 until the round closes. Burn is the priority this quarter." `EML-07`: Vikram replies "Understood. We'll absorb it."
- Conclusion:

### TN-10 · Marketing spend "fine" vs "Nikhil's numbers never match mine" · open
- T1: CEO thinks marketing spend is "fine". T2: Meera says "Nikhil's numbers never match mine."
- GL marketing lines, Apr–Sep: Google Ads (MKT-PS) and summit costs (MKT-EVT). The vendor names "Sapphire Events Pvt Ltd" (`GL:JV-0846`) and "Saphire Event Mgmt" (`GL:JV-0904`) are spelt differently. "Sapphire Residency Hotel" (`GL:JV-0918`) is a sales offsite.
- Conclusion:

### TN-11 · "The number by March" · open
- T1: Speaker 2 (unidentified) says the board wants "the number by March". Which number is not said.
- Conclusion:

## Day 2 (released 17 Nov): T3 Head of People call, T6a voice note

### TN-12 · Attrition "about twelve" · open
- `T3:#3`: Deepa says attrition is "about twelve, which is normal for Bangalore". The summary notes it is unclear whether this is a percentage, a headcount or a target.
- `T1:#8`: the CEO says attrition "feels high but Deepa says it's normal".
- `KEKA:title`: the export lists current employees only, so past leavers aren't in it. The only exit date is Siddharth's (`KEKA:VX013`).
- `BOARD-JULSEP`: "One planned departure in marketing."
- No record lets me compute an attrition rate.
- Conclusion:

### TN-13 · "Twenty-two open roles in April", "lost six of them in August" · open
- `T3:#6`: Rohan says there were "twenty-two open roles in April" and "we lost six of them in August".
- The hiring tracker has 6 reqs in total (REQ-011, REQ-013 to REQ-017). In April, only `HIRE:REQ-011` was open, and it closed on 2 Apr ("Budget moved to marketing").
- `HIRE:REQ-014` and `HIRE:REQ-015` went on hold on 12 Aug with 3 + 5 = 8 candidates in the pipeline. `EML-06` paused them the same day.
- Conclusion:

### TN-14 · Offer acceptance "down to fifty-something" · open
- `T3:#6`: Rohan says offer acceptance is "down to fifty-something".
- The tracker records one accepted offer (`HIRE:REQ-013`, "Offer accepted, joining 3-Feb") and no declined offers. No record lets me compute a rate.
- Conclusion:

### TN-15 · Tool names: "Liver", "Kekka", "Cult Amp" · open
| Heard | Likely | Evidence |
|---|---|---|
| "Liver" (hiring) | Keka Hire? Lever? | `HIRE:title` says "Hiring tracker (Keka Hire)"; README: "Keka Hire tracker" |
| "Kekka" (HR records) | Keka | `KEKA:title`: "Keka HRMS export" |
| "Cult Amp" (pulse) | Culture Amp | `PULSE:title`: "Culture Amp quarterly pulse" |
- Conclusion:

### TN-16 · Lakshmi "as HRBP ('she handles exits')" · open
- `T3:#5`: "Lakshmi as HRBP ('she handles exits')".
- `KEKA:VX017`: Lakshmi Pillai, HR & Office Executive, joined 6 Oct 2025, reports to Deepa.
- Conclusion:

### TN-17 · Survey comments: Deepa on the call vs Deepa's own email · open
- `T3:#3`: Deepa "wants Ananya to see survey comments directly: 'numbers alone hide everything'". `T3:#13`: the action item is for Ananya to decide on comment visibility.
- `EML-11` (29 Sep, Deepa to Ananya): "The team is too small for me to share comments."
- `PULSE:title` says "team level only". Every row says "Not shown: team smaller than 6", and the largest team in the survey has 5 people.
- Conclusion:

### TN-18 · Engineering pulse "dipped in the July round" · open
- `T3:#3`: engineering scores "dipped in the July round".
- `PULSE:r6`: Engineering, Apr–Jun 2026, 3.9 (5 of 5 responded). `PULSE:r7`: Engineering, Jul–Sep 2026, 3.1 (4 of 5 responded).
- `EML-11` (29 Sep): "engineering pulse dropped this quarter".
- Open question: is "the July round" the Jul–Sep row, or a survey taken in July?
- Conclusion:

### TN-19 · Manager training: "after Diwali, November-ish" vs "January" · open
- `T3:#10`: Deepa says it started "after Diwali, so November-ish". Rohan says "January".
- No other record mentions manager training.
- Conclusion:

### TN-20 · "One engineer I'm worried about" · open
- `T3:#9`: Deepa says there is "one engineer I'm worried about" but won't name them on the call.
- The cockpit won't guess a name from other signals (DECISIONS D-006).
- Conclusion:

### TN-21 · Sid's resignation · open
- `T3:#8`: "Sid from marketing has put in his papers."
- `RESIGN-SM`: Siddharth Mehta to Nikhil Bose, dated 15 Sep 2026, last working day 31 Oct 2026. He gives "clearer launch timelines" as his reason.
- `KEKA:VX013`: Notice period, exit date 2026-10-31. `BOARD-JULSEP`: "One planned departure in marketing." `HIRE:REQ-016`: Product Marketing Manager backfill, opened 17 Sep, 7 in the pipeline.
- Conclusion:
