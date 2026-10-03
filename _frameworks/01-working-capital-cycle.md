---
number: 1
title: "The Cash Conversion Cycle as an Operating Lever"
summary: "Placeholder article. Replace this with your own framework. It shows every formatting element the site supports: sections, tables, equations, a worked example and footnotes."
date: 2026-10-03
---

*This is placeholder text showing what each part of an article looks like. Replace it with your own framework, keeping the same Markdown patterns.*

Most finance teams report working capital as a balance sheet figure, then forget it. That misses the point. Working capital is a set of operating decisions about how fast you collect from customers, how long stock sits, and how long you take to pay suppliers. Each decision has a cash value you can calculate, and together they are often worth more than a year of cost-cutting.

This framework does three things: it breaks working capital into its three drivers, puts a cash value on each day of improvement, and ranks the levers by how much cash they release against how hard they are to pull.

## The three drivers

Working capital ties up cash in three places. Two of them consume cash and one funds it:

- **Receivables (DSO).** Cash you have earned but not yet collected. Measured as *days sales outstanding*.
- **Inventory (DIO).** Cash sitting on shelves as stock. Measured as *days inventory outstanding*.
- **Payables (DPO).** Supplier credit that funds part of the other two. Measured as *days payables outstanding*.

The net result is the cash conversion cycle: the number of days between paying for inputs and collecting cash from the customer.

$$
\text{CCC} = \text{DIO} + \text{DSO} - \text{DPO}
$$

Each driver turns into a balance sheet amount through one daily rate. Receivables scale with revenue, while inventory and payables scale with cost of goods sold. One day of DSO is worth $$\tfrac{\text{Revenue}}{365}$$ of cash, and one day of DIO or DPO is worth $$\tfrac{\text{COGS}}{365}$$.

## Baseline: where the cash sits today

Take a business with annual revenue of $146.0m and cost of goods sold of $91.25m, a gross margin of 37.5%. That gives a daily revenue rate of $400,000 and a daily COGS rate of $250,000.

| Driver       | Days | Daily base ($) | Balance ($'000) |
|:-------------|-----:|---------------:|----------------:|
| Receivables  |   60 |        400,000 |          24,000 |
| Inventory    |   45 |        250,000 |          11,250 |
| Payables     |  (40)|        250,000 |        (10,000) |
| Net working capital | 65 |          |          25,250 |
{: .has-total}

The cycle is 65 days, and $25.25m of capital is tied up just to keep the business running.

## Valuing each day of improvement

The value of shortening any driver by $$\Delta d$$ days is the daily base times the change:

$$
\begin{aligned}
\Delta \text{Cash} &= \frac{\text{Revenue}}{365}\,\Delta\text{DSO} \\
&\phantom{=}\; + \frac{\text{COGS}}{365}\,\Delta\text{DIO} \\
&\phantom{=}\; - \frac{\text{COGS}}{365}\,\Delta\text{DPO}
\end{aligned}
$$

This is a one-off release of cash, not a recurring saving. The recurring benefit is the financing cost you avoid on the released amount every year, at your cost of capital $$k$$:

$$
\text{Annual benefit} = \Delta\text{Cash} \times k
$$

<div class="example" markdown="1">

#### Worked example

Management targets three changes: collect 10 days faster, hold 5 fewer days of stock, and negotiate 5 extra days with suppliers.

| Driver       | Before | After | Change in days | Cash released ($'000) |
|:-------------|-------:|------:|---------------:|----------------------:|
| Receivables  |     60 |    50 |            (10)|                 4,000 |
| Inventory    |     45 |    40 |             (5)|                 1,250 |
| Payables     |     40 |    45 |              5 |                 1,250 |
| Total        |     65 |    45 |            (20)|                 6,500 |
{: .has-total}

At a 12% cost of capital, the $6.5m released is worth $$6{,}500 \times 12\% = 780$$, so **$780,000 a year** in avoided financing cost, before counting what the cash earns when reinvested.

</div>

## Ranking the levers

Not every day is equally easy to win. A sensible ranking weighs the cash released per day against how hard it is to deliver and the commercial risk.[^1]

| Lever                      | Cash per day ($'000) | Difficulty | Commercial risk |
|:---------------------------|---------------------:|:-----------|:----------------|
| Tighter collections (DSO)  |                  400 | Medium     | Low to medium   |
| Leaner inventory (DIO)     |                  250 | High       | Medium          |
| Longer supplier terms (DPO)|                  250 | Low        | Medium to high  |

> One day of DSO is worth 1.6 times a day of DIO or DPO in this business, because receivables are built on revenue and the other two are built on cost.

## Where the framework breaks

Every framework has limits. Note yours here so readers trust the rest. For this one:

1. **Seasonality.** Year-end balances can flatter or hide the real cycle. Use average balances wherever possible.
2. **Supplier health.** Stretching payables passes the cost to suppliers, and a fragile supplier base can turn it into a supply risk.[^2]
3. **Revenue mix.** A move towards customers on longer terms raises DSO even with flawless collections.

## Summary

The cash conversion cycle turns working capital from a balance you report into decisions you can value. Put a price on one day of each driver, rank the levers by value and difficulty, and treat the result as a funded plan, not a target.

[^1]: Difficulty and risk ratings are illustrative. Calibrate them to the business you are analysing.
[^2]: Many jurisdictions now regulate payment terms to small suppliers. In India, for example, Section 43B(h) of the Income-tax Act links the deductibility of payments to MSME suppliers to the 45-day limit in the MSMED Act.
