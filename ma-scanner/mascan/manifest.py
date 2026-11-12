"""SQLite manifest: the single record of what was fetched, when, and whether it has been parsed."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    exch TEXT NOT NULL,
    d TEXT NOT NULL,              -- ISO date
    status TEXT NOT NULL,         -- ok | missing | blocked | error
    fmt TEXT,                     -- udiff | nse_legacy | bse_legacy
    path TEXT,                    -- relative to data/raw
    bytes INTEGER,
    sha256 TEXT,
    http INTEGER,
    note TEXT,
    fetched_at TEXT NOT NULL,
    parsed INTEGER NOT NULL DEFAULT 0,
    rows INTEGER,
    PRIMARY KEY (exch, d)
);
"""


@contextmanager
def connect():
    config.DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DB)
    con.row_factory = sqlite3.Row
    con.execute(SCHEMA)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def upsert(con, **row) -> None:
    cols = ["exch", "d", "status", "fmt", "path", "bytes", "sha256", "http", "note", "fetched_at"]
    vals = [row.get(c) for c in cols]
    con.execute(
        f"INSERT INTO files ({','.join(cols)}, parsed, rows) VALUES ({','.join('?' * len(cols))}, 0, NULL) "
        "ON CONFLICT(exch, d) DO UPDATE SET status=excluded.status, fmt=excluded.fmt, path=excluded.path, "
        "bytes=excluded.bytes, sha256=excluded.sha256, http=excluded.http, note=excluded.note, "
        "fetched_at=excluded.fetched_at, parsed=0, rows=NULL",
        vals,
    )
