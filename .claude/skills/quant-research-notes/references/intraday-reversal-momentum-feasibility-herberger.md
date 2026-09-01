# Intraday Reversal vs. Momentum Feasibility (Herberger, Horn & Oehler, 2020)

**Citation:** Herberger, T. A., Horn, M., & Oehler, A. (2020). "Are intraday reversal
and momentum trading strategies feasible? An analysis for German blue chip stocks."
*Financial Markets and Portfolio Management*, 34, 179–197.
https://doi.org/10.1007/s11408-020-00356-2

**Data:** All 30 DAX 30 stocks, 5-minute candles, traded via Deutsche Börse's XETRA,
November 1, 2013 – December 23, 2014 (~14 months, ~27,000 observations per strategy).

## Core Methodology

**A linear time-transformation of two classic, originally monthly/annual frameworks
down to intraday minutes.** De Bondt & Thaler (1985)'s reversal framework used 12/24/
36/60-*month* ranking and holding periods; Jegadeesh & Titman (1993)'s momentum
framework used 3/6/9/12-*month* ranking periods. This paper rescales both by a factor
`k = 8640` (30 days/month × 24h × 12 five-minute-candles/hour), preserving the exact
*ratio* between the original periods while converting them to 5-minute-candle units:
- **Reversal strategies**: ranking periods R = {60, 120, 180, 300} min, holding
  periods H = {60, 120, 180, 300} min — 16 (R,H) combinations.
- **Momentum strategies**: ranking periods R = {15, 30, 45, 60} min, holding periods
  H = {15, 30, 45, 60} min — 16 (R,H) combinations.

**Extreme-portfolio construction** (from a fixed universe of only 30 stocks, not a
broad market): at the end of each ranking period, sort all 30 DAX stocks by their
ranking-period return. The reversal strategy buys the single worst performer (the
"loser," extendable to the worst 3 or 6 in a robustness check); the momentum strategy
buys the single best performer ("winner"). Hold for the holding period, then measure
the **market-adjusted return** — the position's return minus an equal-weighted index
of all 30 DAX stocks over the same window — not the raw return.

**Skip period between ranking and holding** (directly citing Jegadeesh 1990 and
Lehmann 1990): one 5-minute candle is deliberately skipped between the end of the
ranking window and the start of the holding window, specifically to avoid
**bid-ask bounce and price-pressure contamination** of the signal — the same concern
this repo's own signal-construction choices should be checked against (see Mapping).
Overlapping (not just sequential) ranking windows are used to maximize the number of
independent-ish test runs from the relatively short 14-month sample.

**Robustness checks**: portfolio size (1, 3, or 6 stocks per extreme portfolio), skip
period length (1, 2, or 3 candles), day-of-week effects, and time-of-day effects — all
tested explicitly, none found to materially change the results.

## Key Findings

- **A strong, statistically robust intraday reversal effect exists.** Buying the
  single worst-performing DAX stock over a 60–300 minute window and holding 60–300
  minutes produces consistently positive, highly significant (mostly p<0.01)
  market-adjusted returns across every one of the 16 (R,H) combinations tested, and
  the result survives every robustness check (portfolio size, skip period, day/time
  effects).
- **No significant intraday momentum effect exists at all** — buying the recent best
  performer over 15–60 minute windows and holding 15–60 minutes produces flat or
  significantly *negative* market-adjusted returns in most (R,H) combinations tested.
  The paper's plain conclusion: "buying former winners does not lead, on average, to a
  trading strategy that generates excess returns" at these intraday horizons.
- **The reversal effect is statistically real but economically worthless.** This is
  the paper's headline, most quotable finding: the best market-adjusted reversal
  returns top out around **0.19 basis points** per strategy (average, per 5-minute
  candle, over the holding period), while XETRA's own minimum transaction fee for
  the highest-volume trader tier is **~0.48 basis points per trade** — roughly
  **2.5× larger than the entire measured effect**. Even a maximally cost-efficient
  institutional trader, let alone a retail trader, cannot clear the round-trip cost
  of buying then closing the position. The paper's own words: "it is obviously
  impossible that retail investors or institutional investors... could realize low
  enough transaction costs" to exploit this. The one theoretical exception raised
  (not tested): sub-transaction-cost participants like market makers who could
  choose not to hedge inventory when they spot an overreaction, or true high-frequency
  traders operating below the exchange's standard fee schedule.
