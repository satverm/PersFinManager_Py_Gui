"""Budget UI for mobile tkinter app (simple list)."""

import sqlite3
from tkinter import Frame, Label, Listbox, Scrollbar, Toplevel, Entry, Button

from db import get_db_connection
from models import Budget


def list_budgets() -> list[Budget]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, category, target_amount, month
        FROM budgets
        ORDER BY month DESC, category
    """)
    budgets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return budgets


class BudgetForm:
    def __init__(self, parent, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("New Budget")

        self.refresh_callback = refresh_callback

        Label(self.top, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.category_entry = Entry(self.top)
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(self.top, text="Target:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.target_entry = Entry(self.top)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(self.top, text="Month (YYYY-MM):").grid(
            row=2, column=0, padx=5, pady=5, sticky="w"
        )
        self.month_entry = Entry(self.top)
        self.month_entry.grid(row=2, column=1, padx=5, pady=5)

        Button(self.top, text="Save", command=self.save).grid(
            row=3, column=0, columnspan=2, pady=10
        )

    def save(self):
        category = self.category_entry.get().strip()
        target_str = self.target_entry.get()
        month = self.month_entry.get().strip()

        if not category or not month:
            return

        try:
            target = float(target_str)
        except ValueError:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO budgets (category, target_amount, month)
            VALUES (?, ?, ?)""",
            (category, target, month),
        )
        conn.commit()
        conn.close()

        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class BudgetsFrame(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Budgets", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=8)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=3, pady=5)

        Button(frame_buttons, text="New Budget", command=self.open_budget_form).pack(
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
        budgets = list_budgets()
        for b in budgets:
            line = f"{b['category']} | {b['month']} | {b['target_amount']:,.2f}"
            self.listbox.insert("end", line)

    def open_budget_form(self):
        BudgetForm(self, refresh_callback=self.refresh)