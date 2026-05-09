"""
goals.py – Goals UI & logic for mobile tkinter PFM.

Modular frame that:
  - lists savings goals with progress bars (mocked),
  - allows adding new goals via a form.
"""

import sqlite3
from tkinter import Frame, Label, Listbox, Scrollbar, Entry, Button, Toplevel, ttk
from typing import List

from db import get_db_connection
from models import Goal


def list_goals() -> List[Goal]:
    """Fetch all active goals from DB."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT
            id, name, category, target_amount, target_date,
            current_amount, created_at, updated_at
        FROM goals
        ORDER BY target_date
        """
    )
    goals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return goals


def create_goal(
    name: str,
    category: str,
    target_amount: float,
    target_date: str,
) -> int:
    """Create a new goal; returns inserted row id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO goals (name, category, target_amount, target_date)
        VALUES (?, ?, ?, ?)""",
        (name, category, target_amount, target_date),
    )
    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id


class GoalForm:
    def __init__(self, parent, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("New Goal")
        self.refresh_callback = refresh_callback

        Label(self.top, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = Entry(self.top, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(self.top, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.category_var = ttk.Combobox(
            self.top,
            values=["emergency", "vacation", "car", "education", "retirement", "other"],
        )
        self.category_var.grid(row=1, column=1, padx=5, pady=5)

        Label(self.top, text="Target:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = Entry(self.top, width=15)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        Label(self.top, text="Target Date (YYYY-MM-DD):").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.date_entry = Entry(self.top, width=15)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)

        Button(self.top, text="Create Goal", command=self.save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

    def save(self):
        name = self.name_entry.get().strip()
        category = self.category_var.get()
        try:
            target = float(self.amount_entry.get())
        except ValueError:
            return
        target_date = self.date_entry.get().strip()

        if not name or not category or not target_date:
            return

        create_goal(name, category, target, target_date)

        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class GoalsFrame(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Savings Goals", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=8)
        self.listbox.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=3, pady=5)

        Button(frame_buttons, text="New Goal", command=self.open_goal_form).pack(
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
        goals = list_goals()
        for g in goals:
            progress = (
                round((g["current_amount"] / g["target_amount"]) * 100, 1)
                if g["target_amount"] > 0
                else 0.0
            )
            line = f"{g['name']} ({g['category']}) | {g['current_amount']:,.2f} / {g['target_amount']:,.2f} | {progress:.1f}%"
            self.listbox.insert("end", line)

    def open_goal_form(self):
        GoalForm(self, refresh_callback=self.refresh)