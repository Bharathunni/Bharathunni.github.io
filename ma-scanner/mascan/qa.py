"""Data quality gates. HARD failures mean: do not publish anything downstream."""
from __future__ import annotations

from datetime import date, timedelta

import polars as pl

from . import build, config, manifest


def run(since: date | None = None) -> dict:
    issues: list[dict] = []

    def add(level, exch, d, check, detail):
        issues.append(dict(level=level, exch=exch, date=str(d), check=check, detail=detail))

    with manifest.connect() as con:
        for r in con.execute("SELECT exch, d, status, note FROM files WHERE status IN ('error','blocked')"):
            if since is None or r["d"] >= since.isoformat():
                add("HARD", r["exch"], r["d"], f"download_{r['status']}", r["note"] or "")
        ok = {(r["exch"], r["d"]) for r in con.execute("SELECT exch, d FROM files WHERE status='ok'")}

    # one exchange traded, the other has no file: one of the two is wrong
    dates = {d for _, d in ok}
    for d in sorted(dates):
        if since and d < since.isoformat():
            continue
        have = {e for e in ("nse", "bse") if (e, d) in ok}
        if len(have) == 1:
            add("SOFT", ({"nse", "bse"} - have).pop(), d, "missing_vs_other_exchange",
                f"{have.pop()} has a file for this day")

    for exch in ("nse", "bse"):
        if not (config.PRICES / exch).exists():
            continue
        lf = build.load(exch)
        if since:
            lf = lf.filter(pl.col("date") >= since - timedelta(days=45))
        daily = (
            lf.group_by("date").agg(
                rows=pl.len(),
                bad_ohlc=((pl.col("low") > pl.min_horizontal("open", "close")) |
                          (pl.col("high") < pl.max_horizontal("open", "close")) |
                          (pl.col("close") <= 0)).sum(),
                dupes=pl.len() - pl.struct("code", "series").n_unique(),
                no_isin=pl.col("isin").is_null().sum(),
            ).sort("date").collect()
        )
        daily = daily.with_columns(med=pl.col("rows").rolling_median(20, min_samples=5).shift(1))
        for r in daily.iter_rows(named=True):
            if since and r["date"] < since:
                continue
            if r["med"] and r["rows"] < config.MIN_ROWS_VS_MEDIAN * r["med"]:
                add("HARD", exch, r["date"], "low_row_count", f"{r['rows']} rows vs median {r['med']:.0f}")
            if r["bad_ohlc"] / r["rows"] > config.MAX_BAD_OHLC_SHARE:
                add("HARD", exch, r["date"], "bad_ohlc", f"{r['bad_ohlc']} of {r['rows']} rows")
            if r["dupes"]:
                add("HARD", exch, r["date"], "duplicate_keys", f"{r['dupes']} duplicate (code, series)")
            if r["date"] >= date(2016, 1, 1) and r["no_isin"] / r["rows"] > 0.05:
                add("SOFT", exch, r["date"], "isin_missing", f"{r['no_isin']} of {r['rows']} rows")

    config.REPORTS.mkdir(parents=True, exist_ok=True)
    report = config.REPORTS / "qa_latest.csv"
    schema = {"level": pl.Utf8, "exch": pl.Utf8, "date": pl.Utf8, "check": pl.Utf8, "detail": pl.Utf8}
    pl.DataFrame(issues, schema=schema).write_csv(report)
    hard = sum(i["level"] == "HARD" for i in issues)
    return {"hard": hard, "soft": len(issues) - hard, "report": str(report), "issues": issues}
