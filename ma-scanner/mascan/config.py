"""Paths, source URLs and tunables. Everything fragile lives here so a URL change is a one-line fix."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

ROOT = Path(os.environ.get("MASCAN_HOME", Path.cwd()))
DATA = ROOT / "data"
RAW = DATA / "raw"            # immutable exchange files, exactly as downloaded
PRICES = DATA / "prices"      # canonical unadjusted daily rows, one parquet per exchange per year
REPORTS = DATA / "reports"    # QA output
DB = DATA / "manifest.sqlite"  # one row per (exchange, date): what we tried and what happened

DEFAULT_START = date(2005, 1, 1)

# From this date the unified (UDiFF) file is tried first, then the legacy file.
UDIFF_FIRST_FROM = {"nse": date(2024, 7, 1), "bse": date(2024, 1, 1)}

NSE_HOSTS = ["https://nsearchives.nseindia.com", "https://archives.nseindia.com"]
BSE_HOST = "https://www.bseindia.com"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
REFERER = {"nse": "https://www.nseindia.com/all-reports", "bse": "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"}

# Soft 404s: BSE answers any missing file with HTTP 200 and its Angular homepage shell instead of 404.
# A body containing one of these markers means "no file here", not "blocked".
SOFT_404_MARKERS = [b"<app-root"]

REQUEST_GAP_SECONDS = 0.7      # polite gap between requests
MAX_CONSECUTIVE_BLOCKS = 8     # stop the run if the exchange is refusing us
RECHECK_MISSING_DAYS = 7       # recent "missing" days are retried (late publication)

# QA thresholds
MIN_ROWS_VS_MEDIAN = 0.70      # a day with <70% of the trailing median row count is suspect
MAX_BAD_OHLC_SHARE = 0.002     # share of rows allowed to violate low <= open/close <= high


def candidates(exch: str, d: date) -> list[tuple[str, str, str]]:
    """Return [(format, url, filename)] to try for one exchange and date, in order."""
    ymd = d.strftime("%Y%m%d")
    out: list[tuple[str, str, str]] = []
    if exch == "nse":
        mon = d.strftime("%b").upper()
        udiff = [
            ("udiff", f"{h}/content/cm/BhavCopy_NSE_CM_0_0_0_{ymd}_F_0000.csv.zip",
             f"BhavCopy_NSE_CM_0_0_0_{ymd}_F_0000.csv.zip")
            for h in NSE_HOSTS
        ]
        legacy = [
            ("nse_legacy", f"{h}/content/historical/EQUITIES/{d.year}/{mon}/cm{d:%d}{mon}{d.year}bhav.csv.zip",
             f"cm{d:%d}{mon}{d.year}bhav.csv.zip")
            for h in NSE_HOSTS
        ]
        out = udiff + legacy if d >= UDIFF_FIRST_FROM["nse"] else legacy
    elif exch == "bse":
        base = f"{BSE_HOST}/download/BhavCopy/Equity"
        udiff = [("udiff", f"{base}/BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV", f"BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV")]
        legacy = [
            ("bse_legacy", f"{base}/EQ_ISINCODE_{d:%d%m%y}.zip", f"EQ_ISINCODE_{d:%d%m%y}.zip"),
            ("bse_legacy", f"{base}/EQ{d:%d%m%y}_CSV.ZIP", f"EQ{d:%d%m%y}_CSV.ZIP"),
        ]
        out = udiff + legacy if d >= UDIFF_FIRST_FROM["bse"] else legacy
    else:
        raise ValueError(f"unknown exchange {exch!r}")
    return out
