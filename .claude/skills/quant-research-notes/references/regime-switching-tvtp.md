# Markov-Switching Regimes with Time-Varying Transition Probabilities (TVTP)

**Citation:** Haase, F. & Neuenkirch, M. (2023). "Predictability of bull and bear
markets: A new look at forecasting stock market regimes (and returns) in the US."
*International Journal of Forecasting*, 39(2), 587–605.

**Data:** Weekly S&P 500 excess returns (over 3M T-bill), Nov 1989–May 2021; 146
macro-financial predictor variables; recursive out-of-sample test on the most recent
864 weeks (first training window ends Oct 2004).

## Core Methodology (3 steps)

**Step 1 — Dimensionality reduction.** From 146 weekly macro/financial variables,
extract a small number `q` of latent factors via four alternative techniques:
- **Conventional PCA** (`X = UDVᵀ`, keep first `q` components via the Bai & Ng (2002)
  `ICp2` information criterion with an automatic elbow rule).
- **Sparse PCA** — a regularized-regression reformulation of PCA (ridge + LASSO
  penalties on the loadings) that zeroes out some variable loadings, trading a little
  captured variance for interpretability and lower overfitting risk.
- **Soft thresholding** — an elastic-net (LASSO+ridge) preselection *targeted at a
  specific outcome variable* (future excess return, or next-period VIX as a bear-regime
  proxy when the target is latent) before PCA, keeping only the top 75 ranked
  predictors. Elastic net is preferred over plain LASSO here because with groups of
  correlated predictors, LASSO picks only one representative while EN "stretches the
  net to retain all the big fish."
- Combine soft-thresholding with either PCA or sparse PCA → 4 predictor sets total,
  plus a 5th set of directly-observable popular predictors (lagged return, dividend-
  price ratio, VIX, term spread, credit spread, PMI, variance risk premium) as a
  simpler baseline.

**Step 2 — Markov-switching (MS) model with TVTP.** Two regimes (0 = bull, 1 = bear).
Base dynamics:

```
rt = µ_St + ut,   ut ~ i.i.d. N(0, σ²_St),   Pr(St = j | St-1 = i) = p_ij
```

**Specification A** (mean *and* transitions predictable):
```
rt = µ_St + ε_St·z_{t-1} + ut
p_i0,t = exp(ς_i0 + φ_i0·z_{t-1}) / (1 + exp(ς_i0 + φ_i0·z_{t-1}))     [logit link]
```
**Specification B** (transitions only; returns follow a regime-dependent random walk):
same, but constrained `ε_St = 0`.

`z_{t-1}` is a *single* predictor (one PC, one sparse PC, or one observable variable)
per model — deliberately restricted to avoid the estimation instability that comes
from over-parameterizing the switching equation. Estimated via maximum likelihood
(EM algorithm, following Hamilton 1990).

**Prediction** (Hamilton 1989 filter), one-step-ahead:
```
p̂ⱼ_{t+1} = Pr(St+1=j | Ωt) = Σᵢ p_ij,t · Pr(St=i | Ωt)
```
Return forecast is the regime-probability-weighted average of regime-conditional
expectations:
```
r̂_{t+1} = (1 − p̂_{t+1})·E[rt+1|St+1=0] + p̂_{t+1}·E[rt+1|St+1=1]
```

**Step 3 — Forecast combination.** Rather than one kitchen-sink model, estimate many
single-predictor models and pool them in clusters (by predictor-source × specification),
using either simple averaging (`wₘ = 1/M`) or Bayesian Model Averaging weighted by BIC
(`wₘ ∝ exp(−Δₘ/2)`, `Δₘ = BICₘ − BIC*`). 20 total forecast combinations from 5 predictor
clusters × 2 specifications × 2 weighting schemes.

## Key Findings

- **Specification B beat Specification A economically.** Modeling the conditional mean
  in addition to the transition process ("Specification A") introduced extra noise and
  *hurt* the forecasts' economic performance relative to modeling transitions only
  ("Specification B"). Direct lesson: predicting *when a regime changes* is a more
  reliable task than *also* trying to predict *the return within that regime*.
- **Regime forecasts add real, statistically-robust economic value** (beat multiple
  benchmarks on risk-adjusted performance measures), **but the underlying return
  forecasts do not statistically beat common benchmarks** on raw returns — though they
  still lower realized volatility and improve tail-risk measures for a risk-averse
  investor. Evaluate "can this classify the regime" and "can this forecast the return"
  as two separate, independently-assessed claims.
- **Predictive value concentrates in recessions/turmoil**, consistent with prior
  literature (Henkel et al. 2011, Rapach & Zhou 2013) — a regime-based edge is not
  uniform across the sample; expect most of the value in exactly the periods a
  volatility/chop filter would also flag.
