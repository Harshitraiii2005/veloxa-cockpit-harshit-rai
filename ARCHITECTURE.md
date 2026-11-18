# Architecture

Status: v4, Thu 19 Nov 2026 (Day 4). v1 was committed on Day 1. "Changed since v1" at the end lists what moved and why, and git has the full history.

## Goal in one line

Ananya asks one question and gets a short, true answer. The answer cites the records behind it, states a confidence level, and says "I don't know" or "the sources disagree" when that is the honest answer. Everything the cockpit knows is limited to what had been **released** by the date being asked about.

## Shape

```
Veloxa_Hackathon_Release_Packs/      raw material, never edited, not committed (D-007)
        │
        ▼  cockpit/load.py            one parser per file type (xlsx, csv, eml, pdf, docx, txt)
┌──────────── veloxa.db (SQLite, rebuilt from scratch on every run) ─────────────────────┐
│ source      file, kind (export/document/email/transcript/voice_note), released_at      │
│ record      one item: a sheet row, an email, a transcript paragraph, a PDF             │
│ entity      people (Keka Emp ID) and contractors (EXT-*)                               │
│ alias       every spelling seen -> entity, with confidence and evidence                │
│ claim       a number or date a source states, copied as stated   (curation/claims.csv) │
│ verdict     my call on a conflicting claim -> a TN-xx entry      (curation/verdicts.csv)│
│ org_change  dated reporting-line moves (T6b)                     (curation/org_changes)│
└──────────────────────────────────────────────────────────────────────────────────────────┘
        ▲                         ▲
        │ curation/               │  every read goes through connect(as_of) -> v_* views
        │ (my judgements,         │
        │  in reviewable CSV/JSON)├── cockpit/answer.py    question -> topic handler -> Answer
        │                         ├── cockpit/worry.py     ranked worries, top 3 on open (T6a)
        │                         ├── cockpit/agents.py    the 14 people (records + persona)
        │                         ├── cockpit/simulate.py  projected activity after 31 Oct (stretch)
        │                         └── cockpit/__main__.py  CLI: ask, worry, agent, simulate, prompt
                                  tests/  questions.json (38 cases) + unit checks, ./run.sh test
```

## Data model

**Sources and records.** Every file in the four day folders is a `source`. Its `released_at` comes from its folder: 16, 17, 18 and 19 Nov, each at 10:00 IST (A-001). Each source is split into `record`s, and a record ID is what answers cite, so IDs are readable: `GL:JV-0846`, `KEKA:VX013`, `JIRA:Atlas_GA`, `EML-08`, `T2:#4`, `BOARD-APRJUN`. A spreadsheet row is keyed by the first column whose values are all unique, or by row number if there isn't one. The email printout PDF is skipped as a duplicate of the .eml files (D-009). Individual payroll rows are flagged `restricted`.

**Two times on every record.** `released_at` is when the cockpit learned it, and it drives "what did we know on date X?". `occurred_at` is when it happened (in IST), and it drives event questions such as late-night commits.

**One point-in-time gate.** `connect(as_of)` in `cockpit/db.py` creates temp views (`v_record`, `v_entity`, `v_alias`, `v_claim`, `v_verdict`, `v_org_change`). Each view keeps only rows whose evidence was released by `as_of`, and code never reads the base tables. A verdict also has its own `decided_on`, so a call I made with Day 3 evidence can't change a Day 2 answer.

**Reliability tiers** set the default trust: export > document > email/brief > transcript > voice note. They only break ties. Who is right in a conflict is never decided in code.

**Claims, conflicts and verdicts.** For each metric, the best claim is the latest dated one, with the more trusted tier winning a tie. Dated values for other dates form a trend, and an older dated record with no value counts as superseded. A claim **conflicts** with the best one when it is undated or has no usable value and differs by more than 10%. A conflict stays "the sources disagree" until I write a verdict:
- `misheard`, `wrong` or `different-measure`: the claim is set aside, still cited, with its TN reference.
- `cannot-settle`: the claim stays a disagreement, labelled "the records can't settle this".

