"""Command line: python -m mascan <download|build|qa|status|nightly>"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from . import build, config, download, manifest, qa


def _d(s: str) -> date:
    return date.today() if s == "today" else date.fromisoformat(s)


def status() -> None:
    with manifest.connect() as con:
        rows = con.execute(
            "SELECT exch, status, COUNT(*) n, MIN(d) lo, MAX(d) hi FROM files GROUP BY 1,2 ORDER BY 1,2").fetchall()
    if not rows:
        print("manifest is empty: nothing downloaded yet")
    for r in rows:
        print(f"{r['exch']:4} {r['status']:8} {r['n']:6}  {r['lo']} .. {r['hi']}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="mascan")
    sub = p.add_subparsers(dest="cmd", required=True)
    dl = sub.add_parser("download", help="fetch raw bhavcopies")
    dl.add_argument("--from", dest="start", type=_d, default=config.DEFAULT_START)
    dl.add_argument("--to", dest="end", type=_d, default=date.today())
    dl.add_argument("--exch", default="nse,bse")
    dl.add_argument("--retry", action="store_true", help="retry days previously recorded as missing")
    b = sub.add_parser("build", help="parse raw files into parquet")
    b.add_argument("--all", action="store_true", help="rebuild every year")
    q = sub.add_parser("qa", help="run data quality gates")
    q.add_argument("--since", type=_d, default=None)
    sub.add_parser("status", help="show manifest summary")
    n = sub.add_parser("nightly", help="download last 10 days, build, qa")
    n.add_argument("--days", type=int, default=10)
    a = p.parse_args(argv)

    if a.cmd == "download":
        print(download.run(a.exch.split(","), a.start, a.end, retry=a.retry))
    elif a.cmd == "build":
        r = build.run(rebuild_all=a.all)
        print({k: v for k, v in r.items() if k != "failed"})
        for f in r["failed"]:
            print("  PARSE FAIL", f)
    elif a.cmd == "status":
        status()
    elif a.cmd in ("qa", "nightly"):
        since = getattr(a, "since", None)
        if a.cmd == "nightly":
            since = date.today() - timedelta(days=a.days)
            print(download.run(["nse", "bse"], since, date.today()))
            build.run()
        r = qa.run(since)
        for i in r["issues"][:40]:
            print(f"  {i['level']} {i['exch']} {i['date']} {i['check']}: {i['detail']}")
        print(f"QA: {r['hard']} hard, {r['soft']} soft. Report: {r['report']}")
        return 1 if r["hard"] else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
