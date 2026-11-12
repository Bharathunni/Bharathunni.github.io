"""Download raw bhavcopies. Idempotent: a date already fetched is never fetched again.

Every calendar day is attempted (not only weekdays) because special sessions and Muhurat
trading fall on weekends. A day with no file anywhere is recorded as "missing".
"""
from __future__ import annotations

import hashlib
import random
import time
from datetime import date, datetime, timedelta, timezone

import requests

from . import config, manifest


def make_session(exch: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": config.USER_AGENT,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": config.REFERER[exch],
    })
    if exch == "nse":  # NSE hands out cookies on the main site; archives sometimes want them
        try:
            s.get("https://www.nseindia.com", timeout=15)
        except requests.RequestException:
            pass
    return s


def classify(body: bytes) -> str:
    """zip | csv | notfound | html | empty | unknown. Exchanges return HTML pages with HTTP 200."""
    if not body:
        return "empty"
    if body[:2] == b"PK":
        return "zip"
    head = body[:600].lower()
    if b"<html" in head or b"<!doctype" in head:
        if any(m in body[:20000].lower() for m in config.SOFT_404_MARKERS):
            return "notfound"   # site shell served for a missing path (BSE)
        return "html"
    first = head.split(b"\n", 1)[0]
    if first.count(b",") >= 5:
        return "csv"
    return "unknown"


def _get(session, url: str):
    last = None
    for attempt in range(4):
        try:
            r = session.get(url, timeout=40)
        except requests.RequestException as e:
            last = f"network: {type(e).__name__}"
            time.sleep(2 ** attempt)
            continue
        if r.status_code in (429, 500, 502, 503, 504):
            last = f"http {r.status_code}"
            time.sleep(2 ** (attempt + 1))
            continue
        return r.status_code, r.content, None
    return None, b"", last


def fetch_day(session, exch: str, d: date) -> dict:
    """Try each candidate URL for one day. Returns a manifest row (file is written if found)."""
    blocked = error = None
    http = None
    for fmt, url, fname in config.candidates(exch, d):
        code, body, err = _get(session, url)
        time.sleep(config.REQUEST_GAP_SECONDS + random.random() * 0.4)
        http = code
        if err:
            error = err
            continue
        kind = classify(body)
        if code == 200 and kind in ("zip", "csv"):
            rel = f"{exch}/{d.year}/{fname}"
            dest = config.RAW / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(dest.suffix + ".part")
            tmp.write_bytes(body)
            tmp.replace(dest)  # atomic: a crash never leaves a half file
            return dict(status="ok", fmt=fmt, path=rel, bytes=len(body),
                        sha256=hashlib.sha256(body).hexdigest(), http=code, note=None)
        if code == 200 and kind == "notfound":
            continue            # same as a 404
        if code in (401, 403) or (code == 200 and kind == "html"):
            blocked = f"http {code} {kind}"
        elif code != 404:
            error = f"http {code} {kind}"
    if blocked:
        return dict(status="blocked", http=http, note=blocked)
    if error:
        return dict(status="error", http=http, note=error)
    return dict(status="missing", http=http, note="no file on any candidate url")


def run(exchanges: list[str], start: date, end: date, retry: bool = False, session_factory=make_session) -> dict:
    summary = {}
    today = date.today()
    with manifest.connect() as con:
        for exch in exchanges:
            done = {r["d"]: r["status"] for r in con.execute("SELECT d, status FROM files WHERE exch=?", (exch,))}
            session = session_factory(exch)
            counts = {"ok": 0, "missing": 0, "blocked": 0, "error": 0, "skipped": 0}
            streak = 0
            d = start
            while d <= end:
                prev = done.get(d.isoformat())
                recent = (today - d).days <= config.RECHECK_MISSING_DAYS
                skip = prev == "ok" or (prev == "missing" and not recent and not retry)
                if skip:
                    counts["skipped"] += 1
                else:
                    row = fetch_day(session, exch, d)
                    manifest.upsert(con, exch=exch, d=d.isoformat(),
                                    fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"), **row)
                    con.commit()
                    counts[row["status"]] += 1
                    streak = streak + 1 if row["status"] == "blocked" else 0
                    if row["status"] == "ok":
                        print(f"  {exch} {d} ok ({row['fmt']}, {row['bytes']:,} bytes)")
                    if streak >= config.MAX_CONSECUTIVE_BLOCKS:
                        print(f"!! {exch}: refused {streak} times in a row at {d}. Stopping. "
                              "Wait and rerun, or run from a home connection (not a cloud server).")
                        counts["aborted_at"] = d.isoformat()
                        break
                d += timedelta(days=1)
            summary[exch] = counts
    return summary
