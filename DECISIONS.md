# Decisions

These are choices I could defend either way. Each entry says what I picked, the alternative, and why.

## D-001 · Storage: SQLite, rebuilt on every run (16 Nov)
**Picked:** a single `veloxa.db`, deleted and rebuilt from the raw packs on every setup.
**Alternative:** JSON files, or a long-lived DB with migrations.
**Why:** The data is small (a few thousand rows). SQL makes cross-source joins easy to read and explain. Rebuilding from raw files every time means the DB can't drift from the evidence, and there is no migration code to defend.

## D-002 · Answers: deterministic handlers first, LLM optional (16 Nov)
**Picked:** topic handlers that query the DB and build the answer, with citations and confidence computed from the evidence. An LLM is used only for questions no handler covers, and only when a key is present. Its citations are checked against `visible(as_of)`.
**Alternative:** LLM-first RAG over all records.
**Why:** The grading cares whether answers are *true against the data room* and admit uncertainty. A handler is something I can read and test, and it gives the same answer every time. An LLM sounds confident whether or not it's right. The fresh-clone run and the test set must also work without an API key.

## D-003 · Transcript claims are hand-curated, not machine-extracted (16 Nov)
**Picked:** `curation/claims.csv`. I write one row per number or fact a transcript asserts, with the words as heard.
**Alternative:** have an LLM extract claims.
**Why:** Deciding what "forty-two crore, maybe forty-five" means is the exact judgement I'm assessed on. It should be visible in a diff and owned by me. There are only about 6 calls and 4 voice notes, so writing them by hand is affordable.

## D-004 · Point-in-time filters on release date, not event date (16 Nov)
**Picked:** `visible(as_of)` keeps only records whose folder was released (10:00 IST on its day) by `as_of`. A date-only `as_of` means the end of that day in IST.
**Alternative:** filter on when the event happened (`occurred_at`).
**Why:** The brief asks "what did we know on date X?, using the release dates". Every export was taken on 31 Oct, so an event-date filter would leak a 31 Oct snapshot into "what did we know" questions. Event dates are still stored, for questions like "what was the GA date on 1 Sep".

## D-005 · Agent memory = visible records + a fixed persona (16 Nov)
**Picked:** no free-running memory. An agent's context is built fresh each time from the records that mention them (filtered by `as_of`), plus a persona file whose invented details each carry an assumption ID.
**Alternative:** let agents keep a growing conversation memory.
**Why:** A growing memory can drift away from the records, and the brief requires agents to stay consistent with them.

## D-006 · What the cockpit refuses (16 Nov, will grow)
- **Individual salaries.** T2: Meera says salaries "must never show up in anything Ananya sees, only totals". Totals are allowed.
- **Survey comments for small teams.** The cockpit will not try to reconstruct them. *(revised 17 Nov, TN-17)* It no longer refuses outright. It says it doesn't have them and that Deepa wants Ananya to see them, so ask her.
- **Anything outside the data room.** It answers "I don't know" and names the record that would settle it.
- *(added 17 Nov)* **Guessing at people nobody named.** When a leader mentions an unnamed person (for example T3: "one engineer I'm worried about"), the cockpit says nobody was named. It does not infer who from leave, commits or survey scores.

## D-007 · Raw data stays out of the public repo (16 Nov)
**Picked:** `Veloxa_Hackathon_Release_Packs/` is git-ignored. `run.sh` unzips `Veloxa_Hackathon_Release_Packs.zip` if it is in the repo root, and stops with a clear message if neither the folder nor the zip is there.
**Alternative:** commit the packs, so a fresh clone runs with no extra step.
**Why:** The material was sent as confidential, and the rules say not to share it with other candidates. A public repo would do exactly that. Graders already have the zip, so the cost is copying one file.

## D-008 · Agents are offline: grounded facts plus fixed persona lines (17 Nov)
**Picked:** each agent answers from facts computed from records at `as_of` (cited by record ID), plus a few fixed persona lines in `curation/people.json` (cited by assumption ID). No LLM.
**Alternative:** an LLM role-plays each person, using their records as context.
**Why:** The graders' fresh clone has no API key, and answers must be testable and stay consistent with the records. Fixed persona text can't drift and can be reviewed in a diff. The cost is that the agents are less conversational: an unmatched question gets "I'd rather not guess". If there's time, an optional LLM layer can rephrase these answers, using the same citation check as the cockpit.

## D-009 · The email printout PDF is not loaded (18 Nov)
**Picked:** skip `Email_Printouts.pdf` and load the 11 .eml files.
**Alternative:** load both, or load only the printout.
**Why:** I checked the printout line by line against the .eml files: same 11 threads, same text, with times in IST. Loading both would make every email count twice as evidence. The .eml files keep full headers (Message-ID, Cc, timezone), so they are the better copy. If a later printout ever differed from its .eml, the difference itself would become a TRANSCRIPT_NOTES entry.

