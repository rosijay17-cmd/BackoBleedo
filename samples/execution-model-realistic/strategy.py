import backtrader as bt
from backtrader.executionmodels.realistic import RealisticExecutionModel


class SMAStrategy(bt.Strategy):
    """
    Simple 20-day SMA crossover strategy.

    Buy when price crosses above the SMA.
    Sell when price crosses below the SMA.

    When use_execution_model=True, fill price is adjusted
    by RealisticExecutionModel before the order is placed.
    """

    params = (
        ("sma_period", 20),
        ("size", 100),
        ("use_execution_model", False),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.p.sma_period
        )
        self.exec_model = RealisticExecutionModel() if self.p.use_execution_model else None
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None

    def next(self):
        if self.order:
            return

        price = self.data.close[0]

        if not self.position:
            if price > self.sma[0]:
                fill_price = (
                    self.exec_model.adjust_price(price, is_buy=True)
                    if self.exec_model else None
                )
                self.order = self.buy(
                    size=self.p.size,
                    price=fill_price,
                    exectype=bt.Order.Limit if fill_price else bt.Order.Market
                )
        else:
            if price < self.sma[0]:
                fill_price = (
                    self.exec_model.adjust_price(price, is_buy=False)
                    if self.exec_model else None
                )
                self.order = self.sell(
                    size=self.p.size,
                    price=fill_price,
                    exectype=bt.Order.Limit if fill_price else bt.Order.Market
                )
