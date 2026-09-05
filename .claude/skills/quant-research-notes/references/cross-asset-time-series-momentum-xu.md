# Cross-Asset Time-Series Momentum (I-XTSM)

**Citation:** Xu, D., Li, B., Singh, T., & Park, J. C. (2025). "Cross-asset time-series
momentum strategy: A new perspective." *Accounting & Finance*, 65, 2387–2419.
https://doi.org/10.1111/acfi.70001

**Note on the wishlist request this fills:** this is not Moskowitz, Ooi & Pedersen
(2012), "Time Series Momentum" itself (still worth getting directly — it's the
foundational paper this one extends and cites throughout), but it's a direct, current
extension of exactly that literature, tests the original TSM strategy head-to-head as
one of its three benchmarks, and — importantly — brings a genuine backtest-overfitting
validation tool (the shuffle/bootstrap test below) that partially answers wishlist
item #2 as well. Strong ingestion on both fronts.

**Data:** S&P 500 index, monthly returns, January 1990 – December 2023 (408 months);
robustness check using the SPY ETF's actual bid/ask closing prices (Feb 1996–Dec 2023).
19 individual commodity spot prices plus 5 GSCI commodity sub-indices (agricultural,
industrial metals, precious metals, energy, and the headline GSCI) as candidate
cross-assets; Barclays US Aggregate Bond Index as the cross-asset from the prior
literature being extended. Six Fama-French/Carhart factors (MKT, SMB, HML, RMW, CMA,
UMD) plus Hou et al. Q5 factors as risk controls.

## Core Methodology

**Three strategies compared, all built on a (K, H) grid** — K = lookback months
{1,3,6,12,24}, H = holding months {1,3,6,12,24}, 25 (K,H) portfolios per strategy:

- **TSM** (Moskowitz et al. 2012): long the S&P 500 if its own past K-month return is
  positive, short if negative, hold for H months. No cross-asset signal at all.
- **XTSM** (Pitkäjärvi et al. 2020): adds a bond-index signal. Symmetric 3-regime
  construction — **Call** (stock signal + bond signal both positive → long),
  **Put** (both negative → short), **Jump Out** (signals disagree, in either
  direction → hold the risk-free asset instead of taking a directional bet).
