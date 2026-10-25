---
number: 3
title: "Microapp: True Profit per Product for Micro-Businesses"
summary: "A free, offline-first phone app for home businesses: real cost per pack from each batch, bills on WhatsApp, money owed by age, bank statement import and a one-page monthly report for the CA. White-label, one config per client, zero running cost."
date: 2026-10-22
featured: true
image: "/assets/img/builds/microapp/screens.png"
---

Most home businesses in India price by feel. The owner knows what a kilo of green gram costs, but not what one 250 g pack of bath powder costs once packaging, gas and her own three hours at the grinder are in. Sales go into a notebook, payments come in over UPI and cash, and at month end nobody can say which product made money and who still owes what.

The tools on offer don't fit. Accounting apps want ledgers and GST settings the owner will never use. Spreadsheets need someone to build and keep them. Billing apps produce invoices but don't know what anything cost to make.

Microapp asks the owner only what she already knows: what went into this batch, how many packs came out, who bought what. From that it works out the profit on every pack, the money owed to her and a monthly summary her CA can use. It runs on her phone, in Tamil or English, with no account and no internet once installed.

![Three phone screens: home with profit for the month, money owed and best and worst product; a product showing ₹60 earned on every pack; and a bill ready to send on WhatsApp]({{ '/assets/img/builds/microapp/screens.png' | relative_url }})

*Home, product and bill screens, captured from the app running on synthetic data for a fictional month.*

## What it does

- **Costs every batch.** One question per screen: ingredients and what each cost, packs made, packaging per pack, gas hours, labour hours. The app returns cost per pack, earning per pack and a green, amber or red margin signal.
- **Costs bought-in stock.** For resold items, purchase price, freight, packing and other costs are spread over the pieces bought to give a landed cost per piece.
- **Bills on WhatsApp.** A bill is a branded image shared straight to the customer. Each one is marked paid by UPI, paid in cash, or still owed.
- **Tracks money owed by age.** Unpaid bills show days outstanding and turn amber at 15 days and red at 45, the MSME Act payment limit.[^1] One tap sends a polite WhatsApp reminder.
- **Reads bank statements.** Import any bank's CSV. Money in is matched to UPI bills, payees are tagged once and remembered, and tagged business expenses come off the month's profit.
- **Reports to the CA.** A one-page monthly PDF plus a data file, shared from the phone.
- **Speaks the owner's language.** Every screen is in Tamil and English, with Hindi ready. Numbers can be spoken instead of typed.

![The same home screen in English and in Tamil]({{ '/assets/img/builds/microapp/english-tamil.png' | relative_url }})

*The same month in English and Tamil. No accounting words on any screen: "Profit", "People owe you", "Cost per pack".*

## Costing, the way a CA would

The owner never sees a formula, but every number on screen comes from one.

<div class="example" markdown="1">

#### Worked example: one batch of Nalangu Maavu

20 packs of 250 g, selling at ₹120 a pack. Gas at ₹25 an hour and labour at ₹100 an hour are the client's defaults; the owner can change them per batch.

| Cost                          | Basis                  | Amount (₹) |
|:------------------------------|:-----------------------|-----------:|
| Ingredients                   | 4 items, as bought     |        715 |
| Packaging                     | ₹8 × 20 packs          |        160 |
| Gas                           | 1 hour × ₹25           |         25 |
| Labour                        | 3 hours × ₹100         |        300 |
| Batch cost                    |                        |      1,200 |
{: .has-total}

| Per pack                      | Amount (₹) |
|:------------------------------|-----------:|
| Selling price                 |        120 |
| Cost per pack (1,200 ÷ 20)    |       (60) |
| Earning per pack              |         60 |
{: .has-total}

A 50% margin shows green. 10 packs sold in the last 30 days, so the app also says: *"If price goes up by ₹20, you earn about ₹200 more a month."*

</div>

Three rules make the profit figure defensible:

