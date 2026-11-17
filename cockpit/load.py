"""Rebuild veloxa.db from the raw release packs.  Run: python -m cockpit.load"""
import csv
import json
import re
import sqlite3
import zipfile
from datetime import date, datetime
from email import policy
from email.parser import BytesParser
from html import unescape

import openpyxl
from pypdf import PdfReader

from .db import DB, ROOT, SCHEMA, to_ist

PACKS = ROOT / "Veloxa_Hackathon_Release_Packs"
CURATION = ROOT / "curation"

# A-001: each day folder is released at 10:00 IST on its day.
RELEASED = {
    "Day1_Mon_16Nov": "2026-11-16T10:00",
    "Day2_Tue_17Nov": "2026-11-17T10:00",
    "Day3_Wed_18Nov": "2026-11-18T10:00",
    "Day4_Thu_19Nov": "2026-11-19T10:00",
}

# Short, citable source IDs. Unlisted files fall back to: T1/T6a for transcripts,
# EML-01 for emails, else the file stem.
SHORT = {
    "Candidate_Brief.docx": "BRIEF",
    "README.txt": "README",
    "Employee_Master.xlsx": "KEKA",
    "GL_Export_Apr-Sep_2026.xlsx": "GL",
    "Payroll_Register_Jan-Mar_2026.xlsx": "PAYROLL",
    "Board_Update_Apr-Jun_2026.pdf": "BOARD-APRJUN",
    "Board_Update_Jul-Sep_2026.pdf": "BOARD-JULSEP",
    "Leave_Register.xlsx": "LEAVE",           # Day 2
    "Hiring_Tracker.xlsx": "HIRE",
    "Pulse_Survey.xlsx": "PULSE",
    "Resignation_Letter_SM.pdf": "RESIGN-SM",
}
RESTRICTED = {"PAYROLL"}  # D-006: individual salaries never reach the CEO row by row
SKIP_DIRS = {"templates"}  # blank worksheets for my own use, not evidence


def plain(v):
    if isinstance(v, datetime):
        return v.date().isoformat() if v.time() == datetime.min.time() else v.isoformat()
    return v


def first_date(values):
    """First value that is a date, or an ISO-looking date string -> IST ISO."""
    for v in values:
        if isinstance(v, (date, datetime)):
            return to_ist(v)
        if isinstance(v, str) and re.match(r"\d{4}-\d{2}-\d{2}", v):
            return to_ist(v)
    return None


def as_line(data):
    return "; ".join(f"{k}: {v}" for k, v in data.items() if v not in (None, ""))


def table_records(sid, rows, sheet=""):
    """rows: [(row_number, values)]. A one-cell first row is a title line, kept as its own record."""
    rows = [(n, r) for n, r in rows if any(c not in (None, "") for c in r)]
    if sum(c not in (None, "") for c in rows[0][1]) == 1:
        yield f"{sid}:title", f"{sheet}!{rows[0][0]}", None, str(rows[0][1][0]), None
        rows = rows[1:]
    (_, header), body = rows[0], rows[1:]
    # Key = first column whose values are all present and unique (Emp ID, Voucher, Key, sha), else row number.
    cols = list(zip(*(r for _, r in body)))
    key_col = next((i for i, c in enumerate(cols) if None not in c and len(set(c)) == len(c)), None)
    for n, r in body:
        data = {h: plain(v) for h, v in zip(header, r) if h is not None}
        key = plain(r[key_col]) if key_col is not None else f"r{n}"
        yield f"{sid}:{key}", f"{sheet}!{n}", first_date(r), as_line(data), data


def xlsx(path, sid):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        yield from table_records(sid, enumerate(ws.iter_rows(values_only=True), 1), ws.title)
    wb.close()


def csv_rows(path, sid):
    with open(path, newline="", encoding="utf-8") as f:
        yield from table_records(sid, enumerate(csv.reader(f), 1))


def eml(path, sid):
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    data = {k: str(msg[k]) for k in ("From", "To", "Cc", "Subject", "Date") if msg[k]}
    body = msg.get_body(preferencelist=("plain",)).get_content().strip()
    yield sid, "", to_ist(msg["Date"].datetime), as_line(data) + "\n\n" + body, data


def pdf(path, sid):
    text = "\n".join(p.extract_text() for p in PdfReader(path).pages).strip()
    yield sid, "", pdf_date(text), text, None


def pdf_date(text):
    """First date written in the document: '8 Jul 2026', '15 September 2026' or '01/10/2026' (dd/mm)."""
    m = re.search(r"\b(\d{1,2} [A-Z][a-z]+ \d{4})\b", text)
    if m:
        for fmt in ("%d %b %Y", "%d %B %Y"):
            try:
                return to_ist(datetime.strptime(m[1], fmt))
            except ValueError:
                pass
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", text)
    return to_ist(date(int(m[3]), int(m[2]), int(m[1]))) if m else None


