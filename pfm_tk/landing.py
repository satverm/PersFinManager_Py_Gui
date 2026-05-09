"""
landing.py – Mobile‑style Android‑like landing page.

Optional UI: use instead of main.py’s landing. It still uses all
other modules (db.py, accounts.py, transactions.py, etc.).
"""

import os
from tkinter import (
    Tk,
    Frame,
    Label,
    Button,
    Listbox,
    Scrollbar,
    Entry,
    ttk,
    messagebox,
)
from datetime import datetime

from db import init_db
from accounts import get_accounts as get_accounts_from_db
from transactions import get_transactions, create_transaction, get_preset_categories
from backup_ui import open_backup_window


# ------------------------ PRESETS --------------------------------

PRESET_EXPENSE_CATEGORIES = get_preset_categories("expense")
PRESET_INCOME_CATEGORIES = get_preset_categories("income")


# ------------------------ DB HELPERS (UI props) ------------------

def get_total_balance() -> float:
    """Compute sum of all accounts."""
    accounts = get_accounts_from_db()
    return sum(a["balance"] for a in accounts)


def get_recent_expenses(limit: int = 5):
    """Get last N expenses (type='expense')."""
    txns = get_transactions(limit=limit * 2)
    expenses = [t for t in txns if t["type"] == "expense"]
    return expenses[:limit]


# ------------------------ Landing UI Class ------------------------

