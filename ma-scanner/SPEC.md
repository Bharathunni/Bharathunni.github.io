# MA Scanner: locked spec (12 Nov 2026)

## Universe
All equity securities on NSE and BSE, merged by ISIN, primary exchange = higher turnover.
Liquidity floor and series inclusion (SME, trade-to-trade) to be fixed at stage 2 from real data.

## Moving averages (13 periods x SMA and EMA = 26 lines)
- Daily bars: 21, 50, 100, 200
- Weekly bars: 7, 14, 21, 26, 50, 100, 200
- Monthly bars: 50, 100
- Dropped: 200 month, bi-monthly, quarterly

## Signals
- Proximity: price within 5% of a line, split by direction (falling onto it from above, rising into it from below)
- Extension (sell flag): threshold per line derived from the event study, not a fixed percentage
- Confluence: counted by distinct timeframe clusters, not by raw line count

## App
- Screen: table of stocks x lines with % distance, colour deepening near a line; per-stock static chart
- Top cases: home (score weighted to longer lines, confluence filter), one page per MA, watchlist
- Returns after touch: median return at 3m, 6m, 1y, 3y, hit rate, worst drawdown, excess over the
  stock's normal return, event count; pooled by MA and market-cap bucket when the stock's own sample is thin

## Operating rules
- End of day only. Raw exchange files are immutable. Nothing publishes on a hard QA failure.
- Event study recalibrated quarterly.
- Full rule book (touch band, re-arm, weights, thresholds) to be issued as RULES.md after the build.