- **Simple average forecast combination ≈ Bayesian Model Averaging** — no clear
  advantage found for the more complex BMA weighting in this application.
- **Shrinkage (sparse PCA and/or soft thresholding) is recommended over plain PCA** —
  their best model used a *targeted sparse* PCA specifically.
- Two regimes (not three or more) was a deliberate choice: cleaner economic
  interpretation (calm/positive-drift regime vs. volatile/negative-drift regime),
  existing two-regime dating rules for evaluation, and — importantly — more than two
  regimes tended to produce *unstable estimation* in this out-of-sample setting with
  many candidate predictors.

## Pitfalls Flagged by the Authors

- **Overfitting risk from over-parameterized transition equations** is explicit: prior
  work (Guidolin & Hyde 2012; Kole & van Dijk 2017) that put *multiple* variables or
  *more than two* regimes into the switching equation got "rather disappointing
  results," which the authors attribute to overly complex modeling of the switching
  process — hence their deliberate one-predictor, two-regime restriction.
- Model uncertainty and parameter instability are named as *the* central challenge of
  stock-return predictability research generally (Pesaran & Timmermann 1995) — the
  entire three-step architecture (shrinkage → single-predictor MS models → forecast
  combination) exists specifically to hedge against this, not to squeeze out maximum
  in-sample fit.
- Real-time discipline: the recursive out-of-sample exercise explicitly accounts for
  publication lags, data revisions, and transaction costs — a reminder that a backtest
  using contemporaneously-available "clean" data (no revisions, no reporting lag) will
  overstate real-world performance for any strategy using macro/fundamental inputs.
- The paper is explicit that regime *count* is fundamentally uncertain since the state
  is latent — don't treat "2 regimes" as a proven fact, it's a modeling choice made
  for stability and interpretability reasons that happened to work well here.

## Portability

**Not portable to Pine Script** for the estimation machinery — PCA/sparse PCA, EM/MLE
estimation of a TVTP-MS model, and the Hamilton filter all require iterative numerical
optimization and matrix decomposition unavailable in Pine. This entire pipeline belongs
in the Python `quantor` backtesting stack (e.g. `statsmodels`, `scikit-learn` for PCA/
elastic net, a custom or `statsmodels`-adjacent MS-model implementation).

What *is* usable in Pine, as a simplified analogue, not a replacement:
- A **state-dependent threshold** instead of a fixed one — e.g., let the ADX/Choppiness
  chop-filter cutoff itself be a function of a smoothed realized-vol percentile, so the
  "transition probability" into the trending/tradeable state responds to current
  conditions the way TVTP's logit link does, even though it isn't a real MLE-fit model.
- Using the regime label itself (once computed offline in `quantor`) purely as a
  **backtest segmentation tool** — split a Pine strategy's `quantor`-run backtest
  results by the offline-computed bull/bear label to see if performance is regime-
  concentrated, without needing the regime model to run live on the chart at all.

## Mapping to This Repo

- **Direct complement (not replacement) for the existing ADX+Choppiness chop filter.**
  Every strategy in this repo using a fixed `minADX`/`maxCHOP` or `minATRRatio`/
  `maxATRRatio` gate (e.g. `MTF_Second_Flip_Continuation_v1_2.pine`'s
  `useATRRegimeFilter`) is using a fixed-threshold regime proxy. This paper's core
  message — state-dependent transition probabilities beat fixed thresholds, and
  modeling the regime *alone* (not also the return) is more robust — argues for
  prototyping a `quantor`-side TVTP regime classifier and using it as a *validation*
  layer: does the Pine strategy's edge hold up specifically in the offline-classified
  bull/calm regime vs. the bear/turbulent one? If the edge is regime-concentrated (very
  plausible, per the "predictability concentrates in recessions" finding), that's a
  reason to consider gating the strategy by an approximated on-chart regime proxy
  rather than assuming it should trade uniformly across all conditions.
- **"Predict the gate, not the price" discipline applies directly to `finalBias`- style
  filters already used across this repo's strategies** (e.g. the confirmed-1H+4H-
  structure `finalBias` in `MTF_Second_Flip_Continuation_v1_2.pine`). These are already
  built as pure directional gates, not return predictors — Specification B's win over
  Specification A is empirical support for keeping that architecture rather than, say,
  trying to also have the bias filter estimate expected move size.

## Applied in This Repo

*(none yet — update this section if a `quantor`-side TVTP regime classifier or an
on-chart state-dependent-threshold proxy is built, noting the file/module and what
predictor set was used)*
