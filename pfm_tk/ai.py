"""
ai.py – Placeholder AI module for PFM.

Current behavior:
  - Does not talk to an external model.
  - Returns a fixed mock “budget advice” for given categories.

You can later:
  - plug in an LLM / external API,
  - or refactor this into an /ai budget_advice helper.

Function:
  - `get_budget_advice(actuals: dict[str, float], budgets: dict[str, float])`
    returns a list of insights (dict of category, risk, action, reasoning).
"""

from typing import Dict, List, TypedDict


class BudgetAdvice(TypedDict):
    """Structure for one AI‑style advice item."""
    category: str
    risk: str  # "OK", "High", "Over"
    action: str
    reasoning: str


def get_budget_advice(
    actuals: Dict[str, float],
    budgets: Dict[str, float],
) -> List[BudgetAdvice]:
    """
    Mock AI‑style budget advice.

    Given:
      actuals["groceries"] = 14800
      budgets["groceries"] = 15000
    Returns a list of advice dictionaries.
    """
    result: List[BudgetAdvice] = []

    all_cats = set(actuals.keys()) | set(budgets.keys())
    for cat in sorted(all_cats):
        actual = abs(actuals.get(cat, 0))
        target = budgets.get(cat, 0)

        if target <= 0:
            continue  # skip if no budget

        if actual > target:
            risk = "Over"
            action = "Cut back"
            reasoning = (
                f"You've already spent more than your budget for {cat}. "
                "Avoid new discretionary purchases."
            )
        elif actual >= 0.8 * target:
            risk = "High"
            action = "Reduce"
            reasoning = (
                f"You're close to your budget for {cat}. "
                "Try to reduce discretionary items this month."
            )
        else:
            risk = "OK"
            action = "Maintain"
            reasoning = (
                f"Spending for {cat} is within limits. "
                "Maintain this level or transfer surplus to goals."
            )

        result.append(
            BudgetAdvice(
                category=cat,
                risk=risk,
                action=action,
                reasoning=reasoning,
            )
        )

    return result


# Example usage (for testing / demo)
if __name__ == "__main__":
    sample_actuals = {
        "groceries": 14800,
        "rent": 30000,
        "utilities": 4200,
        "entertainment": 9500,
        "transport": 5300,
    }
    sample_budgets = {
        "groceries": 15000,
        "rent": 30000,
        "utilities": 5000,
        "entertainment": 8000,
        "transport": 6000,
    }

    advice = get_budget_advice(sample_actuals, sample_budgets)
    for item in advice:
        print(f"{item['category']} → {item['risk']} | {item['action']}")
        print(f"  {item['reasoning']}")