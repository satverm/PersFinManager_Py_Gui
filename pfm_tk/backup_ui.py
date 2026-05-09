"""
backup_ui.py – Backup UI & helpers for PFM.

Shows:
  - list of existing backups,
  - button to create a new backup,
  - info about file size and date.
"""

import os
import shutil
from datetime import datetime
from tkinter import Frame, Label, Button, Listbox, Scrollbar, messagebox
from tkinter import Toplevel


DATA_DIR = os.path.join("data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "pfm.db")


def get_backup_list():
    """Return list of backup files (name, timestamp, size)."""
    if not os.path.exists(BACKUP_DIR):
        return []

    backups = []
    for fn in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, fn)
        if os.path.isfile(path) and fn.startswith("pfm_backup_") and fn.endswith(".db"):
            try:
                st = os.stat(path)
                mtime = datetime.fromtimestamp(st.st_mtime)
                size = st.st_size
                backups.append({"name": fn, "mtime": mtime, "size": size})
            except Exception:
                pass

    # sort by time, newest first
    backups.sort(key=lambda x: x["mtime"], reverse=True)
    return backups


def create_backup():
    """Create a new backup: pfm.db → backups/pfm_backup_YYYYMMDD_HHMMSS.db."""
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if not os.path.exists(DB_PATH):
        return None  # DB missing

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"pfm_backup_{now}.db")

    try:
        shutil.copy2(DB_PATH, dest)
        return dest
    except Exception:
        return None


# ------------------------ Backup UI Frame -----------------------

class BackupStatusFrame(Frame):
    """Small frame that shows backup list and lets you create new backups."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        Label(
            self,
            text="Backup & Restore",
            font=("Arial", 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)

        self.listbox = Listbox(self, height=8)
        self.listbox.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=5,
            padx=5,
        )

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=3, pady=5)

        Button(
            frame_buttons,
            text="Create New Backup",
            command=self.create_backup_and_refresh,
        ).pack(side="left", padx=2)

        Button(
            frame_buttons,
            text="Refresh List",
            command=self.refresh,
        ).pack(side="left", padx=2)

        # Info label
        self.info_label = Label(
            self,
            text="No backups found",
            font=("Arial", 9),
            fg="#6b7280",
        )
        self.info_label.grid(row=3, column=0, columnspan=3, sticky="w", pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.refresh()

    def create_backup_and_refresh(self):
        """Create a backup and refresh UI."""
        result = create_backup()
        if result is None:
            messagebox.showerror("Backup Failed", "Could not create backup file.")
        else:
            messagebox.showinfo(
                "Backup Created",
                f"Saved to {result}Keep this file safe.",
            )
        self.refresh()

    def refresh(self):
        """Refresh the listbox and info label."""
        self.listbox.delete(0, "end")
        backups = get_backup_list()

        if backups:
            for b in backups:
                size_mb = round(b["size"] / 1024 / 1024, 2)
                line = f"{b['name']} | {b['mtime']} | {size_mb} MB"
                self.listbox.insert("end", line)
            self.info_label.config(
                text=f"{len(backups)} backup(s) found in {BACKUP_DIR}"
            )
        else:
            self.listbox.insert("end", "(No backups)")
            self.info_label.config(
                text=f"No backups in {BACKUP_DIR}Click 'Create New Backup'."
            )


# ------------------------ Optional backup dialog (modal) -------

def open_backup_window(parent):
    """Open a small backup dialog (for use as a button in main.py)."""
    top = Toplevel(parent)
    top.title("Backup & Restore")

    frame = BackupStatusFrame(top)
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    Button(top, text="Close", command=top.destroy).pack(pady=8)