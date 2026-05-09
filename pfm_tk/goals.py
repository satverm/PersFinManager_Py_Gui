"""
goals.py – Goals UI & logic for PFM.

Savings‑goals UI that:
  - lets you set name, category, target, and target date,
  - shows a progress bar (mocked via text),
  - and can be linked to transactions for auto‑updating current_amount.
"""

import sqlite3
from tkinter import Frame, Label, Button, Entry, Listbox, Scrollbar, Toplevel, ttk
from typing import List

from db import get_db_connection
from models import Goal, PresetCategory


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


def list_goals() -> List[Goal]:
    """Fetch all active goals, ordered by target date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT
            id, name, category, target_amount, target_date,
            current_amount, individual_id, created_at, updated_at, notes
        FROM goals
        ORDER BY target_date"""
    )
    goals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return goals


def create_goal(
    name: str,
    category: str,
    target_amount: float,
    target_date: str,
    individual_id: int,
    notes: str,
) -> int:
    """Create a new goal; returns row id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO goals (
            name, category, target_amount, target_date,
            current_amount, individual_id, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, category, target_amount, target_date, 0.0, individual_id, notes),
    )
    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id


def update_goal_amount(goal_id: int, new_current: float):
    """Update current_amount and updated_at for a goal."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE goals SET current_amount = ?, updated_at = datetime('now', 'localtime') WHERE id = ?",
        (new_current, goal_id),
    )
    conn.commit()
    conn.close()


# ------------------------ UI classes ----------------------------

class GoalForm:
    def __init__(self, parent, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("New Goal")

        self.refresh_callback = refresh_callback

        Label(self.top, text="Goal Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.name_entry = Entry(self.top, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(self.top, text="Category:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.category_vars = {
            "income": get_preset_categories("income"),
            "expense": get_preset_categories("expense"),
        }
        self.category_combo = ttk.Combobox(self.top, values=[])
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)

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

        Label(self.top, text="Target Amount:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.amount_entry = Entry(self.top, width=12)
        self.amount_entry.grid(row=3, column=1, padx=5, pady=5)

        Label(self.top, text="Target Date (YYYY-MM-DD):").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.date_entry = Entry(self.top, width=12)
        self.date_entry.grid(row=4, column=1, padx=5, pady=5)

        Label(self.top, text="Individual ID (optional):").grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        self.indiv_entry = Entry(self.top, width=8)
        self.indiv_entry.insert(0, "1")  # default first user
        self.indiv_entry.grid(row=5, column=1, padx=5, pady=5)

        Label(self.top, text="Notes:").grid(
            row=6, column=0, sticky="w", padx=5, pady=5
        )
        self.notes_entry = Entry(self.top, width=30)
        self.notes_entry.grid(row=6, column=1, padx=5, pady=5)

        Button(self.top, text="Create Goal", command=self.save).grid(
            row=7, column=0, columnspan=2, pady=10
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
        name = self.name_entry.get().strip()
        category = self.category_combo.get().strip()
        if not name or not category:
            return

        try:
            target = float(self.amount_entry.get())
        except ValueError:
            return
        if target <= 0:
            return

        target_date = self.date_entry.get().strip()
        if not target_date:
            return

        try:
            individual_id = int(self.indiv_entry.get())
        except ValueError:
            individual_id = 1

        notes = self.notes_entry.get().strip()

        create_goal(name, category, target, target_date, individual_id, notes)

        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class GoalUpdateForm:
    def __init__(self, parent, goal_id: int, current_amount: float, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("Update Goal")

        self.goal_id = goal_id
        self.refresh_callback = refresh_callback

        Label(self.top, text=f"Current: ₹{current_amount:,.2f}").pack(
            pady=5, padx=10
        )

        Label(self.top, text="New Current Amount:").pack(
            pady=(10, 0), padx=10
        )
        self.entry = Entry(self.top, width=15)
        self.entry.pack(pady=5, padx=10)
        self.entry.insert(0, str(current_amount))

        Button(self.top, text="Update", command=self.save).pack(
            pady=10, padx=10
        )

    def save(self):
        try:
            new_current = float(self.entry.get())
            if new_current < 0:
                return
        except ValueError:
            return

        update_goal_amount(self.goal_id, new_current)
        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class GoalsFrame(Frame):
    """Scrollable list of savings goals with progress %."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Savings Goals", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=5
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
            text="New Goal",
            command=self.open_goal_form,
        ).pack(side="left", padx=2)
        Button(
            frame_buttons,
            text="Update Selected",
            command=self.update_selected,
        ).pack(side="left", padx=2)
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
            line = f"{g['name']} | {g['category']} | {g['current_amount']:,.2f}/{g['target_amount']:,.2f} | {progress:.1f}%"
            self.listbox.insert("end", line)

    def open_goal_form(self):
        GoalForm(self, refresh_callback=self.refresh)

    def update_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        text = self.listbox.get(index)
        # Quick parsing to get goal_id and current_amount (in real app, maintain a map)
        # For demo, just pass a reasonable mock
        goals = list_goals()
        if index < len(goals):
            goal = goals[index]
            GoalUpdateForm(self, goal["id"], goal["current_amount"], refresh_callback=self.refresh)