# Veloxa CXO Cockpit

Ananya Rao (CEO, Veloxa Technologies) asks one question and gets a short answer. Each answer cites the records it rests on, states a confidence level, and admits when the sources disagree or don't say. It is built for the Hiyaku Systems hackathon (16–20 Nov 2026), on top of the Veloxa release packs. Veloxa is a fictional company.

**Status:** Day 1. Architecture is done, and the loader builds `veloxa.db` from all four folders with release-date gating. See [ARCHITECTURE.md](ARCHITECTURE.md).

## One command

```bash
./run.sh
```

This needs Python 3.10 or later. The script creates `.venv`, installs `requirements.txt`, rebuilds `veloxa.db` from `Veloxa_Hackathon_Release_Packs/`, and then runs the cockpit.

## Running the test set

```bash
./run.sh test
```

Today this runs the loader and point-in-time checks. The cockpit question set (25+ questions, at least 5 refusal or uncertainty cases) is added later this week.

## Repo map

| Path | What |
|---|---|
| `Veloxa_Hackathon_Release_Packs/` | Raw material as received. Never edited. |
| `cockpit/` | Loader, data model, cockpit, worry list, agents |
| `curation/` | Hand-written judgements: aliases, transcript claims, resolutions |
| `tests/` | Test questions with expected answers |
| `ARCHITECTURE.md` | Design |
| `DECISIONS.md` | Choices that could go either way |
| `ASSUMPTIONS.md` | Assumptions, with source lines and confidence |
| `TRANSCRIPT_NOTES.md` | Suspected mishearings and contradictions, with my conclusions |
| `AI_LOG.md` | What AI did, where it was wrong, what I changed |
| `responses/` | Written responses to the CEO voice notes (T6a–T6d) |
