# Veloxa CXO Cockpit

Ananya Rao (CEO, Veloxa Technologies) asks one question and gets a short answer. Each answer cites the records it rests on, states a confidence level, and admits when the sources disagree or don't say. It is built for the Hiyaku Systems hackathon (16–20 Nov 2026), on top of the Veloxa release packs. Veloxa is a fictional company.

**Status:** Day 2. The loader builds `veloxa.db` from all four folders with release-date gating. The cockpit answers questions on the Day 1 and Day 2 data and opens on the top three worries (T6a). See [ARCHITECTURE.md](ARCHITECTURE.md).

## One command

```bash
cp /path/to/Veloxa_Hackathon_Release_Packs.zip . && ./run.sh
```

The release packs aren't committed, because they were sent as confidential (DECISIONS.md D-007). Copy in the zip from the hackathon email once. After that, `./run.sh` on its own is enough. This needs Python 3.10 or later. The script unzips the packs, creates `.venv`, installs `requirements.txt`, rebuilds `veloxa.db`, and then runs the cockpit.

## Using it

`./run.sh` opens on the top three worries (items new since the day before are marked NEW), then asks for questions. Type `more` to see every worry. You can also run one question at a time:

```bash
.venv/bin/python -m cockpit ask "What is our ARR?"
.venv/bin/python -m cockpit ask "When is Atlas GA?" --as-of 2026-11-16
.venv/bin/python -m cockpit worry --as-of 2026-11-17 --all
```

Every answer ends with a confidence level, a status (`answered`, `unknown`, `disagree` or `refused`) and the record IDs it used. `--as-of` limits the cockpit to what had been released by that date. A question like "what did we know on 15 Nov 2026 about ARR?" sets that date itself.

## Running the test set

```bash
./run.sh test
```

This runs the loader and point-in-time checks, plus the cockpit question set in `tests/questions.json`. Each case gives a question, an `as_of` date, the expected status, words the answer must contain, and records it must cite. An optional `absent` list checks that later material doesn't leak into an earlier answer. There are 26 cases (18 of them refusals, unknowns or disagreements), and a test enforces the brief's minimums of 25 and 5.

## Repo map

| Path | What |
|---|---|
| `Veloxa_Hackathon_Release_Packs/` | Raw material as received. Not committed (D-007); `run.sh` unzips it here. |
| `cockpit/` | Loader, data model, cockpit, worry list, agents |
| `curation/` | Hand-written judgements: aliases, transcript claims, resolutions |
| `tests/` | Test questions with expected answers |
| `ARCHITECTURE.md` | Design |
| `DECISIONS.md` | Choices that could go either way |
| `ASSUMPTIONS.md` | Assumptions, with source lines and confidence |
| `TRANSCRIPT_NOTES.md` | Suspected mishearings and contradictions, with my conclusions |
| `AI_LOG.md` | What AI did, where it was wrong, what I changed |
| `responses/` | Written responses to the CEO voice notes (T6a–T6d) |
