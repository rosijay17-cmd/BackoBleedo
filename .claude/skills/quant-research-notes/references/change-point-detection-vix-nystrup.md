# Non-Parametric Change Point Detection in VIX/Returns for Dynamic Asset Allocation

**Citation:** Nystrup, P., Hansen, B. W., Madsen, H. & Lindström, E. (2016). "Detecting
change points in VIX and S&P 500: A new approach to dynamic asset allocation."
*Journal of Asset Management*, 17(5), 361–374.

**Type:** Empirical, real-market backtest (VIX and S&P 500, daily, January 1990 –
September 2015, 6485 observations), tested in a genuine live-sample, one-day-at-a-time
setting with an explicit one-day implementation delay. Methodologically it is a direct
critique-and-alternative to this skill's own paper #2 (TVTP Markov-switching): the
introduction argues that fixing the number of regimes a priori "based on economic
motivations... is unlikely to be optimal," and proposes detecting regime shifts without
fitting any model with a fixed regime count, without estimating parameters, and without
assuming a distribution for the data at all.

## Core Methodology

**The problem framing** (borrowed from statistical process control, via Ross et al.,
2011): a sequence of observations `x1, x2, ...` is either identically distributed
throughout, or switches from distribution `F0` to `F1` at an unknown change point `τ`.
For any candidate split point `k`, a two-sample test statistic `D_k,t` compares the
observations before and after `k`; the overall detection statistic is
`D_max,t = max_k D_k,t`, and a change is flagged the instant `D_max,t` exceeds a
threshold `h_t`. This is fully **sequential and self-starting** — no reference/training
sample is needed before monitoring begins, and it can equally be run once on a fixed
historical window or updated live as each new observation arrives.

