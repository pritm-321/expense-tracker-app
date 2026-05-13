# Expense Tracker

Personal expense tracker Android app. Log income and expenses, view monthly summaries, and break down spending by category. Fully offline — all data stored locally via SQLite.

## Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.11+ |
| UI | KivyMD (Material Design) |
| Storage | SQLite |
| Build | Buildozer → APK |
| Package manager | uv |
| Target | Android API 33+, minSdk 21 |

---

## Desktop Setup

Desktop is the fast development loop — no APK build required.

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (`pip install uv`)

**Windows extra:** Kivy requires the Visual C++ redistributable. Install it from [Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) if `python main.py` fails with a DLL error.

### Install dependencies

```bash
uv pip install -r requirements.txt
```

### Run

```bash
python main.py
```

### Other commands

```bash
pytest          # run tests
ruff check .    # lint
ruff format .   # format
mypy .          # type check
```

---

## Android (Mobile) Setup

Building the APK requires Buildozer, which only runs on a POSIX environment (Linux/macOS). Windows users must go through WSL2 — the steps are fully covered below.

Choose your OS:

- [macOS](#macos)
- [Windows (via WSL2)](#windows-via-wsl2)

---

### macOS

#### Step 1 — Install system dependencies

```bash
brew install autoconf automake libtool pkg-config openssl
```

Install Java JDK 17 (required by the Android toolchain):

```bash
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
java -version   # should print openjdk 17.x.x
```

#### Step 2 — Install Buildozer

```bash
pip install buildozer
```

#### Step 3 — Enable USB debugging on your Android device

1. Open **Settings → About phone**
2. Tap **Build number** 7 times to unlock Developer Options
3. Go to **Settings → Developer options** → enable **USB debugging**
4. Connect device via USB and accept the trust prompt on the device

Verify device is visible:

```bash
adb devices   # should list your device, not "unauthorized"
```

If `adb` is not found, install Android platform-tools:

```bash
brew install android-platform-tools
```

#### Step 4 — Build and deploy

From the project root:

```bash
buildozer android debug deploy run logcat
```

> **First build: 30–60 minutes.** Buildozer downloads NDK and builds Python from source. Subsequent builds use the cache and are much faster.

To build a release APK (unsigned):

```bash
buildozer android release
```

Output lands in `bin/`.

To clean the build cache:

```bash
buildozer android clean
```

---

### Windows (via WSL2)

Buildozer does not run on Windows natively. The approach:

- **Buildozer** runs inside WSL2 (Ubuntu)
- **USB device** is forwarded from Windows to WSL2 via `usbipd`
- **adb** runs inside WSL2 and communicates with the device

#### Step 1 — Enable WSL2

Open **PowerShell as Administrator**:

```powershell
wsl --install
```

Reboot when prompted. After reboot, open **Ubuntu** from the Start menu and complete the initial user setup.

If WSL is already installed but on version 1:

```powershell
wsl --set-default-version 2
wsl --set-version Ubuntu 2
```

Verify:

```powershell
wsl -l -v   # VERSION column should show 2
```

#### Step 2 — Install usbipd (USB forwarding to WSL2)

In **PowerShell as Administrator**:

```powershell
winget install --interactive --exact dorssel.usbipd-win
```

Reboot after installation.

#### Step 3 — Forward Android device USB to WSL2

Enable USB debugging on your Android device (same as macOS Step 3 above).

Plug in your device, then in **PowerShell as Administrator**:

```powershell
usbipd list                        # note the BUSID of your Android device (e.g. 2-3)
usbipd bind --busid 2-3            # run once to allow sharing
usbipd attach --wsl --busid 2-3    # run each session to attach to WSL2
```

Verify inside the WSL2 Ubuntu terminal:

```bash
adb devices   # should show your device serial, not "unauthorized"
```

If `adb` is not found inside WSL2:

```bash
sudo apt install -y adb
```

> You must re-run `usbipd attach` each time you reconnect the device or restart WSL2.

#### Step 4 — Install build dependencies inside WSL2

Open the **Ubuntu** terminal (WSL2):

```bash
sudo apt update
sudo apt install -y \
    git zip unzip openjdk-17-jdk \
    python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev adb

pip install buildozer
```

#### Step 5 — Clone the repo inside WSL2

> **Important:** Keep the repo inside the WSL2 filesystem (`~/` or `/home/<user>/`). Cloning under `/mnt/c/` causes severe build slowdowns due to filesystem translation overhead.

```bash
cd ~
git clone <repo-url>
cd expense-tracker-app
```

#### Step 6 — Build and deploy

```bash
buildozer android debug deploy run logcat
```

> **First build: 30–60 minutes.** Same as macOS — NDK download + Python source build. Cached after that.

To build a release APK:

```bash
buildozer android release
```

Output lands in `bin/`.

To clean:

```bash
buildozer android clean
```

---

## Device Utilities

```bash
adb devices              # list connected devices
adb logcat | grep python # filter logs to Python output
```

---

## Project Structure

```
.
├── main.py                       # App entry point (required name for python-for-android)
├── app/
│   ├── screens/
│   │   ├── home.py               # Dashboard: monthly summary + recent transactions
│   │   ├── add_transaction.py    # Add income or expense
│   │   ├── history.py            # All transactions, filterable by month
│   │   └── categories.py         # Category breakdown + manage categories
│   ├── widgets/
│   │   ├── transaction_card.py   # Single transaction row
│   │   └── category_chart.py     # Pie/bar chart for the month
│   ├── models/
│   │   ├── transaction.py        # Transaction dataclass
│   │   └── category.py           # Category dataclass
│   └── services/
│       ├── db.py                 # SQLite connection + schema migrations
│       ├── repository.py         # Transaction & category CRUD
│       └── analytics.py          # Monthly totals, category aggregation
├── assets/                       # Icons, fonts, KV layout files
├── tests/                        # Mirrors app/ layout
├── buildozer.spec                # Android build config
├── requirements.txt              # Desktop dependencies
└── pyproject.toml
```

---

## Key Conventions

- **Money is never a float.** Stored as integer minor units (e.g., ₹125.50 → `12550`). Use `Decimal` for arithmetic; convert to display string only at the UI layer.
- **Dates** stored as ISO 8601 strings (`YYYY-MM-DD`). Pass `datetime` objects between layers.
- **No `print()`** — use `from kivy.logger import Logger` so output reaches `logcat` on device.
- **DB path on Android:** `App.get_running_app().user_data_dir + '/expenses.db'`. Never hardcode.

---

## Adding a Dependency

Update **both** files:

1. `requirements.txt` — for desktop dev
2. `buildozer.spec` under `requirements =` — for APK build

If the package has native code (numpy, pillow, etc.), verify a [python-for-android recipe](https://github.com/kivy/python-for-android/tree/develop/pythonforandroid/recipes) exists before adding.

---

## What Not to Commit

```
.buildozer/
bin/
*.apk
expenses.db
```
