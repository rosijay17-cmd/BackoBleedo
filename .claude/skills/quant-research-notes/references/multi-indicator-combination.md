# Weighted Multi-Indicator Signal Combination

**Citation:** Sukma, N. & Namahoot, C. S. (2024/2025). "Enhancing Trading Strategies:
A Multi-indicator Analysis for Profitable Algorithmic Trading." *Computational
Economics*, 65, 3807–3840.

**Data:** AAPL daily data, Jan 2013–Apr 2023 (2,599 days), via Yahoo Finance API.

## Core Methodology

Six indicator signals, one per family (trend/momentum/volatility/volume), each already
reduced to a discrete signal:

| Indicator | Family | Known weakness |
|---|---|---|
| MA20/MA50 crossover | Trend-following | Delayed signals |
| MACD | Trend-following (momentum) | Lagging indicator |
| RSI | Momentum | False signals in range-bound/low-vol markets |
| Bollinger Bands | Volatility | False signals in range-bound markets |
| On-Balance Volume (OBV) | Volume | Inconsistent in choppy markets |
| Ichimoku Kinko Hyo | Trend-following | Complex to interpret |

The paper's Table 3 is a deliberate design checklist: for each indicator, which *other*
indicator in the set "covers" its documented weakness (e.g. MACD's lagging nature is
covered by MA20/MA50, RSI, Bollinger, and OBV all having faster/different failure
modes). The selection isn't "throw indicators at it" — it's picking indicators whose
weaknesses are complementary.

**Combination.** Each indicator `i` gets an integer weight `ωᵢ ∈ {0,1,2,3,4}` (0 = off).
Grid-search over the full Cartesian product of weight combinations
`𝒲 = {(ω1,...,ωn) | ωᵢ ∈ {0,...,4}}`, selecting `𝒲* = argmax TotalReturn`. Combined
signal is a weighted sum, thresholded at zero:

```
CombinedSignal_t = Σᵢ ωᵢ · Signal_i,t

Buy  (B_t = 1)  if CombinedSignal_t > 0
Sell (S_t = -1) if CombinedSignal_t < 0
(no action otherwise)
```

Each `Signal_i` is itself a discrete ±1/0 signal from that indicator's own standard
rule (e.g. MA20 crossing above MA50 → +1, RSI crossing out of oversold → +1, etc.).

## Key Empirical Finding

