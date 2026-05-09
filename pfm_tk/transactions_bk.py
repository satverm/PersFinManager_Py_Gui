"""Transaction UI & logic for mobile tkinter app."""

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
)
from typing import List

from db import get_db_connection
from models import Transaction, Account


def get_accounts() -> List[Account]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM accounts WHERE is_active = 1")
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def list_transactions() -> List[Transaction]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.account_id, a.name as account_name, t.amount, t.type, t.category, t.description, t.timestamp
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.timestamp DESC LIMIT 10
    """)
    transactions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return transactions


class TransactionForm:
    def __init__(self, parent, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("New Transaction")
        self.refresh_callback = refresh_callback

        accounts = get_accounts()
        account_names = [f"{acc['name']} ({acc['id']})" for acc in accounts]
        self.account_map = {f"{acc['name']} ({acc['id']})": acc["id"] for acc in accounts}

        Label(self.top, text="Account:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.account_var = ttk.Combobox(self.top, values=account_names)
        self.account_var.grid(row=0, column=1, padx=5, pady=5)

        Label(self.top, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = Entry(self.top)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(self.top, text="Type:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.type_var = ttk.Combobox(self.top, values=["income", "expense", "transfer"])
        self.type_var.grid(row=2, column=1, padx=5, pady=5)

        Label(self.top, text="Category:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.category_entry = Entry(self.top)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)

        Label(self.top, text="Description:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = Entry(self.top)
        self.desc_entry.grid(row=4, column=1, padx=5, pady=5)

        Button(self.top, text="Save", command=self.save).grid(
            row=5, column=0, columnspan=2, pady=10
        )

    def save(self):
        account_name = self.account_var.get()
        if not account_name or account_name not in self.account_map:
            return

        account_id = self.account_map[account_name]
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            return
        type_ = self.type_var.get()
        category = self.category_entry.get().strip()
        description = self.desc_entry.get().strip()

        if type_ not in ["income", "expense", "transfer"]:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO transactions (account_id, amount, type, category, description)
            VALUES (?, ?, ?, ?, ?)""",
            (account_id, amount, type_, category, description),
        )
        conn.commit()
        conn.close()

        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class TransactionsFrame(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Transactions", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=8)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=3, pady=5)

        Button(
            frame_buttons, text="New Transaction", command=self.open_transaction_form
        ).pack(side="left", padx=2)
        Button(frame_buttons, text="Refresh", command=self.refresh).pack(
            side="left", padx=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        txns = list_transactions()
        for t in txns:
            sign = " +" if t["type"] == "income" else " -"
            amount = abs(t["amount"])
            line = f"{t['account_name']} |{sign}{amount:.2f}| {t['category']} | {t['description']}"
            self.listbox.insert("end", line)

    def open_transaction_form(self):
        TransactionForm(self, refresh_callback=self.refresh)