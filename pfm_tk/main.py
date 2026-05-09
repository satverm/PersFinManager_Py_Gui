"""
PFM – Tkinter Mobile UI (enhanced)

Landing‑style main page:
  - shows total balance, account list, recent expenses,
  - has a quick “Add Expense” with preset categories,
  - exposes backup / preferences buttons.

Requires:
  db.py, models.py, accounts.py, transactions.py, budgets.py, goals.py, ai.py
"""

import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from db import init_db
from accounts import get_accounts as get_accounts_from_db
from transactions import get_transactions as get_recent_transactions
from ai import get_budget_advice


# ------------------------ PRESETS --------------------------------

PRESET_EXPENSE_CATEGORIES = [
    "groceries",
    "utilities",
    "transport",
    "entertainment",
    "dining_out",
    "clothing",
    "health",
    "education",
    "travel",
    "misc"
]


# ------------------------ DB HELPERS (in main for UI props) -----

def get_total_balance() -> float:
    """Compute sum of all active accounts."""
    conn = sqlite3.connect("data/pfm.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(balance) FROM accounts WHERE is_active = 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] or 0.0


def get_account_list() -> list:
    return get_accounts_from_db()


def get_recent_expenses(limit: int = 5) -> list:
    """Get last N expenses (mock list structure)."""
    txns = get_recent_transactions()
    # in real app you’d filter by type == "expense"
    return txns[:limit]


# ------------------------ MAIN UI CLASS -------------------------

class PFMApp(tk.Tk):
    """Main UI: landing page with balances, expenses, presets, and backup."""

    def __init__(self):
        super().__init__()
        self.title("PFM – Personal Finance Manager")
        self.geometry("400x700")  # mobile portrait
        self.minsize(320, 600)

        init_db()  # ensure DB exists

        # Main frame
        main_frame = tk.Frame(self, padx=8, pady=8)
        main_frame.pack(fill="both", expand=True)

        # Header / balance
        header = tk.Frame(main_frame)
        header.pack(fill="x", pady=(0, 12))

        self.balance_label = tk.Label(
            header,
            text="Total Balance: ₹0.00",
            font=("Arial", 14, "bold"),
            fg="#059669",
        )
        self.balance_label.pack(anchor="w")

        # Accounts list (short preview)
        self.accounts_listbox = tk.Listbox(header, height=3)
        self.accounts_listbox.pack(fill="x", pady=(4, 8))

        # Recent transactions (expenses)
        tx_frame = tk.Frame(main_frame)
        tx_frame.pack(fill="x", pady=(0, 12))

        tk.Label(tx_frame, text="Recent Expenses", font=("Arial", 10, "bold")).pack(
            anchor="w"
        )
        self.tx_listbox = tk.Listbox(tx_frame, height=4, width=40)
        self.tx_listbox.pack(fill="x", pady=(4, 0), ipady=0)

        # Quick Add Expense
        expense_frame = tk.LabelFrame(main_frame, text="Add Expense")
        expense_frame.pack(fill="x", pady=(12, 12))

        # Amount
        tk.Label(expense_frame, text="Amount:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.amount_entry = tk.Entry(expense_frame, width=12)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Account
        tk.Label(expense_frame, text="Account:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.accounts_names = [acc["name"] for acc in get_account_list()]
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(
            expense_frame, textvariable=self.account_var, values=self.accounts_names
        )
        self.account_combo.grid(row=1, column=1, padx=5, pady=5)

        # Category (presets)
        tk.Label(expense_frame, text="Category:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            expense_frame, textvariable=self.category_var, values=PRESET_EXPENSE_CATEGORIES
        )
        self.category_combo.grid(row=2, column=1, padx=5, pady=5)

        # Description
        tk.Label(expense_frame, text="Description:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.desc_entry = tk.Entry(expense_frame, width=30)
        self.desc_entry.grid(row=3, column=1, padx=5, pady=5)

        # Submit button
        tk.Button(expense_frame, text="Add Expense", command=self.add_expense).grid(
            row=4, column=0, columnspan=2, pady=8
        )

        # Buttons frame (backup, preferences, tabs)
        buttons = tk.Frame(main_frame)
        buttons.pack(fill="x", pady=(10, 0))

        tk.Button(buttons, text="📊 Full Dashboard", command=self.open_dashboard).pack(
            side="left", padx=2
        )
        tk.Button(
            buttons, text="💾 Backup DB", command=self.backup_db
        ).pack(side="left", padx=2)

        # Load initial data
        self.refresh_ui()

    def refresh_ui(self):
        # Balance
        total = get_total_balance()
        self.balance_label.config(text=f"Total Balance: ₹{total:,.2f}")

        # Accounts
        self.accounts_listbox.delete(0, "end")
        for acc in get_account_list():
            self.accounts_listbox.insert(
                "end", f"{acc['name']} ({acc['type']}) – ₹{acc['balance']:,.2f}"
            )

        # Recent transactions
        self.tx_listbox.delete(0, "end")
        for tx in get_recent_expenses(5):
            line = f"{tx['amount']:,.2f} – {tx.get('category', '—')}"
            self.tx_listbox.insert("end", line)

        # Repopulate account combo if needed
        if self.accounts_names != [acc["name"] for acc in get_account_list()]:
            self.accounts_names = [acc["name"] for acc in get_account_list()]
            self.account_combo["values"] = self.accounts_names

    def add_expense(self):
        """Quick expense entry (mock; you can plug into transactions.py later)."""
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Enter a valid number.")
            return

        if amount <= 0:
            messagebox.showwarning("Invalid Amount", "Amount must be positive.")
            return

        account_name = self.account_var.get()
        if not account_name or account_name not in self.accounts_names:
            messagebox.showwarning("Account", "Select an account.")
            return

        category = self.category_var.get()
        if not category:
            messagebox.showwarning("Category", "Select or type a category.")
            return

        description = self.desc_entry.get().strip()

        # === Here you would plug into real transaction logic ===
        # Example: call a function from transactions.py that:
        #   - inserts transaction,
        #   - updates account balance.
        # For now, this is a placeholder UI.

        conn = sqlite3.connect("data/pfm.db")
        cursor = conn.cursor()
        # (In a real version, you’d fetch account_id from account_name)
        cursor.execute("SELECT id, balance FROM accounts WHERE name = ?", (account_name,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", "Account not found.")
            conn.close()
            return
        account_id, old_balance = row

        # Insert transaction
        cursor.execute(
            "INSERT INTO transactions (account_id, amount, type, category, description) VALUES (?, ?, ?, ?, ?)",
            (account_id, -amount, "expense", category, description),
        )
        # Update account balance
        new_balance = old_balance - amount
        cursor.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id)
        )
        conn.commit()
        conn.close()

        # Refresh UI
        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.refresh_ui()
        messagebox.showinfo("Success", "Expense recorded and balance updated.")

    def backup_db(self):
        """Simple backup: copy pfm.db to backups/ with timestamp."""
        data_dir = os.path.join("data")
        backup_dir = os.path.join("data", "backups")
        os.makedirs(backup_dir, exist_ok=True)

        src = os.path.join(data_dir, "pfm.db")
        if not os.path.exists(src):
            messagebox.showerror("Backup", "Database not found.")
            return

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(backup_dir, f"pfm_backup_{now}.db")
        try:
            import shutil
            shutil.copy2(src, dest)
            messagebox.showinfo(
                "Backup",
                f"Backup saved to {dest}Keep this for safety.",
            )
        except Exception as e:
            messagebox.showerror("Backup Error", str(e))

    def open_dashboard(self):
        """Open a simple notebook dashboard (tabs)."""
        from accounts import AccountsFrame
        from transactions import TransactionsFrame
        from budgets import BudgetsFrame
        from goals import GoalsFrame
        from ai import BudgetAdvice
        from backup_ui import BackupStatusFrame
        from family import FamilyFrame

        tab_window = tk.Toplevel(self)
        tab_window.title("PFM Dashboard")
        tab_window.geometry("400x600")

        notebook = ttk.Notebook(tab_window)
        notebook.pack(fill="both", expand=True, padx=4, pady=4)

        notebook.add(AccountsFrame(notebook), text="🏦 Accounts")
        notebook.add(TransactionsFrame(notebook), text="📊 Transactions")
        notebook.add(BudgetsFrame(notebook), text="🎯 Budgets")
        notebook.add(GoalsFrame(notebook), text="🚀 Goals")
        notebook.add(FamilyFrame(notebook), text="👪 Family")
        notebook.add(BackupStatusFrame(notebook), text="💾 Backups")

        # AI advice (optional, doesn’t affect core)
        try:
            # You can mock actuals / budgets for demo
            actuals = {"groceries": 14800, "rent": 30000, "utilities": 4200, "entertainment": 9500}
            budgets = {"groceries": 15000, "rent": 30000, "utilities": 5000, "entertainment": 8000}
            ai_advice = get_budget_advice(actuals, budgets)

            advice_frame = tk.Frame(notebook)
            notebook.add(advice_frame, text="🤖 AI Advice")

            for item in ai_advice:
                line = f"{item['category']} | {item['risk']} | {item['action']}"
                tk.Label(advice_frame, text=line, wraplength=350, anchor="w").pack(
                    fill="x", pady=2
                )
        except Exception:
            tk.Label(advice_frame, text="AI module not available.").pack(pady=10)

    # For Pydroid, make sure to override mainloop so it doesn’t hang
    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = PFMApp()
    app.run()