- **Reversal returns are also linked to genuinely higher risk, not free alpha.**
  Standard deviations of the reversal strategies' returns are large relative to the
  mean (e.g., 5.3 basis points of SD against a 0.18 basis point mean for the
  shortest-horizon reversal strategy), with leptokurtic (fat-tailed), left-skewed
  return distributions — the same "positive average, real tail risk" shape flagged
  as a caution in multiple other sources already in this skill (papers #6, #9).
- **The effect's economic infeasibility is itself explained by market efficiency,
  not by the effect being spurious.** The paper interprets its own result as
  consistent with market efficiency in the practical sense that matters to traders:
  a real anomaly exists (an overreaction to news during the ranking period that
  partially reverses), but transaction costs — the market's own friction — exactly
  arbitrage away the ability to profit from it for ordinary participants.

## Pitfalls (explicit in the source)

- **A 14-month sample, even with ~27,000 observations from overlapping windows, is
  still a single historical period** — the authors themselves flag that their result
  could in principle be specific to market conditions in late 2013–2014 (a period
  they otherwise argue was fairly representative — no crisis, roughly average
  volatility) and explicitly call for replication over a longer span.
- **No factor-model risk adjustment was possible** at 5-minute granularity, since
  standard factor data (Fama-French, etc.) are only available monthly/daily — the
  authors flag this as leaving open whether their measured "excess" return is fully
  clean of undiscovered risk-factor exposure, or just of the single equal-weighted
  market-index adjustment they did apply.
- **The sample is restricted to only 30 large, highly liquid blue-chip stocks** by
  design (to avoid the bid-ask spread and patchy-liquidity problems smaller stocks
  would introduce) — the result should not be assumed to generalize to less liquid
  instruments, where wider spreads could either eliminate the effect entirely or
  (contrary to this paper's own reasoning) make it appear larger due to
  bid-ask-bounce artifacts the skip period didn't fully control for.

## Portability

**Fully portable as a methodology, not as a specific edge to copy** — this paper
gives a template for *testing whether an intraday effect is real and tradeable*, not
a signal to implement directly:
- The **linear time-rescaling technique** (`R_i = r_i / k`, preserving ratios between
  a set of periods while changing their absolute scale) is a clean, general method
  for adapting any classic monthly/daily framework to an intraday equivalent — a more
  principled alternative to picking intraday lookback periods by feel.
- The **skip-period-to-avoid-bid-ask-bounce** technique is directly checkable and
  applicable to this repo's own Pine scripts: verify whether any signal computed at
  bar close is used for an entry decision on that *same* bar (no gap), versus
  deliberately using `[1]`-lagged or next-bar values the way this paper's one-candle
  skip does.
- The **market-adjusted-return methodology** (return minus an equal-weighted basket
  return, not raw return) is directly reusable in a `quantor` backtest to separate
  genuine idiosyncratic edge from just being exposed to the broader market's own move
  during the test window.
- The **transaction-cost break-even check** (compare the measured effect's magnitude
  directly against the actual fee schedule of the exchange/broker being used) is the
  single most valuable, directly actionable technique here — a concrete checklist
  item for any backtest in this repo claiming a small, high-frequency edge: state the
  effect size in the same units as the broker's actual commission/spread, and check
  the ratio, before claiming the edge is real.

## Mapping to This Repo

- **This paper is real, transaction-cost-aware evidence for exactly the kind of
  regime-conditional architecture `Regime_Engine_TCO_Gatekeeper.pine` already uses**
  (a TREND/EXPANSION router alongside a separate BB/MR mean-reversion router keyed
  off `richWeak`/`cheapWeak` rapZ thresholds) — this paper finds genuine intraday
  mean-reversion (60–300 min horizon) and a genuine *absence* of momentum at very
  short intraday horizons (15–60 min), which is a real-data instance of the same
  "which regime, which horizon" question that architecture is built to answer,
  though on a different asset class (equities, not index futures) and market
  (XETRA, not CME/Globex).
- **A concrete synthesis point worth naming explicitly**: this paper (intraday,
  hours-scale) finds reversal dominant and momentum absent; papers #9 and #12
  (multi-month scale) find momentum/trend-following genuinely validated. Read
  together, these three sources are consistent with a horizon-dependent regime
  switch — reversal at short-to-medium intraday horizons, momentum at multi-month
  horizons — rather than either effect being universally "the" market behavior.
  Worth keeping in mind before assuming a technique validated at one horizon
  (Kaufman's trend systems, paper #12's cross-asset momentum) transfers to a very
  different one (this repo's 5m/1h scripts), or vice versa.
- **The transaction-cost break-even check is the most directly actionable technique
  here, and should be applied to this repo's own small-edge intraday scripts** —
  particularly anything claiming a modest per-trade edge on MNQ/NQ. Futures
  commission structures differ substantially from XETRA's equity fee schedule (this
  repo's own strategy declarations typically use `strategy.commission.cash_per_contract`
  values like $2–$8, a fixed dollar amount per contract rather than a basis-point
  rate), so this paper's specific 0.48bp threshold doesn't transfer directly — but
  the *check itself* (state the average edge in the same units as the real
  commission, and compare) is exactly the discipline to apply before trusting any
  small statistically-significant backtest result in this repo as economically
  tradeable.
- **Worth checking whether any of this repo's signal-construction code has an
  equivalent to the "skip one bar" control.** If a script computes a regime/signal
  reading on a bar and allows an entry on that identical bar's close without any
  lag, it's more exposed to the kind of bid-ask-bounce/price-pressure contamination
  this paper explicitly controls for — not necessarily wrong, but worth an explicit
  check rather than an assumption either way.

## Applied in This Repo

*(none yet — the transaction-cost break-even check is the concrete, ready-to-apply
technique; note here if it's run against any of this repo's intraday strategies.)*
