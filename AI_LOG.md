# AI log

Tool: an AI coding assistant in VS Code. Entries are newest first.

## 17 Nov (Day 2)

**Tasks given to AI**
- Read the Day 2 folder, list the T3 lines that conflict with the exports (TN-12 to TN-21), and add the Day 2 evidence to the Day 1 notes. As on Day 1, it collected evidence only; the conclusions are mine.
- Add the Day 2 answers (hiring, pulse, attrition, the unnamed engineer, leave on person cards), the worry rules, and the top-three opening view for T6a.
- Draft responses/T6a.md. I chose what to push back on: never cut a 5/5, never pad the list, keep the evidence.

**Where it was wrong / what I changed**
- Its quote of Meera's pause email (`EML-06`) grabbed the subject/date header line, not the sentence in the body. I caught this reading the output and now search the body only.
- It named a test variable `top`, which hid the new `top()` function inside that test. I renamed it.
- I asked for engagement drops "of 0.4 or more". 3.8 − 3.4 is 0.3999… in floating point, so marketing would have been silently missed. The rule rounds before comparing, and a comment explains why.

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
