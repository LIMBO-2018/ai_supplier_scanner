"""
core/profit_calculator.py
Calculates resell profit and suggested pricing.
"""
from __future__ import annotations
from dataclasses import dataclass
from config.settings import DEFAULT_MARGIN_PERCENT


@dataclass
class ProfitResult:
    cost: float
    sell_price: float
    profit: float
    margin_pct: float
    roi_pct: float

    def summary(self) -> str:
        return (
            f"💰 Cost Price: ${self.cost:.2f}\n"
            f"🏷️ Sell Price: ${self.sell_price:.2f}\n"
            f"📈 Profit: ${self.profit:.2f}\n"
            f"📊 Margin: {self.margin_pct:.1f}%\n"
            f"🔄 ROI: {self.roi_pct:.1f}%"
        )


def calculate_profit(
    cost: float,
    sell_price: float | None = None,
    margin_pct: float = DEFAULT_MARGIN_PERCENT,
) -> ProfitResult:
    """
    If sell_price is given, compute real profit.
    Otherwise, suggest a sell price using the target margin.
    """
    if sell_price is None or sell_price <= 0:
        sell_price = cost * (1 + margin_pct / 100)

    profit = sell_price - cost
    actual_margin = (profit / sell_price * 100) if sell_price > 0 else 0.0
    roi = (profit / cost * 100) if cost > 0 else 0.0

    return ProfitResult(
        cost=cost,
        sell_price=sell_price,
        profit=profit,
        margin_pct=actual_margin,
        roi_pct=roi,
    )


def suggested_sell_price(cost: float, margin_pct: float = DEFAULT_MARGIN_PERCENT) -> float:
    return round(cost * (1 + margin_pct / 100), 2)

