<!--
Formatting Standards (apply when exporting to PDF/DOCX — e.g. via pandoc):
  Paper size : A4
  Margins    : Left 1.5 in, Right/Top/Bottom 1 in
  Body font  : Times New Roman, 12 pt
  Headings   : Times New Roman, 14–16 pt, Bold
  Line spacing : 1.5
  Alignment  : Justified
  Page numbers : Bottom center or right
  Binding    : Spiral / Hard bound as per college rule
Export command (example):
  pandoc PROJECT_DOCUMENTATION.md -o PROJECT_DOCUMENTATION.pdf \
    -V geometry:a4paper -V geometry:"left=1.5in,right=1in,top=1in,bottom=1in" \
    -V mainfont="Times New Roman" -V fontsize=12pt -V linestretch=1.5
-->

<div align="center">

College Logo
*(Paste Logo Here)*

# PROJECT DOCUMENTATION

# Expense Tracker — Offline Personal Finance Android App

</div>

---

### Submitted By

| | |
|---|---|
| **Name of Student:** | ____________________ |
| **Roll Number:** | ____________________ |
| **Registration Number:** | ____________________ |
| **Department:** | ____________________ |
| **Semester:** | ____________________ |

### Submitted To

| | |
|---|---|
| **College Name:** | ____________________ |
| **Department Name:** | ____________________ |
| **Subject Name:** | ____________________ |
| **Project Guide / Faculty Name:** | ____________________ |

**Submitted In Partial Fulfillment of the Requirement for**
(Write Course / Degree Name) ____________________

**Academic Session: 2025 – 2026**

**Submission Date:** ____________________

<div style="page-break-after: always;"></div>

---

## 1. Declaration by the Student

I, ____________________ (Name of Student), hereby declare that the project titled
**"Expense Tracker — Offline Personal Finance Android App"** is my original work. It has
not been submitted previously for any other degree, diploma, or fellowship. All sources
used have been appropriately acknowledged.

Signature: ____________________   Date: ____________________

## 2. Certificate by the Guide / Head of Department

This is to certify that the project entitled **"Expense Tracker — Offline Personal Finance
Android App"** has been carried out by ____________________ (Roll No. ________) under my
guidance. The work is original and satisfactory for the partial fulfillment of the
requirements for the degree/course.

Guide Signature: ____________________   Date: ____________________

HOD Signature: ____________________   Date: ____________________

## 3. Acknowledgement

I wish to express my sincere gratitude to my project guide ____________________ for their
invaluable guidance. I also thank the Head of Department, faculty members, and the college
administration for providing necessary facilities. Special thanks to my family and friends
for their constant support.

Place: ____________________   Signature: ____________________

## 4. Abstract / Executive Summary

Managing personal finances on mobile devices often requires accounts, internet
connectivity, or paid subscriptions, raising privacy and accessibility concerns. This
project develops **Expense Tracker**, a fully offline Android application that lets a user
record income and expenses, review monthly summaries (total in, total out, net), and
analyse spending by category — with all data stored locally on the device. The application
is built in Python using the KivyMD Material-Design UI framework, an SQLite database for
on-device persistence, and Buildozer to package the project into an Android APK. The
methodology follows a layered architecture that strictly separates the user interface
(screens) from business logic (services), with money stored as integer minor units and
computed using `Decimal` to eliminate floating-point errors. Beyond core logging, the
delivered system adds transaction editing, multi-criteria search and filtering, a settings
screen with configurable currency and theme, and per-category monthly budgets with
over-budget indication. The service layer is covered by an automated test suite of 16
passing tests. The result is a private, dependency-free, install-and-use expense manager
that works without any network connection, demonstrating practical mobile application
engineering, schema-versioned data storage, and disciplined money handling.

**Keywords:** Expense Tracker , Python / KivyMD , Offline Mobile App , SQLite , Personal Finance

<div style="page-break-after: always;"></div>

## 5. Table of Contents

