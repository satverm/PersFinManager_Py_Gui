"""
accounts.py – Account UI & logic for PFM.

Shows a list of accounts with current balances (auto‑updated by transactions).
Uses preset account types and shows a small balance summary.
"""


from tkinter import Frame, Label, Button, Listbox, Scrollbar, Toplevel, Entry, ttk
from typing import List, Dict

from db import get_db_connection
from models import Account


# ------------------------ DB helpers ----------------------------

def get_accounts() -> List[Dict]:
    """Fetch all active accounts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, type, balance, currency FROM accounts WHERE is_active = 1 ORDER BY name"
    )
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def get_total_balance() -> float:
    """Sum of all active accounts."""
    accounts = get_accounts()
    return sum(acc["balance"] for acc in accounts)


# ------------------------ UI classes ----------------------------

class AccountForm:
    def __init__(self, parent, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("New Account")

        self.refresh_callback = refresh_callback

        Label(self.top, text="Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.name_entry = Entry(self.top, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(self.top, text="Type:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.type_var = ttk.Combobox(
            self.top,
            values=["checking", "savings", "investment", "loan", "credit_card"],
        )
        self.type_var.grid(row=1, column=1, padx=5, pady=5)

        Label(self.top, text="Currency:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.currency_entry = Entry(self.top, width=10)
        self.currency_entry.insert(0, "₹")
        self.currency_entry.grid(row=2, column=1, padx=5, pady=5)

        Label(self.top, text="Initial Balance:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.balance_entry = Entry(self.top, width=12)
        self.balance_entry.grid(row=3, column=1, padx=5, pady=5)

        Label(self.top, text="Description (optional):").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.desc_entry = Entry(self.top, width=30)
        self.desc_entry.grid(row=4, column=1, padx=5, pady=5)

        Button(self.top, text="Save", command=self.save).grid(
            row=5, column=0, columnspan=2, pady=10
        )

    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            return

        type_ = self.type_var.get()
        if type_ not in ["checking", "savings", "investment", "loan", "credit_card"]:
            return

        currency = self.currency_entry.get().strip() or "₹"

        try:
            balance = float(self.balance_entry.get() or "0.0")
        except ValueError:
            return

        description = self.desc_entry.get().strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO accounts (name, type, balance, currency, description)
               VALUES (?, ?, ?, ?, ?)""",
            (name, type_, balance, currency, description),
        )
        conn.commit()
        conn.close()

        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class AccountsFrame(Frame):
    """Scrollable list of accounts, linked to main balance on landing page."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Accounts", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=5
        )

        self.total_label = Label(self, text="Total: ₹0.00", font=("Arial", 10))
        self.total_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.listbox = Listbox(self, height=10)
        self.listbox.grid(
            row=2, column=0, columnspan=2, sticky="nsew", pady=5, padx=5
        )

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=3, column=0, columnspan=3, pady=5)

        Button(
            frame_buttons,
            text="Add Account",
            command=self.open_account_form,
        ).pack(side="left", padx=2)
        Button(frame_buttons, text="Refresh", command=self.refresh).pack(
            side="left", padx=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        accounts = get_accounts()

        # Update total balance label
        total = get_total_balance()
        self.total_label.config(text=f"Total: ₹{total:,.2f}")

        # Add each account
        for acc in accounts:
            line = f"{acc['name']} ({acc['type']}) — {acc['currency']}{acc['balance']:,.2f}"
            self.listbox.insert("end", line)

    def open_account_form(self):
        AccountForm(self, refresh_callback=self.refresh)