1. **Labour is a cost.** Owner-operators leave their own time out and overstate profit. Labour hours are a required step in every batch.
2. **Each sale is costed at the batch it came from.** A bill uses the cost per pack of the latest batch made on or before the bill date, so a rise in ingredient prices hits the right sales, not last month's.
3. **No cost, no guess.** Sales of a product with no recorded batch are reported as "sales without a costing", never assumed at zero cost.

Shipping charged to the customer is a pass-through to the courier, so it sits outside margin.

## The monthly report

![One-page monthly summary: sales, receipts by UPI and cash, cost of items sold, gross margin, sales by product and unpaid bills]({{ '/assets/img/builds/microapp/ca-report.png' | relative_url }})

*The October report for the same synthetic data. 6 bills, ₹4,050 of sales, ₹1,675 gross margin.*

It's built for the person who files the return, not the owner. Sales and margin are on the bill date, paid or not (accrual), receipts are split by UPI and cash, and unpaid bills are aged as of today. The data file carries every bill line, so the CA can rebuild any figure on a computer.

| Product                    | Qty | Sales (₹) | Cost (₹) | Margin (₹) |
|:---------------------------|----:|----------:|---------:|-----------:|
| Eeyachombu 1000 ml         |   1 |     1,800 |    1,320 |        480 |
| Nalangu Maavu              |  10 |     1,200 |      600 |        600 |
| Baby Bath Powder           |   7 |     1,050 |      455 |        595 |
| Total                      |  18 |     4,050 |    2,375 |      1,675 |
{: .has-total}

## Rules, not AI

> No AI APIs, no paid APIs, no servers. Running cost is zero, per client, forever.

- **Money is integer paise.** Floats never hold an amount. Every multiplication by hours or quantity rounds back to whole paise, half away from zero, so ₹0.005 and -₹0.005 behave the same.
- **All money maths is pure functions with tests.** The UI never calculates a rupee. 241 Vitest tests cover costing, bills, reports, statement parsing and voice input.
- **Statement matching is exact.** Money in pairs with a UPI bill only on the same amount within ±3 days, closest date first, and each bill is used once. A re-imported statement is recognised line by line and nothing is counted twice.
- **Payee tags are the owner's rules.** Tag "Sri Murugan Traders" as a supplier once and every later entry from them is tagged the same way. Nothing is inferred.
- **Data stays on the phone.** Everything lives in the browser's on-device database. Nothing leaves except through the owner's own Share or Backup, and the app nudges a weekly backup because phones can clear storage when space runs low.

AI was used as leverage to build the app quickly. It is not in the runtime path.

## One codebase, many businesses

Each client is a folder: business name, logo, colours, languages, WhatsApp number and product list. A build turns every folder into its own installable app at its own address, with its own icons, offline cache and database. Adding a business is a config file, not code.

The config takes public brochure information only. Any cost-like key fails the build, so a client's recipes and margins can't leak into a shared repository.

## Stack and source

| Layer        | Choice                                                     |
|:-------------|:-----------------------------------------------------------|
| UI           | React 18, TypeScript (strict)                              |
| Build        | Vite 6, installable offline PWA via vite-plugin-pwa        |
| Storage      | IndexedDB via Dexie, versioned schema with migrations      |
| Bills and PDF | html2canvas and jsPDF, shared through the phone's share sheet |
| Statements   | PapaParse                                                  |
| Tests        | Vitest, 241 tests                                          |
| CI and hosting | GitHub Actions: test, build every client, check each is installable offline; deploy to Cloudflare Pages |

**Live:** the first client, Parambariyam, a herbal personal-care and brassware business, runs at [view-my-apps.pages.dev/parambariyam](https://view-my-apps.pages.dev/parambariyam/). Open it in Chrome on Android and tap **Install app**. **Source:** private, as client configurations live in the same repository.

[^1]: Under Section 15 of the MSMED Act, 2006, a buyer must pay a micro or small enterprise within the agreed period, capped at 45 days from acceptance. Section 43B(h) of the Income-tax Act disallows the deduction for payments made beyond that limit.
