"""
family.py – Family / Individuals UI for PFM.

Shows list of family members (self, spouse, children, etc.)
and basic details (dob, linked accounts).
"""

import sqlite3
from tkinter import (
    Frame,
    Label,
    Button,
    Entry,
    Listbox,
    Scrollbar,
    Toplevel,
    ttk,
    messagebox,
)
from typing import List


DATA_DIR = "data"
DB_PATH = f"{DATA_DIR}/pfm.db"


def get_db_connection():
    """Get DB connection (re‑use the same pattern as db.py)."""
    return sqlite3.connect(DB_PATH)


def list_individuals() -> List[dict]:
    """Fetch all individuals."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT
            id, name, role, dob, income_account_id, expense_account_id
        FROM individuals
        ORDER BY role, name"""
    )
    individuals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return individuals


def get_accounts() -> List[dict]:
    """Helper: get accounts (id, name) for combos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type FROM accounts WHERE is_active = 1")
    accounts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return accounts


def create_individual(
    name: str,
    role: str,
    dob: str,
    income_account_id: int,
    expense_account_id: int,
):
    """Create a new individual."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO individuals (
            name, role, dob, income_account_id, expense_account_id
        ) VALUES (?, ?, ?, ?, ?)""",
        (name, role, dob, income_account_id, expense_account_id),
    )
    conn.commit()
    conn.close()


def update_individual(
    individual_id: int,
    name: str,
    role: str,
    dob: str,
    income_account_id: int,
    expense_account_id: int,
):
    """Update an existing individual."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE individuals
           SET name = ?, role = ?, dob = ?,
               income_account_id = ?, expense_account_id = ?
           WHERE id = ?""",
        (name, role, dob, income_account_id, expense_account_id, individual_id),
    )
    conn.commit()
    conn.close()


# ------------------------ UI classes ----------------------------

class IndividualForm:
    def __init__(self, parent, individual_id: int = None, refresh_callback=None):
        self.top = Toplevel(parent)
        self.top.title("Individual" + ("" if individual_id is None else " (Edit)"))
        self.individual_id = individual_id
        self.refresh_callback = refresh_callback

        accounts = get_accounts()
        self.account_map = {acc["id"]: f"{acc['name']} ({acc['id']})" for acc in accounts}

        accounts_names = list(self.account_map.values())

        # Name
        Label(self.top, text="Name:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.name_entry = Entry(self.top, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Role
        Label(self.top, text="Role:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.role_var = ttk.Combobox(
            self.top,
            values=["self", "spouse", "child", "other"],
        )
        self.role_var.grid(row=1, column=1, padx=5, pady=5)

        # DOB
        Label(self.top, text="Birth Date (YYYY-MM-DD):").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        self.dob_entry = Entry(self.top, width=15)
        self.dob_entry.grid(row=2, column=1, padx=5, pady=5)

        # Income account
        Label(self.top, text="Income Account:").grid(
            row=3, column=0, sticky="w", padx=5, pady=5
        )
        self.income_var = ttk.Combobox(self.top, values=accounts_names)
        self.income_var.grid(row=3, column=1, padx=5, pady=5)

        # Expense account
        Label(self.top, text="Expense Account:").grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )
        self.expense_var = ttk.Combobox(self.top, values=accounts_names)
        self.expense_var.grid(row=4, column=1, padx=5, pady=5)

        Button(self.top, text="Save", command=self.save).grid(
            row=5, column=0, columnspan=2, pady=10
        )

        # If editing, load data
        if individual_id is not None:
            indv = next(
                (i for i in list_individuals() if i["id"] == individual_id), None
            )
            if indv:
                self.name_entry.insert(0, indv["name"])
                self.role_var.set(indv["role"])
                self.dob_entry.insert(0, indv["dob"] or "")
                income_name = self.account_map.get(indv["income_account_id"], "")
                expense_name = self.account_map.get(indv["expense_account_id"], "")
                self.income_var.set(income_name)
                self.expense_var.set(expense_name)

    def save(self):
        name = self.name_entry.get().strip()
        role = self.role_var.get()
        dob = self.dob_entry.get().strip()
        income_name = self.income_var.get()
        expense_name = self.expense_var.get()

        if not name or role not in ["self", "spouse", "child", "other"]:
            messagebox.showwarning("Missing", "Fill required fields.")
            return

        accounts = get_accounts()
        income_id = None
        if income_name:
            for acc in accounts:
                if f"{acc['name']} ({acc['id']})" == income_name:
                    income_id = acc["id"]
                    break
        expense_id = None
        if expense_name:
            for acc in accounts:
                if f"{acc['name']} ({acc['id']})" == expense_name:
                    expense_id = acc["id"]
                    break

        if self.individual_id is None:
            # Create
            create_individual(name, role, dob, income_id, expense_id)
        else:
            # Update
            update_individual(
                self.individual_id, name, role, dob, income_id, expense_id
            )

        self.top.destroy()
        if self.refresh_callback:
            self.refresh_callback()


class FamilyFrame(Frame):
    """Frame that shows family members and lets you manage them."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(self, text="Family & Individuals", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=8)
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
            text="Add Member",
            command=self.open_add_form,
        ).pack(side="left", padx=2)

        Button(
            frame_buttons,
            text="Edit Selected",
            command=self.edit_selected,
        ).pack(side="left", padx=2)

        Button(frame_buttons, text="Refresh", command=self.refresh).pack(
            side="left", padx=2
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, "end")
        individuals = list_individuals()
        for i in individuals:
            line = f"{i['name']} ({i['role']})"
            if i["dob"]:
                line += f" – {i['dob']}"
            income = i["income_account_id"]
            expense = i["expense_account_id"]
            if income or expense:
                line += " | "
                if income:
                    line += f"IN={income}"
                if income and expense:
                    line += " | "
                if expense:
                    line += f"EXP={expense}"
            self.listbox.insert("end", line)

    def open_add_form(self):
        IndividualForm(self, refresh_callback=self.refresh)

    def edit_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        individuals = list_individuals()
        if index >= len(individuals):
            return
        indv = individuals[index]
        IndividualForm(self, individual_id=indv["id"], refresh_callback=self.refresh)