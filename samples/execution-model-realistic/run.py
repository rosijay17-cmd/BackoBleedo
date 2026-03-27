import backtrader as bt
import yfinance as yf
import pandas as pd

from strategy   import SMAStrategy
from cost_model import CommissionModel
from analyzers  import print_results, print_comparison


def get_data(ticker="SPY", start="2020-01-01", end="2024-01-01"):
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [c.lower() for c in df.columns]
    df.dropna(inplace=True)

    return bt.feeds.PandasData(dataname=df)


def run_backtest(use_costs=False, starting_cash=100_000):
    cerebro = bt.Cerebro()
    cerebro.adddata(get_data())
    cerebro.addstrategy(SMAStrategy, use_execution_model=use_costs)
    cerebro.broker.set_cash(starting_cash)

    if use_costs:
        cerebro.broker.addcommissioninfo(CommissionModel())

    cerebro.addanalyzer(bt.analyzers.Returns,    _name="returns")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe",
                        riskfreerate=0.05, annualize=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown,   _name="drawdown")

    results = cerebro.run()
    label = "WITH REALISTIC COSTS" if use_costs else "NO COSTS (ideal world)"
    return print_results(label, results[0])


if __name__ == "__main__":
    print("\nRunning backtest — SPY | SMA-20 | 2020-2024\n")
    no_cost_results = run_backtest(use_costs=False)
    cost_results    = run_backtest(use_costs=True)
    print_comparison(no_cost_results, cost_results)
