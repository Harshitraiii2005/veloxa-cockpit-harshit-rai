# Assumptions

I revise entries rather than deleting them. A revision is added under the original, with its date.

| ID | Date | Assumption | Source line it rests on | Confidence | What would change my mind |
|---|---|---|---|---|---|
| A-001 | 16 Nov | Each day folder counts as released at 10:00 IST on its day. A date-only `as_of` means the end of that day in IST. | Hackathon email §3: "Treat as released at 10:00 AM" | H | A reviewer using a different cutoff |
| A-002 | 16 Nov | The 14 people are the Keka employees in Engineering (5), Finance (3), People & Ops (3) and Marketing (3). The CEO, Sales (2) and Support (2) are left out. | Candidate brief: "14 people across engineering, finance, HR and marketing"; Employee_Master department column gives exactly 5+3+3+3 | H | A later source naming a different set |
| A-003 | 16 Nov | "HR" in the brief means the People & Ops department in Keka. | Brief: "engineering, finance, HR and marketing"; Keka department "People & Ops", with Deepa's title "Head of People & Ops" | H | A separate HR team appearing in a later export |
| A-004 | 16 Nov | Money is in INR. "L" = lakh (1,00,000) and "Cr" = crore (1,00,00,000). | Board updates: "Rs. 5.8 Cr", "Rs. 46 L"; GL column "Amount (Rs.)" | H | n/a |
| A-005 | 16 Nov | Export rows are snapshots as of 31 Oct 2026, not as of the day they were released to me. | data_room/README.txt: "Exported by IT on 31 Oct 2026"; Keka header "Exported 31-Oct-2026" | H | An export with a later export date |
| A-006 | 16 Nov | Transcripts have no recording date, so their `occurred_at` is unknown. They are dated only by release. | T1/T2 headers give duration and audio quality but no date | M | A dated calendar invite or email that references the call |
| A-007 | 17 Nov | A leave register name like "P. Nair" is the Keka employee with that first initial and surname. The alias is only created when exactly one employee matches. | `LEAVE` rows use "A. Das", "P. Nair" and so on; all 19 resolve uniquely against `KEKA` | H | Two employees sharing an initial and surname, or a leave row for someone not in Keka |
| A-008 | 17 Nov | A pulse row's "Quarter" is the period the survey covers, not the date it was sent. | `PULSE:title`: "quarterly pulse"; the Quarter column runs Oct–Dec 2025 to Jul–Sep 2026 | M | A survey export with send dates |
