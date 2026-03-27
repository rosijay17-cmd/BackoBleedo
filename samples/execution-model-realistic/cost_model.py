import backtrader as bt


class CommissionModel(bt.CommInfoBase):
    """
    Charges 10 bps commission on every trade.
    Applied to both buys and sells.
    """
    params = (("commission", 0.001),)

    def _getcommission(self, size, price, pseudoexec):
        return abs(size) * price * self.p.commission
