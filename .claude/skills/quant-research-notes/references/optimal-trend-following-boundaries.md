# Optimal Trend-Following as a Two-Threshold Hysteresis Rule on Regime Probability

**Citation:** Dai, M., Yang, Z., Zhang, Q. & Zhu, Q. J. (2016). "Optimal Trend Following
Trading Rules." *Mathematics of Operations Research*, 41(2), 626–642.

**Type:** Theoretical (stochastic optimal control / free-boundary PDE), with a
simulation study and a real-market backtest (S&P 500, 1972–2011). This is the paper
that mathematically *proves* trend-following is optimal under a specific regime model,
rather than just documenting that it empirically works (contrast with papers #1 and #2
in this skill, which are both empirical).

## Core Methodology

Models price as geometric Brownian motion whose drift switches between two
**unobservable** regimes — bull (`μ1`) and bear (`μ2`) — driven by a hidden two-state
continuous-time Markov chain with switching intensities `λ1` (bull→bear) and `λ2`
(bear→bull). Because the regime itself can't be observed, the paper uses a **Wonham
filter** to convert it into something that *can* be computed from the price history
alone: `p_t = P(bull market | prices up to t)`, the real-time conditional probability
of currently being in the bull regime.

The investor is restricted to **all-in / all-out** positions (fully long or fully
flat — no shorting, no partial sizing), trading at proportional cost `Kb` (buy) and
`Ks` (sell), and the objective is to maximize expected log-utility of terminal wealth
over a finite horizon. Solving the resulting Hamilton-Jacobi-Bellman (HJB) free-boundary
problem, the paper proves (Theorem 1) that the **optimal trading rule is a
threshold-crossing rule on `p_t` alone**:

- **Buy** (go all-in long) the instant `p_t` crosses **up** through an upper boundary
  `p*_b(t)`.
- **Sell** (go flat) the instant `p_t` crosses **down** through a lower boundary
  `p*_s(t)`.
- **Do nothing** while `p_t` sits inside the no-trade band between them.

Critically, `p*_b(t) > p*_s(t)` always (Theorem 1(i)) — the entry threshold is strictly
stricter than the exit threshold. This is not a heuristic whipsaw-reduction trick; it
is the *mathematically optimal* structure. The paper's own framing: this is presented
as a rigorous justification for why practitioners' moving-average trend rules work,
not merely a decorative model.

## Formulas / Parameters

`p_t` dynamics (via the Wonham filter):
```
dp_t = [-(λ1+λ2)·p_t + λ2] dt + [(μ1-μ2)·p_t·(1-p_t) / σ] dB̃_t
```
where `B̃_t` is the innovations process (the "surprise" component of the realized
return relative to what the filter already expected).

Long-horizon threshold constants are pinned by a reference level and a cost term:
```
p0 = (ρ - μ2 + σ²/2) / (μ1 - μ2)          [ρ = risk-free rate]
a  = log[(1 + Kb) / (1 - Ks)]              [cost term]
```
`p*_b(t) > p0 > p*_s(t)` for all `t` — **the reference level `p0` always sits strictly
inside the no-trade band**, never at either boundary. As transaction costs `Kb`/`Ks`
rise, `a` rises, and the two boundaries push further apart — **higher costs
mathematically require a wider no-trade band**, i.e., fewer trades, directly out of
the optimality condition, not as a separate risk overlay bolted on afterward.

**The optimal rule incurs only a finite number of trades almost surely** (Lemma 2) —
proven, not just observed empirically as in paper #1.

Empirical calibration in the paper's own market test: `μ1`, `μ2`, `λ1`, `λ2` are
re-estimated **yearly** from the prior period's realized up/down-trend statistics, and
updated with **exponential smoothing** (`N=6`):
```
update = (1 - 2/N)·old + (2/N)·new
```
— i.e., a plain EMA update on the regime parameters themselves, explicitly chosen to
"overweigh recent information, whereas avoiding unwanted abrupt changes."

