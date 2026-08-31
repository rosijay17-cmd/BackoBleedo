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
| 6 | Optimal trend-following as a two-threshold hysteresis rule on regime probability | `references/optimal-trend-following-boundaries.md` | Dai, Yang, Zhang & Zhu (2016), *Mathematics of Operations Research* |
| 7 | Attention-autoencoder + correlation clustering for dynamic support/resistance levels | `references/deepsupp-attention-support-resistance.md` | Kriuk, Ng & Al Hossain (2025), arXiv:2507.01971 |

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
| HJB free-boundary solve for the exact optimal thresholds | ❌ Not feasible | ⚠️ Possible but heavy | System of variational inequalities — theory-grounding for a design choice, not a library to import |
| Two-threshold hysteresis band (strict entry, loose exit) on a regime signal | ✅ Direct — the *structure*, not the exact optimal levels | ✅ | Doesn't need a real Wonham filter; apply to any 0-1 regime proxy Pine already computes |
| Wonham filter for a literal regime-probability `p_t` | ⚠️ Not really — needs a filtering recursion each bar | ✅ Feasible, lighter than paper #2's TVTP pipeline | A genuinely tractable middle-ground project if a literal implementation is ever wanted |
| Multi-head attention autoencoder (training) | ❌ Not feasible | ✅ Required | No backprop/gradient training of any kind in Pine |
| Rolling Spearman correlation matrix (32×32, per paper #7) | ❌ Not feasible as a matrix pipeline | ✅ Required | Pine has single-pair `ta.correlation`, not a batched matrix operation |
| DBSCAN density-based clustering | ❌ Not feasible | ✅ Required | No clustering primitives in Pine at all |
| Volume-clustered structural levels (the *goal* paper #7 targets) | ✅ Direct, via Volume Profile (POC/VAH/VAL) | — | Already built in `Supply_and_Demand_Zones_XL.pine` — achieves paper #7's stated aim (avoid redundant, evenly-spaced levels) with transparent, causally-grounded math instead of a trained model whose own reported edge is weak (see reference file's Critique) |

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
- **Asymmetric entry/exit thresholds on a regime signal aren't a whipsaw hack — they're
  what the provably optimal rule looks like.** Paper #6 derives, from first principles,
  that the optimal trend-following policy is a strict-entry/loose-exit two-threshold
  band on regime probability, with a no-trade zone between them that widens as
  transaction costs rise. This is independent, theoretical confirmation of a pattern
  this repo already uses empirically (`MTF_Second_Flip`'s "second flip" requirement,
  `BBL_MTF`'s/`Academia_PO3`'s separate enter-vs-hold thresholds on the same score) —
  and it converges with paper #2 rather than contradicting it: even though paper #6's
  stated objective is return-maximizing, the optimal policy it derives still conditions
  on nothing but the regime signal itself, the same "predict the regime, not the
  return" prescription paper #2 reaches empirically.
- **A single backtest run is a single sample path, and paper #6 proves how wide that
  variance can be even under a correctly-specified model** (identical parameters,
  identical thresholds, single-path total returns spanning roughly 0.08x to ~1,888x
  across ten simulated paths in the paper's own Table 3). Every TradingView Strategy
  Tester run on one instrument over one historical window in this repo is exactly that
  kind of single path — walk-forward validation across multiple periods in `quantor`,
  not one in-sample run, is the only way to see whether an edge is really there.

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
- **Every regime/bias gate in this repo ↔ paper #6's two-threshold hysteresis result**:
  wherever a strategy currently re-checks one shared cutoff every bar to decide both
  "may I enter" and "am I still in trend," paper #6 argues for deliberately splitting
  that into two thresholds — stricter to arm/enter, distinctly looser to remain
  armed/hold — with the gap between them widening for higher-cost instruments and
  narrowing for cheap ones (directly relevant to MNQ specifically, a low-commission
  micro contract, where the theoretically-justified no-trade band is narrower than a
  higher-cost strategy's defaults would suggest). This is the concrete architecture
  note for the MNQ trend-following design discussed this session: build the regime gate
  as a real two-threshold band from the start, not one cutoff reused for both entry and
  hold-through.

## Changelog

- **2026-08-17** — Initial creation. Ingested 5 papers: signal volatility (Zoicaș-Ienciu
  & Pochea), TVTP Markov-switching regimes (Haase & Neuenkirch), multi-indicator
  combination (Sukma & Namahoot), RL+fuzzy multi-strategy allocation (Huang et al.),
  implied-vs-historical volatility (Szakmary et al.). No contradictions found between
  papers at this stage — the five cover largely non-overlapping mechanisms (signal
  churn, regime prediction, indicator combination, capital allocation, volatility
  forecasting) with the synthesis notes above covering their few points of overlap.
- **2026-08-23** — Ingested paper #6: Dai, Yang, Zhang & Zhu (2016), "Optimal Trend
  Following Trading Rules" (*Mathematics of Operations Research*) — a stochastic
  optimal-control proof (not an empirical study, unlike papers #1-5) that the optimal
  trend-following rule under a hidden bull/bear Markov-switching model is a
  two-threshold hysteresis band on regime probability, with only finitely many trades
  almost surely and a no-trade zone that widens with transaction costs. No
  contradiction with paper #2 — see the "Contradicts / qualifies" note in the new
  reference file; the two converge on "trade the regime signal alone" from an
  empirical and a theoretical direction respectively. Directly informs the MNQ
  trend-following strategy design discussed the same session (see the Mapping section
  above): the regime/bias gate should be a genuine two-threshold band from the start.
- **2026-08-31** — Ingested paper #7: Kriuk, Ng & Al Hossain (2025), "DeepSupp:
  Attention-Driven Correlation Pattern Analysis for Dynamic Time Series Support and
  Resistance Levels Identification" (arXiv:2507.01971) — a 4-stage deep learning
  pipeline (VWAP/volume feature engineering → rolling Spearman correlation matrices →
  multi-head attention autoencoder → DBSCAN clustering) for support/resistance
  detection. Evaluated against `Regime_Engine_TCO_Gatekeeper.pine` on user request; not
  recommended for implementation — see the new reference file's Independent Critique
  (the paper's own Table 1 shows ~40% of its weighted composite score resting on
  metrics that don't differentiate between any of the 7 methods it tests, and it loses
  the highest-weighted metric to the simplest baseline) and Portability section (no ML
  training, matrix-correlation pipeline, or clustering primitive exists in Pine — a
  hard barrier, not extra effort). No contradiction with papers #1-6; this is the
  skill's first pure market-microstructure/level-detection paper, largely
  non-overlapping with the regime/allocation/volatility papers already ingested. The
  conceptual goal DeepSupp targets (non-redundant structural levels vs. naive methods)
  is already achievable in this repo via the Volume Profile (POC/VAH/VAL) module built
  in `Supply_and_Demand_Zones_XL.pine` this session — flagged as the practical
  alternative if `Regime_Engine_TCO_Gatekeeper.pine`'s simple swing-pivot levels are
  ever upgraded.
