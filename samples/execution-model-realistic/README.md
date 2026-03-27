# Realistic Execution & Cost Engine for Backtrader

Most backtests assume perfect execution. Every trade has hidden costs:

- Bid-ask spread: 5 bps
- Market slippage: 5 bps  
- Commission: 10 bps

## Real results (SPY, SMA-20, 2020-2024)

No costs:  +8.46% return, Sharpe -0.50, Max DD 8.10%
With costs: +1.22% return, Sharpe -8.84, Max DD 1.23%
Cost drag:  -7.24% return

## How to run

pip install -r requirements.txt
python run.py
