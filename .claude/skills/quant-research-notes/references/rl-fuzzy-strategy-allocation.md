# RL + Fuzzy-Logic Hierarchical Multi-Strategy Capital Allocation

**Citation:** Huang, J.-C., Chen, C.-T., Chang, C.-C. & Huang, S.-H. (2025). "Strategy
allocation for financial trading using competitive reinforcement learning and fuzzy
logic." *Applied Soft Computing*, 185, 113927.

**Data:** Taiwan TXF and E-mini S&P 500 (ES) futures, 15-minute bars.

## Core Methodology

A two-level hierarchical system, explicitly modeled on a hedge-fund structure:

- **Local traders** (lower level): each runs one *fixed*, classic trading strategy —
  the paper uses (1) Dual Thrust, (2) Bollinger Bands, (3) Parabolic SAR, (4) RSI,
  (5) MACD — chosen specifically as standardized, well-known benchmarks to prove the
  allocator works, not because they're the only compatible strategies. The framework is
  explicitly "strategy-agnostic": any strategy with a measurable, trackable performance
  history can be plugged in as a local trader.
- **Global manager** (upper level): a reinforcement-learning agent that, at the start
  of each discrete trading period `ω`, assigns a capital-weight vector across the local
  traders (including a cash slot) summing to 1:
  ```
  ε_ω = [ε₁,ω, ε₂,ω, ..., ε_N,ω],   Σᵢ εᵢ,ω = 1
  ```
  Internally: raw features → **fuzzy representation layer** → CNN → deterministic
  policy gradient (DPG) → output weight vector.

**State** fed to the global manager combines *two* distinct information types every
period: (1) recent price-trend features, and (2) each local trader's own recent
realized performance (their account-value changes over a lookback window), plus the
previous period's allocation weights. The paper is explicit that this dual
"market state + strategy state" input is what distinguishes it from ordinary
single-strategy RL trading agents, which only need market data.

**Portfolio value recursion:**
```
V_{ω+1} = V_ω + Σᵢ Σ_τ εᵢ,ω · profitᵢ,τ                      (before cost)
Cω = γ_ω · Σᵢ |εᵢ,ω − εᵢ,ω−1|                                 (turnover-based trading cost)
V'_{ω+1} = V_{ω+1} − Cω
```

**Reward** for the global manager over a training episode of length `H`:
```
R = (1/H) · Σ_ω [ (price_ω · ε_ω) − Cω ]
```
i.e., the weighted average of local traders' realized profit, minus the cost of
rebalancing between periods — so the reward function itself penalizes *churning* the
allocation, not just poor stock-picking.

