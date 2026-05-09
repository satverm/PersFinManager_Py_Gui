"""
backup_ui.py – Enhanced backup UI with:
  - backup,  
  - reset (with auto backup + warning),  
  - load from backup.

Also a small mobile‑style landing page option in landing.py.
"""

import os
import shutil
from datetime import datetime
from tkinter import (
    Frame,
    Label,
    Button,
    Listbox,
    Scrollbar,
    Toplevel,
    messagebox,
    ttk,
)


DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
DB_PATH = os.path.join(DATA_DIR, "pfm.db")


def get_db_connection():
    """Get DB connection (aligns with db.py)."""
    import sqlite3
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_backup_list():
    """Return list of backup files (name, mtime, size)."""
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
    backups.sort(key=lambda x: x["mtime"], reverse=True)
    return backups


def create_backup() -> str or None:
    """Create new backup: pfm.db → backups/pfm_backup_YYYYMMDD_HHMMSS.db."""
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if not os.path.exists(DB_PATH):
        return None

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"pfm_backup_{now}.db")

    try:
        shutil.copy2(DB_PATH, dest)
        return dest
    except Exception:
        return None


def reset_db():
    """Create backup then reset DB (drop all tables, re‑init)."""
    backup_path = create_backup()
    if backup_path is None:
        return False  # backup failed

    # Close any existing connection (in real app, clear conn pool)
    try:
        os.remove(DB_PATH)
    except Exception:
        return False

    # Re‑init schema
    from db import init_db
    init_db()

    return True


def load_from_backup(backup_name: str) -> bool:
    """Copy a backup file to pfm.db."""
    src = os.path.join(BACKUP_DIR, backup_name)
    if not os.path.exists(src):
        return False
    try:
        shutil.copy2(src, DB_PATH)
        return True
    except Exception:
        return False


# ------------------------ Enhanced Backup Frame -----------------

class BackupRestoreFrame(Frame):
    """Backup, reset, and load from backup UI."""

    def __init__(self, parent, refresh_on_done=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.refresh_on_done = refresh_on_done

        Label(self, text="Backup & Restore", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=5
        )

        self.listbox = Listbox(self, height=8)
        self.listbox.grid(
            row=1, column=0, columnspan=2, sticky="nsew", pady=5, padx=5
        )

        scrollbar = Scrollbar(self, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky="ns", padx=0, pady=5)

        frame_buttons = Frame(self)
        frame_buttons.grid(row=2, column=0, columnspan=4, pady=5)

        Button(
            frame_buttons,
            text="💾 Backup DB",
            command=self.do_backup,
        ).pack(side="left", padx=2)

        Button(
            frame_buttons,
            text="🔄 Reset DB",
            command=self.confirm_reset_db,
        ).pack(side="left", padx=2)

        Button(
            frame_buttons,
            text="📂 Load from Backup",
            command=self.confirm_load_backup,
        ).pack(side="left", padx=2)

        Button(
            frame_buttons,
            text="Refresh",
            command=self.refresh_list,
        ).pack(side="left", padx=2)

        self.info_label = Label(
            self,
            text="No backups found",
            font=("Arial", 9),
            fg="#6b7280",
        )
        self.info_label.grid(row=3, column=0, columnspan=4, sticky="w", pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.refresh_list()

    def do_backup(self):
        """Create a backup and refresh UI."""
        path = create_backup()
        if path is None:
            messagebox.showerror("Backup Failed", "Could not create backup file.")
        else:
            messagebox.showinfo(
                "Backup Created",
                f"Saved to {path}Keep this file safe.",
            )
        self.refresh_list()

    def confirm_reset_db(self):
        """Ask before backing up and resetting DB."""
        if not messagebox.askyesno(
            "Reset DB",
            "Create a backup and reset all data? This will clear everything except the backup.",
        ):
            return
        if not reset_db():
            messagebox.showerror("Reset Failed", "Could not reset the database.")
            return
        messagebox.showinfo("Reset Done", "Database reset. You can now start fresh.")
        if self.refresh_on_done:
            self.refresh_on_done()

    def confirm_load_backup(self):
        """Load selected backup file into pfm.db."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a backup to load.")
            return
        index = selection[0]
        backups = get_backup_list()
        if index >= len(backups):
            return
        b = backups[index]
        name = b["name"]

        if not messagebox.askyesno(
            "Load from Backup",
            f"Load database from backup '{name}'?This will overwrite the current data.",
        ):
            return

        if not load_from_backup(name):
            messagebox.showerror("Load Failed", "Could not restore from backup.")
            return
        messagebox.showinfo(
            "Loaded",
            f"Loaded database from backup '{name}'.App may need to restart to reflect changes.",
        )
        if self.refresh_on_done:
            self.refresh_on_done()

    def refresh_list(self):
        """Update listbox and info label."""
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
                text=f"No backups in {BACKUP_DIR}Use 'Backup DB' to create one."
            )


def open_backup_window(parent, refresh_on_done=None):
    """Open backup/restore dialog (modal)."""
    top = Toplevel(parent)
    top.title("Backup & Restore")

    frame = BackupRestoreFrame(top, refresh_on_done=refresh_on_done)
    frame.pack(fill="both", expand=True, padx=8, pady=8)

    Button(top, text="Close", command=top.destroy).pack(pady=8)