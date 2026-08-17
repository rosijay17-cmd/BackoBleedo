---
name: quant-research-notes
description: Persistent knowledge base of reusable concepts, formulas, and documented pitfalls from academic papers on algorithmic/quantitative trading (signal volatility, Markov-switching regimes, breakout/multi-indicator combination, RL+fuzzy multi-strategy allocation, implied-vs-historical volatility). Load this before designing, revising, or backtesting any Pine Script strategy or indicator in this repo, or before doing quant research for the PANDA/QUANTS/quantor work — check it for an applicable technique or a known failure mode before building new logic from scratch.
---

# Quant Research Notes

A living reference library distilled from academic papers the user has uploaded, kept
for reuse across this repo's Pine Script strategy work (PANDA/QUANTS architecture,
`quantor` Python backtesting pipeline, NQ/MNQ ORB/continuation/regime strategies).

**This file is meant to be extended, not replaced.** When new papers or strategy code
are shared:
1. Add a new `references/<slug>.md` file for each new paper using the same structure
   as the existing ones (Citation → Core methodology → Formulas/parameters → Pitfalls →
   Portability → Mapping to this repo).
2. Add a row to the Index table and Portability Matrix below.
3. Add an entry to the Changelog at the bottom with the date and a one-line summary.
4. If a new paper's methodology **contradicts** something already recorded here (e.g. a
   different recommended MA window, a conflicting claim about signal volatility, a
   different regime-count recommendation), do not silently overwrite the old entry —
   add a "Contradicts / qualifies" note under the relevant reference file pointing both
   ways, and surface it explicitly to the user rather than picking a winner unasked.
5. If the user shares new strategy code that implements or partially implements one of
   these concepts, note the file name and what was actually built under "Applied in
   this repo" in the relevant reference file, so this skill also tracks what's already
   been done vs. what's still theoretical.

## Index

| # | Concept | Reference file | Paper (short) |
|---|---|---|---|
| 1 | Trend-following signal volatility as a Sharpe-ratio discount factor | `references/signal-volatility.md` | Zoicaș-Ienciu & Pochea (2023), *Applied Economics* |
| 2 | Markov-switching regimes with time-varying transition probabilities (TVTP) + PCA dimensionality reduction | `references/regime-switching-tvtp.md` | Haase & Neuenkirch (2023), *Intl. J. of Forecasting* |
| 3 | Weighted multi-indicator signal combination | `references/multi-indicator-combination.md` | Sukma & Namahoot (2024/25), *Computational Economics* |
| 4 | RL + fuzzy-logic hierarchical multi-strategy capital allocation | `references/rl-fuzzy-strategy-allocation.md` | Huang, Chen, Chang & Huang (2025), *Applied Soft Computing* |
| 5 | Implied vs. historical volatility as a realized-vol predictor | `references/implied-vs-historical-volatility.md` | Szakmary, Ors, Kim & Davidson (2003), *J. of Banking & Finance* |

## Portability Matrix

What can run natively in Pine Script vs. what needs the Python `quantor` pipeline
(or another offline tool) before it can touch a chart.

| Technique | Pine Script (live/backtest) | Python pipeline | Notes |
|---|---|---|---|
| Signal volatility formula `v(x,y)`, adjusted Sharpe `Z(x,y)` | ✅ Direct — just count signal transitions | ✅ | Pure counting/arithmetic, no estimation involved |
| Weighted multi-indicator combination (`Σ ωᵢ·Signalᵢ`, threshold) | ✅ Direct — weighted sum of existing booleans | ✅ | The *combination* is trivial; see below for the optimizer |
| Grid-search weight optimization | ⚠️ Possible via Strategy Tester's optimizer, but treat with suspicion | ✅ Preferred | Must be walk-forward/out-of-sample, never a single in-sample max (see paper #3's own unaddressed pitfall) |
| ADX/Choppiness/ATR-ratio regime & chop filters | ✅ Already used throughout this repo | — | These are HV-type proxies — paper #5 shows HV-type measures are the *weaker* predictor relative to a true forward-vol signal Pine can't access |
| Markov-switching model estimation (EM/MLE, Hamilton filter) | ❌ Not feasible | ✅ Required | Needs iterative MLE; no Pine primitive for this |
| PCA / sparse PCA / soft-thresholding (elastic net) dimensionality reduction | ❌ Not feasible | ✅ Required | Needs matrix decomposition libraries |
| RL training (CNN + deterministic policy gradient) | ❌ Not feasible | ✅ Required | Needs a deep-learning framework; also needs cross-script equity-curve visibility Pine doesn't have |
| Fuzzy-logic feature smoothing | ⚠️ Approximable with a smoothed/clamped scoring function | ✅ Full version | A Pine "soft gate" (e.g. `math.min(math.max(...), ...)` ramp instead of a hard boolean) captures the spirit cheaply |
| GARCH(1,1) volatility forecasting | ❌ Not feasible | ✅ Required (e.g. `arch` package) | Recursive MLE fit; ATR/realized-range is the Pine-native substitute, with the bias noted in paper #5 |

## Cross-Paper Synthesis

- **Regime/vol filters should stay pure gates, not return predictors.** Paper #2's
  clearest finding is that a model which *also* tried to predict the conditional mean
  (Specification A) did worse economically than one that only modeled the
  regime/transition process (Specification B). This directly validates this repo's
  existing pattern of using `finalBias`/chop filters as binary gates and leaving
  price-target logic (ATR stops, RR multiples) as a separate, independent concern —
  don't be tempted to fold a regime score into a target/sizing formula.
