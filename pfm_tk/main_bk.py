"""
Personal Financial Manager — Tkinter Mobile UI

Entry point: main.py

Modular, single‑user PFM with:
  - accounts, transactions, budgets, goals,
  - SQLite backend,
  - placeholder AI module (ai.py, not yet wired).

Usage in Pydroid:
  - place this in `pfm_tk/main.py`,
  - run it from the Pydroid editor / terminal.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk
from db import init_db
from accounts import AccountsFrame
from transactions import TransactionsFrame
from budgets import BudgetsFrame
from goals import GoalsFrame


class PFMApp(tk.Tk):
    """Main application window with tabbed UI."""

    def __init__(self):
        super().__init__()
        self.title("PFM – Personal Finance Manager")
        self.geometry("400x700")   # mobile‑style tall screen
        self.minsize(320, 600)

        # Initialize DB on first run
        init_db()

        # Main notebook (tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=4, pady=4)

        # Tab 1: Accounts
        self.account_tab = AccountsFrame(notebook)
        notebook.add(self.account_tab, text="🏦 Accounts")

        # Tab 2: Transactions
        self.txn_tab = TransactionsFrame(notebook)
        notebook.add(self.txn_tab, text="📊 Transactions")

        # Tab 3: Budgets
        self.budget_tab = BudgetsFrame(notebook)
        notebook.add(self.budget_tab, text="🎯 Budgets")

        # Tab 4: Goals
        self.goals_tab = GoalsFrame(notebook)
        notebook.add(self.goals_tab, text="🚀 Goals")

        # Footer / status (simple)
        self.status = tk.Label(
            self, text="PFM Tk – Local single‑user app · Data in data/pfm.db"
        )
        self.status.pack(side="bottom", pady=4)


if __name__ == "__main__":
    app = PFMApp()
    app.mainloop()