"""Enhanced SQLite schema for a more exhaustive PFM."""

import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "pfm.db"


def get_db_connection():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Extended schema catering for income, expenses, assets, loans, investments, family, presets."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Accounts (now with type enum)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
                CHECK (type IN ('checking', 'savings', 'investment', 'loan', 'credit_card')),
            balance REAL NOT NULL,
            currency TEXT DEFAULT '₹',
            is_active INTEGER DEFAULT 1,
            description TEXT
        )
    """)

    # 2. Individuals / Family
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS individuals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL
                CHECK (role IN ('self', 'spouse', 'child', 'other')),
            dob TEXT,
            income_account_id INTEGER,
            expense_account_id INTEGER,
            FOREIGN KEY (income_account_id) REFERENCES accounts(id),
            FOREIGN KEY (expense_account_id) REFERENCES accounts(id)
        )
    """)

    # 3. Transactions (with type and category presets)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            individual_id INTEGER,  -- who incurred this?
            amount REAL NOT NULL,
            type TEXT NOT NULL
                CHECK (type IN ('income', 'expense', 'transfer')),
            category TEXT NOT NULL,
            description TEXT,
            timestamp TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (account_id) REFERENCES accounts(id),
            FOREIGN KEY (individual_id) REFERENCES individuals(id)
        )
    """)

    # 4. Assets (apart from regular accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
                CHECK (type IN ('real_estate', 'vehicle', 'other_property')),
            value REAL NOT NULL,
            currency TEXT DEFAULT '₹',
            purchase_date TEXT,
            location TEXT,
            notes TEXT
        )
    """)

    # 5. Loans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
                CHECK (type IN ('personal', 'home', 'vehicle', 'education', 'other')),
            principal REAL NOT NULL,
            remaining REAL NOT NULL,
            rate_percent REAL,
            term_months INTEGER,
            start_date TEXT,
            notes TEXT
        )
    """)

    # 6. Investments (separate from savings accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
                CHECK (type IN ('equity', 'mutual_fund', 'debt', 'gold', 'other')),
            current_value REAL NOT NULL,
            currency TEXT DEFAULT '₹',
            buy_price REAL,
            units REAL,
            asset_ticker TEXT,
            notes TEXT
        )
    """)

    # 7. Budgets (as before, but with clearer structure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            target_amount REAL NOT NULL,
            month TEXT NOT NULL,
            notes TEXT
        )
    """)

    # 8. Goals (as before, now with individual_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            target_amount REAL NOT NULL,
            target_date TEXT NOT NULL,
            current_amount REAL DEFAULT 0.0,
            individual_id INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime')),
            notes TEXT,
            FOREIGN KEY (individual_id) REFERENCES individuals(id)
        )
    """)

    # 9. Preset categories (shared across users)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preset_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL
                CHECK (type IN ('expense', 'income')),
            parent_category TEXT,
            UNIQUE (name, type)
        )
    """)

    # 10. Seed preset expense categories
    presets = [
        ("groceries", "expense"),
        ("utilities", "expense"),
        ("transport", "expense"),
        ("entertainment", "expense"),
        ("dining_out", "expense"),
        ("clothing", "expense"),
        ("health", "expense"),
        ("education", "expense"),
        ("travel", "expense"),
        ("misc", "expense"),
        ("salary", "income"),
        ("freelance", "income"),
        ("rental_income", "income"),
        ("investment_income", "income"),
    ]
    for name, type_ in presets:
        cursor.execute(
            "INSERT OR IGNORE INTO preset_categories (name, type) VALUES (?, ?)",
            (name, type_),
        )

    conn.commit()
    conn.close()