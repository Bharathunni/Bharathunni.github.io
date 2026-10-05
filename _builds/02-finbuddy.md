---
number: 2
title: "FinBuddy: Double-Entry Bookkeeping, Offline"
summary: "An offline-first Android bookkeeping app with real double-entry books: vouchers, trial balance, final accounts, an audit trail and a period lock. Bank CSV import catches duplicates on an exact match. Your books never leave the device."
date: 2026-10-04
featured: true
---

Freelancers, consultants and small firms in India have two bad options. Expense-tracker apps are easy, but they keep single-entry lists that can never produce a balance sheet that ties. Proper accounting software produces real books, but it's built for a desktop and an accountant, and it usually wants your ledgers on someone else's cloud.

FinBuddy closes that gap. It puts the discipline of professional accounting software into a phone app: vouchers, account groups, ledgers, a trial balance, final accounts, an audit trail and a period lock. It needs no account, no server and no internet connection.

**[Try the live demo](https://bharathunni.github.io/Finbuddy-bookkeeping/)** in a browser, no install. It opens on synthetic books for a fictional firm, and anything you change stays in your browser.

![FinBuddy dashboard showing cash and bank, net profit, debtors, creditors and recent vouchers]({{ '/assets/img/builds/finbuddy/dashboard.png' | relative_url }})

*Dashboard on the demo books. Every figure is computed live from the vouchers.*

## Rules, not AI

Books have to balance to the paisa and give the same answer every time. Nothing in FinBuddy is probabilistic or learned.

- **Vouchers can't post unless Dr = Cr**, to the paisa, with explicit rounding at every step so floating-point drift never creeps in.
- **Duplicate detection is an exact match.** No fuzzy matching. A false "duplicate" silently drops a real transaction, which is worse than asking the user to look.
- **Auto-categorisation is keyword rules the user writes**, such as "RENT" to Rent and "SALARY" to Salaries. They're visible and editable, never a model's guess.
- **Every create, edit and delete lands in the audit trail**, in line with the edit-log requirement for Indian accounting software.[^1]

> AI was used as leverage to build the app quickly. It is not in the runtime path.

## Bank import and duplicate detection

Import any bank's CSV export. The app finds the header row and maps the date, narration, withdrawal, deposit and balance columns itself, with a manual override for each. It reads Indian date formats (`dd/mm/yyyy`, `dd-Mon-yy`) and amounts with `₹`, lakh commas or `Cr`/`Dr` suffixes. Withdrawals become Payment vouchers and deposits become Receipt vouchers.

<div class="example" markdown="1">

#### Worked example: importing the same statement twice

A bank line counts as a duplicate only if all four parts of this key match an existing Payment or Receipt:

| Key part   | Match rule                           |
|:-----------|:-------------------------------------|
| Bank ledger | Same ledger                         |
| Date       | Same day                             |
| Amount     | Equal to the paisa                   |
| Narration  | Equal after trimming, ignoring case  |

I imported the demo's sample HDFC statement, assigned ledgers and posted the 7 lines. Then I imported the same file again. All 7 came back flagged, and the post button dropped to zero:

![Bank import review table with all seven lines greyed out and tagged Duplicate]({{ '/assets/img/builds/finbuddy/duplicate-detection.png' | relative_url }})

*Second import of the same statement: 0 ready, 7 duplicates. Captured from the demo build.*

</div>

After posting, the app compares the statement's closing balance with the book balance. It shows either "Reconciles" or the exact unaccounted difference in rupees.

## Reports, computed live

Every report is derived from one pass over the voucher lines, indexed by ledger, so reports stay instant even with thousands of vouchers. All amounts use Indian lakh and crore grouping.

| Report           | Basis                                                  |
|:-----------------|:-------------------------------------------------------|
| Trial Balance    | As at any date, with a "Balanced" check                |
| Trading and P&L  | Any period, gross and net profit carried down          |
| Balance Sheet    | As at any date, with cumulative profit across years    |
| Ledger statement | Running balance                                        |

The demo firm's books for 1 April to 4 October 2026:

| Profit & Loss (₹)            |      Amount |
|:-----------------------------|------------:|
| Gross profit b/d             |    5,18,000 |
| Professional fees            |    2,35,000 |
| Interest received            |      12,400 |
| Salaries                     |  (3,60,000) |
| Rent                         |  (1,40,000) |
| Internet & phone             |     (3,500) |
| Bank charges                 |     (1,180) |
| Net profit                   |    2,60,720 |
{: .has-total}

![FinBuddy Trading and Profit & Loss account in the traditional Dr and Cr format]({{ '/assets/img/builds/finbuddy/profit-loss.png' | relative_url }})

*The same figures in the app, in the traditional two-sided format.*

## Controls

- **Period lock.** Freeze the books up to a date so filed periods can't be changed.
- **Opening balance check.** Any Dr/Cr mismatch in opening balances is flagged before it can corrupt the trial balance.
- **Voucher-type rules.** Six voucher types (Contra, Payment, Receipt, Journal, Sales, Purchase), each with its own checks. Contra only accepts cash and bank ledgers.
- **28 pre-seeded account groups** following the standard Indian chart of accounts, so every ledger lands correctly in the Trading account, P&L or Balance Sheet.
- **GST helper.** Splits a taxable value into CGST and SGST, or IGST, on Sales and Purchase vouchers.

## Stack and source

| Layer        | Choice                                  |
|:-------------|:----------------------------------------|
| UI           | React 19                                |
| Build        | Vite 8                                  |
| Android shell | Capacitor 8                            |
| Storage      | On-device, via `@capacitor/preferences` |
| CSV parsing  | PapaParse                               |
| CI           | GitHub Actions: lint, web build, debug APK on every push |

Data never leaves the phone. There's no account, no analytics and no third-party SDK. Backups are a JSON file sent through the Android share sheet.

**Source:** [github.com/bharathunni/finbuddy-bookkeeping](https://github.com/bharathunni/finbuddy-bookkeeping), MIT licensed. **Demo:** [bharathunni.github.io/Finbuddy-bookkeeping](https://bharathunni.github.io/Finbuddy-bookkeeping/). Every CI run on `main` produces a debug APK you can sideload on Android 7.0 or later.[^2]

[^1]: Under the Companies (Accounts) Rules, accounting software must keep an edit log of every change, and the log can't be switched off.
[^2]: Download it from the run's Artifacts on the repository's Actions tab, as `FinBuddy-debug-apk`.
