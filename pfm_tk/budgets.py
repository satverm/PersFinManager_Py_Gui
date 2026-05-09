"""
budgets.py – Budget UI & logic for PFM.

Allows setting monthly targets for preset categories (income/expense),
then shows a list of current budgets.
"""

import sqlite3
from datetime import date
from tkinter import Frame, Label, Button, Entry, Listbox, Scrollbar, Toplevel, ttk
from typing import List

from db import get_db_connection
from models import Budget, PresetCategory


# ------------------------ DB helpers ----------------------------

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


def list_budgets(month: str) -> List[Budget]:
    """Fetch all budgets for a given month."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, category, target_amount, month "
        "FROM budgets WHERE month = ? ORDER BY category",
        (month,),
    )
    budgets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return budgets


def create_budget(category: str, target_amount: float, month: str):
    """Create or update a budget for a category and month."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if budget exists
    cursor.execute(
        "SELECT id FROM budgets WHERE category = ? AND month = ?",
        (category, month),
    )
    row = cursor.fetchone()
    if row:
        # Update
        cursor.execute(
            "UPDATE budgets SET target_amount = ? WHERE id = ?",
            (target_amount, row["id"]),
        )
    else:
        # Insert
        cursor.execute(
            "INSERT INTO budgets (category, target_amount, month) VALUES (?, ?, ?)",
            (category, target_amount, month),
        )

    conn.commit()
    conn.close()


# ------------------------ UI classes ----------------------------

class BudgetForm:
    def __init__(self, parent, month: str, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("Set Budget")

        self.month = month
        self.refresh_callback = refresh_callback

        Label(self.top, text=f"Month: {month}", font=("Arial", 10)).grid(
            row=0, column=0, columnspan=2, pady=5
        )

        Label(self.top, text="Category:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.category_vars = {
            "income": get_preset_categories("income"),
            "expense": get_preset_categories("expense"),
        }
        self.category_combo = ttk.Combobox(self.top, values=[])
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)

        # Type selector to switch preset list
        Label(self.top, text="Type:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.type_var = ttk.Combobox(
            self.top,
            values=["income", "expense"],
        )
        self.type_var.grid(row=2, column=1, padx=5, pady=5)
        self.type_var.set("expense")
        self.type_var.bind("<<ComboboxSelected>>", self.on_type_change)

        Label(self.top, text="Target:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.target_entry = Entry(self.top, width=15)
        self.target_entry.grid(row=3, column=1, padx=5, pady=5)

        Button(self.top, text="Save Budget", command=self.save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Initialize
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
        category = self.category_combo.get().strip()
        if not category:
            return

        try:
            target = float(self.target_entry.get())
        except ValueError:
            return
        if target <= 0:
            return

        create_budget(category, target, self.month)
        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class BudgetsFrame(Frame):
    """Scrollable list of monthly budgets with preset categories."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        # Use current month as default (YYYY-MM)
        self.month = date.today().strftime("%Y-%m")
        self.month_var = self.month

        Label(self, text="Monthly Budgets", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=5
        )

        Label(self, text=f"Month: {self.month}", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=5
        )

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
            text="Set Budget for This Month",
            command=self.open_budget_form,
        ).pack(side="left", padx=2)
        Button(frame_buttons, text="Refresh", command=self.refresh).pack(
            side="left", padx=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        budgets = list_budgets(self.month)
        for b in budgets:
            line = f"{b['category']} | {b['month']} | ₹{b['target_amount']:,.2f}"
            self.listbox.insert("end", line)

    def open_budget_form(self):
        BudgetForm(self, self.month, refresh_callback=self.refresh)