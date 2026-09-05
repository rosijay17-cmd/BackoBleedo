# Beta Dispersion and Market Timing (Kuntz)

**Citation:** Kuntz, L.-C. (2020). "Beta dispersion and market timing." *Journal of
Empirical Finance*, 59, 235–256.

## Evidentiary basis — read this before the rest of the file

Strong by this skill's standards: 52 years of daily S&P 500 constituent data
(1964–2016), both in-sample AND genuinely out-of-sample evaluation (20-year initial
window, expanding thereafter, tested against two separate benchmarks with the
Clark-West significance correction for nested-model forecast comparison), robustness
checked against seven other known return predictors (dividend yield, short rate, cay
factor, average variance/correlation, return dispersion, sentiment, a 14-indicator PCA
composite) and across good/bad market regimes separately. The out-of-sample R² values
are real and statistically significant, but modest in absolute size (mostly 0.01–0.08)
— consistent with this skill's now-standing theme that no source here hands over a
free, large edge; this is a genuine, validated, *small* one.

## Core Content

**The definition.** Beta dispersion (BD) is the cross-sectional **spread** of individual
stocks' betas against the market at a point in time — not the market's overall
volatility, and not the return dispersion (cross-sectional spread of *returns*, a
different, already-known predictor the paper explicitly distinguishes itself from). Two
measures are given:
- **Quantile-based (QBD):** `QBD_t = mean(beta of top 10% by beta) − mean(beta of
  bottom 10% by beta)` — a simple, robust difference-of-tails statistic.
- **Standard-deviation-based (BD):** `BD_t = sqrt( Σ (w_i,t · β_i,t)² − (Σ w_i,t · β_i,t)²
  )`, computed both value-weighted and equal-weighted across all constituents, not just
  the tails.
Both are computed from **rolling betas** (3/6/12/36-month windows) of each S&P 500
constituent stock against the index.

**The economic mechanism — a genuinely different systemic-risk story than "the market
is volatile."** A market with *low* beta dispersion (all stocks' betas clustered near
1) reacts roughly uniformly to a systematic shock. A market with *high* beta dispersion
(some stocks near-zero beta, some very high) reacts asymmetrically: high-beta names get
hit hard, potentially triggering real financial distress at those specific companies
(sales/profit declines, insolvency risk) — and because firms are economically
interconnected (suppliers, counterparties, sector peers), that localized distress can
propagate as an **endogenous second-round shock** that a low-dispersion market would
never generate from the same initial shock. High beta dispersion is therefore framed
as a measure of a market's *fragility to cascading contagion*, not just "how much is
the index bouncing around" — genuinely distinct from every volatility measure already
in this skill (ATR, Garman-Klass, realized/historical vol, or paper #15's
volatility-volume correlation). The paper adds empirical teeth to this story: the
concentration of high-beta stocks within a *single industry sector* rises noticeably
before both the 2000 dotcom crash and the 2008 crisis, exactly the pattern the cascading
mechanism predicts (a systematic shock hitting one already-concentrated, high-beta
sector first).

**The headline predictive result.** Equal-weighted BD, used alone as the sole predictor
in a linear regression, is a **significant negative predictor of the S&P 500's future
excess return** at 3-, 6-, and 12-month horizons — high beta dispersion today predicts
a lower (or more negative) market return over the following months. Confirmed
out-of-sample (positive, significant `R²_OS` against both a historical-mean benchmark
and a fixed 5.1% risk-premium benchmark) and shown to add information beyond seven
other established predictors tested jointly in a multiple regression (dividend yield,
short rate, cay factor, average variance/correlation, return dispersion, sentiment, a
technical-indicator composite) — BD isn't just a proxy for something else already known
to work.

**Regime-dependence — BD is a *bad-times* predictor, not a universal one.** Splitting
the sample into good and bad market regimes (defined by whether the prior period's
market return was negative), BD's predictive power is **concentrated entirely in bad
regimes** — significant and negative there, essentially zero and insignificant in good
regimes. This is exactly the shape of result this skill has now logged from several
independent directions (see Cross-Paper Synthesis) and matches the paper's own economic
story: the predictor is explicitly built to capture *the market's ability to absorb a
shock it has already been hit by*, which is meaningless information when no shock has
occurred.

