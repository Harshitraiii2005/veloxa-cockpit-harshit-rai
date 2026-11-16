# Architecture

Status: v1, Mon 16 Nov 2026 (Day 1). I'll update this file as the design changes. The history of each change is in git.

## Goal in one line

Ananya asks one question and gets a short, true answer. The answer cites the records behind it, states a confidence level, and says "I don't know" or "the sources disagree" when that is the honest answer. Everything the cockpit knows is limited to what had been **released** by the date being asked about.

## Shape

```
Veloxa_Hackathon_Release_Packs/      raw material, never edited
        │
        ▼  cockpit/load.py            one parser per file type (xlsx, csv, eml, pdf, docx, txt)
┌──────────────────────── veloxa.db (SQLite, rebuilt from scratch on every setup) ─────┐
│ source    file, kind, system, released_at, reliability tier                          │
│ record    one atomic item (xlsx row, email, transcript bullet, PDF doc) + raw JSON   │
│ entity    people, contractors, vendors, projects (canonical IDs)                      │
│ alias     every spelling seen  ->  entity  (+ confidence, evidence)                  │
│ claim     subject / metric / period / value, pointing at a record                    │
│ resolution  which claim I believe for a conflict  ->  TRANSCRIPT_NOTES entry          │
└──────────────────────────────────────────────────────────────────────────────────────┘
        ▲                         ▲
        │ curation/*.csv          │  every read goes through visible(as_of)
        │ (hand-written:          │
        │  aliases, transcript    ├── cockpit/answer.py   question -> handler -> Answer
        │  claims, resolutions)   ├── cockpit/worry.py    ranked "what should I worry about"
        │                         ├── cockpit/agents.py   14 people, grounded + invented persona
        │                         └── cockpit/cli.py, web page (stdlib http.server)
                                  tests/  25+ questions with expected answers, one command
```

## Data model

**Sources and records.** Every file in the four day folders is a `source`. Each source has a `released_at` set from its folder: Day 1 = 16 Nov, Day 2 = 17 Nov, Day 3 = 18 Nov, Day 4 = 19 Nov, all at 10:00 IST. Each source is split into `record`s: one per spreadsheet row, email, transcript bullet or PDF document. A record ID is what the cockpit cites, so I keep it readable: `GL:JV-0846`, `KEKA:VX013`, `PAYROLL:r39`, `EML-08`, `T2:#4`, `BOARD-APRJUN`.

**Two times on every record (bitemporal).**
- `released_at`: when the cockpit learned it. This drives "what did we know on date X?".
- `occurred_at`: when it happened in the company (txn date, email date, ticket created). This drives "what was the GA date on 1 Sep?".

Every query goes through one function, `visible(as_of)`, which keeps only records with `released_at <= as_of`. This is the only place point-in-time is enforced, so later material can't leak through a side door. A resolution only applies when every record it relies on is visible at that date.

**Reliability tiers** (default trust, not a verdict): system export > formal document (board update, invoice, letter) > email > call transcript > voice note. The brief says exports are better but quirky and transcripts are often misheard. A lower tier can still win a specific conflict. When it does, the reason is written down.

**Entities and aliases.** People are keyed by Keka Emp ID (`VX007`). People who aren't in Keka (contractors, for example) get `EXT-*` IDs. Vendors get `VEN-*` and projects `PRJ-*`. Every spelling seen anywhere (`Pria`, `PN`, `pnair@users.noreply.github.com`, `Kartik`, `Joho books`) is an `alias` row with confidence and evidence. This is the provided Entity_Resolution worksheet in table form. I can export it back to the xlsx for the final session.

**Claims and conflicts.** Numbers people state (ARR, burn, headcount, GA date, attrition) become `claim` rows. Exports are parsed in code. Transcript claims are written by hand in `curation/claims.csv`, because deciding what a garbled line "said" is a judgement I want visible in a diff. When two visible claims share subject + metric + period and their values differ, that is a **conflict**. If I've recorded a resolution, the cockpit answers with it and cites both sides. If I haven't, it says "the sources disagree".

## Cockpit answers

The answer path is **deterministic first**:

1. A small router matches the question to a topic handler (headcount, ARR, burn, Atlas GA, hiring, payroll, on-call, a person, and so on).
2. The handler queries `visible(as_of)` and returns an `Answer(text, citations, confidence, status)`, where `status` is one of `answered | unknown | disagree | refused`.
3. Confidence comes from the evidence, not from model tone. Rough rule: High = an export confirms it with no live conflict. Medium = a single document, or a resolved conflict. Low = transcript only.
4. If no handler matches or there is no evidence, the answer is "I don't know", plus what record would settle it.

**Optional LLM layer** (only if `LLM_API_KEY` is set): for questions no handler covers, the LLM gets the visible records that match and must answer only from them, citing record IDs. I check every cited ID against `visible(as_of)`. If an ID doesn't exist or comes from the future, the answer is discarded and the cockpit says "I don't know". The tests and the one-command run never need a key.

**Refusals** (full list in DECISIONS.md). The cockpit refuses individual salaries; the CFO says only totals may reach Ananya (T2). It refuses survey comments for teams under the anonymity threshold. It refuses anything not in the data room, rather than guessing.

## "What should I worry about"

`worry.py` is a list of plain rule functions. Each one looks at visible records and returns `(title, severity 1–5, confidence, evidence IDs)`. Examples: a slipped launch date, single-person dependency, payroll anomalies, spend vs freeze contradictions, on-call load. Items are ranked by severity × confidence. Each item cites its records, and a rule with no evidence on that date returns nothing.

## The 14 people as agents

The 14 are the Keka employees in Engineering (5), Finance (3), People & Ops (3) and Marketing (3), which matches the brief's "14 people across engineering, finance, HR and marketing". Each agent has two layers:

- **Grounded facts**, computed from records at `as_of`: role, manager, tickets, commits, incidents, leave, emails. These are never stored by hand, so they can't drift from the data.
- **Persona** in `curation/people/*.json`: voice, worries, life outside work. Every invented item carries an assumption ID (`A-0xx`) that points to ASSUMPTIONS.md.

Agent memory is the set of visible records that mention them plus their persona. No free-running memory, so an agent can't "remember" something the record contradicts. If a key is set, the LLM role-plays the agent with that context. Offline, the agent answers from its grounded facts in a templated voice.

## Point-in-time

`--as-of 2026-11-17` (CLI) or `?as_of=` (web) works on every question, the worry list and agents. The default is the current time, so the cockpit only "knows" the day folders released so far. Tests pin `as_of` explicitly and include cases where the right answer changes between two dates.

## Tests

`tests/questions.json` holds at least 25 cases `{question, as_of, expect_status, must_contain, must_cite}`. A stdlib runner prints a pass/fail table and returns non-zero on failure. At least 5 cases must come back `unknown`, `disagree` or `refused`.

## Stack and why

- **Python 3.12, SQLite (stdlib).** One file DB, rebuilt from the raw packs on every run, so there is no migration story to defend.
- **Dependencies:** `openpyxl` (xlsx) and `pypdf` (pdf). `.eml`, `.csv` and `.docx` are parsed with the stdlib. An LLM SDK is optional.
- **One command:** `./run.sh` creates a venv, installs requirements, builds `veloxa.db`, runs the tests, and starts the cockpit.

## Known open questions (will change this doc)

- How to treat a document that copies other evidence (for example a printout of the same email threads): as duplicate evidence, or as one source?
- Whether event-time questions before 16 Nov should answer from `occurred_at`, or say nothing was known yet. The current plan is to support both and label which one is used.
- Simulation after 31 Oct (stretch): not designed yet.
