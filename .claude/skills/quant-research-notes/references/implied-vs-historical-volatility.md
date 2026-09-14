# Implied vs. Historical Volatility as a Realized-Volatility Predictor

**Citation:** Szakmary, A., Ors, E., Kim, J. K. & Davidson III, W. N. (2003). "The
predictive power of implied volatility: Evidence from 35 futures markets." *Journal of
Banking & Finance*, 27(11), 2151–2175.

**Data:** Daily implied volatility (IV), historical volatility (HV), and realized
volatility (RV) for 35 futures options across 8 exchanges (equity index, interest
rate, currency, energy, metals, agriculture, livestock), sample windows within
1983–2001.

## Core Methodology

**Realized volatility (RV)**, the target being forecast, is the annualized standard
deviation of continuously-compounded daily returns over the option's remaining life:
```
RV = sqrt[ 260/(T_M − 1) · Σ_{t=1}^{T_M} (R_t − R̄)² ],   R_t = ln(P_t/P_{t-1})
```

**IV** is Black-(1976)-model-implied volatility, unweighted average of the two nearest-
to-the-money calls and puts, adjusted from calendar-day to trading-day maturity:
```
IV_t = IV_t^Bridge · sqrt(T_C / T_M)
```

**HV** is a rolling realized-volatility estimate (30-day window found to be the best
of 30/60/90-day windows tested, both for adjusted-R² and stationarity).

**GARCH(1,1) forecast (GFOR)**: recursive multi-day-ahead conditional-variance
forecasts, using only information available at the forecast date:
```
Rt = μ + εt,   εt ~ N(0, h²t),   h²t = δ + γ·ε²_{t-1} + θ·h²_{t-1}
```
averaged over the recursively-simulated path to the option's maturity.

**Three nested regression tests** (Canina & Figlewski 1993 methodology), each
answering a distinct hypothesis:
```
RVt = a + b·IVt + et            (4)  H1: unbiasedness — expect a=0, b=1
RVt = a' + b'·HVt + et          (5)  H2: compare R² of (4) vs (5) — which has more info?
RVt = a + b·IVt + b'·HVt + et   (6)  H3: does HV add anything once IV is included?
RVt = a + b·IVt + b''·GFORt + et (10) H4: does GARCH add anything once IV is included?
```

## Key Empirical Findings

- **H1 rejected (IV is biased) but directionally correct.** All 35 slope coefficients
  `b` on IV in regression (4) are positive and significant, but *all* are below 1
  (range 0.35–0.76) and 34/35 have significantly positive intercepts. Interpretation:
  **when IV is relatively high, subsequent RV tends to come in lower than IV implied,
  and vice versa** — IV over-predicts vol spikes and under-predicts vol calms, i.e.
  volatility (and its forward-looking estimate) mean-reverts and IV doesn't fully
  price that in.
- **H2 confirmed broadly: IV beats HV.** IV's regression R² exceeds HV's in 34/35
  markets (binomial-test probability of this happening by chance: < 0.0001); in 27/35
  by a wide margin (≥5 percentage points). Sugar futures is the sole consistent
  exception where HV outperforms IV.
- **H3 rejected but the effect is economically tiny.** HV's coefficient is
  significant in only 6/35 markets when included alongside IV, and adding HV only
  raises average adjusted-R² by ~1.3 percentage points over IV alone (from ~35.1% to
  ~36.4%). Statistically HV adds *something*; practically it adds almost nothing once
  IV is already in the model.
- **H4 (GARCH) result is nearly identical to the HV result.** GARCH forecasts are
  significant and positive in only 12/35 markets, and average R² improvement over IV
  alone is negligible (36.4% → 36.6%). More sophisticated modeling of historical data
  (GARCH vs. simple 30-day HV) does **not** meaningfully close the gap with IV.
