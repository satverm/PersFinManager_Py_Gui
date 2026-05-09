"""Lightweight models / data classes for the PFM."""

from typing import List, TypedDict


class Account(TypedDict):
    id: int
    name: str
    type: str
    balance: float
    currency: str
    is_active: int


class Transaction(TypedDict):
    id: int
    account_id: int
    amount: float
    type: str
    category: str
    description: str
    timestamp: str


class Budget(TypedDict):
    id: int
    category: str
    target_amount: float
    month: str


class Goal(TypedDict):
    id: int
    name: str
    category: str
    target_amount: float
    target_date: str
    current_amount: float
    created_at: str
    updated_at: str