Individual-indicator total returns over the backtest window: MA20/50 = 237%,
RSI = 202%, MACD = 334%, Bollinger = 257%, OBV = 331%, Ichimoku = 280%. The
combined, weight-optimized multi-indicator signal returned **837%** — beating every
individual indicator and (per the paper's own Table 5) also beating the stated
buy-and-hold benchmark of 765% over the same window. (Note: the paper's own prose
elsewhere describes the "multi-indicator benchmark" as *outperforming* the individual
indicators without beating buy-and-hold — this is an internal inconsistency in how the
paper labels its own benchmark column vs. its combined-strategy column; Table 5's raw
numbers are the more reliable source and are quoted above. Flag this if citing the
paper's prose claims directly.) Max drawdown for the combined signal (22.8%) was also
the lowest or tied-lowest of all variants tested, and it had the highest win rate
(63.9%) and profit factor (2.75).

## Pitfalls Flagged (and Unaddressed) by the Authors

- **Explicitly acknowledged, not mitigated:** "overfitting and data snooping biases
  pose significant risks in model development, requiring careful validation and
  robustness checks" — this appears in the paper's own limitations discussion, but
  **no train/test split, walk-forward validation, or out-of-sample holdout is
  described anywhere in the methodology.** The weight grid-search that produced the
  837% headline number optimizes directly against the *same* 2013–2023 AAPL sample
  used to report the result. Treat the specific 837% figure, and by extension any
  specific optimized weight vector, as **not validated** — the *combination mechanism*
  is the reusable idea, not this paper's particular weights.
- Single-instrument, single-asset-class backtest (AAPL only) — the authors' own
  "limitations and avenues for further research" section flags this as narrow.
- The paper's headline conclusion is itself a caution: even the *combined* signal fell
  short of the benchmark in the framing the authors emphasize in their abstract/
  discussion ("though falling short of benchmark performance, highlighting the need
  for further refinement") — despite Table 5's raw numbers showing otherwise, the
  authors' own stated takeaway is that individual technical indicators, even combined,
  are not guaranteed to beat a simple buy-and-hold baseline. Don't assume "combine more
  indicators" is a free path to beating buy-and-hold; validate on the specific
  instrument.

## Portability

The **combination formula and threshold logic are trivially portable to Pine
Script** — it's just an integer-weighted sum of existing ±1/0 signal booleans, already
the kind of thing Pine strategies do natively. The **grid-search weight optimizer**
should *not* be run as a one-shot in-sample search; if used at all, run it in the
Python `quantor` pipeline with a proper walk-forward or train/holdout split, or via
TradingView's Strategy Tester optimizer only with an explicit out-of-sample check
before trusting the result.

### Pine Script sketch

```pine
int wMA   = input.int(1, "Weight: MA20/50",   minval=0, maxval=4, group="Combination Weights")
int wRSI  = input.int(1, "Weight: RSI",       minval=0, maxval=4, group="Combination Weights")
int wMACD = input.int(1, "Weight: MACD",      minval=0, maxval=4, group="Combination Weights")
int wBB   = input.int(1, "Weight: Bollinger", minval=0, maxval=4, group="Combination Weights")
int wOBV  = input.int(1, "Weight: OBV",       minval=0, maxval=4, group="Combination Weights")

// each sigX is an existing ±1/0 boolean-cast signal already computed elsewhere
int combinedSignal = wMA*sigMA + wRSI*sigRSI + wMACD*sigMACD + wBB*sigBB + wOBV*sigOBV

bool buySignal  = combinedSignal > 0
bool sellSignal = combinedSignal < 0
```

Weight values are exposed as inputs (rather than hardcoded from a single in-sample
run) specifically so they can be walk-forward tuned per-instrument in `quantor` and
re-entered, not baked in from one grid search.

## Mapping to This Repo

- **Direct template for combining PANDA's 3-gate signals with QUANTS scoring.** If the
  3 gates are currently hard AND-conditions, this paper's pattern is the template for
  converting the *gradeable* components (e.g. chop-filter margin above/below its
  threshold, distance from an ORB/structural level, time-of-session decay) into a
  weighted-sum score, while keeping any genuinely-binary gates (session window active,
  HTF bias direction, day-halt state) as hard 0/1 multipliers layered on top of the
  weighted score rather than folded into it — mirrors this repo's existing convention
  (e.g. `commonEntryPass` as a hard AND-gate feeding into `canLongNow`/`canShortNow` in
  `MTF_Second_Flip_Continuation_v1_2.pine`) of separating hard gates from graded ones.
- **Use Table 3's "weakness-coverage" logic as a checklist before adding any new
  indicator/gate** to an existing strategy: pick additions whose known failure mode is
  covered by something already present, rather than stacking near-duplicate trend
  filters (this repo already layers ADX+Choppiness+EMA+Efficiency-Ratio filters in
  several strategies — worth auditing whether each one actually covers a distinct
  failure mode of the others, per this paper's framework, or is partially redundant).
- **Weight optimization discipline**: any weighted-combination gate built for this
  repo's strategies should have its weights tuned in `quantor` with a walk-forward
  split, exactly because this paper demonstrates — via its own unaddressed limitation —
  how easy it is to report an inflated headline number from a single in-sample grid
  search.

## Applied in This Repo

*(none yet — update this section if a weighted-combination gate is built into any
strategy file, noting the file name, which signals were combined, and whether the
weights were walk-forward validated in `quantor`)*