**Why non-parametric, and why the scale (variance) test specifically:** financial
return series are heavy-tailed (this paper's own Table 1: kurtosis 7.2 for VIX
log-returns, 11.7 for S&P 500 log-returns — both far above the Gaussian's 3). Assuming
Gaussian residuals would misclassify ordinary fat-tail outliers as change points. Citing
Ross et al. (2011), parametric Gaussian tests (t-test for location, F-test for scale)
outperform non-parametric alternatives only for *large* parameter shifts; for *smaller*
shifts and for heavy-tailed data generally, the non-parametric tests win. Of the
non-parametric candidates tried — Mann-Whitney (location), **Mood test** (scale),
Lepage (joint location+scale), Cramér-von Mises, Kolmogorov-Smirnov — **the Mood test
for scale changes was empirically the best performer**, and testing for scale alone
outperformed testing for location alone or for general/joint distributional changes.
General/joint tests found approximately the *same* change points as the scale-only
test, just with a **longer detection delay** — a strictly worse tradeoff, not a
different answer.

**The live-sample test procedure** (this is the part that makes the result credible,
not just a curve-fit): one day at a time. The first 21 observations (≈1 month) seed the
initial allocation. From there, each new day's observation is added to the sample and
tested for a change point. If one is detected to have actually occurred at day `τ < t`
(i.e., detection always lags the true change — the statistic needs the post-change
observations to accumulate before it can reject), the observations from `τ` to `t` are
used to re-estimate the new regime's volatility, the allocation is updated based on that
new estimate, and the change is **implemented at the close of day `t+1`** — a single
trading day of implementation lag is explicitly built into the test, not glossed over.
Between change points, **the portfolio is not rebalanced at all** (a deliberate design
choice, not an oversight — see Pitfalls below for its side effect).

## Formulas / Parameters

**Mood test statistic** (rank-based, scale-only): pooling two samples `A` (size `nA`)
and `B` (size `nB`, `n = nA + nB`), with `r(xi)` the rank of `xi` in the pooled sample:

```
M' = Σ_{xi ∈ A} (r(xi) − (n+1)/2)²
μM' = nA·(n²−1)/12
σM'² = nA·nB·(n+1)·(n²−4)/180
M = |(M' − μM') / σM'|                    (standardized test statistic)
```

Under the null (both samples identically distributed), `M`'s distribution depends only
on `nA`, `nB` — never on the underlying data's actual distribution, which is exactly
what makes it non-parametric/distribution-free.

**Detection threshold calibration:** the threshold `h_t` is not picked from a fixed
significance level per test — it's calibrated to a target **average run length (ARL)
of 10,000** (i.e., an *expected time between false-positive detections* of 10,000
observations under the no-change null), following the implementation in Ross (2015).
This is explicitly framed as a tradeoff dial: a longer ARL means fewer false alarms but
a longer detection delay for real changes.

**EWMA volatility re-estimation**, used once a change point is confirmed, on the
interim observations from `τ` to `t`:
```
EWMA_t = λ·EWMA_{t-1} + (1−λ)·r_t²
```
with `λ = 0.95`, corresponding to an effective memory of ~20 trading days (≈1 month).
The paper found this EWMA a *better* forecaster of realized 1-month-ahead volatility
than the VIX level itself (which carries a persistent, time-varying risk-premium bias
over realized vol — Figure 2 in the paper).

**Allocation rules tested**, all keyed off a 20% annualized-volatility reference level
(the paper's stated assumption for average long-run stock volatility):
- *Linear, long-only*: `100%` stocks at 10% vol, linearly down to `0%` at 30% vol.
- *Linear, long–short*: same slope, extended to `+100%`/`−100%` (leveraged/short) at
  the extremes.
- *Simple switching, long-only*: binary — `100%` stocks whenever estimated vol < 20%,
  else `0%` (all cash).
- *Simple switching, long–short*: binary `100%`/`−100%` at the same 20% cutoff.

**Headline results** (S&P 500 index AR/SD/SR/MDD = 0.071/0.18/0.39/0.57 throughout):

| Strategy (basis) | AR | SD | SR | MDD |
|---|---|---|---|---|
| Long-only, linear, on S&P 500 change points | 0.056 | 0.09 | 0.62 | 0.31 |
| Long-only, linear, on **VIX** change points | 0.062 | 0.10 | 0.64 | 0.24 |
| Long-only, **switching**, on VIX change points | 0.075 | 0.11 | **0.68** | 0.20 |
| Long–short, switching, on VIX change points | 0.074 | 0.15 | 0.40 | 0.44 |

Three consistent findings fall out of this table: **(1) VIX-based change points beat
S&P-500-return-based change points** on every metric tested; **(2) simple binary
switching beats the linear allocation function**, despite being the cruder rule; **(3)
long-only beats long–short** every time — the long–short variant's extra short exposure
adds volatility and drawdown without adding return, because a short leg that isn't
rebalanced grows in effective size exactly when it's losing (see Pitfalls).

**Break-even transaction costs** (one-way, in basis points, before the dynamic
strategy's realized-return edge over the named benchmark disappears):
- Long-only linear strategy vs. Static Portfolio I (S&P-500-based change points): 188bp
- Long-only linear strategy vs. Static Portfolio II (VIX-based change points): 372bp
- Long-only **switching** strategy vs. Static Portfolio III (VIX-based): 627bp
- Long-only switching strategy vs. the S&P 500 index itself: only 93bp

**Trading the VIX directly**: replicating the switching signal by selling short-term
VIX futures (rather than buying the S&P 500) in the low-volatility state harvests the
volatility risk premium (VIX futures curve was in contango most of the 2005–2015 test
window). Tested 20 Dec 2005 – 30 Sep 2015: switching-futures strategy AR 0.179 / SD
0.31 / SR 0.59 / MDD 0.40, vs. a simple long-only VIX-futures switching AR/SR/MDD of
0.045/0.47/0.18. The **best-performing single strategy in the whole paper** was fully
invested in the S&P 500 in the low-vol state and cash in the high-vol state — it beat
both the S&P 500 index and a same-average-exposure static portfolio on Sharpe *and*
realized return, with materially lower tail risk (MDD).

## Pitfalls Flagged (Explicitly, and One Worth Flagging Ourselves)

- **Not rebalancing between change points is a deliberate choice with a real, named
  side effect: it tilts the strategy toward momentum**, per the paper's own words. For
  a long position this is (mildly) helpful — winners are left to run. **For a short
  position the effect is the opposite and more dangerous**: an unrebalanced short's
  effective notional *grows* as the underlying falls (adverse move) and *shrinks* as it
  rises (favorable move) — the paper states this explicitly as part of why its own
  long–short variant underperforms. Any Pine implementation that lets a detected-regime
  position ride unmanaged between signals needs to apply this asymmetry consciously,
  not assume long and short behave as mirror images.
- **Detection is asymmetric: faster at flagging volatility *increases* than
  *decreases*.** The paper says so directly, and cross-references an independent
  finding of the same asymmetry in an HMM-based model from the same lead author
  (Nystrup et al., 2015a) — two different detection *methods*, same directional bias.
  Gradual drift (the exit from a high-vol regime is usually a slow grind, not a sharp
  drop) is harder for a change-point test to catch quickly than an abrupt spike is.
  Expect a real deployed version of this to be quick to de-risk and slower to re-risk.
- **The realized-return edge is concentrated, and the paper says exactly where.** Most
  of the S&P-500-change-point long-only strategy's outperformance vs. its static
  benchmark came from the 2008 financial crisis specifically — the paper's own
  admission: "if the big loss in 2008 was removed from the sample, the dynamic
  strategies would not outperform the index in terms of absolute return." **The
  VIX-based variant is the more convincing of the two on exactly this point**: its
  outperformance built up gradually and continuously across the full 25-year sample,
  including multi-year stretches with no crisis at all — a materially stronger claim of
  genuine, sample-wide edge rather than one-crisis-carries-the-backtest.
- **Change points are not tied to any business-cycle or macro calendar.** Distance
  between consecutive detected change points ranged from a few days to 6 years, and the
  VIX- and S&P-500-based change points frequently did *not* coincide with each other.
  Don't expect (or engineer toward) alignment with FOMC dates, earnings seasons, or
  other calendar anchors — this method finds distributional shifts, not scheduled
  events.
- **ARL = 10,000 is a hand-picked tradeoff dial, not a derived optimum.** The paper is
  explicit that this is a choice between false-alarm rate and detection delay, with no
  claim that 10,000 is uniquely correct for any other instrument, timeframe, or era.
  Re-tuning it for a different asset/timeframe is expected, not a sign the method is
  broken.
- **The test procedure (21-bar seed window, one-day-at-a-time, one-day implementation
  lag) is what makes the reported returns trustworthy — a version that peeks at the
  full-sample change-point locations before "trading" through them would silently
  reintroduce the exact look-ahead bias the live-sample design was built to rule out.**
  Any port of this to `quantor` must preserve the walk-forward, day-by-day structure,
  not run the change-point detector once over the whole history and then backtest
  against its output.

## Portability

**The Mood test itself is directly Pine-computable, unlike this skill's other
regime-detection papers.** Unlike paper #2's TVTP-Markov-switching (needs iterative
MLE/EM — hard blocker) or paper #7's DeepSupp pipeline (needs attention-network
training and DBSCAN clustering — hard blocker), the Mood statistic is closed-form rank
arithmetic: rank a rolling window's observations, compute `M'`/`μM'`/`σM'²` from
`nA`/`nB` alone, done. Evaluating `D_max,t = max_k D_k,t` over every candidate split `k`
in a rolling window of, say, a few hundred bars is an `O(window² )` nested loop —
exactly the kind of computation this project has already proven out this session (the
Dynamic P0 Delta Profile Strategy's structural-profile loops run comparable orders of
magnitude). **This is a genuinely new, directly-buildable-in-Pine regime-detection
primitive** that this skill did not have before — a real rolling change-point detector,
not just a proxy (ADX/Choppiness) standing in for one.

| Technique | Pine Script | Python (`quantor`) | Notes |
|---|---|---|---|
| Mood test statistic (rank-based scale-change test) on a rolling window | ✅ Direct — closed-form rank arithmetic, no estimation | ✅ | The genuinely new capability here; see above |
| Rolling `D_max,t = max_k D_k,t` change-point scan | ✅ Direct, `O(window²)` nested loop like this session's P0 profile scan | ✅ | Window size trades off compute cost vs. detection sensitivity |
| ARL-calibrated detection threshold | ⚠️ Approximable — hand-tune a threshold by backtesting false-alarm frequency | ✅ Preferred — proper ARL calibration needs simulation under the null | A `quantor` project could derive the Pine-side threshold once, offline |
| EWMA volatility re-estimation (`λ=0.95`) | ✅ Direct — `ta.ema(r*r, len)` is exactly this | — | Trivial; already a pattern used elsewhere in this repo |
| Volatility-threshold switching / linear allocation (20% vol reference) | ✅ Direct — simple sizing logic | — | Directly reusable position-sizing pattern |
| VIX as the change-point input series (vs. price's own returns) | ✅ Direct on NQ/ES/SPX-family instruments — `request.security(syminfo.tickerid, ..., "VIX")` or the `CBOE:VIX`/`TVC:VIX` symbol is chartable in Pine | — | Not available for arbitrary/unrelated instruments (MNQ's own realized vol would have to stand in) — see Cross-Paper Synthesis note on paper #5 |
| Selling short-term VIX futures to harvest the risk premium | ❌ Not this repo's instrument scope (no VIX futures scripts here) | — | Noted for completeness; would need a dedicated VIX-futures instrument context |

## Mapping to This Repo

- **A genuinely new, directly-buildable Pine primitive**: a rolling Mood-test
  change-point detector on realized volatility (or on the VIX itself, for NQ/ES/SPX
  family instruments) would give this repo's regime/chop filters (currently all
  ADX/Choppiness/ATR-ratio proxies — see paper #2's Mapping note) a genuinely different,
  non-parametric alternative signal, worth prototyping as its own standalone module
  before wiring into any existing strategy's gate.
- **Directly informs the MNQ/NQ scripts' volatility filters (`Dynamic_Markov_Capacity...`,
  `Adaptive_Trend_Flow...`, the `MNQ_Volume_Delta_Strategy.pine` built this session)**:
  this paper's simplest possible design — a single 20%-vol-equivalent threshold with
  binary switching — outperformed a fancier linear allocation function on this dataset.
  Before adding more continuous/graduated position-sizing curves to this repo's
  strategies, it's worth testing whether a plain threshold switch does just as well, per
  this paper's own head-to-head result.
- **A concrete, low-risk enhancement candidate for any NQ/MNQ/ES strategy in this
  repo**: since the CBOE VIX is directly chartable via `request.security()` for
  Nasdaq-100-family instruments, a VIX-level or VIX-change-point-based regime filter is
  a real, buildable addition — distinct from and complementary to this repo's existing
  ADX/Choppiness-based chop filters, and backed by this paper's finding that VIX-based
  signals outperformed price-return-based ones for exactly this kind of gating decision.
- **The long-vs-long–short asymmetry (unrebalanced short growing against you) is a
  concrete caution for any of this repo's strategies that hold a static short position
  between signals without periodic resizing** — worth auditing whether any existing
  short-side logic in this repo has this same silent asymmetry.

## Contradicts / Qualifies

**Directly qualifies (does not outright contradict) paper #2's Haase & Neuenkirch
TVTP-Markov-switching approach.** This paper's introduction explicitly argues against
paper #2's core modeling choice — fixing the number of hidden regimes in advance
("typically between two and four... based on economic motivations... is unlikely to be
optimal"). Both papers are legitimate, published, peer-reviewed approaches to the same
underlying question (how to detect regime/volatility shifts in financial time series);
neither is shown to dominate the other empirically in either paper (they're never
tested against each other directly). Recorded as a genuine, first-party methodological
disagreement in the literature this skill has now ingested on both sides of — worth
keeping in mind that "how many regimes should the model assume" is an open, contested
design choice, not a solved question with one correct answer.