class LandingPage(Tk):
    """Mobile‑style landing page (Android‑app feel)."""

    def __init__(self):
        super().__init__()
        self.title("PFM – Personal Finance")
        self.geometry("800x1200")  # tall mobile portrait
        self.minsize(1000, 1600)

        init_db()

        # Main container
        main = Frame(self, padx=10, pady=10)
        main.pack(fill="both", expand=True)

        # Header
        header = Frame(main)
        header.pack(fill="x", pady=(0, 12))

        self.balance_label = Label(
            header,
            text="Total: ₹0.00",
            font=("Arial", 15, "bold"),
            fg="#059669",
        )
        self.balance_label.pack(anchor="w")

        # Accounts preview
        self.accounts_listbox = Listbox(header, height=3)
        self.accounts_listbox.pack(fill="x", pady=(4, 8))

        # Recent expenses
        tx_frame = Frame(main)
        tx_frame.pack(fill="x", pady=(0, 12))

        Label(tx_frame, text="Recent Expenses", font=("Arial", 11)).pack(
            anchor="w"
        )
        self.tx_listbox = Listbox(tx_frame, height=4, width=40)
        self.tx_listbox.pack(fill="x", pady=(4, 0))

        # Quick Add section (Android‑style)
        quick = Frame(main, relief="groove", borderwidth=1, padx=8, pady=8)
        quick.pack(fill="x", pady=(12, 12))

        Label(quick, text="Quick Add", font=("Arial", 11, "bold")).pack(
            anchor="w"
        )

        # Account
        frame1 = Frame(quick)
        frame1.pack(fill="x", pady=4)
        Label(frame1, text="Account:", width=10, anchor="w").pack(side="left")
        self.account_names = [acc["name"] for acc in get_accounts_from_db()]
        self.account_var = ttk.Combobox(frame1, values=self.account_names, width=20)
        self.account_var.pack(side="left", padx=4)

        # Amount
        frame2 = Frame(quick)
        frame2.pack(fill="x", pady=4)
        Label(frame2, text="Amount:", width=10, anchor="w").pack(side="left")
        self.amount_entry = Entry(frame2, width=12)
        self.amount_entry.pack(side="left", padx=4)

        # Type
        frame3 = Frame(quick)
        frame3.pack(fill="x", pady=4)
        Label(frame3, text="Type:", width=10, anchor="w").pack(side="left")
        self.type_var = ttk.Combobox(frame3, values=["income", "expense"], width=10)
        self.type_var.pack(side="left", padx=4)

        # Category (preset lists)
        frame4 = Frame(quick)
        frame4.pack(fill="x", pady=4)
        Label(frame4, text="Category:", width=10, anchor="w").pack(side="left")
        self.cat_vars = {
            "income": PRESET_INCOME_CATEGORIES,
            "expense": PRESET_EXPENSE_CATEGORIES,
        }
        self.category_var = ttk.Combobox(frame4, values=[], width=20)
        self.category_var.pack(side="left", padx=4)
        self.type_var.bind("<<ComboboxSelected>>", self.on_type_change)
        self.type_var.set("expense")

        # Description
        frame5 = Frame(quick)
        frame5.pack(fill="x", pady=4)
        Label(frame5, text="Desc:", width=10, anchor="w").pack(side="left")
        self.desc_entry = Entry(frame5, width=30)
        self.desc_entry.pack(side="left", padx=4)

        # Submit button
        Button(quick, text="➕ Add", command=self.add_transaction).pack(
            pady=8, fill="x"
        )

        # Toolbar (Dashboard, Backup, Refresh)
        toolbar = Frame(main)
        toolbar.pack(fill="x", pady=8)

        Button(
            toolbar, text="📊 Dashboard", command=self.open_dashboard
        ).pack(side="left", padx=2)
        Button(
            toolbar, text="💾 Backup & Reset", command=self.open_backup_dialog
        ).pack(side="left", padx=2)
        Button(
            toolbar, text="🔄 Refresh", command=self.refresh_ui
        ).pack(side="left", padx=2)

        self.refresh_ui()

    def on_type_change(self, *args):
        """Update category list when type changes."""
        t = self.type_var.get()
        if t in self.cat_vars:
            self.category_var["values"] = self.cat_vars[t]
            if self.cat_vars[t]:
                self.category_var.set(self.cat_vars[t][0])

    def refresh_ui(self):
        """Reload balances, accounts, recent expenses."""
        total = get_total_balance()
        self.balance_label.config(text=f"Total: ₹{total:,.2f}")

        self.accounts_listbox.delete(0, "end")
        for acc in get_accounts_from_db():
            self.accounts_listbox.insert(
                "end", f"{acc['name']} → ₹{acc['balance']:,.2f}"
            )

        self.tx_listbox.delete(0, "end")
        for tx in get_recent_expenses(5):
            self.tx_listbox.insert(
                "end", f"{abs(tx['amount']):,.2f} – {tx['category']}"
            )

    def add_transaction(self):
        """Add expense/income from quick form."""
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            amount = 0.0
        if amount <= 0:
            messagebox.showwarning("Amount", "Enter a positive amount.")
            return

        account_name = self.account_var.get()
        if not account_name or account_name not in self.account_names:
            messagebox.showwarning("Account", "Select an account.")
            return

        type_ = self.type_var.get()
        if type_ not in ("income", "expense"):
            messagebox.showwarning("Type", "Select income or expense.")
            return

        category = self.category_var.get().strip()
        if not category:
            messagebox.showwarning("Category", "Select or type a category.")
            return

        description = self.desc_entry.get().strip()

        accounts = get_accounts_from_db()
        account_row = next((a for a in accounts if a["name"] == account_name), None)
        if not account_row:
            messagebox.showerror("Error", "Account not found.")
            return
        account_id = account_row["id"]

        create_transaction(account_id, amount, type_, category, description)
        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.refresh_ui()
        messagebox.showinfo("Success", "Transaction recorded.")

    def open_dashboard(self):
        """Open notebook dashboard (same as main.py)."""
        from accounts import AccountsFrame
        from transactions import TransactionsFrame
        from budgets import BudgetsFrame
        from goals import GoalsFrame
        from family import FamilyFrame

        dash = Tk()
        dash.title("PFM Dashboard")
        dash.geometry("1000x1600")

        notebook = ttk.Notebook(dash)
        notebook.pack(fill="both", expand=True, padx=4, pady=4)

        notebook.add(AccountsFrame(notebook), text="Accounts")
        notebook.add(TransactionsFrame(notebook), text="Transactions")
        notebook.add(BudgetsFrame(notebook), text="Budgets")
        notebook.add(GoalsFrame(notebook), text="Goals")
        notebook.add(FamilyFrame(notebook), text="Family")

        dash.mainloop()

    def open_backup_dialog(self):
        """Open enhanced backup window."""
        open_backup_window(self, refresh_on_done=self.refresh_ui)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = LandingPage()
    app.run()