**Role of fuzzy logic**: converts noisy raw price and strategy-performance features
into smoothed membership-style features *before* they reach the CNN/DPG. This is
explicitly framed as an anti-overfitting mechanism (financial data is noisy; a fuzzy
layer "obtains smooth price trends and performance metrics, ensuring a balance between
short-term gains and broad market dynamics"), not merely an interpretability aid.

## Key Findings & Design Choices Worth Reusing

- **Deliberately restricted state/action space as an anti-overfitting measure.** The
  paper explicitly limits how many parameters the RL agent is allowed to adjust,
  reasoning that a more flexible/larger model is *more* prone to overfitting a noisy
  market, not better. This is the same instinct as paper #2's (regime-switching)
  single-predictor restriction — a recurring theme across multiple papers in this
  library: parsimony as a deliberate overfitting defense, not a compromise.
  - Direct citation: "applying deep neural networks in highly dynamic and noisy
    financial markets is susceptible to overfitting issues. In order to increase the
    system's generalization, we further restrict the state and action space during
    model training."
- **The system's edge shows most clearly exactly when a single strategy breaks.**
  Reported result: in a period where buy-and-hold produced a *negative* reward, the
  allocator delivered ARR = 69.66%, Sharpe = 1.63 (TXF market) — i.e., the allocator's
  job is capital preservation via reallocation away from a failing regime/strategy,
  not necessarily maximizing return in every regime uniformly.
- **Outperformed a naive equal-weight allocation baseline** (ES market: allocator ARR
  54.85%/Sharpe 0.8 vs. equal-weight's lower figures) — the dynamic reallocation adds
  value over the simplest possible multi-strategy baseline, not just over single
  strategies.
- **Explainability by design.** Because local traders use known, interpretable classic
  rules, a domain expert can watch which strategies the RL agent currently trusts
  (weights it up) during a given market phase and sanity-check whether that aligns with
  the strategy's known character (e.g., trusting a trend strategy during a strong
  bull run) — a genuine advantage over an opaque single black-box model.

## Pitfalls Flagged by the Authors

- **Idealized backtest assumptions, named explicitly as limitations**: no margin
  calls, fractional futures contracts allowed, and — importantly — **uniform
  transaction costs across all local-trader strategies**, even though real strategies
  differ in turnover and would incur different real-world costs. Any adoption of this
  architecture for real capital should model per-strategy cost/leverage realistically,
  not assume they're interchangeable.
- **Unstable reward signal from dynamic local traders**: the paper notes that when
  local traders' own parameters can also shift, the resulting reward signal becomes
  less stable and requires more training trajectories to show consistent improvement —
  a caution against making *both* the allocator and the underlying strategies adaptive
  simultaneously without extra care.
- Deep RL in noisy, low-data financial markets is repeatedly named as
  overfitting-prone throughout the paper — the fuzzy layer and restricted state/action
  space exist specifically to counter this, and are presented as necessary
  countermeasures, not optional polish.

## Portability

**Not portable to Pine Script at all** for the RL training itself (CNN + deterministic
policy gradient requires a deep-learning framework) — this has to live in the Python
`quantor` pipeline. There is also a structural reason beyond tooling: **a single Pine
script only ever sees its own equity curve**, never another script's. Cross-strategy
capital allocation is architecturally outside what any one `.pine` file can compute —
it must be an external process that reads multiple strategies' performance and either
(a) is applied manually, or (b) drives an execution layer outside TradingView (e.g. a
broker API) that sizes orders per strategy.

The **fuzzy smoothing concept** is cheaply approximable in Pine without real fuzzy
logic: replace a hard boolean gate with a continuous, clamped scoring ramp (e.g.
`math.min(math.max((value - lowThresh)/(highThresh - lowThresh), 0), 1)`) so a
borderline reading contributes partial weight instead of flipping a hard 0/1 gate —
this captures the "smooth the noisy signal before it drives a decision" spirit cheaply.

## Mapping to This Repo

This is the direct conceptual model for the user's stated "if I ever run PANDA, QUANTS,
and the continuation strategy concurrently" scenario. Two honest paths:

1. **Full version (Python, offline or semi-live):** build a `quantor`-side allocator
   that takes (a) each strategy's rolling realized performance (equity curve slope,
   drawdown state, win rate — the kind of stats several of this repo's dashboards
   already track per-strategy) and (b) a market-state feature (could reuse the TVTP-MS
   regime classifier from `references/regime-switching-tvtp.md`) as inputs, and
   outputs a capital-weight recommendation per strategy. This is a genuine research
   project on its own, not a quick add — flag it as such if the user wants to pursue it.
2. **Pragmatic Pine-native downgrade (no RL needed):** a simple rule reflecting the
   same *behavior* the paper's allocator exhibits — reduce size on any strategy
   currently in an active drawdown beyond some threshold, and/or bias size toward
   whichever strategy's rolling N-trade Sharpe/win-rate is currently higher. This can
   live as a position-size multiplier computed per-strategy in Pine (each strategy
   already tracks `tradesToday`/win-rate-adjacent stats via its dashboard conventions),
   without needing cross-script visibility if each strategy only sizes *itself* down
   during its own drawdown (self-regulation) rather than truly reallocating capital
   *between* strategies (which does require the external Python layer).
3. Whichever path is chosen, the reward-function insight — **penalize reallocation
   churn, not just poor performance** (the `Cω` turnover-cost term above) — is worth
   keeping even in the pragmatic downgrade: a position-size multiplier that flips
   abruptly on every bar recreates the exact churn problem paper #1 (signal volatility)
   already warns about, so any such multiplier should itself be smoothed/hysteresis-gated.

## Applied in This Repo

*(none yet — this remains a conceptual model pending the user's decision on whether to
pursue concurrent multi-strategy allocation; update this section if/when either the
full `quantor` allocator or the pragmatic Pine-native downgrade is built)*
