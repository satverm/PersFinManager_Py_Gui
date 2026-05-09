"""
models.py – Extended data shapes for the PFM.

Aligns with db.py's richer schema:
  - accounts, transactions, budgets, goals,
  - assets, loans, investments,
  - individuals / family,
  - preset_categories.
"""

from typing import TypedDict, Optional


# --- Core entities ---

class Account(TypedDict):
    id: int
    name: str
    type: str  # checking|savings|investment|loan|credit_card
    balance: float
    currency: str
    is_active: int
    description: Optional[str]


class Individual(TypedDict):
    id: int
    name: str
    role: str  # self|spouse|child|other
    dob: Optional[str]
    income_account_id: Optional[int]
    expense_account_id: Optional[int]


class Transaction(TypedDict):
    id: int
    account_id: int
    individual_id: Optional[int]
    amount: float
    type: str  # income|expense|transfer
    category: str
    description: Optional[str]
    timestamp: str


class Budget(TypedDict):
    id: int
    category: str
    target_amount: float
    month: str
    notes: Optional[str]


class Goal(TypedDict):
    id: int
    name: str
    category: str
    target_amount: float
    target_date: str
    current_amount: float
    individual_id: Optional[int]
    created_at: str
    updated_at: str
    notes: Optional[str]


# --- Assets, Loans, Investments ---

class Asset(TypedDict):
    id: int
    name: str
    type: str  # real_estate|vehicle|other_property
    value: float
    currency: str
    purchase_date: Optional[str]
    location: Optional[str]
    notes: Optional[str]


class Loan(TypedDict):
    id: int
    name: str
    type: str  # personal|home|vehicle|education|other
    principal: float
    remaining: float
    rate_percent: Optional[float]
    term_months: Optional[int]
    start_date: Optional[str]
    notes: Optional[str]


class Investment(TypedDict):
    id: int
    name: str
    type: str  # equity|mutual_fund|debt|gold|other
    current_value: float
    currency: str
    buy_price: Optional[float]
    units: Optional[float]
    asset_ticker: Optional[str]
    notes: Optional[str]


# --- Preset categories (UI helpers) ---

class PresetCategory(TypedDict):
    id: int
    name: str
    type: str  # expense|income
    parent_category: Optional[str]


# Example usage (for type hints only; no runtime check)
if __name__ == "__main__":
    sample_trans: Transaction = {
        "id": 1,
        "account_id": 1,
        "individual_id": None,
        "amount": -2500.0,
        "type": "expense",
        "category": "groceries",
        "description": "Weekly supermarket",
        "timestamp": "2026-05-09 10:00:00",
    }