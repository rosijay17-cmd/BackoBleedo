# Signal Volatility as a Sharpe-Ratio Discount Factor

**Citation:** Zoicaș-Ienciu, A. & Pochea, M. M. (2023). "What drives trend-following
profits in stocks? The role of the trading signals' volatility." *Applied Economics*,
55(32), 3788–3805.

**Data:** 1,618 global blue-chip stocks, 43,911 evaluation subperiods (125-trading-day,
~6-month windows), 2004–2018, plus a DJIA 1896–2018 robustness check.

## Core Methodology

A trend-following (TF) rule generates a daily signal series `Xₜ ∈ {Buy, Sell, Neutral}`
(here: price vs. a moving average with a `±f%` no-trade band). An investor's *trading
strategy* `s = (x, y)`, `x, y ≥ 0`, converts signals into exposure: `K` under Neutral,
`(1+x)·K` under Buy (x > 0 = leveraged buy), `(1−y)·K` under Sell (y > 1 = short-selling).
`s = (0,0)` degenerates to passive buy-and-hold (BH).

**Signal volatility** `v(x,y)` measures how much of a rule's signal series consists of
*expensive* transitions (Buy↔Sell, which trade the full `(x+y)K`) vs. *cheap* ones
(Buy↔Neutral or Sell↔Neutral, which trade only `xK` or `yK`), normalized to `[0,1]`:

```
v(x,y) = (1/(x+y)) · (b1·x + b2·y)

where, over T signals with T−1 possible transitions:
  b1 = (n_BS + n_BN) / (T − 1)   -- buy-side signal volatility component
  b2 = (n_BS + n_SN) / (T − 1)   -- sell-side signal volatility component
  n_BS = # Buy↔Sell transitions, n_BN = # Buy↔Neutral, n_SN = # Sell↔Neutral
```

`b1`/`b2` are the practically useful outputs: two percentages, one per side, that
summarize how "churny" a rule's buy and sell signals are, independent of the specific
trading strategy `(x,y)` used to trade them.

**Trading-risk-adjusted Sharpe ratio.** Standard Sharpe ratio for the rule under
strategy `(x,y)`: `SRxy = (ER(x,y) + r_BH − r_F) / σxy`. The paper's proposed discount:

```
Z(x,y) = SRxy / (1 + v(x,y))
```

which, expanded, isolates the rule's intrinsic buy/sell excess-return coefficients
(`a1`, `a2`) from the investor's leverage choice:

```
Z(x,y) = [(x+y) / (x(1+b1) + y(1+b2))] · [(a1·x + a2·y + r_BH − r_F) / σxy]
```

Special cases: symmetric strategy `x=y` → `Z(x,x) = 2·SRxx/(2+b1+b2)`; no-leverage buy
`x=0` → `Z(0,y) = SR0y/(1+b2)`; passive BH `x=y=0` → `Z(0,0) = SR_BH` (no discount, since
`v(0,0)=0` by construction).

## Key Empirical Finding

Return volatility (`σ_BH`) has a **bidirectional** effect on TF profit, and you only see
the true (positive) direct effect once signal volatility is controlled for:

```
R_B ≈ (β1 − β2·σ_BH)·r_BH + (β3 − β4·b1)·σ_BH + β5·b1        [buy excess return, simplified]
```

- Without controlling for `b1`/`b2`, most significant loadings on `σ_BH` are actually
  *negative* (116/191 significant coefficients for buy excess return in the full
  sample) — naively, "more volatile stock ⇒ better TF profit" looks false.
- Once `b1` (or `b2`) and the `σ_BH × b1` interaction are added, the loadings on
  `σ_BH` flip to reliably positive and significant (>99% of the 1,618-stock sample),
  while the interaction term is large and negative. Net effect on a given stock depends
  on the balance: at low `b1` (~1%), `σ_BH`'s loading is strongly positive (~0.75–0.91);
  at the sample's *average* `b1`/`b2` (~6%), the interaction nearly cancels it out
  (net loading ~ −0.06 to −0.08).
- `b1`/`b2` are **essentially uncorrelated with `r_BH` and `σ_BH`** (correlations
  0.01–0.24, mostly insignificant) — signal volatility captures genuinely distinct
  information, not just a repackaging of the asset's own volatility.
- The effect is stronger (more significant, bigger magnitude) in the high-volatility
  decile of stocks than the low-volatility decile — the churn penalty bites harder
  exactly where the raw-volatility opportunity looks biggest.
- `b1`/`b2` are historically *stable*: on DJIA 1896–2018, means of ~4.8%/4.2%, "relatively
  stationary" despite huge regime changes — meaning an ex-post signal-volatility estimate
  is a meaningful, reusable number, not something that needs constant re-estimation.