**Distributional regression — a genuinely new technique for this skill, not yet logged
anywhere else here.** Rather than a standard linear regression (which only estimates
the *conditional mean* of the future return, given the predictor), the paper fits a
**structured additive distributional regression**: both the mean *and* the standard
deviation of the future return's assumed normal distribution are modeled as functions
of the current beta dispersion, via penalized maximum-likelihood back-fitting. This
yields a full conditional probability distribution for the future return, from which
`P(future return > 0 | current BD)` can be read off directly — a strictly richer output
than a point forecast, used here as the actual investment-timing trigger.

**The resulting market-timing strategies.** Two variants, both switching between the
S&P 500 and cash/money-market based on `p = P(positive future return | BD)`:
- **Basic:** 100% invested when `p > 50%`, 100% cash otherwise.
- **Weighted:** a continuous position `X_market = 2·(p − 0.5)`, so the size of the bet
  scales with how confident the model is, capped at ±100% (a short position is possible
  when `p` is low enough).
The **weighted** strategy is the standout result: it cuts return volatility by up to
~65% versus buy-and-hold (and ~20% versus a 60/40 stock/bond benchmark) while roughly
matching or modestly trailing their average returns — a materially better Sharpe ratio
and a shallower maximum drawdown than either benchmark, i.e. a genuine risk-reduction
tool, not an alpha-maximizing one. The paper is explicit that this isn't free: turnover/
rebalancing costs are addressed directly (the weighted strategy only actually needs 15–30
rebalances/year if a Sharpe-preserving rebalancing-threshold rule is used, not monthly),
and the authors flag that realistic frictions generally erode most market-timing
strategies' apparent edge (citing Zakamulin, 2014) even though this one is shown to
survive that scrutiny better than typical timing rules.

## Pitfalls (evident from the source itself)

- **Genuinely cross-sectional, multi-security by construction.** BD cannot be computed
  from a single instrument's own price/volume history — it requires the *entire*
  constituent universe of an index (S&P 500 here), a rolling beta estimate for each
  one, and a cross-sectional dispersion statistic across all of them, recomputed every
  month. This is not a "hard to code" problem, it's a different computational shape
  than anything a single-symbol Pine script can access at all.
- **Distributional regression itself needs real statistical-modeling infrastructure**
  (the paper uses GAMLSS-style penalized-likelihood back-fitting) — not something Pine,
  or even a simple linear-regression call, can reproduce.
- **The result is index-level (S&P 500), not single-stock or single-futures-contract.**
  Nothing here says anything directly about NQ/MNQ price dynamics specifically, only
  about the broad market the Nasdaq 100 is correlated with — a macro/systemic overlay,
  not a signal about this repo's actual traded instrument's own idiosyncratic moves.
- **Modest effect size.** Out-of-sample R² values (mostly 0.01–0.08, occasionally
  higher) are statistically real but should not be mistaken for a large, obviously
  tradeable edge on their own — consistent with this skill's standing "no free lunch"
  theme.
- **The weighted strategy's outperformance is a risk-adjusted (Sharpe/volatility) story,
  not a raw-return one** — it should not be read as "beats buy-and-hold in total
  return," it explicitly does not always do that.

## Portability