1. Declaration ...................................................................... i
2. Certificate ..................................................................... ii
3. Acknowledgement ........................................................ iii
4. Abstract ........................................................................ iv
5. List of Figures/Tables ................................................... v
6. Chapter 1: Introduction ................................................. 1
7. Chapter 2: Literature Review ......................................... 5
8. Chapter 3: System Design ............................................. 10
9. Chapter 4: Implementation ............................................ 15
10. Chapter 5: Testing & Results ....................................... 20
11. Chapter 6: Conclusion & Future Scope ........................ 24
12. References .................................................................... 26
13. Appendices .................................................................. 28

## 6. List of Figures / Tables

**Figures:**

- Figure 3.1: System Architecture Diagram
- Figure 3.2: Database Entity-Relationship Overview
- Figure 4.1: Home Screen (Monthly Summary)

**Tables:**

- Table 3.1: Transactions Table Schema
- Table 5.1: Test Case Results

<div style="page-break-after: always;"></div>

## Chapter 1: Introduction

### 1.1 Background

Personal expense tracking helps individuals understand cash flow, control spending, and
plan savings. Most popular mobile finance apps require account creation, cloud sync, or an
internet connection, and frequently display advertisements or lock features behind
subscriptions. For many users — especially students and privacy-conscious individuals — a
simple, private, offline tool is preferable. This project addresses that gap with a
lightweight Android application that keeps every record on the device and needs no network
permission.

### 1.2 Problem Statement

There is no simple, fully offline, ad-free Android application that allows a user to log
income and expenses, view a clear monthly summary, analyse category-wise spending, and
enforce budgets, while guaranteeing that financial data never leaves the device and that
monetary values are stored and computed without rounding errors.

### 1.3 Objectives

- **Objective 1:** Build an offline Android app to record income/expense transactions with
  category, date, and note, storing all data locally in SQLite.
- **Objective 2:** Provide monthly summaries (income, expense, net) and category-wise
  breakdown analytics, with editing, search/filter, and per-category monthly budgets.
- **Objective 3:** Enforce correct money handling (integer minor units + `Decimal`
  arithmetic), a clean UI/logic separation, schema-versioned migrations, and an automated
  test suite for the business-logic layer.

### 1.4 Scope and Limitations

**In scope:** single-user offline use; income/expense logging; edit and delete; monthly
totals and category breakdown; search/filter (type, category, note text); PIN lock;
configurable currency symbol and light/dark theme; per-category monthly budgets with
over-budget indication; Android APK packaging.

**Limitations:** single device, no cloud sync or multi-device backup; one PIN, no
biometric or lockout; currency is a display symbol only (no foreign-exchange conversion);
budgets are monthly and shown for categories that have spending in the selected month;
recurring transactions, attachments, and CSV export are not implemented (listed as future
scope).

## Chapter 2: Literature Review / Related Work

Existing solutions broadly fall into three groups. **Cloud-based apps** (e.g., typical
commercial expense managers) offer multi-device sync but require accounts and an internet
connection, creating privacy exposure and a hard dependency on connectivity.
**Spreadsheet-based tracking** (manual entry into a mobile spreadsheet) is fully
user-controlled but error-prone, has no input validation, and offers no structured
analytics. **Offline note/ledger apps** are private but usually lack category analytics,
budgets, or correct monetary arithmetic (many store money as floating point, introducing
rounding errors).

The relevant technical literature and documentation informing this project include the
Kivy and KivyMD framework documentation (cross-platform Python UI), the SQLite
documentation (embedded, serverless database suited to on-device storage), the
python-for-android / Buildozer toolchain (Python-to-APK packaging), and Python's `decimal`
module documentation (exact decimal arithmetic for financial values). This project
combines the privacy of offline ledger apps with the structured analytics and budgeting of
commercial apps, while explicitly adopting integer-minor-unit storage with `Decimal`
computation to avoid the floating-point pitfalls common in naive implementations.

## Chapter 3: System / Project Design

### 3.1 Architecture

The application uses a layered architecture with a strict separation between presentation
and logic. Screens handle only layout and user input; all database access and computation
go through the services layer.

**Figure 3.1: System Architecture Diagram**

