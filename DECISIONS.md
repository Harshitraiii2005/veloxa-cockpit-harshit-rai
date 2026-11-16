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
- **Survey comments for small teams.** The cockpit will not try to reconstruct them.
- **Anything outside the data room.** It answers "I don't know" and names the record that would settle it.

## D-007 · Raw data in the repo (16 Nov, pending)
**Open:** whether the release packs are committed to the public repo. The fresh-clone run needs them, but the material was sent as confidential.
