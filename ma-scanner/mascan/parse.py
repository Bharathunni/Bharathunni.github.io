"""Turn any raw bhavcopy into one canonical table.

The format is detected from the header row, never from the date, so an early or late
format switch by an exchange cannot silently break parsing.
"""
from __future__ import annotations

import csv
import io
import zipfile
from datetime import date, datetime

import polars as pl

SCHEMA = {
    "date": pl.Date, "exch": pl.Utf8, "code": pl.Utf8, "symbol": pl.Utf8, "name": pl.Utf8,
    "series": pl.Utf8, "sec_type": pl.Utf8, "isin": pl.Utf8,
    "open": pl.Float64, "high": pl.Float64, "low": pl.Float64, "close": pl.Float64, "prev_close": pl.Float64,
    "volume": pl.Float64, "turnover": pl.Float64, "trades": pl.Float64, "fmt": pl.Utf8,
}


class ParseError(Exception):
    pass


def _text(body: bytes) -> str:
    if body[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            names = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not names:
                raise ParseError(f"zip has no csv: {z.namelist()}")
            body = z.read(names[0])
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return body.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ParseError("cannot decode file")


def _num(x):
    if x is None:
        return None
    x = x.strip().replace(",", "")
    if x in ("", "-", "NA", "null"):
        return None
    try:
        return float(x)
    except ValueError:
        return None


def _s(x):
    if x is None:
        return None
    x = x.strip()
    return x or None


def _date(x, fmts):
    x = _s(x)
    if not x:
        return None
    for f in fmts:
        try:
            return datetime.strptime(x.title() if "%b" in f else x, f).date()
        except ValueError:
            continue
    return None


def detect(header: list[str]) -> str:
    h = set(header)
    if "TckrSymb" in h and "ClsPric" in h:
        return "udiff"
    if "SYMBOL" in h and "TOTTRDQTY" in h:
        return "nse_legacy"
    if "SC_CODE" in h and "CLOSE" in h:
        return "bse_legacy"
    raise ParseError(f"unrecognised header: {header[:8]}")


def parse(body: bytes, exch: str, file_date: date) -> pl.DataFrame:
    """Parse one raw file. file_date (from the filename) is the authority; the in-file date must agree."""
    rows = list(csv.reader(io.StringIO(_text(body))))
    if len(rows) < 2:
        raise ParseError("file has no data rows")
    header = [c.strip() for c in rows[0]]
    fmt = detect(header)
    idx = {c: i for i, c in enumerate(header) if c}

    def g(r, col):
        i = idx.get(col)
        return r[i] if i is not None and i < len(r) else None

    out = {k: [] for k in SCHEMA}
    seen_dates = set()
    for r in rows[1:]:
        if not any(c.strip() for c in r):
            continue
        if fmt == "udiff":
            in_date = _date(g(r, "TradDt"), ["%Y-%m-%d", "%d-%b-%Y"])
            rec = dict(code=_s(g(r, "TckrSymb")) if exch == "nse" else _s(g(r, "FinInstrmId")),
                       symbol=_s(g(r, "TckrSymb")), name=_s(g(r, "FinInstrmNm")), series=_s(g(r, "SctySrs")),
                       sec_type=_s(g(r, "FinInstrmTp")), isin=_s(g(r, "ISIN")),
                       open=_num(g(r, "OpnPric")), high=_num(g(r, "HghPric")), low=_num(g(r, "LwPric")),
                       close=_num(g(r, "ClsPric")), prev_close=_num(g(r, "PrvsClsgPric")),
                       volume=_num(g(r, "TtlTradgVol")), turnover=_num(g(r, "TtlTrfVal")),
                       trades=_num(g(r, "TtlNbOfTxsExctd")))
        elif fmt == "nse_legacy":
            in_date = _date(g(r, "TIMESTAMP"), ["%d-%b-%Y"])
            sym = _s(g(r, "SYMBOL"))
            rec = dict(code=sym, symbol=sym, name=None, series=_s(g(r, "SERIES")), sec_type=None,
                       isin=_s(g(r, "ISIN")),
                       open=_num(g(r, "OPEN")), high=_num(g(r, "HIGH")), low=_num(g(r, "LOW")),
                       close=_num(g(r, "CLOSE")), prev_close=_num(g(r, "PREVCLOSE")),
                       volume=_num(g(r, "TOTTRDQTY")), turnover=_num(g(r, "TOTTRDVAL")),
                       trades=_num(g(r, "TOTALTRADES")))
        else:  # bse_legacy
            in_date = _date(g(r, "TRADING_DATE"), ["%d-%b-%y", "%d-%b-%Y", "%d/%m/%Y"])
            rec = dict(code=_s(g(r, "SC_CODE")), symbol=None, name=_s(g(r, "SC_NAME")),
                       series=_s(g(r, "SC_GROUP")), sec_type=_s(g(r, "SC_TYPE")), isin=_s(g(r, "ISIN_CODE")),
                       open=_num(g(r, "OPEN")), high=_num(g(r, "HIGH")), low=_num(g(r, "LOW")),
                       close=_num(g(r, "CLOSE")), prev_close=_num(g(r, "PREVCLOSE")),
                       volume=_num(g(r, "NO_OF_SHRS")), turnover=_num(g(r, "NET_TURNOV")),
                       trades=_num(g(r, "NO_TRADES")))
        if rec["code"] is None or rec["close"] is None:
            continue
        if in_date:
            seen_dates.add(in_date)
        rec.update(date=file_date, exch=exch, fmt=fmt)
        for k in SCHEMA:
            out[k].append(rec[k])

    if not out["code"]:
        raise ParseError("no usable rows")
    if seen_dates and seen_dates != {file_date}:
        raise ParseError(f"file is named {file_date} but contains {sorted(seen_dates)[:3]}")
    return pl.DataFrame(out, schema=SCHEMA)
