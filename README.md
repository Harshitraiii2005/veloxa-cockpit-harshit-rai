# Veloxa CXO Cockpit

Ananya Rao (CEO, Veloxa Technologies) asks one question and gets a short answer. Each answer cites the records it rests on, states a confidence level, and admits when the sources disagree or don't say. It is built for the Hiyaku Systems hackathon (16–20 Nov 2026), on top of the Veloxa release packs. Veloxa is a fictional company.

**Status:** Final. Code freeze is Fri 20 Nov 2026, 18:00 IST. Everything below runs on all four packs. Every CEO voice note (T6a to T6d) has a written response in `responses/`.

- **Cockpit:** one question gives a short answer with a status (`answered`, `unknown`, `disagree`, `refused`), a confidence level, and the record IDs behind it.
- **Worry list:** opens on the top three; items new since yesterday are marked NEW.
- **Point in time:** `--as-of` (or "what did we know on <date>" in the question) limits answers to what had been released.
- **14 agents:** interview the Engineering, Finance, People & Ops and Marketing staff. Their facts come from records; their lives are invented and logged.
- **After 31 Oct (stretch):** a labelled, rate-based projection of activity.

## Reviewing in 10 minutes

1. `./run.sh`: the cockpit opens on today's top three worries. Try a question, then `@sneha what's your week like?`.
2. `responses/`: the four CEO voice notes, each with what changed and where I pushed back.
3. `TRANSCRIPT_NOTES.md`: the conflicts I'd defend first:
   - TN-22: "Snehal" is a contractor, not Sneha.
   - TN-23: Jira's 15 Dec date over "still September-ish".
   - TN-08: the February payroll.
   - TN-26: "nobody is overloaded" vs the work data.
4. Point in time: ask "When is Atlas GA?" with `--as-of` 2026-11-17, 2026-11-18 and 2026-11-19, and watch the answer change only when new material is released.
5. `./run.sh test`: 46 questions plus unit checks.

## One command

```bash
cp /path/to/Veloxa_Hackathon_Release_Packs.zip . && ./run.sh
```

The release packs aren't committed, because they were sent as confidential (DECISIONS.md D-007). Copy in the zip from the hackathon email once. After that, `./run.sh` on its own is enough. This needs Python 3.10 or later. The script unzips the packs, creates `.venv`, installs `requirements.txt`, rebuilds `veloxa.db`, and then runs the cockpit.

## Using it

`./run.sh` opens on the top three worries, then takes questions. Type `more` to see every worry, or `@name question` to talk to one of the 14 people. A blank line quits.

```bash
.venv/bin/python -m cockpit ask "When is Atlas GA?"
.venv/bin/python -m cockpit ask "What did we know on 17 Nov 2026 about the Atlas GA date?"
.venv/bin/python -m cockpit ask "Is engineering overloaded?" --as-of 2026-11-18
.venv/bin/python -m cockpit worry --as-of 2026-11-18 --all
.venv/bin/python -m cockpit agent --list
.venv/bin/python -m cockpit agent Sneha "What's your week like?"
.venv/bin/python -m cockpit simulate --as-of 2026-11-30
```

Things to try:
- Ask for someone's salary: it's refused.
- Ask "Who is Snehal?" on 17 Nov, then on 18 Nov.
- Ask about marketing spend: the sources disagree, and the answer says why it can't be settled.
- Ask "What does Priya's resignation do to version three?" with `--as-of 2026-11-18`, then with `--as-of 2026-11-19`.
- Ask "Can you rank everyone by who's likely to quit?", then ask "Who are our key-person dependencies?"

## Running the test set

```bash
./run.sh test
```

This runs the loader and point-in-time checks, plus the cockpit question set in `tests/questions.json`. Each case gives a question, an `as_of` date, the expected status, words the answer must contain, and records it must cite. An optional `absent` list checks that later material doesn't leak into an earlier answer. There are 46 cases (22 of them refusals, unknowns or disagreements), and a test enforces the brief's minimums of 25 and 5. Unit tests also cover the release gate, the agents, reporting-line moves and the simulation.

## Repo map

| Path | What |
|---|---|
| `Veloxa_Hackathon_Release_Packs/` | Raw material as received. Not committed (D-007); `run.sh` unzips it here. |
| `cockpit/` | Loader, data model, cockpit, worry list, agents |
| `tests/` | Test questions with expected answers |
| `ARCHITECTURE.md` | Design |
| `DECISIONS.md` | Choices that could go either way |
| `ASSUMPTIONS.md` | Assumptions, with source lines and confidence |
| `TRANSCRIPT_NOTES.md` | Suspected mishearings and contradictions, with my conclusions |
| `AI_LOG.md` | What AI did, where it was wrong, what I changed |
| `responses/` | Written responses to the CEO voice notes (T6a–T6d) |
| `curation/` | My judgements as data: claims, verdicts, aliases, contractors, reporting-line moves, the 14 personas |
