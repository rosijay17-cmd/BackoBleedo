from __future__ import absolute_import, division, print_function, unicode_literals


class RealisticExecutionModel:
    """
    Adjusts the fill price of buy/sell orders to account for
    bid-ask spread and market slippage — both applied adversely.

    Parameters
    ----------
    spread   : float — half bid-ask spread as decimal (default 5 bps)
    slippage : float — adverse price movement on fill (default 5 bps)
    """

    def __init__(self, spread: float = 0.0005, slippage: float = 0.0005):
        if spread < 0 or slippage < 0:
            raise ValueError("spread and slippage must be non-negative")
        self.spread = spread
        self.slippage = slippage

    def adjust_price(self, price: float, is_buy: bool = True) -> float:
        direction = 1 if is_buy else -1
        price *= 1 + direction * self.spread
        price *= 1 + direction * self.slippage
        return round(price, 4)

    def total_cost_bps(self) -> float:
        return (self.spread + self.slippage) * 10_000

    def __repr__(self) -> str:
        return (
            f"RealisticExecutionModel("
            f"spread={self.spread * 10_000:.1f}bps, "
            f"slippage={self.slippage * 10_000:.1f}bps)"
        )
