"""Schema, IST time handling, and the one point-in-time gate: connect(as_of)."""
import sqlite3
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "veloxa.db"
IST = timezone(timedelta(hours=5, minutes=30))

# Default trust when sources disagree (lower = more trusted). A lower tier can still win
# a specific conflict; that reasoning lives in TRANSCRIPT_NOTES.md, not here.
TIER = {"export": 1, "document": 2, "email": 3, "brief": 3, "transcript": 4, "voice_note": 5}

SCHEMA = """
CREATE TABLE source (
  id TEXT PRIMARY KEY,          -- short citable name: GL, KEKA, T2, EML-08
  path TEXT NOT NULL,
  kind TEXT NOT NULL,           -- key of TIER
  released_at TEXT NOT NULL,    -- IST ISO; when the cockpit learned it
  restricted INTEGER NOT NULL   -- 1 = individual-level pay data, never shown row by row
);
CREATE TABLE record (
  id TEXT PRIMARY KEY,          -- what answers cite: GL:JV-0846, T2:#4, EML-08
  source_id TEXT NOT NULL REFERENCES source(id),
  locator TEXT,                 -- sheet!row, paragraph, page
  occurred_at TEXT,             -- IST ISO; when it happened in the company, if known
  text TEXT NOT NULL,
  data TEXT                     -- row as JSON, for exports
);
CREATE TABLE entity (
  id TEXT PRIMARY KEY,          -- VX007, EXT-*, VEN-*, PRJ-*
  kind TEXT NOT NULL,           -- person | contractor | vendor | project
  name TEXT NOT NULL,
  record_id TEXT NOT NULL REFERENCES record(id)   -- evidence it exists
);
CREATE TABLE alias (
  alias TEXT NOT NULL,          -- lower-cased spelling as seen
  entity_id TEXT NOT NULL REFERENCES entity(id),
  confidence TEXT NOT NULL,     -- H | M | L
  record_id TEXT NOT NULL REFERENCES record(id),  -- where this spelling was seen
  note TEXT
);
"""


def to_ist(v, end_of_day=False):
    """date/datetime/ISO string -> IST ISO string. Naive values are taken as IST (A-001)."""
    if isinstance(v, str):
        v = v.strip().replace("Z", "+00:00")
        v = datetime.fromisoformat(v) if len(v) > 10 else date.fromisoformat(v)
    if not isinstance(v, datetime):
        v = datetime.combine(v, time(23, 59, 59) if end_of_day else time.min)
    if v.tzinfo is None:
        v = v.replace(tzinfo=IST)
    return v.astimezone(IST).isoformat(timespec="seconds")


def connect(as_of=None):
    """Open the DB with temp views v_record / v_entity / v_alias that only contain
    what had been released by `as_of` (default: now). All reads go through these views."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
      CREATE TEMP TABLE asof (t TEXT NOT NULL);
      CREATE TEMP VIEW v_record AS
        SELECT r.*, s.kind, s.released_at, s.restricted FROM record r JOIN source s ON s.id = r.source_id
        WHERE s.released_at <= (SELECT t FROM asof);
      CREATE TEMP VIEW v_entity AS SELECT * FROM entity WHERE record_id IN (SELECT id FROM v_record);
      CREATE TEMP VIEW v_alias  AS SELECT * FROM alias  WHERE record_id IN (SELECT id FROM v_record);
    """)
    conn.execute("INSERT INTO asof VALUES (?)", (to_ist(as_of or datetime.now(IST), end_of_day=True),))
    return conn
