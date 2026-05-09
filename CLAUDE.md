pip3# Project Overview

A personal **Expense Tracker** Android app built in Python. Lets the user log income and expenses, view a monthly summary (total in, total out, net), and see spending broken down by category. Fully offline — all data stored locally on-device.

## Stack

- **Language:** Python 3.11+
- **UI Framework:** KivyMD (Material Design widgets on top of Kivy)
- **Storage:** SQLite (built into Python — no extra recipe needed for python-for-android)
- **Build Tool:** Buildozer → APK
- **Package Manager:** uv (swap commands for pip/poetry as needed)
- **Target:** Android API 33+, minSdk 21

## Commands

### Desktop development (use this — much faster than rebuilding the APK)

- Install deps: `uv pip install -r requirements.txt`
- Run app: `python main.py`
- Run tests: `pytest`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy .`

### Android build

- First-time init (only once): `buildozer init`
- Debug APK + deploy + tail logs: `buildozer android debug deploy run logcat`
- Release APK: `buildozer android release`
- Clean: `buildozer android clean`

### Device

- `adb devices` — list connected devices
- `adb logcat | grep python` — filter to Python output

## Project Structure

```
.
├── main.py                       # App entry — python-for-android REQUIRES this name
├── app/
│   ├── screens/
│   │   ├── home.py               # Dashboard: current month summary + recent transactions
│   │   ├── add_transaction.py    # Form to add income or expense
│   │   ├── history.py            # All transactions, filterable by month
│   │   └── categories.py         # Category-wise breakdown + manage categories
│   ├── widgets/
│   │   ├── transaction_card.py   # Single transaction row
│   │   └── category_chart.py     # Pie/bar breakdown for the month
│   ├── models/
│   │   ├── transaction.py        # Transaction dataclass
│   │   └── category.py           # Category dataclass
│   └── services/
│       ├── db.py                 # SQLite connection + schema migrations
│       ├── repository.py         # Transaction & category CRUD
│       └── analytics.py          # Monthly totals, category aggregation
├── assets/                       # Icons, fonts, .kv layout files
├── tests/                        # Mirrors app/ layout
├── buildozer.spec                # Android build config — edit in place
├── requirements.txt              # Must mirror buildozer.spec `requirements =`
└── pyproject.toml
```

## Data Model

**Transaction** (single row in `transactions` table):

| Field         | Type       | Notes                                        |
| ------------- | ---------- | -------------------------------------------- |
| `id`          | INTEGER PK | autoincrement                                |
| `type`        | TEXT       | `'income'` or `'expense'` — enforced in code |
| `amount`      | INTEGER    | stored as **minor units** (paise/cents)      |
| `category_id` | INTEGER FK | references `categories(id)`                  |
| `date`        | TEXT       | ISO 8601 `YYYY-MM-DD`                        |
| `note`        | TEXT       | optional, user-provided                      |
| `created_at`  | TEXT       | ISO 8601 timestamp, set by DB                |

**Category**: `id`, `name`, `kind` (`'income'` | `'expense'`), `icon`, `color`.

Default categories seeded on first launch: _Food, Transport, Bills, Shopping, Entertainment, Health, Other_ (expense) and _Salary, Gift, Other_ (income).

## Conventions

- **Money is NEVER stored as float.** Store as integer minor units in DB (e.g., ₹125.50 → `12550`). In Python, convert to `Decimal` for any arithmetic. Format for display only at the UI layer.
- **Dates** use `datetime.date.isoformat()` (`YYYY-MM-DD`) for storage. Pass `datetime` objects between layers, never raw strings.
- **Separate UI from logic.** Screens in `app/screens/` only handle layout + user input; all DB and computation goes through `app/services/`.
- **Type hints** on every public function. Use `from __future__ import annotations` at top of each module.
- **No `print()`.** Use `from kivy.logger import Logger` so logs reach `logcat`.
- **Tests** mirror source layout under `tests/`. Cover `services/` thoroughly — that's where bugs hurt.

## Adding a Dependency

Update **both**:

1. `requirements.txt` (desktop dev)
2. `buildozer.spec` under `requirements =` (APK build)

If the package has native code (e.g., numpy, pillow, matplotlib), check it has a python-for-android recipe before adding: https://github.com/kivy/python-for-android/tree/develop/pythonforandroid/recipes — pure-Python packages usually work fine.

## Gotchas

- **DB location on Android:** SQLite file lives at `App.get_running_app().user_data_dir + '/expenses.db'`. Never hardcode paths — they differ between desktop and device.
- **First buildozer build:** 30–60 min (downloads NDK + builds Python). Subsequent builds cache and are fast.
- **Buildozer needs Linux/macOS.** On Windows, use WSL2.
- **Threading:** Kivy is single-threaded. DB queries on the main thread will freeze the UI on large history lists — use `@mainthread` to update UI from a worker thread.
- **Permissions:** this app needs none beyond the default. Don't add `android.permissions = INTERNET` unless we actually add a network feature.
- **Currency display** is `₹` (INR) by default — keep this configurable if internationalizing later.
- **Don't commit** `.buildozer/`, `bin/`, `*.apk`, or `expenses.db`.

## Workflow Preferences

- **Use Plan Mode** (`Shift+Tab` twice) before non-trivial changes — especially anything touching the DB schema, money math, or `buildozer.spec`.
- **Test on desktop first** with `python main.py` before building an APK.
- **For schema changes:** update `services/db.py` migration list. Never edit an existing migration — add a new one.
- **For new screens:** follow the pattern in `app/screens/home.py` — KV layout in `assets/`, Python class in `screens/`.
- **When in doubt about money math:** use `Decimal`, write a test, and round only at display time.