```
+-----------------------------------------------------------+
|                     Presentation Layer                    |
|  Screens: login, home, add_transaction, history,          |
|           categories, settings                            |
|  Widgets: transaction_card, category_chart, bottom_nav    |
|  Layouts: assets/*.kv (KivyMD Material Design)            |
+----------------------------+------------------------------+
                             | calls (no SQL in screens)
                             v
+-----------------------------------------------------------+
|                       Service Layer                       |
|  db.py         - connection + versioned migrations        |
|  repository.py - transaction & category & budget CRUD     |
|  analytics.py  - monthly totals, category breakdown,      |
|                  budget status                            |
|  auth.py       - PIN set / verify (salted SHA-256)        |
|  settings.py   - key/value app settings                   |
|  utils/format  - central currency formatter               |
+----------------------------+------------------------------+
                             | sqlite3
                             v
+-----------------------------------------------------------+
|                  Data Layer (SQLite file)                 |
|  tables: schema_version, categories, transactions,        |
|          settings, budgets                                 |
|  location: <app user_data_dir>/expenses.db (on device)    |
+-----------------------------------------------------------+
```

**Figure 3.2: Database Entity-Relationship Overview**

```
categories (1) ----<  (N) transactions
     |  id                     category_id  (FK -> categories.id)
     |
     +----<  (0..1) budgets
                 category_id  (PK, FK -> categories.id)

settings (key -> value)       : PIN hash/salt, currency_symbol, theme
schema_version (version)      : tracks applied migration level
```

### 3.2 Modules Description

- **Module 1 — User Interface (screens + widgets + assets):** `LoginScreen` (PIN setup /
  verify), `HomeScreen` (monthly summary + recent transactions), `AddTransactionScreen`
  (add **and edit** a transaction), `HistoryScreen` (all transactions for a month with
  search and filters, edit and delete), `CategoriesScreen` (category-wise breakdown +
  per-category budget management), `SettingsScreen` (currency symbol + theme). Reusable
  widgets: `TransactionCard`, `BottomNavBar`.
- **Module 2 — Data & Logic Services:** `db.py` (SQLite connection, append-only migration
  list, default category seeding), `repository.py` (CRUD for transactions, categories,
  budgets, plus multi-criteria filtering), `analytics.py` (`monthly_totals`,
  `category_breakdown`, `budget_status`), `auth.py` (salted SHA-256 PIN), `settings.py`
  (key/value settings), `utils/format.py` (single currency formatter used by all screens).
- **Module 3 — Data Model:** `Transaction`, `Category`, and `Budget` dataclasses defining
  the typed objects passed between layers (raw SQL rows never escape the repository).

### 3.3 Tools & Technologies Used

