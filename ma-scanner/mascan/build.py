"""Raw files -> canonical parquet (data/prices/<exch>/<year>.parquet). Rebuilds only years with new files."""
from __future__ import annotations

from datetime import date

import polars as pl

from . import config, manifest
from .parse import ParseError, parse


def run(rebuild_all: bool = False) -> dict:
    out = {"years_built": 0, "files_parsed": 0, "failed": []}
    with manifest.connect() as con:
        cond = "" if rebuild_all else "AND parsed=0"
        todo = con.execute(
            f"SELECT DISTINCT exch, substr(d,1,4) AS y FROM files WHERE status='ok' {cond} ORDER BY 1,2"
        ).fetchall()
        for t in todo:
            exch, y = t["exch"], t["y"]
            files = con.execute(
                "SELECT d, path FROM files WHERE exch=? AND status='ok' AND substr(d,1,4)=? ORDER BY d", (exch, y)
            ).fetchall()
            frames = []
            for f in files:
                try:
                    df = parse((config.RAW / f["path"]).read_bytes(), exch, date.fromisoformat(f["d"]))
                except (ParseError, OSError) as e:
                    out["failed"].append(f"{exch} {f['d']}: {e}")
                    con.execute("UPDATE files SET status='error', note=? WHERE exch=? AND d=?",
                                (f"parse: {e}"[:300], exch, f["d"]))
                    continue
                frames.append(df)
                con.execute("UPDATE files SET parsed=1, rows=? WHERE exch=? AND d=?", (df.height, exch, f["d"]))
                out["files_parsed"] += 1
            if frames:
                dest = config.PRICES / exch / f"{y}.parquet"
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(".parquet.part")
                pl.concat(frames).sort(["date", "code", "series"]).write_parquet(tmp, compression="zstd")
                tmp.replace(dest)
                out["years_built"] += 1
                print(f"  built {exch}/{y}.parquet from {len(frames)} files")
            con.commit()
    return out


def load(exch: str | None = None) -> pl.LazyFrame:
    pattern = str(config.PRICES / (exch or "*") / "*.parquet")
    return pl.scan_parquet(pattern)
