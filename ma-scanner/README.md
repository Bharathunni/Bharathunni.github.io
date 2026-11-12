# MA Scanner

Stage 1 of 5: ingest. Downloads every NSE and BSE equity bhavcopy, keeps the raw files untouched,
and builds one clean, unadjusted daily price table with quality gates.

## Setup (Windows, once)

```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py -m pytest -q
```

All 7 tests should pass. They use synthetic files and need no internet.

## First run: smoke test before the full backfill

```
py -m mascan download --from 2026-11-02 --to 2026-11-11
py -m mascan status
py -m mascan build
py -m mascan qa
```

Expected: about 7 `ok` days per exchange, weekend days `missing`, QA with 0 hard issues.
If you see `blocked` or `error`, send me the output. The download URLs are the one part that
could not be tested outside India, and they sit in `mascan/config.py` for a one-line fix.

Then test one old date range per format era:

```
py -m mascan download --from 2024-06-24 --to 2024-07-19
py -m mascan download --from 2010-03-01 --to 2010-03-12
```

## Full backfill

```
py -m mascan download --from 2005-01-01
py -m mascan build
py -m mascan qa
```

Roughly 16,000 requests across both exchanges, a few hours. Safe to stop and rerun: finished
days are skipped. If an exchange starts refusing requests, the run stops by itself rather than
recording those days as holidays.

## Nightly (after 7 pm IST)

```
py -m mascan nightly
```

Exit code 1 means a hard QA failure: nothing downstream should publish.

## Layout

```
data/raw/<exch>/<year>/     original exchange files, never modified
data/prices/<exch>/<year>.parquet   canonical rows: date, exch, code, symbol, name, series,
                            sec_type, isin, open, high, low, close, prev_close, volume, turnover, trades, fmt
data/manifest.sqlite        every (exchange, date) attempted and its outcome
data/reports/qa_latest.csv  QA issues
```

## Stages

1. Ingest (this)
2. Security master (ISIN merge, symbol changes) and corporate action adjustment
3. Weekly and monthly bars, MA engine (26 lines), distance and touch levels
4. Event study (returns after touch, extension thresholds) and scoring
5. Front end (screen, top cases, watchlist) and nightly automation