- **I-XTSM** (this paper's contribution): swaps the bond signal for the **Goldman
  Sachs Commodity Industrial Metals Index (GSCI-IND)**, motivated by Jacobsen et al.
  (2019)'s finding that industrial metals' price information diffuses into stock
  prices within about a month — and correspondingly uses only a **1-month** lookback
  for the cross-asset signal regardless of the stock-side K. Crucially, the regime
  construction is **asymmetric**, not a mirror of XTSM's:
  - stock signal + , cross-asset + → **Call**
  - stock signal − , cross-asset − → **Put**
  - stock signal + , cross-asset − → **Call** (kept long — the paper's reasoning: a
    positive stock trend "still has signs of a waning uptrend" but stays net
    positive, so it's kept rather than treated as a conflict)
  - stock signal − , cross-asset + → **Jump Out** (this is the only disagreement
    case that triggers de-risking — a bearish stock trend against a bullish
    industrial-metals undercurrent is read as the stock downtrend being unreliable)

**Validation methods** (this is the paper's real strength — five independent checks,
not just one backtest):
1. **In-sample and out-of-sample predictive regressions** (rolling 120-month window,
   Newey-West HAC standard errors) of each candidate cross-asset on future stock
   returns, at 1/3/6/12/24-month horizons, both on raw asset returns and on a
   sign-only "signal regression" (removes magnitude, keeps only the timing
   information) — directly distinguishing "does the level predict returns" from
   "does just the direction predict returns," the same distinction this skill's
   paper #2 draws between predicting the regime vs. predicting the return.
2. **Alpha tests** against each other and against six common risk factors (Carhart's
   four plus RMW/CMA from Fama-French 2018/2020), to check whether outperformance is
   a real, unexplained timing skill or just disguised factor/risk exposure.
3. **Risk-adjusted performance**: Sharpe ratio, information ratio (vs. the passive
   benchmark), Sortino ratio, max drawdown, Calmar ratio.
4. **Transaction costs**: a flat 0.5%-per-trade cost (Jegadeesh & Titman's own
   convention), applied to monthly-rebalanced portfolios (so trade frequency is
   naturally low).
5. **Bootstrap/shuffle test** (this is the technique worth pulling into this skill's
   general overfitting-testing toolkit, independent of this specific strategy):
   randomly reorder (shuffle) the actual historical return sequence 2,000 times per
   portfolio — this destroys the *temporal* structure (which return follows which)
   while exactly preserving the *distributional* properties (same set of monthly
   returns, same mean/variance/skew/kurtosis, just scrambled order) — then run the
   identical (K,H) rule against each shuffled series and see where the strategy's
   real, un-shuffled result lands in that distribution of 2,000 (or, pooled across 25
   portfolios, 50,000) shuffled outcomes. If the real result sits deep in the
   distribution's right tail, the strategy is exploiting genuine time-ordering
   (momentum/timing), not just being long a favorably-skewed return distribution that
   any random reordering would also profit from.

## Key Findings

- **I-XTSM materially outperforms TSM, XTSM, and buy-and-hold across the full
  34-year sample**, in sub-samples, across business-cycle expansions and recessions,
  and through the COVID period specifically. Best portfolio (K=12, H=3) terminal
  value on $1 invested: I-XTSM $23.37 vs. TSM $13.75 vs. buy-and-hold $7.02 vs.
  **XTSM $7.70 — barely above the naive benchmark and by far the weakest of the three
  momentum strategies tested**, in this paper's specific stock-only reframing of it
  (see Independent Critique below on why this comparison may not be fully apples to
  apples).
- **The excess return survives a six-factor alpha test with a large, significant
  intercept** (t-statistic up to 17.91 in one specification) even after controlling
  for market, size, value, profitability, investment, and momentum factor exposure —
  the paper's central causal claim is that I-XTSM's edge comes from **investment
  timing**, not from taking on more systematic risk. This directly extends this
  skill's existing "predict the regime/timing, not just take more risk" theme
  (papers #2, #6) into a genuine cross-asset momentum context.
- **Risk-adjusted metrics all favor I-XTSM decisively**: Sharpe 2.64 vs. benchmark
  0.70 (XTSM's own Sharpe, 0.61, is *below* the benchmark); information ratio +0.33
  for I-XTSM vs. **negative** IR for both TSM (−0.07) and XTSM (−0.33) — meaning
  neither of the two prior-literature strategies beats the passive benchmark on a
  risk-adjusted, per-unit-of-active-risk basis in this test, only the new I-XTSM
  does; max drawdown −13% (I-XTSM) vs. −60% (buy-and-hold); Sortino 55.75 vs. lower
  for every other strategy.
- **Momentum collapse is a real, named, and demonstrated failure mode** for the
  plain TSM strategy: TSM's excess returns built up during the 2008 GFC were largely
  given back in 2009 as the market reversed sharply, a well-documented pattern (cited
  to Daniel & Moskowitz 2016, Kim et al. 2012) — I-XTSM's "jump out" mechanism
  avoided this specific drawdown by de-risking into the recovery period instead of
  staying maximally long/short through the reversal.
- **Robust to transaction costs and to using a genuinely tradable instrument**: with
  0.5%/trade costs, I-XTSM's best portfolio still returns $13.90 (vs. an unchanged
  $7.02 benchmark); repeating the whole test on SPY's actual bid/ask prices (not the
  spot index) still shows I-XTSM outperforming, at $8.18 terminal vs. lower for the
  alternatives.
- **The bootstrap test is the strongest single result in the paper**: I-XTSM's real
  (12,3) terminal return of $23.37 sits *above the 99th percentile* ($10.06) of the
  2,000-shuffle empirical distribution for that portfolio — i.e., only ~1% of random
  time-orderings of the exact same set of monthly returns would have produced a
  result this good, meaning the strategy is capturing genuine temporal/timing
  structure, not just holding a favorably-shaped return distribution.
- **The predictive driver is genuinely industrial-metal-specific, not commodities in
  general**: copper, nickel, and zinc show the strongest, most significant predictive
  coefficients on future S&P 500 returns (especially at the 3-month horizon — GSCI-IND
  itself reaches an out-of-sample-relevant in-sample adjusted R² of ~12.45% at 3
  months), while gas, cocoa, and cotton are explicitly reported as *not* significant
  and unsuitable as cross-assets. The paper also tested a REIT index as an
  alternative cross-asset and reports (without full detail — "available upon
  request") that it underperformed GSCI-IND.

## Independent Critique (not flagged by the authors)

- **The headline (K=12, H=3) result is the best-performing of 25 tested (K,H)
  combinations, reported prominently throughout the paper (terminal-value table,
  Sharpe/Sortino/Calmar charts, the bootstrap-test result) without any explicit
  multiple-comparisons correction.** The out-of-sample regression tests (Table 6) do
  validate the *predictor* (whether GSCI-IND's signal has genuine out-of-sample
  power), which is a real and useful check — but they don't address the separate
  question of whether (12,3) specifically was the best of 25 tried combinations
  partly by chance. This is the same pattern this skill's Cross-Paper Synthesis
  already flags for papers #3 and #4 (grid-search a parameter space, report the best
  result, no walk-forward or corrected-significance check on the search itself) — now
  a third independent instance of the same recurring failure mode, this time in an
  otherwise much more rigorous paper.
- **The XTSM benchmark, as tested here, may not be a fair reproduction of Pitkäjärvi
  et al. (2020)'s own result.** This paper explicitly notes it evaluates XTSM as a
  *stock-only* strategy (excluding bond-market returns from the comparison) "for a
  direct comparison with pure stock market strategies like TSM and I-XTSM" — but
  Pitkäjärvi's original XTSM is a genuine dual stock+bond portfolio, and evaluating
  only its stock leg in isolation is a different (and likely less favorable) test
  than the one XTSM's own authors ran. The paper's own footnote acknowledges this
  ("this result does not imply that the overall performance of the XTSM strategy...
  is inferior to the TSM"), but the comparison is still presented prominently
  throughout the main results as XTSM losing to TSM and barely beating the
  benchmark — worth reading that specific result with the caveat the authors
  themselves note only in a footnote, not in the headline framing.
- **The chosen asymmetric regime rule (jump out only on stock−/cross+, not on
  stock+/cross−) is plausible and consistent with the industrial-metals-diffusion
  story the paper tells, but the paper never tests the mirror-image asymmetric rule
  as an alternative specification** to demonstrate the chosen asymmetry wasn't itself
  selected because it happened to fit this specific 34-year sample. Given the
  parameter-search concern above, this is a second, related place where an
  alternative-specification robustness check is conspicuously absent.
- **Net honest read**: the bootstrap test is genuinely strong evidence that *something
  temporally real* is being captured, which is more than most papers in this skill
  demonstrate — but exactly which (K,H) combination and which specific regime
  asymmetry to trust going forward is less settled than the paper's prominent (12,3)
  framing suggests. Treat the *cross-asset concept* (industrial metals lead equity
  returns at a ~1-3 month horizon) as the well-supported takeaway, and the *exact
  parameters* as needing independent re-validation on this repo's own instruments.

## Portability

**Fully portable in concept to a `quantor`-side or even Pine-side implementation** —
unlike most sources in this skill, nothing here requires infrastructure Pine or
`quantor` lacks:
- The core signal (sign of an asset's own trailing K-month return) is a single
  `ta.roc`-style calculation, already trivial in Pine.
- The cross-asset signal (a *different* instrument's trailing 1-month return sign) is
  directly computable in Pine via `request.security()` on a correlated instrument —
  e.g., COMEX copper futures (`HG1!`) are available on TradingView, making a direct,
  literal port of I-XTSM's specific finding (equity momentum confirmed/vetoed by
  industrial-metals momentum) buildable without leaving Pine at all.
- The bootstrap/shuffle validation test, however, belongs in the `quantor` Python
  pipeline, not Pine — it requires generating and backtesting thousands of shuffled
  return sequences per parameter combination, well beyond what Pine's single-pass bar
  execution model can do. This is the one piece of infrastructure genuinely needed
  outside Pine, and it's cheap relative to the MLE/PCA/clustering machinery flagged as
  Python-only elsewhere in this skill — no numerical optimization, just repeated
  resampling and a rule already implementable in plain Python.
- The alpha/factor-regression tests and Newey-West HAC standard errors need a
  statistics package (`statsmodels` or equivalent) — standard, not a barrier, but not
  something Pine can do natively either.

## Mapping to This Repo

- **A third independent source now confirms that genuine, literature-validated
  time-series momentum operates on multi-month holding periods, not the 5m/1h
  intraday scale most of this repo's other scripts use.** Kaufman's trend-systems
  chapter (paper #9), this paper's own (K,H) grid (lookback and holding periods of
  1-24 *months*), and Moskowitz et al.'s original TSM work it extends all agree on
  this. `Kaufman_Trend_System_Swing.pine`, already built this session as a genuine
  daily/swing system, is the right home for anything built from this paper — not the
  intraday `Regime_Engine_TCO_Gatekeeper.pine` or the ORB-family scripts.
- **The specific, well-supported finding — industrial metals momentum leads equity
  index momentum at a 1-3 month horizon — is a concrete, testable, not-yet-used
  confirming signal** for `Kaufman_Trend_System_Swing.pine` or any future swing-style
  MNQ/NQ strategy: pull COMEX copper's (or the broader GSCI-IND concept, approximated
  via a copper/aluminum/zinc basket if a direct GSCI-IND feed isn't available on
  TradingView) trailing 1-month return sign via `request.security()`, and use it as
  an additional cross-asset confirmation or veto alongside the existing slow/fast
  trend agreement — structurally an extension of the same "does a related market
  confirm this" idea already used in this repo's intermarket-adjacent PDH/PDL
  tracking, just with a formally validated instrument and horizon instead of an
  intuitive one.
- **The bootstrap/shuffle test is a genuinely new, concrete addition to this repo's
  overfitting-testing toolkit** — cheaper and simpler to implement in `quantor` than
  the full Bailey/López de Prado probability-of-backtest-overfitting machinery
  (still on this skill's wishlist), and directly actionable now: for any strategy in
  this repo with a promising backtest, shuffle its trade-return sequence a few
  thousand times and check whether the actual result sits meaningfully outside the
  shuffled distribution, before trusting a single backtest number. A concrete,
  buildable partial answer to this skill's own Known Gaps item #2.
- **The 25-portfolio-grid-without-multiple-testing-correction pattern flagged in the
  Independent Critique is a third occurrence of a lesson this skill already carries**
  (papers #3, #4) — worth treating as settled at this point: any future grid search
  over strategy parameters in `quantor` needs either a walk-forward/holdout split or
  an explicit correction for the number of combinations tried, as a standing rule,
  not a per-paper reminder.

## Applied in This Repo

**2026-09-01** — Built a "Cross-Asset Confirmation" module into
`Kaufman_Trend_System_Swing.pine`, porting the I-XTSM asymmetric regime construction
directly: COMEX copper futures (`COMEX:HG1!`, chosen as the live proxy since GSCI-IND
itself isn't a chartable TradingView symbol, and because copper was individually one
of the paper's own strongest-predicting metals) supplies a 1-month trailing return
sign via `request.security()`. Faithful to the paper's actual asymmetry, not a
simplified mirror of it: a bullish stock trend is never blocked or overridden
regardless of copper's reading, but a bearish stock trend against a bullish copper
signal triggers "Jump Out" — blocking a fresh short entry and force-closing an
existing one. The bootstrap/shuffle validation technique (for `quantor`) remains
unbuilt — still a good next candidate if the user wants it.
