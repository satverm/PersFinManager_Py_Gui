"""
transactions.py – Transaction UI & logic for PFM.

- DB‑aware CRUD for transactions.
- Uses preset categories from db.preset_categories.
- Updates account balances on insert.
"""

import sqlite3
from tkinter import (
    Frame,
    Label,
    Button,
    Listbox,
    Scrollbar,
    Entry,
    Toplevel,
    ttk,
    messagebox,
)
from typing import List

from db import get_db_connection
from models import Transaction, Account, PresetCategory


# ------------------------ DB helpers ----------------------------

def get_accounts() -> list[Account]:
    """Fetch all active accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, balance FROM accounts WHERE is_active = 1")
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def get_preset_categories(of_type: str = "expense") -> List[str]:
    """Fetch preset category names of given type."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM preset_categories WHERE type = ? ORDER BY name",
        (of_type,),
    )
    cats = [row["name"] for row in cursor.fetchall()]
    conn.close()
    return cats


def get_transactions(limit: int = 20) -> list[Transaction]:
    """Fetch latest transactions (income + expenses)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT
            t.id, t.account_id, t.amount, t.type, t.category, t.description, t.timestamp,
            a.name as account_name
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.timestamp DESC
        LIMIT ?""",
        (limit,),
    )
    txns = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return txns


def create_transaction(
    account_id: int,
    amount: float,
    type_: str,
    category: str,
    description: str,
):
    """Insert a new transaction and update account balance."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Get current account balance
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Account not found")
    old_balance = row["balance"]

    # 2. Compute new balance
    # For income: +amount; for expense: -amount; for transfer, it’s net‑neutral here
    if type_ == "income":
        delta = amount
    elif type_ == "expense":
        delta = -amount
    else:  # transfer handled elsewhere or ignored in this handler
        delta = 0.0

    new_balance = old_balance + delta

    # 3. Insert transaction
    cursor.execute(
        """INSERT INTO transactions (
            account_id, amount, type, category, description
        ) VALUES (?, ?, ?, ?, ?)""",
        (account_id, amount, type_, category, description),
    )

    # 4. Update account balance
    cursor.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))

    conn.commit()
    conn.close()


# ------------------------ UI classes ----------------------------

class TransactionForm:
    def __init__(self, parent, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("New Transaction")
        self.refresh_callback = refresh_callback

        accounts = get_accounts()
        account_names = [f"{acc['name']} ({acc['id']})" for acc in accounts]
        self.account_map = {name: acc["id"] for name, acc in zip(account_names, accounts)}

        Label(self.top, text="Account:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.account_var = ttk.Combobox(self.top, values=account_names)
        self.account_var.grid(row=0, column=1, padx=5, pady=5)

        Label(self.top, text="Amount:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.amount_entry = Entry(self.top, width=12)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(self.top, text="Type:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.type_var = ttk.Combobox(
            self.top,
            values=["income", "expense"],  # skipping "transfer" here for simplicity
        )
        self.type_var.grid(row=2, column=1, padx=5, pady=5)

        Label(self.top, text="Category:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.category_vars = {
            "income": get_preset_categories("income"),
            "expense": get_preset_categories("expense"),
        }
        self.category_combo = ttk.Combobox(self.top, values=[])
        self.category_combo.grid(row=3, column=1, padx=5, pady=5)

        # when type changes, update category list
        self.type_var.bind("<<ComboboxSelected>>", self.on_type_change)
        self.amount_entry.bind("<FocusOut>", self.on_type_change)

        Label(self.top, text="Description:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.desc_entry = Entry(self.top, width=30)
        self.desc_entry.grid(row=4, column=1, padx=5, pady=5)

        Button(self.top, text="Save", command=self.save).grid(
            row=5, column=0, columnspan=2, pady=10
        )

        # Initialize
        self.type_var.set("expense")
        self.on_type_change()

    def on_type_change(self, *args):
        """Update category list when type changes."""
        type_ = self.type_var.get()
        if type_ not in self.category_vars:
            return
        self.category_combo["values"] = self.category_vars[type_]
        if self.category_vars[type_]:
            self.category_combo.set(self.category_vars[type_][0])

    def save(self):
        account_name = self.account_var.get()
        if not account_name or account_name not in self.account_map:
            messagebox.showwarning("Account", "Select an account.")
            return

        account_id = self.account_map[account_name]

        try:
            raw = self.amount_entry.get()
            if not raw:
                messagebox.showwarning("Amount", "Enter an amount.")
                return
            amount = float(raw)
        except ValueError:
            messagebox.showwarning("Amount", "Enter a valid number.")
            return

        if amount <= 0:
            messagebox.showwarning("Amount", "Amount must be positive.")
            return

        type_ = self.type_var.get()
        if type_ not in ("income", "expense"):
            messagebox.showwarning("Type", "Select income or expense.")
            return

        category = self.category_combo.get().strip()
        if not category:
            messagebox.showwarning("Category", "Select or type a category.")
            return

        description = self.desc_entry.get().strip()

        try:
            create_transaction(account_id, amount, type_, category, description)
            self.top.destroy()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class TransactionsFrame(Frame):
    """Scrollable list of transactions with quick‑add from main UI."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Transactions", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=10)
        self.listbox.grid(
            row=1, column=0, columnspan=2, sticky="nsew", pady=5, padx=5
        )

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=3, pady=5)

        Button(
            frame_buttons,
            text="New Transaction",
            command=self.open_transaction_form,
        ).pack(side="left", padx=2)
        Button(frame_buttons, text="Refresh", command=self.refresh).pack(
            side="left", padx=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        txns = get_transactions(limit=20)
        for t in txns:
            amount = t["amount"]
            if t["type"] == "income":
                sign = " +"
                color = "green"
            elif t["type"] == "expense":
                sign = " -"
                color = "red"
            else:
                sign = " "
                color = "black"
            line = f"{t['timestamp']} | {sign}{abs(amount):,.2f} | {t['account_name']} | {t['type']} | {t['category']}"
            self.listbox.insert("end", line)

    def open_transaction_form(self):
        TransactionForm(self, refresh_callback=self.refresh)