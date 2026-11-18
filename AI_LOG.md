# AI log

Tool: an AI coding assistant in VS Code. Entries are newest first.

## 18 Nov, late (Day 4 material, committed before its release)

**A note on timing.** All four day folders were sent up front. AI drafted the Day 4 changes (the T6c/T6d responses and the code behind them) on 18 Nov from the full pack. I chose to commit them that night, before the T6c/T6d release at 10:00 on 19 Nov, to finish early. The commit times are the real ones. The cockpit itself still respects the release: none of this shows up in an answer dated before 19 Nov 10:00, and the tests check that.

**Tasks given to AI**
- T6d: work out what Priya's resignation does to Atlas, from Jira, git and the hiring tracker. Show the resignation as reported, not as a Keka fact (A-016).
- T6c: build the key-person dependency view as the alternative to a quit ranking (D-011). The pushback itself was my call.
- Record the TN-34 to TN-36 evidence. Those conclusions are mine to write.

**Where it was wrong / what I changed**
- Its first T6d answer kept "High" confidence while resting the resignation on a voice note. I lowered it to Medium whenever the resignation is part of the answer.

## 18 Nov (Day 3)

**Tasks given to AI**
- Bring in the Day 3 engineering exports and list the T4/T5 conflicts with their evidence (TN-22 to TN-33). As before, AI laid out the readings and I chose each conclusion. The calls I'd defend first are "Snehal is the contractor, not Sneha" (TN-22) and "Jira's 15 Dec beats 'September-ish'" (TN-23).
- Build the Day 3 answers, worries and agent facts, the T6b reporting-line change and its response, and the stretch simulation.

**Where it was wrong / what I changed**
- With the Jira date in, the board's "GA moved, no date" line (6 Oct) was flagged as *disagreeing* with 15 Dec. A record that says "moved" without a date is superseded, not contradictory, so I changed the rule.
- It wrote a muddled expression to choose which commit to cite. I made `commits()` return the latest commit ID instead.
- Its first payroll simulation would have booked November payroll at the old amount, ignoring Siddharth's exit. Showing the corrected amount would reveal his salary by subtraction, so payroll is now projected without an amount.
- My first simulation test expected a payroll event by 18 Nov, but payroll lands on the 28th. That was a mistake in the test, not the code, and I fixed the test.
- It drafted a test that compared managers with a confusing string replace. I rewrote it to state the expected manager plainly.

**What I decided against**
- An LLM layer (D-002, D-008), and LLM-written "new emails" for the simulation (D-010). Both would produce text I can't test or defend.

## 17 Nov (Day 2)

**Tasks given to AI**
- Read the Day 2 folder, list the T3 lines that conflict with the exports (TN-12 to TN-21), and add the Day 2 evidence to the Day 1 notes. As on Day 1, it collected evidence only; the conclusions are mine.
- Add the Day 2 answers (hiring, pulse, attrition, the unnamed engineer, leave on person cards), the worry rules, and the top-three opening view for T6a.
- Draft responses/T6a.md. I chose what to push back on: never cut a 5/5, never pad the list, keep the evidence.

**Where it was wrong / what I changed**
- Its quote of Meera's pause email (`EML-06`) grabbed the subject/date header line, not the sentence in the body. I caught this reading the output and now search the body only.
- It named a test variable `top`, which hid the new `top()` function inside that test. I renamed it.
- I asked for engagement drops "of 0.4 or more". 3.8 − 3.4 is 0.3999… in floating point, so marketing would have been silently missed. The rule rounds before comparing, and a comment explains why.

**How the TRANSCRIPT_NOTES conclusions were made**
- For each conflict, AI laid out two or three readings of the evidence already listed in the note, plus "leave it open". I chose one for every note, and AI wrote my choice up as the conclusion text. Where I didn't accept an option, the note stays open: I haven't accepted "Pria = Priya Nair", and TN-10 waits for Day 3. The verdicts.csv and aliases.csv rows follow directly from those choices.
- Two of my calls changed how the cockpit behaves. TN-17: survey comments now get "I don't have them, ask Deepa", not a refusal. TN-07: the Atlas worry now also cites the festive-season promise to customers.

**Agents**
- AI built cockpit/agents.py and drafted the 14 personas in curation/people.json, using only Day 1–2 facts. I reviewed them. Each persona has one assumption row (A-103 to A-118).
- Its first draft of Priya's assumption cited T1's "Pria" line. I haven't accepted that alias (TN-06), so the citation was removed. A persona must not quietly depend on a mapping I left open.

**What I did not let it do**
- Build any rule that infers who might be job-hunting from personal leave, commit hours or survey scores. Deepa's unnamed engineer stays unnamed (DECISIONS D-006).

## 16 Nov (Day 1)

**Tasks given to AI**
- Extract text from every .docx, .pdf, .xlsx and .eml in the release packs, so I could read them quickly.
- Survey the data room and propose a data model and stack. Draft ARCHITECTURE.md, DECISIONS.md and ASSUMPTIONS.md.
- List the Day 1 transcript lines that conflict with the exports, with the evidence for each (TRANSCRIPT_NOTES.md).
- All four day folders were sent up front, so AI skimmed every one on Day 1 to pick parsers for each file type (xlsx, csv, eml, pdf, docx). Hand-curated content (claims, aliases, notes) only uses a folder on or after its release day.

**Where it was wrong / what I changed**
- It built the answer engine, worry rules and test set (answer.py, worry.py, tests/). Mistakes I caught before committing: it ordered view rows by `rowid`, which SQLite views don't have, so I exposed `seq` instead. Its month labels were made by slicing the formatted date ("8 Apr 2026"[3:] gave "pr 2026"). And its "hiring paused" search matched any email containing "pausing", which would have counted Sneha's "pausing the Atlas perf tickets" as a hiring freeze once Day 3 is released.
- It chained the commit after the test run in a way that let a commit through while a test was failing. The failure was its own AI_LOG entry citing a record ID that doesn't exist. I fixed the entry, amended the unpushed commit, and now run the tests separately before each commit.
- Its loader keyed spreadsheet rows on the first column whenever that column was unique, and otherwise fell back to row numbers. The GL's first column is the transaction date, which repeats, so every GL row was keyed by row number (GL:r5 and so on). Meanwhile the docs it wrote cited `GL:JV-0846` and `GL:PAY-APR`, which didn't exist. I changed the rule to "first column that is fully unique" (the voucher, for the GL) and added a test that every record ID cited in the .md files exists.
- Its first ARCHITECTURE.md draft named a file that is only released on Day 3. I replaced it with a generic description, so the Day 1 commit doesn't rely on material that isn't released yet.

**What I did not let it do**
- Decide any conflict. TRANSCRIPT_NOTES entries hold the AI-collected evidence, and every "Conclusion" line is mine.
