---
name: quant-research-notes
description: Persistent knowledge base of reusable concepts, formulas, and documented pitfalls from academic papers and reference texts on algorithmic/quantitative trading (signal volatility, Markov-switching regimes, breakout/multi-indicator combination, RL+fuzzy multi-strategy allocation, implied-vs-historical volatility, support/resistance detection, cycle analysis). Load this before designing, revising, or backtesting any Pine Script strategy or indicator in this repo, or before doing quant research for the PANDA/QUANTS/quantor work — check it for an applicable technique or a known failure mode before building new logic from scratch.
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
| 8 | Cycle identification (peak/valley measurement, triangular-weighted MACD, trigonometric curve fitting) | `references/cycle-analysis-kaufman.md` | Kaufman (2019), *Trading Systems and Methods*, Ch. 11 |
| 9 | Trend systems toolkit (bands/channels, single/multi-trend crossovers, ATR position sizing, MA-family confluence, projected crossovers) | `references/trend-systems-kaufman.md` | Kaufman (2019), *Trading Systems and Methods*, Ch. 8 |
| 10 | Intraday pivot/exhaustion concepts (ORB Kilroy, Break-Away Pivots/Laps, Y-High/Low exhaustion, gap-close reversal, EMA-translation, Inverse 78.6% target) | `references/pivot-exhaustion-grid-scheier.md` | Scheier (2014), *Pivots, Patterns, and Intraday Swing Trades*, Ch. 3 |
| 11 | Candlestick pattern catalog + pivot-point confluence (multi-timeframe agreement, first-test-only fade rule, P3T signal architecture) | `references/candlestick-patterns-and-pivot-confluence-person.md` | Person (2004), *A Complete Guide to Technical Trading Tactics*, Ch. 4 & 6 |
| 12 | Cross-asset time-series momentum (industrial metals lead equity momentum) + bootstrap/shuffle overfitting test | `references/cross-asset-time-series-momentum-xu.md` | Xu, Li, Singh & Park (2025), *Accounting & Finance* |

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
| Triangular-weighted MA / triangular MACD (fixed, known period) | ✅ Direct — a custom weighted-average kernel, same shape as any Pine MA | — | Just math; the hard part is picking a real period (see next row), not the indicator itself |
| Peak/valley cycle-length measurement (discover a candidate period) | ❌ Not for live Pine | ✅ Preferred (offline, once) | Find the period offline first, then hardcode it into a Pine oscillator — never search for it live bar-by-bar |
| Trigonometric least-squares curve fit, searching over frequency `ω` | ❌ Not feasible as a live search | ✅ Required (Solver/`scipy.optimize` or equivalent) | A *fixed*-`ω` single-frequency fit reduces to closed-form OLS Pine could compute, but finding `ω` itself is the same class of iterative/nonlinear problem as the MLE and clustering steps already flagged elsewhere in this matrix |
| Fourier/spectral analysis, MESA (Ehlers) | ⚠️ Unassessed | ⚠️ Unassessed | Not covered in the source excerpt ingested (paper #8) — flagged as a gap, not evaluated either way yet |
| Bands/channels (Keltner, %, ATR/stdev-scaled, Bollinger, Modified Bollinger) | ✅ Direct | — | Pure arithmetic/recursive smoothing; Modified Bollinger formulas are copy-portable as given |
| Single/multi-trend crossover systems (MA, EXP, BO, SWG, LRS, Donchian, Golden/Death Cross, ROC, Ichimoku) | ✅ Direct | — | `ta.sma`/`ta.ema`/`ta.highest`/`ta.lowest`/`ta.linreg` cover essentially all of it |
| ATR-scaled position sizing (`investment / (ATR × BigPointValue)`) | ✅ Direct | — | Candidate proper fix for this session's earlier zero-qty/margin-rejection sizing bugs, not just the patches actually applied |
| Moving-average-family confluence count (monotonic MA-fan agreement) | ✅ Direct | — | A `for` loop over N periods; genuinely new confirmation axis, not yet used anywhere in this repo |
| Projected MA-crossover price (CP2), Market Directional Indicator (MDI) | ✅ Direct | — | Closed-form arithmetic on rolling price sums |
| "Ahead of the crowd" positioning, portfolio replication | ⚠️ Codeable but unverified | — | No barrier to building, but paper #9 gives no backtest evidence either works |
| Techno-fundamental discretionary exit | ❌ Not systematizable | — | Requires real-time discretionary judgment about *why* a trend is happening; source's own worked example (2010→2011 Fed case) shows it failing |
| Ehlers' quotient transform (early trend ID) | ⚠️ Partial | ⚠️ Unassessed | Formula given; the roofing filter/AGC steps that complete the actual indicator aren't in the source excerpt — same shape as the Fourier/MESA gap above |
| ORB far-side exhaustion ("Kilroy"), Break-Away Lap, Y-High/Low exhaustion read | ✅ Direct | — | Mechanical level/comparison logic; this repo already has the underlying ORB/level infrastructure in several scripts (see paper #10's Mapping) |
| Floor Trader's Pivot Points (DP/S/R formula) | ✅ Direct | — | Formula is trivial; getting the all-session-vs-day-only H/L/C convention right is the actual pitfall, not the math |
| Inverse 78.6% Projection Rule (exit target) | ✅ Direct, once a Break-Away Pivot is identified | — | Projection arithmetic is trivial; detecting the Ledge itself is the harder, judgment-based part |
| Break-Away Pivot/Ledge detection, manual trend lines, Measured-Move chart-pattern targets (triangle/H&S/channel/wedge) | ⚠️ Needs a real detection algorithm | — | None of these are specified mechanically in the source; this repo's `Auto_Pattern_Detector_Targets_MarkitTick_Session_Strategy.pine` may already be relevant prior art for the pattern-target family |
| True Market Profile (TPO-based Value Area/POC) | ❌ Not native to Pine | — | No time-price-opportunity primitive in Pine; Volume Profile (already built this session) is the source's own named substitute |
| Full candlestick pattern catalog (hammer/doji variants/engulfing/harami/dark cloud/piercing/three-candle/three-method patterns) | ✅ Direct | — | Every pattern is pure `open`/`high`/`low`/`close` geometry with a bar or two of history — the most cleanly portable content in this skill so far; no repo script currently implements formal candle-pattern recognition |
| Multi-timeframe pivot confluence, "first test only" pivot-fade rule | ✅ Direct | — | Mechanical once a base pivot-point module exists; no current analogue in this repo |
| "Eight to ten new records" exhaustion counter, "pillar of strength/weakness" (multi-candle engulfing) | ✅ Direct | — | Streak counters and consumed-candle-count checks; straightforward extensions of patterns already in the candle catalog |
| Cross-asset momentum signal (e.g. industrial metals trailing 1-month return sign confirming/vetoing equity momentum) | ✅ Direct | — | A single `request.security()` call on a correlated instrument (e.g. COMEX copper) plus a sign check — no infrastructure barrier at all |
| Bootstrap/shuffle overfitting test (randomize return-sequence order, compare real result to the shuffled distribution) | ❌ Not for live Pine | ✅ Direct, and cheap | No numerical optimization needed — just repeated resampling and rerunning a rule already implementable in plain Python; a concrete, buildable partial answer to this skill's own Known Gaps item #2 |
| Six-factor alpha test (Fama-French/Carhart + Q5) to check if excess return is real timing skill vs. disguised risk exposure | ❌ Not for live Pine | ✅ Required (`statsmodels` or equivalent) | Standard regression tooling, not a barrier — just not something Pine can do |

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
- **A cycle-based decomposition (paper #8) is a genuinely different generative model
  from the regime-switching paradigm papers #2 and #6 already established here, not a
  variant of it.** Trend+seasonal+cycle+noise treats price as a sum of continuous,
  periodic components; Markov-switching treats it as a discrete hidden state with
  transition probabilities. This repo's own TCO engine (REGIME: TREND/EXPANSION/CHOP/SQZ)
  is architecturally a regime-switching classifier, not a cycle detector — paper #8
  doesn't contradict anything already recorded, but it's a reminder that "the market has
  structure" can mean two different mathematical things, and this repo has so far only
  built the regime-switching kind. Adding a genuine cycle-based signal would need its
  own from-scratch validation (see the next point), not an extension of existing gates.
- **Paper #8's own worked examples are the clearest illustration yet, across this
  entire skill, of a source policing its own claims' evidence quality in real time** —
  the cattle cycle (real fundamental mechanism, consistent measured period across two
  disjoint eras) is presented as valid, the Swiss franc "cycle" (inconsistent period,
  no proposed mechanism) as a deliberate negative example, and multi-decade
  political/war cycles as citations the author himself flags as too thin to trust
  (incompatible period claims between sources, "only three full cycles... difficult to
  tell... if the entire pattern is just a coincidence"). Worth internalizing as a
  template for evaluating *any* future pattern-detection claim in this skill, cycle or
  otherwise: does a real mechanism exist, and does the claimed period hold up across
  multiple independent samples — not just "does the chart look periodic."
- **Paper #9 independently confirms, from real multi-market backtests rather than
  theory, several patterns this skill and this repo had already converged on from
  other directions.** Its 2-consecutive-bar ROC confirmation rule is the same
  debounce principle as paper #6's proven hysteresis band and this repo's
  `MTF_Second_Flip` naming; its Bollinger-squeeze breakout filter is the same idea as
  `Regime_Engine_TCO_Gatekeeper.pine`'s `isSqueeze`/`WAIT BREAKOUT` state, just built on
  band width instead of ATR-ratio/range-efficiency; its MPTDI step-weighted system
  (1972) is the same "let regime state change trading parameters" idea as this repo's
  `riskMode`-by-`regime` pattern, just via discrete volatility steps instead of a
  continuous classifier. Multiple independent sources landing on the same handful of
  structural ideas is a stronger signal than any one of them alone.
- **Multi-gate/multi-confirmation stacking (this repo's own recurring pattern — CVD +
  Volume Trend + regime + bias, all hard-AND'd) has a real, quotable limit paper #9
  demonstrates directly**: a 2-trend crossover *substantially improved* the strongly
  trending Eurodollar market but barely moved the needle on the noisier e-mini S&P
  ("a 2-trend system improves an already-trending market, but not a noisy one," the
  source's own words). This doesn't contradict this repo's design (paper #6's
  theoretical hysteresis result still supports strict-entry gating in general), but it's
  a concrete reason to expect the TCO engine's stacked gates to help most on the
  cleanest-trending instruments and to mainly just cut signal count — not necessarily
  improve win rate — on noisier ones, and to verify that per-instrument in `quantor`
  rather than assume it uniformly.
- **A famous, historically-popular parameter set failing a direct modern retest (paper
  #9's 4-9-18 crossover, "none of the results would have convinced you to trade this")
  is the same lesson this skill's Changelog already drew from paper #8's 4-9-18-style
  political cycles and the Swiss franc cycle**: reputation, age, or a colorful name is
  never evidence. Treat any "classic"/"well-known" parameter combination proposed for
  this repo's scripts with the same skepticism as a brand-new, untested one.
- **Paper #10 is this skill's weakest evidentiary source so far — one discretionary
  practitioner's chart-based philosophy, with exactly one quantified sample (39 gaps,
  one contract, one 90-day window) in the whole chapter — and is logged with that
  weighting made explicit, the same discipline already applied to paper #8's political
  cycles. It still earns its place for two reasons: several of its techniques are
  precise and mechanically portable regardless of validation status (Break-Away Lap,
  the EMA HTF-to-LTF translation ratio, the pivot-point session-range pitfall, the
  Inverse 78.6% projection rule), and two of its claims **independently converge with
  sources already in this skill without either one citing the other** — its Y-High/
  Y-Low "initial break is exhaustion, not confirmation" claim matches this repo's
  existing liquidity-sweep/fakeout scripts, and its explicit endorsement of
  Volume-at-Price as a Market-Profile substitute matches the DeepSupp-critique-driven
  decision (paper #7) to build Volume Profile into this repo's scripts. Independent
  convergence from an unrelated, much less rigorous source doesn't upgrade either
  claim to "proven," but it's a real reason for modest additional confidence beyond
  what either source alone would justify.
- **Paper #11 gives this repo's entire confluence-gate architecture a named,
  citable, decades-old precedent.** Sklarew's 1980 "Rule of Multiple Techniques"
  ("the more indicators that confirm each other, the better the chance of an accurate
  forecast"), quoted by Person, is the same structural idea as this repo's
  `Regime_Engine_TCO_Gatekeeper.pine` AND-gating regime + bias + acceptance score +
  CVD confirmation + volume trend confirmation before calling anything tradeable —
  and Person's own "P3T signal" (pivot level + candle pattern + oscillator
  confirmation) is a concrete three-part instance of exactly that pattern. Worth
  treating as independent confirmation that this repo's confluence-first design
  philosophy has real pedigree, not as license to keep stacking gates indefinitely —
  paper #9's "a 2-trend system helps a trending market, not a noisy one" finding is
  still the operative caution on how far to take it.
- **Papers #10 and #11 independently describe the same Floor Trader's Pivot Point
  formula and the same all-session-vs-day-only session-range pitfall**, a decade
  apart (Person, 2004; Scheier, 2014) without either citing the other. Two unrelated
  practitioner sources converging on identical mechanics is a mild point in favor of
  the formula being genuinely standard trading-floor knowledge rather than one
  author's idiosyncratic construction — though it says nothing about whether trading
  off the resulting levels actually has an edge, which neither source tests
  systematically. See `references/candlestick-patterns-and-pivot-confluence-person.md`'s
  Overlap note for the full cross-reference.
- **Paper #12's bootstrap/shuffle test is this skill's first concrete, ready-to-use
  overfitting-validation tool** (Known Gaps item #2), and it sharpens exactly what
  "no free edge" should mean going forward: not just "beat a buy-and-hold benchmark,"
  but "beat what the same set of returns would earn under thousands of random
  time-orderings." Cheap enough to run in `quantor` on any of this repo's existing
  backtests without needing the heavier Bailey/López de Prado machinery still on the
  wishlist.
- **A third independent occurrence of the same recurring pattern**: paper #12's
  headline (K=12, H=3) result is the best of 25 tested parameter combinations,
  reported prominently without an explicit multiple-comparisons correction — the
  same unaddressed grid-search risk this skill already flagged in papers #3 and #4.
  Three independent papers now exhibiting this exact gap is enough to treat it as a
  standing rule rather than a per-paper caveat: any parameter grid search in
  `quantor` needs a walk-forward/holdout split or an explicit correction for the
  number of combinations tried, full stop.
- **A fourth independent source now confirms genuine, literature-validated momentum
  operates on multi-month holding periods** — paper #12's (K,H) grid runs 1-24
  *months*, the same order of magnitude as Kaufman's trend-systems chapter (paper #9)
  and the Moskowitz et al. (2012) TSM work it extends. `Kaufman_Trend_System_Swing.pine`
  remains the right home for anything built from this lineage, not this repo's
  intraday scripts.
- **A single backtest run is a single sample path, and paper #6 proves how wide that
  variance can be even under a correctly-specified model** (identical parameters,
  identical thresholds, single-path total returns spanning roughly 0.08x to ~1,888x
  across ten simulated paths in the paper's own Table 3). Every TradingView Strategy
  Tester run on one instrument over one historical window in this repo is exactly that
  kind of single path — walk-forward validation across multiple periods in `quantor`,
  not one in-sample run, is the only way to see whether an edge is really there.

## Known Gaps / Wishlist

Every source ingested so far (papers #1-11) falls into one of two buckets: academic
regime/allocation/volatility papers, or discretionary practitioner books on levels and
candle patterns. Two whole categories that matter directly for this repo's actual work
are missing entirely. Ranked by expected value if the user's library can supply them:

1. **Time-series momentum / trend-following, the actual academic literature** —
   Moskowitz, Ooi & Pedersen, "Time Series Momentum" (*Journal of Financial
   Economics*, 2012) is the seminal modern paper here, with real risk-adjusted return
   statistics across dozens of futures markets including equity index futures.
   **Partially filled by paper #12** (Xu et al. 2025), which extends and directly
   tests the original TSM strategy — but the 2012 original is still worth getting on
   its own, since paper #12 only summarizes it as a benchmark rather than reproducing
   its full cross-market evidence base.
2. **Backtest overfitting / statistical validation tools** — Bailey, Borwein, López de
   Prado & Zhu, "The Probability of Backtest Overfitting" and the companion
   "Deflated Sharpe Ratio" paper; López de Prado's *Advances in Financial Machine
   Learning* (the triple-barrier method, meta-labeling, purged/embargoed
   cross-validation). Nearly every paper in this skill's Cross-Paper Synthesis flags
   overfitting as a risk (papers #2, #3, #4, #6, #9, #12) without giving a rigorous
   way to *measure* it. **Partially filled by paper #12's bootstrap/shuffle test** —
   a real, concrete, cheap-to-implement validation technique now logged and ready to
   use in `quantor` — but the heavier machinery (PBO, Deflated Sharpe, purged CV) is
   still worth getting for a more rigorous treatment.
3. **Order flow / market microstructure** — Easley, López de Prado & O'Hara on VPIN
   ("The Volume Clock: Insights into the High-Frequency Paradigm"); Cont, Kukanov &
   Stoikov, "The Price Impact of Order Book Events." Directly relevant to sharpening
   (or honestly bounding the limits of) the CVD/order-flow module already built this
   session in `Regime_Engine_TCO_Gatekeeper.pine` — real academic microstructure work
   would clarify what a Pine-computable proxy can and can't actually capture relative
   to true order-flow signals.
4. **Position sizing / money management theory** — Ralph Vince, *Portfolio Management
   Formulas* or *The Mathematics of Money Management* (Optimal f); the original Kelly
   criterion paper (J. L. Kelly, 1956) and Ed Thorp's trading adaptations of it. This
   repo currently uses ad hoc ATR-based and percent-of-equity sizing (see paper #9's
   Mapping section) with no formal framework to check whether that sizing is leaving
   edge on the table or risking ruin.
5. **Volatility modeling beyond IV-vs-HV** — Corsi's HAR-RV ("heterogeneous
   autoregressive" realized volatility) model, notably simple and effective relative
   to GARCH; the original Engle/Bollerslev ARCH/GARCH papers for foundational
   grounding beneath paper #5's IV/HV comparison.
6. *(Lower priority, still useful)* Regime-detection alternatives beyond TVTP
   Markov-switching — Bayesian online changepoint detection (Adams & MacKay) or
   hidden semi-Markov models — since paper #2 is currently this skill's only
   regime-detection paradigm.

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
- **2026-08-31** — Ingested paper #8: Kaufman (2019), "Cycle Analysis" (Ch. 11 of
  *Trading Systems and Methods*, uploaded as a 21-page excerpt). A textbook survey, not
  an empirical study — first source in this skill of that kind, and it introduces a
  genuinely new generative-model paradigm (trend+seasonal+cycle+noise decomposition)
  distinct from the Markov-switching regime paradigm papers #2/#6 already established
  here; see the new Cross-Paper Synthesis notes. Practical takeaways: the triangular
  MACD (a triangular-weighted MA pair, differenced) is directly portable to Pine, but
  only once a genuine periodic component is confirmed offline for the actual
  instrument/timeframe — the source's own cattle-cycle (valid, fundamentals-backed) vs.
  Swiss-franc (invalid, no mechanism, inconsistent period) contrast is the operative
  lesson, more than any formula. Several of the source's own later cycle claims
  (8.6-year business cycle, 25/54-year political cycles) are flagged by the author
  himself as too thin to trust — carried into the reference file's Key Findings rather
  than treated as usable signal. No contradiction with papers #1-7. The excerpt stops
  before the chapter's own stated main methods (Fourier/spectral analysis, Ehlers'
  MESA) — flagged as an open gap if the rest of the chapter or a dedicated source is
  ever supplied.
- **2026-08-31** — Ingested paper #9: Kaufman (2019), "Trend Systems" (Ch. 8 of
  *Trading Systems and Methods*, uploaded as a 56-page excerpt). By far the most
  directly applicable source in this skill so far — real multi-market backtest tables
  (not single anecdotal charts) covering bands/channels, single- and multi-trend
  crossover systems, ATR-based position sizing, and MA-family confluence, almost all of
  it directly Pine-portable (a rarity here). Key empirical findings: ~35% win rate is
  the normal trend-following profile (winners must average ≥2.85x losers); exponential
  smoothing consistently underperforms simple MA/momentum; no single trend system wins
  across all instruments; a 2-trend confirmation system helps a strongly trending
  market (Eurodollar) far more than a noisy one (e-mini S&P) — see the new Cross-Paper
  Synthesis notes for how this bears on this repo's own multi-gate architecture. Several
  ideas in this chapter (Bollinger squeeze, MPTDI's regime-conditional parameters, ROC's
  2-bar confirmation) turn out to be things this repo and this skill had already
  independently converged on from other directions — logged as convergent validation.
  Also surfaces two concrete, not-yet-built candidates for this repo: an ATR-scaled
  position-sizing formula (a proper fix for the zero-qty/margin-rejection bug class
  root-caused earlier this session in the Trend Following Strategy v6 files) and a
  moving-average-family confluence count as a genuinely new confirmation axis for
  `Regime_Engine_TCO_Gatekeeper.pine`. No contradiction with papers #1-8.
- **2026-09-01** — Ingested paper #10: Scheier (2014), "Pivot/Exhaustion Grid" (Ch. 3 of
  *Pivots, Patterns, and Intraday Swing Trades*). This skill's first purely
  discretionary/practitioner source — logged with an explicit evidentiary-weight
  caveat (one 39-gap anecdotal sample is the only quantified claim in the chapter; see
  the new reference file's opening note). Covers ORB-as-all-day-level exhaustion
  ("Kilroy"), Break-Away Pivots/Ledges, Break-Away Laps (same family as a Fair Value
  Gap, which the user already chose to drop from `Regime_Engine_TCO_Gatekeeper.pine`
  earlier this session), Y-High/Y-Low exhaustion (not continuation), gap-close
  reversal behavior, an HTF-to-LTF EMA-period translation ratio, the Floor Trader's
  Pivot session-range pitfall, and the Inverse 78.6% Projection Rule for exit targets.
  Two claims independently converge with existing skill entries without either source
  citing the other — see the new Cross-Paper Synthesis note. No contradiction with
  papers #1-9.
- **2026-09-01** — Ingested paper #11: Person (2004), "A Complete Guide to Technical
  Trading Tactics" (Ch. 4 "Candle Charts" and Ch. 6 "Pivot Point Analysis"). Same
  evidentiary category as paper #10 (practitioner's book, worked chart examples, no
  systematic backtest) — logged with that weighting stated explicitly. Two chapters
  worth of content: a full, precisely-defined, and unusually cleanly-portable
  candlestick pattern catalog (hammer/star/doji variants/engulfing/harami/dark cloud/
  piercing/three-candle patterns/three-method continuation patterns) that no script in
  this repo currently implements; and pivot-point techniques including multi-
  timeframe pivot confluence, a "first test only" pivot-fade rule, an "eight to ten
  new records" exhaustion counter, and the "pillar of strength/weakness" multi-candle
  engulfing refinement. Overlaps with paper #10 on the Floor Trader's Pivot Point
  formula and its all-session-vs-day-only pitfall — cross-referenced rather than
  re-derived; see the new reference file's Overlap note and the new Cross-Paper
  Synthesis note on that convergence. Also surfaces Sklarew's 1980 "Rule of Multiple
  Techniques," a decades-old, explicitly-named precedent for this repo's own
  confluence-gate architecture. No contradiction with papers #1-10.
- **2026-09-01** — Ingested paper #12: Xu, Li, Singh & Park (2025), "Cross-asset
  time-series momentum strategy: A new perspective" (*Accounting & Finance*),
  supplied by the user in response to this skill's own Known Gaps item #1. A genuine
  academic paper extending Moskowitz et al. (2012)'s TSM and Pitkäjärvi et al.
  (2020)'s XTSM: replaces XTSM's bond cross-asset signal with the GSCI Industrial
  Metals Index (motivated by industrial metals' ~1-month information diffusion into
  equity prices), with an asymmetric 3-regime construction (Call/Put/Jump Out). Five
  independent validation methods (predictive regressions with in- and out-of-sample
  tests, six-factor alpha tests, risk-adjusted performance, transaction costs, and a
  bootstrap/shuffle test) — the most rigorous evidentiary basis of any source in this
  skill so far. The bootstrap test partially fills Known Gaps item #2 as a concrete,
  ready-to-use overfitting-validation tool. Independent critique flags the headline
  (K=12,H=3) result as the best of 25 tested combinations without a multiple-
  comparisons correction — a third occurrence of the same pattern already flagged in
  papers #3 and #4, now treated as a standing rule rather than a per-paper caveat —
  and notes the paper's XTSM benchmark may not fairly reproduce Pitkäjärvi et al.'s
  own dual stock+bond result. Confirms (a fourth independent source) that
  literature-validated momentum operates on multi-month holding periods, reinforcing
  that `Kaufman_Trend_System_Swing.pine`, not this repo's intraday scripts, is the
  right home for anything built from this lineage. No contradiction with papers #1-11.