- **Frontend:** KivyMD (Material Design widgets on Kivy 2.3); KV layout files
- **Backend:** Python 3.11+ (application logic in the services layer)
- **Database:** SQLite (embedded, on-device, accessed via Python's `sqlite3`)
- **Others:** Buildozer + python-for-android (APK build); pytest (testing); ruff
  (lint/format); mypy (type checking); `decimal.Decimal` (exact money arithmetic);
  Android API 33+ target, minSdk 21

<div style="page-break-after: always;"></div>

## Chapter 4: Implementation

The application entry point is `main.py`, which initialises the database, applies the
persisted theme, registers all screens with a `ScreenManager`, and launches the app.

**Working process (typical flow):**

1. **Launch & lock:** `init_db()` runs pending migrations and seeds default categories on
   first run. `LoginScreen` either sets a new PIN or verifies the existing one (salted
   SHA-256, timing-safe comparison).
2. **Add transaction:** the user picks Income/Expense, a category, amount, date, and an
   optional note. The amount entered in rupees is converted to integer **paise** before
   storage; validation rejects empty/invalid/non-positive amounts.
3. **View & analyse:** `HomeScreen` shows the current month's income, expense, and net.
   `CategoriesScreen` shows a category-wise breakdown with progress bars.
4. **Edit / search:** from `HistoryScreen`, the pencil button reopens the entry form
   pre-filled for editing; the search field and Income/Expense/category filters narrow the
   list.
5. **Settings:** the user changes the currency symbol or toggles the light/dark theme;
   choices persist in the `settings` table and apply across all screens.
6. **Budgets:** from `CategoriesScreen`, a per-category monthly budget can be set; spend is
   shown as `spent / budgeted` and turns red when over budget.

**Figure 4.1: Home Screen (Monthly Summary)** *(insert screenshot of `python main.py`
running the Home screen here)*

Representative code segments are listed in **Appendix B**. Key implementation conventions:

- **Money is never a float.** Stored as integer minor units; computed with `Decimal`;
  formatted only at the UI layer through one helper, `utils/format.format_money()`.
- **No SQL in screens.** Screens call repository/analytics functions only.
- **Schema migrations are append-only.** Each schema change adds a new entry to
  `MIGRATIONS`; existing entries are never edited (latest version: v3 — `budgets`).
- **Logging, not printing.** `kivy.logger.Logger` is used so output reaches Android
  `logcat`.

## Chapter 5: Testing & Results

### 5.1 Test Cases

Automated tests target the service layer (where defects are most costly). They use a
temporary SQLite database via a monkeypatched DB path, so tests are isolated and do not
touch real data.

**Table 5.1: Test Case Results**

| # | Test Case | Module | Expected | Result |
|---|-----------|--------|----------|--------|
| 1 | Create tables + settings + budgets on init | db | All tables exist | Pass |
| 2 | Seed default categories (7 expense + 3 income) | db | Count = 10 | Pass |
| 3 | `init_db()` idempotent on second call | db | No duplicate seeds | Pass |
| 4 | Add → update → delete transaction | repository | Values reflect each step | Pass |
| 5 | Filter by type / category / note text | repository | Correct subset returned | Pass |
| 6 | Budget set / upsert / delete | repository | CRUD correct | Pass |
| 7 | Monthly totals — empty month | analytics | income=expense=net=0 | Pass |
| 8 | Monthly totals — with data | analytics | Correct income/expense/net | Pass |
| 9 | Monthly totals — ignores other months | analytics | Other month excluded | Pass |
| 10 | Category breakdown aggregation | analytics | Correct per-category total | Pass |
| 11 | Budget status — over budget flagged | analytics | `over = True`, remaining negative | Pass |
| 12 | Budget status — no budgets | analytics | Empty list | Pass |
| 13 | Get setting — default fallback | settings | Returns provided default | Pass |
| 14 | Set / get / upsert setting | settings | Latest value returned | Pass |
| 15 | Money formatter — default ₹ symbol | utils.format | "₹125.50" etc. | Pass |
| 16 | Money formatter — honors currency setting | utils.format | "$125.50" | Pass |

**Summary:** 16 / 16 automated tests passed (`pytest -q` → `16 passed`). All application
modules byte-compile; all six KV layout files parse and screen classes resolve.

### 5.2 Output Screenshots

*(Place screenshots here — run `python main.py` on desktop and capture: Login/PIN, Home
summary, Add Transaction, History with filters, Categories with a budget over-limit (red),
Settings with currency/theme.)*

### 5.3 Performance Analysis

The database is a local SQLite file; all queries are single-table or simple joins with
month-prefix or indexed primary-key lookups, so typical operations complete in
milliseconds. The service test suite runs in well under one second. The main UI
consideration is that Kivy is single-threaded — very large history lists should update the
UI from a worker thread (`@mainthread`) to avoid frame drops; current data volumes for a
personal user are well within smooth interactive limits.

## Chapter 6: Conclusion & Future Scope

### 6.1 Conclusion

The project delivers a working, fully offline personal expense tracker for Android. It
meets all stated objectives: local income/expense logging with categories, monthly and
category analytics, transaction editing, multi-criteria search/filter, configurable
currency and theme, and per-category monthly budgets — built on a clean layered
architecture with disciplined money handling and an automated, passing test suite.

### 6.2 Limitations

Single-device only (no sync/backup); single PIN with no biometric or failed-attempt
lockout; currency is a display symbol with no FX conversion; budgets are monthly and
appear for categories that have spending in the selected month; no recurring transactions,
attachments, or data export yet.

### 6.3 Future Enhancements

- Recurring transactions (salary/rent auto-entry)
- CSV / JSON export and backup-restore
- Spending trend charts and year-to-date analytics (reuse the `category_chart` widget)
- Biometric unlock and failed-attempt lockout
- Receipt photo attachments per transaction
- Category management UI (add / rename / delete custom categories)

## 7. References / Bibliography

[1] Kivy Project. *Kivy: Cross-platform Python framework — Documentation.* Available: https://kivy.org/doc/stable/
[2] KivyMD. *KivyMD: Material Design components for Kivy — Documentation.* Available: https://kivymd.readthedocs.io/
[3] SQLite Consortium. *SQLite Documentation.* Available: https://www.sqlite.org/docs.html
[4] Python Software Foundation. *`decimal` — Decimal fixed point and floating point arithmetic.* Available: https://docs.python.org/3/library/decimal.html
[5] Kivy Organisation. *python-for-android & Buildozer Documentation.* Available: https://buildozer.readthedocs.io/

<div style="page-break-after: always;"></div>

## 8. Appendices

### Appendix A: User Manual

1. **Install / run (desktop):** `uv pip install -r requirements.txt`, then `python main.py`.
2. **First launch:** set a 4-digit PIN; re-enter to confirm.
3. **Add a transaction:** Home → **+** → choose Income/Expense, category, amount, date,
   optional note → **Save**.
4. **Edit / delete:** History tab → pencil icon to edit (form opens pre-filled), trash icon
   to delete (with confirmation).
5. **Search / filter:** History tab → type in the search box; use All/Income/Expense and
   the category filter.
6. **Budgets:** Categories tab → wallet icon on an expense category → enter a monthly
   budget; the row shows `spent / budgeted` and turns red when over.
7. **Settings:** Settings tab (gear) → choose currency symbol; toggle Light/Dark theme.
   Choices persist between launches.
8. **Build APK (Android):** `buildozer android debug deploy run logcat`.

### Appendix B: Source Code (key segments)

**B.1 Versioned migrations — append-only (`app/services/db.py`):**

```python
MIGRATIONS: list[str] = [
    # v0 -> v1: initial schema (categories, transactions, schema_version)
    "...",
    # v1 -> v2: settings key/value table (PIN hash, etc.)
    "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);",
    # v2 -> v3: per-category monthly budgets
    """
    CREATE TABLE IF NOT EXISTS budgets (
        category_id INTEGER PRIMARY KEY REFERENCES categories(id),
        amount      INTEGER NOT NULL,
        period      TEXT NOT NULL DEFAULT 'monthly' CHECK(period IN ('monthly'))
    );
    """,
]
```

**B.2 Correct money handling — central formatter (`app/utils/format.py`):**

```python
def format_money(minor_units: int | Decimal) -> str:
    """Format integer minor units (paise) as a currency string for display only."""
    major = Decimal(minor_units) / 100
    return f"{currency_symbol()}{major:,.2f}"
```

**B.3 Multi-criteria filtering (`app/services/repository.py`):**

```python
def get_transactions(month=None, tx_type=None, category_id=None, note_query=None):
    clauses, params = [], []
    if month is not None:
        clauses.append("date LIKE ?"); params.append(f"{month:%Y-%m}%")
    if tx_type is not None:
        clauses.append("type = ?"); params.append(tx_type)
    if category_id is not None:
        clauses.append("category_id = ?"); params.append(category_id)
    if note_query:
        clauses.append("note LIKE ?"); params.append(f"%{note_query}%")
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT * FROM transactions{where} ORDER BY date DESC"
    ...
```

**B.4 Budget status analytics (`app/services/analytics.py`):**

```python
def budget_status(month):
    # join budgets with this month's expense totals; per category:
    # budgeted, spent, remaining, pct, over (spent > budgeted)
    ...
```

### Appendix C: Plagiarism Report

*(Attach the plagiarism / similarity report generated by the institution's tool here.)*

---

*Project Documentation Template – Academic Session 2025-2026*