| Technique | Pine Script (live/backtest) | Python pipeline | Notes |
|---|---|---|---|
| Beta dispersion computation (QBD or BD, from a full constituent universe's rolling betas) | ❌ Not feasible | ✅ Required | Cross-sectional, needs the full S&P 500 (or Nasdaq 100) constituent list and per-stock rolling regressions — same class of barrier as papers #2/#7's matrix pipelines, and paper #15's cross-stock correlation matrix |
| Using a *computed* BD reading as a live market-vulnerability overlay/gate in Pine | ⚠️ Possible via `request.seed()` or a periodically-updated manual input | ✅ Compute offline, refresh periodically | The same "compute offline in `quantor`, then feed the result into Pine as a slow-moving reference series or manual input" pattern already used for this skill's other cross-sectional/ML-blocked techniques |
| Structured additive distributional regression (joint mean+stdev modeling via penalized likelihood) | ❌ Not feasible | ✅ Required (e.g. Python `statsmodels`, R `gamlss`) | A genuinely new technique for this skill — richer than the plain linear predictive regressions used in papers #1/#5/#12/#13 |
| Deriving `P(return > 0)` from a fitted conditional distribution as a timing trigger | ✅ Direct, once the distribution parameters exist | ✅ Required to fit the distribution first | The probability calculation itself is simple algebra on a normal CDF; the hard part (fitting mean/stdev jointly) is Python-only |
| Weighted position sizing proportional to signal confidence (`X = 2·(p − 0.5)`) | ✅ Direct | — | A clean, simple continuous-sizing pattern, reusable for ANY existing 0–1 probability/confidence score this repo already computes, not specific to beta dispersion |
| Rebalancing-threshold rule (only trade when the weight change exceeds a limit, not every period) | ✅ Direct | — | A straightforward "only re-signal if drift exceeds X" gate — directly reduces overtrading/cost drag on any continuously-varying position-sizing scheme |
| Good/bad regime split by trailing return sign, tested as an explicit interaction/dummy | ✅ Direct | — | Simple conditional logic; same regime-dependent-predictor pattern already usable elsewhere in this repo |

## Mapping to This Repo

- **A genuinely new risk axis, not a competing signal.** Every predictor already in
  this skill (signal volatility, TVTP regimes, cross-asset momentum, intraday reversal,
  breakout quality) is about *directional* or *timing* edge. Beta dispersion answers a
  different question entirely — "how fragile is the broad market to a cascading
  shock right now" — and is explicitly shown to add information beyond seven other
  known predictors tested jointly. This makes it a strong candidate as a **macro
  overlay/risk-throttle**, not a replacement for anything this repo already computes:
  e.g., reduce position size or widen stops across every NQ/MNQ strategy in this repo
  when a `quantor`-computed BD reading is elevated, since that's specifically when
  systemic downside risk (not idiosyncratic Nasdaq-specific risk) is highest.
- **Best home: an offline `quantor` module, not a live Pine computation.** Given the
  hard cross-sectional barrier, the practical path is a periodic (e.g. weekly) BD
  computation in `quantor` over the S&P 500 or Nasdaq 100 constituents, published as a
  slow-moving regime label ("elevated" / "normal") that either gets manually
  transcribed into a Pine input, or published as a `request.seed()` custom data feed if
  this repo ever sets one up — the same offline-then-import pattern already flagged for
  paper #2's TVTP regime model and paper #7's DeepSupp levels.
- **Distributional regression is a genuinely new upgrade path worth flagging for
  `quantor` generally**, independent of beta dispersion specifically — any of this
  skill's existing point-forecast predictors (paper #1's signal volatility, paper #12's
  cross-asset momentum, paper #13's intraday reversal) could in principle be re-fit this
  way to get a full `P(favorable outcome)` instead of a bare sign/magnitude forecast,
  then sized continuously the way this paper's weighted strategy does — a concrete,
  broadly-applicable technique upgrade, not limited to this one paper's specific
  predictor.
- **The weighted, confidence-proportional position-sizing pattern (`X = 2·(p − 0.5)`,
  capped at ±100%) is directly reusable today**, with zero new infrastructure, on any
  existing 0–1 probability already computed in this repo — most directly the Markov
  regime-probability engine in `Dynamic_Markov_Capacity_PDH_PDL_Liquidity_Retracements_v6
  .pine` (`probabilityBull`/`probabilityBear`), which currently only gates entries with a
  hard threshold rather than sizing continuously off its own confidence level.

## Applied in This Repo

*(none yet — the confidence-proportional position-sizing pattern is the one
zero-infrastructure candidate ready to build today; the beta-dispersion overlay itself
needs a `quantor`-side module first.)*