- **Every "combine multiple signals" idea (papers #3 and #4) needs an explicit
  overfitting guard, because neither source paper actually demonstrates one.** Paper #3
  optimizes indicator weights by grid-search directly against the reported backtest's
  own TotalReturn — a textbook in-sample optimization the authors flag as a risk in
  their limitations section but never test out-of-sample. Paper #4's RL allocator
  handles this more seriously (deliberately restricts state/action space, uses fuzzy
  smoothing, reports idealized-assumptions limitations) but the underlying lesson is
  the same: any weight/allocation optimizer built off this repo's strategies must run
  on the `quantor` pipeline with a walk-forward or train/holdout split, never TradingView
  Strategy Tester's default in-sample "Optimize" button treated as a final answer.
- **Two independent "volatility" signals should not be conflated.** Paper #1's *signal
  volatility* (how often a rule's own buy/sell/neutral state flips) is a different axis
  from paper #5's *return/realized volatility* — the two are shown to have near-zero
  correlation empirically (paper #1, Table 3), yet both discount performance through
  different channels (signal volatility discounts via trading costs/false-signal risk;
  return volatility discounts via IV/HV forecast bias). A strategy's dashboard should
  track both separately rather than assuming a single "volatility" reading covers it.
- **No off-the-shelf paper here gives a validated edge; each documents its own
  shortfall against a naive benchmark.** Paper #2's return forecasts don't beat
  buy-and-hold statistically (only regime *classification* adds value). Paper #3's
  individual indicators all lag a buy-and-hold benchmark, and even its "winning"
  combined signal's out-of-sample validity is untested. Treat every formula in this
  skill as a *building block*, not a proven strategy — always re-validate on this
  repo's own instruments (NQ/MNQ/ES) and timeframes in `quantor` before trusting it.

## Mapping to This Repo's Architecture

The user's own naming — **PANDA** (a 3-gate signal architecture), **QUANTS**
(a scoring layer), and the **`quantor`** Python backtesting pipeline — does not appear
as literal file/folder names inside the `BackoBleedo` repo as attached to this session
(checked: no `PANDA`/`QUANTS`/`quantor` strings in any `.pine` file or `README.rst`).
So the mappings below are inferred from the recurring *pattern* already visible across
this repo's strategies (`Trend_Continuation_Zones.pine`,
`MTF_Second_Flip_Continuation_v1_2.pine`, `15_Minute_ORB_Box_Break_Return_Cross_Strategy.pine`,
etc.) — an HTF/session bias gate, a chop filter (ADX min + Choppiness max), a
cooldown/trade-count gate, a dashboard, and a dual alert path. If PANDA/QUANTS/quantor
live in code outside this repo, point Claude at that source next time so these mappings
can be corrected against the real implementation rather than inference.

- **PANDA's 3 gates ↔ paper #3's weighted combination**: if the 3 gates are currently
  hard AND-conditions, paper #3's `CombinedSignal = Σ ωᵢ·Signalᵢ` pattern is a template
  for turning graded components (chop-filter margin, distance-to-level, session-time
  decay) into a weighted score instead of a hard pass/fail, while keeping any
  genuinely-binary gates (session window, HTF bias direction) as 0/1 multipliers on top.
- **QUANTS scoring ↔ paper #1's signal volatility / paper #5's IV-vs-HV bias**: if
  QUANTS produces a quality score, cross-check it isn't accidentally re-deriving signal
  volatility (paper #1) under another name — the investigation earlier in this session
  already confirmed, for `Trend_Continuation_Zones.pine`, that its Quality Score field
  has zero references outside display code, i.e. it isn't wired into any gate yet. Paper
  #1's `b1`/`b2` (buy/sell signal-volatility components) would be a legitimate net-new
  QUANTS input distinct from anything already scored.
- **Concurrent PANDA + QUANTS + continuation-strategy allocation ↔ paper #4's global
  manager / local traders**: if these ever run concurrently for real capital
  allocation, that decision structurally cannot live inside a single `.pine` file (a
  Pine script only sees its own equity curve). It belongs in `quantor` as an offline or
  semi-live allocator, with each Pine strategy as one "local trader" whose rolling
  performance stats (already tracked via each strategy's dashboard conventions) feed
  the allocator's state. See `references/rl-fuzzy-strategy-allocation.md` for the full
  vs. pragmatic-downgrade options.
- **Chop/regime filters across this repo (ADX/Choppiness/ATR-ratio) ↔ paper #2's TVTP
  regimes / paper #5's IV-vs-HV bias**: these existing filters are all HV-type proxies
  built from price/range data — paper #5's evidence says that class of predictor is
  weaker than a true forward-looking (IV-style) signal Pine has no access to, and
  paper #2's TVTP model shows a *state-dependent* transition probability outperforms a
  fixed threshold. The `quantor` pipeline is the right place to prototype a TVTP-style
  regime classifier (see reference file for the exact model spec) and use it either to
  segment walk-forward validation windows, or to derive a simplified on-chart proxy.

## Changelog

- **2026-08-17** — Initial creation. Ingested 5 papers: signal volatility (Zoicaș-Ienciu
  & Pochea), TVTP Markov-switching regimes (Haase & Neuenkirch), multi-indicator
  combination (Sukma & Namahoot), RL+fuzzy multi-strategy allocation (Huang et al.),
  implied-vs-historical volatility (Szakmary et al.). No contradictions found between
  papers at this stage — the five cover largely non-overlapping mechanisms (signal
  churn, regime prediction, indicator combination, capital allocation, volatility
  forecasting) with the synthesis notes above covering their few points of overlap.