**S&P 500 real-market test (1972–2011):** trend-following 11.03% return / 0.217 Sharpe
vs. buy-and-hold 9.80% / 0.128 Sharpe vs. 10-year bonds at 6.79%. The Sharpe
improvement is proportionally larger than the return improvement — the paper's own
reading is that the edge shows up more as a **smoother equity curve** than as
dramatically higher raw return.

## Pitfalls Flagged (Explicitly, and One Worth Flagging Ourselves)

- **Single-path variance is enormous even when the ensemble average clearly wins.**
  Table 3 in the paper: ten individual simulated paths, *identical* parameters and
  thresholds, total returns ranging from roughly 0.08x to ~1,888x. The authors'
  explicit analogy: this is like O'Neil's CANSLIM — "that it works on a period of time
  does not mean it works on each stock when applied... measured based on the overall
  average when applied to a group." **A single TradingView Strategy Tester backtest on
  one instrument over one historical window is exactly a single sample path** — this
  paper is a direct, formal warning against reading too much into it.
- **The paper's own "threshold choice is robust" finding is an averaged-simulation
  result under a correctly-specified, stationary regime model** — it explicitly likens
  this to "150-day vs. 200-day moving average" giving comparable results. Don't
  generalize this robustness claim to real, non-stationary markets without also doing
  the paper's own second step below.
- **Regime parameters are not stable across periods in real data.** The market test
  had to re-estimate `μ1`, `μ2`, `λ1`, `λ2` *every year* because a single full-sample
  estimate was "quite different in different time periods" when the authors checked it
  directly. A fixed-forever calibration is explicitly rejected by the paper's own
  methodology.
- **Two regimes only (bull/bear), and the authors say so themselves** — "future
  research: how the approach works in models with more than two states, e.g., bull,
  bear, sideways markets" is listed as their own open problem.
- **Finite-horizon artifact**: both boundaries collapse toward the trivial "never buy" /
  "always exit" as `t → T`, an effect of the model's forced-liquidation-at-maturity
  assumption — this doesn't map onto a strategy with no fixed terminal date, though it
  loosely echoes a forced flatten-at-session-close rule.

## Portability

**The HJB/free-boundary derivation itself is not something to solve in Pine, and not
really a `quantor` task either** — it requires solving a system of variational
inequalities, well beyond either environment's normal toolkit. This paper is
theory-grounding for a design choice, not a literal library to import.

**What is directly portable, and cheaply:**
- The **two-threshold hysteresis structure** (strict entry threshold, looser exit
  threshold, on the *same* underlying regime signal) is trivially implementable on
  *any* 0–1-ish regime proxy Pine can compute — ADX-normalized trend quality, an
  EMA-stack agreement fraction, `Academia_PO3`'s state probabilities, etc. This doesn't
  require a real Wonham filter to benefit from the result.