## Pitfalls Flagged by the Authors

- **Data snooping via signal sensitivity.** "There will always be countless ex post
  rules able to exploit [a] modest price dynamic, just because their signal sensitivity
  can be calibrated to match the asset's characteristics during that particular
  period." A highly-tuned rule with excellent in-sample Sharpe may simply have high
  hidden signal volatility that will bite out-of-sample via trading costs and false
  signals — the paper's whole point is that raw Sharpe doesn't penalize this, `Z(x,y)`
  does.
- **Sell signals are structurally weaker.** Mean before-costs sell excess return is
  negative (`−R_S = −1.58%`) even before costs, vs. positive buy excess return
  (`R_B = 2.77%`) — a documented asymmetry, not specific to any one strategy.
- **"Positive cost" paradox.** Price-slippage return from realistic (`t+1`) trading
  timing was found to be *positive* on average (`PS_B = 0.65%`, `PS_S = 0.27%`) — this
  is explicitly attributed to *declining TF signal accuracy* over the sample, not a
  free lunch; don't assume execution-timing slippage is always a cost to subtract.
- **Short-selling underperforms.** The `s3=(0,2)` (short-selling) strategy variant had
  the lowest gross return (1.63%/yr) of the three standard strategies tested, tracing
  to the documented inaccuracy of TF sell signals specifically.
- Explicitly **not** an optimization/data-mining exercise: "we ignored any optimization
  or learning process that could isolate the most profitable parameterizations,
  processes that end by generating unwanted data snooping" — the paper's headline
  numbers are deliberately *not* the best achievable result, a reminder that any
  attempt to search for the best-performing `(x,y)` or filter width needs its own
  out-of-sample discipline.

## Portability

Fully portable to **Pine Script** (a running count of signal-state transitions weighted
by which type they are, divided by bar count — see below) and to the Python `quantor`
pipeline (same formula, plus the regression/backtest machinery to reproduce the paper's
robustness checks).

### Pine Script sketch

```pine
// state: 1 = buy, -1 = sell, 0 = neutral (from existing entry logic)
var int nBS = 0, nBN = 0, nSN = 0, nTotal = 0
int prevState = state[1]
if state != prevState and not na(prevState)
    nTotal += 1
    if (state == 1 and prevState == -1) or (state == -1 and prevState == 1)
        nBS += 1
    else if (state == 1 and prevState == 0) or (state == 0 and prevState == 1)
        nBN += 1
    else if (state == -1 and prevState == 0) or (state == 0 and prevState == -1)
        nSN += 1

float b1 = nTotal > 0 ? (nBS + nBN) / nTotal : na   // buy-side signal volatility
float b2 = nTotal > 0 ? (nBS + nSN) / nTotal : na   // sell-side signal volatility
```

## Mapping to This Repo

- **Diagnostic dashboard field.** Add `b1`/`b2` (or a combined `v(x,y)`) as a plotted
  data-window field or dashboard row on any signal-generating strategy in this repo —
  directly analogous to the `rrBoxConditionLong`/`plotLongSignal` extraction done for
  `Trend_Continuation_Zones.pine` earlier in this session: a named, plottable boolean/
  float exposing an otherwise-implicit gate.
- **Cross-reference against Quality Score.** The Quality Score investigation on
  `Trend_Continuation_Zones.pine` found it has zero wiring into any gate. `b1`/`b2`
  would be legitimate, empirically-motivated *new* inputs to such a score — distinct
  from it, per the near-zero correlation finding above.
- **Candidate filter for MTF Second-Flip / continuation strategies.** The paper's
  finding that `σ_BH`'s benefit is eaten by high `b1`/`b2` suggests: when a strategy's
  own recent signal volatility (rolling `b1`/`b2` over, say, the last 20–50 signals)
  is elevated, either tighten the existing chop filter (ADX min / Choppiness max) or
  extend the cooldown — the paper's mechanism for *why* churny signals underperform
  (trading-cost drag, false-signal risk) is exactly what a cooldown/chop filter is
  meant to suppress, so this gives a principled, back-testable trigger for when to
  tighten them adaptively instead of using a fixed threshold.
- **`Z(x,y)` as a secondary metric in `quantor`.** When comparing two variants of a
  strategy in the Python pipeline, report `Z(x,y)` alongside the raw Sharpe ratio —
  a variant with a higher raw Sharpe but much higher signal volatility should look
  *worse* under `Z`, which is a more honest out-of-sample expectation.

## Applied in This Repo

*(none yet — update this section when `b1`/`b2` or `Z(x,y)` are actually implemented
in a strategy file, noting the file name and what was built)*