- Findings are **robust across option maturities** (10 to ~70 trading days) and, for
  the S&P 500 specifically, **robust across the 1987-crash pre/post split** — this
  isn't a sample-period artifact.

## Pitfalls / Caveats Flagged by the Authors

- **IV is a biased predictor, not just a noisy one.** The systematic bias (slope < 1,
  positive intercept) means a naive "IV level = expected forward vol" reading will be
  wrong in a *predictable direction* at the extremes — high current vol readings
  should be expected to mean-revert down, low readings to mean-revert up. Any
  vol-regime classification built on a raw vol reading (IV or, in Pine's case, an ATR/
  HV proxy) inherits this same mean-reversion bias unless corrected for.
- **Measurement error from bid-ask spreads** biases the IV slope coefficient
  *downward* in these regressions — the authors note Jorion's (1995) simulation shows
  this bias is real but not nearly large enough to explain the full gap from 1.0,
  ruling out "it's just microstructure noise" as a full explanation.
- **Near-the-money option selection matters.** IV computed from at/near-the-money
  options is a materially better RV predictor than IV including deep in/out-of-the-
  money options (smile-effect contamination) — a data-construction detail that matters
  if this kind of analysis is ever replicated on different data sources.
- The one clear exception (sugar futures) is a reminder that "IV beats HV" is a
  **strong general pattern, not a universal law** — always check the specific
  instrument rather than assuming the aggregate finding transfers unconditionally.

## Portability

**Not directly portable to Pine Script for the estimation** (regression/GARCH require
iterative fitting) — and more fundamentally, **Pine Script has no access to an options
market's implied volatility for most instruments traded in this repo's strategies**
(NQ/MNQ/ES futures strategies here are built on price/OHLC data, not options chains).
The GARCH(1,1) machinery belongs in the Python `quantor` pipeline (e.g. the `arch`
package) if ever needed for offline volatility research.

## Mapping to This Repo

- **Every ATR/HV-type filter in this repo is using the *weaker* class of predictor by
  this paper's own evidence.** Filters like `MTF_Second_Flip_Continuation_v1_2.pine`'s
  `useATRRegimeFilter` (`minATRRatio`/`maxATRRatio` on `atr/atrBaseline`), or the
  Choppiness-Index-based chop filters elsewhere in this repo, are all HV-class
  measures — the paper's H2/H4 results say this class of signal captures meaningfully
  less forward-looking information than a true options-market IV would. Practical
  takeaway: **don't expect an ATR-ratio or Choppiness gate to behave like a clean
  forward-vol signal** — it's a reasonable, necessary proxy given Pine's data
  constraints, but should stay one gate among several (as this repo already does,
  layering chop filters with structure/session/bias gates) rather than being trusted
  as a standalone regime arbiter.
- **Static-threshold vol filters should be expected to misfire at the extremes.** Since
  even the *best* predictor (IV) shows mean-reverting bias, a fixed-cutoff ATR-ratio
  filter (e.g., `minATRRatio = 0.70`, `maxATRRatio = 2.00`) is plausibly systematically
  wrong near its own boundaries — worth specifically stress-testing those boundary
  regions in `quantor` walk-forward tests (does the strategy's performance degrade in a
  structured way right around the cutoff, consistent with a mean-reversion bias, or is
  it clean?) rather than assuming linear behavior across the full ATR-ratio range.
- **If any instrument traded by this repo's strategies has a liquid, accessible options
  market** (e.g. ES options, unlike NQ/MNQ's typically thinner options liquidity), IV
  could genuinely be pulled into the Python `quantor` pipeline as an *offline*
  regime-classification input superior to ATR/Choppiness — flagged as a real option
  for `quantor`-side research, not something to wait on for Pine-native work.

## Applied in This Repo

*(none yet — this paper's main use is as a caution on existing ATR/Choppiness-based
filters rather than a new component to build; update this section only if an IV-based
regime input is added to the `quantor` pipeline for an instrument with liquid options)*
