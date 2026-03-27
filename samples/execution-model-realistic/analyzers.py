def print_results(label: str, strat) -> dict:
    returns  = strat.analyzers.returns.get_analysis()
    sharpe   = strat.analyzers.sharpe.get_analysis()
    drawdown = strat.analyzers.drawdown.get_analysis()

    total_return = returns.get("rtot", 0) * 100
    sharpe_ratio = sharpe.get("sharperatio") or 0.0
    max_dd       = drawdown.max.drawdown

    print(f"\n{'='*40}")
    print(f"  {label}")
    print(f"{'='*40}")
    print(f"  Total Return : {total_return:+.2f}%")
    print(f"  Sharpe Ratio : {sharpe_ratio:.4f}")
    print(f"  Max Drawdown : {max_dd:.2f}%")
    print(f"{'='*40}")

    return {
        "label":      label,
        "return_pct": total_return,
        "sharpe":     sharpe_ratio,
        "max_dd_pct": max_dd,
    }


def print_comparison(no_cost: dict, with_cost: dict):
    return_drag = with_cost["return_pct"] - no_cost["return_pct"]
    sharpe_drag = with_cost["sharpe"]     - no_cost["sharpe"]
    dd_change   = with_cost["max_dd_pct"] - no_cost["max_dd_pct"]

    print(f"\n{'='*40}")
    print("  COST DRAG SUMMARY")
    print(f"{'='*40}")
    print(f"  Return drag  : {return_drag:+.2f}%")
    print(f"  Sharpe drag  : {sharpe_drag:+.4f}")
    print(f"  Drawdown Δ   : {dd_change:+.2f}%")
    print(f"{'='*40}")
    print("\n  Interpretation:")
    print(f"  Every percentage point of drag is real money")
    print(f"  left on the table due to spread, slippage,")
    print(f"  and commission — costs most backtests ignore.\n")
