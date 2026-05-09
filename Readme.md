next Readme.md

Here is a **concise, single‑file `README.md`** for your **Tkinter‑mobile‑PFM** app.  
You can drop this into `pfman_tk/README.md` and it will match the file‑by‑file structure you just built.

***

```markdown
# PFM – Personal Finance Manager (Tkinter Mobile Edition)

A **single‑user** personal finance manager built with **Python + Tkinter + SQLite**, designed for:

- tracking **accounts**, **transactions**, **budgets**, and **savings goals**,  
- managing **family members** (self, spouse, child, etc.),  
- supporting **assets, loans, investments**,  
- and providing **simple backup** for your data (`data/pfm.db`).

The UI is mobile‑focused (tall portrait layout, small touch‑friendly tabs) and runs directly in **Pydroid** or any Python‑Tkinter‑friendly environment.

## 📦 Project Structure

```text
pfman_tk/
├── main.py           # Root app: landing page, quick‑expense, dashboard tabs
├── db.py             # SQLite schema (accounts, transactions, budgets, goals, family, assets, loans, investments, presets)
├── models.py         # Typed dicts for all entities (Account, Transaction, Budget, Goal, Individual, etc.)
├── accounts.py       # Account list + UI (creates, edits, shows balances)
├── transactions.py   # Transaction CRUD with preset categories and auto balance update
├── budgets.py        # Monthly budget targets per category (linked to presets)
├── goals.py          # Savings goals with progress % and auto / manual amount update
├── family.py         # Family / individuals tab (self, spouse, child, linked accounts)
├── backup_ui.py      # Backup status panel + one‑click backup of data/pfm.db
└── README.md         # This file
```

## ✅ Features

- **Landing UI**  
  - Shows **total balance** and short account list.  
  - Has a **quick “Add Expense” box** with **preset categories** so you type as little as possible.

- **Accounts**  
  - Supports types: `checking`, `savings`, `investment`, `loan`, `credit_card`.  
  - Balances update automatically when you post transactions.

- **Transactions**  
  - Records **income, expenses, transfers**.  
  - Uses **preset categories** (`groceries`, `utilities`, `entertainment`, `salary`, etc.).  
  - UI auto‑reloads after insert.

- **Budgets**  
  - Set **monthly targets** per category (exp/ncome).  
  - Can later wire to AI‑advice or dashboards.

- **Savings Goals**  
  - Define **name, category, target, target date**.  
  - Shows **progress %** text‑style; `current_amount` can be updated manually or from transactions.

- **Family / Individuals**  
  - Track **self, spouse, child, other**.  
  - Link each person to an **income** and **expense** account for reporting.

- **Assets, Loans, Investments**  
  - Track real estate, vehicles, loans, equities, etc.  
  - Independent of regular accounts for reporting.

- **Backup & Restore**  
  - Automatic backup to `data/backups/pfm_backup_YYYYMMDD_HHMMSS.db`.  
  - `backup_ui.py` shows backup list and lets you create new backups.

## 📦 Prerequisites

- Python 3.9+  
- `tkinter` (usually included with standard Python; on some Linux distros you may need: `sudo apt install python3-tk`)  

For Android (Pydroid): install a Python‑Tkinter package that exposes `tkinter` in the app.

## ⚙️ Setup & Running

1. Clone or create the project:

   ```bash
   mkdir pfman_tk
   cd pfman_tk
   # copy all .py files here
   ```

2. Ensure directory structure:

   ```bash
   pfman_tk/
   ├── main.py
   ├── db.py
   ├── models.py
   ├── accounts.py
   ├── transactions.py
   ├── budgets.py
   ├── goals.py
   ├── family.py
   ├── backup_ui.py
   └── README.md
   ```

3. Install requirements (only `tkinter` needed; no extra pip if already included):

   ```bash
   # typically nothing extra; if you use other helpers later:
   pip install some-extra-package
   ```

4. Run the app:

   ```bash
   python main.py
   ```

   - The app will:
     - auto‑create `data/pfm.db` on first run,  
     - show a **mobile‑style UI** with tabs.

## 📱 UI Layout (Tabs)

Once the app starts:

- **Main view**  
  - Total balance, short account preview, recent expenses, “Add Expense” box.

- **📊 Transactions Tab**  
  - Full list of income / expenses, presets for categories.

- **🏦 Accounts Tab**  
  - All accounts with current balances.

- **🎯 Budgets Tab**  
  - Monthly targets per category (preset‑category‑aware).

- **🚀 Goals Tab**  
  - Savings goals with progress %.

- **👪 Family Tab**  
  - Manage family members and link them to accounts.

- **💾 Backups Tab** (or popup)  
  - List existing backups and create new ones.

## 🧩 Data Model Highlights

Tables (from `db.py`):

- `accounts` – bank, savings, investment, etc.  
- `transactions` – with `type` and `category` (from `preset_categories`).  
- `budgets` – monthly per‑category targets.  
- `goals` – savings‑goal tracking.  
- `individuals` – family members.  
- `assets` – real estate, vehicles, properties.  
- `loans` – personal, home, vehicle, education, etc.  
- `investments` – equities, mutual funds, gold, etc.  
- `preset_categories` – reusable categories for UI (income/expense).

All data lives in `data/pfm.db`. Backups go to `data/backups/`.

## 💾 Backup & Data Safety

Use the **Backup** UI to:

- create time‑stamped backups of `data/pfm.db`,  
- list existing backups,  
- keep a copy off‑device (e.g., cloud drive).

Manually you can:

```bash
cp data/pfm.db /some/backup/location/pfm-$(date +%Y%m%d).db
```

This is your **only financial data**, so treat it like a ledger.

## 📝 Extensibility Ideas

You can later extend this app by:

- wiring **AI‑advice** into the UI (budget vs actual, risk flags),  
- adding **reports** (monthly summaries, charts),  
- exporting to **CSV/Excel**,  
- or adding a small **web app** (FastAPI wrapper) that talks to the same `pfm.db`.

## 📚 References

- Tkinter + SQLite basics –  
  https://www.w3resource.com/python-exercises/tkinter/  
- Python GUI + SQLite tutorials –  
  https://www.geeksforgeeks.org/python/python-tkinter-listbox-widget/  
- Personal finance trackers with Tkinter –  
  https://datacoach.in/build-a-personal-budget-tracker-with-tkinter-and-sqlite-in-python/
```

***

This `README.md` steps your future‑you through:

- what the app is,  
- how to run it,  
- what each file does,  
- and how to keep data safe.

If you want, the **next step** can be a **tiny `start.py`** or **`main.py` comment block** that explains the “launch sequence” for Pydroid specifically.