- The **exponentially-smoothed, periodically-refreshed parameter re-estimation**
  (`update = (1-2/N)·old + (2/N)·new`) is literally what `ta.ema()` already computes —
  this validates using an *adaptive*, rolling-normalized threshold (as
  `TrendFollowingEngine_v3.pine`'s `adxNormLo`/`adxNormHi` band already does) over a
  single fixed-forever cutoff (as several other strategies in this repo still use).
- A **literal Wonham-filter `p_t`** is a lightweight filtering recursion (much cheaper
  than paper #2's full PCA+TVTP-MS pipeline) and is a genuinely tractable `quantor`
  project if a faithful implementation of this paper's result is ever wanted, with the
  resulting threshold-crossing rule then approximated on-chart.

## Mapping to This Repo

- **This is the formal justification for a pattern already used throughout this
  session, not a new idea to bolt on.** `MTF_Second_Flip_Continuation_v1_2.pine`'s
  requirement of a *second* directional flip (stricter than mere trend agreement)
  before arming an entry, `BBL_MTF.pine`'s and `Academia_PO3`'s separate
  enter-vs-hold thresholds on the same score (`accEnter` vs. `accExit`,
  `dirMinScore` vs. the softer `65` "building" read) — these are all, in effect,
  asymmetric two-threshold hysteresis rules already. This paper says that structure
  isn't just a practical whipsaw guard, it's what the mathematically optimal
  trend-following rule looks like.
- **Directly sharpens the MNQ trend-following design proposed last turn.** Whichever
  entry trigger gets chosen (pullback reclaim / second-flip / liquidity sweep), the
  underlying regime/bias gate should be built as a genuine two-threshold band from the
  start — a stricter threshold to *arm/enter*, a distinctly looser one to *stay
  armed/hold* — rather than one shared cutoff re-checked every bar. Concretely: don't
  reuse the same `htfAdxMin` value to both gate entry and to decide whether bias is
  still valid; give entry and hold-through separate, deliberately-spread thresholds,
  mirroring `p*_b > p0 > p*_s`.
- **Independent, theoretical confirmation (not just paper #1's empirical one) that
  cooldowns/trade caps aren't just risk management — they're what optimal behavior
  looks like.** Two separate papers in this skill, one empirical (signal volatility
  discounts returns via cost/false-signal risk) and one theoretical (the optimal rule
  provably trades finitely often, and the no-trade band widens with cost), now both
  point at the same prescription. For a low-commission instrument like MNQ
  specifically, this also cuts the other way: `a = log[(1+Kb)/(1-Ks)]` shrinks as costs
  shrink, so the theoretically-justified no-trade band is *narrower* for a cheap micro
  contract than it would be for a higher-cost instrument — a concrete argument for not
  over-tightening MNQ's cooldown/selectivity to match a much higher-cost strategy's
  defaults.
- **Reinforces `TrendFollowingEngine_v3.pine`'s adaptive-normalization approach
  (`adxNormLo`/`adxNormHi`) over a single hardcoded ADX cutoff** — the paper's own
  market test needed yearly, recency-weighted re-estimation to work at all; a
  regime threshold fixed once and never revisited is exactly the thing the paper's
  own methodology rejects.
- **The single-path-variance warning applies directly to every Strategy Tester run in
  this repo.** A good (or bad) backtest on MNQ's actual price history over the last
  1–3 years is one realized path. Walk-forward validation across multiple periods in
  `quantor` — not a single in-sample TradingView run — is the only way to actually see
  whether an ensemble-level edge like the one this paper proves is present.

## Contradicts / Qualifies

**No contradiction with paper #2 (Haase & Neuenkirch TVTP) — the two actually
converge.** Paper #2 found that a regime model which *also* tries to predict the
conditional mean return underperforms one that predicts the regime/transition alone.
This paper's stated objective *is* return-maximizing (expected log-utility of
terminal wealth) — but the *optimal policy it derives* still conditions on nothing but
the regime probability `p_t` itself; the return-maximizing objective, once solved,
collapses to a pure regime-threshold rule with no separate return forecast layered on
top. Read together: paper #2 shows empirically that trying to also forecast returns
hurts a live model; this paper shows theoretically that even when return-maximization
*is* the stated goal, the provably optimal policy still reduces to trading the regime
signal alone. Same prescription, reached two different ways — strengthens rather than
weakens the "predict the regime, not the return" rule already recorded in this skill's
synthesis notes.

## Applied in This Repo

- **`MNQ_Multi_Trigger_Trend_Continuation.pine`** (2026-08-23) — the regime gate
  (section 15) is built as a genuine two-threshold hysteresis band from the start:
  `regimeEnterMin` (strict, default 70) arms a fresh regime, `regimeHoldMin` (loose,
  default 45) is the distinctly lower bar required merely to remain in it, applied to
  a continuous 0–100 trend-quality score (ADX-normalized + Choppiness-normalized +
  Efficiency-normalized + bias/persistence agreement) rather than a literal Wonham-
  filter probability. A regime disarming resets every entry-trigger engine's pending
  state, so nothing carries across regimes — the same "no stale state across a regime
  change" discipline this paper's model implies.
