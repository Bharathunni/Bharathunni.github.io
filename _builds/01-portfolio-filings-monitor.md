---
number: 1
title: "Portfolio Filings Monitor"
summary: "An unattended service that checks every stock in a portfolio against BSE corporate filings each morning, keeps only the material events, ranks them by severity and emails each user a headline-first digest. No servers, no database, no paid data."
date: 2026-10-04
featured: true
---

Anyone holding Indian equities directly has the same blind spot. Exchange filings are where an auditor resignation, a pledge invocation or a default first becomes public, and BSE publishes them in a constant stream. Almost all are routine: trading-window closures, newspaper ads, Reg 74(5) certificates. The few that matter are buried in that noise, and by the time they reach the news the price has often already moved.

This build reads the filings so the investor doesn't have to. At 07:00 IST every day it pulls the last 26 hours of announcements for every holding, throws away the routine, ranks what's left by severity and sends each user one email showing what changed in their portfolio overnight.

## What it does

- **Watches live holdings.** Each user's portfolio comes from a published Google Sheet, so they edit it on their phone and the next morning's run picks up the change. An inline copy in the repo is the fallback if Google is down.
- **Fetches once per stock.** If five users hold the same stock, BSE gets one call, not five.
- **Filters to material events.** Every filing is classified by explicit keyword rules into a fixed severity table. The routine ones are dropped.
- **Emails each user their own brief.** High-severity holdings come first, then medium, then low. Quiet holdings are listed at the bottom so the user knows they were checked.

![Sample digest email showing a HIGH red flag for an auditor resignation, two MEDIUM items and one LOW order win]({{ '/assets/img/builds/portfolio-filings-monitor/sample-digest.png' | relative_url }})

*The digest, rendered from the repo's own test run on fictional companies (`examples/render_sample.py`). 8 raw filings in, 4 material filings out.*

## Why the classifier is rules, not AI

A digest that decides whether an auditor resignation reaches an investor has to be exact, repeatable and auditable. A language model would be quicker to write and worse to trust: on a bad day it can miss a red flag, and it can never tell you why.

So every filing is matched against explicit keyword lists, and for any line in any email you can point to the exact rule that kept or dropped it. The same input always gives the same output.

> AI was used as leverage to build this quickly. It is not in the runtime path.

Four rules keep it honest:

1. **Severity is a fixed table, not a score.** Category maps straight to HIGH, MEDIUM or LOW. There is no probabilistic ranking.
2. **Red flags are checked before noise.** A HIGH match wins even if the headline also looks routine, so the filter fails towards over-reporting, never towards a silent miss.
3. **Whole-word matching only.** A plain substring check would fire `asm` (the ASM surveillance list) on "enthusiasm". Every keyword is matched as a whole word, and the known leak cases are pinned by regression tests.[^1]
4. **Failures are loud.** If one user's sheet or email fails, that user is skipped, everyone else still gets their digest, and the run exits red so the owner is notified.

## The severity model

| Severity | Categories                      | Example triggers                                                              |
|:---------|:--------------------------------|:------------------------------------------------------------------------------|
| HIGH     | Red flag, Management, Pledge    | Auditor resignation, fraud, default, NCLT/IBC, SEBI order, ASM/GSM, CFO exit  |
| MEDIUM   | Earnings, Dividend, Capital, M&A, Rating | Results, buyback, QIP, rights, merger or demerger, rating action    |
| LOW      | Orders                          | Order wins, letters of intent, contracts                                      |
| Dropped  | Noise                           | Trading window, Reg 74(5), newspaper ads, ESOP allotments, analyst-meet notices |

<div class="example" markdown="1">

#### Worked example: one morning's feed

Five holdings, eight raw filings. This is the exact input the sample render uses, run through the same `classify()` path as the live service.

| Holding  | Filing                                              | Result            |
|:---------|:----------------------------------------------------|:------------------|
| ALPHACEM | Resignation of Statutory Auditor                    | **HIGH** red flag |
| ALPHACEM | Closure of Trading Window                           | Dropped           |
| BETAFIN  | Outcome of Board Meeting, Financial Results Q2 FY27 | MEDIUM earnings   |
| BETAFIN  | Credit Rating reaffirmed                            | MEDIUM rating     |
| BETAFIN  | Newspaper Publication of financial results          | Dropped           |
| GAMMAPWR | Receipt of Order worth Rs 240 crore                 | LOW orders        |
| DELTAIT  | Certificate under Reg. 74 (5)                       | Dropped           |
| DELTAIT  | Analyst / Institutional Investor Meet, Intimation   | Dropped           |

Four of eight survive. The one that matters, the auditor exit, is at the top of the email in red.

</div>

## How it runs

The whole thing runs on GitHub Actions, which is free. There is no server to keep alive.

- **Schedule.** A cron at 01:30 UTC, which is 07:00 IST.
- **Lookback.** 26 hours. The 2-hour overlap absorbs cron delays. BSE's API filters by calendar date only, so each filing is re-checked against its IST timestamp to stop a morning run re-reporting the previous night.[^2]
- **Data source.** BSE, not NSE. BSE answers requests from datacentre IPs when browser headers are sent; NSE doesn't. That's why the portfolio is keyed on BSE scrip codes.
- **Validation on commit.** Any edit under `portfolios/` triggers a validation-only run, so a malformed portfolio file fails at commit time rather than at 07:00.
- **Tests on every change.** `pytest` plus a full offline render of the sample digest on every Python commit.

## Stack and source

| Layer      | Choice                              |
|:-----------|:------------------------------------|
| Language   | Python 3.12, one dependency (`requests`) |
| Scheduler  | GitHub Actions cron                 |
| Holdings   | Google Sheets, published as CSV     |
| Data       | BSE corporate announcements API     |
| Delivery   | Gmail SMTP with an App Password     |
| Tests      | `pytest`, no network needed         |

**Source:** [github.com/bharathunni/portfolio-filings-monitor](https://github.com/bharathunni/portfolio-filings-monitor). The public repo ships with an illustrative portfolio and fictional sample filings only. No real holdings.

[^1]: The matcher lives in `keywords.py`. It allows plurals (`penalty` matches "penalties") and a trailing `*` for prefixes (`pledge invo*` matches "invoked" and "invocation"), but never a match inside a longer word.
[^2]: BSE stamps filings in IST wall-clock time while GitHub's runners run on UTC, so every date window in the script is computed in IST.
