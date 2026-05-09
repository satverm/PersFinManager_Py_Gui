"""Account UI & logic for mobile tkinter app."""

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
from models import Account


def get_accounts() -> List[Account]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, type, balance, currency "
        "FROM accounts WHERE is_active = 1 ORDER BY balance DESC"
    )
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def create_account_window(parent):
    def on_save():
        name = entry_name.get().strip()
        type_ = combo_type.get()
        if not name or type_ not in ["checking", "savings", "investment"]:
            return
        balance = float(entry_balance.get() or "0.0")
        currency = entry_currency.get() or "₹"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO accounts (name, type, balance, currency) VALUES (?, ?, ?, ?)",
            (name, type_, balance, currency),
        )
        conn.commit()
        conn.close()

        top.destroy()
        parent.refresh_accounts()

    top = Toplevel(parent)
    top.title("New Account")

    Label(top, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_name = Entry(top)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    Label(top, text="Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    combo_type = ttk.Combobox(top, values=["checking", "savings", "investment"])
    combo_type.grid(row=1, column=1, padx=5, pady=5)

    Label(top, text="Balance:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_balance = Entry(top)
    entry_balance.grid(row=2, column=1, padx=5, pady=5)

    Label(top, text="Currency:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_currency = Entry(top)
    entry_currency.insert(0, "₹")
    entry_currency.grid(row=3, column=1, padx=5, pady=5)

    Button(top, text="Save", command=on_save).grid(
        row=4, column=0, columnspan=2, pady=10
    )


class AccountsFrame(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Accounts", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=8)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=3, pady=5)

        Button(frame_buttons, text="Add Account", command=self.open_add_account).pack(
            side="left", padx=2
        )
        Button(frame_buttons, text="Refresh", command=self.refresh).pack(
            side="left", padx=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        accounts = get_accounts()
        for acc in accounts:
            line = f"{acc['name']} ({acc['type']}) — {acc['currency']}{acc['balance']:,.2f}"
            self.listbox.insert("end", line)

    def open_add_account(self):
        create_account_window(self)