**Entities and aliases.** People are keyed by Keka Emp ID. Aliases are generated from Keka (full name, email, first name and "P. Nair" form when unique), plus my accepted mappings in `curation/aliases.csv` ("Pria", "Snehal" -> the contractor, Priya's GitHub address, and so on). Jira initials are matched to Keka initials only when they're unique (A-009).

## Cockpit answers

There is a deterministic router of topic handlers. Each reads the views and returns `Answer(text, status, confidence, cites)`, with status `answered | unknown | disagree | refused`. Confidence comes from the tier of the evidence, and drops one level when a disagreement is still open. The topics are pay (checked first, so a refusal can't be bypassed), the unnamed engineer, ARR, burn, runway, customers, hiring, headcount, incidents/on-call, Atlas, pulse, engineering workload, attrition, people, and marketing spend. A question that matches no topic, or has no evidence on that date, gets "I don't know". "What did we know on <date>" in the question sets the date itself.

There is **no LLM layer**. v1 planned an optional one; I dropped it (see D-002 and D-008) because every answer has to be testable and run without a key.

## "What should I worry about"

`worry.py` is a list of plain rule functions over the views. Each yields `Worry(severity, title, why, confidence, cites)`, and a rule with no evidence on a date yields nothing. Ranking is severity first, then confidence. When the cockpit opens it shows the top three. Any extra 5/5 items are always shown, the list is never padded, and items that weren't on the previous day's list are marked NEW (T6a). The rules are:
- Atlas slipped or undated
- one person holding 40% or more of open Atlas work
- backend hiring paused after a recruiter advance
- engagement drops of 0.4 or more
- someone on call in 90% or more of weeks
- a joiner paid for a full month
- lookalike vendors within one cost centre
- leavers, and the work they own
- leaders' figures that don't match the records
- *(19 Nov)* a reported resignation by the person holding most of the open work, which raises the load rule to 5/5

## The 14 people as agents

The 14 are fixed by Emp ID: the persona file `curation/people.json`, matching A-002. They are not fixed by department, so moving people around (T6b) never drops an agent. An answer is built fresh each time from:
- **grounded facts** computed at `as_of`: role, manager (effective-dated), reports, reqs, emails, leave, Jira points, commits, on-call weeks and incidents;
- **persona lines** (work, life, mood, leave note), each cited by one assumption ID (A-103 to A-118).

Pay is refused. Quitting is discussed only when a record shows a resignation (a Keka exit date, or since 19 Nov a resignation reported by the CEO and shown as reported, A-016). "What did you do this week?" answers from the simulation and says so. There is no free-running memory (D-005), and no LLM (D-008).

## Day 4: resignations and dependencies (T6c, T6d)

A resignation reported only in a voice note is a claim (`resigned:VX007`, `notice:VX007`). It is shown as "reported" with the notice "unconfirmed", next to Keka's 31 Oct "Active". The Atlas answer adds its impact: open points held, share of atlas-engine commits, and the rest of the team's pace. It gives no new GA date. Instead of a quit ranking (refused, D-011), `dependencies()` lists where the work rests on one person: 40% or more of open Jira points, 60% or more of a repo's commits, 90% or more of on-call weeks, 90% or more of ledger entries.

## Reporting lines (T6b)

`org_change` rows record who moves, to whom, from when, and the source record. `manager_of()` reads the line as at the date asked about. An undated move is shown as "announced" and changes nothing. Nothing guesses a date or invents a person.

## After 31 Oct (stretch)

`simulate.py` is a seeded projection from measured rates: commits, the late-night share, the on-call swap, Jira pace, and recurring ledger lines (D-010, A-014). It is computed on the fly, never stored or cited, and always labelled. The Atlas answer adds a straight-line finish date at the pace since April (A-015).

## Tests

`./run.sh test` runs everything with the stdlib `unittest`:
- 46 question cases in `tests/questions.json`. Each has an `as_of`, an expected status, words the answer must contain, records it must cite, and an optional `absent` list that catches later facts leaking into earlier answers. 22 of the cases are refusals, unknowns or disagreements, and a test enforces the brief's minimums of 25 and 5.
- unit checks for the release gate, docs citing only real record IDs, the agents, reporting lines, and the simulation.

## Stack and why

- **Python 3.10+ and SQLite (stdlib).** The DB is rebuilt from the raw packs on every run, so there is nothing to migrate.
- **Two dependencies:** `openpyxl` and `pypdf`. Email, CSV and docx are parsed with the stdlib.
- **One command:** `./run.sh` unzips the packs if needed, creates the venv, installs, builds the DB, and opens the cockpit. `./run.sh test` runs the tests.

## Changed since v1 (16 Nov)

| What | v1 plan | Now | Why |
|---|---|---|---|
| Conflict handling | one "resolution" per conflict | a verdict per claim, plus `cannot-settle` | some claims are set aside for different reasons; TN-27 can't be settled |
| LLM layer | optional, behind a key | not built | answers must be testable and keyless (D-002, D-008) |
| Who the 14 are | department filter | fixed Emp IDs | T6b: moving people must not drop agents |
| Reporting lines | Keka only | Keka plus dated `org_change` | T6b |
| Email printout | open question | skipped as a duplicate | D-009 |
| Event-time questions before 16 Nov | open question | answered "nothing released yet"; event dates are used inside answers (commit hours, GA history) | the brief defines "what did we know" by release date |
| After 31 Oct | not designed | rate-based projection | D-010 |
| Web page | planned | not built; the CLI opens on the top three | no requirement needed it; time went to the must-haves |