def docx(path, sid):
    """One record per paragraph: T1:#0 is the title, T1:#1 the recording header, and so on."""
    xml = zipfile.ZipFile(path).read("word/document.xml").decode()
    paras = [unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in xml.split("</w:p>")]
    for i, p in enumerate(p for p in paras if p):
        yield f"{sid}:#{i}", f"para {i}", None, p, None


def txt(path, sid):
    yield sid, "", None, path.read_text(encoding="utf-8").strip(), None


PARSERS = {".xlsx": xlsx, ".csv": csv_rows, ".eml": eml, ".pdf": pdf, ".docx": docx, ".txt": txt}


def kind_of(parts, name):
    if parts[0] == "transcripts":
        return "voice_note" if name.startswith("T6") else "transcript"
    if parts[0] == "brief":
        return "brief"
    if name.endswith(".eml"):
        return "email"
    if name.endswith(".pdf"):
        return "document"
    return "export"


def source_id(path):
    if path.name in SHORT:
        return SHORT[path.name]
    if m := re.match(r"(T\d+[a-z]?)_", path.name):
        return m[1]
    if path.suffix == ".eml":
        return f"EML-{path.stem}"
    return path.stem


def load_curated(conn, name, table, cols):
    """curation/<name>.csv -> table. Each row must point at a record that exists."""
    path = CURATION / name
    if not path.exists():
        return
    with open(path, newline="", encoding="utf-8") as f:
        rows = [tuple(r[c] for c in cols) for r in csv.DictReader(f)]
    conn.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", rows)


def build():
    DB.unlink(missing_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    for day, released in RELEASED.items():
        for path in sorted((PACKS / day).rglob("*")):
            parts = path.relative_to(PACKS / day).parts
            if path.suffix not in PARSERS or SKIP_DIRS & set(parts):
                continue
            sid = source_id(path)
            conn.execute("INSERT INTO source VALUES (?,?,?,?,?)",
                         (sid, str(path.relative_to(ROOT)), kind_of(parts, path.name),
                          to_ist(released), int(sid in RESTRICTED)))
            conn.executemany("INSERT INTO record VALUES (?,?,?,?,?,?)",
                             [(rid, sid, loc, occ, text, data and json.dumps(data, default=str))
                              for rid, loc, occ, text, data in PARSERS[path.suffix](path, sid)])

    # People come straight from Keka. Aliases: full name, email, and (when unique among
    # employees) first name and "P. Nair" style, which the leave register uses (A-007).
    people = conn.execute("SELECT id, data FROM record WHERE source_id = 'KEKA' AND data IS NOT NULL").fetchall()
    people = [(rid, json.loads(d)) for rid, d in people]
    short = {rid: (p["Full Name"].split()[0].lower(), f"{p['Full Name'][0]}. {p['Full Name'].split()[-1]}".lower())
             for rid, p in people}
    for rid, p in people:
        conn.execute("INSERT INTO entity VALUES (?,?,?,?)", (p["Emp ID"], "person", p["Full Name"], rid))
        spellings = {p["Full Name"].lower(), p["Work Email"].lower()}
        for i, form in enumerate(short[rid]):
            if [s[i] for s in short.values()].count(form) == 1:
                spellings.add(form)
        conn.executemany("INSERT INTO alias VALUES (?,?,?,?,?)",
                         [(s, p["Emp ID"], "H", rid, "Keka") for s in spellings])

    load_curated(conn, "entities.csv", "entity", ("id", "kind", "name", "record_id"))
    load_curated(conn, "aliases.csv", "alias", ("alias", "entity_id", "confidence", "record_id", "note"))
    load_curated(conn, "claims.csv", "claim", ("id", "metric", "value", "unit", "as_at", "record_id", "quote"))
    load_curated(conn, "verdicts.csv", "verdict", ("claim_id", "verdict", "reason", "decided_on"))
    # verdicts.csv holds a plain date; it takes effect at that day's 10:00 IST release (A-001).
    conn.execute("UPDATE verdict SET decided_on = decided_on || 'T10:00:00+05:30'")
    conn.commit()
    return conn


if __name__ == "__main__":
    conn = build()
    for row in conn.execute("""SELECT s.released_at, s.kind, COUNT(*) FROM record r JOIN source s ON s.id = r.source_id
                               GROUP BY 1, 2 ORDER BY 1, 2"""):
        print(*row)
    print("people:", conn.execute("SELECT COUNT(*) FROM entity WHERE kind = 'person'").fetchone()[0])
